from fastapi import FastAPI
from api.endpoints import user
from mangum import Mangum  # Adapter to run FastAPI on AWS Lambda

app = FastAPI(title="User Profile API", version="1.0.0")

# Include our user routes under the "/users" path.
app.include_router(user.router, prefix="/users", tags=["users"])

# The Mangum handler wraps the ASGI app so it can be called by AWS Lambda.
handler = Mangum(app)


# Optionally, include a startup event to initialize your DB models, etc.
@app.on_event("startup")
async def on_startup():
    # You might want to create the tables here if they don't exist:
    # from app.models.user import Base
    # from app.db.session import engine
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    pass
