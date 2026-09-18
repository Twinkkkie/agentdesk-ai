from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from app.services.planner import plan_tasks


class AgentState(TypedDict):
    request: str
    tasks: list[dict[str, Any]]
    summary: str
    proposed_actions: list[dict[str, Any]]


async def analyze(state: AgentState) -> dict:
    plan = await plan_tasks(state["request"], state["tasks"])
    return {
        "summary": plan.summary,
        "proposed_actions": [action.model_dump(mode="json") for action in plan.actions],
    }


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("analyze", analyze)
    graph.set_entry_point("analyze")
    graph.add_edge("analyze", END)
    return graph.compile()


triage_graph = build_graph()
