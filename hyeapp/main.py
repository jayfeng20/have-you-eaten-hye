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
