import logging
from fastapi import logger
from sqlmodel import Session
from fastapi_app.models import UserData, engine

import json

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

def seed_database(json_path: str = "src/seed_data.json"):
    """
    Populates the UserData table using entries from a JSON file.
    """
    logger.info("Load data from JSON file and seed database...")

    # Load data from JSON file
    with open(json_path, "r") as f:
        data = json.load(f)

    with Session(engine) as session:
        for item in data:
            fields = item["fields"]
            user = UserData(**fields)
            session.add(user)
        session.commit()

    logger.info(f"✅ Inserted {len(data)} test users into database.")


if __name__ == "__main__":
    seed_database()


# To run this script, use the command:
# python3 src/seed_test_users.py