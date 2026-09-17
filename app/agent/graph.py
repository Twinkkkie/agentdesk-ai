from typing import TypedDict

from langgraph.graph import END, StateGraph


class AgentState(TypedDict):
    request: str
    task_titles: list[str]
    summary: str
    proposed_actions: list[dict[str, str | int | bool]]


def analyze(state: AgentState) -> AgentState:
    open_count = len(state["task_titles"])
    state["summary"] = f"Analyzed {open_count} open task(s) for request: {state['request']}"
    state["proposed_actions"] = [
        {
            "action": "review_priorities",
            "reason": "Prioritize open work before making changes.",
            "requires_approval": True,
        }
    ]
    return state


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("analyze", analyze)
    graph.set_entry_point("analyze")
    graph.add_edge("analyze", END)
    return graph.compile()


triage_graph = build_graph()
