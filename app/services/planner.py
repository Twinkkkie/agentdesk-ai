import logging
import re
from typing import Any

from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.models.task import TaskStatus
from app.schemas.agent import AgentPlan, ProposedAction

logger = logging.getLogger(__name__)


def _fallback_plan(request: str, tasks: list[dict[str, Any]]) -> AgentPlan:
    text = request.lower()
    actions: list[ProposedAction] = []

    id_match = re.search(r"(?:task\s*)?#?(\d+)", text)
    if id_match:
        task_id = int(id_match.group(1))
        known_ids = {int(task["id"]) for task in tasks}
        if task_id in known_ids:
            if any(word in text for word in ("done", "complete", "completed", "finish", "finished")):
                actions.append(
                    ProposedAction(
                        action="set_status",
                        task_id=task_id,
                        status=TaskStatus.done,
                        reason="The request explicitly asks to complete this task.",
                    )
                )
            elif any(word in text for word in ("start", "progress", "work on")):
                actions.append(
                    ProposedAction(
                        action="set_status",
                        task_id=task_id,
                        status=TaskStatus.in_progress,
                        reason="The request explicitly asks to start work on this task.",
                    )
                )

    create_match = re.search(r"(?:create|add)\s+(?:a\s+)?task[:\s]+(.+)", request, re.IGNORECASE)
    if create_match:
        title = create_match.group(1).strip().strip(".")
        if title:
            actions.append(
                ProposedAction(
                    action="create_task",
                    title=title[:200],
                    reason="The request explicitly asks to create a task.",
                )
            )

    summary = (
        f"Reviewed {len(tasks)} open task(s). "
        + (f"Prepared {len(actions)} action proposal(s)." if actions else "No safe mutation was inferred.")
    )
    return AgentPlan(summary=summary, actions=actions)


async def plan_tasks(request: str, tasks: list[dict[str, Any]]) -> AgentPlan:
    if not settings.openai_api_key:
        return _fallback_plan(request, tasks)

    prompt = f"""
You are a task-planning assistant. You may only propose actions; never claim that an action
has already been executed.

Allowed actions:
- create_task: requires a title
- set_status: requires an existing task_id and status of todo, in_progress, or done

User request:
{request}

Current open tasks:
{tasks}

Return a concise summary and only actions that are directly supported by the request.
"""
    try:
        llm = ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            temperature=0,
        )
        structured = llm.with_structured_output(AgentPlan)
        result = await structured.ainvoke(prompt)
        return AgentPlan.model_validate(result)
    except Exception as exc:
        logger.warning("LLM planning failed; using deterministic fallback: %s", exc)
        return _fallback_plan(request, tasks)
