"""
KGDRL Core v2 - Knowledge-Guided Deep Reinforcement Learning
for Pharmaceutical Smart Wave Allocation

Upgrades from vanilla PPO:
1. Graph Attention Network (GAT) encoder replaces MLP state encoding
2. Knowledge Graph captures order-zone-temp relationships
3. KL divergence constraint aligns policy with TZU heuristic expertise
4. TZU pre-training for faster convergence

Author: AI-assisted implementation
Date: 2026/06/05 (Day 2 of Commercialization Plan)
"""

import numpy as np
import random
import math
import json
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass, field
import matplotlib.pyplot as plt
from tqdm import tqdm
import warnings

# PyTorch imports
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    warnings.warn("PyTorch not available. KGDRL requires PyTorch.")

# Import base components from pharma_wave_allocation.py
from pharma_wave_allocation import (
    SKU, Order, DataGenerator, PharmaWaveEnv,
    run_heuristic, compare_heuristics, plot_training_results,
    evaluate_agent as evaluate_ppo_agent
)

# =============================================================================
# 1. KNOWLEDGE GRAPH CONSTRUCTION
# =============================================================================

class KnowledgeGraph:
    """
    Heterogeneous knowledge graph for pharmaceutical wave allocation.

    Node types:
        - order (o): candidate orders in the pool
        - zone (z): warehouse zones (0-7)
        - temp (t): temperature categories (0-3)
        - wave (w): current active wave

    Edge types:
        - order-zone: order requires picking from zone
        - order-temp: order's dominant temperature
        - zone-zone: spatial proximity (adjacent in 2x4 grid)
        - temp-temp: compatibility (same or compatible temps)
        - wave-order: order currently in wave
        - wave-zone: zone covered by current wave
        - wave-temp: temperature covered by current wave
    """

    TEMP_COMPATIBILITY = {
        0: [0, 1],      # ambient compatible with ambient, cool
        1: [0, 1],      # cool compatible with ambient, cool
        2: [2],         # cold only with cold
        3: [3],         # frozen only with frozen
    }

    def __init__(self, n_zones=8, n_temps=4, k_candidates=10):
        self.n_zones = n_zones
        self.n_temps = n_temps
        self.k_candidates = k_candidates

        # Node counts
        self.n_order_nodes = k_candidates
        self.n_zone_nodes = n_zones
        self.n_temp_nodes = n_temps
        self.n_wave_nodes = 1
        self.n_nodes = self.n_order_nodes + self.n_zone_nodes + self.n_temp_nodes + self.n_wave_nodes

        # Node type offsets
        self.order_offset = 0
        self.zone_offset = self.n_order_nodes
        self.temp_offset = self.n_order_nodes + self.n_zone_nodes
        self.wave_offset = self.n_order_nodes + self.n_zone_nodes + self.n_temp_nodes

        # Pre-compute zone adjacency (2x4 grid)
        self._build_zone_adjacency()

    def _build_zone_adjacency(self):
        """Build spatial adjacency for 2x4 grid zones"""
        self.zone_adj = {}
        for z in range(self.n_zones):
            row, col = z // 4, z % 4
            neighbors = []
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = row + dr, col + dc
                if 0 <= nr < 2 and 0 <= nc < 4:
                    neighbors.append(nr * 4 + nc)
            self.zone_adj[z] = neighbors

    def build_graph(self, env: PharmaWaveEnv, state_dict: Dict) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Build graph representation from environment state.

        Returns:
            node_features: (N, d_node) node feature matrix
            edge_index: (2, E) edge list [source, target]
            edge_type: (E,) edge type labels
        """
        candidates = env._get_candidates()
        d_node = 16  # feature dimension per node

        node_features = np.zeros((self.n_nodes, d_node), dtype=np.float32)
        edges_src = []
        edges_dst = []
        edge_types = []

        # ---- ORDER nodes ----
        for i in range(self.k_candidates):
            node_idx = self.order_offset + i
            if i < len(candidates):
                o = candidates[i]
                remaining = ((o.arrival_time + o.deadline * 60) - env.current_time) / 60
                cx, cy = o.zone_centroid
                feat = [
                    o.n_items / 5.0,
                    remaining / 24.0,
                    o.dominant_temp / 3.0,
                    cx / 3.0,
                    cy / 1.0,
                    1.0 if o.is_urgent else 0.0,
                    1.0,  # node exists
                    0.0,  # padding
                ]
            else:
                feat = [0.0] * 6 + [0.0, 0.0]  # padding for non-existent candidate
            node_features[node_idx, :len(feat)] = feat
            node_features[node_idx, 8:] = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]  # type embedding: order

        # ---- ZONE nodes ----
        for z in range(self.n_zones):
            node_idx = self.zone_offset + z
            cx, cy = z % 4, z // 4
            is_active = 1.0 if z in env.active_wave_zones else 0.0
            node_features[node_idx] = [
                cx / 3.0, cy / 1.0, is_active, 0.0,
                0.0, 0.0, 0.0, 0.0,
                0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,  # type: zone
            ]

        # ---- TEMP nodes ----
        for t in range(self.n_temps):
            node_idx = self.temp_offset + t
            is_active = 1.0 if t in env.active_wave_temps else 0.0
            node_features[node_idx] = [
                t / 3.0, is_active, 0.0, 0.0,
                0.0, 0.0, 0.0, 0.0,
                0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0,  # type: temp
            ]

        # ---- WAVE node ----
        wave_idx = self.wave_offset
        node_features[wave_idx] = [
            len(env.active_wave_orders) / env.max_wave_orders,
            env.active_wave_volume / env.max_wave_volume,
            (env.current_time - env.active_wave_start_time) / 120 if env.active_wave_orders else 0,
            len(env.active_wave_zones) / self.n_zones,
            0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0,  # type: wave
        ]

        # ---- EDGES ----
        # 1. Order-Zone edges
        for i, o in enumerate(candidates[:self.k_candidates]):
            o_idx = self.order_offset + i
            for z in o.required_zones:
                z_idx = self.zone_offset + z
                edges_src.extend([o_idx, z_idx])
                edges_dst.extend([z_idx, o_idx])
                edge_types.extend([0, 0])  # type 0: order-zone

        # 2. Order-Temp edges
        for i, o in enumerate(candidates[:self.k_candidates]):
            o_idx = self.order_offset + i
            t_idx = self.temp_offset + o.dominant_temp
            edges_src.extend([o_idx, t_idx])
            edges_dst.extend([t_idx, o_idx])
            edge_types.extend([1, 1])  # type 1: order-temp

        # 3. Zone-Zone proximity edges
        for z in range(self.n_zones):
            z_idx = self.zone_offset + z
            for nz in self.zone_adj[z]:
                nz_idx = self.zone_offset + nz
                edges_src.extend([z_idx, nz_idx])
                edges_dst.extend([nz_idx, z_idx])
                edge_types.extend([2, 2])  # type 2: zone-zone

        # 4. Temp-Temp compatibility edges
        for t in range(self.n_temps):
            t_idx = self.temp_offset + t
            for ct in self.TEMP_COMPATIBILITY[t]:
                ct_idx = self.temp_offset + ct
                edges_src.append(t_idx)
                edges_dst.append(ct_idx)
                edge_types.append(3)  # type 3: temp-temp

        # 5. Wave-Order edges
        for i, o in enumerate(candidates[:self.k_candidates]):
            o_idx = self.order_offset + i
            edges_src.extend([wave_idx, o_idx])
            edges_dst.extend([o_idx, wave_idx])
            edge_types.extend([4, 4])  # type 4: wave-order

        # 6. Wave-Zone edges
        for z in env.active_wave_zones:
            z_idx = self.zone_offset + z
            edges_src.extend([wave_idx, z_idx])
            edges_dst.extend([z_idx, wave_idx])
            edge_types.extend([5, 5])  # type 5: wave-zone

        # 7. Wave-Temp edges
        for t in env.active_wave_temps:
            t_idx = self.temp_offset + t
            edges_src.extend([wave_idx, t_idx])
            edges_dst.extend([t_idx, wave_idx])
            edge_types.extend([6, 6])  # type 6: wave-temp

        if len(edges_src) == 0:
            # Empty graph fallback
            edge_index = np.zeros((2, 0), dtype=np.int64)
            edge_type = np.zeros(0, dtype=np.int64)
        else:
            edge_index = np.array([edges_src, edges_dst], dtype=np.int64)
            edge_type = np.array(edge_types, dtype=np.int64)

        return node_features, edge_index, edge_type


# =============================================================================
# 2. GRAPH ATTENTION NETWORK ENCODER (Self-Implemented)
# =============================================================================

class GATLayer(nn.Module):
    """
    Single Graph Attention Layer (simplified, no multi-head for stability).

    Reference: Veličković et al. "Graph Attention Networks" (ICLR 2018)
    """

    def __init__(self, in_dim, out_dim, dropout=0.1):
        super().__init__()
        self.in_dim = in_dim
        self.out_dim = out_dim

        self.W = nn.Linear(in_dim, out_dim, bias=False)
        self.a_src = nn.Linear(out_dim, 1, bias=False)
        self.a_dst = nn.Linear(out_dim, 1, bias=False)
        self.dropout = nn.Dropout(dropout)

        self._reset_parameters()

    def _reset_parameters(self):
        nn.init.xavier_uniform_(self.W.weight)
        nn.init.xavier_uniform_(self.a_src.weight)
        nn.init.xavier_uniform_(self.a_dst.weight)

    def forward(self, x, edge_index):
        """
        Args:
            x: (N, in_dim) node features
            edge_index: (2, E) edge list
        Returns:
            out: (N, out_dim) updated node features
        """
        # Linear transformation
        h = self.W(x)  # (N, out_dim)
        h = self.dropout(h)

        # Compute attention scores
        attn_src = self.a_src(h)  # (N, 1)
        attn_dst = self.a_dst(h)  # (N, 1)

        # Gather source and target attention
        src_idx = edge_index[0]  # (E,)
        dst_idx = edge_index[1]  # (E,)

        edge_attn = attn_src[src_idx] + attn_dst[dst_idx]  # (E, 1)
        edge_attn = F.leaky_relu(edge_attn, negative_slope=0.2)

        # Softmax normalization per destination node
        N = x.size(0)
        attn_exp = torch.exp(edge_attn - edge_attn.max())  # numerical stability

        # Sum of attention weights per destination
        attn_sum = torch.zeros(N, 1, device=x.device)
        attn_sum.scatter_add_(0, dst_idx.unsqueeze(1), attn_exp)

        # Normalize
        alpha = attn_exp / (attn_sum[dst_idx] + 1e-8)

        # Aggregate messages
        out = torch.zeros(N, self.out_dim, device=x.device)
        messages = alpha * h[src_idx]  # (E, out_dim)
        out.scatter_add_(0, dst_idx.unsqueeze(1).expand(-1, self.out_dim), messages)

        return F.elu(out)


class GATEncoder(nn.Module):
    """
    Graph Attention Network encoder that replaces the MLP state encoder.

    Architecture:
        Input: heterogeneous graph G_t = (V, E, X)
        Layer 1: GAT(in_dim=16, hidden_dim=64)
        Layer 2: GAT(hidden_dim=64, hidden_dim=64)
        Readout: mean pooling over order nodes + wave node -> state embedding
        Output: state_embedding (128-dim)
    """

    def __init__(self, node_dim=16, hidden_dim=64, out_dim=128, dropout=0.1):
        super().__init__()
        self.node_dim = node_dim
        self.hidden_dim = hidden_dim
        self.out_dim = out_dim

        self.gat1 = GATLayer(node_dim, hidden_dim, dropout)
        self.gat2 = GATLayer(hidden_dim, hidden_dim, dropout)

        # Readout: combine order nodes and wave node
        self.readout_attn = nn.Linear(hidden_dim, 1)
        self.readout_proj = nn.Linear(hidden_dim, out_dim)

        self.dropout = nn.Dropout(dropout)
        self._reset_parameters()

    def _reset_parameters(self):
        nn.init.xavier_uniform_(self.readout_proj.weight)
        nn.init.xavier_uniform_(self.readout_attn.weight)

    def forward(self, node_features, edge_index, n_orders=10):
        """
        Args:
            node_features: (N, node_dim)
            edge_index: (2, E)
            n_orders: number of order nodes to consider
        Returns:
            state_embedding: (out_dim,)
        """
        # GAT layers
        h = self.gat1(node_features, edge_index)
        h = self.dropout(h)
        h = self.gat2(h, edge_index)

        # Readout: weighted average over order nodes + wave node
        order_nodes = h[:n_orders]  # (k_candidates, hidden_dim)
        wave_node = h[-1:]  # (1, hidden_dim)

        # Attention weights for order nodes
        attn_scores = self.readout_attn(order_nodes)  # (k_candidates, 1)
        attn_weights = F.softmax(attn_scores, dim=0)
        order_repr = (attn_weights * order_nodes).sum(dim=0)  # (hidden_dim,)

        # Combine with wave node
        combined = order_repr + wave_node.squeeze(0)
        state_embedding = self.readout_proj(combined)

        return F.relu(state_embedding)


# =============================================================================
# 3. KNOWLEDGE-GUIDED PPO AGENT
# =============================================================================

class KnowledgeGuidedPolicyNet(nn.Module):
    """Policy network with GAT encoder + MLP head"""

    def __init__(self, node_dim=16, hidden_dim=64, gat_out_dim=128, action_dim=11, dropout=0.1):
        super().__init__()
        self.gat_encoder = GATEncoder(node_dim, hidden_dim, gat_out_dim, dropout)

        # Policy head: MLP over graph embedding
        self.fc1 = nn.Linear(gat_out_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, action_dim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, node_features, edge_index, n_orders=10):
        embedding = self.gat_encoder(node_features, edge_index, n_orders)
        x = F.relu(self.fc1(embedding))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        return F.relu(self.fc3(x))


class KnowledgeGuidedValueNet(nn.Module):
    """Value network with GAT encoder + MLP head"""

    def __init__(self, node_dim=16, hidden_dim=64, gat_out_dim=128, dropout=0.1):
        super().__init__()
        self.gat_encoder = GATEncoder(node_dim, hidden_dim, gat_out_dim, dropout)

        self.fc1 = nn.Linear(gat_out_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, 1)
        self.dropout = nn.Dropout(dropout)

    def forward(self, node_features, edge_index, n_orders=10):
        embedding = self.gat_encoder(node_features, edge_index, n_orders)
        x = F.relu(self.fc1(embedding))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        return self.fc3(x)


class KnowledgeGuidedPPO:
    """
    Knowledge-Guided PPO Agent.

    Key features:
    1. GAT-based state encoding (replaces MLP)
    2. Knowledge graph injection via KL divergence:
       L_total = L_PPO_CLIP + lambda_kg * D_KL(pi_theta || pi_TZU)
    3. TZU heuristic pre-training support
    """

    def __init__(self, node_dim=16, action_dim=11, hidden_dim=64, gat_out_dim=128,
                 actor_lr=5e-4, critic_lr=1e-5, gamma=0.96, lmbda=0.95,
                 epochs=10, eps=0.2, lambda_kg=0.1, device='cpu'):

        self.device = torch.device(device)
        self.action_dim = action_dim
        self.lambda_kg = lambda_kg
        self.epochs = epochs
        self.eps = eps
        self.gamma = gamma
        self.lmbda = lmbda
        self.k_candidates = action_dim - 1

        self.actor = KnowledgeGuidedPolicyNet(
            node_dim, hidden_dim, gat_out_dim, action_dim
        ).to(self.device)
        self.critic = KnowledgeGuidedValueNet(
            node_dim, hidden_dim, gat_out_dim
        ).to(self.device)

        self.actor_optimizer = torch.optim.Adam(self.actor.parameters(), lr=actor_lr)
        self.critic_optimizer = torch.optim.Adam(self.critic.parameters(), lr=critic_lr)

        self.actor_losses = []
        self.critic_losses = []
        self.kg_losses = []

        # Knowledge graph builder
        self.kg = KnowledgeGraph(n_zones=8, n_temps=4, k_candidates=self.k_candidates)

    def _get_graph_state(self, env: PharmaWaveEnv, state_dict: Dict):
        """Convert environment state to graph tensors"""
        node_features, edge_index, edge_type = self.kg.build_graph(env, state_dict)

        node_features = torch.tensor(node_features, dtype=torch.float).to(self.device)
        if edge_index.shape[1] > 0:
            edge_index = torch.tensor(edge_index, dtype=torch.long).to(self.device)
        else:
            edge_index = torch.zeros((2, 0), dtype=torch.long, device=self.device)

        return node_features, edge_index

    def _compute_tzu_probs(self, env: PharmaWaveEnv, state_dict: Dict,
                           valid_actions: List[int]) -> torch.Tensor:
        """
        Compute TZU heuristic probability distribution.
        Returns soft-max distribution over valid actions.
        """
        candidates = env._get_candidates()
        n_candidates = len(candidates)

        probs = torch.zeros(self.action_dim, device=self.device)

        if n_candidates == 0:
            probs[self.action_dim - 1] = 1.0
            return probs

        scores = []
        generator = DataGenerator(seed=42)

        for i in range(self.action_dim - 1):
            if i >= len(candidates) or i not in valid_actions:
                scores.append(-1e6)
                continue

            o = candidates[i]

            # Temperature match
            temp_match = 1.0 if (o.dominant_temp in env.active_wave_temps or
                                 not env.active_wave_temps) else 0.0

            # Zone proximity
            if env.active_wave_zones:
                wcx = np.mean([generator.zone_coords[z][0] for z in env.active_wave_zones])
                wcy = np.mean([generator.zone_coords[z][1] for z in env.active_wave_zones])
                ox, oy = o.zone_centroid
                zone_prox = 1.0 / (1.0 + abs(ox - wcx) + abs(oy - wcy))
            else:
                zone_prox = 1.0

            # Urgency
            remaining = (o.arrival_time + o.deadline * 60) - env.current_time
            urgency = 1.0 / (1.0 + max(0, remaining / 60))

            score = 0.4 * temp_match + 0.4 * zone_prox + 0.2 * urgency
            scores.append(score)

        # Close wave score (last action)
        if self.action_dim - 1 in valid_actions:
            wave_fill = len(env.active_wave_orders) / env.max_wave_orders
            close_score = wave_fill * 2.0
            scores.append(close_score)
        else:
            scores.append(-1e6)

        # Softmax with temperature
        scores_t = torch.tensor(scores, dtype=torch.float, device=self.device)
        scores_t = scores_t / 0.5  # temperature
        scores_t = scores_t - scores_t.max()  # numerical stability
        exp_scores = torch.exp(scores_t)

        # Mask invalid actions
        mask = torch.zeros(self.action_dim, device=self.device)
        for a in valid_actions:
            mask[a] = 1.0

        masked_exp = exp_scores * mask
        if masked_exp.sum() > 1e-8:
            probs = masked_exp / masked_exp.sum()
        else:
            probs = mask / mask.sum()

        return probs

    def select_action(self, env: PharmaWaveEnv, state_dict: Dict,
                      valid_actions: List[int], deterministic=False):
        """Select action using GAT-encoded policy"""
        node_features, edge_index = self._get_graph_state(env, state_dict)
        n_orders = min(len(env._get_candidates()), self.k_candidates)

        with torch.no_grad():
            probs_raw = self.actor(node_features, edge_index, n_orders)

        # Mask invalid actions
        mask = torch.zeros(self.action_dim, device=self.device)
        mask[valid_actions] = 1.0

        probs = probs_raw * mask
        if probs.sum() < 1e-8:
            probs = mask / mask.sum()
        else:
            probs = probs / probs.sum()

        if deterministic:
            action = torch.argmax(probs).item()
        else:
            dist = torch.distributions.Categorical(probs)
            action = dist.sample().item()

        log_prob = torch.log(probs[action] + 1e-8)

        return action, log_prob.item(), probs.cpu().numpy()

    def compute_advantages(self, rewards, values, next_values, dones):
        """GAE advantage computation"""
        advantages = []
        gae = 0.0

        for t in reversed(range(len(rewards))):
            delta = rewards[t] + self.gamma * next_values[t] * (1 - dones[t]) - values[t]
            gae = delta + self.gamma * self.lmbda * gae * (1 - dones[t])
            advantages.insert(0, gae)

        return np.array(advantages)

    def update(self, trajectory):
        """
        Update actor and critic with knowledge-guided PPO loss.
        """
        # Unpack trajectory
        actions = np.array([t['action'] for t in trajectory])
        old_log_probs = np.array([t['log_prob'] for t in trajectory])
        rewards = np.array([t['reward'] for t in trajectory])
        dones = np.array([t['done'] for t in trajectory])
        valid_masks = [t['valid_actions'] for t in trajectory]
        graph_states = [t['graph_state'] for t in trajectory]
        tzu_probs_list = [t.get('tzu_probs', None) for t in trajectory]

        batch_size = len(trajectory)

        # Compute values using graph critic
        values_list = []
        next_values_list = []

        with torch.no_grad():
            for gs in graph_states:
                node_f, edge_i = gs
                v = self.critic(node_f, edge_i).squeeze().cpu().item()
                values_list.append(v)
            for i in range(len(graph_states)):
                if i + 1 < len(graph_states):
                    node_f, edge_i = graph_states[i + 1]
                else:
                    node_f, edge_i = graph_states[i]
                v = self.critic(node_f, edge_i).squeeze().cpu().item()
                next_values_list.append(v)

        values = np.array(values_list)
        next_values = np.array(next_values_list)

        # Compute advantages
        advantages = self.compute_advantages(rewards, values, next_values, dones)
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        td_target = advantages + values

        # Prepare tensors
        actions_t = torch.tensor(actions, dtype=torch.long).view(-1, 1).to(self.device)
        old_log_probs_t = torch.tensor(old_log_probs, dtype=torch.float).view(-1, 1).to(self.device)
        advantages_t = torch.tensor(advantages, dtype=torch.float).view(-1, 1).to(self.device)
        td_target_t = torch.tensor(td_target, dtype=torch.float).view(-1, 1).to(self.device)

        # PPO + KG update
        for epoch in range(self.epochs):
            log_probs_all = []
            values_pred = []
            pi_theta_all = []

            for i in range(batch_size):
                node_f, edge_i = graph_states[i]

                n_orders = min(len(valid_masks[i]) - (1 if self.action_dim - 1 in valid_masks[i] else 0),
                               self.k_candidates)

                # Actor output
                probs_raw = self.actor(node_f, edge_i, n_orders)
                mask = torch.zeros(self.action_dim, device=self.device)
                for a in valid_masks[i]:
                    mask[a] = 1.0
                masked = probs_raw * mask
                if masked.sum() < 1e-8:
                    probs = mask / mask.sum()
                else:
                    probs = masked / masked.sum()

                log_prob_i = torch.log(probs[actions[i]] + 1e-8)
                log_probs_all.append(log_prob_i)
                pi_theta_all.append(probs)

                # Critic value
                v_i = self.critic(node_f, edge_i)
                values_pred.append(v_i)

            log_probs_t = torch.stack(log_probs_all).view(-1, 1)
            values_t = torch.stack(values_pred).view(-1, 1)

            # PPO loss
            ratio = torch.exp(log_probs_t - old_log_probs_t)
            surr1 = ratio * advantages_t
            surr2 = torch.clamp(ratio, 1 - self.eps, 1 + self.eps) * advantages_t
            actor_loss_ppo = -torch.min(surr1, surr2).mean()

            # Knowledge-guided KL loss
            kg_loss_val = 0.0
            kl_count = 0
            for i in range(batch_size):
                if tzu_probs_list[i] is not None:
                    tzu_p = tzu_probs_list[i]
                    pi_theta = pi_theta_all[i]

                    # KL(pi_theta || pi_TZU) = sum(pi_theta * log(pi_theta / pi_TZU))
                    mask = torch.zeros(self.action_dim, device=self.device)
                    for a in valid_masks[i]:
                        mask[a] = 1.0
                    valid = mask > 0

                    if valid.sum() > 0:
                        kl_i = (pi_theta[valid] * torch.log(
                            (pi_theta[valid] + 1e-8) / (tzu_p[valid] + 1e-8)
                        )).sum()
                        kg_loss_val += kl_i.item()
                        kl_count += 1

            if kl_count > 0:
                kg_loss = torch.tensor(kg_loss_val / kl_count, device=self.device)
            else:
                kg_loss = torch.tensor(0.0, device=self.device)

            # Total loss
            actor_loss = actor_loss_ppo + self.lambda_kg * kg_loss
            critic_loss = F.mse_loss(values_t, td_target_t)

            # Backprop
            self.actor_optimizer.zero_grad()
            self.critic_optimizer.zero_grad()
            actor_loss.backward()
            critic_loss.backward()

            torch.nn.utils.clip_grad_norm_(self.actor.parameters(), 0.5)
            torch.nn.utils.clip_grad_norm_(self.critic.parameters(), 0.5)

            self.actor_optimizer.step()
            self.critic_optimizer.step()

            self.actor_losses.append(actor_loss.item())
            self.critic_losses.append(critic_loss.item())
            self.kg_losses.append(kg_loss.item())


# =============================================================================
# 4. PRE-TRAINING WITH TZU DEMONSTRATIONS
# =============================================================================

def generate_tzu_demonstrations(generator: DataGenerator, n_episodes=50) -> List[Dict]:
    """
    Generate demonstration trajectories using TZU heuristic.
    These will be used for behavioral cloning pre-training.
    """
    demonstrations = []

    for ep in tqdm(range(n_episodes), desc="Generating TZU demonstrations"):
        orders = generator.generate_orders(horizon_hours=4.0)
        env = PharmaWaveEnv(orders)
        state_dict = env.reset()

        trajectory = []
        episode_reward = 0.0

        while not env.done:
            valid_actions = env.get_valid_actions(state_dict)
            candidates = env._get_candidates()

            if not candidates or len(valid_actions) == 0:
                action = env.k_candidates
            else:
                # Compute TZU score for each valid candidate
                best_score = -float('inf')
                best_action = env.k_candidates

                for i, o in enumerate(candidates):
                    if i not in valid_actions:
                        continue

                    temp_match = 1.0 if (o.dominant_temp in env.active_wave_temps or
                                         not env.active_wave_temps) else 0.0

                    if env.active_wave_zones:
                        wcx = np.mean([generator.zone_coords[z][0] for z in env.active_wave_zones])
                        wcy = np.mean([generator.zone_coords[z][1] for z in env.active_wave_zones])
                        ox, oy = o.zone_centroid
                        zone_prox = 1.0 / (1.0 + abs(ox - wcx) + abs(oy - wcy))
                    else:
                        zone_prox = 1.0

                    remaining = (o.arrival_time + o.deadline * 60) - env.current_time
                    urgency = 1.0 / (1.0 + max(0, remaining / 60))

                    score = 0.4 * temp_match + 0.4 * zone_prox + 0.2 * urgency
                    if score > best_score:
                        best_score = score
                        best_action = i

                action = best_action

            # Get graph state before step
            kg = KnowledgeGraph()
            node_f, edge_i, _ = kg.build_graph(env, state_dict)
            graph_state = (torch.tensor(node_f, dtype=torch.float),
                          torch.tensor(edge_i, dtype=torch.long))

            state_vec = env.get_state_vector(state_dict)

            next_state_vec, reward, done, info = env.step(action)
            next_state_dict = env.get_state()

            trajectory.append({
                'state_vec': state_vec,
                'graph_state': graph_state,
                'action': action,
                'reward': reward,
                'next_state_vec': next_state_vec,
                'next_graph_state': graph_state,
                'done': float(done),
                'valid_actions': valid_actions,
                'state_dict': state_dict,
            })

            episode_reward += reward
            state_dict = next_state_dict

        demonstrations.append({
            'trajectory': trajectory,
            'total_reward': episode_reward,
            'n_waves': len(env.waves)
        })

    return demonstrations


def pretrain_kgdrl_with_tzu(agent: KnowledgeGuidedPPO,
                             demonstrations: List[Dict],
                             epochs=20, lr=1e-3):
    """
    Behavioral cloning pre-training using TZU demonstrations.
    Trains the actor to mimic TZU policy via supervised learning.
    """
    print(f"[Pre-training] {len(demonstrations)} demonstrations, {epochs} epochs")

    # Flatten all transitions
    all_transitions = []
    for demo in demonstrations:
        all_transitions.extend(demo['trajectory'])

    # Create optimizer with higher learning rate for pre-training
    pretrain_optimizer = torch.optim.Adam(agent.actor.parameters(), lr=lr)
    agent.actor.train()

    for epoch in range(epochs):
        total_loss = 0.0
        correct = 0
        count = 0

        # Shuffle and batch
        indices = np.random.permutation(len(all_transitions))

        for idx in indices:
            trans = all_transitions[idx]
            node_f, edge_i = trans['graph_state']
            node_f = node_f.to(agent.device).requires_grad_(True)
            if edge_i.numel() > 0:
                edge_i = edge_i.to(agent.device)
            else:
                edge_i = torch.zeros((2, 0), dtype=torch.long, device=agent.device)
            action = trans['action']
            valid_actions = trans['valid_actions']

            n_orders = min(len(valid_actions) - (1 if agent.action_dim - 1 in valid_actions else 0),
                           agent.k_candidates)

            probs_raw = agent.actor(node_f, edge_i, n_orders)
            mask = torch.zeros(agent.action_dim, device=agent.device)
            for a in valid_actions:
                mask[a] = 1.0
            masked = probs_raw * mask

            if masked.sum() < 1e-8:
                # Fallback: uniform over valid actions
                probs = mask.float() / mask.sum()
            else:
                probs = masked / masked.sum()

            # Cross-entropy loss
            loss = -torch.log(probs[action] + 1e-8)

            if loss.requires_grad:
                pretrain_optimizer.zero_grad()
                loss.backward()
                pretrain_optimizer.step()

            total_loss += loss.item()
            pred = torch.argmax(probs.detach()).item()
            if pred == action:
                correct += 1
            count += 1

        acc = correct / max(count, 1)
        avg_loss = total_loss / max(count, 1)
        print(f"  Epoch {epoch+1}/{epochs}: Loss={avg_loss:.4f}, Acc={acc:.3f}")

    print("[Pre-training] Complete.")
    return agent


# =============================================================================
# 5. TRAINING AND EVALUATION
# =============================================================================

def train_kgdrl(generator: DataGenerator,
                n_episodes=120,
                update_interval=20,
                pretrain=True,
                n_pretrain_demos=30,
                lambda_kg=0.1,
                device='cpu'):
    """Train KGDRL agent with optional TZU pre-training"""

    if not TORCH_AVAILABLE:
        print("PyTorch not available. Skipping KGDRL training.")
        return None, []

    # Create agent
    env_temp = PharmaWaveEnv(generator.generate_orders(horizon_hours=4.0))
    action_dim = env_temp.action_dim

    agent = KnowledgeGuidedPPO(
        node_dim=16,
        action_dim=action_dim,
        hidden_dim=64,
        gat_out_dim=128,
        lambda_kg=lambda_kg,
        device=device
    )

    # Optional: Pre-train with TZU demonstrations
    if pretrain:
        print("\n[KGDRL] Generating TZU demonstrations for pre-training...")
        demos = generate_tzu_demonstrations(generator, n_episodes=n_pretrain_demos)
        agent = pretrain_kgdrl_with_tzu(agent, demos, epochs=10, lr=1e-3)

    episode_rewards = []
    episode_metrics = []

    for episode in tqdm(range(n_episodes), desc="Training KGDRL"):
        orders = generator.generate_orders(horizon_hours=4.0)
        env = PharmaWaveEnv(orders)
        state_dict = env.reset()

        trajectory = []
        episode_reward = 0.0

        while not env.done:
            valid_actions = env.get_valid_actions(state_dict)

            action, log_prob, probs = agent.select_action(
                env, state_dict, valid_actions, deterministic=False
            )

            # Get graph state
            node_f, edge_i = agent._get_graph_state(env, state_dict)
            graph_state = (node_f, edge_i)

            # Compute TZU probs for KL loss
            tzu_probs = agent._compute_tzu_probs(env, state_dict, valid_actions)

            state_vec = env.get_state_vector(state_dict)

            next_state_vec, reward, done, info = env.step(action)
            next_state_dict = env.get_state()

            trajectory.append({
                'state_vec': state_vec,
                'graph_state': graph_state,
                'action': action,
                'log_prob': log_prob,
                'reward': reward,
                'next_state_vec': next_state_vec,
                'done': float(done),
                'valid_actions': valid_actions,
                'tzu_probs': tzu_probs,
            })

            episode_reward += reward
            state_dict = next_state_dict

        episode_rewards.append(episode_reward)
        episode_metrics.append({
            'reward': episode_reward,
            'n_waves': len(env.waves),
            'distance': env.total_picking_distance,
            'misses': env.deadline_misses,
            'violations': env.temp_violations
        })

        # PPO update
        if len(trajectory) > 0 and (episode + 1) % update_interval == 0:
            agent.update(trajectory)

    return agent, episode_metrics


def evaluate_kgdrl(agent: KnowledgeGuidedPPO,
                   generator: DataGenerator,
                   n_eval=20) -> List[Dict]:
    """Evaluate KGDRL agent"""
    results = []

    for i in tqdm(range(n_eval), desc="Evaluating KGDRL"):
        orders = generator.generate_orders(horizon_hours=4.0)
        env = PharmaWaveEnv(orders)
        state_dict = env.reset()

        total_reward = 0.0

        while not env.done:
            valid_actions = env.get_valid_actions(state_dict)
            action, _, _ = agent.select_action(env, state_dict, valid_actions, deterministic=True)

            _, reward, done, info = env.step(action)
            state_dict = env.get_state()
            total_reward += reward

        results.append({
            'total_reward': total_reward,
            'n_waves': len(env.waves),
            'total_distance': env.total_picking_distance,
            'deadline_misses': env.deadline_misses,
            'temp_violations': env.temp_violations,
            'avg_wave_size': np.mean([w['orders'] for w in env.waves]) if env.waves else 0
        })

    return results


# =============================================================================
# 6. ABLATION STUDY
# =============================================================================

def run_ablation_study(generator: DataGenerator,
                       n_ppo_episodes=120,
                       n_kgdrl_episodes=120,
                       n_eval=20,
                       pretrain=True,
                       lambda_kg=0.1,
                       device='cpu') -> Dict:
    """
    Run ablation study comparing:
    1. Vanilla PPO (MLP encoder)
    2. KGDRL with GAT but no KL loss (lambda_kg=0)
    3. KGDRL full (GAT + KL loss)
    4. Heuristic baselines (FCFS, TZU)
    """

    results = {}

    # --- Heuristic baselines ---
    print("\n" + "="*60)
    print("ABLATION STUDY")
    print("="*60)

    print("\n[1] Running heuristic baselines...")
    heuristic_summary, _ = compare_heuristics(generator, n_instances=n_eval)
    results['heuristics'] = heuristic_summary

    # --- Vanilla PPO ---
    if TORCH_AVAILABLE:
        print("\n[2] Training Vanilla PPO (MLP encoder)...")
        from pharma_wave_allocation import train_ppo
        ppo_agent, ppo_train_metrics = train_ppo(
            generator, n_episodes=n_ppo_episodes, update_interval=20
        )
        ppo_eval = evaluate_ppo_agent(ppo_agent, generator, n_eval=n_eval, use_ppo=True)

        results['vanilla_ppo'] = {
            'train_metrics': ppo_train_metrics,
            'eval': {
                'avg_reward': float(np.mean([r['total_reward'] for r in ppo_eval])),
                'std_reward': float(np.std([r['total_reward'] for r in ppo_eval])),
                'avg_distance': float(np.mean([r['total_distance'] for r in ppo_eval])),
                'avg_waves': float(np.mean([r['n_waves'] for r in ppo_eval])),
                'avg_misses': float(np.mean([r['deadline_misses'] for r in ppo_eval])),
                'avg_violations': float(np.mean([r['temp_violations'] for r in ppo_eval])),
            }
        }

        # --- KGDRL without KL (lambda=0) ---
        print("\n[3] Training KGDRL-GAT (no KL guidance)...")
        kgdrl_no_kl, kgdrl_no_kl_metrics = train_kgdrl(
            generator, n_episodes=n_kgdrl_episodes, update_interval=20,
            pretrain=pretrain, lambda_kg=0.0, device=device
        )
        kgdrl_no_kl_eval = evaluate_kgdrl(kgdrl_no_kl, generator, n_eval=n_eval)

        results['kgdrl_no_kl'] = {
            'train_metrics': kgdrl_no_kl_metrics,
            'eval': {
                'avg_reward': float(np.mean([r['total_reward'] for r in kgdrl_no_kl_eval])),
                'std_reward': float(np.std([r['total_reward'] for r in kgdrl_no_kl_eval])),
                'avg_distance': float(np.mean([r['total_distance'] for r in kgdrl_no_kl_eval])),
                'avg_waves': float(np.mean([r['n_waves'] for r in kgdrl_no_kl_eval])),
                'avg_misses': float(np.mean([r['deadline_misses'] for r in kgdrl_no_kl_eval])),
                'avg_violations': float(np.mean([r['temp_violations'] for r in kgdrl_no_kl_eval])),
            }
        }

        # --- KGDRL full ---
        print("\n[4] Training KGDRL-Full (GAT + KL guidance)...")
        kgdrl_full, kgdrl_full_metrics = train_kgdrl(
            generator, n_episodes=n_kgdrl_episodes, update_interval=20,
            pretrain=pretrain, lambda_kg=lambda_kg, device=device
        )
        kgdrl_full_eval = evaluate_kgdrl(kgdrl_full, generator, n_eval=n_eval)

        results['kgdrl_full'] = {
            'train_metrics': kgdrl_full_metrics,
            'eval': {
                'avg_reward': float(np.mean([r['total_reward'] for r in kgdrl_full_eval])),
                'std_reward': float(np.std([r['total_reward'] for r in kgdrl_full_eval])),
                'avg_distance': float(np.mean([r['total_distance'] for r in kgdrl_full_eval])),
                'avg_waves': float(np.mean([r['n_waves'] for r in kgdrl_full_eval])),
                'avg_misses': float(np.mean([r['deadline_misses'] for r in kgdrl_full_eval])),
                'avg_violations': float(np.mean([r['temp_violations'] for r in kgdrl_full_eval])),
            }
        }

    # Save results
    with open('ablation_study.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Print summary
    print("\n" + "="*60)
    print("ABLATION STUDY RESULTS")
    print("="*60)
    print(f"{'Method':<20} {'Avg Reward':<12} {'Avg Dist':<12} {'Avg Waves':<12} {'Misses':<10} {'Viol.':<8}")
    print("-"*60)

    for h, stats in heuristic_summary.items():
        print(f"{h:<20} {stats['avg_reward']:<12.1f} {stats['avg_distance']:<12.1f} "
              f"{stats['avg_waves']:<12.1f} {stats['avg_misses']:<10.1f} {stats['avg_violations']:<8.1f}")

    if TORCH_AVAILABLE:
        print(f"{'Vanilla PPO':<20} {results['vanilla_ppo']['eval']['avg_reward']:<12.1f} "
              f"{results['vanilla_ppo']['eval']['avg_distance']:<12.1f} "
              f"{results['vanilla_ppo']['eval']['avg_waves']:<12.1f} "
              f"{results['vanilla_ppo']['eval']['avg_misses']:<10.1f} "
              f"{results['vanilla_ppo']['eval']['avg_violations']:<8.1f}")
        print(f"{'KGDRL-GAT (no KL)':<20} {results['kgdrl_no_kl']['eval']['avg_reward']:<12.1f} "
              f"{results['kgdrl_no_kl']['eval']['avg_distance']:<12.1f} "
              f"{results['kgdrl_no_kl']['eval']['avg_waves']:<12.1f} "
              f"{results['kgdrl_no_kl']['eval']['avg_misses']:<10.1f} "
              f"{results['kgdrl_no_kl']['eval']['avg_violations']:<8.1f}")
        print(f"{'KGDRL-Full':<20} {results['kgdrl_full']['eval']['avg_reward']:<12.1f} "
              f"{results['kgdrl_full']['eval']['avg_distance']:<12.1f} "
              f"{results['kgdrl_full']['eval']['avg_waves']:<12.1f} "
              f"{results['kgdrl_full']['eval']['avg_misses']:<10.1f} "
              f"{results['kgdrl_full']['eval']['avg_violations']:<8.1f}")

    print("="*60)
    print("Results saved to ablation_study.json")

    return results


# =============================================================================
# 7. MAIN EXECUTION
# =============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("KGDRL v2 - Knowledge-Guided Deep RL")
    print("Pharmaceutical Smart Wave Allocation")
    print("=" * 60)

    if not TORCH_AVAILABLE:
        print("ERROR: PyTorch is required for KGDRL.")
        print("Install with: pip install torch")
        exit(1)

    # Initialize
    generator = DataGenerator(seed=42)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Device: {device}")

    # Run ablation study
    results = run_ablation_study(
        generator,
        n_ppo_episodes=120,
        n_kgdrl_episodes=120,
        n_eval=20,
        pretrain=True,
        lambda_kg=0.1,
        device=device
    )

    print("\nDone!")
