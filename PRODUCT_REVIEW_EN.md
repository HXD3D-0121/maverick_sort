# Maverick-SORT — Product Review & Demo Guide

> **Document Type**: LLM Feature Differentiation Review + Enterprise Presentation Script  
> **Applicable Versions**: Essential v7.0 (Standard) + Professional v5.0 (Pro)  
> **Last Updated**: 2026/06/08

---

## 1. LLM Calling Permission Differentiation Matrix

| AI Feature Module | Standard v7 | Pro v5 | Differentiation Note |
|------------------|-------------|--------|---------------------|
| **Sidebar Copilot** | ✅ FAQ Q&A | ✅ FAQ Q&A | Same code in both versions |
| **AI Copilot Page** | ✅ FAQ Page | ✅ FAQ Page | Same code in both versions |
| **Algorithm Arena** | ✅ `explain_benchmark` | ✅ `explain_benchmark` | Auto-generates algorithm comparison conclusions |
| **Scenario Simulator** | ✅ `summarize_what_if` | ✅ `summarize_what_if` | Auto-generates What-If executive summary |
| **SLA Analytics** | ✅ `explain_sla_trend` | ✅ `explain_sla_trend` | Auto-interprets SLA trend data |
| **Alert Center** | ✅ `analyze_alert` | ✅ `analyze_alert` | RAG-based root-cause analysis |
| **Strategy Optimizer** | ❌ | ✅ `explain_pareto` | **Pro Only**: Pareto strategy explanation |
| **Live Adaptive** | ❌ | ✅ `explain_adaptive_adjustment` | **Pro Only**: Adaptive adjustment interpretation |
| **Data Center** | ❌ | ✅ `demand_forecaster` | **Pro Only**: AI demand forecasting |
| **Command Center** | ❌ | ✅ `explain_3d_command_center` | **Pro Only**: 3D tactical insight |
| **Business Analysis** | ❌ | ✅ `generate_business_report` | **Pro Only**: Investor-grade report |

**Core Differentiation Summary**:
- **Standard Edition**: 6 AI feature points, covering daily operational assistance
- **Pro Edition**: 10 AI feature points, adding **predictive AI** and **deep strategy AI** on top of Standard

---

## 2. Copilot Interaction Fix Log

The following fixes were applied to Copilot in this iteration, synchronized across both versions:

| Fix Item | Before | After |
|----------|--------|-------|
| Quick question button call path | `ask_with_context()` (LLM guesses blindly) | `ask_faq()` (hits preset cache) |
| Free-form input call path | `ask_with_context()` (no context) | `ask_faq()` (FAQ cache + LLM fallback) |
| `_fuzzy_match()` matching logic | Rigid whole-sentence containment | Added keyword trigger map (`nsga`/`kgdrl`/`adaptive` etc.) |
| Input rerun loop | No clear → infinite loop | `del session_state` → single trigger |
| Message render order | History above, input below | Input above, history below (replies grow downward) |
| Offline message | Generic text | Shows specific reason from `hf['msg']` |

---

## 3. Enterprise Presentation Script (English)

### Step 1: Open Standard v7 (Show Basic AI Capabilities)

> "This is the **Essential Edition**, designed for small-to-medium warehouses. AI capabilities cover daily operational decision support."

**Demo Actions**:
1. Click **"🤖 Maverick Copilot"** in sidebar → Type `What is KGDRL?` → Show instant preset answer
2. Go to **Algorithm Arena** → Click any benchmark comparison → AI strategy conclusion auto-generates at bottom (green highlight)
3. Go to **Scenario Simulator** → Run a What-If scenario → AI executive summary auto-generates

**Talking Points**:
> "The Standard Edition has 6 built-in AI decision-support points: Copilot Q&A, algorithm conclusions, What-If reports, SLA insights, and alert analysis. All work out of the box."

### Step 2: Switch to Pro v5 (Show Advanced AI Capabilities)

> "This is the **Pro Edition**, designed for large warehouses and enterprise groups. On top of Standard, it adds **predictive AI** and **deep strategy AI**."

**Demo Actions**:
1. Go to **Strategy Optimizer** → Run NSGA-II → Click a Pareto point → Show AI auto-explanation: "Why this strategy point suits cost-first scenarios"
2. Go to **Data Center** → Upload orders.csv → Click AI Forecast → Show 7-day demand forecast + AI natural-language interpretation
3. Go to **Live Adaptive** → Trigger a capacity adjustment → Show AI auto-interpretation: "Why the system expanded capacity at this time point"

**Talking Points**:
> "Pro adds 4 deep AI features: strategy optimization explanation, real-time adaptive interpretation, demand forecasting, and 3D tactical insights. These aren't generic chatbots—they're **domain AI embedded in business workflows**—every conclusion is based on real-time computed data."

### Step 3: Differentiation Summary (Key Message for Decision Makers)

| Dimension | Standard | Pro |
|-----------|----------|-----|
| AI Count | 6 feature points | 10 feature points |
| AI Depth | Explains existing results | **Predicts future** + explains strategy |
| Use Case | Daily operational support | Group-level strategic decisions |
| Pricing | ¥2,999/warehouse/month | ¥8,999/warehouse/month |

---

## 4. Required Files for LLM Invocation

The following files must be committed completely; otherwise AI features will not work:

```
hf_integration/
├── __init__.py              # Package entry
├── config.py                # API key resolution, model config
├── client.py                # Unified LLM client (3-tier fallback)
├── prompts.py               # 10 bilingual Prompt templates
├── insight_engine.py        # Decision explanation (5 scenarios)
├── report_generator.py      # Auto report summarization
├── copilot.py               # Smart assistant (FAQ + keyword trigger)
├── alert_analyzer.py        # RAG root-cause analysis
└── demand_forecaster.py     # Time-series forecasting

page_modules/shared.py         # try_import_hf() unified import wrapper
streamlit_app_pro_v5.py       # Pro entry (includes Data Center, Strategy Optimizer, etc.)
streamlit_app_v7.py           # Standard entry
requirements.txt              # Must include huggingface_hub, transformers, torch, plotly
```

---

## 5. Launch Commands

```bash
# Standard Edition
.venv\Scripts\streamlit.exe run streamlit_app_v7.py

# Pro Edition
.venv\Scripts\streamlit.exe run streamlit_app_pro_v5.py

# Or double-click to run
run_app.bat
```

---

> **Document Version**: v1.0  
> **Last Updated**: 2026/06/08
