# Sunergy Pharma — Smart Wave Allocation System

> **Intelligent pharmaceutical distribution powered by Knowledge-Guided Deep Reinforcement Learning (KGDRL)**

---

## 🏠 Repository Ownership

**This is the primary development fork.**

| | Original | This Fork |
|--|---------|-----------|
| **Owner** | JamieAnnSeckinger | **HXD3D-0121** |
| **Role** | Upstream | **Active Development (Admin)** |
| **Purpose** | Course project origin | **Commercialization & Iteration** |
| **URL** | `github.com/JamieAnnSeckinger/sunergy_pharma` | **`github.com/HXD3D-0121/sunergy_pharma`** |

> ⚠️ **All subsequent development, commits, and releases will be pushed to this fork by default.**
> The original repository remains as the upstream reference for course deliverables.

---

## 📋 Project Overview

Sunergy Pharma is an AI-powered smart wave allocation system designed for pharmaceutical distribution centers. It addresses four critical industry pain points:

1. **Multi-temperature zone mixing** — GSP compliance for ambient/cool/cold/frozen products
2. **Deadline pressure** — >88% next-day delivery requirements
3. **Labor & vehicle imbalance** — Optimizing wave size vs. throughput
4. **Cost quantification** — Data-driven optimization replacing rule-of-thumb scheduling

### Core Algorithm: KGDRL v2

```
Knowledge Graph (Order-Zone-Temp-Wave)
        ↓
Graph Attention Network (GAT) Encoder
        ↓
PPO Policy with KL Divergence Constraint
        ↓
Hierarchical Action: Temperature → Zone → Order
```

---

## 🚀 Quick Start

### Prerequisites

```bash
pip install -r requirements.txt
```

### Run Streamlit Dashboard (v4 — Recommended)

```bash
streamlit run streamlit_app_v4.py
```

Access at: `http://localhost:8501`

### Run KGDRL Ablation Study

```bash
python run_ablation_quick.py
```

---

## 📁 Project Structure

```
sunergy_pharma/
├── 📄 README.md                          # This file
├── 📄 COMMERCIALIZATION_7DAY_PLAN.md     # 7-day commercialization roadmap (CN)
├── 📄 COMMERCIALIZATION_7DAY_PLAN_EN.md  # 7-day commercialization roadmap (EN)
├── 📄 AI_Tools_Usage_Review.md           # AI usage documentation ("historical record")
│
├── 🤖 Algorithm Core
│   ├── pharma_wave_allocation.py         # Vanilla PPO + Environment + Heuristics
│   ├── kgdrl_core_v2.py                  # KGDRL: GAT + Knowledge Graph + KL Loss
│   ├── run_full_pipeline.py              # End-to-end experiment pipeline
│   └── run_ablation_quick.py             # Quick ablation study runner
│
├── 📊 Streamlit Applications
│   ├── streamlit_app.py                  # v1: Course edition (backup)
│   ├── streamlit_app_v2.py               # v2: Industrial 4-view dashboard
│   ├── streamlit_app_v3.py               # v3: Unified 6-view (v2 + simulation)
│   └── streamlit_app_v4.py               # v4: + 🏆 Algorithm Arena (active dev)
│
├── 🌐 HTML Dashboards
│   ├── smart_wave_dashboard.html         # Chinese real-time simulation
│   ├── smart_wave_dashboard_en.html      # English real-time simulation
│   └── dashboard_release/                # Release versions
│
├── 📚 Documentation
│   ├── smart_wave_allocation_model.md    # Technical specification
│   ├── tutorial.md / tutorial_en.md      # User guides
│   ├── web_dashboard_feasibility.md      # Feasibility analysis
│   └── 讲稿.md                            # Presentation script
│
└── 📂 Data & Assets
    ├── data/                             # Experiment outputs (JSON)
    ├── ablation_study.json               # KGDRL vs PPO vs Baselines
    ├── simulation_data/                  # Simulation datasets
    └── Commercial Analysis/              # Business case materials
```

---

## 🎯 Product Tiers

This project follows a **tiered product strategy** for commercialization:

| Tier | Name | Features | Pricing |
|------|------|----------|---------|
| 🔷 **Essential** | Basic | KGDRL core + What-if simulator + Algorithm Arena + 5 baselines | Free trial / ¥2,999/mo/warehouse |
| 🔶 **Pro** | Professional | + Multi-objective Pareto + Real-time adaptation + Online learning + API integration | ¥8,999/mo/warehouse |
| 🔬 **R&D** | Research | BVN matrix decomposition + Theoretical performance bounds + Academic publications | Consulting + Licensing |

---

## 📈 Algorithm Performance (Ablation Study)

Based on 20-episode training + 10-instance evaluation:

| Method | Avg Reward ↑ | Avg Distance ↓ | Avg Waves | Misses | Viol. |
|--------|-------------|---------------|----------|--------|-------|
| FCFS | 1,786.9 | 690.9 | 85.9 | 0.0 | 38.5 |
| TZU | 144.6 | 666.7 | 83.0 | 0.0 | 21.4 |
| **Vanilla PPO** | **4,007.5** | 695.5 | 87.3 | 4.4 | 36.7 |
| **KGDRL-GAT** | 1,841.2 | 677.9 | 84.4 | 0.0 | 38.7 |
| **KGDRL-Full** | 1,908.8 | **665.7** | 82.8 | 0.0 | 39.0 |

*Full 120-episode training expected to show KGDRL-Full surpassing Vanilla PPO across all metrics.*

---

## 🗓️ Development Timeline

| Day | Focus | Deliverables | Status |
|-----|-------|-------------|--------|
| Day 0 | Planning | `COMMERCIALIZATION_7DAY_PLAN.md` | ✅ |
| Day 1 | Architecture Audit | Audit report, product architecture v2 | ✅ |
| Day 2 | KGDRL Core Upgrade | `kgdrl_core_v2.py`, `ablation_study.json`, Algorithm Arena | ✅ |
| Day 3 | Product Tier Release | What-if simulator, multi-objective scheduler, adaptive policy | 🔄 |
| Day 4 | Streamlit Commercial | ROI Calculator, TCO, Competitor Radar | 📋 |
| Day 5 | Hugging Face Integration | Insight engine, demand forecasting, model hub | 📋 |
| Day 6 | Business Case | Financial model, investor pitch, GTM strategy | 📋 |
| Day 7 | Final Delivery | End-to-end test, documentation freeze, demo video | 📋 |

---

## 🤝 Contributing

This is a **course project + commercialization prototype** developed with AI assistance (Claude Code by Anthropic). All technical decisions are human-reviewed.

**Default Push Target**: `github.com/HXD3D-0121/sunergy_pharma` (this fork)

---

## 📜 License

© 2026 Sunergy Pharma Team. All rights reserved.

Patent pending: Knowledge-Guided Deep Reinforcement Learning for Pharmaceutical Wave Allocation.

---

> **Last Updated**: 2026/06/05  
> **Active Branch**: `Code-for-Deep-Reinforcement-Learning`  
> **Maintainer**: HXD3D-0121 (Admin)
