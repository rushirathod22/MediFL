"""
MediFL Main Application Server
Serves both REST APIs and the Web Dashboard UI on http://localhost:8000
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from src.server.core.config import settings
from src.server.api.routes import router as api_router
from src.server.services.fl_coordinator import get_coordinator

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise Medical Federated Learning Platform",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Router
app.include_router(api_router)

# Mount frontend directory for static assets if needed
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.on_event("startup")
async def startup_event():
    """Initialize coordinator and prepare hospital edge agents on server start."""
    coordinator = get_coordinator()
    print(f"[OK] MediFL Platform Initialized. Ready for Federated Rounds with {len(coordinator.hospital_agents)} hospital nodes.")


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve the MediFL Control Plane Web Dashboard."""
    frontend_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return HTMLResponse("<h2>MediFL Dashboard Loading...</h2>")


@app.get("/healthz")
async def health_check():
    """Liveness probe."""
    coordinator = get_coordinator()
    return {
        "status": "HEALTHY",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "round": coordinator.current_round,
        "strategy": coordinator.strategy_name,
        "nodes": len(coordinator.hospital_agents),
    }
