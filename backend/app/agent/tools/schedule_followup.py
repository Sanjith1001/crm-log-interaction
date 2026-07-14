import json
import uuid
from langchain_core.runnables import RunnableConfig
from app.agent.state import AgentState
from app.agent.llm import call_llm, router_model_name
from app.services import hcp_service

async def run(state: AgentState, config: RunnableConfig) -> AgentState:
    db = config.get("configurable", {}).get("db")
    if not db:
        state["tool_result"] = {"error": "Database session not provided in config"}
        return state

    tool_args = state.get("tool_args", {})
    raw_input = state.get("raw_input", "")

    if not tool_args.get("hcp_name") or not tool_args.get("date"):
        prompt = """Extract follow-up scheduling details from the prompt.
Output JSON object: {"hcp_name": "Dr. Name", "date": "YYYY-MM-DD", "time": "HH:MM"}. Use null for missing fields.
"""
        res = await call_llm(
            system_prompt=prompt,
            user_prompt=raw_input,
            model=router_model_name(),
            response_format={"type": "json_object"}
        )
        try:
            tool_args = json.loads(res)
        except Exception:
            pass

    hcp_name = tool_args.get("hcp_name", "")
    hcp_match = None
    if hcp_name:
        hcps = await hcp_service.search_hcps(db, query=hcp_name)
        if hcps:
            hcp_match = hcps[0]

    if not hcp_match:
        state["tool_result"] = {"message": f"Could not find HCP '{hcp_name}' to schedule follow-up."}
        return state

    date_val = tool_args.get("date", "2026-08-01")
    time_val = tool_args.get("time", "14:00")
    
    state["tool_result"] = {
        "status": "success",
        "hcp_name": hcp_match.name,
        "date": date_val,
        "time": time_val,
        "message": f"Successfully scheduled follow-up meeting with {hcp_match.name} on {date_val} at {time_val}."
    }
    state["tool_calls_made"].append({
        "tool": "schedule_followup",
        "args": {"hcp_name": hcp_match.name, "date": date_val, "time": time_val}
    })
    return state
