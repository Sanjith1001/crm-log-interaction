from app.agent.state import AgentState

TOOL_SCHEMA = {
    "name": "email_summary",
    "description": "Format an interaction summary email.",
}


async def run(state: AgentState) -> AgentState:
    state["tool_result"] = {"email": None}
    state.setdefault("tool_calls_made", []).append({"tool": "email_summary"})
    return state

