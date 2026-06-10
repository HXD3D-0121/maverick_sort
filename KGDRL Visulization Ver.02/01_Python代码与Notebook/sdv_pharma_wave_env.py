"""
Smart Wave Allocation for Pharmaceutical Distribution
Deep Reinforcement Learning Implementation (PPO)
Based on SDV-generated realistic simulation data
"""

import numpy as np
import random
import math
import collections
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass, field
import pandas as pd
from datetime import datetime, timedelta
import json

# Try importing torch, fallback to numpy-only if unavailable
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("Warning: PyTorch not available. DRL training will use numpy fallback.")

# =============================================================================
# 1. DATA LOADING FROM SDV-GENERATED CSVs
# =============================================================================

class SDVDataLoader:
    """Loads and preprocesses SDV-generated simulation data."""

    def __init__(self, data_dir="../../simulation_data/generated_datasets_sdv_SMALL"):
        self.data_dir = data_dir
        self.orders = None
        self.order_lines = None
        self.products = None
        self.warehouses = None
        self.customers = None
        self._load_all()

    def _load_all(self):
        print("[DataLoader] Loading SDV simulation datasets...")
        self.orders = pd.read_csv(f"{self.data_dir}/orders.csv")
        self.order_lines = pd.read_csv(f"{self.data_dir}/order_lines.csv")
        self.products = pd.read_csv(f"{self.data_dir}/products.csv")
        self.warehouses = pd.read_csv(f"{self.data_dir}/warehouses.csv")
        self.customers = pd.read_csv(f"{self.data_dir}/customers.csv")

        # Parse datetime
        self.orders['order_datetime'] = pd.to_datetime(self.orders['order_datetime'])
        self.orders['required_delivery_date'] = pd.to_datetime(self.orders['required_delivery_date'])

        # Build lookups
        self.sku_to_temp = dict(zip(self.products['sku_id'], self.products['storage_temperature']))
        self.sku_to_volume = dict(zip(self.products['sku_id'], self.products['unit_volume_liters']))
        self.sku_to_weight = dict(zip(self.products['sku_id'], self.products['unit_weight_kg']))
        self.sku_to_abc = dict(zip(self.products['sku_id'], self.products['abc_class']))

        # Temperature to numeric
        self.temp_map = {'ambient': 0, 'cool': 1, 'cold': 2, 'frozen': 3}
        self.temp_names = ['ambient', 'cool', 'cold', 'frozen']

        # Build order details
        self.order_details = self._build_order_details()

        print(f"[DataLoader] Loaded {len(self.orders)} orders, {len(self.order_lines)} lines, {len(self.products)} SKUs")

    def _build_order_details(self):
        """Aggregate order_lines into order-level features."""
        details = {}

        grouped = self.order_lines.groupby('order_id')
        for order_id, group in grouped:
            skus = group['sku_id'].tolist()
            qtys = group['quantity_ordered'].tolist()

            temps = [self.sku_to_temp.get(s, 'ambient') for s in skus]
            volumes = [self.sku_to_volume.get(s, 0.1) * q for s, q in zip(skus, qtys)]
            weights = [self.sku_to_weight.get(s, 0.1) * q for s, q in zip(skus, qtys)]

            dominant_temp = max(set(temps), key=temps.count)

            details[order_id] = {
                'skus': skus,
                'quantities': qtys,
                'temps': temps,
                'dominant_temp': dominant_temp,
                'dominant_temp_idx': self.temp_map[dominant_temp],
                'total_volume': sum(volumes),
                'total_weight': sum(weights),
                'n_skus': len(skus),
                'temp_set': set(temps),
                'has_special_handling': any(t in ['cold', 'frozen'] for t in temps),
            }
        return details

    def get_orders_for_warehouse(self, warehouse_id):
        """Get all orders assigned to a specific warehouse."""
        wh_orders = self.orders[self.orders['warehouse_id'] == warehouse_id].copy()
        wh_orders = wh_orders.sort_values('order_datetime').reset_index(drop=True)

        # Convert to internal Order objects
        orders = []
        base_time = wh_orders['order_datetime'].min()

        for idx, row in wh_orders.iterrows():
            oid = row['order_id']
            detail = self.order_details.get(oid, {})
            if not detail:
                continue

            arrival_min = (row['order_datetime'] - base_time).total_seconds() / 60.0

            # Deadline: hours from arrival to required delivery
            deadline_hours = (row['required_delivery_date'] - row['order_datetime']).total_seconds() / 3600.0
            deadline_hours = max(2, min(deadline_hours, 72))  # Clamp 2-72h

            # Priority score
            priority = row['priority_level']
            priority_score = {'normal': 0, 'high': 1, 'urgent': 2}[priority]

            orders.append({
                'order_id': oid,
                'arrival_time': arrival_min,
                'deadline_hours': deadline_hours,
                'priority': priority,
                'priority_score': priority_score,
                'warehouse_id': warehouse_id,
                'n_skus': detail['n_skus'],
                'total_volume': detail['total_volume'],
                'total_weight': detail['total_weight'],
                'dominant_temp': detail['dominant_temp'],
                'dominant_temp_idx': detail['dominant_temp_idx'],
                'temp_set': detail['temp_set'],
                'has_special_handling': detail['has_special_handling'],
                'skus': detail['skus'],
            })

        return orders


# =============================================================================
# 2. ENVIRONMENT DEFINITION (SDV-Based Realistic Data)
# =============================================================================

class SDVPharmaWaveEnv:
    """
    Smart Wave Allocation Environment using SDV-generated realistic data.

    State: Current wave status + order pool + temporal info
    Action: Select order to add to wave, or close wave
    Reward: Picking efficiency + compliance + timeliness
    """

    def __init__(self,
                 orders: List[Dict],
                 warehouse_bins: Dict[str, List[Tuple[str, str]]],
                 sku_to_temp: Dict[str, str] = None,
                 max_wave_orders: int = 50,
                 max_wave_volume: float = 150.0,
                 max_wave_weight: float = 80.0,
                 picking_speed: float = 60.0,
                 setup_time: float = 10.0,
                 time_step: float = 5.0,
                 alpha_eff: float = 1.0,
                 alpha_temp: float = 100.0,
                 alpha_deadline: float = 40.0,
                 alpha_setup: float = 8.0,
                 alpha_priority: float = 20.0,
                 alpha_completion: float = 3.0,
                 alpha_unprocessed_penalty: float = 50.0,
                 k_candidates: int = 10,
                 max_steps: int = 5000):

        self.all_orders = orders
        self.warehouse_bins = warehouse_bins
        self.sku_to_temp = sku_to_temp or {}
        self.max_wave_orders = max_wave_orders
        self.max_wave_volume = max_wave_volume
        self.max_wave_weight = max_wave_weight
        self.picking_speed = picking_speed
        self.setup_time = setup_time
        self.time_step = time_step

        # Reward coefficients
        self.alpha_eff = alpha_eff
        self.alpha_temp = alpha_temp
        self.alpha_deadline = alpha_deadline
        self.alpha_setup = alpha_setup
        self.alpha_priority = alpha_priority
        self.alpha_completion = alpha_completion
        self.alpha_unprocessed_penalty = alpha_unprocessed_penalty
        self.max_steps = max_steps

        self.k_candidates = k_candidates
        self.n_temps = 4

        # Build bin zones for distance calculation
        self._build_zone_topology()

        # Internal state
        self.current_time = 0.0
        self.order_pool: List[Dict] = []
        self.pending_orders: List[Dict] = []  # Not yet arrived
        self.waves: List[Dict] = []

        # Active wave
        self.active_wave_orders: List[Dict] = []
        self.active_wave_volume = 0.0
        self.active_wave_weight = 0.0
        self.active_wave_start_time = 0.0
        self.active_wave_temps: set = set()
        self.active_wave_skus: set = set()

        # Tracking
        self.total_picking_distance = 0.0
        self.total_setup_time = 0.0
        self.deadline_misses = 0
        self.temp_violations = 0
        self.priority_score_sum = 0

        self.done = False
        self.step_count = 0

    def _build_zone_topology(self):
        """Build simplified zone coordinate mapping from bin IDs."""
        self.zone_coords = {}
        self.bin_to_zone = {}

        zone_idx = 0
        for wh_id, bins in self.warehouse_bins.items():
            for bin_id, temp in bins:
                # Extract zone from bin_id like "WH_001_AMBIENT_111"
                parts = bin_id.split('_')
                if len(parts) >= 3:
                    zone_name = f"{wh_id}_{parts[2]}"
                else:
                    zone_name = bin_id

                if zone_name not in self.zone_coords:
                    self.zone_coords[zone_name] = zone_idx
                    zone_idx += 1

                self.bin_to_zone[bin_id] = self.zone_coords[zone_name]

        self.n_zones = len(self.zone_coords)

        # Simple grid layout for distance
        self.zone_positions = {}
        grid_size = max(1, int(math.ceil(math.sqrt(self.n_zones))))
        for i, zone_name in enumerate(self.zone_coords.keys()):
            self.zone_positions[zone_name] = (i % grid_size, i // grid_size)

    def _zone_distance(self, z1_name: str, z2_name: str) -> float:
        """Manhattan distance between zones."""
        p1 = self.zone_positions.get(z1_name, (0, 0))
        p2 = self.zone_positions.get(z2_name, (0, 0))
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    def reset(self):
        """Reset environment to initial state."""
        self.current_time = 0.0
        self.order_pool = []
        self.pending_orders = sorted(self.all_orders, key=lambda o: o['arrival_time'])
        self.waves = []

        self.active_wave_orders = []
        self.active_wave_volume = 0.0
        self.active_wave_weight = 0.0
        self.active_wave_start_time = 0.0
        self.active_wave_temps = set()
        self.active_wave_skus = set()

        self.total_picking_distance = 0.0
        self.total_setup_time = 0.0
        self.deadline_misses = 0
        self.temp_violations = 0
        self.priority_score_sum = 0

        self.done = False
        self.step_count = 0

        self._process_arrivals()
        return self.get_state()

    def _process_arrivals(self):
        """Move arrived orders from pending to pool."""
        newly_arrived = [o for o in self.pending_orders if o['arrival_time'] <= self.current_time]
        self.pending_orders = [o for o in self.pending_orders if o['arrival_time'] > self.current_time]
        self.order_pool.extend(newly_arrived)

    def _estimate_picking_distance(self, orders: List[Dict]) -> float:
        """Estimate picking tour length for orders."""
        if not orders:
            return 0.0

        # Collect unique SKUs and their zones
        all_skus = set()
        for o in orders:
            all_skus.update(o['skus'])

        # Simplified: each SKU goes to its dominant temp zone
        zones_visited = set()
        for sku in all_skus:
            temp = self.sku_to_temp.get(sku, 'ambient')
            # Find a bin of this temperature
            for wh_id, bins in self.warehouse_bins.items():
                for bin_id, bin_temp in bins:
                    if bin_temp == temp:
                        zones_visited.add(self.bin_to_zone.get(bin_id, 0))
                        break

        if not zones_visited:
            return 0.0

        # Nearest neighbor heuristic
        unvisited = set(zones_visited)
        current = 0  # entry point
        total_dist = 0.0

        zone_list = list(self.zone_positions.keys())

        while unvisited:
            nearest = min(unvisited, key=lambda z: self._zone_distance(
                zone_list[current] if current < len(zone_list) else zone_list[0],
                zone_list[z] if z < len(zone_list) else zone_list[0]
            ) if z < len(zone_list) and current < len(zone_list) else 0)

            total_dist += self._zone_distance(
                zone_list[current] if current < len(zone_list) else zone_list[0],
                zone_list[nearest] if nearest < len(zone_list) else zone_list[0]
            ) if current < len(zone_list) and nearest < len(zone_list) else 0

            current = nearest
            unvisited.remove(nearest)

        # Return to entry
        total_dist += self._zone_distance(
            zone_list[current] if current < len(zone_list) else zone_list[0],
            zone_list[0]
        ) if current < len(zone_list) else 0

        return total_dist

    def _close_wave(self) -> Tuple[float, Dict]:
        """Close active wave, compute rewards/penalties."""
        if not self.active_wave_orders:
            return 0.0, {}

        # Picking distance
        distance = self._estimate_picking_distance(self.active_wave_orders)
        picking_time = distance / self.picking_speed

        # Setup time
        self.total_setup_time += self.setup_time

        # Finish time
        finish_time = self.current_time + self.setup_time + picking_time

        # Deadline penalties
        deadline_penalty = 0.0
        for o in self.active_wave_orders:
            allowed_finish = o['arrival_time'] + o['deadline_hours'] * 60
            if finish_time > allowed_finish:
                hours_late = (finish_time - allowed_finish) / 60
                deadline_penalty += hours_late * self.alpha_deadline
                self.deadline_misses += 1

        # Temperature penalty
        temp_penalty = 0.0
        if len(self.active_wave_temps) > 1:
            temps = sorted(self.active_wave_temps)
            incompatible = False
            if (0 in temps or 1 in temps) and (2 in temps or 3 in temps):
                incompatible = True
            if 2 in temps and 3 in temps:
                incompatible = True
            if incompatible:
                temp_penalty = self.alpha_temp
                self.temp_violations += 1

        # Priority reward (higher priority orders should be processed earlier)
        priority_reward = 0.0
        for o in self.active_wave_orders:
            priority_reward += o['priority_score'] * self.alpha_priority * 0.1

        # 【新增】订单完成奖励：每完成一单 +alpha_completion
        completion_reward = self.alpha_completion * len(self.active_wave_orders)

        # Efficiency reward
        efficiency_reward = -self.alpha_eff * distance

        # Setup cost
        setup_cost = -self.alpha_setup

        total_reward = (efficiency_reward + temp_penalty + deadline_penalty +
                        setup_cost + priority_reward + completion_reward)

        wave_info = {
            'orders': len(self.active_wave_orders),
            'volume': self.active_wave_volume,
            'weight': self.active_wave_weight,
            'distance': distance,
            'finish_time': finish_time,
            'temps': list(self.active_wave_temps),
            'priority_sum': sum(o['priority_score'] for o in self.active_wave_orders),
        }

        self.total_picking_distance += distance
        self.waves.append(wave_info)

        # Reset active wave
        self.active_wave_orders = []
        self.active_wave_volume = 0.0
        self.active_wave_weight = 0.0
        self.active_wave_temps = set()
        self.active_wave_skus = set()
        self.active_wave_start_time = self.current_time

        return total_reward, wave_info

    def _get_candidates(self) -> List[Dict]:
        """Get top-K candidate orders from pool (by urgency)."""
        if not self.order_pool:
            return []

        def urgency(o: Dict):
            remaining = (o['arrival_time'] + o['deadline_hours'] * 60) - self.current_time
            priority_boost = o['priority_score'] * (-1000)  # Higher priority = more urgent
            return remaining + priority_boost

        sorted_pool = sorted(self.order_pool, key=urgency)
        return sorted_pool[:self.k_candidates]

    def get_state(self) -> Dict:
        """Return state representation as dictionary."""
        candidates = self._get_candidates()

        # Wave features
        wave_features = np.array([
            len(self.active_wave_orders) / self.max_wave_orders,
            self.active_wave_volume / self.max_wave_volume,
            self.active_wave_weight / self.max_wave_weight,
            (self.current_time - self.active_wave_start_time) / 120 if self.active_wave_orders else 0,
            len(self.active_wave_temps) / self.n_temps,
        ], dtype=np.float32)

        # Temp mask
        temp_mask = np.zeros(self.n_temps, dtype=np.float32)
        for t in self.active_wave_temps:
            temp_mask[t] = 1.0

        # Candidate features
        candidate_features = []
        for i in range(self.k_candidates):
            if i < len(candidates):
                o = candidates[i]
                remaining_time = ((o['arrival_time'] + o['deadline_hours'] * 60) - self.current_time) / 60
                feat = [
                    o['n_skus'] / 15.0,
                    o['total_volume'] / 10.0,
                    o['total_weight'] / 5.0,
                    remaining_time / 72.0,
                    o['dominant_temp_idx'] / 3.0,
                    o['priority_score'] / 2.0,
                    1.0 if o['has_special_handling'] else 0.0,
                ]
            else:
                feat = [0.0] * 7
            candidate_features.extend(feat)
        candidate_features = np.array(candidate_features, dtype=np.float32)

        # Global stats
        urgent_count = sum(1 for o in self.order_pool
                          if (o['arrival_time'] + o['deadline_hours'] * 60) - self.current_time < 120)
        global_stats = np.array([
            urgent_count / max(len(self.order_pool), 1),
            len(self.pending_orders) / max(len(self.all_orders), 1),
            len(self.order_pool) / 100.0,
            len(self.waves) / 100.0,
        ], dtype=np.float32)

        state_dict = {
            'wave': wave_features,
            'temp_mask': temp_mask,
            'candidates': candidate_features,
            'global': global_stats,
            'n_candidates': len(candidates),
            'can_close': len(self.active_wave_orders) >= 1
        }

        return state_dict

    def get_state_vector(self, state_dict: Dict) -> np.ndarray:
        """Flatten state dict to vector."""
        parts = [
            state_dict['wave'],
            state_dict['temp_mask'],
            state_dict['candidates'],
            state_dict['global']
        ]
        return np.concatenate(parts)

    @property
    def state_dim(self) -> int:
        return 5 + self.n_temps + 7 * self.k_candidates + 4

    @property
    def action_dim(self) -> int:
        return self.k_candidates + 1  # K candidates + CLOSE

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict]:
        """
        Action: 0..k_candidates-1 = add candidate order to wave
                k_candidates = close wave
        """
        self.step_count += 1
        candidates = self._get_candidates()
        reward = 0.0
        info = {'action_type': 'none'}

        if action < len(candidates) and action >= 0:
            order = candidates[action]

            if len(self.active_wave_orders) < self.max_wave_orders and \
               self.active_wave_volume + order['total_volume'] <= self.max_wave_volume and \
               self.active_wave_weight + order['total_weight'] <= self.max_wave_weight:

                self.active_wave_orders.append(order)
                self.active_wave_volume += order['total_volume']
                self.active_wave_weight += order['total_weight']
                self.active_wave_temps.add(order['dominant_temp_idx'])
                self.active_wave_skus.update(order['skus'])
                self.order_pool.remove(order)

                reward = +0.5  # 【优化】正奖励鼓励 accumulate
                info['action_type'] = 'add'
            else:
                reward = -10.0
                info['action_type'] = 'invalid_capacity'

        elif action == len(candidates) or action == self.k_candidates:
            wave_reward, wave_info = self._close_wave()
            reward = wave_reward
            info = wave_info
            info['action_type'] = 'close'

        else:
            reward = -5.0
            info['action_type'] = 'invalid'

        self.current_time += self.time_step
        self._process_arrivals()

        if len(self.order_pool) == 0 and len(self.pending_orders) == 0:
            if self.active_wave_orders:
                wave_reward, wave_info = self._close_wave()
                reward += wave_reward
            self.done = True

        if self.step_count > self.max_steps:
            if self.active_wave_orders:
                wave_reward, wave_info = self._close_wave()
                reward += wave_reward
            # 【新增】对未处理订单施加重罚
            unprocessed = len(self.order_pool) + len(self.pending_orders)
            if unprocessed > 0:
                reward -= self.alpha_unprocessed_penalty * unprocessed
            self.done = True

        state_dict = self.get_state()
        state_vec = self.get_state_vector(state_dict)

        return state_vec, reward, self.done, info

    def get_valid_actions(self, state_dict: Dict) -> List[int]:
        """Return list of valid action indices."""
        valid = []
        candidates = self._get_candidates()
        n_candidates = len(candidates)
        wave_order_full = len(self.active_wave_orders) >= self.max_wave_orders

        if not wave_order_full:
            for i in range(min(n_candidates, self.k_candidates)):
                o = candidates[i]
                if self.active_wave_volume + o['total_volume'] <= self.max_wave_volume and \
                   self.active_wave_weight + o['total_weight'] <= self.max_wave_weight:
                    valid.append(i)

        can_close = len(self.active_wave_orders) >= 1
        if can_close or n_candidates == 0 or wave_order_full or len(valid) == 0:
            valid.append(self.k_candidates)

        return valid if valid else [self.k_candidates]


# =============================================================================
# 3. HEURISTICS
# =============================================================================

def run_heuristic(env: SDVPharmaWaveEnv, heuristic_name: str) -> Dict:
    """Run a rule-based heuristic on the environment."""
    state_dict = env.reset()
    total_reward = 0.0

    while not env.done:
        candidates = env._get_candidates()
        valid_actions = env.get_valid_actions(state_dict)

        if not candidates or len(valid_actions) == 0:
            action = env.k_candidates
        else:
            if heuristic_name == 'FCFS':
                action = 0 if 0 in valid_actions else env.k_candidates

            elif heuristic_name == 'TEMP_FIRST':
                best_action = env.k_candidates
                if env.active_wave_temps:
                    for i, o in enumerate(candidates):
                        if i in valid_actions and o['dominant_temp_idx'] in env.active_wave_temps:
                            best_action = i
                            break
                else:
                    if 0 in valid_actions:
                        best_action = 0
                action = best_action

            elif heuristic_name == 'PRIORITY_FIRST':
                best_action = env.k_candidates
                max_priority = -1
                for i, o in enumerate(candidates):
                    if i in valid_actions and o['priority_score'] > max_priority:
                        max_priority = o['priority_score']
                        best_action = i
                action = best_action

            elif heuristic_name == 'EDD':
                best_action = env.k_candidates
                min_remaining = float('inf')
                for i, o in enumerate(candidates):
                    if i in valid_actions:
                        remaining = (o['arrival_time'] + o['deadline_hours'] * 60) - env.current_time
                        if remaining < min_remaining:
                            min_remaining = remaining
                            best_action = i
                action = best_action

            elif heuristic_name == 'TZU':
                best_score = -float('inf')
                best_action = env.k_candidates

                for i, o in enumerate(candidates):
                    if i not in valid_actions:
                        continue

                    temp_match = 1.0 if o['dominant_temp_idx'] in env.active_wave_temps or not env.active_wave_temps else 0.0

                    remaining = (o['arrival_time'] + o['deadline_hours'] * 60) - env.current_time
                    urgency = 1.0 / (1.0 + max(0, remaining / 60))

                    priority_bonus = o['priority_score'] / 2.0

                    score = 0.35 * temp_match + 0.35 * urgency + 0.3 * priority_bonus
                    if score > best_score:
                        best_score = score
                        best_action = i

                action = best_action
            else:
                action = random.choice(valid_actions)

        state_vec, reward, done, info = env.step(action)
        state_dict = env.get_state()
        total_reward += reward

    return {
        'total_reward': total_reward,
        'n_waves': len(env.waves),
        'total_distance': env.total_picking_distance,
        'deadline_misses': env.deadline_misses,
        'temp_violations': env.temp_violations,
        'waves': env.waves
    }


# =============================================================================
# 4. PPO (same architecture as before, adapted dimensions)
# =============================================================================

if TORCH_AVAILABLE:
    class PolicyNet(nn.Module):
        def __init__(self, state_dim, hidden_dim, action_dim):
            super(PolicyNet, self).__init__()
            self.fc1 = nn.Linear(state_dim, hidden_dim)
            self.fc2 = nn.Linear(hidden_dim, hidden_dim * 2)
            self.fc3 = nn.Linear(hidden_dim * 2, hidden_dim)
            self.fc4 = nn.Linear(hidden_dim, action_dim)

        def forward(self, x):
            x = F.relu(self.fc1(x))
            x = F.relu(self.fc2(x))
            x = F.relu(self.fc3(x))
            return F.relu(self.fc4(x))

    class ValueNet(nn.Module):
        def __init__(self, state_dim, hidden_dim):
            super(ValueNet, self).__init__()
            self.fc1 = nn.Linear(state_dim, hidden_dim)
            self.fc2 = nn.Linear(hidden_dim, hidden_dim * 2)
            self.fc3 = nn.Linear(hidden_dim * 2, hidden_dim)
            self.fc4 = nn.Linear(hidden_dim, 1)

        def forward(self, x):
            x = F.relu(self.fc1(x))
            x = F.relu(self.fc2(x))
            x = F.relu(self.fc3(x))
            return self.fc4(x)

    class PPOAgent:
        def __init__(self, state_dim, action_dim, hidden_dim=None,
                     actor_lr=5e-4, critic_lr=1e-5, gamma=0.96, lmbda=0.95,
                     epochs=10, eps=0.2, device='cpu'):
            self.device = torch.device(device)
            self.state_dim = state_dim
            self.action_dim = action_dim
            hidden_dim = state_dim * 3 if hidden_dim is None else hidden_dim

            self.actor = PolicyNet(state_dim, hidden_dim, action_dim).to(self.device)
            self.critic = ValueNet(state_dim, hidden_dim).to(self.device)

            self.actor_optimizer = torch.optim.Adam(self.actor.parameters(), lr=actor_lr)
            self.critic_optimizer = torch.optim.Adam(self.critic.parameters(), lr=critic_lr)

            self.gamma = gamma
            self.lmbda = lmbda
            self.epochs = epochs
            self.eps = eps

            self.actor_losses = []
            self.critic_losses = []

        def select_action(self, state, valid_actions, deterministic=False):
            state_tensor = torch.tensor(state, dtype=torch.float).unsqueeze(0).to(self.device)

            with torch.no_grad():
                probs_raw = self.actor(state_tensor).squeeze(0)

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
            advantages = []
            gae = 0.0

            for t in reversed(range(len(rewards))):
                delta = rewards[t] + self.gamma * next_values[t] * (1 - dones[t]) - values[t]
                gae = delta + self.gamma * self.lmbda * gae * (1 - dones[t])
                advantages.insert(0, gae)

            return np.array(advantages)

        def update(self, trajectory):
            states = np.array([t['state'] for t in trajectory])
            actions = np.array([t['action'] for t in trajectory])
            old_log_probs = np.array([t['log_prob'] for t in trajectory])
            rewards = np.array([t['reward'] for t in trajectory])
            next_states = np.array([t['next_state'] for t in trajectory])
            dones = np.array([t['done'] for t in trajectory])
            valid_masks = [t['valid_actions'] for t in trajectory]

            with torch.no_grad():
                states_t = torch.tensor(states, dtype=torch.float).to(self.device)
                next_states_t = torch.tensor(next_states, dtype=torch.float).to(self.device)
                values = self.critic(states_t).squeeze().cpu().numpy()
                next_values = self.critic(next_states_t).squeeze().cpu().numpy()

            advantages = self.compute_advantages(rewards, values, next_values, dones)
            advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
            td_target = advantages + values

            states_t = torch.tensor(states, dtype=torch.float).to(self.device)
            actions_t = torch.tensor(actions, dtype=torch.long).view(-1, 1).to(self.device)
            old_log_probs_t = torch.tensor(old_log_probs, dtype=torch.float).view(-1, 1).to(self.device)
            advantages_t = torch.tensor(advantages, dtype=torch.float).view(-1, 1).to(self.device)
            td_target_t = torch.tensor(td_target, dtype=torch.float).view(-1, 1).to(self.device)

            for _ in range(self.epochs):
                probs_raw = self.actor(states_t)

                batch_size = probs_raw.shape[0]
                probs = torch.zeros_like(probs_raw)
                for i in range(batch_size):
                    mask = torch.zeros(self.action_dim, device=self.device)
                    mask[valid_masks[i]] = 1.0
                    masked = probs_raw[i] * mask
                    if masked.sum() < 1e-8:
                        probs[i] = mask / mask.sum()
                    else:
                        probs[i] = masked / masked.sum()

                log_probs = torch.log(probs.gather(1, actions_t) + 1e-8)
                ratio = torch.exp(log_probs - old_log_probs_t)

                surr1 = ratio * advantages_t
                surr2 = torch.clamp(ratio, 1 - self.eps, 1 + self.eps) * advantages_t
                actor_loss = -torch.min(surr1, surr2).mean()

                critic_loss = F.mse_loss(self.critic(states_t), td_target_t)

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


# =============================================================================
# 5. TRAINING AND EVALUATION
# =============================================================================

def train_ppo(env_factory, n_episodes=100, update_interval=10):
    """Train PPO agent."""
    if not TORCH_AVAILABLE:
        print("PyTorch not available. Skipping PPO training.")
        return None, []

    env = env_factory()
    state_dim = env.state_dim
    action_dim = env.action_dim

    agent = PPOAgent(state_dim, action_dim, hidden_dim=128)

    episode_rewards = []
    episode_metrics = []

    for episode in range(n_episodes):
        env = env_factory()
        state_dict = env.reset()
        state = env.get_state_vector(state_dict)

        trajectory = []
        episode_reward = 0.0

        while not env.done:
            valid_actions = env.get_valid_actions(state_dict)
            action, log_prob, probs = agent.select_action(state, valid_actions)

            next_state_vec, reward, done, info = env.step(action)
            next_state_dict = env.get_state()

            trajectory.append({
                'state': state,
                'action': action,
                'log_prob': log_prob,
                'reward': reward,
                'next_state': next_state_vec,
                'done': float(done),
                'valid_actions': valid_actions
            })

            episode_reward += reward
            state = next_state_vec
            state_dict = next_state_dict

        episode_rewards.append(episode_reward)
        episode_metrics.append({
            'reward': episode_reward,
            'n_waves': len(env.waves),
            'distance': env.total_picking_distance,
            'misses': env.deadline_misses,
            'violations': env.temp_violations
        })

        if len(trajectory) > 0 and (episode + 1) % update_interval == 0:
            agent.update(trajectory)

    return agent, episode_metrics


def evaluate_agent(agent, env_factory, n_eval=10, use_ppo=True):
    """Evaluate agent on hold-out instances."""
    results = []

    for i in range(n_eval):
        env = env_factory()
        state_dict = env.reset()
        total_reward = 0.0
        step_log = []

        while not env.done:
            valid_actions = env.get_valid_actions(state_dict)

            if use_ppo and TORCH_AVAILABLE:
                state = env.get_state_vector(state_dict)
                action, _, _ = agent.select_action(state, valid_actions, deterministic=True)
            else:
                action = random.choice(valid_actions)

            state_vec, reward, done, info = env.step(action)
            state_dict = env.get_state()
            total_reward += reward

            step_log.append({
                'time': float(env.current_time),
                'action': int(action),
                'action_type': info.get('action_type', 'unknown'),
                'reward': float(reward),
                'wave_orders': len(env.active_wave_orders),
            })

        results.append({
            'total_reward': float(total_reward),
            'n_waves': int(len(env.waves)),
            'total_distance': float(env.total_picking_distance),
            'deadline_misses': int(env.deadline_misses),
            'temp_violations': int(env.temp_violations),
            'step_log': step_log[:100],
            'waves': [{
                'orders': w['orders'],
                'distance': float(w['distance']),
                'temps': w['temps'],
            } for w in env.waves]
        })

    return results


def compare_heuristics(env_factory, n_instances=10):
    """Compare all heuristics on same instances."""
    heuristics = ['FCFS', 'TEMP_FIRST', 'PRIORITY_FIRST', 'EDD', 'TZU']
    all_results = {h: [] for h in heuristics}

    for i in range(n_instances):
        for h in heuristics:
            env = env_factory()
            result = run_heuristic(env, h)
            result['instance'] = i
            all_results[h].append(result)

    summary = {}
    for h in heuristics:
        rewards = [r['total_reward'] for r in all_results[h]]
        distances = [r['total_distance'] for r in all_results[h]]
        waves = [r['n_waves'] for r in all_results[h]]
        misses = [r['deadline_misses'] for r in all_results[h]]
        violations = [r['temp_violations'] for r in all_results[h]]

        summary[h] = {
            'avg_reward': float(np.mean(rewards)),
            'std_reward': float(np.std(rewards)),
            'avg_distance': float(np.mean(distances)),
            'avg_waves': float(np.mean(waves)),
            'avg_misses': float(np.mean(misses)),
            'avg_violations': float(np.mean(violations))
        }

    return summary, all_results


if __name__ == '__main__':
    print("=" * 60)
    print("Smart Wave Allocation - SDV Realistic Data")
    print("Deep Reinforcement Learning Prototype")
    print("=" * 60)

    # Load data
    print("\n[1] Loading SDV simulation data...")
    loader = SDVDataLoader()

    # Use WH_001 as example
    warehouse_id = "WH_001"
    orders = loader.get_orders_for_warehouse(warehouse_id)
    print(f"    Warehouse {warehouse_id}: {len(orders)} orders")

    # Build warehouse bins
    wh_data = loader.warehouses[loader.warehouses['warehouse_id'] == warehouse_id].iloc[0]
    bins = []
    for zone, count in [
        ("ambient", wh_data["ambient_zone_bins"]),
        ("cool", wh_data["cool_zone_bins"]),
        ("cold", wh_data["cold_zone_bins"]),
        ("frozen", wh_data["frozen_zone_bins"]),
        ("controlled", wh_data["controlled_zone_bins"]),
    ]:
        count = min(int(count), 50)  # Limit for performance
        for b in range(count):
            bins.append((f"{warehouse_id}_{zone.upper()}_{b+1:03d}", zone))

    sku_to_temp = loader.sku_to_temp
    warehouse_bins = {warehouse_id: bins}
    env = SDVPharmaWaveEnv(orders, warehouse_bins, sku_to_temp)
    print(f"    State dim: {env.state_dim}, Action dim: {env.action_dim}")

    # Heuristic comparison
    print("\n[2] Running heuristic baselines...")
    summary, _ = compare_heuristics(lambda: SDVPharmaWaveEnv(orders, warehouse_bins, sku_to_temp), n_instances=5)

    print(f"{'Heuristic':<18} {'Avg Reward':<12} {'Avg Dist':<12} {'Avg Waves':<12} {'Misses':<10} {'Viol.':<8}")
    print("-" * 72)
    for h, s in summary.items():
        print(f"{h:<18} {s['avg_reward']:<12.1f} {s['avg_distance']:<12.1f} "
              f"{s['avg_waves']:<12.1f} {s['avg_misses']:<10.1f} {s['avg_violations']:<8.1f}")

    # Train PPO
    if TORCH_AVAILABLE:
        print("\n[3] Training PPO agent...")
        agent, metrics = train_ppo(lambda: SDVPharmaWaveEnv(orders, warehouse_bins, sku_to_temp), n_episodes=80, update_interval=8)

        print("\n[4] Evaluating PPO...")
        ppo_results = evaluate_agent(agent, lambda: SDVPharmaWaveEnv(orders, warehouse_bins, sku_to_temp), n_eval=5, use_ppo=True)

        ppo_reward = np.mean([r['total_reward'] for r in ppo_results])
        ppo_dist = np.mean([r['total_distance'] for r in ppo_results])
        ppo_misses = np.mean([r['deadline_misses'] for r in ppo_results])
        ppo_viol = np.mean([r['temp_violations'] for r in ppo_results])

        print(f"\nPPO Results: reward={ppo_reward:.1f}, dist={ppo_dist:.1f}, misses={ppo_misses:.1f}, viol={ppo_viol:.1f}")

    print("\nDone!")
