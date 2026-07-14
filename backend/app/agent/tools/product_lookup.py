import json
from langchain_core.runnables import RunnableConfig
from app.agent.state import AgentState
from app.agent.llm import call_llm, router_model_name
from sqlalchemy import select
from app.models.product import Product

async def run(state: AgentState, config: RunnableConfig) -> AgentState:
    db = config.get("configurable", {}).get("db")
    if not db:
        state["tool_result"] = {"error": "Database session not provided in config"}
        return state

    tool_args = state.get("tool_args", {})
    raw_input = state.get("raw_input", "")

    product_name = tool_args.get("product_name", "")
    if not product_name:
        prompt = """Extract the product name the user wants to look up.
Output JSON object: {"product_name": "Product Name"}. Use null if missing.
"""
        res = await call_llm(
            system_prompt=prompt,
            user_prompt=raw_input,
            model=router_model_name(),
            response_format={"type": "json_object"}
        )
        try:
            product_name = json.loads(res).get("product_name", "")
        except Exception:
            product_name = raw_input

    if not product_name:
        state["tool_result"] = {"message": "Please specify a product name to look up."}
        return state

    stmt = select(Product)
    res = await db.execute(stmt)
    all_products = res.scalars().all()
    
    product_match = None
    for p in all_products:
        if p.name.lower() in product_name.lower() or product_name.lower() in p.name.lower():
            product_match = p
            break

    if not product_match:
        state["tool_result"] = {"message": f"Could not find product matching '{product_name}'."}
        return state

    details = {
        "Ozempic": {
            "class": "GLP-1 Receptor Agonist",
            "indication": "Type 2 Diabetes mellitus, Cardiovascular risk reduction",
            "dosage": "0.25mg to 2.0mg injected subcutaneously once weekly",
            "stock_inventory": 420
        },
        "Keytruda": {
            "class": "PD-1 Inhibitor (Immunotherapy)",
            "indication": "Melanoma, Non-Small Cell Lung Cancer, HNSCC, Hodgkin Lymphoma",
            "dosage": "200mg IV infusion every 3 weeks",
            "stock_inventory": 150
        },
        "Januvia": {
            "class": "DPP-4 Inhibitor",
            "indication": "Type 2 Diabetes mellitus glycemic control",
            "dosage": "100mg orally once daily",
            "stock_inventory": 850
        },
        "Lipitor": {
            "class": "HMG-CoA Reductase Inhibitor (Statin)",
            "indication": "Hypercholesterolemia, Cardiovascular disease prevention",
            "dosage": "10mg to 80mg orally once daily",
            "stock_inventory": 1200
        }
    }.get(product_match.name, {
        "class": "General Therapeutics",
        "indication": "General clinical indications",
        "dosage": "As directed by physician",
        "stock_inventory": 100
    })

    state["tool_result"] = {
        "id": str(product_match.id),
        "name": product_match.name,
        "class": details["class"],
        "indication": details["indication"],
        "dosage": details["dosage"],
        "stock_inventory": details["stock_inventory"]
    }
    state["tool_calls_made"].append({
        "tool": "product_lookup",
        "args": {"product_name": product_match.name}
    })
    return state
