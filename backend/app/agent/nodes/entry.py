from app.agent.state import AgentState

async def entry_node(state: AgentState) -> AgentState:
    # Ensure tool_calls_made is initialized in state
    if "tool_calls_made" not in state or state["tool_calls_made"] is None:
        state["tool_calls_made"] = []
    
    # Simple pass-through or normalization if needed
    return state
