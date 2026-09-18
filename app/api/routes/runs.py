from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.agent_run import AgentRun, RunStatus
from app.schemas.agent import AgentRunRead, ExecutionResult
from app.services.tool_executor import execute_actions

router = APIRouter(prefix="/agent/runs", tags=["agent-runs"])


@router.get("", response_model=list[AgentRunRead])
async def list_runs(db: AsyncSession = Depends(get_db)) -> list[AgentRun]:
    result = await db.execute(select(AgentRun).order_by(AgentRun.id.desc()).limit(100))
    return list(result.scalars().all())


@router.get("/{run_id}", response_model=AgentRunRead)
async def get_run(run_id: int, db: AsyncSession = Depends(get_db)) -> AgentRun:
    run = await db.get(AgentRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Agent run not found")
    return run


@router.post("/{run_id}/approve", response_model=list[ExecutionResult])
async def approve_run(run_id: int, db: AsyncSession = Depends(get_db)) -> list[ExecutionResult]:
    run = await db.get(AgentRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Agent run not found")
    if run.status != RunStatus.proposed.value:
        raise HTTPException(status_code=409, detail="Agent run has already been decided")

    results = await execute_actions(run.proposed_actions, db)
    run.status = RunStatus.executed.value
    run.decided_at = datetime.now(timezone.utc)
    await db.commit()
    return results


@router.post("/{run_id}/reject", response_model=AgentRunRead)
async def reject_run(run_id: int, db: AsyncSession = Depends(get_db)) -> AgentRun:
    run = await db.get(AgentRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Agent run not found")
    if run.status != RunStatus.proposed.value:
        raise HTTPException(status_code=409, detail="Agent run has already been decided")

    run.status = RunStatus.rejected.value
    run.decided_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(run)
    return run
