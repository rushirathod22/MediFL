"""
Unit Tests for Hospital Edge Agent Client
"""
import pytest
from src.edge_agent.client import HospitalEdgeAgent


def test_edge_agent_initialization():
    agent = HospitalEdgeAgent("node-test", "Test Memorial Hospital", num_samples=150)
    assert agent.node_id == "node-test"
    assert agent.num_samples == 150
    assert len(agent.dataset) == 150


def test_edge_agent_local_training():
    agent = HospitalEdgeAgent("node-test-train", "City Clinic", num_samples=64, dp_enabled=True)
    update = agent.train_round(global_weights=None, epochs=1, lr=0.01)
    
    assert update.node_id == "node-test-train"
    assert update.num_samples == 64
    assert "loss" in update.metrics
    assert "accuracy" in update.metrics
    assert isinstance(update.weights, dict)
    assert len(update.weights) > 0


def test_edge_agent_evaluate():
    agent = HospitalEdgeAgent("node-test-eval", "Apex Health", num_samples=50)
    ref_weights = agent.get_reference_weights()
    loss, acc = agent.evaluate(ref_weights)
    assert isinstance(loss, float)
    assert isinstance(acc, float)
    assert 0.0 <= acc <= 100.0
