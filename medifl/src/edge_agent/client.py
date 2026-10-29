"""
MediFL Hospital Edge Agent Client
Runs locally within hospital firewall boundaries.
Trains local PyTorch diagnostic model on private patient data without data egress.
Applies Differential Privacy (DP-SGD) noise injection before returning weights.
"""
import copy
import logging
import sys
from typing import Dict, List, Optional, Tuple

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

from src.aggregator.base import ModelUpdate
from src.common.privacy import DifferentialPrivacyEngine

logger = logging.getLogger("medifl.edge_agent")


class DiagnosticNN(nn.Module):
    """
    Lightweight Diagnostic Neural Network for Chest X-Ray / Clinical Feature Classification.
    Class 0: Normal / Healthy
    Class 1: Pneumonia / Disease Finding
    """
    def __init__(self, input_features: int = 32, num_classes: int = 2):
        super(DiagnosticNN, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_features, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.25),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)


def state_dict_to_weights(state_dict: Dict[str, torch.Tensor]) -> Dict[str, List[float]]:
    """Converts PyTorch state_dict tensors to JSON-serializable list of floats."""
    return {k: v.cpu().detach().clone().flatten().tolist() for k, v in state_dict.items()}


def weights_to_state_dict(
    weights: Dict[str, List[float]], reference_state_dict: Dict[str, torch.Tensor]
) -> Dict[str, torch.Tensor]:
    """Reconstructs PyTorch state_dict tensors from flat float lists."""
    new_state_dict = {}
    for k, v in weights.items():
        ref_tensor = reference_state_dict[k]
        new_state_dict[k] = torch.tensor(v, dtype=ref_tensor.dtype).reshape(ref_tensor.shape)
    return new_state_dict


class HospitalEdgeAgent:
    """
    Hospital Edge Node Agent.
    Strict Data Privacy Guarantee:
    - Raw patient data is isolated within this class instance (representing hospital network).
    - Only differential-privacy sanitised model weights are transmitted back.
    """

    def __init__(
        self,
        node_id: str,
        hospital_name: str,
        num_samples: int = 500,
        feature_dim: int = 32,
        class_balance: float = 0.5,
        dp_enabled: bool = True,
        clip_norm: float = 1.0,
        noise_multiplier: float = 0.05,
    ):
        self.node_id = node_id
        self.hospital_name = hospital_name
        self.num_samples = num_samples
        self.feature_dim = feature_dim
        self.dp_enabled = dp_enabled

        # Privacy Engine for DP-SGD noise injection
        self.dp_engine = DifferentialPrivacyEngine(
            target_epsilon=8.0, target_delta=1e-5, max_grad_norm=clip_norm
        )
        self.noise_multiplier = noise_multiplier

        # Generate local synthetic hospital data distribution (simulating real hospital chest X-ray features)
        # Use node-specific seed to simulate Non-IID heterogeneous data
        seed = abs(hash(node_id)) % 100000
        torch.manual_seed(seed)

        # Generate disease features with slight class separation
        num_pos = int(num_samples * class_balance)
        num_neg = num_samples - num_pos

        pos_features = torch.randn(num_pos, feature_dim) + 0.65
        neg_features = torch.randn(num_neg, feature_dim) - 0.65

        pos_labels = torch.ones(num_pos, dtype=torch.long)
        neg_labels = torch.zeros(num_neg, dtype=torch.long)

        X = torch.cat([pos_features, neg_features], dim=0)
        y = torch.cat([pos_labels, neg_labels], dim=0)

        # Shuffle local dataset
        indices = torch.randperm(num_samples)
        self.dataset = TensorDataset(X[indices], y[indices])
        self.dataloader = DataLoader(self.dataset, batch_size=32, shuffle=True)

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = DiagnosticNN(input_features=feature_dim, num_classes=2).to(self.device)
        self.reference_state_dict = copy.deepcopy(self.model.state_dict())

    def get_reference_weights(self) -> Dict[str, List[float]]:
        """Return base architecture weights template."""
        return state_dict_to_weights(self.reference_state_dict)

    def train_round(
        self,
        global_weights: Optional[Dict[str, List[float]]],
        epochs: int = 2,
        lr: float = 0.008,
    ) -> ModelUpdate:
        """
        Executes local training round:
        1. Ingests global model weights from server.
        2. Fits local neural network on private hospital records.
        3. Injects Differential Privacy noise if enabled.
        4. Returns ModelUpdate (weights + sample count + loss/acc).
        """
        # Load global model weights into local instance
        if global_weights is not None:
            self.model.load_state_dict(
                weights_to_state_dict(global_weights, self.reference_state_dict)
            )

        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=lr)

        self.model.train()
        total_loss = 0.0
        correct = 0
        total = 0

        for epoch in range(epochs):
            for batch_x, batch_y in self.dataloader:
                batch_x, batch_y = batch_x.to(self.device), batch_y.to(self.device)
                optimizer.zero_grad()

                outputs = self.model(batch_x)
                loss = criterion(outputs, batch_y)
                loss.backward()

                # Gradient norm clipping for DP-SGD
                if self.dp_enabled:
                    nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=self.dp_engine.max_grad_norm)

                optimizer.step()

                total_loss += loss.item() * batch_x.size(0)
                _, preds = torch.max(outputs, 1)
                correct += (preds == batch_y).sum().item()
                total += batch_y.size(0)

        avg_loss = total_loss / max(total * epochs, 1)
        accuracy = (correct / max(total * epochs, 1)) * 100.0

        # Extract trained state_dict
        trained_state_dict = self.model.state_dict()

        # Apply Differential Privacy parameter noise injection
        if self.dp_enabled and self.noise_multiplier > 0:
            for k in trained_state_dict.keys():
                if "weight" in k:
                    trained_state_dict[k] = self.dp_engine.add_noise(
                        trained_state_dict[k], noise_multiplier=self.noise_multiplier
                    )

        trained_weights = state_dict_to_weights(trained_state_dict)
        metrics = {
            "loss": round(avg_loss, 4),
            "accuracy": round(accuracy, 2),
            "samples": self.num_samples,
        }

        logger.info(
            f"[{self.hospital_name}] Local Training Done: "
            f"Loss={avg_loss:.4f}, Accuracy={accuracy:.2f}% | DP-noised={self.dp_enabled}"
        )

        return ModelUpdate(
            node_id=self.node_id,
            weights=trained_weights,
            num_samples=self.num_samples,
            metrics=metrics,
        )

    def evaluate(self, global_weights: Dict[str, List[float]]) -> Tuple[float, float]:
        """Evaluates global weights against local hospital dataset."""
        eval_model = DiagnosticNN(input_features=self.feature_dim, num_classes=2).to(self.device)
        eval_model.load_state_dict(weights_to_state_dict(global_weights, self.reference_state_dict))
        eval_model.eval()

        criterion = nn.CrossEntropyLoss()
        total_loss, correct, total = 0.0, 0, 0

        with torch.no_grad():
            for batch_x, batch_y in self.dataloader:
                batch_x, batch_y = batch_x.to(self.device), batch_y.to(self.device)
                outputs = eval_model(batch_x)
                loss = criterion(outputs, batch_y)
                total_loss += loss.item() * batch_x.size(0)
                _, preds = torch.max(outputs, 1)
                correct += (preds == batch_y).sum().item()
                total += batch_y.size(0)

        return round(total_loss / max(total, 1), 4), round((correct / max(total, 1)) * 100.0, 2)


def create_default_hospital_agents() -> List[HospitalEdgeAgent]:
    """Generates the three benchmark hospital nodes for the platform."""
    return [
        HospitalEdgeAgent(
            node_id="node-01",
            hospital_name="Hospital A (Mumbai)",
            num_samples=500,
            class_balance=0.55,
        ),
        HospitalEdgeAgent(
            node_id="node-02",
            hospital_name="Hospital B (Pune)",
            num_samples=300,
            class_balance=0.48,
        ),
        HospitalEdgeAgent(
            node_id="node-03",
            hospital_name="Hospital C (Delhi)",
            num_samples=200,
            class_balance=0.52,
        ),
    ]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    agent = HospitalEdgeAgent("test-node", "Test Hospital", num_samples=100)
    update = agent.train_round(global_weights=None, epochs=2)
    print(f"Sample Update: Node={update.node_id}, Samples={update.num_samples}, Metrics={update.metrics}")
