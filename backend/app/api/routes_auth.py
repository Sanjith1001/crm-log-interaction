from fastapi import APIRouter

router = APIRouter(tags=["auth"])


@router.post("/auth/login")
async def login() -> dict[str, str]:
    return {"access_token": "demo-token", "token_type": "bearer"}

