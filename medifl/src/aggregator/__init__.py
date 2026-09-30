"""
MediFL Aggregator Package — Core Federated Learning Engine
"""
from src.aggregator.base import BaseAggregator, ModelUpdate
from src.aggregator.fedavg import FedAvgAggregator
from src.aggregator.fedprox import FedProxAggregator

__all__ = ["BaseAggregator", "ModelUpdate", "FedAvgAggregator", "FedProxAggregator"]
