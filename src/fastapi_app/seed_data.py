import logging
import sys

from sqlmodel import SQLModel

from fastapi_app.models import create_db_and_tables, engine


logger = logging.getLogger("app")
logger.setLevel(logging.INFO)

if not logger.hasHandlers():
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def drop_all():
    logger.info("Drpping db...")
    SQLModel.metadata.drop_all(engine)


if __name__ == "__main__":
    logger.info("Create Database and tables from seed_data.py")
    create_db_and_tables()
