# Maverick-SORT — Smart Wave Allocation System

> **Intelligent pharmaceutical distribution powered by Knowledge-Guided Deep Reinforcement Learning (KGDRL)**

---

## 🏠 Repository Ownership

**This is the primary development fork.**

| | Original | This Fork |
|--|---------|-----------|
| **Owner** | JamieAnnSeckinger | **HXD3D-0121** |
| **Role** | Upstream | **Active Development (Admin)** |
| **Purpose** | Course project origin | **Commercialization & Iteration** |
| **URL** | `github.com/JamieAnnSeckinger/maverick_sort` | **`github.com/HXD3D-0121/maverick_sort`** |

> ⚠️ **All subsequent development, commits, and releases will be pushed to this fork by default.**
> The original repository remains as the upstream reference for course deliverables.

---

## 📋 Project Overview

Maverick-SORT is an AI-powered smart wave allocation system designed for pharmaceutical distribution centers. It addresses four critical industry pain points:

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

### Run Streamlit Dashboard

**Standard Edition (v7.0)** — 18 pages, core operational features:
```bash
streamlit run streamlit_app_v7.py
```

**Professional Edition (v5.0)** — 23 pages, full AI + prediction + strategy features:
```bash
streamlit run streamlit_app_pro_v5.py
```

**Windows One-Click Launch** (auto-uses `.venv`):
```bash
run_app.bat
```

Access at: `http://localhost:8501`

### Run KGDRL Ablation Study

```bash
python run_ablation_quick.py
```

---

## 📁 Project Structure

```
maverick_sort/
├── 📄 README.md                          # This file
├── 📄 COMMERCIALIZATION_7DAY_PLAN.md     # 7-day commercialization roadmap (CN)
├── 📄 COMMERCIALIZATION_7DAY_PLAN_EN.md  # 7-day commercialization roadmap (EN)
├── 📄 AI_Tools_Usage_Review.md           # AI usage documentation ("historical record")
├── 📄 AI_Tools_Usage_Review_EN.md        # English version
├── 📄 PRODUCT_REVIEW.md                  # LLM differentiation matrix + demo script (CN)
├── 📄 PRODUCT_REVIEW_EN.md               # English version
├── 📄 DEPLOYMENT_GUIDE.md                # Streamlit Cloud deployment guide
├── 📄 COPILOT_TEST_PROMPTS.md            # 23 test prompts for Copilot QA
│
├── 🤖 Algorithm Core
│   ├── pharma_wave_allocation.py         # Vanilla PPO + Environment + Heuristics
│   ├── kgdrl_core_v2.py                  # KGDRL: GAT + Knowledge Graph + KL Loss
│   ├── run_full_pipeline.py              # End-to-end experiment pipeline
│   ├── run_ablation_quick.py             # Quick ablation study runner
│   ├── what_if_simulator.py              # What-if scenario simulator
│   ├── multi_objective_scheduler.py      # NSGA-II Pareto scheduler
│   └── adaptive_policy.py                # EWMA + online learning + federated
│
├── 🧠 AI Integration (Hugging Face)
│   └── hf_integration/                   # 9 LLM modules (Copilot, Insight, Forecast, RAG)
│       ├── __init__.py
│       ├── config.py                     # API key resolution, model registry
│       ├── client.py                     # Unified LLM client (3-tier fallback)
│       ├── prompts.py                    # 10 bilingual prompt templates
│       ├── copilot.py                    # FAQ + context-aware assistant
│       ├── insight_engine.py             # Decision explanation (5 scenarios)
│       ├── report_generator.py           # Auto report summarization
│       ├── alert_analyzer.py             # RAG root-cause analysis
│       └── demand_forecaster.py          # Time-series forecasting
│
├── 📊 Streamlit Applications
│   ├── streamlit_app.py                  # v1: Course edition (backup)
│   ├── streamlit_app_v2.py               # v2: Industrial 4-view dashboard
│   ├── streamlit_app_v3.py               # v3: Unified 6-view (v2 + simulation)
│   ├── streamlit_app_v4.py               # v4: + 🏆 Algorithm Arena
│   ├── streamlit_app_v5.py               # v5: Essential edition (What-if + Arena)
│   ├── streamlit_app_v6.py               # v6: Essential trimmed (17 pages)
│   ├── streamlit_app_v7.py               # v7: AI-enhanced Essential (18 pages, current)
│   ├── streamlit_app_pro_v1.py           # Pro v1: early prototype
│   ├── streamlit_app_pro_v2.py           # Pro v2: full feature matrix
│   ├── streamlit_app_pro_v3.py           # Pro v3: modular refactor
│   ├── streamlit_app_pro_v4.py           # Pro v4: data-aware + Data Hub
│   └── streamlit_app_pro_v5.py           # Pro v5: + Hugging Face AI (23 pages, current)
│
├── 🧩 Page Modules (Modular Architecture)
│   └── page_modules/                     # 7 independent page modules
│       ├── shared.py                     # CSS, data generators, upload router
│       ├── orders_inventory.py
│       ├── operations.py                 # Alert Center, SLA, Task Station
│       ├── scheduling.py                 # Scenario Simulator, Strategy Optimizer
│       ├── tech_showcase.py              # KGDRL, AI Copilot page, Patent Wall
│       ├── business.py                   # ROI, TCO, Pricing
│       └── demo.py
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
│   ├── DATA_UPLOAD_FEASIBILITY_REPORT.md # Data upload technical plan
│   ├── 3D_DASHBOARD_OPTIMIZATION_PLAN.md # 3D panel strategic upgrade
│   ├── bvn_research_note.md              # BVN matrix decomposition research
│   ├── product_tier_pricing.md           # Pricing strategy
│   └── 讲稿.md                            # Presentation script
│
├── 🚀 Deployment
│   ├── requirements.txt                  # All dependencies (HF, torch, plotly)
│   ├── run_app.bat                       # Windows one-click launcher
│   └── run_app.ps1                       # PowerShell launcher
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
| Day 3 | Product Tier Release | What-if simulator, multi-objective scheduler, adaptive policy, pricing | ✅ |
| Day 4 | Modular Refactor + Data Upload | `page_modules/`, Data Hub, 3D Optimization Plan | ✅ |
| Day 5 | Hugging Face Integration | `hf_integration/`, Copilot, Insight Engine, Demand Forecast, RAG | ✅ |
| Day 6 | Business Case | Financial model, investor pitch, GTM strategy | 📋 |
| Day 7 | Final Delivery | End-to-end test, documentation freeze, demo video | 📋 |

---

## 🔔 Team Notice: Recent Additions (Day 3–5)

> **For teammates pulling this repo**: The following major components were added after Day 2. If you forked/cloned earlier, please pull the latest `Code-for-Deep-Reinforcement-Learning` branch.

### New Directories (must not be deleted)
| Directory | Purpose | Files |
|-----------|---------|-------|
| `hf_integration/` | Hugging Face LLM integration | 9 Python modules (Copilot, Insight Engine, Forecast, RAG, etc.) |
| `page_modules/` | Modular Streamlit architecture | 7 modules (shared, operations, scheduling, tech_showcase, etc.) |

### New Entry Points (use these for demo)
| File | Edition | Pages | AI Features |
|------|---------|-------|-------------|
| `streamlit_app_v7.py` | Essential (Standard) | 18 | Sidebar Copilot + Algorithm Arena + What-If + SLA |
| `streamlit_app_pro_v5.py` | Professional | 23 | All of v7 + Strategy Optimizer + Data Center + Live Adaptive + RAG |

### New Documents
| File | Purpose |
|------|---------|
| `DEPLOYMENT_GUIDE.md` | How to deploy to Streamlit Cloud (includes Secrets setup for HF_TOKEN) |
| `PRODUCT_REVIEW.md` / `_EN.md` | LLM differentiation matrix + enterprise demo script |
| `COPILOT_TEST_PROMPTS.md` | 23 test prompts to verify Copilot QA accuracy |
| `DATA_UPLOAD_FEASIBILITY_REPORT.md` | Technical plan for customer data upload |
| `3D_DASHBOARD_OPTIMIZATION_PLAN.md` | Strategic 3D visualization upgrade plan |

### Launch Checklist for Teammates
1. `pip install -r requirements.txt` (now includes `huggingface_hub`, `transformers`, `torch`, `plotly`)
2. Double-click `run_app.bat` (Windows) or run `.venv\Scripts\streamlit.exe run streamlit_app_pro_v5.py`
3. For Cloud deployment, see `DEPLOYMENT_GUIDE.md` Section 3

---

## 🤝 Contributing

This is a **course project + commercialization prototype** developed with AI assistance (Claude Code by Anthropic). All technical decisions are human-reviewed.

**Default Push Target**: `github.com/HXD3D-0121/maverick_sort` (this fork)

---

## 📜 License

© 2026 JamieAnnSeckinger. All rights reserved.

Patent pending: Knowledge-Guided Deep Reinforcement Learning for Pharmaceutical Wave Allocation.

---

> **Last Updated**: 2026/06/08  
> **Active Branch**: `Code-for-Deep-Reinforcement-Learning`  
> **Maintainer**: HXD3D-0121 (Admin)
