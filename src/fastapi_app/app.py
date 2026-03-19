import logging
import os
import pathlib

from fastapi_app.custom_agents import  get_agent_response
from azure.monitor.opentelemetry import configure_azure_monitor
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
from pydantic import BaseModel
from sqlmodel import Session, select

from .models import ChatMessage, ChatRequest, ChatResponse, GPSPayload, UserLocation, engine, UserData

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


# @app.post("/auth/login")
# async def login(data: LoginRequest, session: Session = Depends(get_db_session)):
#     if not data.username or not data.password:
#         raise HTTPException(status_code=400, detail="Username and password are required")

#     user = session.exec(select(UserData).where(UserData.username == data.username)).first()
#     if not user or user.password != data.password:
#         raise HTTPException(status_code=401, detail="Invalid username or password")

#     token = f"dummy-token-for-{user.id}"
#     return {"token": token, "user_id": user.id, "username": user.username}
@app.post("/auth/login")
async def login(data: LoginRequest):
    return {
        "token": "dummy-token-12345",
        "user_id": 1,
        "username":"testuser1"
    }

# this is not authenticated, will need to add auth logic later
@app.post("/chat")
async def chat_endpoint(chat_request: ChatRequest):
    """
    Endpoint that accepts chat messages and returns the AI's response,
    optionally including health data as a system message.
    """
    try:
        chat_request_dict = chat_request.dict()
        messages = chat_request_dict.get("messages", [])
        user_id = chat_request.user_id


        # ===== Store incoming user messages =====
        with Session(engine) as session:
            last_message = messages[-1]

            db_msg = ChatMessage(
                user_id=user_id,
                role=last_message["role"],
                content=last_message["content"],
                health_data=chat_request.health_data,
                gps_data=chat_request.gps_data,
            )
            session.add(db_msg)
            session.commit()
        with Session(engine) as session:
            # fetch the last 5 locations for the user
            statement = (
                select(UserLocation.latitude, UserLocation.longitude, UserLocation.created_at)
                .where(UserLocation.user_id == user_id)
                .order_by(UserLocation.created_at.desc())
                .limit(5)
            )
            recent_locations = session.exec(statement).all()

            if recent_locations:
                location_history_message = "User's recent location history:\n"
                for loc in reversed(recent_locations):  # oldest first
                    location_history_message += (
                        f"- {loc.created_at}: "
                        f"Lat {loc.latitude}, Lon {loc.longitude}\n"
                    )
                messages.append({"role": "system", "content": location_history_message})

        health_data = chat_request_dict.get("health_data")
        if health_data:
            healthDataMessage = (
                f"User's latest health metrics:\n"
                f"- Body Fat: {health_data.get('bodyFat', 'N/A')}%\n"
                f"- Last 7 days of Heart Rate: {health_data.get('heartRate', 'N/A')} bpm\n"
                f"- Last 7 days of Step Count: {health_data.get('stepCount', 'N/A')}\n"
                f"- Last 7 days of Active Energy: {health_data.get('activeEnergy', 'N/A')} kcal\n"
                f"- Last 7 days of Flights Climbed: {health_data.get('flightsClimbed', 'N/A')}"
                f"- Last 7 days of Sleep: {health_data.get('sleep', 'N/A')}"
            )
            messages.append({"role": "system", "content": healthDataMessage})

        gps_data = chat_request_dict.get("gps_data")
        print("gps data is: ", gps_data)
        if gps_data:
            gpsMessage = (
                f"User's current location:\n"
                f"- Latitude: {gps_data.get('latitude', 'N/A')}\n"
                f"- Longitude: {gps_data.get('longitude', 'N/A')}\n"
                f"- Accuracy: {gps_data.get('accuracy', 'N/A')} meters"
            )
            messages.append({"role": "system", "content": gpsMessage})

        response = await get_agent_response({"messages": messages})


        # ===== Store assistant response =====
        with Session(engine) as session:
            db_msg = ChatMessage(
                user_id=user_id,
                role="assistant",
                content=response,
            )
            session.add(db_msg)
            session.commit()

        return {"response": response}

    except Exception as e:
        logger.exception("Error in /chat endpoint")
        return {"error": str(e)}

# this is not authenticated, will need to add auth logic later
@app.get("/chat/history/{user_id}")
def get_chat_history(user_id: int):
    try:
        with Session(engine) as session:
            statement = (
                select(ChatMessage)
                .where(ChatMessage.user_id == user_id)
                .order_by(ChatMessage.created_at)
            )

            db_messages = session.exec(statement).all()

            # format for frontend
            messages = [
                {
                    "role": msg.role,
                    "content": msg.content,
                }
                for msg in db_messages
            ]

            return {"messages": messages}

    except Exception as e:
        logger.exception("Error fetching chat history")
        raise HTTPException(status_code=500, detail=str(e))

# this is not authenticated, will need to add auth logic later
from fastapi import Body


@app.post("/location/{user_id}")
def post_location(user_id: int, gps_data: GPSPayload = Body(...)):
    """
    Store a single GPS location for a user.
    """ 
    try:
        with Session(engine) as session:
            db_location = UserLocation(
                user_id=user_id,
                latitude=gps_data.latitude,
                longitude=gps_data.longitude,
                accuracy=gps_data.accuracy,
            )
            session.add(db_location)
            session.commit()

        return {"status": "success", "message": "Location saved"}

    except Exception as e:
        logger.exception("Error saving user location")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Cornell Health App is running!"}