"""
Base Aggregator — Abstract class that all FL strategies inherit from.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import hashlib
import json
import logging

logger = logging.getLogger("medifl.aggregator")


class ModelUpdate:
    """Represents one hospital node's local training result for a round."""

    def __init__(self, node_id: str, weights: Dict[str, list], num_samples: int, metrics: dict):
        self.node_id = node_id
        self.weights = weights        # {"layer_name": [weight_flat_values]}
        self.num_samples = num_samples  # Number of samples trained locally
        self.metrics = metrics          # {"loss": 0.5, "accuracy": 0.85}


class BaseAggregator(ABC):
    """
    Abstract base class for all FL aggregation strategies.
    Enforces validation, logging, and weight hashing for immutable audit trails.
    """

    def __init__(self, project_id: str, hyperparams: dict = None):
        self.project_id = project_id
        self.current_round = 0
        self.hyperparams = hyperparams or {}
        self.logger = logging.getLogger(f"medifl.aggregator.{project_id}")

    @abstractmethod
    def aggregate(self, updates: List[ModelUpdate]) -> Dict[str, list]:
        """
        Combine model updates from all hospitals into one global model.
        Implemented by specific strategies (FedAvg, FedProx, etc.).
        """
        pass

    def validate_weights(self, weights: Dict[str, list]) -> bool:
        """Check that weight shapes and types are valid."""
        for layer_name, values in weights.items():
            if not isinstance(values, list) or len(values) == 0:
                self.logger.error(f"Invalid weights for layer: {layer_name}")
                return False
        return True

    def compute_weights_hash(self, weights: Dict[str, list]) -> str:
        """Create a SHA-256 hash of model weights for cryptographic audit log."""
        weights_str = json.dumps(weights, sort_keys=True, default=str)
        return hashlib.sha256(weights_str.encode()).hexdigest()
