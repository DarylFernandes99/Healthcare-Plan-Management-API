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

    def validate_data(self, data):
        try:
            validate(instance=data, schema=self.plan_schema)
        except ValidationError as e:
            raise ValueError(f"Invalid data: {e.message}")

    def create_plan(self, plan):
        plan_data = plan
        plan_id = plan_data['objectId']
        if not self.get_plan(plan_id):
            self.validate_data(plan_data)
            self.save(plan_id, plan_data)
            return 1
        return 0

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

    def get_plan(self, plan_id) -> int:
        return self.get(plan_id)

    def delete_plan(self, plan_id):
        return self.delete(plan_id)
