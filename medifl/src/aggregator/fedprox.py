"""
FedProx — Li et al., 2020
https://arxiv.org/abs/1812.06127

Federated Proximal aggregation for handling heterogeneous non-IID data distributions.
"""
from typing import List, Dict
from src.aggregator.base import BaseAggregator, ModelUpdate


class FedProxAggregator(BaseAggregator):
    """
    FedProx Strategy — adds proximal regularizer penalty term μ
    to prevent local models from drifting too far from global weights.
    """

    def __init__(self, project_id: str, hyperparams: dict = None, mu: float = 0.01):
        super().__init__(project_id, hyperparams)
        self.mu = mu
        self.global_reference_weights = None

    def aggregate(self, updates: List[ModelUpdate]) -> Dict[str, list]:
        if not updates:
            raise ValueError("No updates received to aggregate!")

        self.logger.info(f"[FedProx] Aggregating {len(updates)} updates with proximal term mu={self.mu}")

        # Apply proximal penalty to updates if previous global weights exist
        if self.global_reference_weights is not None:
            updates = [
                ModelUpdate(
                    node_id=u.node_id,
                    weights=self._apply_proximal_penalty(u.weights, self.global_reference_weights),
                    num_samples=u.num_samples,
                    metrics=u.metrics,
                )
                for u in updates
            ]

        total_samples = sum(u.num_samples for u in updates)
        node_weights = [u.num_samples / total_samples for u in updates]

        layer_names = updates[0].weights.keys()
        aggregated = {}
        for layer in layer_names:
            layer_values = []
            for i, update in enumerate(updates):
                weighted = [v * node_weights[i] for v in update.weights[layer]]
                layer_values.append(weighted)
            aggregated[layer] = [sum(vals) for vals in zip(*layer_values)]

        self.global_reference_weights = aggregated
        self.current_round += 1
        return aggregated

    def _apply_proximal_penalty(
        self, local_weights: Dict[str, list], global_weights: Dict[str, list]
    ) -> Dict[str, list]:
        """w_penalized = w_local - mu * (w_local - w_global)"""
        penalized = {}
        for layer in local_weights:
            penalized[layer] = [
                loc - self.mu * (loc - glob)
                for loc, glob in zip(local_weights[layer], global_weights[layer])
            ]
        return penalized
