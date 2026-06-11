# Maverick-SORT: Knowledge-Guided Deep Reinforcement Learning for Pharmaceutical Smart Wave Allocation

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.58-FF4B4B.svg)](https://streamlit.io/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.12-EE4C2C.svg)](https://pytorch.org/)

This repository contains the implementation of **Maverick-SORT**, a decision-support system for pharmaceutical warehouse wave allocation. It combines a **Knowledge-Guided Deep Reinforcement Learning (KGDRL)** core with interactive Streamlit dashboards, offering both an **Essential Edition** (free trial, browser-only) and a **Professional Edition** (live data upload, advanced optimization).

The core question the system answers: *In five minutes, can AI-driven wave allocation save money before committing to any WMS integration?*

---

## 🚀 Quick Start

### Essential Edition (Recommended First Try)
```bash
pip install -r requirements-standard.txt
streamlit run streamlit_app_v7.py
```

### Professional Edition
```bash
pip install -r requirements-pro.txt
streamlit run streamlit_app_pro_v5.py
```

### Static HTML Dashboard (No Backend)
Open `dashboard_release/smart_wave_dashboard_en.html` directly in any modern browser.

---

## 📂 Repository Structure

```
maverick_sort/
|
├── 📱 Streamlit Applications
│   ├── streamlit_app_v7.py              # Essential Edition (18 pages, free trial)
│   ├── streamlit_app_pro_v5.py          # Professional Edition (23 pages, live data)
│   ├── streamlit_app.py                 # Legacy unified entry
│   └── streamlit_app_v2.py ~ v6.py      # Earlier iteration versions
│   └── streamlit_app_pro_v1.py ~ v4.py  # Earlier Pro iterations
│
├── 🧠 Core Algorithms
│   ├── kgdrl_core_v2.py                 # KGDRL engine: GAT + PPO + KL heuristic guidance
│   ├── pharma_wave_allocation.py        # Baseline PPO environment and heuristics
│   ├── multi_objective_scheduler.py     # NSGA-II Pareto optimizer (Pro module)
│   ├── adaptive_policy.py               # EWMA-based online adaptive policy (Pro module)
│   └── what_if_simulator.py             # Scenario simulator (Essential module)
│
├── 📦 Page Modules (for v6/v7/Pro)
│   ├── page_modules/shared.py           # Common CSS, session state, data routers
│   ├── page_modules/orders_inventory.py # Orders, analytics, warehouse zones
│   ├── page_modules/operations.py       # Dashboard, SLA, task workstation, alerts
│   ├── page_modules/scheduling.py       # Algorithm Arena, What-If, NSGA-II, Live Adaptive
│   ├── page_modules/tech_showcase.py    # KGDRL framework, AI engine, multi-warehouse
│   ├── page_modules/business.py         # ROI, TCO, competitor radar, pricing
│   └── page_modules/demo.py             # Real-time simulation, demo mode
│
├── 🤖 Hugging Face AI Integration
│   ├── hf_integration/client.py         # Unified LLM client with 3-tier fallback
│   ├── hf_integration/copilot.py        # Maverick Copilot (FAQ + context-aware)
│   ├── hf_integration/insight_engine.py # Natural-language explanations for results
│   ├── hf_integration/report_generator.py # Auto-report generation for What-If / business
│   ├── hf_integration/alert_analyzer.py # RAG-based root-cause analysis (Pro)
│   ├── hf_integration/demand_forecaster.py # Time-series demand forecasting (Pro)
│   ├── hf_integration/prompts.py        # Bilingual prompt templates
│   └── hf_integration/config.py         # Availability detection and fallback config
│
├── 🔬 Research & Experiments
│   ├── Code of KGDRL/                   # Original KGDRL research notebooks
│   │   ├── experiment_KGDRL.ipynb
│   │   ├── experiment_DDQN.ipynb
│   │   ├── experiment_DDPG.ipynb
│   │   ├── experiment_A2C.ipynb
│   │   ├── experiment_rules.ipynb
│   │   ├── experiment_robustness.ipynb
│   │   ├── network.py                   # GAT + Actor-Critic networks
│   │   ├── new_env.py                   # Pharmaceutical wave environment
│   │   ├── PDR.py                       # Priority dispatching rules
│   │   └── raw_PPO.py / raw_DQN.py / raw_DDPG.py  # Raw RL baselines
│   │
│   └── Code of KGDRL_new/               # Refactored KGDRL experiment suite
│       ├── experiment_KGDRL.ipynb
│       ├── experiment_large_scale_after_modification.py
│       ├── network.py
│       ├── new_env.py
│       ├── PDR.py
│       ├── raw_PPO.py
│       └── Data/                        # Training/evaluation JSON outputs
│
├── 📊 Visualization & Dashboards
│   ├── dashboard_release/               # Standalone HTML dashboard (zero setup)
│   │   ├── smart_wave_dashboard.html
│   │   ├── smart_wave_dashboard_en.html
│   │   └── data/                        # Embedded JSON plot data
│   │
│   ├── KGDRL Visulization Ver.01/       # First-generation visualization package
│   │   ├── 01_Python代码与Notebook/
│   │   ├── 02_Markdown文档/
│   │   ├── 03_可视化面板HTML/
│   │   └── 06_运行数据/
│   │
│   └── KGDRL Visulization Ver.02/       # Second-generation visualization package
│       ├── 01_Python代码与Notebook/
│       ├── 02_Markdown文档/
│       ├── 03_可视化面板HTML/
│       └── 06_运行数据/
│
├── 🔧 Utilities & Pipelines
│   ├── run_full_pipeline.py             # Full benchmark: data → heuristics → PPO → eval
│   ├── run_ablation_quick.py            # Quick ablation study runner
│   ├── gen_demo_v2.py                   # Generate synthetic demo CSV datasets
│   ├── smart_wave_allocation.ipynb      # End-to-end allocation notebook
│   ├── translate_dashboard.py           # Dashboard localization helper
│   └── fix_streamlit_v3.py              # Deployment hotfix utilities
│
├── 💼 Product & Commercialization Docs
│   ├── COMMERCIALIZATION_7DAY_PLAN.md
│   ├── COMMERCIALIZATION_7DAY_PLAN_EN.md
│   ├── PRODUCT_REVIEW.md
│   ├── PRODUCT_REVIEW_EN.md
│   ├── product_tier_pricing.md
│   ├── DATA_UPLOAD_FEASIBILITY_REPORT.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── web_dashboard_feasibility.md
│   └── 3D_DASHBOARD_OPTIMIZATION_PLAN.md
│
├── 📚 Course & Research Materials
│   ├── 20260608_Presentation_of_Digital_Innovation/  # Slide deck and speech draft
│   ├── background/                      # Case description and pharma knowledge
│   ├── deep_research/                   # Research notes and references
│   ├── Commercial Analysis/             # Market and competitor analysis
│   ├── casebook_text.txt
│   └── problem_and_solution_draft.md
│
├── 🗂️ Demo Data
│   ├── demo_data/
│   ├── demo_data_v2/
│   └── simulation_data/
│
└── ⚙️ Configuration
    ├── requirements.txt                 # Default dependencies (auto-synced with standard)
    ├── requirements-standard.txt        # Essential Edition dependencies
    ├── requirements-pro.txt             # Professional Edition dependencies
    ├── .streamlit/config.toml           # Streamlit server and watcher config
    └── run_app.bat / run_app.ps1        # Windows quick launch scripts
```

---

## 🧩 Module Descriptions

### 1. Streamlit Applications

| File | Edition | Pages | Purpose |
|------|---------|-------|---------|
| `streamlit_app_v7.py` | **Essential** | 18 | Free-trial entry point. Browser-only, demo-data-first, five-minute validation. |
| `streamlit_app_pro_v5.py` | **Professional** | 23 | Paid tier. Live CSV upload hub, NSGA-II optimizer, EWMA adaptive intelligence. |
| `streamlit_app.py` | Legacy | — | Early unified prototype. |
| `streamlit_app_v2-v6.py` | Iterations | — | Progressive UI/UX iterations leading to v7. |
| `streamlit_app_pro_v1-v4.py` | Iterations | — | Progressive Pro feature iterations. |

**Why two editions?** The Essential Edition reduces the adoption barrier to near zero (no install, no data upload, no IT ticket). The Professional Edition is for warehouses that have already validated the idea and need live-data scale-up features.

### 2. Core Algorithms

| File | Function |
|------|----------|
| `kgdrl_core_v2.py` | **KGDRL engine**: Graph Attention Network (GAT) state encoder + PPO + KL-divergence constraint aligned with TZU heuristic. |
| `pharma_wave_allocation.py` | Vanilla PPO environment, data generator, and rule-based baselines (FCFS, TEMP_FIRST, ZONE_NN, EDD, TZU). |
| `multi_objective_scheduler.py` | **Pro module**: NSGA-II multi-objective Pareto frontier for cost × time × compliance trade-offs. |
| `adaptive_policy.py` | **Pro module**: EWMA demand prediction, dynamic wave capacity, online policy fine-tuning, federated-learning stubs. |
| `what_if_simulator.py` | **Essential module**: Parameter-sensitivity and scenario-comparison simulator without touching live systems. |

### 3. Page Modules

| File | Responsibility |
|------|----------------|
| `page_modules/shared.py` | Shared CSS (`PRO_CSS`), session-state helpers, upload validators, data routers. |
| `page_modules/orders_inventory.py` | Omni-channel orders, order analytics, warehouse & temperature zones. |
| `page_modules/operations.py` | Operations dashboard, SLA analytics, task workstation, smart alert center. |
| `page_modules/scheduling.py` | Algorithm Arena, What-If Lab, Strategy Optimizer (NSGA-II), Live Adaptive Intelligence. |
| `page_modules/tech_showcase.py` | KGDRL framework visualization, AI learning engine, multi-warehouse network. |
| `page_modules/business.py` | ROI calculator, TCO analysis, competitor radar, plans & pricing. |
| `page_modules/demo.py` | Real-time simulation embed and auto-play demo mode. |

### 4. Hugging Face AI Integration

| File | Function |
|------|----------|
| `hf_integration/config.py` | Model configs, availability detection, graceful degradation. |
| `hf_integration/client.py` | Unified LLM wrapper: HF Inference API → local transformers → rule-based mock. |
| `hf_integration/copilot.py` | Maverick Copilot: FAQ mode and context-aware assistant. |
| `hf_integration/insight_engine.py` | Natural-language explanations for benchmark, Pareto, and SLA results. |
| `hf_integration/report_generator.py` | Auto-generate What-If and business analysis reports. |
| `hf_integration/alert_analyzer.py` | **Pro**: Lightweight RAG for alert root-cause analysis. |
| `hf_integration/demand_forecaster.py` | **Pro**: Time-series demand forecasting with HF fallback to EWMA. |
| `hf_integration/prompts.py` | Bilingual (CN/EN) prompt templates for Qwen2.5-Instruct. |

### 5. Visualization Dashboards

| Path | Description |
|------|-------------|
| `dashboard_release/` | Production-ready standalone HTML dashboard. No Python backend required. |
| `KGDRL Visulization Ver.01/` | First-generation package: Python notebooks + HTML panels + run data. |
| `KGDRL Visulization Ver.02/` | Second-generation package with improved SDV-based data pipeline. |

---

## 🛠️ Installation

### Standard / Essential
```bash
pip install -r requirements-standard.txt
```

### Professional
```bash
pip install -r requirements-pro.txt
```

> **Note on `torchvision`**: intentionally omitted from all `requirements*.txt` files to avoid version conflicts with `torch==2.12.0`. The code gracefully degrades when `torchvision` is absent.

---

## ▶️ Usage

### Run Essential Edition
```bash
streamlit run streamlit_app_v7.py
```

### Run Professional Edition
```bash
streamlit run streamlit_app_pro_v5.py
```

### Run Full Benchmark Pipeline
```bash
python run_full_pipeline.py
```

### Run Quick Ablation Study
```bash
python run_ablation_quick.py
```

### Generate Demo Datasets
```bash
python gen_demo_v2.py
```

---

## 📈 Algorithm Arena Benchmarks

The `Algorithm Arena` compares KGDRL against five heuristic baselines:

| Method | Reward | Distance (m) | Waves | Deadline Miss | Temp Violations |
|--------|--------|--------------|-------|---------------|-----------------|
| FCFS | 1,786.9 | 690.9 | 85.9 | 0.0 | 38.5 |
| TEMP_FIRST | -2,958.1 | 987.4 | 125.8 | 0.0 | 0.0 |
| ZONE_NN | 1,733.8 | 669.0 | 82.9 | 0.0 | 37.3 |
| EDD | 1,752.0 | 667.8 | 83.1 | 0.0 | 37.5 |
| TZU | 144.6 | 666.7 | 83.0 | 0.0 | 21.4 |
| PPO (Vanilla) | 4,007.5 | 695.5 | 87.3 | 4.4 | 36.7 |
| **KGDRL-Full** | **1,908.8** | **665.7** | **82.8** | **0.0** | **39.0** |

*KGDRL achieves the lowest picking distance while maintaining zero deadline misses.*

---

## 🧪 Research Artifacts

- Original research notebooks: `Code of KGDRL/`
- Refactored experiment suite: `Code of KGDRL_new/`
- Presentation materials: `20260608_Presentation_of_Digital_Innovation/`
- AI-tool usage review: `AI_Tools_Usage_Review.md` / `AI_Tools_Usage_Review_EN.md`

---

## 📄 License & Attribution

This project was developed as part of the **Digital Innovation** course (SDC / AAUBS / UCAS, 2026).

Core algorithm: Knowledge-Guided Deep Reinforcement Learning for pharmaceutical smart wave allocation.

UI implementation: AI-assisted, human-reviewed.
