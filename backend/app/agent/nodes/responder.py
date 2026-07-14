import json
from app.agent.state import AgentState
from app.agent.llm import call_llm, responder_model_name

async def responder_node(state: AgentState) -> AgentState:
    selected_tool = state.get("selected_tool")
    tool_result = state.get("tool_result")
    pending_confirmation = state.get("pending_confirmation")
    raw_input = state.get("raw_input", "")

    system_prompt = """You are a helpful, professional AI assistant inside an AI-first pharma CRM.
Your task is to take the result of the tool the agent executed (or the current state) and write a brief, friendly, and professional response to the representative.
Keep it concise and clear. Highlight key actions taken, dates, and products.
Do NOT output any raw UUIDs to the user.
Format output using Markdown.
"""

    if pending_confirmation:
        # The agent proposed an edit and needs confirmation
        diff_data = pending_confirmation.get("diff", {})
        diff_str = "\n".join([f"- **{k}**: {v['before']} ➔ {v['after']}" for k, v in diff_data.items()])
        
        user_prompt = f"""An edit has been requested, but requires confirmation.
Here are the proposed changes:
{diff_str}

Please generate a friendly message presenting these changes and asking the representative if they would like to confirm or cancel the edit.
"""
        response_text = await call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=responder_model_name()
        )
        state["final_response"] = response_text
        return state

    if not selected_tool:
        # No tool was matched, clarify user intent
        user_prompt = f"""The user said: "{raw_input}"
We did not match any specific tools. Write a friendly response asking for clarification. Offer examples of what they can do (log a visit, edit an interaction, search, look up HCP profiles, or get recommendations).
"""
        response_text = await call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=responder_model_name()
        )
        state["final_response"] = response_text
        return state

    # Synthesize standard tool success responses
    user_prompt = f"""The user said: "{raw_input}"
We executed the tool: "{selected_tool}".
Here is the result of the tool execution:
{json.dumps(tool_result, default=str)}

Please write a brief, professional summary confirming the action was completed. Mention specific details (e.g. HCP name, products, follow-up date).
"""
    response_text = await call_llm(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        model=responder_model_name()
    )
    state["final_response"] = response_text
    return state
