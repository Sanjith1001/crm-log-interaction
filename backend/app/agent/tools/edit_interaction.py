import json
import uuid
from datetime import date
from langchain_core.runnables import RunnableConfig
from app.agent.state import AgentState
from app.agent.llm import call_llm, router_model_name
from app.services import interaction_service, hcp_service
from app.models.product import Product
from sqlalchemy import select

async def run(state: AgentState, config: RunnableConfig) -> AgentState:
    db = config.get("configurable", {}).get("db")
    if not db:
        state["tool_result"] = {"error": "Database session not provided in config"}
        return state

    tool_args = state.get("tool_args", {})
    raw_input = state.get("raw_input", "").lower().strip()
    representative_id = uuid.UUID(state.get("representative_id"))
    pending = state.get("pending_confirmation")

    # 1. Confirmation flow
    if pending and pending.get("tool") == "edit_interaction":
        if any(word in raw_input for word in ["yes", "confirm", "ok", "approve", "do it"]):
            interaction_id = uuid.UUID(pending["args"]["interaction_id"])
            update_data = pending["args"]["data"]
            
            if "products_discussed" in update_data:
                update_data["products_discussed"] = [uuid.UUID(p) for p in update_data["products_discussed"]]
                
            interaction = await interaction_service.update_interaction(
                db, interaction_id, update_data, representative_id
            )
            # Fetch fresh HCP name to bypass cached relationship values
            hcp_obj = await hcp_service.get_hcp_by_id(db, interaction.hcp_id)
            hcp_name = hcp_obj.name if hcp_obj else interaction.hcp.name

            state["tool_result"] = {
                "message": "Interaction updated successfully.",
                "id": str(interaction.id),
                "hcp_name": hcp_name,
                "visit_date": str(interaction.visit_date),
                "updated_fields": list(update_data.keys())
            }
            state["pending_confirmation"] = None
            state["tool_calls_made"].append({
                "tool": "edit_interaction",
                "args": {
                    "interaction_id": str(interaction_id),
                    "status": "confirmed",
                    "data": update_data
                }
            })
            return state
        elif any(word in raw_input for word in ["no", "cancel", "stop", "abort"]):
            state["tool_result"] = {"message": "Edit cancelled by user."}
            state["pending_confirmation"] = None
            state["tool_calls_made"].append({
                "tool": "edit_interaction",
                "args": {"status": "cancelled"}
            })
            return state

    # 2. Form Mode Edit
    if state.get("input_mode") == "form" and tool_args:
        interaction_id = uuid.UUID(tool_args["interaction_id"])
        update_data = tool_args["data"]
        
        if "products_discussed" in update_data:
            update_data["products_discussed"] = [uuid.UUID(p) for p in update_data["products_discussed"]]
            
        interaction = await interaction_service.update_interaction(
            db, interaction_id, update_data, representative_id
        )
        state["tool_result"] = {
            "message": "Form edit saved successfully.",
            "id": str(interaction.id),
            "hcp_name": interaction.hcp.name,
            "visit_date": str(interaction.visit_date),
            "summary": interaction.summary
        }
        state["tool_calls_made"].append({
            "tool": "edit_interaction",
            "args": {"interaction_id": str(interaction_id), "mode": "form"}
        })
        return state

    # 3. Chat Mode Edit Request
    interactions = await interaction_service.list_interactions(db, representative_id=representative_id)
    if not interactions:
        state["tool_result"] = {"error": "No interactions found to edit."}
        return state

    target_interaction = interactions[0]
    existing_entities = dict(target_interaction.extracted_entities or {})

    system_prompt = f"""You are an editing assistant. The user wants to edit an interaction.
Here is the existing interaction data:
- HCP: {target_interaction.hcp.name}
- Specialty: {target_interaction.hcp.specialty}
- Date: {target_interaction.visit_date}
- Products: {[p.name for p in target_interaction.products]}
- Notes: {target_interaction.raw_notes}
- Summary: {target_interaction.summary}
- Samples given: {target_interaction.samples_given}
- Action items: {target_interaction.action_items}
- Follow up date: {target_interaction.follow_up_date}
- Sentiment: {existing_entities.get("sentiment", "Positive")}
- Materials shared: {existing_entities.get("materials_shared", [])}
- Outcomes: {existing_entities.get("outcomes", "")}

Analyze the user's edit request and output a JSON object containing ONLY the fields that should be changed and their new values. Keep everything else exactly the same.
Fields:
- `hcp_name` (text, e.g. "Dr. John" or "Dr. Smith")
- `visit_date` (YYYY-MM-DD)
- `raw_notes` (text)
- `summary` (text)
- `samples_given` (list of dicts)
- `action_items` (list of dicts)
- `follow_up_date` (YYYY-MM-DD)
- `products_discussed` (list of product names to search and add)
- `sentiment` ("Positive", "Neutral", or "Negative")
- `materials_shared` (list of strings, e.g. ["Brochures."])
- `outcomes` (text)

Output format:
{{
  "changes": {{
     "fieldname": "new value"
  }}
}}
"""
    edit_request = state.get("raw_input", "")
    response_text = await call_llm(
        system_prompt=system_prompt,
        user_prompt=f"User edit request: {edit_request}",
        model=router_model_name(),
        response_format={"type": "json_object"}
    )

    try:
        changes_data = json.loads(response_text).get("changes", {})
    except Exception:
        changes_data = {}

    if not changes_data:
        state["tool_result"] = {"error": "Could not identify any changes to apply."}
        return state

    # Parse and update hcp_name mapping to hcp_id
    diff = {}
    if "hcp_name" in changes_data:
        new_hcp_name = changes_data["hcp_name"]
        hcps = await hcp_service.search_hcps(db, query=new_hcp_name)
        if hcps:
            matched_hcp = hcps[0]
            changes_data["hcp_id"] = str(matched_hcp.id)
            diff["hcp_name"] = {
                "before": target_interaction.hcp.name,
                "after": matched_hcp.name
            }
            del changes_data["hcp_name"]

    # Handle products discussed mapping
    if "products_discussed" in changes_data:
        prod_uuids = []
        for name in changes_data["products_discussed"]:
            res = await db.execute(select(Product).where(Product.name.ilike(f"%{name}%")))
            p = res.scalar_one_or_none()
            if p:
                prod_uuids.append(str(p.id))
        changes_data["products_discussed"] = prod_uuids

        old_val = [p.name for p in target_interaction.products]
        prod_names = []
        for uid in prod_uuids:
            res = await db.execute(select(Product).where(Product.id == uuid.UUID(uid)))
            p = res.scalar_one_or_none()
            if p:
                prod_names.append(p.name)
        diff["products_discussed"] = {
            "before": old_val,
            "after": prod_names
        }

    # Merge custom details (sentiment, materials_shared, outcomes) into extracted_entities
    updated_entities = False
    for k in ["sentiment", "materials_shared", "outcomes"]:
        if k in changes_data:
            existing_entities[k] = changes_data[k]
            updated_entities = True
            diff[k] = {
                "before": target_interaction.extracted_entities.get(k) if target_interaction.extracted_entities else None,
                "after": changes_data[k]
            }
            del changes_data[k]

    if updated_entities:
        changes_data["extracted_entities"] = existing_entities

    # Add standard fields diffs
    for key, new_val in list(changes_data.items()):
        if key in ["extracted_entities", "products_discussed", "hcp_id"]:
            continue
        old_val = getattr(target_interaction, key, None)
        diff[key] = {
            "before": str(old_val) if old_val else "None",
            "after": str(new_val)
        }

    state["pending_confirmation"] = {
        "tool": "edit_interaction",
        "args": {
            "interaction_id": str(target_interaction.id),
            "data": changes_data
        },
        "diff": diff
    }
    
    state["tool_result"] = {"pending": True, "diff": diff}
    return state
