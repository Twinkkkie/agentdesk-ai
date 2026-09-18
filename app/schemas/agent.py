from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.agent_run import RunStatus
from app.models.task import TaskStatus


class ProposedAction(BaseModel):
    action: Literal["create_task", "set_status"]
    reason: str = Field(min_length=1, max_length=500)
    task_id: int | None = None
    title: str | None = Field(default=None, max_length=200)
    status: TaskStatus | None = None


class AgentPlan(BaseModel):
    summary: str
    actions: list[ProposedAction] = []


class TriageRequest(BaseModel):
    request: str = Field(min_length=1, max_length=1000)


class AgentRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    request: str
    summary: str
    proposed_actions: list[dict]
    status: RunStatus
    created_at: datetime
    decided_at: datetime | None


class ExecutionResult(BaseModel):
    action: str
    ok: bool
    detail: str
