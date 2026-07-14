import json
from app.agent.state import AgentState
from app.agent.llm import call_llm, router_model_name
from app.agent.prompts.router_prompt import ROUTER_SYSTEM_PROMPT

async def router_node(state: AgentState) -> AgentState:
    input_mode = state.get("input_mode", "chat")
    raw_input = state.get("raw_input", "")
    
    if not raw_input:
        state["selected_tool"] = None
        state["tool_args"] = None
        return state

    # If the input is from Structured Form, route deterministically
    if input_mode == "form":
        try:
            payload = json.loads(raw_input)
            if payload.get("id"):
                state["selected_tool"] = "edit_interaction"
                state["tool_args"] = {
                    "interaction_id": payload.get("id"),
                    "data": payload
                }
            else:
                state["selected_tool"] = "log_interaction"
                state["tool_args"] = {
                    "form_data": payload
                }
            return state
        except Exception:
            pass

    # Chat mode LLM routing
    user_msg = f"Current user input: {raw_input}"
    if state.get("messages"):
        history = []
        for msg in state["messages"][-5:]:
            if hasattr(msg, "type"):
                role = msg.type
                content = getattr(msg, "content", "")
            elif isinstance(msg, dict):
                role = msg.get("role", "user")
                content = msg.get("content", "")
            else:
                role = "user"
                content = str(msg)
            history.append(f"{role.capitalize()}: {content}")
        user_msg = "Conversation history:\n" + "\n".join(history) + f"\n\nCurrent user input: {raw_input}"

    response_text = await call_llm(
        system_prompt=ROUTER_SYSTEM_PROMPT,
        user_prompt=user_msg,
        model=router_model_name(),
        response_format={"type": "json_object"}
    )

    try:
        data = json.loads(response_text)
        state["selected_tool"] = data.get("selected_tool")
        state["tool_args"] = data.get("tool_args")
    except Exception:
        state["selected_tool"] = None
        state["tool_args"] = None

    return state
