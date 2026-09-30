"""
MediFL Differential Privacy Engine & Accountant Module
"""
import math
from typing import Tuple, Dict, Any

class DifferentialPrivacyEngine:
    """
    Differential Privacy wrapper for model training and update sanitization.
    """
    def __init__(self, target_epsilon: float = 3.0, target_delta: float = 1e-5, max_grad_norm: float = 1.0):
        self.target_epsilon = target_epsilon
        self.target_delta = target_delta
        self.max_grad_norm = max_grad_norm

    def add_noise(self, param_tensor: Any, noise_multiplier: float = 1.0) -> Any:
        """Applies Gaussian noise to parameter weights for DP guarantees."""
        import torch
        noise = torch.randn_like(param_tensor) * (noise_multiplier * self.max_grad_norm)
        return param_tensor + noise

    def get_privacy_budget_consumed(self, current_round: int, total_rounds: int) -> Tuple[float, float]:
        """Calculates consumed (epsilon, delta) budget based on FL rounds."""
        consumed_eps = (current_round / max(total_rounds, 1)) * self.target_epsilon
        return round(consumed_eps, 4), self.target_delta


class PrivacyAccountant:
    """
    Tracks overall privacy budget expenditure across federated learning rounds.
    """
    def __init__(self, epsilon_limit: float = 10.0, delta_limit: float = 1e-5):
        self.epsilon_limit = epsilon_limit
        self.delta_limit = delta_limit
        self.current_epsilon = 0.0
        self.current_delta = 0.0
        self.history = []

    def log_round(self, round_num: int, eps_used: float, delta_used: float):
        self.current_epsilon += eps_used
        self.current_delta = max(self.current_delta, delta_used)
        self.history.append({
            "round": round_num,
            "epsilon": round(self.current_epsilon, 4),
            "delta": self.current_delta,
            "within_budget": self.current_epsilon <= self.epsilon_limit
        })

    def is_budget_exhausted(self) -> bool:
        return self.current_epsilon >= self.epsilon_limit
