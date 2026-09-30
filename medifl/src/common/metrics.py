"""
MediFL Round Metrics & Store Module
"""
from dataclasses import dataclass, asdict
from typing import Dict, List, Any

@dataclass
class RoundMetrics:
    round_id: int
    loss: float
    accuracy: float
    epsilon_spent: float
    num_clients: int
    audit_hash: str

class MetricsStore:
    """
    In-memory and file-persistent storage for FL execution round metrics.
    """
    def __init__(self):
        self.history: List[RoundMetrics] = []

    def record(self, metrics: RoundMetrics):
        self.history.append(metrics)

    def get_latest(self) -> Dict[str, Any]:
        if not self.history:
            return {}
        return asdict(self.history[-1])

    def get_all(self) -> List[Dict[str, Any]]:
        return [asdict(m) for m in self.history]
