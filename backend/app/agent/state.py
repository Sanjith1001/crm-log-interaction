from typing import Literal, Optional, TypedDict, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict, total=False):
    messages: Annotated[list, add_messages]     # full chat/turn history
    input_mode: Literal["form", "chat"]
    representative_id: str
    raw_input: str                              # normalized user text
    selected_tool: Optional[str]                # set by router node
    tool_args: Optional[dict]                   # structured args extracted for the tool
    tool_result: Optional[dict]                 # raw result returned by tool execution
    pending_confirmation: Optional[dict]         # non-null => graph paused awaiting user confirm
    tool_calls_made: list[dict]                  # audit trail for this turn, shown in UI
    final_response: Optional[str]
