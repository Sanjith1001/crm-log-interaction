import uuid
from langchain_core.runnables import RunnableConfig
from app.agent.state import AgentState
from app.services import interaction_service

async def run(state: AgentState, config: RunnableConfig) -> AgentState:
    db = config.get("configurable", {}).get("db")
    if not db:
        state["tool_result"] = {"error": "Database session not provided in config"}
        return state

    representative_id = uuid.UUID(state.get("representative_id"))

    interactions = await interaction_service.list_interactions(db, representative_id=representative_id)

    total_visits = len(interactions)
    product_counts = {}
    total_samples = 0
    sample_counts = {}

    for inter in interactions:
        for prod in inter.products:
            product_counts[prod.name] = product_counts.get(prod.name, 0) + 1
        
        for sample in inter.samples_given or []:
            name = sample.get("product_name", "Unknown")
            qty = int(sample.get("qty", 0))
            total_samples += qty
            sample_counts[name] = sample_counts.get(name, 0) + qty

    top_product = "None"
    if product_counts:
        top_product = max(product_counts, key=product_counts.get)

    state["tool_result"] = {
        "total_visits_logged": total_visits,
        "product_discussion_frequency": product_counts,
        "top_product_discussed": top_product,
        "total_samples_distributed": total_samples,
        "sample_distribution_by_product": sample_counts,
        "message": f"Sales Performance Summary generated. Total Visits: {total_visits}. Top Product: {top_product}."
    }
    state["tool_calls_made"].append({
        "tool": "sales_summary",
        "args": {}
    })
    return state
