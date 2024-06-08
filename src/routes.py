from flask import request, Response, Blueprint
from src.controllers.plans_controller import plans
from src import config
import logging

logger = logging.getLogger(__name__)

# main blueprint to be registered with application
api = Blueprint('', __name__)
# register new routes with api blueprint
plan_path = f"{config.VERSION}/plan"
api.register_blueprint(plans, url_prefix=plan_path)

@api.before_app_request
def before_request():
    logger.info("Request started for {}: {}".format(request.method, request.url_rule))

# updating headers after completion
@api.after_app_request
def add_header(response: Response) -> Response:
    logger.info("Request completed for {}: {}".format(request.method, request.url_rule))
    return response

# removing body data from 405 method response
@api.app_errorhandler(405)
def special_exception_handler(error: Response) -> Response:
    logger.warning("Method not allowed")
    return Response(status=405)
