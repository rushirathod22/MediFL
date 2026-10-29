"""
Unit Tests for FedProx Aggregation Strategy
"""
import pytest
from src.aggregator.base import ModelUpdate
from src.aggregator.fedprox import FedProxAggregator


def test_fedprox_proximal_penalty():
    aggregator = FedProxAggregator(project_id="test-fedprox", mu=0.1)
    
    # Set initial global reference weights
    aggregator.global_reference_weights = {"w": [10.0, 20.0]}
    
    # Hospital update with local drift
    local_weights = {"w": [12.0, 25.0]}
    penalized = aggregator._apply_proximal_penalty(local_weights, aggregator.global_reference_weights)
    
    # w_penalized = w_local - mu * (w_local - w_global)
    # 12.0 - 0.1 * (12.0 - 10.0) = 12.0 - 0.2 = 11.8
    # 25.0 - 0.1 * (25.0 - 20.0) = 25.0 - 0.5 = 24.5
    assert pytest.approx(penalized["w"][0], 0.001) == 11.8
    assert pytest.approx(penalized["w"][1], 0.001) == 24.5


def test_fedprox_aggregation_flow():
    aggregator = FedProxAggregator(project_id="test-fedprox-flow", mu=0.05)
    
    update1 = ModelUpdate("node-1", {"layer": [1.0, 2.0]}, num_samples=100, metrics={})
    update2 = ModelUpdate("node-2", {"layer": [3.0, 4.0]}, num_samples=100, metrics={})
    
    # First round: no previous reference, computes standard weighted average
    res1 = aggregator.aggregate([update1, update2])
    assert pytest.approx(res1["layer"][0], 0.001) == 2.0
    assert pytest.approx(res1["layer"][1], 0.001) == 3.0
    
    # Second round: applies proximal regularizer towards round 1 weights
    update3 = ModelUpdate("node-1", {"layer": [2.5, 3.5]}, num_samples=100, metrics={})
    res2 = aggregator.aggregate([update3])
    assert "layer" in res2
