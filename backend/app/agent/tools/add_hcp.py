import json
import uuid
from langchain_core.runnables import RunnableConfig
from app.agent.state import AgentState
from app.agent.llm import call_llm, router_model_name
from app.services import hcp_service
from app.schemas.hcp import HcpCreate

async def run(state: AgentState, config: RunnableConfig) -> AgentState:
    db = config.get("configurable", {}).get("db")
    if not db:
        state["tool_result"] = {"error": "Database session not provided in config"}
        return state

    tool_args = state.get("tool_args", {})
    raw_input = state.get("raw_input", "")

    if not tool_args.get("name"):
        prompt = """Extract details of the new Healthcare Professional (HCP) or doctor to add to our database.
Output JSON object: {"name": "Dr. Name", "specialty": "Specialty Name", "hospital": "Hospital Name", "city": "City Name"}. Use null for missing fields.
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

    name = tool_args.get("name")
    if not name:
        state["tool_result"] = {"message": "Please specify at least a name to add a new doctor."}
        return state

    if not name.lower().startswith("dr.") and not name.lower().startswith("dr "):
        name = "Dr. " + name

    specialty = tool_args.get("specialty") or "General Medicine"
    hospital = tool_args.get("hospital") or "City Hospital"
    city = tool_args.get("city") or "Local"

    hcp_in = HcpCreate(
        id=uuid.uuid4(),
        name=name,
        specialty=specialty,
        hospital=hospital,
        city=city,
        prescription_preferences={
            "brand_preference": "None",
            "patient_volume": "medium",
            "notes": "Added via AI Chatbot Assistant."
        }
    )

    new_doc = await hcp_service.create_hcp(db, hcp_in)

    state["tool_result"] = {
        "status": "success",
        "id": str(new_doc.id),
        "name": new_doc.name,
        "specialty": new_doc.specialty,
        "hospital": new_doc.hospital,
        "city": new_doc.city,
        "message": f"Successfully created new doctor profile: {new_doc.name} ({new_doc.specialty}) at {new_doc.hospital}."
    }
    state["tool_calls_made"].append({
        "tool": "add_hcp",
        "args": {"name": new_doc.name, "specialty": new_doc.specialty}
    })
    return state
