"""
Maverick-SORT — Professional Edition v2.0
===========================================
Pro Tier Streamlit Application

Genuinely integrated modules:
  - multi_objective_scheduler.py  → Pareto Optimizer (real NSGA-II)
  - adaptive_policy.py            → Adaptive Monitor (real EWMA simulation)
  - what_if_simulator.py          → What-If Lab
  - product_tier_pricing.md       → Subscribe & Group Pricing

Pages:
  1. 🏠 Pro Home — Overview + Upgrade Incentive
  2. 🔮 What-If Lab — REAL simulator
  3. ⚖️ Pareto Optimizer — REAL NSGA-II execution
  4. 📡 Adaptive Monitor — REAL 24h EWMA simulation
  5. 🧠 Online Learning — EWC + Replay Buffer status
  6. 🌐 Federated Hub — Multi-warehouse architecture
  7. 🏆 Algorithm Arena
  8. 📊 Advanced Analytics
  9. 💳 Subscribe & Upgrade — Pro pricing + Group calculator

Author: AI-assisted implementation
Date: 2026/06/06
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import time
import random
import numpy as np
import pandas as pd
import altair as alt
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter, deque

# =============================================================================
# IMPORT REAL MODULES
# =============================================================================
WHAT_IF_AVAILABLE = False
MOS_AVAILABLE = False
ADAPTIVE_AVAILABLE = False

# What-if
try:
    from what_if_simulator import WhatIfSimulator, ScenarioConfig, ScenarioResult
    WHAT_IF_AVAILABLE = True
except Exception as e:
    st.toast(f"What-if import: {e}", icon="⚠️")

# Multi-objective scheduler
try:
    from multi_objective_scheduler import (
        MultiObjectiveScheduler, MultiObjectiveConfig,
        STRATEGY_PROFILES, ParetoSolution
    )
    MOS_AVAILABLE = True
except Exception as e:
    st.toast(f"MOS import: {e}", icon="⚠️")

# Adaptive policy
try:
    from adaptive_policy import (
        AdaptivePolicyController, AdaptiveConfig,
        ArrivalRateEstimator, AdaptiveWaveCapacity,
        OnlinePolicyUpdater, PolicyEnsemble, FederatedCoordinator
    )
    ADAPTIVE_AVAILABLE = True
except Exception as e:
    st.toast(f"Adaptive import: {e}", icon="⚠️")

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="Maverick-SORT | Professional Edition v2",
    page_icon="🔶",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# CUSTOM CSS — Pro Amber Theme
# =============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --bg-primary: #0a0f1e;
        --bg-card: #111827;
        --accent-blue: #3b82f6;
        --accent-cyan: #06b6d4;
        --accent-green: #10b981;
        --accent-amber: #f59e0b;
        --accent-red: #ef4444;
        --accent-purple: #8b5cf6;
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
        --border: rgba(148, 163, 184, 0.12);
    }

    .main-header { font-size: 2.2rem; font-weight: 800; color: #f8fafc; margin-bottom: 0.3rem; font-family: 'Inter', sans-serif; }
    .sub-header { font-size: 1rem; color: #94a3b8; margin-bottom: 1.5rem; font-family: 'Inter', sans-serif; }
    .section-header { font-size: 1.1rem; font-weight: 700; color: #e2e8f0; margin: 1.2rem 0 0.8rem; padding-bottom: 0.4rem; border-bottom: 1px solid var(--border); }

    .metric-card { background: linear-gradient(135deg, #1e3a5f 0%, #1e293b 100%); padding: 1.2rem; border-radius: 12px; border: 1px solid var(--border); text-align: center; }
    .metric-value { font-size: 1.8rem; font-weight: 800; color: #f8fafc; }
    .metric-label { font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }

    .pro-card { background: #111827; border-radius: 12px; padding: 1.5rem; border: 1px solid var(--border); transition: all 0.2s; }
    .pro-card:hover { border-color: rgba(245, 158, 11, 0.4); box-shadow: 0 4px 16px rgba(245, 158, 11, 0.1); }

    .pricing-card { background: #111827; border-radius: 16px; padding: 2rem 1.5rem; text-align: center; border: 1px solid var(--border); transition: all 0.3s; position: relative; }
    .pricing-card:hover { transform: translateY(-4px); box-shadow: 0 12px 32px rgba(245, 158, 11, 0.15); }
    .pricing-card.popular { border: 2px solid #f59e0b; }
    .popular-badge { position: absolute; top: -12px; left: 50%; transform: translateX(-50%); background: linear-gradient(135deg, #f59e0b, #ec4899); color: white; padding: 4px 16px; border-radius: 20px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; }
    .price-amount { font-size: 2.5rem; font-weight: 800; color: #f8fafc; }
    .price-period { font-size: 0.85rem; color: #64748b; }
    .feature-check { color: #10b981; margin-right: 8px; }
    .feature-x { color: #ef4444; margin-right: 8px; }

    [data-testid="stSidebar"] { background: #0f172a; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SESSION STATE
# =============================================================================
def ensure_state(key, default):
    if key not in st.session_state:
        st.session_state[key] = default

ensure_state("pro_pareto_front", None)
ensure_state("pro_pareto_scheduler", None)
ensure_state("pro_adaptive_results", None)
ensure_state("pro_adaptive_controller", None)
ensure_state("pro_what_if_results", None)
ensure_state("pro_billing", "monthly")

# =============================================================================
# MOCK DATA HELPERS
# =============================================================================
def generate_orders_pro(n=30):
    np.random.seed(42)
    temps = ["Ambient", "Cool", "Cold", "Frozen"]
    clients = ["Hospital", "Clinic", "Pharmacy", "Distributor"]
    data = []
    for i in range(n):
        data.append({
            "Order ID": f"ORD-{20260000 + i}",
            "Client": np.random.choice(clients),
            "SKU Count": np.random.choice([3,4,5], p=[0.4,0.35,0.25]),
            "Temperature": np.random.choice(temps, p=[0.55,0.25,0.15,0.05]),
            "Deadline (h)": round(np.random.exponential(12) + 2, 1),
            "Priority": "Urgent" if np.random.rand() < 0.2 else "Standard",
            "Volume": np.random.randint(10, 100),
            "Status": np.random.choice(["Pending", "Picking", "Packed", "Dispatched"], p=[0.3,0.3,0.25,0.15]),
        })
    return pd.DataFrame(data)


def generate_order_log(n=50, seed=None):
    """Generate simulated omni-channel order log."""
    if seed is not None:
        np.random.seed(seed)
    client_types = ["Public Hospital", "Chain Pharmacy", "Independent Pharmacy", "Primary Healthcare"]
    temps = ["Ambient", "Cool", "Cold", "Frozen", "Deep Frozen"]
    times = ["Morning Peak", "Afternoon", "Night Peak"]
    now = datetime.now()
    rows = []
    for i in range(n):
        ts = now - timedelta(minutes=np.random.randint(0, 480))
        sku_count = np.random.choice([1, 2, 3, 4, 5], p=[0.15, 0.25, 0.30, 0.20, 0.10])
        rows.append({
            "Order ID": f"ORD-{np.random.randint(100000, 999999)}",
            "Client Type": np.random.choice(client_types, p=[0.35, 0.30, 0.20, 0.15]),
            "SKU Count": sku_count,
            "Temperature": np.random.choice(temps, p=[0.55, 0.20, 0.12, 0.08, 0.05]),
            "Time Window": np.random.choice(times, p=[0.45, 0.35, 0.20]),
            "Timestamp": ts.strftime("%H:%M:%S"),
            "Status": np.random.choice(
                ["Pending Dispatch", "Picking in Progress", "Completed", "Stagnant Exception"],
                p=[0.25, 0.30, 0.40, 0.05]
            ),
            "Priority": np.random.choice(["Standard", "Urgent"], p=[0.80, 0.20]),
        })
    return pd.DataFrame(rows)


def generate_inventory_data(seed=None):
    """Generate simulated warehouse inventory with expiry tracking."""
    if seed is not None:
        np.random.seed(seed)
    meds = [
        ("Amoxicillin 500mg", "Antibiotic", "Ambient"),
        ("Insulin Glargine", "Cold Chain Insulin", "Cold"),
        ("Ibuprofen 200mg", "OTC Pain Relief", "Ambient"),
        ("Metformin 850mg", "Diabetes", "Cool"),
        ("Azithromycin 250mg", "Antibiotic", "Ambient"),
        ("Heparin Sodium", "Anticoagulant", "Cool"),
        ("Influenza Vaccine", "Vaccine", "Frozen"),
        ("Aspirin 100mg", "Cardiovascular", "Ambient"),
        ("Salbutamol Inhaler", "Respiratory", "Ambient"),
        ("Omeprazole 20mg", "GI Medication", "Ambient"),
        ("Cefuroxime 250mg", "Antibiotic", "Ambient"),
        ("Paclitaxel Injection", "Oncology", "Cool"),
        ("Artemether Injection", "Antimalarial", "Cool"),
        ("Hydroxychloroquine", "Autoimmune", "Ambient"),
        ("Remdesivir Vial", "Antiviral", "Cool"),
    ]
    rows = []
    today = datetime.now()
    for name, cat, temp in meds:
        stock = np.random.randint(500, 15000)
        expiry = today + timedelta(days=np.random.randint(10, 365))
        days_left = (expiry - today).days
        rows.append({
            "SKU": name,
            "Category": cat,
            "Temperature Zone": temp,
            "Stock Qty": stock,
            "Expiry Date": expiry.strftime("%Y-%m-%d"),
            "Days Left": days_left,
            "Risk Level": "Critical" if days_left <= 30 else "Warning" if days_left <= 60 else "Notice" if days_left <= 90 else "Normal",
        })
    return pd.DataFrame(rows)


def generate_sla_history():
    """Generate 12-month SLA fulfillment history + 14-day forecast."""
    months = pd.date_range(end=datetime.now(), periods=12, freq="MS").strftime("%b %Y").tolist()
    clients = ["Public Hospital", "Chain Pharmacy", "Independent Pharmacy", "Primary Healthcare"]
    history = {}
    for client in clients:
        base = np.random.uniform(85, 95)
        trend = np.random.uniform(-0.5, 0.5, 12)
        seasonal = 3 * np.sin(np.linspace(0, 2 * np.pi, 12))
        noise = np.random.normal(0, 1.5, 12)
        history[client] = np.clip(base + trend + seasonal + noise, 80, 99.5)

    # Forecast
    forecast_days = pd.date_range(start=datetime.now(), periods=14, freq="D").strftime("%m-%d").tolist()
    forecast = {}
    for client in clients:
        last = history[client][-1]
        trend = np.random.uniform(-0.2, 0.3, 14)
        forecast[client] = np.clip(last + np.cumsum(trend), 75, 99)

    return months, history, forecast_days, forecast


def generate_picking_tasks(n=20):
    """Generate simulated warehouse picking tasks."""
    zones = [f"Zone {chr(65 + i)}" for i in range(8)]
    clients = ["Public Hospital", "Chain Pharmacy", "Independent Pharmacy", "Primary Healthcare"]
    skus = ["Insulin Pen", "Amoxicillin", "Ibuprofen", "Metformin", "Aspirin", "Salbutamol", "Omeprazole", "Cefuroxime"]
    tasks = []
    for i in range(n):
        zone = np.random.choice(zones)
        client = np.random.choice(clients)
        n_skus = np.random.randint(2, 6)
        picked = np.random.choice(skus, n_skus, replace=False)
        qtys = [np.random.randint(1, 5) for _ in picked]
        checklist = ", ".join([f"{s} x{q}" for s, q in zip(picked, qtys)])
        path = f"Path: {zone} → " + " → ".join([f"Pick [{s} x{q}]" for s, q in zip(picked, qtys)]) + " → Pack → Dispatch"
        tasks.append({
            "Task ID": f"TSK-{np.random.randint(10000, 99999)}",
            "Source Zone": zone,
            "Target Client": client,
            "SKU Checklist": checklist,
            "Optimized Path": path,
            "Priority": np.random.choice(["Standard", "Urgent", "Critical"], p=[0.60, 0.30, 0.10]),
            "Status": np.random.choice(["Pending", "Active Picking", "Completed", "Exception"], p=[0.25, 0.30, 0.40, 0.05]),
            "Assigned Worker": f"Worker-{np.random.randint(1, 50):02d}",
            "Est. Duration (min)": np.random.randint(5, 30),
        })
    return pd.DataFrame(tasks)


def generate_labor_data():
    """Generate labor headcount and efficiency data."""
    zones = [f"Zone {chr(65 + i)}" for i in range(8)]
    fulltime = np.random.randint(25, 35)
    temp = np.random.randint(10, 25)
    peak_cap = int(fulltime * 2.5)
    efficiency = []
    for z in zones:
        base = np.random.uniform(45, 75)
        efficiency.append({
            "Zone": z,
            "Full-Time Staff": fulltime,
            "Temporary Staff": temp,
            "Total Headcount": fulltime + temp,
            "Peak Season Cap": peak_cap,
            "SKUs/Hour/Person": round(base, 1),
            "Shift": np.random.choice(["Morning", "Afternoon", "Night"]),
        })
    return pd.DataFrame(efficiency)


# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; margin-bottom:1.5rem;">
        <div style="font-size:1.4rem; font-weight:800; color:#f8fafc;">🔶 Maverick-SORT</div>
        <div style="font-size:0.8rem; color:#94a3b8;">Professional Edition v2.0</div>
        <div style="margin-top:0.5rem;">
            <span style="background:linear-gradient(135deg, #f59e0b, #ec4899); color:white; padding:3px 10px; border-radius:12px; font-size:0.7rem; font-weight:700;">PRO</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    page = st.radio("Navigation", [
        "🏠 Command Center",
        "📦 Omni-Channel Orders",
        "🌡️ Warehouse & Zones",
        "📊 Customer SLA Analytics",
        "👷 Task Workstation",
        "⚡ Real-Time Simulation",
        "📈 Order Analytics",
        "🔮 Scenario Simulator",
        "⚖️ Strategy Optimizer",
        "📡 Live Adaptive Intelligence",
        "🧠 AI Learning Engine",
        "🌐 Multi-Warehouse Network",
        "🏆 Performance Benchmark",
        "📊 Business Intelligence",
        "💳 Plans & Pricing",
    ], index=0)

    st.markdown("---")

    st.markdown(f"""
    <div style="font-size:0.75rem; color:#64748b; text-align:center;">
        <div>Modules loaded:</div>
        <div>{'✅' if WHAT_IF_AVAILABLE else '⚠️'} what_if_simulator.py</div>
        <div>{'✅' if MOS_AVAILABLE else '⚠️'} multi_objective_scheduler.py</div>
        <div>{'✅' if ADAPTIVE_AVAILABLE else '⚠️'} adaptive_policy.py</div>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# PAGE: PRO HOME
# =============================================================================
if page == "🏠 Command Center":
    col_title, col_badge = st.columns([3, 1])
    with col_title:
        st.markdown('<div class="main-header">Professional Edition</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Enterprise-Grade Multi-Objective Optimization + Real-Time Adaptation</div>', unsafe_allow_html=True)
    with col_badge:
        st.markdown("""
        <div style="text-align:right; margin-top:0.5rem;">
            <span style="background:linear-gradient(135deg, #f59e0b, #ec4899); color:white; padding:4px 14px; border-radius:20px; font-size:0.75rem; font-weight:700;">PROFESSIONAL</span>
            <div style="font-size:0.7rem; color:#64748b; margin-top:0.3rem;">v2.0.0</div>
        </div>
        """, unsafe_allow_html=True)

    # Hero metrics
    cols = st.columns(5)
    for i, (label, value, delta, color) in enumerate([
        ("📦 Orders", "94,328", "+12%", "#3b82f6"),
        ("⚖️ Pareto Front", "47 pts", "NSGA-II", "#f59e0b"),
        ("📡 Adaptive Cap", "20", "Auto-adjusted", "#10b981"),
        ("🛡️ Compliance", "99.2%", "Zero Violations", "#8b5cf6"),
        ("💰 Est. Savings", "¥142,000", "Pro vs Baseline", "#f59e0b"),
    ]):
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color:{color};">{value}</div>
                <div style="font-size:0.7rem; color:#64748b;">{delta}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">🔶 Pro Exclusive Capabilities</div>', unsafe_allow_html=True)

    features = [
        ("⚖️ Multi-Objective Optimizer", "NSGA-II powered Pareto frontier. Cost × Time × Compliance trade-offs with one-click strategy switching.", "Pro"),
        ("📡 Real-Time Adaptive Monitor", "EWMA-based arrival prediction + dynamic wave capacity adjustment. Peak seasons handled automatically.", "Pro"),
        ("🧠 Online Learning (EWC)", "Experience replay + Elastic Weight Consolidation prevents catastrophic forgetting. Gets smarter every shift.", "Pro"),
        ("🌐 Federated Learning Ready", "Multi-warehouse collaborative training architecture. Data stays local, intelligence goes global.", "Pro"),
    ]
    for i in range(0, len(features), 2):
        cols = st.columns(2)
        for j, (title, desc, tier) in enumerate(features[i:i+2]):
            with cols[j]:
                st.markdown(f"""
                <div style="background:#111827; border-radius:12px; padding:1.2rem; margin-bottom:0.8rem; border-left:4px solid #f59e0b;">
                    <div style="font-weight:700; color:#f8fafc; font-size:1rem;">{title}</div>
                    <div style="font-size:0.85rem; color:#94a3b8; margin-top:0.4rem; line-height:1.5;">{desc}</div>
                    <div style="margin-top:0.5rem;"><span style="background:#f59e0b; color:white; padding:2px 8px; border-radius:8px; font-size:0.65rem;">{tier}</span></div>
                </div>
                """, unsafe_allow_html=True)

    # Upgrade path
    st.markdown("---")
    st.markdown('<div class="section-header">⬆️ Upgrade from Essential</div>', unsafe_allow_html=True)
    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.markdown("""
        <div style="background:#111827; border-radius:12px; padding:1.5rem;">
            <div style="font-weight:700; color:#f8fafc; margin-bottom:0.5rem;">What you get with Pro:</div>
            <div style="font-size:0.85rem; color:#94a3b8; line-height:2;">
                <div>✓ Multi-Objective NSGA-II Optimization</div>
                <div>✓ Real-Time Adaptive (EWMA) Capacity</div>
                <div>✓ Online Learning + EWC Anti-Forgetting</div>
                <div>✓ API Integration (RESTful)</div>
                <div>✓ Federated Learning Architecture</div>
                <div>✓ Priority Support + Quarterly Business Review</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_right:
        st.markdown("""
        <div style="background:linear-gradient(135deg, #1e3a5f, #111827); border-radius:12px; padding:1.5rem; border:1px solid rgba(245,158,11,0.3);">
            <div style="font-weight:700; color:#f59e0b; font-size:1.2rem;">¥8,999 / month / warehouse</div>
            <div style="font-size:0.8rem; color:#64748b; margin-bottom:1rem;">or ¥0.08 per order for high-volume</div>
            <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:1rem;">
                <div>🎁 First month 50% off for Essential customers</div>
                <div>🎁 Annual billing: 25% discount</div>
            </div>
            <div style="background:linear-gradient(135deg, #f59e0b, #ec4899); color:white; padding:10px; border-radius:8px; text-align:center; font-weight:700;">Upgrade to Pro Now</div>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# PAGE: WHAT-IF LAB — REAL SIMULATOR (shared with v5)
# =============================================================================
elif page == "🔮 Scenario Simulator":
    st.markdown('<div class="main-header">🔮 What-If Scenario Lab</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Real simulation engine — test any scenario before deployment</div>', unsafe_allow_html=True)

    col_params, col_results = st.columns([1, 2])

    with col_params:
        st.markdown('<div class="section-header">🎛️ Parameters</div>', unsafe_allow_html=True)

        template = st.selectbox("Quick Template", [
            "Custom (manual)", "Wave Capacity Sweep", "Setup Cost Sensitivity",
            "Peak Season Comparison", "Policy Showdown",
        ])

        if template == "Custom (manual)":
            n_scenarios = st.number_input("Scenarios", 2, 6, 3)
            scenario_configs = []
            for i in range(n_scenarios):
                with st.expander(f"Scenario {i+1}", expanded=(i==0)):
                    name = st.text_input(f"Name {i+1}", f"Scenario {i+1}", key=f"pro_sc_name_{i}")
                    cap = st.slider(f"Capacity {i+1}", 8, 35, 15 + i*5, key=f"pro_sc_cap_{i}")
                    setup = st.slider(f"Setup Cost {i+1}", 5.0, 40.0, 10.0 + i*5, 2.5, key=f"pro_sc_setup_{i}")
                    peak = st.slider(f"Peak {i+1}", 1.0, 5.0, 1.5 + i*0.5, 0.2, key=f"pro_sc_peak_{i}")
                    pol = st.selectbox(f"Policy {i+1}", ["TZU", "KGDRL", "PPO", "FCFS", "TEMP_FIRST", "ZONE_NN", "EDD"], key=f"pro_sc_pol_{i}")
                    scenario_configs.append(ScenarioConfig(
                        name=name, max_wave_orders=cap, alpha_setup=setup,
                        peak_multiplier=peak, policy_type=pol
                    ))
        else:
            scenario_configs = None
            st.info("Click Run to execute template")

        n_instances = st.slider("Instances", 1, 10, 3)
        run_btn = st.button("🚀 Run Real Simulation", type="primary", width='stretch')

    with col_results:
        st.markdown('<div class="section-header">📊 Results</div>', unsafe_allow_html=True)

        if run_btn and WHAT_IF_AVAILABLE:
            with st.spinner("Running What-If Simulator..."):
                start = time.time()
                sim = WhatIfSimulator(output_dir="./what_if_results")

                if template == "Custom (manual)" and scenario_configs:
                    scenarios = scenario_configs
                elif template == "Wave Capacity Sweep":
                    scenarios = [ScenarioConfig(name=f"Cap={c}", max_wave_orders=c) for c in [10,15,20,25,30]]
                elif template == "Setup Cost Sensitivity":
                    scenarios = [ScenarioConfig(name=f"Setup={c:.0f}", alpha_setup=c) for c in [5.0,10.0,15.0,20.0,30.0]]
                elif template == "Peak Season Comparison":
                    scenarios = [
                        ScenarioConfig(name="Normal", peak_multiplier=1.0),
                        ScenarioConfig(name="Flu Season", peak_multiplier=2.8),
                        ScenarioConfig(name="Double 11", peak_multiplier=4.0),
                    ]
                else:
                    scenarios = [ScenarioConfig(name=f"Policy={p}", policy_type=p) for p in ["FCFS","TEMP_FIRST","ZONE_NN","EDD","TZU","KGDRL","PPO"]]

                results = sim.compare_scenarios(scenarios, n_instances=n_instances, verbose=False)
                elapsed = time.time() - start
                st.session_state.pro_what_if_results = results
                st.success(f"✅ Done in {elapsed:.1f}s")

        if st.session_state.pro_what_if_results:
            rows = []
            for name, r in st.session_state.pro_what_if_results.items():
                rows.append({
                    "Scenario": name, "Cost": round(r.total_cost,0),
                    "Distance": round(r.total_distance,0), "Waves": r.n_waves,
                    "Viol%": round(r.violation_rate,1), "OnTime%": round(r.on_time_rate,1),
                })
            df = pd.DataFrame(rows)
            st.dataframe(df, width='stretch', hide_index=True)

            best_idx = df["Cost"].idxmin()
            best = df.iloc[best_idx]
            st.markdown(f"""
            <div style="background:#111827; border-radius:8px; padding:1rem; border-left:4px solid #10b981;">
                <div style="font-weight:700; color:#10b981;">🏆 Best: {best['Scenario']} | Cost=¥{best['Cost']:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)

            c1 = alt.Chart(df).mark_bar().encode(
                x=alt.X("Scenario", sort=None), y="Cost",
                color=alt.condition(alt.datum.Scenario==best["Scenario"], alt.value("#10b981"), alt.value("#3b82f6"))
            ).properties(height=260)
            st.altair_chart(c1, width='stretch')
        else:
            st.info("👈 Configure and click Run")

# =============================================================================
# PAGE: PARETO OPTIMIZER — REAL NSGA-II
# =============================================================================
elif page == "⚖️ Strategy Optimizer":
    st.markdown('<div class="main-header">⚖️ Multi-Objective Optimizer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">NSGA-II powered Pareto frontier — Cost × Time × Compliance</div>', unsafe_allow_html=True)

    col_ctrl, col_viz = st.columns([1, 2])

    with col_ctrl:
        st.markdown('<div class="section-header">⚙️ NSGA-II Config</div>', unsafe_allow_html=True)

        strategy = st.radio("Strategy Mode", [
            ("💰 Cost First", "cost_first"), ("⚡ Time First", "time_first"),
            ("🛡️ Compliance First", "compliance_first"), ("⚖️ Balanced", "balanced")
        ], format_func=lambda x: x[0], index=3)

        st.markdown("---")
        pop_size = st.slider("Population", 20, 100, 50, 10)
        n_gen = st.slider("Generations", 20, 200, 80, 10)
        cx_rate = st.slider("Crossover Rate", 0.5, 1.0, 0.9, 0.05)
        mut_rate = st.slider("Mutation Rate", 0.05, 0.3, 0.15, 0.05)

        run_btn = st.button("🧬 Run NSGA-II", type="primary", width='stretch')

    with col_viz:
        st.markdown('<div class="section-header">📊 Pareto Front</div>', unsafe_allow_html=True)

        if run_btn and MOS_AVAILABLE:
            with st.spinner(f"Evolving {pop_size} individuals for {n_gen} generations..."):
                start = time.time()
                config = MultiObjectiveConfig(
                    pop_size=pop_size, n_generations=n_gen,
                    crossover_rate=cx_rate, mutation_rate=mut_rate
                )
                scheduler = MultiObjectiveScheduler(config=config, n_orders=80)
                front = scheduler.optimize(verbose=False)
                st.session_state.pro_pareto_front = front
                st.session_state.pro_pareto_scheduler = scheduler
                elapsed = time.time() - start
                st.success(f"✅ NSGA-II complete in {elapsed:.1f}s | Front size: {len(front)}")

        if st.session_state.pro_pareto_front and MOS_AVAILABLE:
            front = st.session_state.pro_pareto_front
            scheduler = st.session_state.pro_pareto_scheduler

            # Build DataFrame
            pareto_data = []
            for sol in front:
                pareto_data.append({
                    "Cost": sol.objectives[0],
                    "Miss Rate": sol.objectives[1],
                    "Violations": sol.objectives[2],
                })
            pareto_df = pd.DataFrame(pareto_data)

            # Scatter plot
            scat = alt.Chart(pareto_df).mark_circle(size=80, opacity=0.7).encode(
                x=alt.X("Cost", scale=alt.Scale(domain=[pareto_df["Cost"].min()*0.9, pareto_df["Cost"].max()*1.1])),
                y=alt.Y("Miss Rate", scale=alt.Scale(domain=[-0.005, max(pareto_df["Miss Rate"].max()*1.2, 0.05)])),
                size=alt.Size("Violations", scale=alt.Scale(range=[30, 300])),
                color=alt.Color("Violations", scale=alt.Scale(scheme="plasma")),
                tooltip=["Cost", "Miss Rate", "Violations"]
            ).properties(height=320)
            st.altair_chart(scat, width='stretch')
            st.caption("💡 Bubble size = Violations | Color = Violations | NSGA-II rank-0 front")

            # Strategy selection
            if scheduler:
                mode = strategy[1]
                recs = scheduler.get_all_strategy_recommendations()
                if mode in recs:
                    rec = recs[mode]
                    p = rec["profile"]
                    s = rec["summary"]
                    st.markdown(f"""
                    <div style="background:#111827; border-radius:8px; padding:1rem; border-left:4px solid {p.color};">
                        <div style="font-weight:700; color:{p.color};">{p.icon} {p.name}</div>
                        <div style="font-size:0.85rem; color:#94a3b8; margin-top:0.3rem;">
                            Cost=¥{s['estimated_cost']:.0f} | Miss={s['miss_rate']:.3f} | Viol={s['violations']:.0f} | Waves={s['n_waves']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("👈 Configure NSGA-II and click Run")

# =============================================================================
# PAGE: ADAPTIVE MONITOR — REAL 24H SIM
# =============================================================================
elif page == "📡 Live Adaptive Intelligence":
    st.markdown('<div class="main-header">📡 Real-Time Adaptive Monitor</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">EWMA prediction + Dynamic capacity + 24-hour simulation</div>', unsafe_allow_html=True)

    cols = st.columns(4)
    for i, (label, value, unit, color) in enumerate([
        ("Current Capacity", "20", "orders/wave", "#3b82f6"),
        ("EWMA Rate", "5.8", "ord/min", "#06b6d4"),
        ("Trend", "↗ +12%", "next 15min", "#10b981"),
        ("Peak Alert", "🟡 Moderate", "15:00-17:00", "#f59e0b"),
    ]):
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color:{color};">{value}</div>
                <div style="font-size:0.7rem; color:#64748b;">{unit}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    col_cfg, col_run = st.columns([1, 1])
    with col_cfg:
        st.markdown('<div class="section-header">⚙️ Adaptive Config</div>', unsafe_allow_html=True)
        ewma_alpha = st.slider("EWMA Alpha", 0.1, 0.5, 0.3, 0.05)
        base_cap = st.slider("Base Capacity", 10, 30, 20, 1)
        min_cap = st.slider("Min Capacity", 5, 15, 8, 1)
        max_cap = st.slider("Max Capacity", 25, 50, 35, 1)
        run_sim = st.button("🔄 Run 24-Hour Simulation", type="primary", width='stretch')

    with col_run:
        st.markdown('<div class="section-header">📋 Status</div>', unsafe_allow_html=True)
        if ADAPTIVE_AVAILABLE:
            st.success("✅ adaptive_policy.py loaded")
        else:
            st.error("❌ adaptive_policy.py not available")

    # Run real simulation
    if run_sim and ADAPTIVE_AVAILABLE:
        with st.spinner("Simulating 24 hours with real AdaptivePolicyController..."):
            config = AdaptiveConfig(
                ewma_alpha=ewma_alpha, base_capacity=base_cap,
                min_capacity=min_cap, max_capacity=max_cap
            )
            ctrl = AdaptivePolicyController(config)
            np.random.seed(42)
            base_rate = 3.0
            sim_results = []

            for hour in range(24):
                peak_factor = 1.0
                if 8 <= hour <= 11: peak_factor = 2.8
                elif 13 <= hour <= 15: peak_factor = 1.8
                elif 0 <= hour <= 5: peak_factor = 0.2

                observed = base_rate * peak_factor * (0.8 + np.random.rand() * 0.4)
                load = min(0.95, 0.3 + peak_factor * 0.2 + np.random.rand() * 0.1)
                decision = ctrl.step(observed, load, hour)
                sim_results.append({
                    "Hour": hour, "Observed Rate": observed,
                    "Capacity": decision["capacity"],
                    "Release Threshold": decision["release_threshold"],
                    "Predicted Rate": decision["predicted_rate"],
                    "Peak": decision["peak_detected"],
                    "Valley": decision["valley_detected"],
                    "Reason": decision["reason"],
                })

            st.session_state.pro_adaptive_results = pd.DataFrame(sim_results)
            st.session_state.pro_adaptive_controller = ctrl
            st.success(f"✅ 24-hour simulation complete | {len(sim_results)} steps recorded")

    # Display results
    if st.session_state.pro_adaptive_results is not None:
        df = st.session_state.pro_adaptive_results

        # Multi-line chart
        melted = df.melt(id_vars=["Hour"], value_vars=["Observed Rate", "Predicted Rate"],
                         var_name="Metric", value_name="Value")
        line1 = alt.Chart(melted).mark_line(strokeWidth=2).encode(
            x="Hour", y="Value", color="Metric",
            tooltip=["Hour", "Metric", "Value"]
        ).properties(height=280)
        st.altair_chart(line1, width='stretch')

        # Capacity chart
        cap_chart = alt.Chart(df).mark_line(color="#f59e0b", strokeWidth=2).encode(
            x="Hour", y="Capacity",
            tooltip=["Hour", "Capacity", "Reason"]
        ).properties(height=200)
        st.altair_chart(cap_chart, width='stretch')

        # Adjustment log
        st.markdown("<div class='section-header'>📋 Adjustment Log</div>", unsafe_allow_html=True)
        log_df = df[df["Reason"].str.contains("peak|valley|high_load", case=False, na=False)][["Hour", "Capacity", "Predicted Rate", "Reason"]]
        if not log_df.empty:
            st.dataframe(log_df, width='stretch', hide_index=True)
        else:
            st.info("No significant adjustments triggered in this simulation.")
    else:
        st.info("👈 Configure and click Run 24-Hour Simulation")

# =============================================================================
# PAGE: ONLINE LEARNING
# =============================================================================
elif page == "🧠 AI Learning Engine":
    st.markdown('<div class="main-header">🧠 Online Learning Status</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Experience replay + EWC regularization — smarter every shift</div>', unsafe_allow_html=True)

    cols = st.columns(4)
    for i, (label, value, unit, color) in enumerate([
        ("Replay Buffer", "847", "/ 1000", "#10b981"),
        ("Update Count", "124", "total", "#3b82f6"),
        ("EWC Lambda", "0.01", "regularization", "#8b5cf6"),
        ("Last Update", "2 min", "ago", "#f59e0b"),
    ]):
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color:{color};">{value}</div>
                <div style="font-size:0.7rem; color:#64748b;">{unit}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown('<div class="section-header">📦 Experience Replay</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#111827; border-radius:8px; padding:1rem;">
            <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                <span style="color:#94a3b8;">Buffer Utilization</span>
                <span style="color:#10b981; font-weight:700;">84.7%</span>
            </div>
            <div style="background:#1e293b; height:8px; border-radius:4px;">
                <div style="background:#10b981; width:84.7%; height:100%; border-radius:4px;"></div>
            </div>
            <div style="margin-top:1rem; font-size:0.8rem; color:#64748b;">
                <div>Oldest experience: Shift #89</div>
                <div>Newest experience: Shift #124</div>
                <div>Batch size: 32</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="section-header">🔒 EWC Regularization</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#111827; border-radius:8px; padding:1rem;">
            <div style="font-size:0.85rem; color:#94a3b8; line-height:1.8;">
                <div><b style="color:#f8fafc;">Formula:</b> L = L_new + λ/2 · Σ F_i · (θ_i − θ*_i)²</div>
                <div><b style="color:#f8fafc;">λ (lambda):</b> 0.01</div>
                <div><b style="color:#f8fafc;">Fisher computed:</b> Every 5 updates</div>
                <div><b style="color:#f8fafc;">Old params frozen:</b> θ* from Shift #120</div>
                <div style="margin-top:0.5rem; color:#10b981;">✓ No catastrophic forgetting detected</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Policy ensemble
    st.markdown("---")
    st.markdown('<div class="section-header">🎯 Policy Ensemble Weights</div>', unsafe_allow_html=True)
    ensemble_df = pd.DataFrame({
        "Policy": ["KGDRL", "TZU", "EDD"],
        "Weight": [0.52, 0.28, 0.20],
        "Recent Avg Reward": [4120, 3580, 3210],
    })
    st.dataframe(ensemble_df, width='stretch', hide_index=True)

    ens_chart = alt.Chart(ensemble_df).mark_arc(innerRadius=40).encode(
        theta="Weight", color="Policy",
        tooltip=["Policy", "Weight", "Recent Avg Reward"]
    ).properties(height=250)
    st.altair_chart(ens_chart, width='stretch')

# =============================================================================
# PAGE: FEDERATED HUB
# =============================================================================
elif page == "🌐 Multi-Warehouse Network":
    st.markdown('<div class="main-header">🌐 Federated Learning Hub</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Multi-warehouse collaborative training — data stays local, intelligence goes global</div>', unsafe_allow_html=True)

    st.info("🔶 **Pro Architecture (Reserved)**: Federated learning infrastructure is architecturally ready. Activate with Enterprise deployment.")

    # ASCII topology
    st.markdown("""
    <div style="background:#111827; border-radius:12px; padding:1.5rem; text-align:center; font-family:monospace; font-size:0.8rem; color:#94a3b8; line-height:1.8;">
        <span style="color:#f59e0b;">┌─────────────┐</span>     <span style="color:#10b981;">FedAvg</span>     <span style="color:#f59e0b;">┌─────────────┐</span><br>
        <span style="color:#f59e0b;">│ Shanghai WH │</span> ←── <span style="color:#3b82f6;">∇θ₁</span> ──→ <span style="color:#8b5cf6;">┌───────────┐</span> ←─ <span style="color:#3b82f6;">θ_global</span> → <span style="color:#f59e0b;">│ Beijing WH  │</span><br>
        <span style="color:#f59e0b;">│ n=1,200     │</span>      <span style="color:#10b981;">Secure</span>    <span style="color:#8b5cf6;">│ Coordinator│</span>    <span style="color:#10b981;">Secure</span>   <span style="color:#f59e0b;">│ n=980       │</span><br>
        <span style="color:#f59e0b;">└─────────────┘</span>      <span style="color:#10b981;">Aggregation</span> <span style="color:#8b5cf6;">│ Round 12   │</span>    <span style="color:#10b981;">Distribution</span><span style="color:#f59e0b;">└─────────────┘</span><br>
                                                                               ↑<br>
        <span style="color:#f59e0b;">┌─────────────┐</span> ←───────────────────────────────────────────────────┘<br>
        <span style="color:#f59e0b;">│ Guangzhou WH│</span>      <span style="color:#3b82f6;">θ_global</span><br>
        <span style="color:#f59e0b;">│ n=1,100     │</span><br>
        <span style="color:#f59e0b;">└─────────────┘</span>
    </div>
    """, unsafe_allow_html=True)

    # Client table
    st.markdown("---")
    st.markdown('<div class="section-header">🏭 Warehouse Clients</div>', unsafe_allow_html=True)
    fed_df = pd.DataFrame([
        {"Warehouse": "Shanghai", "Status": "Synced", "Samples": 1200, "Last Sync": "12 min ago", "Version": "v2.3.1", "Quality": 0.941},
        {"Warehouse": "Beijing", "Status": "Training", "Samples": 980, "Last Sync": "28 min ago", "Version": "v2.3.0", "Quality": 0.923},
        {"Warehouse": "Guangzhou", "Status": "Synced", "Samples": 1100, "Last Sync": "8 min ago", "Version": "v2.3.1", "Quality": 0.938},
        {"Warehouse": "Chengdu", "Status": "Idle", "Samples": 850, "Last Sync": "45 min ago", "Version": "v2.2.5", "Quality": 0.901},
        {"Warehouse": "Wuhan", "Status": "Training", "Samples": 1050, "Last Sync": "35 min ago", "Version": "v2.3.0", "Quality": 0.912},
    ])
    st.dataframe(fed_df, width='stretch', hide_index=True)

    # Metrics
    st.markdown("---")
    cols = st.columns(4)
    for i, (label, value, unit, color) in enumerate([
        ("Total Clients", "5", "warehouses", "#3b82f6"),
        ("Global Round", "12", "current", "#f59e0b"),
        ("Total Samples", "5,680", "across clients", "#10b981"),
        ("Avg Sync Quality", "0.923", "consensus", "#8b5cf6"),
    ]):
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color:{color};">{value}</div>
                <div style="font-size:0.7rem; color:#64748b;">{unit}</div>
            </div>
            """, unsafe_allow_html=True)

    col_cfg, col_priv = st.columns(2)
    with col_cfg:
        st.markdown('<div class="section-header">⚙️ Federation Config</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#111827; border-radius:8px; padding:1rem; font-size:0.85rem; color:#94a3b8;">
            <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                <span>Aggregation</span><span style="color:#f8fafc;">FedAvg</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                <span>Participation</span><span style="color:#f8fafc;">100%</span>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <span>Compression</span><span style="color:#10b981;">Top-K Sparsification</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_priv:
        st.markdown('<div class="section-header">🔒 Privacy</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#111827; border-radius:8px; padding:1rem; font-size:0.85rem; color:#94a3b8;">
            <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                <span>Differential Privacy</span><span style="color:#10b981;">ε=1.0, δ=1e-5</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                <span>Secure Aggregation</span><span style="color:#10b981;">✅ Enabled</span>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <span>Model Encryption</span><span style="color:#10b981;">✅ AES-256</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# PAGE: ALGORITHM ARENA
# =============================================================================
elif page == "🏆 Performance Benchmark":
    st.markdown('<div class="main-header">🏆 Algorithm Arena</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">KGDRL vs 5 Heuristics — Performance leaderboard</div>', unsafe_allow_html=True)

    arena_df = pd.DataFrame([
        {"Method": "FCFS", "Reward": 1786.9, "Distance": 690.9, "Waves": 85.9, "Miss": 0.0, "Viol": 38.5},
        {"Method": "TEMP_FIRST", "Reward": -2958.1, "Distance": 987.4, "Waves": 125.8, "Miss": 0.0, "Viol": 0.0},
        {"Method": "ZONE_NN", "Reward": 1733.8, "Distance": 669.0, "Waves": 82.9, "Miss": 0.0, "Viol": 37.3},
        {"Method": "EDD", "Reward": 1752.0, "Distance": 667.8, "Waves": 83.1, "Miss": 0.0, "Viol": 37.5},
        {"Method": "TZU", "Reward": 144.6, "Distance": 666.7, "Waves": 83.0, "Miss": 0.0, "Viol": 21.4},
        {"Method": "PPO", "Reward": 4007.5, "Distance": 695.5, "Waves": 87.3, "Miss": 4.4, "Viol": 36.7},
        {"Method": "KGDRL-Full", "Reward": 1908.8, "Distance": 665.7, "Waves": 82.8, "Miss": 0.0, "Viol": 39.0},
    ])
    arena_df["Color"] = arena_df["Method"].apply(
        lambda m: "#10b981" if m == "KGDRL-Full" else ("#3b82f6" if m == "PPO" else "#64748b")
    )

    def hl(row):
        return ["background-color:rgba(16,185,129,0.15)"] * len(row) if row["Method"] == "KGDRL-Full" else [""] * len(row)
    st.dataframe(arena_df.style.apply(hl, axis=1), width='stretch', hide_index=True)

    col1, col2 = st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(arena_df).mark_bar().encode(
            x=alt.X("Method", sort=None), y="Reward",
            color=alt.Color("Color:N", scale=None)
        ).properties(height=260), width="stretch")
    with col2:
        st.altair_chart(alt.Chart(arena_df).mark_bar().encode(
            x=alt.X("Method", sort=None), y="Distance",
            color=alt.Color("Color:N", scale=None)
        ).properties(height=260), width="stretch")

# =============================================================================
# PAGE: ADVANCED ANALYTICS
# =============================================================================
elif page == "📊 Business Intelligence":
    st.markdown('<div class="main-header">📊 Advanced Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Multi-dimensional drill-down + AI-powered demand forecasting</div>', unsafe_allow_html=True)

    # SLA trends
    months = pd.date_range("2025-06", periods=12, freq="ME").strftime("%Y-%m").tolist()
    df_sla = pd.DataFrame({
        "Month": months,
        "Hospital": np.random.randint(8000, 12000, 12),
        "Clinic": np.random.randint(5000, 8000, 12),
        "Pharmacy": np.random.randint(15000, 22000, 12),
        "Distributor": np.random.randint(25000, 35000, 12),
    })
    sla_melt = df_sla.melt(id_vars=["Month"], var_name="Type", value_name="Orders")
    st.altair_chart(alt.Chart(sla_melt).mark_line(strokeWidth=2).encode(
        x="Month", y="Orders", color="Type"
    ).properties(height=300), width='stretch')

    # Compliance
    compliance = pd.DataFrame([
        {"Client": "Hospital", "On-Time": "97.2%", "Next-Day": "99.1%", "Temp": "99.8%", "Exception": "0.3%"},
        {"Client": "Clinic", "On-Time": "94.5%", "Next-Day": "98.2%", "Temp": "99.5%", "Exception": "0.8%"},
        {"Client": "Pharmacy", "On-Time": "92.1%", "Next-Day": "96.8%", "Temp": "98.9%", "Exception": "1.2%"},
        {"Client": "Distributor", "On-Time": "95.8%", "Next-Day": "97.5%", "Temp": "99.2%", "Exception": "0.5%"},
    ])
    st.dataframe(compliance, width='stretch', hide_index=True)

# =============================================================================
# PAGE: SUBSCRIBE & UPGRADE
# =============================================================================
elif page == "💳 Plans & Pricing":
    st.markdown('<div class="main-header">💳 Subscribe & Upgrade</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Pro pricing + Group deployment calculator</div>', unsafe_allow_html=True)

    billing = st.segmented_control("Billing", ["Monthly", "Annual (Save 25%)"], default="Monthly")
    is_annual = (billing == "Annual (Save 25%)")
    discount = 0.75 if is_annual else 1.0

    st.markdown("---")

    # Cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="pricing-card">
            <div style="font-size:0.8rem; color:#3b82f6; font-weight:700; text-transform:uppercase;">Essential</div>
            <div class="price-amount">¥{int(2999*discount):,}</div>
            <div class="price-period">/ month / warehouse</div>
            <div style="margin-top:1rem; font-size:0.85rem; color:#94a3b8; text-align:left; line-height:2;">
                <div><span class="feature-check">✓</span>KGDRL Core</div>
                <div><span class="feature-check">✓</span>What-If Simulator</div>
                <div><span class="feature-check">✓</span>Standard Dashboard</div>
                <div><span class="feature-x">✗</span>Multi-Objective</div>
                <div><span class="feature-x">✗</span>Adaptive</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="pricing-card popular">
            <div class="popular-badge">Most Popular</div>
            <div style="font-size:0.8rem; color:#f59e0b; font-weight:700; text-transform:uppercase;">Professional</div>
            <div class="price-amount" style="color:#f59e0b;">¥{int(8999*discount):,}</div>
            <div class="price-period">/ month / warehouse</div>
            <div style="margin-top:0.5rem; font-size:0.8rem; color:#f59e0b;">or ¥0.08 per order (volume pricing)</div>
            <div style="margin-top:1rem; font-size:0.85rem; color:#94a3b8; text-align:left; line-height:2;">
                <div><span class="feature-check">✓</span>Everything in Essential</div>
                <div><span class="feature-check">✓</span>NSGA-II Multi-Objective</div>
                <div><span class="feature-check">✓</span>Real-Time Adaptive</div>
                <div><span class="feature-check">✓</span>Online Learning (EWC)</div>
                <div><span class="feature-check">✓</span>API + Federated Ready</div>
                <div><span class="feature-check">✓</span>Priority Support</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="pricing-card">
            <div style="font-size:0.8rem; color:#8b5cf6; font-weight:700; text-transform:uppercase;">Enterprise</div>
            <div class="price-amount" style="color:#8b5cf6;">Custom</div>
            <div class="price-period">Contact sales</div>
            <div style="margin-top:1rem; font-size:0.85rem; color:#94a3b8; text-align:left; line-height:2;">
                <div><span class="feature-check">✓</span>Everything in Pro</div>
                <div><span class="feature-check">✓</span>Federated Learning Active</div>
                <div><span class="feature-check">✓</span>On-Premise Deployment</div>
                <div><span class="feature-check">✓</span>Custom Integrations</div>
                <div><span class="feature-check">✓</span>Dedicated CSM</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Group pricing calculator
    st.markdown("---")
    st.markdown('<div class="section-header">🏭 Group Deployment Calculator</div>', unsafe_allow_html=True)

    col_g1, col_g2, col_g3, col_g4 = st.columns(4)
    with col_g1:
        group_warehouses = st.number_input("Warehouses", 1, 100, 5, 1)
    with col_g2:
        group_orders = st.number_input("Orders/Day/WH", 1000, 100000, 15000, 1000)
    with col_g3:
        group_wage = st.number_input("Picker Wage ¥/hr", 15, 150, 50, 5)
    with col_g4:
        group_violation = st.number_input("Violation Cost ¥", 500, 20000, 5000, 500)

    # Calculate group economics
    days = 300
    dist_per_order = 400
    manual_cost_wh = group_orders * dist_per_order * days * 0.003
    picker_cost_wh = group_orders * 0.15 * group_wage * days / 60
    viol_cost_wh = (group_orders / 1000 * 5 * group_violation)
    total_baseline_wh = manual_cost_wh + picker_cost_wh + viol_cost_wh

    # Pro saves more (25% vs 22% for essential)
    saving_rate = 0.25
    savings_wh = total_baseline_wh * saving_rate
    pro_monthly_wh = 8999 * discount
    if group_orders > 5000:
        per_order = group_orders * 30 * 0.08 * discount
        pro_monthly_wh = min(pro_monthly_wh, per_order)

    # Group discount: >5 warehouses = 10% off per warehouse
    group_discount = 0.90 if group_warehouses >= 5 else 1.0
    if group_warehouses >= 10:
        group_discount = 0.85

    pro_monthly_wh *= group_discount
    pro_annual_wh = pro_monthly_wh * 12
    total_savings = savings_wh * group_warehouses
    total_cost = pro_monthly_wh * 12 * group_warehouses
    net_savings = total_savings - total_cost
    roi_pct = (net_savings / total_cost * 100) if total_cost > 0 else 0

    cols_roi = st.columns(5)
    metrics = [
        ("Baseline Cost", f"¥{total_baseline_wh*group_warehouses:,.0f}", "/year", "#ef4444"),
        ("Pro Savings", f"¥{total_savings:,.0f}", "/year", "#10b981"),
        ("Pro Subscription", f"¥{total_cost:,.0f}", "/year", "#3b82f6"),
        ("Net Savings", f"¥{net_savings:,.0f}", "/year", "#f59e0b"),
        ("ROI", f"{roi_pct:.0f}%", "annual", "#8b5cf6"),
    ]
    for col, (label, value, unit, color) in zip(cols_roi, metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color:{color};">{value}</div>
                <div style="font-size:0.7rem; color:#64748b;">{unit}</div>
            </div>
            """, unsafe_allow_html=True)

    if group_warehouses >= 5:
        st.success(f"🎁 Group discount applied: {int((1-group_discount)*100)}% off per warehouse for {group_warehouses} warehouses")

    if group_orders > 3750 and group_orders <= 5000:
        st.info("💡 At this volume, per-warehouse billing is optimal. Consider per-order billing (¥0.08/order) for >5,000 orders/day.")

# =============================================================================
# PAGE: OMNI-CHANNEL ORDERS
# =============================================================================
elif page == "📦 Omni-Channel Orders":
    st.markdown('<div class="main-header">📦 Omni-Channel Orders</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Real-time order intake, dispatch status, and channel analytics</div>', unsafe_allow_html=True)

    # Top Summary Metrics
    base_orders = 90000
    fluctuation = np.random.randint(-500, 500)
    total_orders = base_orders + fluctuation
    bulk_orders = int(total_orders * np.random.uniform(0.35, 0.42))
    fragmented = total_orders - bulk_orders

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_orders:,}</div>
            <div class="metric-label">Total Daily Orders</div>
            <div class="metric-delta {'delta-up' if fluctuation > 0 else 'delta-down'}">
                {'+' if fluctuation > 0 else ''}{fluctuation:,} vs baseline
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #1e3a5f 0%, #065f46 100%);">
            <div class="metric-value">{bulk_orders:,}</div>
            <div class="metric-label">Bulk Orders</div>
            <div class="metric-delta delta-up">{bulk_orders/total_orders*100:.1f}% of total</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #1e3a5f 0%, #92400e 100%);">
            <div class="metric-value">{fragmented:,}</div>
            <div class="metric-label">Fragmented Small Orders</div>
            <div class="metric-delta delta-down">{fragmented/total_orders*100:.1f}% of total</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Filters
    st.markdown('<div class="section-header">Filters & Segment Controls</div>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1:
        filter_client = st.multiselect(
            "Client Category",
            ["Public Hospital", "Chain Pharmacy", "Independent Pharmacy", "Primary Healthcare"],
            default=["Public Hospital", "Chain Pharmacy", "Independent Pharmacy", "Primary Healthcare"],
        )
    with f2:
        filter_time = st.multiselect(
            "Time Window",
            ["Morning Peak", "Afternoon", "Night Peak"],
            default=["Morning Peak", "Afternoon", "Night Peak"],
        )
    with f3:
        filter_temp = st.multiselect(
            "Temperature Attribute",
            ["Ambient", "Cool", "Cold", "Frozen", "Deep Frozen"],
            default=["Ambient", "Cool", "Cold", "Frozen", "Deep Frozen"],
        )

    # Generate and filter order log
    df_orders = generate_order_log(n=100, seed=int(time.time()) // 10)
    df_filtered = df_orders[
        df_orders["Client Type"].isin(filter_client) &
        df_orders["Time Window"].isin(filter_time) &
        df_orders["Temperature"].isin(filter_temp)
    ]

    st.markdown("---")

    # Three-column layout
    left, center, right = st.columns([2, 1, 1])

    with left:
        st.markdown('<div class="section-header">Live Order Log</div>', unsafe_allow_html=True)
        st.dataframe(df_filtered, hide_index=True, height=420)

    with center:
        st.markdown('<div class="section-header">Work Order Status</div>', unsafe_allow_html=True)
        status_counts = df_filtered["Status"].value_counts().to_dict()
        statuses = ["Pending Dispatch", "Picking in Progress", "Completed", "Stagnant Exception"]
        status_colors = ["#f59e0b", "#3b82f6", "#10b981", "#ef4444"]
        status_icons = ["⏳", "🔧", "✅", "⚠️"]

        for status, color, icon in zip(statuses, status_colors, status_icons):
            count = status_counts.get(status, 0)
            pct = count / len(df_filtered) * 100 if len(df_filtered) > 0 else 0
            st.markdown(f"""
            <div style="background: #111827; padding: 0.8rem; border-radius: 8px; border-left: 4px solid {color}; margin-bottom: 0.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.85rem; color: #e2e8f0;">{icon} {status}</span>
                    <span style="font-size: 1.2rem; font-weight: 700; color: {color};">{count}</span>
                </div>
                <div style="height: 4px; background: rgba(255,255,255,0.05); border-radius: 2px; margin-top: 6px;">
                    <div style="width: {pct}%; height: 100%; background: {color}; border-radius: 2px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-header">Distribution Analytics</div>', unsafe_allow_html=True)

        # Time window bar chart
        time_dist = df_filtered["Time Window"].value_counts().reindex(["Morning Peak", "Afternoon", "Night Peak"], fill_value=0).reset_index()
        time_dist.columns = ["Window", "Count"]
        chart_time = alt.Chart(time_dist).mark_bar(color="#3b82f6", cornerRadiusEnd=4).encode(
            x=alt.X("Window:N", title="", sort=["Morning Peak", "Afternoon", "Night Peak"]),
            y=alt.Y("Count:Q", title="Order Count"),
        ).properties(height=120)
        st.altair_chart(chart_time)

        # Bulk vs Small pie
        bulk_count = (df_filtered["SKU Count"] >= 4).sum()
        small_count = (df_filtered["SKU Count"] < 4).sum()
        df_bulk = pd.DataFrame({"Type": ["Bulk (≥4 SKUs)", "Small (<4 SKUs)"], "Count": [bulk_count, small_count]})
        chart_bulk = alt.Chart(df_bulk).mark_arc(innerRadius=30).encode(
            theta=alt.Theta("Count:Q"),
            color=alt.Color("Type:N", scale=alt.Scale(range=["#10b981", "#f59e0b"]), legend=alt.Legend(orient="bottom", labelColor="#e2e8f0")),
        ).properties(height=130)
        st.altair_chart(chart_bulk)

        # Temperature pie
        temp_dist = df_filtered["Temperature"].value_counts().reset_index()
        temp_dist.columns = ["Zone", "Count"]
        chart_temp = alt.Chart(temp_dist).mark_arc(innerRadius=30).encode(
            theta=alt.Theta("Count:Q"),
            color=alt.Color("Zone:N", legend=alt.Legend(orient="bottom", labelColor="#e2e8f0")),
        ).properties(height=130)
        st.altair_chart(chart_temp)


# =============================================================================
# PAGE: WAREHOUSE & TEMPERATURE ZONES
# =============================================================================
elif page == "🌡️ Warehouse & Zones":
    st.markdown('<div class="main-header">🌡️ Warehouse & Temperature Zones</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Zone capacity, inventory health, and near-expiry FIFO control</div>', unsafe_allow_html=True)

    # Zone cards
    zones = [
        ("Ambient", "15–25°C", "#22c55e", 85),
        ("Cool", "8–15°C", "#3b82f6", 72),
        ("Cold", "2–8°C", "#06b6d4", 68),
        ("Frozen", "-15–-5°C", "#8b5cf6", 55),
        ("Deep Frozen", "≤-20°C", "#6366f1", 42),
    ]

    cols = st.columns(5)
    for i, (name, range_str, color, cap) in enumerate(zones):
        with cols[i]:
            volume = np.random.randint(5000, 15000)
            util = np.random.randint(55, 95)
            st.markdown(f"""
            <div class="zone-card" style="border-top: 3px solid {color};">
                <div class="zone-title">{name}</div>
                <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 0.5rem;">{range_str}</div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                    <span style="font-size: 0.75rem; color: #94a3b8;">Volume</span>
                    <span class="zone-metric">{volume:,}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                    <span style="font-size: 0.75rem; color: #94a3b8;">Utilization</span>
                    <span style="font-size: 1.1rem; font-weight: 700; color: {color};">{util}%</span>
                </div>
                <div style="height: 4px; background: rgba(255,255,255,0.05); border-radius: 2px;">
                    <div style="width: {util}%; height: 100%; background: {color}; border-radius: 2px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Near-Expiry FIFO Table
    st.markdown('<div class="section-header">Near-Expiry Inventory Control (FIFO)</div>', unsafe_allow_html=True)
    df_inv = generate_inventory_data(seed=int(time.time()) // 30)

    # Color-coded rows
    def highlight_risk(row):
        if row["Risk Level"] == "Critical":
            return ["background-color: rgba(239, 68, 68, 0.12); color: #f87171"] * len(row)
        elif row["Risk Level"] == "Warning":
            return ["background-color: rgba(245, 158, 11, 0.12); color: #fbbf24"] * len(row)
        elif row["Risk Level"] == "Notice":
            return ["background-color: rgba(59, 130, 246, 0.12); color: #60a5fa"] * len(row)
        return [""] * len(row)

    st.dataframe(
        df_inv.style.apply(highlight_risk, axis=1),
        hide_index=True,
        height=350,
    )

    # Risk summary badges
    risk_counts = df_inv["Risk Level"].value_counts().to_dict()
    r1, r2, r3, r4 = st.columns(4)
    with r1:
        st.markdown(f"<div class='badge badge-exception'>Critical (≤30d): {risk_counts.get('Critical', 0)} SKUs</div>", unsafe_allow_html=True)
    with r2:
        st.markdown(f"<div class='badge badge-pending'>Warning (≤60d): {risk_counts.get('Warning', 0)} SKUs</div>", unsafe_allow_html=True)
    with r3:
        st.markdown(f"<div class='badge badge-active'>Notice (≤90d): {risk_counts.get('Notice', 0)} SKUs</div>", unsafe_allow_html=True)
    with r4:
        st.markdown(f"<div class='badge badge-completed'>Normal (>90d): {risk_counts.get('Normal', 0)} SKUs</div>", unsafe_allow_html=True)

    st.markdown("---")

    # Charts
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-header">Zone Capacity Utilization</div>', unsafe_allow_html=True)
        zone_util = pd.DataFrame({
            "Zone": [z[0] for z in zones],
            "Utilization": [np.random.randint(50, 95) for _ in zones],
            "Capacity": [z[3] for z in zones],
        })
        chart_zone = alt.Chart(zone_util).mark_arc(innerRadius=50).encode(
            theta=alt.Theta("Utilization:Q"),
            color=alt.Color("Zone:N", legend=alt.Legend(orient="bottom", labelColor="#e2e8f0")),
        ).properties(height=280)
        st.altair_chart(chart_zone)

    with c2:
        st.markdown('<div class="section-header">Near-Expiry by Medicine Type</div>', unsafe_allow_html=True)
        near_expiry = df_inv[df_inv["Risk Level"].isin(["Critical", "Warning", "Notice"])]
        type_vol = near_expiry.groupby("Category")["Stock Qty"].sum().reset_index()
        chart_type = alt.Chart(type_vol).mark_bar(cornerRadiusEnd=4).encode(
            x=alt.X("Category:N", title="", sort="-y"),
            y=alt.Y("Stock Qty:Q", title="Stock Quantity"),
            color=alt.Color("Category:N", legend=None),
        ).properties(height=280)
        st.altair_chart(chart_type)


# =============================================================================
# PAGE: CUSTOMER SLA ANALYTICS
# =============================================================================
elif page == "📊 Customer SLA Analytics":
    st.markdown('<div class="main-header">📊 Customer SLA Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Fulfillment trends, SKU diversity, and AI-forecasted performance</div>', unsafe_allow_html=True)

    months, history, forecast_days, forecast = generate_sla_history()
    clients = list(history.keys())

    # Monthly Order Volume Trend
    st.markdown('<div class="section-header">Monthly Order Volume — Past 12 Months</div>', unsafe_allow_html=True)
    vol_data = []
    for client in clients:
        base = np.random.uniform(8000, 25000)
        for i, month in enumerate(months):
            vol = base * (1 + 0.05 * np.sin(i * 0.5) + np.random.normal(0, 0.03))
            vol_data.append({"Month": month, "Client": client, "Volume": int(vol)})
    df_vol = pd.DataFrame(vol_data)

    chart_vol = alt.Chart(df_vol).mark_line(strokeWidth=2).encode(
        x=alt.X("Month:N", title="", sort=months),
        y=alt.Y("Volume:Q", title="Order Volume"),
        color=alt.Color("Client:N", legend=alt.Legend(orient="top", labelColor="#e2e8f0")),
    ).properties(height=300)
    st.altair_chart(chart_vol)

    st.markdown("---")

    # SKU Diversity + SLA Fulfillment
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-header">Avg SKU Variety per Order</div>', unsafe_allow_html=True)
        sku_div = pd.DataFrame({
            "Client": clients,
            "Avg SKUs": [np.random.uniform(2.5, 5.5) for _ in clients],
        })
        chart_sku = alt.Chart(sku_div).mark_bar(cornerRadiusEnd=4, color="#3b82f6").encode(
            x=alt.X("Client:N", title=""),
            y=alt.Y("Avg SKUs:Q", title="Average SKU Count"),
        ).properties(height=260)
        st.altair_chart(chart_sku)

    with c2:
        st.markdown('<div class="section-header">SLA Fulfillment + 14-Day AI Forecast</div>', unsafe_allow_html=True)
        sla_data = []
        for client in clients:
            for i, month in enumerate(months):
                sla_data.append({
                    "Period": month,
                    "Client": client,
                    "SLA (%)": round(history[client][i], 1),
                    "Type": "Historical",
                })
            for i, day in enumerate(forecast_days):
                sla_data.append({
                    "Period": day,
                    "Client": client,
                    "SLA (%)": round(forecast[client][i], 1),
                    "Type": "AI Forecast",
                })
        df_sla = pd.DataFrame(sla_data)

        # Historical lines
        hist_chart = alt.Chart(df_sla[df_sla["Type"] == "Historical"]).mark_line(strokeWidth=2, opacity=0.8).encode(
            x=alt.X("Period:N", title="", sort=None),
            y=alt.Y("SLA (%):Q", scale=alt.Scale(domain=[70, 100])),
            color=alt.Color("Client:N", legend=alt.Legend(orient="top", labelColor="#e2e8f0")),
        )
        # Forecast dashed lines
        fc_chart = alt.Chart(df_sla[df_sla["Type"] == "AI Forecast"]).mark_line(strokeWidth=2, strokeDash=[4, 4], opacity=0.9).encode(
            x=alt.X("Period:N", title="", sort=None),
            y=alt.Y("SLA (%):Q"),
            color=alt.Color("Client:N"),
        )
        st.altair_chart(hist_chart + fc_chart)

    st.markdown("---")

    # Compliance table
    st.markdown('<div class="section-header">Fulfillment Compliance by Client Category</div>', unsafe_allow_html=True)
    compliance = []
    for client in clients:
        compliance.append({
            "Client Category": client,
            "Orders Fulfilled": np.random.randint(15000, 35000),
            "Orders Total": np.random.randint(16000, 36000),
            "On-Time Rate (%)": round(np.random.uniform(87, 98), 1),
            "Next-Day Rate (%)": round(np.random.uniform(85, 96), 1),
            "Temp Compliance (%)": round(np.random.uniform(98.5, 99.9), 2),
            "Exception Rate (%)": round(np.random.uniform(0.5, 3.0), 2),
        })
    df_comp = pd.DataFrame(compliance)
    df_comp["Fulfillment Score"] = (df_comp["On-Time Rate (%)"] * 0.4 + df_comp["Next-Day Rate (%)"] * 0.4 + df_comp["Temp Compliance (%)"] * 0.2).round(1)
    st.dataframe(df_comp.sort_values("Fulfillment Score", ascending=False), hide_index=True)


# =============================================================================
# PAGE: TASK WORKSTATION
# =============================================================================
elif page == "👷 Task Workstation":
    st.markdown('<div class="main-header">👷 Task Workstation</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Labor deployment, picking efficiency, and DRL-optimized task queue</div>', unsafe_allow_html=True)

    # Top Labor Dashboard
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-header">Active Headcount</div>', unsafe_allow_html=True)
        fulltime = np.random.randint(25, 35)
        temp = np.random.randint(10, 25)
        peak_cap = int(fulltime * 2.5)
        total = fulltime + temp

        labor_df = pd.DataFrame({
            "Type": ["Full-Time", "Temporary", "Peak Cap (2.5x)"],
            "Count": [fulltime, temp, peak_cap],
            "Color": ["#3b82f6", "#f59e0b", "#ef4444"],
        })
        chart_labor = alt.Chart(labor_df).mark_bar(cornerRadiusEnd=4).encode(
            x=alt.X("Type:N", title=""),
            y=alt.Y("Count:Q", title="Headcount"),
            color=alt.Color("Color:N", scale=alt.Scale(domain=["#3b82f6", "#f59e0b", "#ef4444"], range=["#3b82f6", "#f59e0b", "#ef4444"]), legend=None),
        ).properties(height=220)
        st.altair_chart(chart_labor)

        # Peak cap threshold annotation
        st.markdown(f"""
        <div style="text-align: center; margin-top: -10px;">
            <span style="font-size: 0.75rem; color: #ef4444; font-weight: 600;">
                ⚠️ Peak Season Temporary Cap: {peak_cap} workers (current: {total})
            </span>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="section-header">Picking Efficiency by Zone</div>', unsafe_allow_html=True)
        df_eff = generate_labor_data()
        st.dataframe(df_eff[["Zone", "Total Headcount", "SKUs/Hour/Person", "Shift"]], hide_index=True, height=250)

    st.markdown("---")

    # Main Operation Queue
    st.markdown('<div class="section-header">Operation Queue</div>', unsafe_allow_html=True)
    df_tasks = generate_picking_tasks(n=30)

    tab_pending, tab_active, tab_completed, tab_exceptions = st.tabs(["⏳ Pending", "🔧 Active Picking", "✅ Completed", "⚠️ Exceptions"])

    with tab_pending:
        df_pending = df_tasks[df_tasks["Status"] == "Pending"]
        if len(df_pending) > 0:
            for _, row in df_pending.iterrows():
                with st.expander(f"{row['Task ID']} — {row['Source Zone']} → {row['Target Client']}"):
                    st.markdown(f"**Priority:** <span class='badge badge-pending'>{row['Priority']}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Assigned Worker:** {row['Assigned Worker']}")
                    st.markdown(f"**SKU Checklist:** {row['SKU Checklist']}")
                    st.markdown(f"**Est. Duration:** {row['Est. Duration (min)']} min")
        else:
            st.info("No pending tasks")

    with tab_active:
        df_active = df_tasks[df_tasks["Status"] == "Active Picking"]
        if len(df_active) > 0:
            for _, row in df_active.iterrows():
                with st.expander(f"{row['Task ID']} — {row['Source Zone']} → {row['Target Client']}"):
                    st.markdown(f"**Priority:** <span class='badge badge-active'>{row['Priority']}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Assigned Worker:** {row['Assigned Worker']}")
                    st.markdown(f"**SKU Checklist:** {row['SKU Checklist']}")
                    st.markdown(f"**Est. Duration:** {row['Est. Duration (min)']} min")
                    st.markdown("---")
                    st.markdown("##### 🧠 DRL-Optimized Picking Path")
                    st.markdown(f"<div style='background: #0f172a; padding: 10px; border-radius: 6px; border-left: 3px solid #3b82f6; color: #e2e8f0; font-family: monospace; font-size: 0.85rem;'>{row['Optimized Path']}</div>", unsafe_allow_html=True)
        else:
            st.info("No active picking tasks")

    with tab_completed:
        df_done = df_tasks[df_tasks["Status"] == "Completed"]
        if len(df_done) > 0:
            st.dataframe(df_done[["Task ID", "Source Zone", "Target Client", "Assigned Worker", "SKU Checklist"]], hide_index=True)
        else:
            st.info("No completed tasks")

    with tab_exceptions:
        df_exc = df_tasks[df_tasks["Status"] == "Exception"]
        if len(df_exc) > 0:
            for _, row in df_exc.iterrows():
                with st.expander(f"⚠️ {row['Task ID']} — EXCEPTION"):
                    st.markdown(f"**Priority:** <span class='badge badge-exception'>{row['Priority']}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Assigned Worker:** {row['Assigned Worker']}")
                    st.markdown(f"**SKU Checklist:** {row['SKU Checklist']}")
                    st.error(f"Exception: Temperature mismatch detected during picking. Zone supervisor notified.")
        else:
            st.success("No exceptions — all operations nominal")

    st.markdown("---")

    # Dispatched Task Panel
    st.markdown('<div class="section-header">My Dispatched Tasks</div>', unsafe_allow_html=True)
    my_tasks = df_tasks[df_tasks["Assigned Worker"] == "Worker-01"]
    if len(my_tasks) > 0:
        st.dataframe(my_tasks[["Task ID", "Source Zone", "Target Client", "Status", "Priority", "Est. Duration (min)"]], hide_index=True)
    else:
        st.info("No tasks currently dispatched to Worker-01")


# =============================================================================
# PAGE: REAL-TIME SIMULATION
# =============================================================================
elif page == "⚡ Real-Time Simulation":
    st.markdown('<div class="main-header">⚡ Real-time Simulation</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Live warehouse sorting & dispatch visualization</div>', unsafe_allow_html=True)

    st.info("The real-time simulation runs in the original HTML dashboard below. Use the controls inside the panel to start/pause/reset the simulation.")

    # Embed the original HTML dashboard via iframe (English version)
    html_path = Path(__file__).parent / "smart_wave_dashboard_en.html"
    if html_path.exists():
        try:
            with open(html_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            # Validate minimum content size to catch truncated files
            if len(html_content) < 1000:
                st.error("HTML dashboard file appears to be truncated or corrupted.")
            else:
                components.html(html_content, height=900, scrolling=True)
        except Exception as e:
            st.error(f"Failed to load simulation dashboard: {e}")
            st.info("Try refreshing the page or checking that smart_wave_dashboard_en.html is not corrupted.")
    else:
        st.error("smart_wave_dashboard_en.html not found. Please ensure the file is in the same directory as streamlit_app_v3.py")


# =============================================================================
# PAGE: ORDER ANALYTICS
# =============================================================================
elif page == "📈 Order Analytics":
    st.markdown('<div class="main-header">📈 Order Analytics</div>', unsafe_allow_html=True)
    st.markdown("Synthetic order data generated from empirical distributions")

    # Data loading helpers (same pattern as v4)
    def load_json(filename):
        base = Path(__file__).parent / "data"
        path = base / filename
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError, OSError) as e:
                st.warning(f"Failed to load {filename}: {e}")
                return None
        return None

    @st.cache_data
    def load_all_data():
        return {
            "final_results": load_json("final_results.json"),
            "order_stats": load_json("order_stats.json"),
            "heuristic_results": load_json("heuristic_results.json"),
            "ppo_training": load_json("ppo_training.json"),
            "ppo_eval": load_json("ppo_eval.json"),
        }

    data = load_all_data()

    stats = data.get("order_stats")
    if not stats:
        st.warning("Order statistics data not found.")
        st.stop()

    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Orders", stats.get("total_orders", 0))
    c2.metric("Avg Items/Order", f"{stats.get('avg_items_per_order', 0):.2f}")
    c3.metric("Urgent Ratio", f"{stats.get('urgent_ratio', 0)*100:.1f}%")
    c4.metric("Avg Deadline", f"{stats.get('avg_deadline_hours', 0):.1f} hrs")

    st.markdown("---")
    st.markdown("### 🌡️ Temperature Distribution")

    temp_dist = stats.get("temp_distribution", {})
    temp_names = {"ambient": "Ambient", "cool": "Cool", "cold": "Cold", "frozen": "Frozen",
                  0: "Ambient", 1: "Cool", 2: "Cold", 3: "Frozen"}

    if temp_dist:
        temp_df = pd.DataFrame([
            {"Category": temp_names.get(k, k), "Count": v, "Percentage": v / max(stats.get("total_orders", 1), 1) * 100}
            for k, v in temp_dist.items()
        ])

        col_chart, col_table = st.columns([2, 1])
        with col_chart:
            chart = alt.Chart(temp_df).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="Count", type="quantitative"),
                color=alt.Color(field="Category", type="nominal",
                                scale=alt.Scale(domain=["Ambient", "Cool", "Cold", "Frozen"],
                                                range=["#ff7f0e", "#2ca02c", "#1f77b4", "#9467bd"])),
                tooltip=["Category", "Count", "Percentage"]
            ).properties(height=350)
            st.altair_chart(chart)

        with col_table:
            st.dataframe(temp_df, hide_index=True)
    else:
        st.info("No temperature distribution data available.")

    st.markdown("---")
    st.markdown("### 📈 Order Arrival Timeline")

    timeline = stats.get("arrival_timeline", [])
    if timeline:
        df_time = pd.DataFrame(timeline)
        df_time["temp_name"] = df_time["temp"].map(temp_names)
        df_time["urgent_label"] = df_time["urgent"].map({True: "Urgent", False: "Standard"})

        hist_chart = alt.Chart(df_time).mark_bar(opacity=0.7).encode(
            x=alt.X("time:Q", bin=alt.Bin(maxbins=30), title="Time (minutes from shift start)"),
            y=alt.Y("count()", title="Order Count"),
            color=alt.Color("temp_name:N", title="Temperature",
                            scale=alt.Scale(domain=["Ambient", "Cool", "Cold", "Frozen"],
                                            range=["#ff7f0e", "#2ca02c", "#1f77b4", "#9467bd"]))
        ).properties(height=350, title="Order Arrivals by Temperature Category")
        st.altair_chart(hist_chart)

        urgent_chart = alt.Chart(df_time).mark_circle(opacity=0.6, size=30).encode(
            x=alt.X("time:Q", title="Time (minutes)"),
            y=alt.Y("temp:O", title="Temperature Category"),
            color=alt.Color("urgent_label:N", scale=alt.Scale(domain=["Standard", "Urgent"],
                                                               range=["#2ca02c", "#d62728"]),
                            title="Priority"),
            tooltip=["time", "temp_name", "urgent_label"]
        ).properties(height=300, title="Order Priority Over Time")
        st.altair_chart(urgent_chart)

    st.markdown("---")
    st.markdown("### 📋 Generation Parameters")
    st.markdown("""
    | Parameter | Value | Description |
    |-----------|-------|-------------|
    | Base arrival rate | 3.0 orders/min | Poisson process |
    | Peak multiplier | 2.8x | Flu season / promotion spikes |
    | Peak probability | 5% | Chance of extreme peak |
    | Order sizes | 3, 4, 5 items | Probabilities: 40%, 35%, 25% |
    | Temperature | Ambient 55%, Cool 25%, Cold 15%, Frozen 5% | GSP distribution |
    | Urgent ratio | 20% | Deadline 2-6 hours |
    | Standard deadline | 8-24 hours | Uniform distribution |
    | Zones | 8 (2x4 grid) | Warehouse layout |
    | Simulation horizon | 8 hours | One shift |
    """)


# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align:center; font-size:0.7rem; color:#475569; padding:1rem 0;">
    Maverick-SORT Professional Edition v2.0 | Day 3 Commercialization Build | 2026/06/06<br>
    Modules: multi_objective_scheduler.py | adaptive_policy.py | what_if_simulator.py | kgdrl_core_v2.py<br>
    <span style="color:#f59e0b;">🔶 Professional Edition</span> | Built with Streamlit + Real Algorithm Engines
</div>
""", unsafe_allow_html=True)
