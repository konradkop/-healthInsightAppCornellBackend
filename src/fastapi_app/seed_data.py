from sqlmodel import SQLModel

from fastapi_app.models import create_db_and_tables, engine


def drop_all():
    SQLModel.metadata.drop_all(engine)


if __name__ == "__main__":
    create_db_and_tables()
