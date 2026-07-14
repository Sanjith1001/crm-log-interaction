import json
import uuid
import asyncio
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import CurrentRep, current_rep, get_db_session
from app.schemas.agent import AgentInvokeRequest
from app.agent.graph import graph

router = APIRouter(tags=["agent"])

@router.post("/agent/invoke")
async def invoke_agent(
    payload: AgentInvokeRequest,
    db: AsyncSession = Depends(get_db_session),
    rep: CurrentRep = Depends(current_rep)
):
    async def event_generator():
        yield f"data: {json.dumps({'event': 'status', 'text': 'Agent routing...'})}\n\n"
        
        config = {
            "configurable": {
                "thread_id": payload.session_id,
                "db": db
            }
        }
        
        state_info = await graph.aget_state(config)
        current_messages = []
        pending_conf = None
        
        if state_info and state_info.values:
            current_messages = state_info.values.get("messages", [])
            pending_conf = state_info.values.get("pending_confirmation")

        initial_state = {
            "messages": current_messages + [{"role": "user", "content": payload.raw_input}],
            "input_mode": payload.input_mode,
            "raw_input": payload.raw_input,
            "representative_id": str(rep.id),
            "tool_calls_made": [],
            "pending_confirmation": pending_conf
        }

        try:
            final_state = await graph.ainvoke(initial_state, config)
            
            selected_tool = final_state.get("selected_tool")
            tool_args = final_state.get("tool_args")
            tool_result = final_state.get("tool_result")
            tool_calls = final_state.get("tool_calls_made", [])
            pending_confirmation = final_state.get("pending_confirmation")
            
            if selected_tool:
                yield f"data: {json.dumps({'event': 'tool_start', 'tool': selected_tool, 'args': tool_args})}\n\n"
                await asyncio.sleep(0.5)
                yield f"data: {json.dumps({'event': 'tool_end', 'tool': selected_tool, 'output': tool_result})}\n\n"

            response_text = final_state.get("final_response", "")
            
            # Stream response word-by-word
            words = response_text.split(" ")
            for i, word in enumerate(words):
                space = " " if i > 0 else ""
                yield f"data: {json.dumps({'event': 'token', 'token': space + word})}\n\n"
                await asyncio.sleep(0.03)

            yield f"data: {json.dumps({'event': 'final', 'text': response_text, 'tool_calls': tool_calls, 'pending_confirmation': pending_confirmation})}\n\n"
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print("Agent execution error:", error_trace)
            yield f"data: {json.dumps({'event': 'token', 'token': f'Error during agent execution: {str(e)}'})}\n\n"
            yield f"data: {json.dumps({'event': 'final', 'text': f'Error: {str(e)}', 'tool_calls': [], 'pending_confirmation': None})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.post("/agent/confirm")
async def confirm_agent_action(
    payload: dict,
    db: AsyncSession = Depends(get_db_session),
    rep: CurrentRep = Depends(current_rep)
):
    session_id = payload.get("session_id", "demo-session")
    choice = payload.get("choice", "confirm")
    
    config = {
        "configurable": {
            "thread_id": session_id,
            "db": db
        }
    }
    
    state_info = await graph.aget_state(config)
    if not state_info or not state_info.values:
        return {"status": "error", "message": "No active agent session found"}
        
    pending_conf = state_info.values.get("pending_confirmation")
    if not pending_conf:
        return {"status": "error", "message": "No pending action to confirm"}

    raw_input = "yes" if choice == "confirm" else "no"
    
    initial_state = dict(state_info.values)
    initial_state["raw_input"] = raw_input
    
    final_state = await graph.ainvoke(initial_state, config)
    
    return {
        "status": "success",
        "final_response": final_state.get("final_response"),
        "tool_calls_made": final_state.get("tool_calls_made")
    }
