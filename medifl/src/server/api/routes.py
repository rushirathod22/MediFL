"""
MediFL REST API Routes
Exposes endpoints for federated round triggering, strategy switching,
status queries, node telemetry, model weight exports, and session resets.
"""
import os
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, FileResponse

from src.server.models.schemas import RoundTriggerRequest, StrategyChangeRequest
from src.server.services.fl_coordinator import get_coordinator

router = APIRouter(prefix="/api/v1", tags=["Federated Learning"])


@router.get("/status")
async def get_system_status() -> Dict[str, Any]:
    """Retrieve complete live state of the federated learning coordinator."""
    coordinator = get_coordinator()
    return coordinator.get_status()


@router.post("/trigger-round")
async def trigger_round(req: Optional[RoundTriggerRequest] = None) -> Dict[str, Any]:
    """
    Execute a real federated learning round across all connected hospital nodes.
    Performs local training on hospital edge nodes, applies DP-SGD noise,
    aggregates via FedAvg/FedProx, and updates global weights.
    """
    coordinator = get_coordinator()
    strategy = req.strategy if req else None
    epochs = req.epochs if req else 2
    lr = req.lr if req else 0.008
    mu = req.mu if req else 0.01

    try:
        result = coordinator.trigger_round(
            strategy=strategy,
            epochs=epochs,
            lr=lr,
            mu=mu,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Federated round execution failed: {str(e)}")


@router.post("/reset")
async def reset_session() -> Dict[str, Any]:
    """Reset the federated training session back to round 0."""
    coordinator = get_coordinator()
    coordinator.reset_session()
    return {"status": "SUCCESS", "message": "Federated training session reset to Round 0"}


@router.post("/strategy")
async def switch_strategy(req: StrategyChangeRequest) -> Dict[str, Any]:
    """Switch aggregation strategy (FedAvg vs FedProx)."""
    coordinator = get_coordinator()
    coordinator.set_strategy(req.strategy, mu=req.mu or 0.01)
    return {
        "status": "SUCCESS",
        "strategy": coordinator.strategy_name,
        "mu": coordinator.fedprox_mu if coordinator.strategy_name == "FedProx" else None,
    }


@router.get("/history")
async def get_training_history():
    """Retrieve full history of all federated rounds."""
    coordinator = get_coordinator()
    return {"history": coordinator.history}


@router.get("/nodes")
async def get_hospital_nodes():
    """List all participating hospital edge nodes and telemetry."""
    coordinator = get_coordinator()
    return {"nodes": [
        {
            "node_id": a.node_id,
            "hospital_name": a.hospital_name,
            "num_samples": a.num_samples,
            "status": "ONLINE",
            "dp_enabled": a.dp_enabled,
        }
        for a in coordinator.hospital_agents
    ]}


@router.get("/logs")
async def get_audit_logs():
    """Retrieve recent cryptographic audit log entries."""
    coordinator = get_coordinator()
    return {"logs": coordinator.audit_logs}


@router.get("/export-model")
async def export_model_checkpoint():
    """Download the latest global model PyTorch checkpoint."""
    coordinator = get_coordinator()
    checkpoint_path = os.path.join(
        coordinator.checkpoint_dir, f"medifl_model_round_{coordinator.current_round}.pth"
    )
    if os.path.exists(checkpoint_path):
        return FileResponse(
            checkpoint_path,
            filename=f"medifl_global_model_round_{coordinator.current_round}.pth",
            media_type="application/octet-stream",
        )
    return JSONResponse(
        content={
            "round": coordinator.current_round,
            "strategy": coordinator.strategy_name,
            "accuracy": coordinator.latest_accuracy,
            "loss": coordinator.latest_loss,
            "hash": coordinator.latest_hash,
            "weights_sample": {
                k: v[:5] for k, v in coordinator.global_weights.items()
            },
        }
    )
