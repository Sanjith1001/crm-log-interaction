import json
import uuid
from langchain_core.runnables import RunnableConfig
from app.agent.state import AgentState
from app.agent.llm import call_llm, router_model_name
from app.services import interaction_service

async def run(state: AgentState, config: RunnableConfig) -> AgentState:
    db = config.get("configurable", {}).get("db")
    if not db:
        state["tool_result"] = {"error": "Database session not provided in config"}
        return state

    tool_args = state.get("tool_args", {})
    raw_input = state.get("raw_input", "")
    representative_id = uuid.UUID(state.get("representative_id"))

    query_str = None
    if tool_args and "query" in tool_args:
        query_str = tool_args["query"]
        
    if not query_str:
        system_prompt = """You are a search query extractor. Extract the main search terms, doctor name, or product name the user wants to search for in their past interactions.
Output a JSON object: {"query": "search query text"}
"""
        response_text = await call_llm(
            system_prompt=system_prompt,
            user_prompt=raw_input,
            model=router_model_name(),
            response_format={"type": "json_object"}
        )
        try:
            query_str = json.loads(response_text).get("query", "")
        except Exception:
            query_str = raw_input

    interactions = await interaction_service.list_interactions(
        db, representative_id=representative_id, query=query_str
    )

    results = []
    for inter in interactions:
        results.append({
            "id": str(inter.id),
            "hcp_name": inter.hcp.name,
            "visit_date": str(inter.visit_date),
            "summary": inter.summary,
            "products_discussed": [p.name for p in inter.products],
            "samples_given": inter.samples_given,
            "follow_up_date": str(inter.follow_up_date) if inter.follow_up_date else None
        })

    state["tool_result"] = {
        "search_query": query_str,
        "results": results[:5]
    }
    state["tool_calls_made"].append({
        "tool": "search_interaction",
        "args": {"query": query_str}
    })
    return state
