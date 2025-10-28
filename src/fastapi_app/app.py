import logging
import os
import pathlib

from azure.monitor.opentelemetry import configure_azure_monitor
from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlmodel import Session, select
from fastapi.middleware.cors import CORSMiddleware
from .models import  User, engine
from fastapi import HTTPException

# Setup logger and Azure Monitor:
logger = logging.getLogger("app")
logger.setLevel(logging.INFO)
if os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):
    configure_azure_monitor()


# Setup FastAPI app:
app = FastAPI()

# For testing, we allow everything
# In production, replace with your actual web frontend URLs
if os.getenv("RUNNING_IN_PRODUCTION"):
    allowed_origins = [
        "https://your-production-frontend.com",
        "https://another-frontend.com",
    ]
else:
    allowed_origins = [
        "http://localhost:19006",  # Expo web
        "http://localhost:3000",   # React web dev server
        "http://localhost:8081", 
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Mobile apps don’t need CORS, web does
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

parent_path = pathlib.Path(__file__).parent.parent
app.mount("/mount", StaticFiles(directory=parent_path / "static"), name="static")
templates = Jinja2Templates(directory=parent_path / "templates")
templates.env.globals["prod"] = os.environ.get("RUNNING_IN_PRODUCTION", False)
# Use relative path for url_for, so that it works behind a proxy like Codespaces
templates.env.globals["url_for"] = app.url_path_for


# Dependency to get the database session
def get_db_session():
    with Session(engine) as session:
        yield session


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/auth/login")
async def login(data: LoginRequest, session: Session = Depends(get_db_session)):
    if not data.username or not data.password:
        raise HTTPException(status_code=400, detail="Username and password are required")

    user = session.exec(select(User).where(User.username == data.username)).first()
    if not user or user.password != data.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = f"dummy-token-for-{user.id}"
    return {"token": token, "user_id": user.id, "username": user.username}


@app.get("/")
async def root():
    return {"message": "Cornell Health App is running!"}