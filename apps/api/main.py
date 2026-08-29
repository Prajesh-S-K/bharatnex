"""FastAPI application for the SMART-MINE prototype command centre."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.routes import router
from apps.api.storage import Database

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "smart_mine.db"


@asynccontextmanager
async def lifespan(application: FastAPI):
    application.state.database = Database(DATA_PATH)
    application.state.database.initialize()
    yield


app = FastAPI(
    title="SMART-MINE AI API",
    version="0.2.0-prototype",
    description="Prototype monitoring and decision-support API; not a certified safety system.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
