from typing import Literal

from pydantic import BaseModel, Field


class AgentInvokeRequest(BaseModel):
    session_id: str = Field(default="demo-session")
    input_mode: Literal["form", "chat"]
    raw_input: str


class AgentInvokeResponse(BaseModel):
    session_id: str
    final_response: str
    tool_calls_made: list[dict]

