"""
Full pipeline: SDV data loading -> heuristic comparison -> PPO training -> evaluation -> JSON export
"""
import json
import numpy as np
import random
import math
import os
import sys

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sdv_pharma_wave_env import (
    SDVDataLoader, SDVPharmaWaveEnv, run_heuristic,
    PPOAgent, TORCH_AVAILABLE
)

print("=" * 70)
print("FULL PIPELINE: SDV Realistic Data -> Heuristics -> PPO -> JSON Export")
print("=" * 70)

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

DATA_DIR = "../../simulation_data/generated_datasets_sdv_SMALL"
OUTPUT_DIR = "../../06_运行数据/data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

N_HEURISTIC_INSTANCES = 10
N_TRAIN_EPISODES = 120
N_EVAL_EPISODES = 10

# =============================================================================
# 1. Load data
# =============================================================================
print("\n[1/5] Loading SDV simulation data...")
loader = SDVDataLoader(DATA_DIR)

warehouse_id = "WH_001"
orders = loader.get_orders_for_warehouse(warehouse_id)
sku_to_temp = loader.sku_to_temp

wh_data = loader.warehouses[loader.warehouses['warehouse_id'] == warehouse_id].iloc[0]
bins = []
for zone, count in [
    ("ambient", wh_data["ambient_zone_bins"]),
    ("cool", wh_data["cool_zone_bins"]),
    ("cold", wh_data["cold_zone_bins"]),
    ("frozen", wh_data["frozen_zone_bins"]),
    ("controlled", wh_data["controlled_zone_bins"]),
]:
    count = min(int(count), 50)
    for b in range(count):
        bins.append((f"{warehouse_id}_{zone.upper()}_{b+1:03d}", zone))

warehouse_bins = {warehouse_id: bins}

def make_env():
    return SDVPharmaWaveEnv(orders, warehouse_bins, sku_to_temp,
                           max_wave_orders=50, max_wave_volume=150.0,
                           alpha_setup=8.0, alpha_deadline=40.0,
                           alpha_completion=3.0, alpha_unprocessed_penalty=50.0,
                           time_step=5.0, max_steps=5000)

env_test = make_env()
print(f"  Orders: {len(orders)}, State dim: {env_test.state_dim}, Action dim: {env_test.action_dim}")

# Save order stats
order_stats = {
    'warehouse_id': warehouse_id,
    'total_orders': len(orders),
    'avg_skus_per_order': float(np.mean([o['n_skus'] for o in orders])),
    'priority_distribution': {
        'normal': sum(1 for o in orders if o['priority'] == 'normal'),
        'high': sum(1 for o in orders if o['priority'] == 'high'),
        'urgent': sum(1 for o in orders if o['priority'] == 'urgent'),
    },
    'temp_distribution': {
        'ambient': sum(1 for o in orders if o['dominant_temp'] == 'ambient'),
        'cool': sum(1 for o in orders if o['dominant_temp'] == 'cool'),
        'cold': sum(1 for o in orders if o['dominant_temp'] == 'cold'),
        'frozen': sum(1 for o in orders if o['dominant_temp'] == 'frozen'),
    },
    'arrival_timeline': [
        {'time': float(o['arrival_time']), 'temp': o['dominant_temp'], 'priority': o['priority']}
        for o in orders[:200]
    ]
}

with open(f'{OUTPUT_DIR}/order_stats.json', 'w', encoding='utf-8') as f:
    json.dump(order_stats, f, ensure_ascii=False, indent=2)
print(f"  Saved order_stats.json")

# =============================================================================
# 2. Heuristic comparison
# =============================================================================
print(f"\n[2/5] Running heuristic comparison ({N_HEURISTIC_INSTANCES} instances)...")
heuristics = ['FCFS', 'TEMP_FIRST', 'PRIORITY_FIRST', 'EDD', 'TZU']
all_heuristic_results = {h: [] for h in heuristics}

for i in range(N_HEURISTIC_INSTANCES):
    for h in heuristics:
        env = make_env()
        result = run_heuristic(env, h)
        all_heuristic_results[h].append({
            'total_reward': float(result['total_reward']),
            'n_waves': int(result['n_waves']),
            'total_distance': float(result['total_distance']),
            'deadline_misses': int(result['deadline_misses']),
            'temp_violations': int(result['temp_violations']),
        })

heuristic_summary = {}
for h in heuristics:
    rewards = [r['total_reward'] for r in all_heuristic_results[h]]
    distances = [r['total_distance'] for r in all_heuristic_results[h]]
    waves = [r['n_waves'] for r in all_heuristic_results[h]]
    misses = [r['deadline_misses'] for r in all_heuristic_results[h]]
    violations = [r['temp_violations'] for r in all_heuristic_results[h]]

    heuristic_summary[h] = {
        'avg_reward': float(np.mean(rewards)),
        'std_reward': float(np.std(rewards)),
        'avg_distance': float(np.mean(distances)),
        'avg_waves': float(np.mean(waves)),
        'avg_misses': float(np.mean(misses)),
        'avg_violations': float(np.mean(violations)),
    }

with open(f'{OUTPUT_DIR}/heuristic_results.json', 'w', encoding='utf-8') as f:
    json.dump({'summary': heuristic_summary, 'raw': all_heuristic_results}, f, ensure_ascii=False, indent=2)
print(f"  Saved heuristic_results.json")

print("\n  Heuristic Summary:")
for h, s in heuristic_summary.items():
    print(f"    {h:18s}: reward={s['avg_reward']:8.1f} +/- {s['std_reward']:6.1f}, "
          f"waves={s['avg_waves']:5.1f}, dist={s['avg_distance']:8.1f}")

# =============================================================================
# 3. PPO Training
# =============================================================================
agent = None
metrics = []

if TORCH_AVAILABLE:
    print(f"\n[3/5] Training PPO agent ({N_TRAIN_EPISODES} episodes)...")

    env = make_env()
    state_dim = env.state_dim
    action_dim = env.action_dim

    agent = PPOAgent(state_dim, action_dim, hidden_dim=128,
                     actor_lr=5e-4, critic_lr=1e-5)

    for episode in range(N_TRAIN_EPISODES):
        env = make_env()
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

        metrics.append({
            'reward': float(episode_reward),
            'n_waves': int(len(env.waves)),
            'distance': float(env.total_picking_distance),
            'misses': int(env.deadline_misses),
            'violations': int(env.temp_violations),
        })

        if len(trajectory) > 0 and (episode + 1) % 10 == 0:
            agent.update(trajectory)

    with open(f'{OUTPUT_DIR}/ppo_training.json', 'w', encoding='utf-8') as f:
        json.dump({
            'training_metrics': metrics,
            'actor_losses': [float(x) for x in agent.actor_losses],
            'critic_losses': [float(x) for x in agent.critic_losses],
        }, f, ensure_ascii=False, indent=2)
    print(f"  Saved ppo_training.json")
    print(f"  Final avg reward (last 10): {np.mean([m['reward'] for m in metrics[-10:]]):.1f}")
else:
    print("\n[3/5] SKIPPED - PyTorch not available")

# =============================================================================
# 4. PPO Evaluation
# =============================================================================
ppo_eval_results = []

if TORCH_AVAILABLE and agent is not None:
    print(f"\n[4/5] Evaluating PPO ({N_EVAL_EPISODES} instances)...")

    for i in range(N_EVAL_EPISODES):
        env = make_env()
        state_dict = env.reset()
        total_reward = 0.0
        step_log = []

        while not env.done:
            valid_actions = env.get_valid_actions(state_dict)
            state = env.get_state_vector(state_dict)
            action, _, _ = agent.select_action(state, valid_actions, deterministic=True)

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

        ppo_eval_results.append({
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

    ppo_summary = {
        'avg_reward': float(np.mean([r['total_reward'] for r in ppo_eval_results])),
        'avg_waves': float(np.mean([r['n_waves'] for r in ppo_eval_results])),
        'avg_distance': float(np.mean([r['total_distance'] for r in ppo_eval_results])),
        'avg_misses': float(np.mean([r['deadline_misses'] for r in ppo_eval_results])),
        'avg_violations': float(np.mean([r['temp_violations'] for r in ppo_eval_results])),
    }

    with open(f'{OUTPUT_DIR}/ppo_eval.json', 'w', encoding='utf-8') as f:
        json.dump({'summary': ppo_summary, 'episodes': ppo_eval_results}, f, ensure_ascii=False, indent=2)
    print(f"  Saved ppo_eval.json")
    print(f"  PPO avg reward: {ppo_summary['avg_reward']:.1f}")
else:
    print("\n[4/5] SKIPPED - PyTorch not available")

# =============================================================================
# 5. Generate comparison plots
# =============================================================================
print("\n[5/5] Generating comparison data...")

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

methods = list(heuristic_summary.keys())
if TORCH_AVAILABLE and ppo_eval_results:
    methods.append('PPO')

rewards = [heuristic_summary[m]['avg_reward'] for m in methods if m in heuristic_summary]
if TORCH_AVAILABLE and ppo_eval_results:
    rewards.append(ppo_summary['avg_reward'])

colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#e377c2']
axes[0, 0].bar(methods, rewards, color=colors[:len(methods)])
axes[0, 0].set_ylabel('Average Total Reward')
axes[0, 0].set_title('Method Comparison: Total Reward')
axes[0, 0].tick_params(axis='x', rotation=45)
axes[0, 0].grid(True, alpha=0.3, axis='y')

if TORCH_AVAILABLE and metrics:
    rewards_train = [m['reward'] for m in metrics]
    window = max(1, len(rewards_train) // 20)
    if len(rewards_train) >= window:
        ma = np.convolve(rewards_train, np.ones(window)/window, mode='valid')
        axes[0, 1].plot(rewards_train, alpha=0.3, color='blue', label='Raw')
        axes[0, 1].plot(range(window-1, len(rewards_train)), ma, color='red', linewidth=2, label=f'MA({window})')
    else:
        axes[0, 1].plot(rewards_train, color='blue')
    axes[0, 1].set_xlabel('Episode')
    axes[0, 1].set_ylabel('Total Reward')
    axes[0, 1].set_title('PPO Training Curve')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
else:
    axes[0, 1].text(0.5, 0.5, 'PPO not available', ha='center', va='center', transform=axes[0, 1].transAxes)

waves_data = [heuristic_summary[m]['avg_waves'] for m in heuristic_summary.keys()]
if TORCH_AVAILABLE and ppo_eval_results:
    waves_data.append(ppo_summary['avg_waves'])
axes[1, 0].bar(methods, waves_data, color=colors[:len(methods)])
axes[1, 0].set_ylabel('Average Waves')
axes[1, 0].set_title('Method Comparison: Waves Created')
axes[1, 0].tick_params(axis='x', rotation=45)
axes[1, 0].grid(True, alpha=0.3, axis='y')

for h in heuristic_summary.keys():
    dist = heuristic_summary[h]['avg_distance']
    miss = heuristic_summary[h]['avg_misses']
    axes[1, 1].scatter(dist, miss, s=200, label=h, alpha=0.7)
if TORCH_AVAILABLE and ppo_eval_results:
    axes[1, 1].scatter(ppo_summary['avg_distance'], ppo_summary['avg_misses'], s=200, marker='*', color='red', label='PPO', alpha=0.9)
axes[1, 1].set_xlabel('Average Picking Distance')
axes[1, 1].set_ylabel('Average Deadline Misses')
axes[1, 1].set_title('Distance vs Deadline Misses')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/comparison_plots.png', dpi=150, bbox_inches='tight')
print("  Saved comparison_plots.png")

# =============================================================================
# 6. Final comparison table
# =============================================================================
print("\n" + "=" * 70)
print("FINAL COMPARISON TABLE")
print("=" * 70)
print(f"{'Method':<18} {'Reward':<10} {'Waves':<8} {'Distance':<10} {'Misses':<8} {'Viol.':<8}")
print("-" * 70)
for h, s in heuristic_summary.items():
    print(f"{h:<18} {s['avg_reward']:<10.1f} {s['avg_waves']:<8.1f} "
          f"{s['avg_distance']:<10.1f} {s['avg_misses']:<8.1f} {s['avg_violations']:<8.1f}")
if TORCH_AVAILABLE and ppo_eval_results:
    print(f"{'PPO (DRL)':<18} {ppo_summary['avg_reward']:<10.1f} {ppo_summary['avg_waves']:<8.1f} "
          f"{ppo_summary['avg_distance']:<10.1f} {ppo_summary['avg_misses']:<8.1f} {ppo_summary['avg_violations']:<8.1f}")
print("=" * 70)

final_results = {
    'heuristic_summary': heuristic_summary,
    'ppo_available': TORCH_AVAILABLE,
}
if TORCH_AVAILABLE and ppo_eval_results:
    final_results['ppo_summary'] = ppo_summary

with open(f'{OUTPUT_DIR}/final_results.json', 'w', encoding='utf-8') as f:
    json.dump(final_results, f, ensure_ascii=False, indent=2)

print("\nAll outputs saved to ./06_运行数据/data/")
