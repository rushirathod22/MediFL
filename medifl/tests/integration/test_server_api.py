"""
Integration Tests for MediFL FastAPI Endpoints
"""
import pytest
from fastapi.testclient import TestClient
from src.server.main import app

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "round" in data
    assert "nodes" in data


def test_status_endpoint():
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "READY"
    assert "round" in data
    assert "strategy" in data
    assert len(data["nodes"]) == 3


def test_strategy_switch_endpoint():
    # Switch to FedProx
    response = client.post("/api/v1/strategy", json={"strategy": "fedprox", "mu": 0.02})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["strategy"] == "FedProx"
    
    # Switch back to FedAvg
    response = client.post("/api/v1/strategy", json={"strategy": "fedavg"})
    assert response.status_code == 200
    assert response.json()["strategy"] == "FedAvg"


def test_trigger_round_endpoint():
    response = client.post("/api/v1/trigger-round", json={"strategy": "fedavg", "epochs": 1, "lr": 0.01})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["round"] >= 1
    assert "loss" in data
    assert "accuracy" in data
    assert "hash" in data
    assert data["num_nodes"] == 3


def test_history_and_reset_endpoints():
    # Check history contains rounds
    hist_resp = client.get("/api/v1/history")
    assert hist_resp.status_code == 200
    assert len(hist_resp.json()["history"]) >= 1
    
    # Reset session
    reset_resp = client.post("/api/v1/reset")
    assert reset_resp.status_code == 200
    assert reset_resp.json()["status"] == "SUCCESS"
    
    # Status after reset
    status_resp = client.get("/api/v1/status")
    assert status_resp.json()["round"] == 0
