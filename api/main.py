from contextlib import asynccontextmanager
from fastapi import FastAPI
from db.database import init_db
from v1.endpoints import books, auth, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(books.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")


@app.get("/")
async def root():
    a = 5
    a += 8
    print("Comment CI tests")

    return {"message": "Hello World"}
