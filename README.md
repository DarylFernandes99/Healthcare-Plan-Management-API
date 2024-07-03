## Oauth Postman setup
https://blog.postman.com/how-to-access-google-apis-using-oauth-in-postman/

## Docker command to create redis container
```
$ docker run -d --name my-redis-stack -p 6379:6379 redis
```

### Contents of .env file
```
# .env
PYTHON_ENV = "development"

DEV_PORT = "5000"
DEV_HOST = "localhost"
REDIS_DEV_HOST = "localhost"
REDIS_DEV_PORT = "6379"
DEV_VERSION = "v1"
DEV_OAUTH_CLIENT_ID = "<OAUTH_CLIENT_ID>"

PROD_PORT = "5000"
PROD_HOST = "localhost"
REDIS_PROD_HOST = "localhost"
REDIS_PROD_PORT = "6379"
PROD_VERSION = "v1"
PROD_OAUTH_CLIENT_ID = "<OAUTH_CLIENT_ID>"
```
