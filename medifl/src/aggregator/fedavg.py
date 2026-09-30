"""
Federated Averaging (FedAvg) — McMahan et al., 2017
https://arxiv.org/abs/1602.05629

Computes sample-weighted average of model parameters from participating hospital edge nodes.
"""
from typing import List, Dict
from src.aggregator.base import BaseAggregator, ModelUpdate


class FedAvgAggregator(BaseAggregator):
    """
    Federated Averaging aggregation strategy.
    
    Formula:
    W_global = Σ ( (n_k / N_total) * W_k )
    where n_k is the number of local training samples at hospital k,
    N_total is the sum of samples across all participating hospitals,
    and W_k are the trained parameters from hospital k.
    """

    def aggregate(self, updates: List[ModelUpdate]) -> Dict[str, list]:
        """
        Perform weighted average of all hospital model updates.

        Args:
            updates: List of ModelUpdate objects from hospital nodes

        Returns:
            Aggregated global model weights dictionary
        """
        if not updates:
            raise ValueError("No updates received to aggregate!")

        self.logger.info(
            f"[FedAvg] Aggregating {len(updates)} node updates for round {self.current_round}"
        )

        # 1. Total samples across all hospitals
        total_samples = sum(u.num_samples for u in updates)
        if total_samples <= 0:
            raise ValueError("Total sample count across participating nodes must be > 0")

        # 2. Node weight proportions: w_k = n_k / total_samples
        node_weights = [u.num_samples / total_samples for u in updates]
        node_weight_map = {u.node_id: round(w, 4) for u, w in zip(updates, node_weights)}
        self.logger.info(f"[FedAvg] Calculated Node Weight Distribution: {node_weight_map}")

        # 3. Perform weighted averaging per layer
        aggregated = self._weighted_average(updates, node_weights)

        # 4. Hash verification & audit logging
        if self.validate_weights(aggregated):
            w_hash = self.compute_weights_hash(aggregated)
            self.logger.info(
                f"[SUCCESS] [FedAvg] Round {self.current_round} completed successfully. "
                f"Global Weight Hash: {w_hash[:16]}..."
            )

        self.current_round += 1
        return aggregated

    def _weighted_average(
        self, updates: List[ModelUpdate], node_weights: List[float]
    ) -> Dict[str, list]:
        """Weighted element-wise sum of weights across all layers."""
        layer_names = updates[0].weights.keys()
        result = {}

        for layer in layer_names:
            layer_values = []
            for i, update in enumerate(updates):
                node_layer = update.weights[layer]
                # Multiply parameter array by hospital weight proportion
                weighted = [v * node_weights[i] for v in node_layer]
                layer_values.append(weighted)

            # Sum across all hospital nodes for this layer
            aggregated_layer = [sum(values) for values in zip(*layer_values)]
            result[layer] = aggregated_layer

        return result
