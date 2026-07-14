from typing import Literal, Dict, Any
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig

from app.agent.state import AgentState
from app.agent.nodes.entry import entry_node
from app.agent.nodes.router import router_node
from app.agent.nodes.responder import responder_node
from app.agent.tools.registry import TOOL_REGISTRY

def route_tools(state: AgentState) -> str:
    selected_tool = state.get("selected_tool")
    if selected_tool in TOOL_REGISTRY:
        return selected_tool
    return "responder"

builder = StateGraph(AgentState)

# Add core nodes
builder.add_node("entry", entry_node)
builder.add_node("router", router_node)
builder.add_node("responder", responder_node)

# Register tools from registry
for tool_name, tool_data in TOOL_REGISTRY.items():
    builder.add_node(tool_name, tool_data["run"])

# Setup edges
builder.add_edge(START, "entry")
builder.add_edge("entry", "router")

# Map router selections
tool_routing = {tool_name: tool_name for tool_name in TOOL_REGISTRY.keys()}
tool_routing["responder"] = "responder"

builder.add_conditional_edges(
    "router",
    route_tools,
    tool_routing
)

# Connect tools to responder
for tool_name in TOOL_REGISTRY.keys():
    builder.add_edge(tool_name, "responder")

builder.add_edge("responder", END)

# Compile Graph
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

async def run_agent(initial_state: AgentState, config: RunnableConfig | None = None) -> AgentState:
    if config is None:
        config = {"configurable": {"thread_id": "default-session"}}
    return await graph.ainvoke(initial_state, config)
