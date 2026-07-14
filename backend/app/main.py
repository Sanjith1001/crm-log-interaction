from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_agent, routes_auth, routes_hcp, routes_interactions


def create_app() -> FastAPI:
    app = FastAPI(title="CRM Log Interaction API")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(routes_auth.router, prefix="/api")
    app.include_router(routes_agent.router, prefix="/api")
    app.include_router(routes_interactions.router, prefix="/api")
    app.include_router(routes_hcp.router, prefix="/api")
    return app


app = create_app()

