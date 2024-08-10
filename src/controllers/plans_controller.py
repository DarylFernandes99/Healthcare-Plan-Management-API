from flask import request, Response, json, Blueprint
from src.middlewares.auth_middleware import authorization_required
from src import plan_model, etag_model
import logging
import pika
import os

logger = logging.getLogger(__name__)

# plans controller blueprint to be registered with api blueprint
plans = Blueprint("plans", __name__)

# Setup RabbitMQ connection
connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv('RABBITMQ_HOST', 'localhost')))
channel = connection.channel()
channel.queue_declare(queue='plans')

@plans.route('', methods=['POST', 'GET'])
@authorization_required
def create_plan(_: dict) -> Response:
    plan_data_obj = None
    try:
        if request.method == 'POST':
            plan_data_obj = request.json
            try:
                message = {
                    'action': 'create',
                    'data': plan_data_obj
                }

                if plan_model.get_plan(plan_data_obj['objectId']):
                    return Response(
                        response=json.dumps({
                            "status": "failed",
                            "message": "Plan already exists!"
                        }),
                        status=409,
                        mimetype="application/json"
                    )

                channel.basic_publish(exchange='', routing_key='plans', body=json.dumps(message))
                logger.info("Published create message to RabbitMQ")
                response = Response(
                    response=json.dumps({
                        "status": "success",
                        "message": "Plan created successfully!"
                    }),
                    status=201,
                    mimetype="application/json"
                )
                # response.add_etag()
                # etag_value = response.headers.get("Etag").strip('\"')
                # logger.info("Created Etag value - {}".format(etag_value))
                # plan_model.create_etag(plan_data_obj['objectId'], etag_value)
                return response
            except Exception as e:
                logger.error(str(e))
                return Response(
                    response=json.dumps({
                        "status": "failed",
                        "message": str(e)
                    }),
                    status=400,
                    mimetype="application/json"
                )
        # Get request
        else:
            try:
                logger.info("Fetched multiple plans")
                if_none_match = request.headers.get('If-None-Match')
                if if_none_match and etag_model.check_key_exists(if_none_match):
                    logger.warning("Content not modified")
                    return Response(status=304)
                
                plan_data = plan_model.get_multiple_plans()
                if not plan_data:
                    logger.info("No plans found")
                    return Response(
                        response=json.dumps({
                            "status": "failed",
                            "message": "No plans found"
                        }),
                        status=404,
                        mimetype="application/json"
                    )
                logger.info("Fetched plans data")
                response = Response(
                    response=json.dumps(plan_data),
                    status=200,
                    mimetype="application/json",
                )
                response.add_etag()
                etag_value = response.headers.get("Etag").strip('\"')
                logger.info("Saved Etag value - {}".format(etag_value))
                etag_model.save_etag(etag_value, plan_data)
                return response
            except Exception as e:
                logger.error(str(e))
                return Response(
                    response=json.dumps({
                        "status": "failed",
                        "message": str(e)
                    }),
                    status=400,
                    mimetype="application/json"
                )
    except Exception as e:
        logger.error(str(e))
        return Response(
            response=json.dumps({
                "status": "failed",
                "message": str(e)
            }),
            status=500,
            mimetype="application/json"
        )

@plans.route('/<plan_id>', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
@authorization_required
def plans_controller(_: dict, plan_id: str) -> Response:
    try:
        # Put Request
        if request.method == 'PUT':
            return Response(status=400)
        # Delete request
        elif request.method == 'DELETE':
            if plan_model.delete_plan_etag(plan_id):
                logger.info("Plan deleted successfully - {}".format(plan_id))
                return Response(
                    response=json.dumps({
                        "status": "success",
                        "message": "Plan deleted successfully"
                    }),
                    status=200,
                    mimetype="application/json"
                )
        # PATCH request
        elif request.method == 'PATCH':
            if_match = request.headers.get('If-Match')
            if if_match and not plan_model.check_etag_exists(if_match):
                logger.warning("No ETAG found")
                return Response(status=412)
            
            try:
                plan_data_obj = request.json
                message = {
                    'action': 'update',
                    'data': {
                        'objectId': plan_id,
                        **plan_data_obj
                    }
                }
                channel.basic_publish(exchange='', routing_key='plans', body=json.dumps(message))
                logger.info("Published update message to RabbitMQ")
                # plan_data = plan_model.update_plan_partial(plan_id, plan_data_obj)
                
                logger.info("Plan data updated successfully - {}".format(plan_id))
                response = Response(
                    # response=json.dumps(plan_data),
                    response=json.dumps({
                        "status": "success",
                        "message": "Plan Updated successfully!"
                    }),
                    status=200,
                    mimetype="application/json"
                )
                # response.add_etag()
                # etag_value = response.headers.get("Etag").strip('\"')
                # logger.info("Updated Etag value - {}".format(etag_value))
                # plan_model.create_etag(plan_id, etag_value)
                return response
                # else:
                #     logger.info("Failed to update plan - {}".format(plan_id))
                #     return Response(
                #         response=json.dumps({
                #             "status": "failed",
                #             "message": "Failed to update plan"
                #         }),
                #         status=400,
                #         mimetype="application/json"
                #     )
            except Exception as e:
                logger.error(str(e))
                return Response(
                    response=json.dumps({
                        "status": "failed",
                        "message": str(e)
                    }),
                    status=400,
                    mimetype="application/json"
                )
        # Get Request
        else:
            logger.info("Fetching plan data")
            if_none_match = request.headers.get('If-None-Match')
            if if_none_match and plan_model.check_etag_exists(if_none_match):
                logger.warning("Content not modified")
                return Response(status=304)
            
            plan_data = plan_model.get_complete_plan(plan_id)
            if not plan_data:
                logger.info("No plan found")
                return Response(
                    response=json.dumps({
                        "status": "failed",
                        "message": "No plan found"
                    }),
                    status=404,
                    mimetype="application/json"
                )
            logger.info("Fetched plan data")
            response = Response(
                response=json.dumps(plan_data),
                status=200,
                mimetype="application/json",
            )
            response.add_etag()
            etag_value = response.headers.get("Etag").strip('\"')
            logger.info("Saved Etag value - {}".format(etag_value))
            plan_model.create_etag(plan_id, etag_value)
            return response
    except Exception as e:
        logger.error(str(e))
        return Response(
            response=json.dumps({
                "status": "failed",
                "message": str(e)
            }),
            status=500,
            mimetype="application/json"
        )

@plans.route('/es_plan/<plan_id>', methods=['GET'])
@authorization_required
def es_plan_data_controller(_: dict, plan_id: str) -> Response:
    try:
        logger.info("Fetching plan from es data")
        if_none_match = request.headers.get('If-None-Match')
        if if_none_match and plan_model.check_etag_exists(if_none_match):
            logger.warning("Content not modified")
            return Response(status=304)
        
        plan_data = plan_model.get_complete_plan_es(plan_id)
        if not plan_data:
            logger.info("No plan found")
            return Response(
                response=json.dumps({
                    "status": "failed",
                    "message": "No plan found"
                }),
                status=404,
                mimetype="application/json"
            )
        logger.info("Fetched plan data")
        response = Response(
            response=json.dumps(plan_data),
            status=200,
            mimetype="application/json",
        )
        response.add_etag()
        etag_value = response.headers.get("Etag").strip('\"')
        logger.info("Saved Etag value - {}".format(etag_value))
        plan_model.create_etag(plan_id, etag_value)
        return response
    except Exception as e:
        logger.error(str(e))
        return Response(
            response=json.dumps({
                "status": "failed",
                "message": str(e)
            }),
            status=500,
            mimetype="application/json"
        )

@plans.route('/es_data', methods=['GET'])
@authorization_required
def es_data_controller(_: dict) -> Response:
    try:
        args = request.args
        logger.info("Fetch plan from ES")
        if_none_match = request.headers.get('If-None-Match')
        if if_none_match and plan_model.check_etag_exists(if_none_match):
            logger.warning("Content not modified")
            return Response(status=304)
        
        plan_data = None

        if args.get("parent_type"):
            plan_data = plan_model.get_es_children(args.get("parent_type"), args.get("id"))
        else:
            print(args.get("id"))
            plan_data = plan_model.get_es_plan(args.get("id"))
        
        if not plan_data:
            logger.info("No plan found in ES")
            return Response(
                response=json.dumps({
                    "status": "failed",
                    "message": "No plan found"
                }),
                status=404,
                mimetype="application/json"
            )
        logger.info("Fetched plan data from ES")
        response = Response(
            response=json.dumps(plan_data),
            status=200,
            mimetype="application/json",
        )
        response.add_etag()
        etag_value = response.headers.get("Etag").strip('\"')
        logger.info("Saved ES Etag value - {}".format(etag_value))
        plan_model.create_etag(args.get("id"), etag_value)
        return response
    except Exception as e:
        logger.error(str(e))
        return Response(
            response=json.dumps({
                "status": "failed",
                "message": str(e)
            }),
            status=500,
            mimetype="application/json"
        )
