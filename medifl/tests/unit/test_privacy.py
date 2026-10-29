"""
Unit Tests for Differential Privacy Engine and Privacy Accountant
"""
import pytest
import torch
from src.common.privacy import DifferentialPrivacyEngine, PrivacyAccountant


def test_dp_engine_noise_injection():
    engine = DifferentialPrivacyEngine(target_epsilon=5.0, target_delta=1e-5, max_grad_norm=1.0)
    tensor = torch.zeros(10, 10)
    noised = engine.add_noise(tensor, noise_multiplier=0.1)
    
    assert noised.shape == tensor.shape
    # Ensure noise was indeed added (not identical to all zeros)
    assert not torch.allclose(tensor, noised)


def test_privacy_accountant_logging():
    accountant = PrivacyAccountant(epsilon_limit=8.0, delta_limit=1e-5)
    assert not accountant.is_budget_exhausted()
    assert accountant.current_epsilon == 0.0
    
    accountant.log_round(1, eps_used=2.0, delta_used=1e-5)
    assert accountant.current_epsilon == 2.0
    assert not accountant.is_budget_exhausted()
    
    accountant.log_round(2, eps_used=4.0, delta_used=1e-5)
    assert accountant.current_epsilon == 6.0
    assert not accountant.is_budget_exhausted()
    
    accountant.log_round(3, eps_used=3.0, delta_used=1e-5)
    assert accountant.current_epsilon == 9.0
    assert accountant.is_budget_exhausted()
