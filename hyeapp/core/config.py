import os
from dotenv import load_dotenv

load_dotenv()


class DatabaseConfig:
    DB_USERNAME: str = os.getenv("HYE_DB_USERNAME")
    DB_PASSWORD: str = os.getenv("HYE_DB_PASSWORD")
    DB_HOST: str = os.getenv("HYE_DB_HOST")
    DB_PORT: str = os.getenv("HYE_DB_PORT", "5432")
    DB_NAME: str = os.getenv("HYE_DB_NAME")


db_configuration = DatabaseConfig()
