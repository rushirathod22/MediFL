"""
MediFL Main Application Server
Serves both REST APIs and the Web Dashboard UI on http://localhost:8000
"""
import os
import random
import hashlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from src.server.core.config import settings

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

# Global in-memory state for live UI demonstration
server_state = {
    "round": 5,
    "accuracy": 89.4,
    "loss": 0.24,
    "epsilon": 2.4,
}


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve the MediFL Control Plane Web Dashboard."""
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return HTMLResponse("<h2>MediFL Dashboard Loading...</h2>")


@app.get("/healthz")
async def health_check():
    return {"status": "HEALTHY", "app": settings.APP_NAME, "version": settings.APP_VERSION}


@app.post("/api/v1/trigger-round")
async def trigger_round():
    """Simulate a real-time FL round trigger from the Web UI."""
    server_state["round"] += 1
    server_state["loss"] = max(0.10, round(server_state["loss"] - 0.022, 4))
    server_state["accuracy"] = min(97.5, round(server_state["accuracy"] + 1.6, 2))
    server_state["epsilon"] = min(8.0, round(server_state["epsilon"] + 0.4, 2))

    w_hash = hashlib.sha256(f"round-{server_state['round']}-{random.random()}".encode()).hexdigest()

    return {
        "status": "SUCCESS",
        "round": server_state["round"],
        "loss": server_state["loss"],
        "accuracy": server_state["accuracy"],
        "epsilon": server_state["epsilon"],
        "hash": w_hash[:24] + "...",
    }
