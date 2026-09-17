from fastapi import FastAPI

from app.api.routes import agent, health, tasks
from app.core.config import settings

app = FastAPI(title=settings.app_name, version="0.1.0")

app.include_router(health.router)
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(agent.router, prefix="/api/v1")
