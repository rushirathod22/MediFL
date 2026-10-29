"""
Unit Tests for FedAvg Aggregation Strategy
"""
import pytest
from src.aggregator.base import ModelUpdate
from src.aggregator.fedavg import FedAvgAggregator


def test_fedavg_aggregation_math():
    aggregator = FedAvgAggregator(project_id="test-fedavg")
    
    # 2 hospital nodes: Node A has 300 samples, Node B has 100 samples (3:1 ratio)
    weights_a = {"layer1": [1.0, 2.0, 3.0]}
    weights_b = {"layer1": [5.0, 6.0, 7.0]}
    
    update_a = ModelUpdate("node-a", weights_a, num_samples=300, metrics={})
    update_b = ModelUpdate("node-b", weights_b, num_samples=100, metrics={})
    
    # Expected weighted average:
    # 0.75 * [1.0, 2.0, 3.0] + 0.25 * [5.0, 6.0, 7.0]
    # layer1[0] = 0.75*1 + 0.25*5 = 0.75 + 1.25 = 2.0
    # layer1[1] = 0.75*2 + 0.25*6 = 1.50 + 1.50 = 3.0
    # layer1[2] = 0.75*3 + 0.25*7 = 2.25 + 1.75 = 4.0
    
    aggregated = aggregator.aggregate([update_a, update_b])
    
    assert "layer1" in aggregated
    assert pytest.approx(aggregated["layer1"][0], 0.001) == 2.0
    assert pytest.approx(aggregated["layer1"][1], 0.001) == 3.0
    assert pytest.approx(aggregated["layer1"][2], 0.001) == 4.0


def test_fedavg_empty_updates_raises_error():
    aggregator = FedAvgAggregator(project_id="test-empty")
    with pytest.raises(ValueError):
        aggregator.aggregate([])


def test_fedavg_hash_generation():
    aggregator = FedAvgAggregator(project_id="test-hash")
    weights = {"layer1": [0.1, 0.2, 0.3], "layer2": [1.0, 2.0]}
    h1 = aggregator.compute_weights_hash(weights)
    h2 = aggregator.compute_weights_hash(weights)
    assert isinstance(h1, str)
    assert len(h1) == 64  # SHA-256 length
    assert h1 == h2
