"""
Smart Wave Allocation for Pharmaceutical Distribution
Deep Reinforcement Learning Implementation (PPO)
Based on KGDRL research paradigm, without knowledge guidance module
"""

import numpy as np
import random
import math
import collections
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass, field
import matplotlib.pyplot as plt
from tqdm import tqdm
import pandas as pd

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
# 1. DATA GENERATION - EMPIRICAL DISTRIBUTIONS
# =============================================================================

@dataclass
class SKU:
    """Individual stock keeping unit"""
    sku_id: int
    zone: int
    temp_category: int  # 0=ambient, 1=cool, 2=cold, 3=frozen

@dataclass
class Order:
    """Customer order"""
    order_id: int
    arrival_time: float
    skus: List[SKU]
    deadline: float  # hours from arrival
    volume: float
    is_urgent: bool

    @property
    def n_items(self):
        return len(self.skus)

    @property
    def dominant_temp(self):
        """Most frequent temperature category in order"""
        temps = [sku.temp_category for sku in self.skus]
        return max(set(temps), key=temps.count)

    @property
    def required_zones(self):
        return list(set(sku.zone for sku in self.skus))

    @property
    def zone_centroid(self):
        """Centroid of required zones (simplified to mean of zone coords)"""
        zones = self.required_zones
        # Zone coordinates: 2x4 grid
        coords = [(z % 4, z // 4) for z in zones]
        return (np.mean([c[0] for c in coords]), np.mean([c[1] for c in coords]))


class DataGenerator:
    """
    Generates synthetic order data based on empirical distributions
    from the pharmaceutical distribution casebook.
    """

    def __init__(self, seed: int = 42, base_rate: float = 3.0):
        """
        Args:
            seed: random seed
            base_rate: average orders per minute (default 3.0 for prototype scale)
                       For enterprise scale (~90K/day), use ~187.5
        """
        self.rng = np.random.RandomState(seed)
        random.seed(seed)

        # Warehouse parameters
        self.n_zones = 8
        self.zone_coords = {z: (z % 4, z // 4) for z in range(self.n_zones)}

        # Temperature distribution
        self.temp_probs = [0.55, 0.25, 0.15, 0.05]
        self.temp_names = ['ambient', 'cool', 'cold', 'frozen']

        # Order size distribution
        self.order_sizes = [3, 4, 5]
        self.order_size_probs = [0.40, 0.35, 0.25]

        # Arrival process
        self.base_rate = base_rate  # orders per minute
        self.peak_prob = 0.05
        self.peak_multiplier = 2.8

        # Deadline distribution
        self.urgent_prob = 0.20

    def _is_peak_period(self, t: float) -> bool:
        """Check if time t is in peak period (bimodal: 9AM=60min, 2PM=300min)"""
        # t is minutes from shift start (8-hour shift = 480 min)
        peak1 = abs(t - 60) < 30   # 9AM peak
        peak2 = abs(t - 300) < 30  # 2PM peak
        return peak1 or peak2

    def generate_orders(self, horizon_hours: float = 8.0) -> List[Order]:
        """Generate a full day of orders"""
        horizon_min = horizon_hours * 60
        orders = []
        order_id = 0
        t = 0.0

        while t < horizon_min:
            # Determine arrival rate
            rate = self.base_rate
            if self._is_peak_period(t):
                rate *= 1.5
            if self.rng.rand() < self.peak_prob:
                rate *= self.peak_multiplier

            # Sample inter-arrival time (exponential)
            dt = self.rng.exponential(1.0 / rate)
            t += dt
            if t >= horizon_min:
                break

            # Generate order
            order = self._generate_single_order(order_id, t)
            orders.append(order)
            order_id += 1

        return orders

    def _generate_single_order(self, order_id: int, arrival_time: float) -> Order:
        """Generate a single order"""
        n_items = self.rng.choice(self.order_sizes, p=self.order_size_probs)

        # Generate SKUs
        skus = []
        for i in range(n_items):
            zone = self.rng.randint(0, self.n_zones)
            temp = self.rng.choice(4, p=self.temp_probs)
            skus.append(SKU(sku_id=order_id*100+i, zone=zone, temp_category=temp))

        # Deadline
        is_urgent = self.rng.rand() < self.urgent_prob
        if is_urgent:
            deadline = self.rng.uniform(2, 6)
        else:
            deadline = self.rng.uniform(8, 24)

        # Volume
        volume = n_items * self.rng.uniform(5, 20)

        return Order(
            order_id=order_id,
            arrival_time=arrival_time,
            skus=skus,
            deadline=deadline,
            volume=volume,
            is_urgent=is_urgent
        )

    def zone_distance(self, z1: int, z2: int) -> float:
        """Manhattan distance between zones"""
        c1 = self.zone_coords[z1]
        c2 = self.zone_coords[z2]
        return abs(c1[0] - c2[0]) + abs(c1[1] - c2[1])


# =============================================================================
# 2. ENVIRONMENT DEFINITION
# =============================================================================

class PharmaWaveEnv:
    """
    Smart Wave Allocation Environment

    State: Current wave status + order pool + temporal info
    Action: Select order to add to wave, or close wave
    Reward: Picking efficiency + compliance + timeliness
    """

    def __init__(self,
                 orders: List[Order],
                 max_wave_orders: int = 30,
                 max_wave_volume: float = 500,
                 picking_speed: float = 60.0,  # meters/min
                 setup_time: float = 10.0,      # minutes per wave
                 time_step: float = 1.0,
                 alpha_eff: float = 1.0,
                 alpha_temp: float = 100.0,
                 alpha_deadline: float = 50.0,
                 alpha_setup: float = 15.0,
                 k_candidates: int = 10):

        self.all_orders = orders
        self.max_wave_orders = max_wave_orders
        self.max_wave_volume = max_wave_volume
        self.picking_speed = picking_speed
        self.setup_time = setup_time
        self.time_step = time_step

        # Reward coefficients
        self.alpha_eff = alpha_eff
        self.alpha_temp = alpha_temp
        self.alpha_deadline = alpha_deadline
        self.alpha_setup = alpha_setup

        self.k_candidates = k_candidates
        self.n_zones = 8
        self.n_temps = 4

        # Internal state
        self.current_time = 0.0
        self.order_pool: List[Order] = []
        self.pending_orders: List[Order] = []  # Not yet arrived
        self.waves: List[Dict] = []  # Completed waves

        # Active wave
        self.active_wave_orders: List[Order] = []
        self.active_wave_volume = 0.0
        self.active_wave_start_time = 0.0
        self.active_wave_zones: set = set()
        self.active_wave_temps: set = set()

        # Tracking
        self.total_picking_distance = 0.0
        self.total_setup_time = 0.0
        self.deadline_misses = 0
        self.temp_violations = 0

        self.done = False
        self.step_count = 0

    def reset(self):
        """Reset environment to initial state"""
        self.current_time = 0.0
        self.order_pool = []
        self.pending_orders = sorted(self.all_orders, key=lambda o: o.arrival_time)
        self.waves = []

        self.active_wave_orders = []
        self.active_wave_volume = 0.0
        self.active_wave_start_time = 0.0
        self.active_wave_zones = set()
        self.active_wave_temps = set()

        self.total_picking_distance = 0.0
        self.total_setup_time = 0.0
        self.deadline_misses = 0
        self.temp_violations = 0

        self.done = False
        self.step_count = 0

        # Initial order arrivals
        self._process_arrivals()

        return self.get_state()

    def _process_arrivals(self):
        """Move arrived orders from pending to pool"""
        newly_arrived = [o for o in self.pending_orders if o.arrival_time <= self.current_time]
        self.pending_orders = [o for o in self.pending_orders if o.arrival_time > self.current_time]
        self.order_pool.extend(newly_arrived)

    def _estimate_picking_distance(self, orders: List[Order]) -> float:
        """Estimate TSP tour length for picking orders (simplified)"""
        if not orders:
            return 0.0

        zones = list(set(z for o in orders for z in o.required_zones))
        if not zones:
            return 0.0

        # Simplified: entry -> nearest neighbor tour -> exit
        entry = (0, 0)
        coords = [self._get_zone_coord(z) for z in zones]

        # Nearest neighbor heuristic
        unvisited = set(range(len(coords)))
        current = entry
        total_dist = 0.0

        while unvisited:
            nearest = min(unvisited, key=lambda i: self._euclid(current, coords[i]))
            total_dist += self._euclid(current, coords[nearest])
            current = coords[nearest]
            unvisited.remove(nearest)

        # Return to entry
        total_dist += self._euclid(current, entry)

        return total_dist

    def _get_zone_coord(self, z: int) -> Tuple[float, float]:
        return (z % 4, z // 4)

    def _euclid(self, a, b):
        return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

    def _close_wave(self) -> Tuple[float, Dict]:
        """Close active wave, compute rewards/penalties"""
        if not self.active_wave_orders:
            return 0.0, {}

        # Picking distance
        distance = self._estimate_picking_distance(self.active_wave_orders)
        picking_time = distance / self.picking_speed

        # Setup time
        self.total_setup_time += self.setup_time

        # Finish time (simplified: current_time + setup + picking)
        finish_time = self.current_time + self.setup_time + picking_time

        # Deadline penalties
        deadline_penalty = 0.0
        for o in self.active_wave_orders:
            allowed_finish = o.arrival_time + o.deadline * 60  # deadline in minutes
            if finish_time > allowed_finish:
                hours_late = (finish_time - allowed_finish) / 60
                deadline_penalty += hours_late * self.alpha_deadline
                self.deadline_misses += 1

        # Temperature penalty
        temp_penalty = 0.0
        if len(self.active_wave_temps) > 1:
            # Check if temps are compatible
            temps = sorted(self.active_wave_temps)
            # ambient(0) can mix with cool(1); cold(2) and frozen(3) must be separate
            incompatible = False
            if (0 in temps or 1 in temps) and (2 in temps or 3 in temps):
                incompatible = True
            if 2 in temps and 3 in temps:
                incompatible = True
            if incompatible:
                temp_penalty = self.alpha_temp
                self.temp_violations += 1

        # Efficiency reward (negative distance)
        efficiency_reward = -self.alpha_eff * distance

        # Setup cost
        setup_cost = -self.alpha_setup

        total_reward = efficiency_reward + temp_penalty + deadline_penalty + setup_cost

        wave_info = {
            'orders': len(self.active_wave_orders),
            'volume': self.active_wave_volume,
            'distance': distance,
            'finish_time': finish_time,
            'temps': list(self.active_wave_temps),
            'zones': list(self.active_wave_zones)
        }

        # Update total tracking
        self.total_picking_distance += distance
        self.waves.append(wave_info)

        # Reset active wave
        self.active_wave_orders = []
        self.active_wave_volume = 0.0
        self.active_wave_zones = set()
        self.active_wave_temps = set()
        self.active_wave_start_time = self.current_time

        return total_reward, wave_info

    def _get_candidates(self) -> List[Order]:
        """Get top-K candidate orders from pool (by urgency)"""
        if not self.order_pool:
            return []

        # Sort by urgency (remaining time until deadline)
        def urgency(o: Order):
            remaining = (o.arrival_time + o.deadline * 60) - self.current_time
            return remaining

        sorted_pool = sorted(self.order_pool, key=urgency)
        return sorted_pool[:self.k_candidates]

    def get_state(self) -> Dict:
        """Return state representation as dictionary"""
        candidates = self._get_candidates()

        # Wave features
        wave_features = np.array([
            len(self.active_wave_orders) / self.max_wave_orders,
            self.active_wave_volume / self.max_wave_volume,
            (self.current_time - self.active_wave_start_time) / 120 if self.active_wave_orders else 0,  # normalized age
            len(self.active_wave_zones) / self.n_zones
        ], dtype=np.float32)

        # Zone mask
        zone_mask = np.zeros(self.n_zones, dtype=np.float32)
        for z in self.active_wave_zones:
            zone_mask[z] = 1.0

        # Temp mask
        temp_mask = np.zeros(self.n_temps, dtype=np.float32)
        for t in self.active_wave_temps:
            temp_mask[t] = 1.0

        # Candidate features
        candidate_features = []
        for i in range(self.k_candidates):
            if i < len(candidates):
                o = candidates[i]
                remaining_time = ((o.arrival_time + o.deadline * 60) - self.current_time) / 60  # hours
                cx, cy = o.zone_centroid
                feat = [
                    o.n_items / 5.0,
                    remaining_time / 24.0,
                    o.dominant_temp / 3.0,
                    cx / 3.0,
                    cy / 1.0,
                    1.0 if o.is_urgent else 0.0
                ]
            else:
                feat = [0.0] * 6
            candidate_features.extend(feat)
        candidate_features = np.array(candidate_features, dtype=np.float32)

        # Global stats
        urgent_count = sum(1 for o in self.order_pool
                          if (o.arrival_time + o.deadline * 60) - self.current_time < 120)
        global_stats = np.array([
            urgent_count / max(len(self.order_pool), 1),
            len(self.pending_orders) / max(len(self.all_orders), 1),
            len(self.order_pool) / 50.0  # normalized pool size
        ], dtype=np.float32)

        state_dict = {
            'wave': wave_features,
            'zone_mask': zone_mask,
            'temp_mask': temp_mask,
            'candidates': candidate_features,
            'global': global_stats,
            'n_candidates': len(candidates),
            'can_close': len(self.active_wave_orders) >= 1
        }

        return state_dict

    def get_state_vector(self, state_dict: Dict) -> np.ndarray:
        """Flatten state dict to vector"""
        parts = [
            state_dict['wave'],
            state_dict['zone_mask'],
            state_dict['temp_mask'],
            state_dict['candidates'],
            state_dict['global']
        ]
        return np.concatenate(parts)

    @property
    def state_dim(self) -> int:
        return 4 + self.n_zones + self.n_temps + 6 * self.k_candidates + 3

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
            # Add order to wave
            order = candidates[action]

            # Check capacity
            if len(self.active_wave_orders) < self.max_wave_orders and \
               self.active_wave_volume + order.volume <= self.max_wave_volume:

                self.active_wave_orders.append(order)
                self.active_wave_volume += order.volume
                self.active_wave_zones.update(order.required_zones)
                self.active_wave_temps.add(order.dominant_temp)
                self.order_pool.remove(order)

                # Small negative reward for adding (encourages closing when full)
                reward = -0.1
                info['action_type'] = 'add'
            else:
                # Invalid: capacity exceeded
                reward = -10.0
                info['action_type'] = 'invalid_capacity'

        elif action == len(candidates) or action == self.k_candidates:
            # Close wave
            wave_reward, wave_info = self._close_wave()
            reward = wave_reward
            info = wave_info
            info['action_type'] = 'close'

        else:
            # Invalid action
            reward = -5.0
            info['action_type'] = 'invalid'

        # Advance time slightly
        self.current_time += self.time_step
        self._process_arrivals()

        # Check if done
        if len(self.order_pool) == 0 and len(self.pending_orders) == 0:
            # Close any remaining wave
            if self.active_wave_orders:
                wave_reward, wave_info = self._close_wave()
                reward += wave_reward
            self.done = True

        # Also limit episode length
        if self.step_count > 2000:
            if self.active_wave_orders:
                wave_reward, wave_info = self._close_wave()
                reward += wave_reward
            self.done = True

        state_dict = self.get_state()
        state_vec = self.get_state_vector(state_dict)

        return state_vec, reward, self.done, info

    def get_valid_actions(self, state_dict: Dict) -> List[int]:
        """Return list of valid action indices"""
        valid = []
        candidates = self._get_candidates()
        n_candidates = len(candidates)
        wave_order_full = len(self.active_wave_orders) >= self.max_wave_orders

        # Check each candidate individually for volume capacity
        if not wave_order_full:
            for i in range(min(n_candidates, self.k_candidates)):
                if self.active_wave_volume + candidates[i].volume <= self.max_wave_volume:
                    valid.append(i)

        # Closing wave (valid if wave has orders, pool empty, or capacity reached)
        can_close = len(self.active_wave_orders) >= 1
        if can_close or n_candidates == 0 or wave_order_full or len(valid) == 0:
            valid.append(self.k_candidates)

        return valid if valid else [self.k_candidates]


# =============================================================================
# 3. RULE-BASED HEURISTICS
# =============================================================================

def run_heuristic(env: PharmaWaveEnv, heuristic_name: str, generator: DataGenerator) -> Dict:
    """Run a rule-based heuristic on the environment"""
    state_dict = env.reset()
    total_reward = 0.0

    while not env.done:
        candidates = env._get_candidates()
        valid_actions = env.get_valid_actions(state_dict)

        if not candidates or len(valid_actions) == 0:
            action = env.k_candidates  # close
        else:
            if heuristic_name == 'FCFS':
                # First come first serve: add first candidate if possible
                if 0 in valid_actions:
                    action = 0
                else:
                    action = env.k_candidates

            elif heuristic_name == 'TEMP_FIRST':
                # Find candidate matching active wave temperature
                best_action = env.k_candidates
                if env.active_wave_temps:
                    for i, o in enumerate(candidates):
                        if i in valid_actions and o.dominant_temp in env.active_wave_temps:
                            best_action = i
                            break
                else:
                    if 0 in valid_actions:
                        best_action = 0
                action = best_action

            elif heuristic_name == 'ZONE_NN':
                # Add order with zone closest to current wave centroid
                if env.active_wave_zones:
                    # Current wave centroid
                    wcx = np.mean([generator.zone_coords[z][0] for z in env.active_wave_zones])
                    wcy = np.mean([generator.zone_coords[z][1] for z in env.active_wave_zones])

                    best_dist = float('inf')
                    best_action = env.k_candidates
                    for i, o in enumerate(candidates):
                        if i in valid_actions:
                            ox, oy = o.zone_centroid
                            dist = abs(ox - wcx) + abs(oy - wcy)
                            if dist < best_dist:
                                best_dist = dist
                                best_action = i
                    action = best_action
                else:
                    action = 0 if 0 in valid_actions else env.k_candidates

            elif heuristic_name == 'EDD':
                # Earliest due date: most urgent first
                best_action = env.k_candidates
                min_remaining = float('inf')
                for i, o in enumerate(candidates):
                    if i in valid_actions:
                        remaining = (o.arrival_time + o.deadline * 60) - env.current_time
                        if remaining < min_remaining:
                            min_remaining = remaining
                            best_action = i
                action = best_action

            elif heuristic_name == 'TZU':
                # Temperature-Zone-Urgency composite score
                best_score = -float('inf')
                best_action = env.k_candidates

                for i, o in enumerate(candidates):
                    if i not in valid_actions:
                        continue

                    # Temperature match
                    temp_match = 1.0 if o.dominant_temp in env.active_wave_temps or not env.active_wave_temps else 0.0

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
# 4. PPO DEEP REINFORCEMENT LEARNING
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
            advantages = []
            gae = 0.0

            for t in reversed(range(len(rewards))):
                delta = rewards[t] + self.gamma * next_values[t] * (1 - dones[t]) - values[t]
                gae = delta + self.gamma * self.lmbda * gae * (1 - dones[t])
                advantages.insert(0, gae)

            return np.array(advantages)

        def update(self, trajectory):
            # Unpack trajectory
            states = np.array([t['state'] for t in trajectory])
            actions = np.array([t['action'] for t in trajectory])
            old_log_probs = np.array([t['log_prob'] for t in trajectory])
            rewards = np.array([t['reward'] for t in trajectory])
            next_states = np.array([t['next_state'] for t in trajectory])
            dones = np.array([t['done'] for t in trajectory])
            valid_masks = [t['valid_actions'] for t in trajectory]

            # Compute values
            with torch.no_grad():
                states_t = torch.tensor(states, dtype=torch.float).to(self.device)
                next_states_t = torch.tensor(next_states, dtype=torch.float).to(self.device)
                values = self.critic(states_t).squeeze().cpu().numpy()
                next_values = self.critic(next_states_t).squeeze().cpu().numpy()

            # Compute advantages
            advantages = self.compute_advantages(rewards, values, next_values, dones)
            advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

            td_target = advantages + values

            # Convert to tensors
            states_t = torch.tensor(states, dtype=torch.float).to(self.device)
            actions_t = torch.tensor(actions, dtype=torch.long).view(-1, 1).to(self.device)
            old_log_probs_t = torch.tensor(old_log_probs, dtype=torch.float).view(-1, 1).to(self.device)
            advantages_t = torch.tensor(advantages, dtype=torch.float).view(-1, 1).to(self.device)
            td_target_t = torch.tensor(td_target, dtype=torch.float).view(-1, 1).to(self.device)

            # PPO update
            for _ in range(self.epochs):
                probs_raw = self.actor(states_t)

                # Apply masks
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

def train_ppo(generator: DataGenerator, n_episodes=200, update_interval=20):
    """Train PPO agent"""
    if not TORCH_AVAILABLE:
        print("PyTorch not available. Skipping PPO training.")
        return None, []

    # Create environment for dimension inference
    orders = generator.generate_orders(horizon_hours=4.0)
    env = PharmaWaveEnv(orders)
    state_dim = env.state_dim
    action_dim = env.action_dim

    agent = PPOAgent(state_dim, action_dim, hidden_dim=128)

    episode_rewards = []
    episode_metrics = []

    for episode in tqdm(range(n_episodes), desc="Training PPO"):
        # Generate new data each episode
        orders = generator.generate_orders(horizon_hours=4.0)
        env = PharmaWaveEnv(orders)
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

        # Update after collecting enough experience
        if len(trajectory) > 0 and (episode + 1) % update_interval == 0:
            agent.update(trajectory)

    return agent, episode_metrics


def evaluate_agent(agent, generator: DataGenerator, n_eval=20, use_ppo=True):
    """Evaluate agent on hold-out instances"""
    results = []

    for i in range(n_eval):
        orders = generator.generate_orders(horizon_hours=4.0)
        env = PharmaWaveEnv(orders)
        state_dict = env.reset()

        total_reward = 0.0

        while not env.done:
            valid_actions = env.get_valid_actions(state_dict)

            if use_ppo and TORCH_AVAILABLE:
                state = env.get_state_vector(state_dict)
                action, _, _ = agent.select_action(state, valid_actions, deterministic=True)
            else:
                # Random fallback
                action = random.choice(valid_actions)

            state_vec, reward, done, info = env.step(action)
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


def plot_training_results(metrics, save_path=None):
    """Plot training curves"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    rewards = [m['reward'] for m in metrics]
    waves = [m['n_waves'] for m in metrics]
    distances = [m['distance'] for m in metrics]
    misses = [m['misses'] for m in metrics]

    # Moving average
    window = max(1, len(rewards) // 20)
    if len(rewards) >= window:
        ma_rewards = np.convolve(rewards, np.ones(window)/window, mode='valid')
    else:
        ma_rewards = rewards

    axes[0, 0].plot(rewards, alpha=0.3, color='blue')
    if len(ma_rewards) < len(rewards):
        axes[0, 0].plot(range(window-1, len(rewards)), ma_rewards, color='red', linewidth=2)
    else:
        axes[0, 0].plot(ma_rewards, color='red', linewidth=2)
    axes[0, 0].set_xlabel('Episode')
    axes[0, 0].set_ylabel('Total Reward')
    axes[0, 0].set_title('Training Reward (PPO)')
    axes[0, 0].grid(True, alpha=0.3)

    axes[0, 1].plot(waves, color='green')
    axes[0, 1].set_xlabel('Episode')
    axes[0, 1].set_ylabel('Number of Waves')
    axes[0, 1].set_title('Waves per Episode')
    axes[0, 1].grid(True, alpha=0.3)

    axes[1, 0].plot(distances, color='orange')
    axes[1, 0].set_xlabel('Episode')
    axes[1, 0].set_ylabel('Total Picking Distance')
    axes[1, 0].set_title('Picking Distance per Episode')
    axes[1, 0].grid(True, alpha=0.3)

    axes[1, 1].plot(misses, color='red')
    axes[1, 1].set_xlabel('Episode')
    axes[1, 1].set_ylabel('Deadline Misses')
    axes[1, 1].set_title('Deadline Misses per Episode')
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
    plt.show()


def compare_heuristics(generator: DataGenerator, n_instances=20):
    """Compare all heuristics on same instances"""
    heuristics = ['FCFS', 'TEMP_FIRST', 'ZONE_NN', 'EDD', 'TZU']
    all_results = {h: [] for h in heuristics}

    for i in tqdm(range(n_instances), desc="Evaluating heuristics"):
        orders = generator.generate_orders(horizon_hours=4.0)

        for h in heuristics:
            env = PharmaWaveEnv(orders)
            result = run_heuristic(env, h, generator)
            result['instance'] = i
            all_results[h].append(result)

    # Aggregate
    summary = {}
    for h in heuristics:
        rewards = [r['total_reward'] for r in all_results[h]]
        distances = [r['total_distance'] for r in all_results[h]]
        waves = [r['n_waves'] for r in all_results[h]]
        misses = [r['deadline_misses'] for r in all_results[h]]
        violations = [r['temp_violations'] for r in all_results[h]]

        summary[h] = {
            'avg_reward': np.mean(rewards),
            'std_reward': np.std(rewards),
            'avg_distance': np.mean(distances),
            'avg_waves': np.mean(waves),
            'avg_misses': np.mean(misses),
            'avg_violations': np.mean(violations)
        }

    return summary, all_results


# =============================================================================
# 6. MAIN EXECUTION
# =============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("Smart Wave Allocation - Pharmaceutical Distribution")
    print("Deep Reinforcement Learning Prototype")
    print("=" * 60)

    # Initialize data generator
    generator = DataGenerator(seed=42)

    # Generate sample data
    print("\n[1] Generating synthetic order data...")
    orders = generator.generate_orders(horizon_hours=4.0)
    print(f"    Generated {len(orders)} orders")
    print(f"    Avg items per order: {np.mean([o.n_items for o in orders]):.2f}")
    print(f"    Urgent orders: {sum(1 for o in orders if o.is_urgent)} ({sum(1 for o in orders if o.is_urgent)/len(orders)*100:.1f}%)")

    # Test environment
    print("\n[2] Testing environment...")
    env = PharmaWaveEnv(orders)
    state_dict = env.reset()
    print(f"    State dimension: {env.state_dim}")
    print(f"    Action dimension: {env.action_dim}")

    # Run heuristics comparison
    print("\n[3] Running heuristic baselines...")
    heuristic_summary, heuristic_results = compare_heuristics(generator, n_instances=10)

    print("\n" + "-" * 60)
    print("HEURISTIC COMPARISON RESULTS")
    print("-" * 60)
    print(f"{'Heuristic':<15} {'Avg Reward':<12} {'Avg Dist':<12} {'Avg Waves':<12} {'Misses':<10} {'Viol.':<8}")
    print("-" * 60)
    for h, stats in heuristic_summary.items():
        print(f"{h:<15} {stats['avg_reward']:<12.1f} {stats['avg_distance']:<12.1f} "
              f"{stats['avg_waves']:<12.1f} {stats['avg_misses']:<10.1f} {stats['avg_violations']:<8.1f}")

    # Train PPO if torch available
    if TORCH_AVAILABLE:
        print("\n[4] Training PPO agent...")
        agent, metrics = train_ppo(generator, n_episodes=100, update_interval=10)

        print("\n[5] Evaluating trained agent...")
        ppo_results = evaluate_agent(agent, generator, n_eval=10, use_ppo=True)

        ppo_reward = np.mean([r['total_reward'] for r in ppo_results])
        ppo_dist = np.mean([r['total_distance'] for r in ppo_results])
        ppo_misses = np.mean([r['deadline_misses'] for r in ppo_results])
        ppo_viol = np.mean([r['temp_violations'] for r in ppo_results])

        print("\n" + "-" * 60)
        print("PPO RESULTS (Evaluation)")
        print("-" * 60)
        print(f"{'PPO':<15} {ppo_reward:<12.1f} {ppo_dist:<12.1f} "
              f"{'--':<12} {ppo_misses:<10.1f} {ppo_viol:<8.1f}")

        # Plot
        plot_training_results(metrics)
    else:
        print("\n[4] Skipping PPO training (PyTorch not available)")
        print("    Install PyTorch to enable DRL training: pip install torch")

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)
