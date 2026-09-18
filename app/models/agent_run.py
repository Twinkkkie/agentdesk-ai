from datetime import datetime, timezone
from enum import StrEnum

from sqlalchemy import DateTime, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RunStatus(StrEnum):
    proposed = "proposed"
    rejected = "rejected"
    executed = "executed"


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    request: Mapped[str] = mapped_column(Text())
    summary: Mapped[str] = mapped_column(Text())
    proposed_actions: Mapped[list[dict]] = mapped_column(JSON(), default=list)
    status: Mapped[str] = mapped_column(String(32), default=RunStatus.proposed.value, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
