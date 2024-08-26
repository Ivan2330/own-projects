from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import get_db_and_tables
from app.routers import auth, projects, tasks  # Імпорт ваших роутерів

app = FastAPI(title="Task Manager API", version="1.0.0")

# CORS налаштування (якщо ваш фронтенд буде працювати на іншому домені)
origins = [
    "http://localhost",
    "http://localhost:3000",  # Наприклад, якщо ваш фронтенд на React
    # Інші допустимі домени
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Підключення до бази даних та створення таблиць
@app.on_event("startup")
async def on_startup():
    await get_db_and_tables()

# Підключення роутерів
app.include_router(auth.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Task Manager API!"}

