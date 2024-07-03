from functools import wraps
from flask import request, Response, json
import logging
import jwt
import requests
from jwt.algorithms import RSAAlgorithm
from src import config

logger = logging.getLogger(__name__)

def authorization_required(f):

    def get_google_public_keys():
        response = requests.get('https://www.googleapis.com/oauth2/v3/certs')
        response.raise_for_status()
        return response.json()

    def get_key(kid, keys):
        for key in keys['keys']:
            if key['kid'] == kid:
                return key
        raise ValueError("Key not found")
    
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_token = None
        if "Authorization" in request.headers:
            auth_token = request.headers["Authorization"].split(" ")[1]
        
        if not auth_token:
            logger.warning("No Authorization data received")
            return Response(
                response=json.dumps({
                    "status": "failed",
                    "message": "Could not validate user"
                }),
                status=401,
                mimetype="application/json"
            )
        try:
            # Get JWT headers
            header_data = jwt.get_unverified_header(auth_token)

            # Get Google's public keys
            keys = get_google_public_keys()
            
            # Find the right key
            key = get_key(header_data["kid"], keys)
            
            # Construct the public key
            public_key = RSAAlgorithm.from_jwk(key)

            user = jwt.decode(jwt=auth_token, key=public_key, algorithms=[header_data["alg"], ], audience=config.OAUTH_CLIENT_ID)

            if not user:
                logger.warning("Invalid user")
                return Response(
                    response=json.dumps({
                        "status": "failed",
                        "message": "Could not validate user"
                    }),
                    status=401,
                    mimetype="application/json"
                )
        except Exception as e:
            if (type(e) == jwt.InvalidAudienceError):
                logger.error("Invalid Client ID -> {}".format(str(e)))
            elif (type(e) == jwt.ExpiredSignatureError):
                logger.warning("Expired Signature -> {}".format(str(e)))
            elif (type(e) == jwt.DecodeError):
                logger.warning("Decode error -> {}".format(str(e)))
            else:
                logger.error(str(e))
                return Response(
                    response=json.dumps({
                        "status": "failed",
                        "message": "Internal Server Error"
                    }),
                    status=500,
                    mimetype="application/json"
                )
            return Response(
                response=json.dumps({
                    "status": "failed",
                    "message": "Failed to validate user"
                }),
                status=401,
                mimetype="application/json"
            )

        logger.info("Validated User - {}".format(user["email"]))
        return f(user, *args, **kwargs)

    return decorated
