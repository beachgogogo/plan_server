from odmantic import AIOEngine
from fastapi import FastAPI
from concurrent.futures import ThreadPoolExecutor


# Odmantic Setting
engine = AIOEngine(database="test")

# init FastAPI handler
app = FastAPI()

# init threadpool
executor = ThreadPoolExecutor()
