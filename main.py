from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import get_db_and_tables
from app.routers import auth, projects, tasks  
from contextlib import asynccontextmanager



@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="Task Manager API", version="1.0.0")


origins = [
    "http://localhost",
    "http://localhost:3000", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    await get_db_and_tables()


app.include_router(auth.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": "Welcome to the Task Manager API!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, log_level="info")

