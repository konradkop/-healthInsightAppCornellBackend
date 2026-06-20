import logging
import os
import sys
from datetime import datetime
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import DateTime, Column, func, text, UniqueConstraint
from sqlmodel import Field, SQLModel, create_engine
from typing import List, Optional, Any
from pydantic import BaseModel
from sqlalchemy.dialects.postgresql import JSONB

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


if os.getenv("WEBSITE_HOSTNAME"):
    logger.info("Connecting to Azure PostgreSQL Flexible server based on AZURE_POSTGRESQL_CONNECTIONSTRING...")
    env_connection_string = os.getenv("AZURE_POSTGRESQL_CONNECTIONSTRING")
    if env_connection_string is None:
        logger.info("Missing environment variable AZURE_POSTGRESQL_CONNECTIONSTRING")
        logger.info("Connecting to local PostgreSQL server based on .env file...")
        load_dotenv()
        POSTGRES_USERNAME = os.environ.get("DBUSER")
        POSTGRES_PASSWORD = os.environ.get("DBPASS")
        POSTGRES_HOST = os.environ.get("DBHOST")
        POSTGRES_DATABASE = os.environ.get("DBNAME")
        POSTGRES_PORT = os.environ.get("DBPORT", 5432)
        sql_url = f"postgresql://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"
        logger.info("String constructed: " + sql_url)
    else:
        # Parse the connection string
        details = dict(item.split('=') for item in env_connection_string.split())

        # Properly format the URL for SQLAlchemy
        sql_url = (
            f"postgresql://{quote_plus(details['user'])}:{quote_plus(details['password'])}"
            f"@{details['host']}:{details['port']}/{details['dbname']}?sslmode={details['sslmode']}"
        )
        logger.info("String constructed: " + sql_url)


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

# anything with table=True will be stored in a table
class UserData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=50)
    password: str = Field(max_length=50)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    messages: List[Message] 
    use_harm_guardrail: Optional[bool] = True
    use_mi_check_guardrail: Optional[bool] = True
    use_sensing_agent: Optional[bool] = False
    sensing_prompt: Optional[str] = None
    reset_agent: Optional[bool] = None
    health_data: Optional[dict[str, Any]] = None
    gps_data: Optional[dict[str, Any]] = None
    
class ChatResponse(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field()
    reply: str = Field()

# chatrequest just stores the types, chatMessage is what's actually going in the db@app.post("/chat")
class ChatMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)

    role: str = Field(max_length=20)  # "user" or "assistant"
    content: str

    health_data: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSONB)
    )

    gps_data: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSONB)
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

class GPSPayload(BaseModel):
    latitude: float
    longitude: float
    accuracy: Optional[float] = None

class UserLocation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)

    latitude: float
    longitude: float
    accuracy: Optional[float] = None

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

class HeartRate(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)

    bpm: float

    recorded_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

    __table_args__ = (
        UniqueConstraint("user_id", "recorded_at", name="uq_heart_user_date"),
    )

class StepCount(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)

    steps: int

    recorded_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

    __table_args__ = (
        UniqueConstraint("user_id", "recorded_at", name="uq_step_user_date"),
    )

class Sleep(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)

    duration_hours: float

    recorded_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

    __table_args__ = (
        UniqueConstraint("user_id", "recorded_at", name="uq_sleep_user_date"),
    )
class ActiveEnergy(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)

    kcal: float

    recorded_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

    __table_args__ = (
        UniqueConstraint("user_id", "recorded_at", name="uq_energy_user_date"),
    )
class FlightsClimbed(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)

    flights: int

    recorded_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

    __table_args__ = (
        UniqueConstraint("user_id", "recorded_at", name="uq_flights_user_date"),
    )
class BodyFat(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True) 
    user_id: int = Field(index=True) 
    percentage: float 
    recorded_at: datetime = Field( 
        default_factory=datetime.utcnow, 
        sa_column=Column( DateTime(timezone=True), 
        server_default=func.now(), ) )
    
    __table_args__ = (
    UniqueConstraint("user_id", "recorded_at", name="uq_bodyfat_user_time"),
)