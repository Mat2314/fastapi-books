from contextlib import asynccontextmanager
from fastapi import FastAPI
from db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    a = 5
    a += 8
    print("Comment CI tests")

    return {"message": "Hello World"}
