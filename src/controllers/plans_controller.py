from flask import request, Response, json, Blueprint
from src.middlewares.auth_middleware import authorization_required
from src import plan_model, etag_model
import logging

logger = logging.getLogger(__name__)

# plans controller blueprint to be registered with api blueprint
plans = Blueprint("plans", __name__)

@plans.route('', methods=['POST', 'GET'])
@authorization_required
def create_user(_: dict) -> Response:
    plan_data_obj = None
    try:
        if request.method == 'POST':
            plan_data_obj = request.json
            try:
                if not plan_model.create_plan(plan_data_obj):
                    logger.error("Failed to create Plan - Plan already exists!")
                    return Response(
                        response=json.dumps({
                            "status": "failed",
                            "message": "Plan already exists!"
                        }),
                        status=409,
                        mimetype="application/json"
                    )
                logger.info("Plan created succesffuly")
                response = Response(
                    response=json.dumps({
                        "status": "success",
                        "data": plan_data_obj,
                        "message": "Plan created successfully"
                    }),
                    status=201,
                    mimetype="application/json"
                )
                response.add_etag()
                etag_value = response.headers.get("Etag").strip('\"')
                logger.info("Created Etag value - {}".format(etag_value))
                etag_model.save_etag(etag_value, plan_data_obj)
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
def get_update_controller(_: dict, plan_id: str) -> Response:
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
            if_none_match = request.headers.get('If-Match')
            if if_none_match and not plan_model.check_etag_exists(if_none_match):
                logger.warning("No ETAG found")
                return Response(status=412)
            
            try:
                plan_data_obj = request.json
                plan_data = plan_model.update_plan_partial(plan_id, plan_data_obj)
                if plan_data:
                    logger.info("Plan updated successfully - {}".format(plan_id))
                    plan_model.delete_plan_etag(plan_id, delete_plan=False)
                    response = Response(
                        response=json.dumps({
                            "status": "success",
                            "message": "Plan updated successfully",
                            "data": plan_data
                        }),
                        status=200,
                        mimetype="application/json"
                    )
                    response.add_etag()
                    etag_value = response.headers.get("Etag").strip('\"')
                    logger.info("Saved updated Etag value - {}".format(etag_value))
                    # etag_model.save_etag(etag_value, plan_data)
                    plan_model.create_etag(plan_id, etag_value)

                    return response
                logger.error("Failed to update Plan - Plan not found!")
                return Response(
                    response=json.dumps({
                        "status": "failed",
                        "message": "Plan not found!"
                    }),
                    status=404,
                    mimetype="application/json"
                )
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
            if_none_match = request.headers.get('If-None-Match')
            if if_none_match and plan_model.check_etag_exists(if_none_match):
                logger.warning("Content not modified")
                return Response(status=304)
            
            plan_data = plan_model.get_plan(plan_id)
            if not plan_data:
                logger.info("Plan not found - {}".format(plan_id))
                return Response(
                    response=json.dumps({
                        "status": "failed",
                        "message": "Plan not found"
                    }),
                    status=404,
                    mimetype="application/json"
                )
            logger.info("Fetched plan data for {}".format(plan_id))
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
        
        logger.error("Plan not found - {}".format(plan_id))
        return Response(
                response=json.dumps({
                    "status": "failed",
                    "message": "No Plan found"
                }),
                status=404,
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
