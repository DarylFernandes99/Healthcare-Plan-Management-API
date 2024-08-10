import json
from redis import Redis
from src.models.elastic_search_model import ElasticSearchConfig
from jsonschema import validate, ValidationError
from src.models.redis_model import RedisModel

class PlanModel(RedisModel):
    plan_schema = {}
    try:
        plan_schema = json.load(open("src/models/useCaseSchema.json"))
    except Exception as e:
        print(e)

    def __init__(self, redis_client: Redis, es: ElasticSearchConfig):
        super().__init__(redis_client, "plan")
        self.etag_model = RedisModel(redis_client, "etag")
        self.es = es
        self.INDEX_NAME = "plans"

    def validate_data(self, data):
        try:
            validate(instance=data, schema=self.plan_schema)
        except ValidationError as e:
            raise ValueError(f"Invalid data: {e.message}")

    def create_plan(self, plan, update=False):
        plan_data = plan
        self.validate_data(plan_data)
        plan_id = plan_data['objectId']
        
        if not self.get_plan(plan_id) or update:
            elastic_conn = self.es.create_index if not update else self.es.update_index

            updated_plan = {k: v for k, v in plan_data.items() if k not in ["planCostShares", "linkedPlanServices"]}

            es_plan = updated_plan.copy()
            es_plan["join_field"] = {"name": "plan"}  # Set join_field for parent document
            elastic_conn(index=self.INDEX_NAME, id=plan_id, body=es_plan, doc_type="_doc")

            # Store planCostShares in Redis and Elasticsearch
            plan_cost_share_data = plan_data["planCostShares"].copy()
            plan_cost_share_id = "{}:{}".format(plan_cost_share_data["objectType"], plan_cost_share_data["objectId"])
            updated_plan["planCostShares"] = plan_cost_share_id
            self.save(plan_cost_share_id, plan_cost_share_data)

            plan_cost_share_data["join_field"] = {
                "name": "planCostShare", 
                "parent": plan_id  # Link to parent plan
            }
            elastic_conn(index=self.INDEX_NAME, id=plan_cost_share_data["objectId"], routing=plan_id, body=plan_cost_share_data, doc_type="_doc")

            # Initialize the list for linkedPlanServices in the updated plan
            updated_plan["linkedPlanServices"] = []
            
            for linked_service in plan_data["linkedPlanServices"]:
                linked_plan_service_data = linked_service.copy()
                linked_plan_service_id = linked_plan_service_data["objectId"]

                # Index linkedPlanService in Elasticsearch
                es_linked_plan_service = {k: v for k, v in linked_plan_service_data.items() if k not in ["linkedService", "planserviceCostShares"]}
                es_linked_plan_service["join_field"] = {
                    "name": "linkedPlanService", 
                    "parent": plan_id  # Link to parent plan
                }
                elastic_conn(index=self.INDEX_NAME, id=linked_plan_service_id, routing=plan_id, body=es_linked_plan_service, doc_type="_doc")

                # Store linkedService data
                linked_service_data = linked_plan_service_data["linkedService"].copy()
                linked_service_id = linked_service_data["objectId"]
                linked_service_name = "{}:{}".format(linked_service_data["objectType"], linked_service_data["objectId"])
                self.save(linked_service_name, linked_service_data)

                linked_service_data["join_field"] = {
                    "name": "linkedService", 
                    "parent": linked_plan_service_id  # Link to linkedPlanService
                }
                elastic_conn(index=self.INDEX_NAME, id=linked_service_id, routing=linked_plan_service_id, body=linked_service_data, doc_type="_doc")
                linked_plan_service_data["linkedService"] = linked_service_name

                # Store planserviceCostShares data
                planservice_cost_share_data = linked_plan_service_data["planserviceCostShares"].copy()
                planservice_cost_share_id = planservice_cost_share_data["objectId"]
                planservice_cost_share_name = "{}:{}".format(planservice_cost_share_data["objectType"], planservice_cost_share_id)
                self.save(planservice_cost_share_name, planservice_cost_share_data)

                planservice_cost_share_data["join_field"] = {
                    "name": "planserviceCostShare", 
                    "parent": linked_plan_service_id  # Link to linkedPlanService
                }
                elastic_conn(index=self.INDEX_NAME, id=planservice_cost_share_id, routing=linked_plan_service_id, body=planservice_cost_share_data, doc_type="_doc")
                linked_plan_service_data["planserviceCostShares"] = planservice_cost_share_name

                # Save the updated linkedPlanService data
                linked_plan_service_name = "{}:{}".format(linked_plan_service_data["objectType"], linked_plan_service_data["objectId"])
                self.save(linked_plan_service_name, linked_plan_service_data)
                updated_plan["linkedPlanServices"].append(linked_plan_service_name)

            # Save the updated plan in Redis and Elasticsearch
            self.save(plan_id, updated_plan)
            return 1
        
        return 0
    
    def create_etag(self, plan_id, etag):
        return self.etag_model.save(f"{self.get_key(plan_id)}:{etag}", self.get_plan(plan_id))

    def update_plan_partial(self, plan_id, update_data):
        plan_data = self.get_complete_plan(plan_id)
        
        if not plan_data:
            return []
        
        if update_data["planCostShares"]:
            if "planCostShares" in plan_data:
                plan_data["planCostShares"].update(update_data["planCostShares"])
            else:
                plan_data["planCostShares"] = update_data["planCostShares"]
        
        for service in (update_data["linkedPlanServices"] or []):
            found = False
            for existing_service in plan_data.get("linkedPlanServices", []):
                if existing_service["objectId"] == service["objectId"]:
                    existing_service.update(service)
                    found = True
                    break
            if not found:
                plan_data.setdefault("linkedPlanServices", []).append(service)

        self.validate_data(plan_data)
        self.delete_plan_etag(plan_id, delete_plan=False)
        self.create_plan(plan_data, True)
        return plan_data

    def get_plan(self, plan_id):
        plan_data = self.get(plan_id)
        # if plan_data:
        #     for key, value in plan_data.items():
        #         if key == "planCostShares":
        #             plan_data[key] = self.get(value)
        #         elif key == "linkedPlanServices":
        #             for idx, service_value in enumerate(value):
        #                 temp_service = self.get(service_value)
        #                 for service_key, val in temp_service.items():
        #                     if service_key == "linkedService" or service_key == "planserviceCostShares":
        #                         temp_service[service_key] = self.get(val)
        #                 plan_data[key][idx] = temp_service
        return plan_data
    
    def get_complete_plan(self, plan_id):
        plan_data = self.get(plan_id)
        if not plan_data:
            return None
        
        if plan_data["planCostShares"]:
            plan_data["planCostShares"] = self.get(plan_data["planCostShares"])
        
        if plan_data["linkedPlanServices"]:
            for idx, service_value in enumerate(plan_data["linkedPlanServices"]):
                temp_service = self.get(service_value)

                if temp_service["linkedService"]:
                    temp_service["linkedService"] = self.get(temp_service["linkedService"])

                if temp_service["planserviceCostShares"]:
                    temp_service["planserviceCostShares"] = self.get(temp_service["planserviceCostShares"])
                
                plan_data["linkedPlanServices"][idx] = temp_service
        
        return plan_data
    
    def remove_join_field(self, obj):
        if isinstance(obj, dict):
            # Remove 'join_field' key if present
            if 'join_field' in obj:
                del obj['join_field']
            
            # Recursively process dictionary values
            for key in list(obj.keys()):
                self.remove_join_field(obj[key])
        
        elif isinstance(obj, list):
            # Recursively process list items
            for item in obj:
                self.remove_join_field(item)
    
    def check_es_hits(self, data: dict):
        if not data['hits']['hits']:
            return None  # Plan not found

        return [value["_source"] or {} for value in data['hits']['hits']]

    def get_es_plan(self, plan_id):
        query = {
            "query": {
                "term": {
                    "objectId": plan_id
                }
            }
        }

        return self.check_es_hits(self.es.search_index(index=self.INDEX_NAME, body=query))
    
    def get_es_children(self, parent_type: str, parent_id: str):
        query = {
            "query": {
                "has_parent": {
                    "parent_type": parent_type,
                    "query": {
                        "term": {
                            "_id": parent_id,
                        }
                    }
                }
            }
        }

        return self.check_es_hits(self.es.search_index(index=self.INDEX_NAME, routing=parent_id, body=query))

    def get_complete_plan_es(self, plan_id):
        # Fetch plan from ES
        plan_result = self.get_es_plan(plan_id)

        # Check if plan is found
        if not plan_result:
            return None
        plan_data = plan_result[0]

        # Get plan children from ES
        children_data = self.get_es_children("plan", plan_id)
        
        # Get planCostShare and linkedPlanService from children result
        plan_cost_share_data = list(filter(lambda d: d['objectType'] == "membercostshare", children_data))[0] or {}
        linked_plan_service_data = list(filter(lambda d: d['objectType'] == "planservice", children_data)) or []


        # Iterate over linked_plan_service_data
        for idx, linked_service in enumerate(linked_plan_service_data):
            linked_service_id = linked_service["objectId"]

            # Get linkedPlanService children from ES
            linked_service_children_result = self.get_es_children("linkedPlanService", linked_service_id)
            
            # Get planCostShare and linkedService objects from linked service children
            linked_plan_service_data[idx]["linkedService"] = list(filter(lambda d: d['objectType'] == "service", linked_service_children_result))[0] or {}
            linked_plan_service_data[idx]["planserviceCostShares"] = list(filter(lambda d: d['objectType'] == "membercostshare", linked_service_children_result))[0] or {}

        
        plan_data["planCostShares"] = plan_cost_share_data
        plan_data["linkedPlanServices"] = linked_plan_service_data

        self.remove_join_field(plan_data)

        return plan_data

    def get_multiple_plans(self) -> list:
        keys = self.get_multiple_keys(self.key_prefix)
        return self.get_multiple_values(keys)

    def delete_plan_etag(self, plan_id, delete_plan=True):
        plan = self.get_key(plan_id)
        keys = [plan] if delete_plan else []
        keys.extend(self.get_multiple_keys(f"{self.etag_model.key_prefix}:{plan}:*"))
        keys.extend(self.get_multiple_keys(f"{plan}:*"))

        plan_data = self.get(plan_id)
        es_ids = [
            {"delete": {"_index": self.INDEX_NAME, "_id": plan_data["objectId"]}}
        ]

        plan_cost_share_id = plan_data["planCostShares"].split(":")[1]
        es_ids.append({"delete": {"_index": self.INDEX_NAME, "_id": plan_cost_share_id}})
        keys.extend([self.get_key(plan_data["planCostShares"])])

        for service in (plan_data["linkedPlanServices"] or []):
            service_id = service.split(":")[1]
            
            linked_service_data = self.get(service)
            linked_service_id = linked_service_data["linkedService"].split(":")[1]
            es_ids.append({"delete": {"_index": self.INDEX_NAME, "_id": linked_service_id}})
            
            plan_service_cost_shares = linked_service_data["planserviceCostShares"].split(":")[1]
            es_ids.append({"delete": {"_index": self.INDEX_NAME, "_id": plan_service_cost_shares}})
            
            keys.extend([self.get_key(service), self.get_key(linked_service_data["linkedService"]), self.get_key(linked_service_data["planserviceCostShares"])])
            es_ids.append({"delete": {"_index": self.INDEX_NAME, "_id": service_id}})
        
        self.es.bulk_operations(es_ids)

        return self.delete_multiple_keys(keys)
    
    def check_etag_exists(self, etag):
        return self.etag_model.get_multiple_keys(f"{self.etag_model.key_prefix}:*:{etag}")
