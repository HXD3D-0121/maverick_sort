"""
Quick ablation study runner (reduced episodes for faster execution).
Generates ablation_study.json for Day 2 deliverable.
"""
import sys
import json
import numpy as np
from kgdrl_core_v2 import run_ablation_study, DataGenerator

if __name__ == '__main__':
    print("Quick Ablation Study - Day 2")
    print("="*60)

    generator = DataGenerator(seed=42)

    results = run_ablation_study(
        generator,
        n_ppo_episodes=20,
        n_kgdrl_episodes=20,
        n_eval=10,
        pretrain=True,
        lambda_kg=0.1,
        device='cpu'
    )

    print("\nQuick ablation complete. Results saved to ablation_study.json")
