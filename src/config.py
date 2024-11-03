from fastapi import FastAPI
from concurrent.futures import ThreadPoolExecutor

# from odmantic import AIOEngine
# # Odmantic Setting
# engine = AIOEngine(database="test")

from sqlmodel import create_engine, SQLModel
from src.database.pg_model import (UserProfile, UserAddresses, MinimumTaskUnit,
                                       Plan, UserFolder, User)

database_name = "test"
database_url = f"postgresql://postgres:123456@127.0.0.1:5432/{database_name}"
engine = create_engine(database_url)


def init_database():
    SQLModel.metadata.create_all(engine)


# init FastAPI handler
app = FastAPI()

# init threadpool
executor = ThreadPoolExecutor()
