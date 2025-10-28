import logging
import os
import sys
from datetime import datetime
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import DateTime, Integer, String, func, text
from sqlmodel import Field, SQLModel, create_engine

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

if not logger.hasHandlers():
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


sql_url = ""
logger.info("Trying to connect to database...")
logger.info("V666")

if os.getenv("WEBSITE_HOSTNAME"):
    logger.info("Connecting to Azure PostgreSQL Flexible server based on AZURE_POSTGRESQL_CONNECTIONSTRING...")
    env_connection_string = os.getenv("AZURE_POSTGRESQL_CONNECTIONSTRING")
    if env_connection_string is None:
        logger.info("Missing environment variable AZURE_POSTGRESQL_CONNECTIONSTRING")
    else:
        # Parse the connection string
        details = dict(item.split('=') for item in env_connection_string.split())

        # Properly format the URL for SQLAlchemy
        sql_url = (
            f"postgresql://{quote_plus(details['user'])}:{quote_plus(details['password'])}"
            f"@{details['host']}:{details['port']}/{details['dbname']}?sslmode={details['sslmode']}"
        )
        logger.info("String constructed: " + sql_url)

else:
    logger.info("Connecting to local PostgreSQL server based on .env file...")
    load_dotenv()
    POSTGRES_USERNAME = os.environ.get("DBUSER")
    POSTGRES_PASSWORD = os.environ.get("DBPASS")
    POSTGRES_HOST = os.environ.get("DBHOST")
    POSTGRES_DATABASE = os.environ.get("DBNAME")
    POSTGRES_PORT = os.environ.get("DBPORT", 5432)

    sql_url = f"postgresql://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"

logger.info("Creating SQL Engine")

try:
    engine = create_engine(sql_url, pool_pre_ping=True)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        logger.info("✅ Successfully connected to the database!")

except Exception as e:
    logger.error("❌ Unexpected error during database connection:")
    logger.exception(e)


def create_db_and_tables():
    logger.info("Creating Database and tables")
    return SQLModel.metadata.create_all(engine)


# class User(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     username: str = Field(max_length=50)
#     password: str = Field(max_length=50)
#     created_at: datetime = Field(
#         default_factory=datetime.utcnow,
#         sa_column=Column(DateTime(timezone=True), server_default=func.now())
#     )

class user_data(SQLModel, table=True):
    id: int | None = Field(
        default=None,
        primary_key=True,
        sa_type=Integer,
        sa_column_kwargs={"autoincrement": True, "nullable": False}
    )
    username: str = Field(
        sa_type=String,
        sa_column_kwargs={"nullable": False, "unique": True, "length": 50}
    )
    password: str = Field(
        sa_type=String,
        sa_column_kwargs={"nullable": False, "length": 50}
    )
    created_at: datetime = Field(
        sa_type=DateTime,
        sa_column_kwargs={"server_default": func.now(), "nullable": False}
    )