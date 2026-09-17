from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.graph import triage_graph
from app.db.session import get_db
from app.models.task import Task, TaskStatus

router = APIRouter(prefix="/agent", tags=["agent"])


class TriageRequest(BaseModel):
    request: str = Field(min_length=1, max_length=1000)


@router.post("/triage")
async def triage(payload: TriageRequest, db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(Task).where(Task.status != TaskStatus.done))
    tasks = list(result.scalars().all())
    state = triage_graph.invoke(
        {
            "request": payload.request,
            "task_titles": [task.title for task in tasks],
            "summary": "",
            "proposed_actions": [],
        }
    )
    return {
        "summary": state["summary"],
        "proposed_actions": state["proposed_actions"],
        "requires_human_approval": True,
    }
