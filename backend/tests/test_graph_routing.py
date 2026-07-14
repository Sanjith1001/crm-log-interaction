import pytest
from app.agent.graph import run_agent
from app.agent.state import AgentState
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings

@pytest.mark.asyncio
async def test_agent_log_interaction_routing():
    state = {
        "raw_input": "I met Dr. Rao today to discuss Ozempic, gave 5 samples.",
        "input_mode": "chat",
        "representative_id": "e0a6d45e-4c07-4228-b9a5-1ffef76e330e",
        "tool_calls_made": []
    }
    
    engine = create_async_engine(settings.database_url, future=True)
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    async with async_session_maker() as db:
        config = {
            "configurable": {
                "thread_id": "test-session-routing",
                "db": db
            }
        }
        final_state = await run_agent(state, config)
        
        assert final_state["selected_tool"] == "log_interaction"
        assert "tool_result" in final_state
        assert "final_response" in final_state
        print("Test passed! Selected tool:", final_state["selected_tool"])
