import json
import uuid
from langchain_core.runnables import RunnableConfig
from app.agent.state import AgentState
from app.agent.llm import call_llm, responder_model_name, router_model_name
from app.agent.prompts.followup_prompt import FOLLOWUP_SYSTEM_PROMPT
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
    hcp_id = None
    if tool_args:
        hcp_name = tool_args.get("hcp_name")
        hcp_id = tool_args.get("hcp_id")

    if not hcp_id and not hcp_name:
        system_prompt = """Extract the doctor's name the user wants recommendations for.
Output a JSON object: {"hcp_name": "doctor name"}
"""
        response_text = await call_llm(
            system_prompt=system_prompt,
            user_prompt=raw_input,
            model=router_model_name(),
            response_format={"type": "json_object"}
        )
        try:
            hcp_name = json.loads(response_text).get("hcp_name", "")
        except Exception:
            hcp_name = raw_input

    hcp = None
    if hcp_id:
        hcp = await hcp_service.get_hcp_by_id(db, uuid.UUID(hcp_id))
    elif hcp_name:
        hcps = await hcp_service.search_hcps(db, query=hcp_name)
        if hcps:
            hcp = hcps[0]

    if not hcp:
        hcps = await hcp_service.search_hcps(db)
        if hcps:
            hcp = hcps[0]
        else:
            state["tool_result"] = {"error": "No HCP found to generate recommendations for."}
            return state

    interactions = await interaction_service.list_interactions(
        db, representative_id=representative_id, hcp_id=hcp.id
    )

    if not interactions:
        state["tool_result"] = {
            "hcp_name": hcp.name,
            "recommendation": f"No past interactions found for {hcp.name}. We recommend a standard introductory meeting to discuss specialty guidelines and preferences."
        }
        return state

    history_lines = []
    for inter in interactions[:5]:
        history_lines.append(
            f"Date: {inter.visit_date}\n"
            f"Products Discussed: {[p.name for p in inter.products]}\n"
            f"Summary: {inter.summary}\n"
            f"Notes: {inter.raw_notes}\n"
            f"Samples Distributed: {inter.samples_given}\n"
            f"Action Items: {inter.action_items}\n"
            f"---"
        )
    history_context = "\n".join(history_lines)

    user_prompt = f"""HCP Name: {hcp.name}
Specialty: {hcp.specialty}
Hospital: {hcp.hospital}

Past Interaction History:
{history_context}
"""
    recommendation = await call_llm(
        system_prompt=FOLLOWUP_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        model=responder_model_name()
    )

    state["tool_result"] = {
        "hcp_name": hcp.name,
        "recommendation": recommendation
    }
    state["tool_calls_made"].append({
        "tool": "followup_recommendation",
        "args": {"hcp_name": hcp.name}
    })
    return state
