from app.agent.state import AgentState

TOOL_SCHEMA = {
    "name": "compliance_checker",
    "description": "Check interaction text for compliance concerns.",
}


async def run(state: AgentState) -> AgentState:
    state["tool_result"] = {"flags": []}
    state.setdefault("tool_calls_made", []).append({"tool": "compliance_checker"})
    return state

