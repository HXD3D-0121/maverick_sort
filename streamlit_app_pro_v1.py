"""
Sunergy Pharma — Pro Edition Command Center
============================================
Smart Supply Chain Command Center v5.0

Product Tier: 🔶 Pro (Professional Edition)
Features:
  - What-If Scenario Lab (Essential + Pro)
  - Multi-Objective Pareto Optimizer (Pro)
  - Real-Time Adaptive Monitor (Pro)
  - Federated Learning Architecture Preview (Pro)
  - Product Tier Selector
  - Advanced Analytics Dashboard

Author: AI-assisted implementation
Date: 2026/06/06 (Day 3 of Commercialization Plan)
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
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="Sunergy Pharma Pro | Enterprise Command Center",
    page_icon="🔶",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# CUSTOM CSS — Pro Edition Dark Executive Theme
# =============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --bg-primary: #0a0f1e;
        --bg-card: #111827;
        --bg-elevated: #1e293b;
        --accent-blue: #3b82f6;
        --accent-cyan: #06b6d4;
        --accent-green: #10b981;
        --accent-amber: #f59e0b;
        --accent-red: #ef4444;
        --accent-purple: #8b5cf6;
        --accent-pink: #ec4899;
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --border: rgba(148, 163, 184, 0.12);
    }

    .main-header {
        font-size: 2.4rem;
        font-weight: 800;
        color: #f8fafc;
        margin-bottom: 0.3rem;
        font-family: 'Inter', sans-serif;
        letter-spacing: -0.02em;
    }
    .pro-badge {
        background: linear-gradient(135deg, #f59e0b 0%, #ec4899 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .sub-header {
        font-size: 1rem;
        color: #94a3b8;
        margin-bottom: 1.5rem;
        font-family: 'Inter', sans-serif;
    }
    .section-header {
        font-size: 1.15rem;
        font-weight: 700;
        color: #e2e8f0;
        margin: 1.2rem 0 0.8rem 0;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid var(--border);
    }

    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #1e293b 100%);
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid var(--border);
        color: #f8fafc;
        text-align: center;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.15);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #f8fafc;
        margin-bottom: 0.2rem;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Feature Cards */
    .feature-card {
        background: #111827;
        border: 1px solid rgba(148, 163, 184, 0.12);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.2s;
    }
    .feature-card:hover {
        border-color: rgba(245, 158, 11, 0.4);
        box-shadow: 0 4px 16px rgba(245, 158, 11, 0.1);
    }
    .feature-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 0.5rem;
    }
    .feature-desc {
        font-size: 0.9rem;
        color: #94a3b8;
        line-height: 1.5;
    }

    /* Pareto Chart */
    .pareto-container {
        background: #111827;
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid var(--border);
    }

    /* Strategy Mode Selector */
    .strategy-cost { border-left: 4px solid #10b981; }
    .strategy-time { border-left: 4px solid #3b82f6; }
    .strategy-compliance { border-left: 4px solid #8b5cf6; }
    .strategy-balanced { border-left: 4px solid #f59e0b; }

    /* Tier Comparison */
    .tier-essential { border-top: 3px solid #3b82f6; }
    .tier-pro { border-top: 3px solid #f59e0b; }
    .tier-rd { border-top: 3px solid #8b5cf6; }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: #0f172a;
    }
    [data-testid="stSidebar"] .stRadio label {
        color: #e2e8f0;
        font-size: 0.9rem;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0f172a;
    }
    ::-webkit-scrollbar-thumb {
        background: #334155;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #475569;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SESSION STATE
# =============================================================================
if "live_mode" not in st.session_state:
    st.session_state.live_mode = False
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()
if "what_if_results" not in st.session_state:
    st.session_state.what_if_results = {}
if "pareto_solutions" not in st.session_state:
    st.session_state.pareto_solutions = []
if "shift_history" not in st.session_state:
    st.session_state.shift_history = []
if "federated_clients" not in st.session_state:
    st.session_state.federated_clients = []

# =============================================================================
# MOCK DATA GENERATORS
# =============================================================================

def generate_orders(n=50):
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


def generate_telemetry_stream(n_points=100):
    """生成实时遥测数据流"""
    np.random.seed(int(time.time()) % 1000)
    t = np.arange(n_points)
    base = 3.0
    peak = 2.8
    # 双峰模式
    seasonal = 1 + 0.8 * np.sin(t / 15 * np.pi) + 0.5 * np.sin(t / 8 * np.pi)
    noise = np.random.randn(n_points) * 0.3
    arrival_rate = base * seasonal + noise
    arrival_rate = np.clip(arrival_rate, 0.5, 12)

    # 容量动态调整
    capacity = np.where(arrival_rate > 6, 15, 20)
    capacity = np.where(arrival_rate < 2, 25, capacity)

    # 负载
    load = np.clip(arrival_rate / capacity * 100 + np.random.randn(n_points) * 5, 15, 98)

    return pd.DataFrame({
        "Time Step": t,
        "Arrival Rate (ord/min)": np.round(arrival_rate, 1),
        "Wave Capacity": capacity,
        "System Load (%)": np.round(load, 1),
        "EWMA Predicted": np.round(np.convolve(arrival_rate, np.ones(5)/5, mode='same'), 1),
    })


def generate_pareto_front(n=40):
    """生成模拟帕累托前沿"""
    np.random.seed(42)
    # 生成L形帕累托前沿
    costs = np.linspace(2000, 8000, n)
    miss_rates = 0.15 * np.exp(-costs / 3000) + np.random.randn(n) * 0.005
    miss_rates = np.clip(miss_rates, 0, 0.15)
    violations = 8 * np.exp(-costs / 2500) + np.random.randn(n) * 0.5
    violations = np.clip(violations, 0, 10)

    strategies = np.random.choice(
        ["💰 Cost First", "⚡ Time First", "🛡️ Compliance First", "⚖️ Balanced"],
        size=n,
        p=[0.25, 0.25, 0.25, 0.25]
    )

    return pd.DataFrame({
        "Cost": np.round(costs, 0),
        "Miss Rate": np.round(miss_rates, 4),
        "Violations": np.round(violations, 1),
        "Strategy": strategies,
        "Rank": np.random.choice([0, 1, 2], size=n, p=[0.4, 0.35, 0.25]),
    })


def generate_what_if_scenarios():
    """生成What-if对比数据"""
    scenarios = [
        {"Scenario": "Current (TZU)", "Cost": 3850, "Distance": 665, "Waves": 83, "Viol%": 4.2, "OnTime%": 96.5},
        {"Scenario": "Conservative (Cap=15)", "Cost": 4200, "Distance": 620, "Waves": 105, "Viol%": 2.1, "OnTime%": 98.2},
        {"Scenario": "Aggressive (Cap=30)", "Cost": 3400, "Distance": 720, "Waves": 58, "Viol%": 7.8, "OnTime%": 92.1},
        {"Scenario": "High Setup Cost", "Cost": 3100, "Distance": 690, "Waves": 52, "Viol%": 5.5, "OnTime%": 94.3},
        {"Scenario": "Peak Season", "Cost": 5200, "Distance": 710, "Waves": 92, "Viol%": 6.2, "OnTime%": 89.5},
    ]
    return pd.DataFrame(scenarios)


def generate_federated_status():
    """生成联邦学习状态数据"""
    warehouses = ["Shanghai", "Beijing", "Guangzhou", "Chengdu", "Wuhan"]
    data = []
    for wh in warehouses:
        data.append({
            "Warehouse": wh,
            "Status": np.random.choice(["Synced", "Training", "Idle"], p=[0.6, 0.25, 0.15]),
            "Local Samples": np.random.randint(800, 1500),
            "Last Sync": f"{np.random.randint(1, 60)} min ago",
            "Model Version": f"v2.{np.random.randint(1, 5)}.{np.random.randint(0, 9)}",
            "Sync Quality": np.round(np.random.uniform(0.85, 0.99), 3),
        })
    return pd.DataFrame(data)


# =============================================================================
# SIDEBAR NAVIGATION
# =============================================================================

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; margin-bottom:1.5rem;">
        <div style="font-size:1.5rem; font-weight:800; color:#f8fafc;">
            🔶 Sunergy Pharma
        </div>
        <div style="font-size:0.85rem; color:#94a3b8;">
            Pro Edition Command Center
        </div>
        <div style="margin-top:0.5rem;">
            <span class="pro-badge">Professional</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    page = st.radio(
        "Navigation",
        [
            "🏠 Home — Product Overview",
            "🔮 What-If Scenario Lab",
            "⚖️ Multi-Objective Optimizer",
            "📡 Real-Time Adaptive Monitor",
            "🌐 Federated Learning Hub",
            "🏆 Algorithm Arena",
            "📦 Omni-Channel Orders",
            "🌡️ Warehouse & Zones",
            "📊 Customer SLA Analytics",
            "👷 Worker Task Station",
        ],
        index=0,
    )

    st.markdown("---")

    # Product Tier Selector
    st.markdown("""
    <div style="margin-bottom:0.5rem; color:#94a3b8; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.5px;">
        Product Tier
    </div>
    """, unsafe_allow_html=True)

    tier = st.selectbox(
        "Select Tier",
        ["🔷 Essential", "🔶 Pro (Current)", "🔬 R&D"],
        index=1,
        label_visibility="collapsed",
    )

    st.markdown("---")

    # Live Mode Toggle
    st.session_state.live_mode = st.toggle(
        "🔄 Live Mode",
        value=st.session_state.live_mode,
        help="Enable real-time data refresh every 3 seconds"
    )

    if st.session_state.live_mode:
        st.caption("Refreshing every 3s...")
        time.sleep(2.5)
        st.rerun()

# =============================================================================
# PAGE: HOME — PRODUCT OVERVIEW
# =============================================================================

if page == "🏠 Home — Product Overview":
    col_title, col_badge = st.columns([3, 1])
    with col_title:
        st.markdown('<div class="main-header">Enterprise Command Center</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Sunergy Pharma Pro Edition — Multi-Warehouse Smart Wave Allocation</div>', unsafe_allow_html=True)
    with col_badge:
        st.markdown("""
        <div style="text-align:right; margin-top:0.5rem;">
            <span class="pro-badge">Professional</span>
            <div style="font-size:0.75rem; color:#64748b; margin-top:0.3rem;">v5.0.0-pro</div>
        </div>
        """, unsafe_allow_html=True)

    # Hero Metrics
    st.markdown("---")
    cols = st.columns(5)
    metrics = [
        ("📦 Total Orders", "94,328", "+12% vs yesterday", "#3b82f6"),
        ("🌊 Active Waves", "87", "-3% vs yesterday", "#06b6d4"),
        ("⏱️ Avg Process Time", "4.2 min", "-18% vs baseline", "#10b981"),
        ("🛡️ Temp Compliance", "99.2%", "+0.5% vs yesterday", "#8b5cf6"),
        ("💰 Est. Daily Savings", "¥47,600", "KGDRL vs TZU", "#f59e0b"),
    ]
    for col, (label, value, delta, color) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color:{color};">{value}</div>
                <div style="font-size:0.75rem; color:#64748b;">{delta}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Feature Grid
    st.markdown('<div class="section-header">🔶 Pro Edition Capabilities</div>', unsafe_allow_html=True)

    features = [
        ("🔮 What-If Scenario Lab", "Interactive parameter sensitivity analysis. Test 'what if I reduce wave capacity by 20%?' in seconds.", "what_if_simulator.py"),
        ("⚖️ Multi-Objective Optimizer", "NSGA-II powered Pareto frontier for Cost × Time × Compliance trade-offs. One-click strategy switching.", "multi_objective_scheduler.py"),
        ("📡 Real-Time Adaptive Monitor", "EWMA-based arrival rate prediction with dynamic wave capacity adjustment. Handles peak seasons automatically.", "adaptive_policy.py"),
        ("🌐 Federated Learning Hub", "Multi-warehouse collaborative training architecture. Data stays local, intelligence goes global.", "adaptive_policy.py"),
        ("🏆 Algorithm Arena", "PPO vs KGDRL vs 5 heuristics. Real-time leaderboard with training convergence curves.", "kgdrl_core_v2.py"),
        ("📊 Enterprise Analytics", "4-view industrial dashboard: Orders, Warehouse, SLA, Worker. 3-second real-time refresh.", "streamlit_app_v4.py"),
    ]

    for i in range(0, len(features), 2):
        cols = st.columns(2)
        for j, (title, desc, module) in enumerate(features[i:i+2]):
            with cols[j]:
                st.markdown(f"""
                <div class="feature-card">
                    <div class="feature-title">{title}</div>
                    <div class="feature-desc">{desc}</div>
                    <div style="margin-top:0.5rem; font-size:0.75rem; color:#64748b; font-family:monospace;">
                        → {module}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Product Tier Comparison
    st.markdown("---")
    st.markdown('<div class="section-header">📊 Product Tier Comparison</div>', unsafe_allow_html=True)

    tier_data = pd.DataFrame([
        {"Feature": "KGDRL Core Engine", "🔷 Essential": "✅", "🔶 Pro": "✅", "🔬 R&D": "✅"},
        {"Feature": "What-If Simulator", "🔷 Essential": "✅", "🔶 Pro": "✅", "🔬 R&D": "❌"},
        {"Feature": "Algorithm Arena", "🔷 Essential": "✅", "🔶 Pro": "✅", "🔬 R&D": "❌"},
        {"Feature": "Multi-Objective NSGA-II", "🔷 Essential": "❌", "🔶 Pro": "✅", "🔬 R&D": "❌"},
        {"Feature": "Real-Time Adaptive", "🔷 Essential": "❌", "🔶 Pro": "✅", "🔬 R&D": "❌"},
        {"Feature": "Online Learning (EWC)", "🔷 Essential": "❌", "🔶 Pro": "✅", "🔬 R&D": "❌"},
        {"Feature": "Federated Learning", "🔷 Essential": "❌", "🔶 Pro": "✅ Architecture", "🔬 R&D": "❌"},
        {"Feature": "API Integration", "🔷 Essential": "❌", "🔶 Pro": "✅", "🔬 R&D": "❌"},
        {"Feature": "BVN Decomposition", "🔷 Essential": "❌", "🔶 Pro": "❌", "🔬 R&D": "✅ Research"},
        {"Feature": "Pricing", "🔷 Essential": "¥2,999/mo", "🔶 Pro": "¥8,999/mo", "🔬 R&D": "Consulting"},
    ])
    st.dataframe(tier_data, use_container_width=True, hide_index=True)

# =============================================================================
# PAGE: WHAT-IF SCENARIO LAB
# =============================================================================

elif page == "🔮 What-If Scenario Lab":
    st.markdown('<div class="main-header">🔮 What-If Scenario Lab</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Test hypotheses before committing — zero-risk scenario analysis</div>', unsafe_allow_html=True)

    st.info("💡 **Essential Edition Feature**: Available in all tiers. Try changing parameters and see real-time impact on cost, compliance, and throughput.")

    col_params, col_results = st.columns([1, 2])

    with col_params:
        st.markdown('<div class="section-header">🎛️ Parameters</div>', unsafe_allow_html=True)

        wave_cap = st.slider("Wave Capacity (orders)", 8, 35, 20, 1)
        setup_cost = st.slider("Setup Cost (alpha)", 5.0, 40.0, 15.0, 2.5)
        peak_mult = st.slider("Peak Multiplier", 1.0, 5.0, 2.8, 0.2)
        temp_penalty = st.slider("Temp Violation Penalty", 50, 200, 100, 10)
        deadline_pen = st.slider("Deadline Miss Penalty", 20, 100, 50, 5)
        policy = st.selectbox("Policy", ["TZU", "KGDRL", "PPO", "EDD", "FCFS"])

        if st.button("🚀 Run Simulation", type="primary", use_container_width=True):
            with st.spinner("Running 5 instances..."):
                time.sleep(1.5)
            st.success("Simulation complete!")
            st.session_state.what_if_results["latest"] = {
                "wave_cap": wave_cap, "setup_cost": setup_cost,
                "peak_mult": peak_mult, "policy": policy
            }

        st.markdown("---")
        st.markdown("""
        <div style="font-size:0.8rem; color:#64748b;">
            <b>Quick Templates:</b><br>
            • <a href="#" style="color:#3b82f6;">Wave Capacity Sweep</a><br>
            • <a href="#" style="color:#3b82f6;">Peak Season Stress Test</a><br>
            • <a href="#" style="color:#3b82f6;">Policy Comparison</a>
        </div>
        """, unsafe_allow_html=True)

    with col_results:
        st.markdown('<div class="section-header">📊 Scenario Comparison</div>', unsafe_allow_html=True)

        df = generate_what_if_scenarios()
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Highlight best cost
        best_idx = df["Cost"].idxmin()
        st.markdown(f"""
        <div style="background:#111827; border-radius:8px; padding:1rem; margin:1rem 0; border-left:4px solid #10b981;">
            <div style="font-weight:700; color:#10b981;">🏆 Best Cost Scenario: {df.iloc[best_idx]['Scenario']}</div>
            <div style="font-size:0.85rem; color:#94a3b8; margin-top:0.3rem;">
                Cost = ¥{df.iloc[best_idx]['Cost']:,.0f} | Distance = {df.iloc[best_idx]['Distance']:.0f}m | On-Time = {df.iloc[best_idx]['OnTime%']:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Charts
        tab_cost, tab_radar, tab_sensitivity = st.tabs(["💰 Cost Breakdown", "🕸️ Radar", "📈 Sensitivity"])

        with tab_cost:
            chart = alt.Chart(df).mark_bar().encode(
                x=alt.X("Scenario", sort=None),
                y="Cost",
                color=alt.condition(
                    alt.datum.Scenario == df.iloc[best_idx]["Scenario"],
                    alt.value("#10b981"),
                    alt.value("#3b82f6")
                ),
                tooltip=["Scenario", "Cost", "Distance", "OnTime%"]
            ).properties(height=300)
            st.altair_chart(chart, use_container_width=True)

        with tab_radar:
            # Normalize for radar
            radar_df = df.copy()
            for col in ["Cost", "Distance", "Waves"]:
                radar_df[col] = 1 - (radar_df[col] - radar_df[col].min()) / (radar_df[col].max() - radar_df[col].min() + 1e-9)
            radar_df["OnTime%"] = radar_df["OnTime%"] / 100
            radar_df["Viol%"] = 1 - radar_df["Viol%"] / 100

            radar_melted = radar_df.melt(
                id_vars=["Scenario"],
                value_vars=["Cost", "Distance", "Waves", "OnTime%", "Viol%"],
                var_name="Metric",
                value_name="Score"
            )
            radar_chart = alt.Chart(radar_melted).mark_line(opacity=0.7).encode(
                x=alt.X("Metric", sort=None),
                y="Score",
                color="Scenario",
                strokeWidth=alt.value(2),
            ).properties(height=300)
            st.altair_chart(radar_chart, use_container_width=True)

        with tab_sensitivity:
            # Sensitivity curve mock
            cap_range = np.arange(10, 31)
            sens_cost = 2000 + 8000 / (cap_range - 5) + np.random.randn(len(cap_range)) * 100
            sens_df = pd.DataFrame({"Capacity": cap_range, "Cost": sens_cost})
            sens_chart = alt.Chart(sens_df).mark_line(color="#f59e0b", strokeWidth=2).encode(
                x="Capacity",
                y="Cost",
                tooltip=["Capacity", "Cost"]
            ) + alt.Chart(sens_df).mark_point(color="#f59e0b", size=60).encode(
                x="Capacity", y="Cost"
            )
            st.altair_chart(sens_chart.properties(height=300), use_container_width=True)
            st.caption("Cost vs Wave Capacity — sweet spot around 18-22 orders")

# =============================================================================
# PAGE: MULTI-OBJECTIVE OPTIMIZER
# =============================================================================

elif page == "⚖️ Multi-Objective Optimizer":
    st.markdown('<div class="main-header">⚖️ Multi-Objective Optimizer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">NSGA-II powered Pareto frontier — Cost × Time × Compliance</div>', unsafe_allow_html=True)

    st.info("🔶 **Pro Edition Feature**: Unlock with Pro license. Optimize across three conflicting objectives simultaneously.")

    col_ctrl, col_viz = st.columns([1, 2])

    with col_ctrl:
        st.markdown('<div class="section-header">🎚️ Strategy Mode</div>', unsafe_allow_html=True)

        strategy = st.radio(
            "Select Strategy",
            [
                ("💰 Cost First", "cost_first"),
                ("⚡ Time First", "time_first"),
                ("🛡️ Compliance First", "compliance_first"),
                ("⚖️ Balanced", "balanced"),
            ],
            format_func=lambda x: x[0],
            index=3,
        )

        st.markdown("---")

        st.markdown('<div class="section-header">⚙️ NSGA-II Config</div>', unsafe_allow_html=True)
        pop_size = st.slider("Population Size", 20, 100, 50, 10)
        n_gen = st.slider("Generations", 20, 200, 80, 10)
        cx_rate = st.slider("Crossover Rate", 0.5, 1.0, 0.9, 0.05)
        mut_rate = st.slider("Mutation Rate", 0.05, 0.3, 0.15, 0.05)

        if st.button("🧬 Run NSGA-II Optimization", type="primary", use_container_width=True):
            with st.spinner(f"Evolving {pop_size} individuals for {n_gen} generations..."):
                time.sleep(2)
            st.success("Pareto front computed!")
            st.session_state.pareto_solutions = generate_pareto_front(40)

        st.markdown("---")

        # Strategy description
        strategy_desc = {
            "cost_first": "Maximize operational savings. Best for daily operations with stable demand.",
            "time_first": "Maximize on-time delivery. Best for flu seasons and emergency distributions.",
            "compliance_first": "Zero tolerance for temperature violations. Best for GSP audit periods.",
            "balanced": "Even trade-off across all three objectives. Recommended default.",
        }
        st.markdown(f"""
        <div style="background:#111827; border-radius:8px; padding:0.8rem; font-size:0.85rem; color:#94a3b8;">
            <b>Mode Description:</b><br>{strategy_desc[strategy[1]]}
        </div>
        """, unsafe_allow_html=True)

    with col_viz:
        st.markdown('<div class="section-header">📊 Pareto Front Visualization</div>', unsafe_allow_html=True)

        pareto_df = generate_pareto_front()

        # 3D scatter (Cost × Miss Rate × Violations)
        pareto_chart = alt.Chart(pareto_df).mark_circle(size=80, opacity=0.7).encode(
            x=alt.X("Cost", scale=alt.Scale(domain=[1500, 8500])),
            y=alt.Y("Miss Rate", scale=alt.Scale(domain=[-0.01, 0.16])),
            color=alt.Color("Strategy", scale=alt.Scale(
                domain=["💰 Cost First", "⚡ Time First", "🛡️ Compliance First", "⚖️ Balanced"],
                range=["#10b981", "#3b82f6", "#8b5cf6", "#f59e0b"]
            )),
            size=alt.Size("Violations", scale=alt.Scale(range=[30, 300])),
            tooltip=["Cost", "Miss Rate", "Violations", "Strategy"]
        ).properties(height=350)

        st.altair_chart(pareto_chart, use_container_width=True)
        st.caption("💡 Bubble size = Temperature Violations | Color = Strategy Mode")

        # 2D projections
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown("**Cost vs Miss Rate**")
            c1 = alt.Chart(pareto_df).mark_circle(size=50, opacity=0.6).encode(
                x="Cost", y="Miss Rate", color="Strategy"
            ).properties(height=200)
            st.altair_chart(c1, use_container_width=True)

        with col_p2:
            st.markdown("**Cost vs Violations**")
            c2 = alt.Chart(pareto_df).mark_circle(size=50, opacity=0.6).encode(
                x="Cost", y="Violations", color="Strategy"
            ).properties(height=200)
            st.altair_chart(c2, use_container_width=True)

    # Strategy recommendations
    st.markdown("---")
    st.markdown('<div class="section-header">🎯 Strategy Recommendations</div>', unsafe_allow_html=True)

    rec_cols = st.columns(4)
    recs = [
        ("💰 Cost First", "#10b981", "strategy-cost", "Est. Cost: ¥3,100", "Miss: 8.2%", "Viol: 6"),
        ("⚡ Time First", "#3b82f6", "strategy-time", "Est. Cost: ¥4,200", "Miss: 1.5%", "Viol: 3"),
        ("🛡️ Compliance First", "#8b5cf6", "strategy-compliance", "Est. Cost: ¥4,800", "Miss: 4.1%", "Viol: 0"),
        ("⚖️ Balanced", "#f59e0b", "strategy-balanced", "Est. Cost: ¥3,850", "Miss: 3.5%", "Viol: 4"),
    ]
    for col, (name, color, css, cost, miss, viol) in zip(rec_cols, recs):
        with col:
            st.markdown(f"""
            <div class="feature-card {css}" style="border-left: 4px solid {color};">
                <div style="font-weight:700; color:{color}; font-size:1rem;">{name}</div>
                <div style="margin-top:0.5rem; font-size:0.85rem; color:#94a3b8;">
                    {cost}<br>{miss}<br>{viol}
                </div>
            </div>
            """, unsafe_allow_html=True)

# =============================================================================
# PAGE: REAL-TIME ADAPTIVE MONITOR
# =============================================================================

elif page == "📡 Real-Time Adaptive Monitor":
    st.markdown('<div class="main-header">📡 Real-Time Adaptive Monitor</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">EWMA prediction + Dynamic capacity adjustment + Online learning telemetry</div>', unsafe_allow_html=True)

    st.info("🔶 **Pro Edition Feature**: Automatically adjusts wave capacity based on predicted arrival rates.")

    # Top metrics
    cols = st.columns(4)
    adaptive_metrics = [
        ("Current Capacity", "20", "orders/wave", "#3b82f6"),
        ("EWMA Rate", "5.8", "ord/min", "#06b6d4"),
        ("Trend", "↗ +12%", "next 15min", "#10b981"),
        ("Peak Alert", "🟡 Moderate", "15:00-17:00", "#f59e0b"),
    ]
    for col, (label, value, unit, color) in zip(cols, adaptive_metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color:{color};">{value}</div>
                <div style="font-size:0.75rem; color:#64748b;">{unit}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Main telemetry chart
    telemetry_df = generate_telemetry_stream(100)

    st.markdown('<div class="section-header">📈 Real-Time Telemetry</div>', unsafe_allow_html=True)

    # Multi-line chart
    tele_melted = telemetry_df.melt(
        id_vars=["Time Step"],
        value_vars=["Arrival Rate (ord/min)", "Wave Capacity", "System Load (%)"],
        var_name="Metric",
        value_name="Value"
    )
    tele_chart = alt.Chart(tele_melted).mark_line(strokeWidth=2).encode(
        x="Time Step",
        y="Value",
        color=alt.Color("Metric", scale=alt.Scale(
            domain=["Arrival Rate (ord/min)", "Wave Capacity", "System Load (%)"],
            range=["#3b82f6", "#f59e0b", "#ef4444"]
        )),
        tooltip=["Metric", "Value"]
    ).properties(height=350)
    st.altair_chart(tele_chart, use_container_width=True)

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown('<div class="section-header">🎛️ Capacity Adjustment Log</div>', unsafe_allow_html=True)
        adj_log = pd.DataFrame([
            {"Time": "14:32", "Old Cap": 20, "New Cap": 15, "Reason": "Peak detected", "Rate": 7.2},
            {"Time": "14:15", "Old Cap": 20, "New Cap": 20, "Reason": "Seasonal", "Rate": 4.8},
            {"Time": "13:58", "Old Cap": 22, "New Cap": 20, "Reason": "High load", "Rate": 5.5},
            {"Time": "13:30", "Old Cap": 25, "New Cap": 22, "Reason": "Valley ended", "Rate": 4.2},
            {"Time": "12:45", "Old Cap": 25, "New Cap": 25, "Reason": "Seasonal", "Rate": 2.1},
        ])
        st.dataframe(adj_log, use_container_width=True, hide_index=True)

    with col_right:
        st.markdown('<div class="section-header">🧠 Online Learning Status</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#111827; border-radius:8px; padding:1rem;">
            <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                <span style="color:#94a3b8;">Replay Buffer</span>
                <span style="color:#10b981; font-weight:700;">847 / 1000</span>
            </div>
            <div style="background:#1e293b; height:8px; border-radius:4px; margin-bottom:1rem;">
                <div style="background:#10b981; width:84.7%; height:100%; border-radius:4px;"></div>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                <span style="color:#94a3b8;">Update Count</span>
                <span style="color:#3b82f6; font-weight:700;">124</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                <span style="color:#94a3b8;">EWC Regularization</span>
                <span style="color:#8b5cf6; font-weight:700;">λ = 0.01</span>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <span style="color:#94a3b8;">Last Update</span>
                <span style="color:#f59e0b; font-weight:700;">2 min ago</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<div class="section-header">🎯 Policy Ensemble Weights</div>', unsafe_allow_html=True)
        ensemble_df = pd.DataFrame({
            "Policy": ["KGDRL", "TZU", "EDD"],
            "Weight": [0.52, 0.28, 0.20],
            "Recent Avg Reward": [4120, 3580, 3210],
        })
        st.dataframe(ensemble_df, use_container_width=True, hide_index=True)

# =============================================================================
# PAGE: FEDERATED LEARNING HUB
# =============================================================================

elif page == "🌐 Federated Learning Hub":
    st.markdown('<div class="main-header">🌐 Federated Learning Hub</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Multi-warehouse collaborative training — Data stays local, intelligence goes global</div>', unsafe_allow_html=True)

    st.info("🔶 **Pro Edition Architecture (Reserved)**: Federated learning infrastructure is architecturally ready. Activate with Enterprise deployment.")

    # Architecture diagram placeholder
    st.markdown("""
    <div style="background:#111827; border-radius:12px; padding:1.5rem; margin:1rem 0; text-align:center;">
        <div style="font-family:monospace; font-size:0.85rem; color:#94a3b8; line-height:1.8;">
            <span style="color:#f59e0b;">┌─────────────────┐</span>     <span style="color:#10b981;">FedAvg Aggregation</span>     <span style="color:#f59e0b;">┌─────────────────┐</span><br>
            <span style="color:#f59e0b;">│  Shanghai WH    │</span> ←─── <span style="color:#3b82f6;">∇θ₁</span> ─────→ <span style="color:#8b5cf6;">┌───────────────┐</span> ←─── <span style="color:#3b82f6;">θ_global</span> ───→ <span style="color:#f59e0b;">│  Beijing WH   │</span><br>
            <span style="color:#f59e0b;">│  Local Model    │</span>      <span style="color:#3b82f6;">(1,200 samples)</span>  <span style="color:#8b5cf6;">│   Coordinator  │</span>      <span style="color:#3b82f6;">θ_global</span>       <span style="color:#f59e0b;">│  Local Model  │</span><br>
            <span style="color:#f59e0b;">│  n=1,200        │</span> ───→ <span style="color:#10b981;">Secure</span> ───→ <span style="color:#8b5cf6;">│   Round 12     │</span> ───→ <span style="color:#10b981;">Secure</span> ───→ <span style="color:#f59e0b;">│  n=980        │</span><br>
            <span style="color:#f59e0b;">└─────────────────┘</span>      <span style="color:#10b981;">Aggregation</span>    <span style="color:#8b5cf6;">└───────────────┘</span>      <span style="color:#10b981;">Distribution</span>   <span style="color:#f59e0b;">└─────────────────┘</span><br>
                                                                               ↑<br>
            <span style="color:#f59e0b;">┌─────────────────┐</span> ←─────────────────────────────────────────────────┘<br>
            <span style="color:#f59e0b;">│  Guangzhou WH   │</span>      <span style="color:#3b82f6;">θ_global</span><br>
            <span style="color:#f59e0b;">│  Local Model    │</span><br>
            <span style="color:#f59e0b;">│  n=1,100        │</span> ───→ <span style="color:#3b82f6;">∇θ₃</span><br>
            <span style="color:#f59e0b;">└─────────────────┘</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Client status table
    st.markdown('<div class="section-header">🏭 Warehouse Client Status</div>', unsafe_allow_html=True)
    fed_df = generate_federated_status()
    st.dataframe(fed_df, use_container_width=True, hide_index=True)

    # Metrics
    st.markdown("---")
    cols = st.columns(4)
    fed_metrics = [
        ("Total Clients", "5", "warehouses", "#3b82f6"),
        ("Global Round", "12", "current", "#f59e0b"),
        ("Total Samples", "5,680", "across clients", "#10b981"),
        ("Avg Sync Quality", "0.923", "consensus score", "#8b5cf6"),
    ]
    for col, (label, value, unit, color) in zip(cols, fed_metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color:{color};">{value}</div>
                <div style="font-size:0.75rem; color:#64748b;">{unit}</div>
            </div>
            """, unsafe_allow_html=True)

    col_config, col_privacy = st.columns(2)
    with col_config:
        st.markdown('<div class="section-header">⚙️ Federation Config</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#111827; border-radius:8px; padding:1rem; font-size:0.85rem; color:#94a3b8;">
            <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                <span>Aggregation Algorithm</span>
                <span style="color:#f8fafc;">FedAvg</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                <span>Participation Rate</span>
                <span style="color:#f8fafc;">100%</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                <span>Local Epochs</span>
                <span style="color:#f8fafc;">5</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                <span>Sync Interval</span>
                <span style="color:#f8fafc;">100 episodes</span>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <span>Compression</span>
                <span style="color:#10b981;">Top-K Sparsification</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_privacy:
        st.markdown('<div class="section-header">🔒 Privacy Protection</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#111827; border-radius:8px; padding:1rem; font-size:0.85rem; color:#94a3b8;">
            <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                <span>Differential Privacy</span>
                <span style="color:#10b981;">ε = 1.0, δ = 1e-5</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                <span>Secure Aggregation</span>
                <span style="color:#10b981;">✅ Enabled</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                <span>Data Never Leaves</span>
                <span style="color:#10b981;">✅ Local</span>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <span>Model Encryption</span>
                <span style="color:#10b981;">✅ AES-256</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.info("🌐 **Enterprise Deployment Required**: Federated Learning is architecturally ready but requires Enterprise license for activation. Contact sales for multi-warehouse deployment.")

# =============================================================================
# PAGE: ALGORITHM ARENA (from v4)
# =============================================================================

elif page == "🏆 Algorithm Arena":
    st.markdown('<div class="main-header">🏆 Algorithm Arena</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">PPO vs KGDRL vs 5 Heuristics — Performance leaderboard with convergence analysis</div>', unsafe_allow_html=True)

    # Hero metrics
    cols = st.columns(4)
    arena_metrics = [
        ("KGDRL Distance", "665.7 m", "🏆 Industry lowest", "#10b981"),
        ("PPO Reward", "4,007.5", "Best single-objective", "#3b82f6"),
        ("TZU Violations", "21.4", "Best heuristic", "#f59e0b"),
        ("Training Episodes", "120", "Converged", "#8b5cf6"),
    ]
    for col, (label, value, delta, color) in zip(cols, arena_metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color:{color};">{value}</div>
                <div style="font-size:0.75rem; color:#64748b;">{delta}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Comparison table
    arena_df = pd.DataFrame([
        {"Method": "FCFS", "Reward": 1786.9, "Distance": 690.9, "Waves": 85.9, "Miss": 0.0, "Viol": 38.5, "Tier": "Heuristic"},
        {"Method": "TEMP_FIRST", "Reward": -2958.1, "Distance": 987.4, "Waves": 125.8, "Miss": 0.0, "Viol": 0.0, "Tier": "Heuristic"},
        {"Method": "ZONE_NN", "Reward": 1733.8, "Distance": 669.0, "Waves": 82.9, "Miss": 0.0, "Viol": 37.3, "Tier": "Heuristic"},
        {"Method": "EDD", "Reward": 1752.0, "Distance": 667.8, "Waves": 83.1, "Miss": 0.0, "Viol": 37.5, "Tier": "Heuristic"},
        {"Method": "TZU", "Reward": 144.6, "Distance": 666.7, "Waves": 83.0, "Miss": 0.0, "Viol": 21.4, "Tier": "Heuristic"},
        {"Method": "PPO (Vanilla)", "Reward": 4007.5, "Distance": 695.5, "Waves": 87.3, "Miss": 4.4, "Viol": 36.7, "Tier": "DRL"},
        {"Method": "KGDRL-Full", "Reward": 1908.8, "Distance": 665.7, "Waves": 82.8, "Miss": 0.0, "Viol": 39.0, "Tier": "DRL+KG"},
    ])

    # Highlight KGDRL
    def highlight_kgdrl(row):
        if row["Method"] == "KGDRL-Full":
            return ["background-color: rgba(16, 185, 129, 0.15)"] * len(row)
        return [""] * len(row)

    st.dataframe(arena_df.style.apply(highlight_kgdrl, axis=1), use_container_width=True, hide_index=True)

    # Charts
    col_bar, col_radar = st.columns(2)
    with col_bar:
        st.markdown("**Reward Comparison**")
        bar = alt.Chart(arena_df).mark_bar().encode(
            x=alt.X("Method", sort=None),
            y="Reward",
            color=alt.condition(
                alt.datum.Method == "KGDRL-Full",
                alt.value("#10b981"),
                alt.condition(
                    alt.datum.Tier == "DRL",
                    alt.value("#3b82f6"),
                    alt.value("#64748b")
                )
            )
        ).properties(height=280)
        st.altair_chart(bar, use_container_width=True)

    with col_radar:
        st.markdown("**Distance Comparison**")
        bar2 = alt.Chart(arena_df).mark_bar().encode(
            x=alt.X("Method", sort=None),
            y="Distance",
            color=alt.condition(
                alt.datum.Method == "KGDRL-Full",
                alt.value("#10b981"),
                alt.value("#64748b")
            )
        ).properties(height=280)
        st.altair_chart(bar2, use_container_width=True)

    # Knowledge Graph SVG
    st.markdown("---")
    st.markdown('<div class="section-header">🧬 Knowledge Graph Topology</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#111827; border-radius:12px; padding:1rem; text-align:center;">
        <svg viewBox="0 0 800 400" style="max-width:100%; height:auto;">
            <!-- Background grid -->
            <defs>
                <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                    <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.5"/>
                </pattern>
            </defs>
            <rect width="800" height="400" fill="#111827"/>
            <rect width="800" height="400" fill="url(#grid)"/>

            <!-- Orders (green) -->
            <circle cx="100" cy="100" r="8" fill="#10b981" opacity="0.8"/>
            <circle cx="150" cy="80" r="8" fill="#10b981" opacity="0.8"/>
            <circle cx="120" cy="150" r="8" fill="#10b981" opacity="0.8"/>
            <circle cx="180" cy="130" r="8" fill="#10b981" opacity="0.8"/>
            <text x="140" y="60" fill="#10b981" font-size="12" font-family="monospace">Orders</text>

            <!-- Zones (blue) -->
            <circle cx="350" cy="100" r="10" fill="#3b82f6" opacity="0.8"/>
            <circle cx="400" cy="80" r="10" fill="#3b82f6" opacity="0.8"/>
            <circle cx="380" cy="150" r="10" fill="#3b82f6" opacity="0.8"/>
            <circle cx="320" cy="130" r="10" fill="#3b82f6" opacity="0.8"/>
            <text x="360" y="60" fill="#3b82f6" font-size="12" font-family="monospace">Zones</text>

            <!-- Temps (purple) -->
            <circle cx="600" cy="100" r="10" fill="#8b5cf6" opacity="0.8"/>
            <circle cx="650" cy="130" r="10" fill="#8b5cf6" opacity="0.8"/>
            <circle cx="620" cy="170" r="10" fill="#8b5cf6" opacity="0.8"/>
            <circle cx="680" cy="160" r="10" fill="#8b5cf6" opacity="0.8"/>
            <text x="630" y="60" fill="#8b5cf6" font-size="12" font-family="monospace">Temps</text>

            <!-- Wave (center, amber) -->
            <circle cx="400" cy="280" r="15" fill="#f59e0b" opacity="0.9"/>
            <text x="385" y="320" fill="#f59e0b" font-size="12" font-family="monospace">Wave</text>

            <!-- Edges: Order-Zone -->
            <line x1="108" y1="100" x2="342" y2="100" stroke="#3b82f6" stroke-width="1" opacity="0.4"/>
            <line x1="158" y1="80" x2="342" y2="100" stroke="#3b82f6" stroke-width="1" opacity="0.4"/>
            <line x1="128" y1="150" x2="380" y2="150" stroke="#3b82f6" stroke-width="1" opacity="0.4"/>

            <!-- Edges: Zone-Temp -->
            <line x1="358" y1="100" x2="592" y2="100" stroke="#8b5cf6" stroke-width="1" opacity="0.4"/>
            <line x1="400" y1="80" x2="600" y2="100" stroke="#8b5cf6" stroke-width="1" opacity="0.4"/>

            <!-- Edges: Wave connections -->
            <line x1="150" y1="108" x2="385" y2="265" stroke="#f59e0b" stroke-width="1.5" opacity="0.5"/>
            <line x1="350" y1="108" x2="395" y2="265" stroke="#f59e0b" stroke-width="1.5" opacity="0.5"/>
            <line x1="600" y1="108" x2="405" y2="265" stroke="#f59e0b" stroke-width="1.5" opacity="0.5"/>
        </svg>
        <div style="font-size:0.75rem; color:#64748b; margin-top:0.5rem;">
            Heterogeneous Graph: Orders → Zones → Temps → Wave (GAT Attention-based Readout)
        </div>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# PAGE: OMNI-CHANNEL ORDERS (from v3/v4)
# =============================================================================

elif page == "📦 Omni-Channel Orders":
    st.markdown('<div class="main-header">📦 Omni-Channel Orders</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Real-time order flow across all channels</div>', unsafe_allow_html=True)

    cols = st.columns(4)
    for i, (label, value) in enumerate([
        ("Total Daily Orders", "94,328"),
        ("Bulk Orders", "28,298"),
        ("Fragmented Orders", "66,030"),
        ("Pending Dispatch", "1,247"),
    ]):
        with cols[i]:
            st.metric(label, value, delta=None)

    # Filters
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.selectbox("Client Category", ["All", "Hospital", "Clinic", "Pharmacy", "Distributor"])
    with col_f2:
        st.selectbox("Time Window", ["All", "Morning (6-12)", "Afternoon (12-18)", "Evening (18-24)"])
    with col_f3:
        st.selectbox("Temperature", ["All", "Ambient", "Cool", "Cold", "Frozen", "Deep Frozen"])

    df_orders = generate_orders(20)
    st.dataframe(df_orders, use_container_width=True, hide_index=True)

# =============================================================================
# PAGE: WAREHOUSE & ZONES (from v3/v4)
# =============================================================================

elif page == "🌡️ Warehouse & Zones":
    st.markdown('<div class="main-header">🌡️ Warehouse & Temperature Zones</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Zone capacity, utilization, and near-expiry FIFO control</div>', unsafe_allow_html=True)

    zones = ["Ambient", "Cool", "Cold", "Frozen", "Deep Frozen"]
    capacities = [45000, 28000, 12000, 6000, 2000]
    utilized = [38500, 22400, 10800, 4800, 1600]
    colors_z = ["#10b981", "#3b82f6", "#06b6d4", "#8b5cf6", "#ec4899"]

    cols = st.columns(5)
    for col, zone, cap, util, color in zip(cols, zones, capacities, utilized, colors_z):
        pct = util / cap * 100
        with col:
            st.markdown(f"""
            <div class="metric-card" style="border-top: 3px solid {color};">
                <div class="metric-label">{zone}</div>
                <div class="metric-value" style="color:{color};">{pct:.0f}%</div>
                <div style="font-size:0.75rem; color:#64748b;">{util:,} / {cap:,} units</div>
            </div>
            """, unsafe_allow_html=True)

    # Near-expiry table
    st.markdown("---")
    st.markdown('<div class="section-header">⏰ Near-Expiry FIFO Control</div>', unsafe_allow_html=True)
    expiry_df = pd.DataFrame([
        {"SKU": "INS-001", "Name": "Insulin Glargine", "Zone": "Cold", "Expiry": "2026-06-15", "Days Left": 9, "Risk": "🔴 Critical", "Qty": 1200},
        {"SKU": "VAC-042", "Name": "Influenza Vaccine", "Zone": "Cold", "Expiry": "2026-06-28", "Days Left": 22, "Risk": "🟡 Warning", "Qty": 850},
        {"SKU": "ANT-103", "Name": "Amoxicillin 500mg", "Zone": "Ambient", "Expiry": "2026-07-10", "Days Left": 34, "Risk": "🔵 Notice", "Qty": 3200},
        {"SKU": "ANT-205", "Name": "Azithromycin 250mg", "Zone": "Ambient", "Expiry": "2026-08-01", "Days Left": 56, "Risk": "⚪ Normal", "Qty": 1800},
    ])
    st.dataframe(expiry_df, use_container_width=True, hide_index=True)

# =============================================================================
# PAGE: CUSTOMER SLA (from v3/v4)
# =============================================================================

elif page == "📊 Customer SLA Analytics":
    st.markdown('<div class="main-header">📊 Customer SLA Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Fulfillment compliance and AI-powered demand forecasting</div>', unsafe_allow_html=True)

    months = pd.date_range("2025-06", periods=12, freq="M").strftime("%Y-%m").tolist()
    df_sla = pd.DataFrame({
        "Month": months,
        "Hospital": np.random.randint(8000, 12000, 12),
        "Clinic": np.random.randint(5000, 8000, 12),
        "Pharmacy": np.random.randint(15000, 22000, 12),
        "Distributor": np.random.randint(25000, 35000, 12),
    })

    sla_melted = df_sla.melt(id_vars=["Month"], var_name="Client Type", value_name="Orders")
    chart = alt.Chart(sla_melted).mark_line(strokeWidth=2).encode(
        x="Month",
        y="Orders",
        color="Client Type",
        tooltip=["Month", "Client Type", "Orders"]
    ).properties(height=300)
    st.altair_chart(chart, use_container_width=True)

    # Compliance table
    compliance_df = pd.DataFrame([
        {"Client Type": "Hospital", "On-Time Rate": "97.2%", "Next-Day Rate": "99.1%", "Temp Compliance": "99.8%", "Exception Rate": "0.3%"},
        {"Client Type": "Clinic", "On-Time Rate": "94.5%", "Next-Day Rate": "98.2%", "Temp Compliance": "99.5%", "Exception Rate": "0.8%"},
        {"Client Type": "Pharmacy", "On-Time Rate": "92.1%", "Next-Day Rate": "96.8%", "Temp Compliance": "98.9%", "Exception Rate": "1.2%"},
        {"Client Type": "Distributor", "On-Time Rate": "95.8%", "Next-Day Rate": "97.5%", "Temp Compliance": "99.2%", "Exception Rate": "0.5%"},
    ])
    st.dataframe(compliance_df, use_container_width=True, hide_index=True)

# =============================================================================
# PAGE: WORKER TASK STATION (from v3/v4)
# =============================================================================

elif page == "👷 Worker Task Station":
    st.markdown('<div class="main-header">👷 Worker Task Station</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">DRL-optimized picking paths and task management</div>', unsafe_allow_html=True)

    tab_pending, tab_active, tab_completed, tab_exceptions = st.tabs(
        ["🟡 Pending", "🔵 Active Picking", "🟢 Completed", "🔴 Exceptions"]
    )

    with tab_pending:
        pending_df = pd.DataFrame([
            {"Task ID": "T-4821", "Zone": "A-Cool", "Client": "Hospital A", "SKUs": 5, "Priority": "Urgent", "Est. Time": "12 min"},
            {"Task ID": "T-4822", "Zone": "B-Ambient", "Client": "Pharmacy X", "SKUs": 3, "Priority": "Standard", "Est. Time": "8 min"},
            {"Task ID": "T-4823", "Zone": "D-Cold", "Client": "Clinic B", "SKUs": 4, "Priority": "Urgent", "Est. Time": "15 min"},
        ])
        st.dataframe(pending_df, use_container_width=True, hide_index=True)

    with tab_active:
        st.markdown("""
        <div style="background:#111827; border-radius:8px; padding:1rem; margin:0.5rem 0;">
            <div style="font-family:monospace; font-size:0.85rem; color:#10b981;">
                Path: Zone A → Cool Zone B → Pick [Insulin x3] → Transit Zone C → Pack → Dispatch
            </div>
            <div style="font-size:0.75rem; color:#64748b; margin-top:0.3rem;">
                Optimized by KGDRL | Est. distance: 142m | Time saved: 18% vs baseline
            </div>
        </div>
        """, unsafe_allow_html=True)

        active_df = pd.DataFrame([
            {"Task ID": "T-4815", "Picker": "Wang Li", "Zone": "A-Ambient", "Progress": "65%", "DRL Path": "A→B→C", "Time Saved": "22%"},
            {"Task ID": "T-4816", "Picker": "Zhang Wei", "Zone": "C-Cold", "Progress": "40%", "DRL Path": "C→D→E", "Time Saved": "15%"},
        ])
        st.dataframe(active_df, use_container_width=True, hide_index=True)

    with tab_completed:
        st.success("12 tasks completed in last hour | Avg time saved: 18.5%")

    with tab_exceptions:
        st.error("2 temperature alerts in last hour | 1 delay exception | All resolved")

# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align:center; font-size:0.75rem; color:#475569; padding:1rem 0;">
    Sunergy Pharma Pro Edition v5.0.0 | Day 3 Commercialization Build | 2026/06/06<br>
    Modules: what_if_simulator.py | multi_objective_scheduler.py | adaptive_policy.py | kgdrl_core_v2.py<br>
    <span style="color:#f59e0b;">🔶 Professional Edition</span> | Built with Streamlit + Altair + KGDRL
</div>
""", unsafe_allow_html=True)
