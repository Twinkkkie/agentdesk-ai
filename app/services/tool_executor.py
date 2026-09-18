from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.schemas.agent import ExecutionResult, ProposedAction


async def execute_actions(actions: list[dict], db: AsyncSession) -> list[ExecutionResult]:
    results: list[ExecutionResult] = []

    for raw in actions:
        action = ProposedAction.model_validate(raw)

        if action.action == "create_task":
            if not action.title:
                results.append(ExecutionResult(action=action.action, ok=False, detail="Missing task title."))
                continue
            task = Task(title=action.title)
            db.add(task)
            await db.flush()
            results.append(
                ExecutionResult(
                    action=action.action,
                    ok=True,
                    detail=f"Created task #{task.id}: {task.title}",
                )
            )
            continue

        if action.action == "set_status":
            if action.task_id is None or action.status is None:
                results.append(
                    ExecutionResult(action=action.action, ok=False, detail="Missing task_id or status.")
                )
                continue
            task = await db.get(Task, action.task_id)
            if task is None:
                results.append(
                    ExecutionResult(
                        action=action.action,
                        ok=False,
                        detail=f"Task #{action.task_id} was not found.",
                    )
                )
                continue
            task.status = action.status.value
            results.append(
                ExecutionResult(
                    action=action.action,
                    ok=True,
                    detail=f"Task #{task.id} status changed to {task.status}.",
                )
            )

    return results
