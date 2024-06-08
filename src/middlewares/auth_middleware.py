from functools import wraps
from flask import request, Response, json
from src import bcrypt
from src.models.users_model import Users
import base64
from sqlalchemy import exc
import logging

logger = logging.getLogger(__name__)

def authorization_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_data = None
        if "Authorization" in request.headers:
            auth_data = base64.b64decode(request.headers["Authorization"].split(" ")[1]).decode('utf-8')
        if not auth_data:
            logger.error("No Authorization data received")
            return Response(
                response=json.dumps({
                    "status": "failed",
                    "message": "Could not validate user"
                }),
                status=401,
                mimetype="application/json"
            )
        try:
            auth_data = auth_data.split(":")
            user = Users.query.filter_by(username = auth_data[0]).first()
            if not user:
                logger.error("Could not validate User! - Not found")
                return Response(
                    response=json.dumps({
                        "status": "failed",
                        "message": "Could not validate user"
                    }),
                    status=401,
                    mimetype="application/json"
                )
            is_valid = bcrypt.check_password_hash(user.password, auth_data[1])
            if not is_valid:
                logger.error("Could not validate user - Incorrect credentials")
                return Response(
                    response=json.dumps({
                        "status": "failed",
                        "message": "Incorrect credentials provided"
                    }),
                    status=401,
                    mimetype="application/json"
                )
            if not user.is_verified:
                logger.error("Could not validate user - Verification Pending")
                return Response(
                    response=json.dumps({
                        "status": "failed",
                        "message": "User verification is pending"
                    }),
                    status=403,
                    mimetype="application/json"
                )
        except exc.IntegrityError as e:
            return Response(
                response=json.dumps({
                    "status": "failed",
                    "message": str(e.orig)
                }),
                status=400,
                mimetype="application/json"
            )
        except Exception as e:
            return Response(
                response=json.dumps({
                    "status": "failed",
                    "message": str(e)
                }),
                status=500,
                mimetype="application/json"
            )

        logger.info("Validated User - {}".format(auth_data[0]))
        return f(user, *args, **kwargs)

    return decorated
