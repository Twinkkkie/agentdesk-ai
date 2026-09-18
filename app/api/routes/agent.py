from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.graph import triage_graph
from app.db.session import get_db
from app.models.agent_run import AgentRun
from app.models.task import Task, TaskStatus
from app.schemas.agent import AgentRunRead, TriageRequest

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/triage", response_model=AgentRunRead, status_code=status.HTTP_201_CREATED)
async def triage(payload: TriageRequest, db: AsyncSession = Depends(get_db)) -> AgentRun:
    result = await db.execute(select(Task).where(Task.status != TaskStatus.done.value))
    tasks = list(result.scalars().all())

    state = await triage_graph.ainvoke(
        {
            "request": payload.request,
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                }
                for task in tasks
            ],
            "summary": "",
            "proposed_actions": [],
        }
    )

    run = AgentRun(
        request=payload.request,
        summary=state["summary"],
        proposed_actions=state["proposed_actions"],
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return run
