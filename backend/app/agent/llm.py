from groq import AsyncGroq
from app.config import settings

# Initialize Groq async client
client = AsyncGroq(api_key=settings.groq_api_key)

def router_model_name() -> str:
    return settings.groq_model_router

def responder_model_name() -> str:
    return settings.groq_model_responder

async def call_llm(system_prompt: str, user_prompt: str, model: str, response_format: dict | None = None) -> str:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    kwargs = {}
    if response_format:
        kwargs["response_format"] = response_format
        
    completion = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.1,
        **kwargs
    )
    return completion.choices[0].message.content or ""

async def call_llm_messages(messages: list[dict], model: str, response_format: dict | None = None) -> str:
    kwargs = {}
    if response_format:
        kwargs["response_format"] = response_format
        
    completion = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.1,
        **kwargs
    )
    return completion.choices[0].message.content or ""
