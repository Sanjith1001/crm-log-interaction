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

    hcp_name = tool_args.get("hcp_name", "")
    if not hcp_name:
        prompt = """Extract the doctor or HCP name the user wants to run a compliance audit on.
Output JSON object: {"hcp_name": "Doctor Name"}. Use null if missing.
"""
        res = await call_llm(
            system_prompt=prompt,
            user_prompt=raw_input,
            model=router_model_name(),
            response_format={"type": "json_object"}
        )
        try:
            hcp_name = json.loads(res).get("hcp_name", "")
        except Exception:
            hcp_name = raw_input

    if not hcp_name:
        state["tool_result"] = {"message": "Please specify a doctor name to run a compliance audit."}
        return state

    hcps = await hcp_service.search_hcps(db, query=hcp_name)
    if not hcps:
        state["tool_result"] = {"message": f"No HCP found matching '{hcp_name}'."}
        return state

    hcp = hcps[0]
    interactions = await interaction_service.list_interactions(
        db, representative_id=representative_id, hcp_id=hcp.id
    )

    total_samples = 0
    sample_breakdown = {}
    for inter in interactions:
        for sample in inter.samples_given or []:
            name = sample.get("product_name", "Unknown")
            qty = int(sample.get("qty", 0))
            total_samples += qty
            sample_breakdown[name] = sample_breakdown.get(name, 0) + qty

    is_compliant = total_samples <= 20
    status_msg = "COMPLIANT" if is_compliant else "NON-COMPLIANT (Limit of 20 units exceeded)"

    state["tool_result"] = {
        "hcp_name": hcp.name,
        "specialty": hcp.specialty,
        "hospital": hcp.hospital,
        "total_samples_given": total_samples,
        "sample_breakdown": sample_breakdown,
        "compliance_status": status_msg,
        "is_compliant": is_compliant,
        "message": f"Compliance Audit completed for {hcp.name}. Status: {status_msg}."
    }
    state["tool_calls_made"].append({
        "tool": "compliance_audit",
        "args": {"hcp_name": hcp.name}
    })
    return state
