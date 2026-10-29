"""
Pydantic Schemas for MediFL REST API
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class HospitalNodeInfo(BaseModel):
    node_id: str
    hospital_name: str
    num_samples: int
    status: str = "ONLINE"
    last_accuracy: Optional[float] = None
    last_loss: Optional[float] = None


class RoundTriggerRequest(BaseModel):
    strategy: Optional[str] = Field("fedavg", description="'fedavg' or 'fedprox'")
    epochs: Optional[int] = Field(2, ge=1, le=10, description="Local training epochs per node")
    lr: Optional[float] = Field(0.008, gt=0.0, le=0.1, description="Learning rate")
    mu: Optional[float] = Field(0.01, ge=0.0, le=1.0, description="Proximal term for FedProx")


class StrategyChangeRequest(BaseModel):
    strategy: str = Field(..., description="'fedavg' or 'fedprox'")
    mu: Optional[float] = Field(0.01, ge=0.0, le=1.0)


class AuditLogEntry(BaseModel):
    timestamp: str
    tag: str  # 'info', 'success', 'dp', 'hash', 'warning'
    message: str


class RoundStatusResponse(BaseModel):
    status: str
    round: int
    max_rounds: int = 10
    strategy: str
    loss: float
    accuracy: float
    epsilon: float
    target_epsilon: float
    delta: float
    hash: str
    num_nodes: int
    nodes: List[HospitalNodeInfo]
    history: List[Dict[str, Any]]
