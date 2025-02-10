from fastapi import FastAPI
from api.endpoints import user
from mangum import Mangum  # Adapter to run FastAPI on AWS Lambda
from log.logging_config import setup_logging
import os

setup_logging()

app = FastAPI(title="HYE", version="1.0.0")

# Include our user routes under the "/users" path.
app.include_router(user.router, prefix="/users", tags=["users"])

# The Mangum handler wraps the ASGI app so it can be called by AWS Lambda.
handler = Mangum(app)

# import urllib.request

# def handler(event, context):
#     try:
#         response = urllib.request.urlopen('https://cognito-idp.us-east-2.amazonaws.com/us-east-2_j7TTNd6qj/.well-known/jwks.json')
#         status_code = response.getcode()
#         print('Response Code:', status_code)
#         print('Response Data:', response.read().decode('utf-8'))
#         return status_code
#     except Exception as e:
#         print('Error:', e)
#         raise e
