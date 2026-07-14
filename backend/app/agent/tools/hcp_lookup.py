import json
import uuid
from langchain_core.runnables import RunnableConfig
from app.agent.state import AgentState
from app.agent.llm import call_llm, router_model_name
from app.services import hcp_service, interaction_service

async def run(state: AgentState, config: RunnableConfig) -> AgentState:
    db = config.get("configurable", {}).get("db")
    if not db:
        state["tool_result"] = {"error": "Database session not provided in config"}
        return state

    tool_args = state.get("tool_args", {})
    raw_input = state.get("raw_input", "")
    representative_id = uuid.UUID(state.get("representative_id"))

    hcp_name = None
    if tool_args and "name" in tool_args:
        hcp_name = tool_args["name"]

    if not hcp_name:
        system_prompt = """Extract the name of the Healthcare Professional (HCP) or doctor the user wants to lookup.
Output a JSON object: {"name": "doctor name"}
"""
        response_text = await call_llm(
            system_prompt=system_prompt,
            user_prompt=raw_input,
            model=router_model_name(),
            response_format={"type": "json_object"}
        )
        try:
            hcp_name = json.loads(response_text).get("name", "")
        except Exception:
            hcp_name = raw_input

    hcps = await hcp_service.search_hcps(db, query=hcp_name)
    if not hcps:
        state["tool_result"] = {"message": f"No HCP found matching '{hcp_name}'."}
        return state

    hcp = hcps[0]
    interactions = await interaction_service.list_interactions(
        db, representative_id=representative_id, hcp_id=hcp.id
    )

    recent = []
    for inter in interactions[:3]:
        recent.append({
            "visit_date": str(inter.visit_date),
            "summary": inter.summary,
            "products_discussed": [p.name for p in inter.products]
        })

    state["tool_result"] = {
        "hcp": {
            "id": str(hcp.id),
            "name": hcp.name,
            "specialty": hcp.specialty,
            "hospital": hcp.hospital,
            "city": hcp.city,
            "prescription_preferences": hcp.prescription_preferences
        },
        "recent_interactions": recent
    }
    state["tool_calls_made"].append({
        "tool": "hcp_lookup",
        "args": {"name": hcp.name}
    })
    return state
