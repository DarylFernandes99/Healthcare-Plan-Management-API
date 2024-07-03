import json
from redis import Redis
from jsonschema import validate, ValidationError
from src.models.redis_model import RedisModel

class PlanModel(RedisModel):
    plan_schema = {}
    try:
        plan_schema = json.load(open("src/models/useCaseSchema.json"))
    except Exception as e:
        print(e)

    def __init__(self, redis_client: Redis):
        super().__init__(redis_client, "plan")
        self.etag_model = RedisModel(redis_client, "etag")

    def validate_data(self, data):
        try:
            validate(instance=data, schema=self.plan_schema)
        except ValidationError as e:
            raise ValueError(f"Invalid data: {e.message}")

    def create_plan(self, plan):
        plan_data = plan
        self.validate_data(plan_data)
        plan_id = plan_data['objectId']
        if not self.get_plan(plan_id):
            self.save(plan_id, plan_data)
            return 1
        return 0
    
    def create_etag(self, plan_id, etag):
        return self.etag_model.save(f"{self.get_key(plan_id)}:{etag}", self.get_plan(plan_id))

    # def update_plan(self, plan_id, **kwargs):
    #     plan_data = self.get(plan_id)
    #     if not plan_data:
    #         raise ValueError("Plan not found")
        
    #     for key, value in kwargs.items():
    #         if key == "password":
    #             value = generate_password_hash(value)
    #         plan_data[key] = value
    #     self.validate_data(plan_data)
    #     self.save(plan_id, plan_data)
    #     return plan_data

    def update_plan_partial(self, plan_id, update_data):
        plan_data = self.get(plan_id)
        if not plan_data:
            return []

        for key, value in update_data.items():
            if key == "planCostShares":
                if "planCostShares" in plan_data:
                    plan_data["planCostShares"].update(value)
                else:
                    plan_data["planCostShares"] = value
            elif key == "linkedPlanServices":
                for service in value:
                    found = False
                    for existing_service in plan_data.get("linkedPlanServices", []):
                        if existing_service["objectId"] == service["objectId"]:
                            existing_service.update(service)
                            found = True
                            break
                    if not found:
                        plan_data.setdefault("linkedPlanServices", []).append(service)
            # elif key in plan_data:
            #     plan_data[key] = value
            # else:
            #     plan_data[key] = value

        self.validate_data(plan_data)
        self.save(plan_id, plan_data)
        return plan_data

    def get_plan(self, plan_id):
        return self.get(plan_id)

    def get_multiple_plans(self) -> list:
        keys = self.get_multiple_keys(self.key_prefix)
        return self.get_multiple_values(keys)

    def delete_plan_etag(self, plan_id, delete_plan=True):
        plan = self.get_key(plan_id)
        keys = [plan] if delete_plan else []
        keys.extend(self.get_multiple_keys(f"{self.etag_model.key_prefix}:{plan}:*"))
        return self.delete_multiple_keys(keys)
    
    def check_etag_exists(self, etag):
        return self.etag_model.get_multiple_keys(f"{self.etag_model.key_prefix}:*:{etag}")
