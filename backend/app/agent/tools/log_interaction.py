import json
import uuid
from datetime import date
from langchain_core.runnables import RunnableConfig
from app.agent.state import AgentState
from app.agent.llm import call_llm, router_model_name
from app.agent.prompts.extraction_prompt import EXTRACTION_SYSTEM_PROMPT
from app.services import interaction_service, hcp_service
from app.models.product import Product
from app.schemas.interaction import InteractionCreate
from sqlalchemy import select

async def run(state: AgentState, config: RunnableConfig) -> AgentState:
    db = config.get("configurable", {}).get("db")
    if not db:
        state["tool_result"] = {"error": "Database session not provided in config"}
        return state
        
    tool_args = state.get("tool_args", {})
    raw_input = state.get("raw_input", "")
    representative_id = uuid.UUID(state.get("representative_id"))

    # Form Mode Submit
    if tool_args and "form_data" in tool_args:
        form_data = tool_args["form_data"]
        hcp_id = uuid.UUID(form_data["hcp_id"])
        products_discussed = [uuid.UUID(p) for p in form_data.get("products_discussed", [])]
        samples_given = form_data.get("samples_given", [])
        action_items = form_data.get("action_items", [])
        
        visit_date = date.today()
        if form_data.get("visit_date"):
            visit_date = date.fromisoformat(form_data["visit_date"])
            
        follow_up_date = None
        if form_data.get("follow_up_date"):
            follow_up_date = date.fromisoformat(form_data["follow_up_date"])
            
        raw_notes = form_data.get("notes", "")
        summary = form_data.get("summary") or "Logged via Structured Form."

        interaction_in = InteractionCreate(
            hcp_id=hcp_id,
            visit_date=visit_date,
            raw_notes=raw_notes,
            summary=summary,
            extracted_entities={
                "hcp_name": form_data.get("hcp_name"),
                "samples_given": samples_given,
                "action_items": action_items
            },
            samples_given=samples_given,
            action_items=action_items,
            follow_up_date=follow_up_date,
            source="form",
            products_discussed=products_discussed
        )
        
        interaction = await interaction_service.create_interaction(db, interaction_in, representative_id)
        state["tool_result"] = {
            "id": str(interaction.id),
            "hcp_name": interaction.hcp.name,
            "visit_date": str(interaction.visit_date),
            "summary": interaction.summary
        }
        state["tool_calls_made"].append({
            "tool": "log_interaction",
            "args": {"source": "form", "hcp_id": str(hcp_id)}
        })
        return state

    # Chat Mode Entity Extraction
    response_text = await call_llm(
        system_prompt=EXTRACTION_SYSTEM_PROMPT,
        user_prompt=raw_input,
        model=router_model_name(),
        response_format={"type": "json_object"}
    )

    try:
        extracted = json.loads(response_text)
    except Exception:
        extracted = {}

    hcp_name = extracted.get("hcp_name", "")
    hcp = None
    if hcp_name:
        hcps = await hcp_service.search_hcps(db, query=hcp_name)
        if hcps:
            hcp = hcps[0]
            
    if not hcp:
        # Fallback to first available HCP
        hcps = await hcp_service.search_hcps(db)
        if hcps:
            hcp = hcps[0]
        else:
            state["tool_result"] = {"error": "No Healthcare Professional found to associate with."}
            return state

    products_discussed = []
    extracted_products = extracted.get("products", [])
    for prod_name in extracted_products:
        result = await db.execute(select(Product).where(Product.name.ilike(f"%{prod_name}%")))
        p = result.scalar_one_or_none()
        if p:
            products_discussed.append(p.id)

    visit_date = date.today()
    if extracted.get("visit_date"):
        try:
            visit_date = date.fromisoformat(extracted["visit_date"])
        except ValueError:
            pass
            
    follow_up_date = None
    if extracted.get("follow_up_date"):
        try:
            follow_up_date = date.fromisoformat(extracted["follow_up_date"])
        except ValueError:
            pass

    interaction_in = InteractionCreate(
        hcp_id=hcp.id,
        visit_date=visit_date,
        raw_notes=raw_input,
        summary=extracted.get("summary", "Meeting logged via Chat."),
        extracted_entities=extracted,
        samples_given=extracted.get("samples_given", []),
        action_items=extracted.get("action_items", []),
        follow_up_date=follow_up_date,
        source="chat",
        products_discussed=products_discussed
    )

    interaction = await interaction_service.create_interaction(db, interaction_in, representative_id)
    state["tool_result"] = {
        "id": str(interaction.id),
        "hcp_name": interaction.hcp.name,
        "visit_date": str(interaction.visit_date),
        "summary": interaction.summary,
        "extracted_entities": extracted
    }
    state["tool_calls_made"].append({
        "tool": "log_interaction",
        "args": extracted
    })
    return state
