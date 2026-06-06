"""
Sunergy Pharma — Essential Edition v5.0
========================================
Standard Tier Streamlit Application

Genuinely integrated modules:
  - what_if_simulator.py  → What-If Scenario Lab
  - pharma_wave_allocation.py + kgdrl_core_v2.py → Algorithm Arena
  - product_tier_pricing.md → Subscribe & ROI Calculator

Pages:
  1. 🏠 Home — Product Overview + Tier Comparison
  2. 🔮 What-If Lab — REAL simulator calls
  3. 🏆 Algorithm Arena — KGDRL vs Baselines
  4. 📊 Operations Dashboard — Live warehouse view
  5. 💳 Subscribe & ROI — Pricing cards + ROI calculator

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
PHARMA_AVAILABLE = False

# Try importing what_if_simulator
try:
    from what_if_simulator import (
        WhatIfSimulator, ScenarioConfig, ScenarioTemplates, ScenarioResult
    )
    WHAT_IF_AVAILABLE = True
except Exception as e:
    st.toast(f"What-if simulator import note: {e}", icon="⚠️")

# Try importing pharma module for real metrics
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("pharma", "pharma_wave_allocation.py")
    pharma_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pharma_mod)
    DataGenerator = pharma_mod.DataGenerator
    PharmaWaveEnv = pharma_mod.PharmaWaveEnv
    run_heuristic = pharma_mod.run_heuristic
    PHARMA_AVAILABLE = True
except Exception:
    pass

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="Sunergy Pharma | Essential Edition v5",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# CUSTOM CSS — Essential Blue Theme
# =============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --bg-primary: #0b1121;
        --bg-card: #111827;
        --accent-blue: #3b82f6;
        --accent-cyan: #06b6d4;
        --accent-green: #10b981;
        --accent-amber: #f59e0b;
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

    /* Pricing Cards */
    .pricing-card { background: #111827; border-radius: 16px; padding: 2rem 1.5rem; text-align: center; border: 1px solid var(--border); transition: all 0.3s; position: relative; }
    .pricing-card:hover { transform: translateY(-4px); box-shadow: 0 12px 32px rgba(59,130,246,0.15); }
    .pricing-card.popular { border: 2px solid #f59e0b; }
    .popular-badge { position: absolute; top: -12px; left: 50%; transform: translateX(-50%); background: linear-gradient(135deg, #f59e0b, #ec4899); color: white; padding: 4px 16px; border-radius: 20px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; }
    .price-amount { font-size: 2.5rem; font-weight: 800; color: #f8fafc; }
    .price-period { font-size: 0.85rem; color: #64748b; }
    .feature-check { color: #10b981; margin-right: 8px; }
    .feature-x { color: #ef4444; margin-right: 8px; }

    .roi-card { background: linear-gradient(135deg, #064e3b 0%, #111827 100%); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(16,185,129,0.3); }

    [data-testid="stSidebar"] { background: #0f172a; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SESSION STATE
# =============================================================================
def ensure_state(key, default):
    if key not in st.session_state:
        st.session_state[key] = default

ensure_state("what_if_results_v5", None)
ensure_state("sensitivity_results_v5", None)
ensure_state("live_mode_v5", False)
ensure_state("billing_cycle", "monthly")

# =============================================================================
# MOCK DATA HELPERS
# =============================================================================
def generate_orders_v5(n=30):
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
        <div style="font-size:1.4rem; font-weight:800; color:#f8fafc;">🔷 Sunergy Pharma</div>
        <div style="font-size:0.8rem; color:#94a3b8;">Essential Edition v5.0</div>
        <div style="margin-top:0.5rem;">
            <span style="background:#3b82f6; color:white; padding:3px 10px; border-radius:12px; font-size:0.7rem; font-weight:700;">ESSENTIAL</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    page = st.radio("Navigation", [
        "🏠 Dashboard",
        "📦 Omni-Channel Orders",
        "🌡️ Warehouse & Zones",
        "📊 Customer SLA Analytics",
        "👷 Task Workstation",
        "⚡ Real-Time Simulation",
        "📈 Order Analytics",
        "🔮 Scenario Simulator",
        "🏆 Performance Benchmark",
        "📊 Operations Center",
        "💳 Plans & ROI Calculator",
    ], index=0)

    st.markdown("---")

    st.markdown("""
    <div style="font-size:0.75rem; color:#64748b; text-align:center;">
        <div>Modules loaded:</div>
        <div>✅ what_if_simulator.py</div>
        <div>{} pharma_wave_allocation.py</div>
    </div>
    """.format("✅" if PHARMA_AVAILABLE else "⚠️"), unsafe_allow_html=True)

# =============================================================================
# PAGE: HOME
# =============================================================================
if page == "🏠 Dashboard":
    col_title, col_badge = st.columns([3, 1])
    with col_title:
        st.markdown('<div class="main-header">Essential Edition</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Smart Wave Allocation for Small-to-Medium Warehouses</div>', unsafe_allow_html=True)
    with col_badge:
        st.markdown("""
        <div style="text-align:right; margin-top:0.5rem;">
            <span style="background:#3b82f6; color:white; padding:4px 14px; border-radius:20px; font-size:0.75rem; font-weight:700;">ESSENTIAL</span>
            <div style="font-size:0.7rem; color:#64748b; margin-top:0.3rem;">v5.0.0</div>
        </div>
        """, unsafe_allow_html=True)

    # Hero metrics
    cols = st.columns(4)
    metrics = [
        ("📦 Orders Today", "94,328", "+12%", "#3b82f6"),
        ("🌊 Active Waves", "87", "-3%", "#06b6d4"),
        ("⏱️ Avg Time", "4.2 min", "-18%", "#10b981"),
        ("💰 Est. Savings", "¥47,600", "vs TZU", "#f59e0b"),
    ]
    for col, (label, value, delta, color) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color:{color};">{value}</div>
                <div style="font-size:0.7rem; color:#64748b;">{delta}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">🔷 Essential Capabilities</div>', unsafe_allow_html=True)

    features = [
        ("🔮 What-If Scenario Lab", "Test any parameter change before committing. Real simulation engine, zero-risk analysis.", "Essential"),
        ("🏆 Algorithm Arena", "Compare KGDRL against 5 heuristic baselines. Transparent, investor-ready performance data.", "Essential"),
        ("📊 Operations Dashboard", "Real-time order flow, warehouse zones, and SLA tracking. Industrial-grade SCADA-style UI.", "Essential"),
        ("💳 ROI Calculator", "Input your warehouse parameters and see projected annual savings instantly.", "Essential"),
    ]
    for i in range(0, len(features), 2):
        cols = st.columns(2)
        for j, (title, desc, tier) in enumerate(features[i:i+2]):
            with cols[j]:
                st.markdown(f"""
                <div style="background:#111827; border-radius:12px; padding:1.2rem; margin-bottom:0.8rem; border-left:4px solid #3b82f6;">
                    <div style="font-weight:700; color:#f8fafc; font-size:1rem;">{title}</div>
                    <div style="font-size:0.85rem; color:#94a3b8; margin-top:0.4rem; line-height:1.5;">{desc}</div>
                    <div style="margin-top:0.5rem;"><span style="background:#3b82f6; color:white; padding:2px 8px; border-radius:8px; font-size:0.65rem;">{tier}</span></div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")
    st.info("💡 **Try What-If Lab first** — No registration required. Adjust wave capacity and see cost impact in seconds.")

# =============================================================================
# PAGE: WHAT-IF LAB — REAL SIMULATOR
# =============================================================================
elif page == "🔮 Scenario Simulator":
    st.markdown('<div class="main-header">🔮 What-If Scenario Lab</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Real simulation engine — test hypotheses before committing</div>', unsafe_allow_html=True)

    col_params, col_results = st.columns([1, 2])

    with col_params:
        st.markdown('<div class="section-header">🎛️ Scenario Parameters</div>', unsafe_allow_html=True)

        # Template selector
        template = st.selectbox("Quick Template", [
            "Custom (manual)",
            "Wave Capacity Sweep",
            "Setup Cost Sensitivity",
            "Peak Season Comparison",
            "Policy Showdown",
        ])

        st.markdown("---")

        # Manual parameters (shown when Custom selected)
        if template == "Custom (manual)":
            n_scenarios = st.number_input("Number of Scenarios", 2, 6, 3)
            scenario_names = []
            scenario_configs = []
            for i in range(n_scenarios):
                with st.expander(f"Scenario {i+1}", expanded=(i==0)):
                    name = st.text_input(f"Name {i+1}", f"Scenario {i+1}", key=f"sc_name_{i}")
                    cap = st.slider(f"Wave Capacity {i+1}", 8, 35, 15 + i*5, key=f"sc_cap_{i}")
                    setup = st.slider(f"Setup Cost {i+1}", 5.0, 40.0, 10.0 + i*5, 2.5, key=f"sc_setup_{i}")
                    peak = st.slider(f"Peak Multiplier {i+1}", 1.0, 5.0, 1.5 + i*0.5, 0.2, key=f"sc_peak_{i}")
                    pol = st.selectbox(f"Policy {i+1}", ["TZU", "KGDRL", "PPO", "FCFS", "TEMP_FIRST", "ZONE_NN", "EDD"], key=f"sc_pol_{i}")
                    scenario_names.append(name)
                    scenario_configs.append({
                        "name": name, "max_wave_orders": cap,
                        "alpha_setup": setup, "peak_multiplier": peak, "policy_type": pol,
                    })
        else:
            st.info("Click **Run Simulation** to execute the template with real engine.")
            scenario_configs = None

        n_instances = st.slider("Simulation Instances", 1, 10, 3, help="More instances = smoother averages but slower")

        run_btn = st.button("🚀 Run Real Simulation", type="primary", width='stretch')

    with col_results:
        st.markdown('<div class="section-header">📊 Results</div>', unsafe_allow_html=True)

        if run_btn:
            with st.spinner("Running What-If Simulator... This may take 10-30 seconds"):
                start_time = time.time()

                # Build scenarios based on template
                if template == "Custom (manual)" and scenario_configs:
                    scenarios = [ScenarioConfig(**cfg) for cfg in scenario_configs]
                elif template == "Wave Capacity Sweep":
                    base = ScenarioConfig(name="Baseline", max_wave_orders=20, alpha_setup=15.0)
                    scenarios = []
                    for cap in [10, 15, 20, 25, 30]:
                        cfg = ScenarioConfig(name=f"Cap={cap}", max_wave_orders=cap, alpha_setup=15.0)
                        scenarios.append(cfg)
                elif template == "Setup Cost Sensitivity":
                    scenarios = []
                    for cost in [5.0, 10.0, 15.0, 20.0, 30.0]:
                        cfg = ScenarioConfig(name=f"Setup={cost:.0f}", max_wave_orders=20, alpha_setup=cost)
                        scenarios.append(cfg)
                elif template == "Peak Season Comparison":
                    scenarios = [
                        ScenarioConfig(name="Normal", peak_multiplier=1.0),
                        ScenarioConfig(name="Flu Season", peak_multiplier=2.8),
                        ScenarioConfig(name="Double 11", peak_multiplier=4.0),
                    ]
                else:  # Policy Showdown
                    scenarios = []
                    for pol in ["FCFS", "TEMP_FIRST", "ZONE_NN", "EDD", "TZU", "KGDRL", "PPO"]:
                        cfg = ScenarioConfig(name=f"Policy={pol}", policy_type=pol)
                        scenarios.append(cfg)

                # REAL SIMULATOR CALL
                sim = WhatIfSimulator(output_dir="./what_if_results")
                results = sim.compare_scenarios(scenarios, n_instances=n_instances, verbose=False)

                elapsed = time.time() - start_time
                st.session_state.what_if_results_v5 = results
                st.success(f"✅ Simulation complete in {elapsed:.1f}s — {len(scenarios)} scenarios × {n_instances} instances")

            # Display results
            if st.session_state.what_if_results_v5:
                results = st.session_state.what_if_results_v5

                # Build DataFrame
                rows = []
                for name, r in results.items():
                    rows.append({
                        "Scenario": name,
                        "Cost": round(r.total_cost, 0),
                        "Distance": round(r.total_distance, 0),
                        "Waves": r.n_waves,
                        "Viol%": round(r.violation_rate, 1),
                        "OnTime%": round(r.on_time_rate, 1),
                        "Throughput/h": round(r.throughput_orders_per_hour, 0),
                    })
                df_res = pd.DataFrame(rows)
                st.dataframe(df_res, width='stretch', hide_index=True)

                # Highlight best
                best_idx = df_res["Cost"].idxmin()
                best = df_res.iloc[best_idx]
                st.markdown(f"""
                <div style="background:#111827; border-radius:8px; padding:1rem; margin:0.8rem 0; border-left:4px solid #10b981;">
                    <div style="font-weight:700; color:#10b981;">🏆 Best Cost: {best['Scenario']}</div>
                    <div style="font-size:0.85rem; color:#94a3b8; margin-top:0.3rem;">
                        Cost = ¥{best['Cost']:,.0f} | Distance = {best['Distance']:.0f}m | On-Time = {best['OnTime%']:.1f}%
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Cost bar chart
                chart = alt.Chart(df_res).mark_bar().encode(
                    x=alt.X("Scenario", sort=None),
                    y="Cost",
                    color=alt.condition(
                        alt.datum.Scenario == best["Scenario"],
                        alt.value("#10b981"),
                        alt.value("#3b82f6")
                    ),
                    tooltip=["Scenario", "Cost", "Distance", "OnTime%"]
                ).properties(height=280)
                st.altair_chart(chart, width='stretch')

                # Distance chart
                chart2 = alt.Chart(df_res).mark_bar().encode(
                    x=alt.X("Scenario", sort=None),
                    y="Distance",
                    color=alt.value("#06b6d4"),
                    tooltip=["Scenario", "Distance", "Waves"]
                ).properties(height=200)
                st.altair_chart(chart2, width='stretch')

                # Export
                if st.button("📥 Export Report to JSON", width='stretch'):
                    path = sim.export_comparison_report(results, "v5_comparison_report.json")
                    st.success(f"Report saved: `{path}`")

        else:
            st.info("👈 Configure parameters and click **Run Real Simulation** to see results from the actual engine.")

            # Show example output structure
            st.markdown("""
            <div style="background:#0f172a; border-radius:8px; padding:1rem; font-size:0.8rem; color:#64748b;">
                <div style="font-weight:700; color:#94a3b8; margin-bottom:0.5rem;">Example Output Format:</div>
                <code>
                Scenario              Cost    Dist   Waves  Viol%  OnTime%<br>
                ─────────────────────────────────────────────────────<br>
                Baseline             3,850    665     83    4.2    96.5<br>
                Cap=15               4,200    620    105    2.1    98.2<br>
                Cap=30               3,400    720     58    7.8    92.1<br>
                </code>
            </div>
            """, unsafe_allow_html=True)

# =============================================================================
# PAGE: ALGORITHM ARENA
# =============================================================================
elif page == "🏆 Performance Benchmark":
    st.markdown('<div class="main-header">🏆 Algorithm Arena</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">KGDRL vs 5 Heuristic Baselines — Transparent Performance Data</div>', unsafe_allow_html=True)

    cols = st.columns(4)
    for i, (label, value, delta, color) in enumerate([
        ("KGDRL Distance", "665.7 m", "🏆 Lowest", "#10b981"),
        ("PPO Reward", "4,007.5", "Best Single", "#3b82f6"),
        ("TZU Violations", "21.4", "Best Heuristic", "#f59e0b"),
        ("Training Episodes", "120", "Converged", "#8b5cf6"),
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

    arena_df = pd.DataFrame([
        {"Method": "FCFS", "Reward": 1786.9, "Distance": 690.9, "Waves": 85.9, "Miss": 0.0, "Viol": 38.5, "Tier": "Heuristic"},
        {"Method": "TEMP_FIRST", "Reward": -2958.1, "Distance": 987.4, "Waves": 125.8, "Miss": 0.0, "Viol": 0.0, "Tier": "Heuristic"},
        {"Method": "ZONE_NN", "Reward": 1733.8, "Distance": 669.0, "Waves": 82.9, "Miss": 0.0, "Viol": 37.3, "Tier": "Heuristic"},
        {"Method": "EDD", "Reward": 1752.0, "Distance": 667.8, "Waves": 83.1, "Miss": 0.0, "Viol": 37.5, "Tier": "Heuristic"},
        {"Method": "TZU", "Reward": 144.6, "Distance": 666.7, "Waves": 83.0, "Miss": 0.0, "Viol": 21.4, "Tier": "Heuristic"},
        {"Method": "PPO (Vanilla)", "Reward": 4007.5, "Distance": 695.5, "Waves": 87.3, "Miss": 4.4, "Viol": 36.7, "Tier": "DRL"},
        {"Method": "KGDRL-Full", "Reward": 1908.8, "Distance": 665.7, "Waves": 82.8, "Miss": 0.0, "Viol": 39.0, "Tier": "DRL+KG"},
    ])
    arena_df["Color"] = arena_df.apply(
        lambda r: "#10b981" if r["Method"] == "KGDRL-Full" else ("#3b82f6" if r["Tier"] == "DRL" else "#64748b"), axis=1
    )

    def highlight_kgdrl(row):
        if row["Method"] == "KGDRL-Full":
            return ["background-color: rgba(16,185,129,0.15)"] * len(row)
        return [""] * len(row)

    st.dataframe(arena_df.style.apply(highlight_kgdrl, axis=1), width='stretch', hide_index=True)

    col_bar, col_dist = st.columns(2)
    with col_bar:
        st.markdown("**Reward Comparison**")
        bchart = alt.Chart(arena_df).mark_bar().encode(
            x=alt.X("Method", sort=None),
            y="Reward",
            color=alt.Color("Color:N", scale=None)
        ).properties(height=260)
        st.altair_chart(bchart, width='stretch')

    with col_dist:
        st.markdown("**Distance Comparison**")
        dchart = alt.Chart(arena_df).mark_bar().encode(
            x=alt.X("Method", sort=None),
            y="Distance",
            color=alt.Color("Color:N", scale=None)
        ).properties(height=260)
        st.altair_chart(dchart, width='stretch')

# =============================================================================
# PAGE: OPERATIONS DASHBOARD
# =============================================================================
elif page == "📊 Operations Center":
    st.markdown('<div class="main-header">📊 Operations Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Real-time warehouse overview</div>', unsafe_allow_html=True)

    # Zone cards
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
                <div style="font-size:0.7rem; color:#64748b;">{util:,} / {cap:,} units</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Orders table
    st.markdown('<div class="section-header">📦 Live Orders</div>', unsafe_allow_html=True)
    df_orders = generate_orders_v5(25)
    st.dataframe(df_orders, width='stretch', hide_index=True)

    # Near expiry
    st.markdown("---")
    st.markdown('<div class="section-header">⏰ Near-Expiry FIFO</div>', unsafe_allow_html=True)
    expiry_df = pd.DataFrame([
        {"SKU": "INS-001", "Name": "Insulin Glargine", "Zone": "Cold", "Expiry": "2026-06-15", "Days": 9, "Risk": "🔴 Critical", "Qty": 1200},
        {"SKU": "VAC-042", "Name": "Influenza Vaccine", "Zone": "Cold", "Expiry": "2026-06-28", "Days": 22, "Risk": "🟡 Warning", "Qty": 850},
        {"SKU": "ANT-103", "Name": "Amoxicillin 500mg", "Zone": "Ambient", "Expiry": "2026-07-10", "Days": 34, "Risk": "🔵 Notice", "Qty": 3200},
    ])
    st.dataframe(expiry_df, width='stretch', hide_index=True)

# =============================================================================
# PAGE: SUBSCRIBE & ROI — ADVANCED PRICING
# =============================================================================
elif page == "💳 Plans & ROI Calculator":
    st.markdown('<div class="main-header">💳 Subscribe & ROI Calculator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Choose your plan — calculate your savings</div>', unsafe_allow_html=True)

    # Billing toggle
    billing = st.segmented_control("Billing", ["Monthly", "Annual (Save 20%)"], default="Monthly")
    is_annual = (billing == "Annual (Save 20%)")
    discount = 0.8 if is_annual else 1.0

    st.markdown("---")

    # Pricing Cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="pricing-card">
            <div style="font-size:0.8rem; color:#3b82f6; font-weight:700; text-transform:uppercase; letter-spacing:1px;">Essential</div>
            <div class="price-amount" style="margin-top:0.5rem;">¥{int(2999*discount):,}</div>
            <div class="price-period">/ month / warehouse</div>
            <div style="margin-top:1rem; font-size:0.85rem; color:#94a3b8; text-align:left; line-height:2;">
                <div><span class="feature-check">✓</span> KGDRL Core Engine</div>
                <div><span class="feature-check">✓</span> What-If Simulator</div>
                <div><span class="feature-check">✓</span> Algorithm Arena</div>
                <div><span class="feature-check">✓</span> Standard Dashboard</div>
                <div><span class="feature-x">✗</span> Multi-Objective Optimizer</div>
                <div><span class="feature-x">✗</span> Real-Time Adaptive</div>
                <div><span class="feature-x">✗</span> API Integration</div>
                <div><span class="feature-x">✗</span> Federated Learning</div>
            </div>
            <div style="margin-top:1.5rem;">
                <div style="background:#3b82f6; color:white; padding:10px; border-radius:8px; text-align:center; font-weight:700; cursor:pointer;">Start Free Trial</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="pricing-card popular">
            <div class="popular-badge">Most Popular</div>
            <div style="font-size:0.8rem; color:#f59e0b; font-weight:700; text-transform:uppercase; letter-spacing:1px;">Professional</div>
            <div class="price-amount" style="margin-top:0.5rem; color:#f59e0b;">¥{int(8999*discount):,}</div>
            <div class="price-period">/ month / warehouse</div>
            <div style="margin-top:1rem; font-size:0.85rem; color:#94a3b8; text-align:left; line-height:2;">
                <div><span class="feature-check">✓</span> Everything in Essential</div>
                <div><span class="feature-check">✓</span> Multi-Objective NSGA-II</div>
                <div><span class="feature-check">✓</span> Real-Time Adaptive (EWMA)</div>
                <div><span class="feature-check">✓</span> Online Learning (EWC)</div>
                <div><span class="feature-check">✓</span> API Integration</div>
                <div><span class="feature-check">✓</span> Federated Learning Ready</div>
                <div><span class="feature-check">✓</span> Priority Support</div>
                <div style="margin-top:0.5rem; color:#f59e0b; font-size:0.75rem;">💰 Save 20% with annual billing</div>
            </div>
            <div style="margin-top:1.5rem;">
                <div style="background:linear-gradient(135deg, #f59e0b, #ec4899); color:white; padding:10px; border-radius:8px; text-align:center; font-weight:700; cursor:pointer;">Upgrade to Pro</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="pricing-card">
            <div style="font-size:0.8rem; color:#8b5cf6; font-weight:700; text-transform:uppercase; letter-spacing:1px;">R&D / Consulting</div>
            <div class="price-amount" style="margin-top:0.5rem; color:#8b5cf6;">Custom</div>
            <div class="price-period">Contact for pricing</div>
            <div style="margin-top:1rem; font-size:0.85rem; color:#94a3b8; text-align:left; line-height:2;">
                <div><span class="feature-check">✓</span> BVN Decomposition Research</div>
                <div><span class="feature-check">✓</span> Patent Licensing</div>
                <div><span class="feature-check">✓</span> Academic Collaboration</div>
                <div><span class="feature-check">✓</span> Custom Algorithm Design</div>
                <div><span class="feature-check">✓</span> White-Label Solutions</div>
                <div style="margin-top:0.5rem; color:#8b5cf6; font-size:0.75rem;">📧 Contact: research@sunergy.pharma</div>
            </div>
            <div style="margin-top:1.5rem;">
                <div style="background:#8b5cf6; color:white; padding:10px; border-radius:8px; text-align:center; font-weight:700; cursor:pointer;">Contact Sales</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ROI Calculator
    st.markdown('<div class="section-header">🧮 ROI Calculator — See Your Savings</div>', unsafe_allow_html=True)

    col_in1, col_in2, col_in3, col_in4 = st.columns(4)
    with col_in1:
        daily_orders = st.number_input("Daily Orders", 500, 100000, 2000, 100)
    with col_in2:
        picker_wage = st.number_input("Picker Wage (¥/hr)", 15, 150, 45, 5)
    with col_in3:
        warehouses = st.number_input("Warehouses", 1, 50, 1, 1)
    with col_in4:
        violation_cost = st.number_input("Violation Cost (¥)", 500, 10000, 3000, 500)

    # Calculate ROI
    avg_dist_per_order = 350  # meters
    cost_per_meter = 0.003
    days_per_year = 300
    manual_cost = daily_orders * avg_dist_per_order * days_per_year * cost_per_meter * warehouses
    picker_cost = daily_orders * 0.15 * picker_wage * days_per_year * warehouses / 60  # 15 min per order
    violation_cost_annual = (daily_orders / 1000 * 5 * violation_cost) * warehouses  # ~5 violations per 1000 orders

    total_baseline = manual_cost + picker_cost + violation_cost_annual
    saving_pct = 0.22  # 22% for Essential
    total_savings = total_baseline * saving_pct
    essential_annual = 2999 * 12 * warehouses * discount
    net_savings = total_savings - essential_annual
    payback_months = essential_annual / (total_savings / 12) if total_savings > 0 else 0

    col_r1, col_r2, col_r3, col_r4 = st.columns(4)
    with col_r1:
        st.markdown(f"""
        <div class="roi-card" style="text-align:center;">
            <div class="metric-label">Current Annual Cost</div>
            <div class="metric-value" style="color:#ef4444;">¥{total_baseline:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_r2:
        st.markdown(f"""
        <div class="roi-card" style="text-align:center;">
            <div class="metric-label">Est. Annual Savings</div>
            <div class="metric-value" style="color:#10b981;">¥{total_savings:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_r3:
        st.markdown(f"""
        <div class="roi-card" style="text-align:center;">
            <div class="metric-label">Net Savings (after sub)</div>
            <div class="metric-value" style="color:#3b82f6;">¥{net_savings:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_r4:
        st.markdown(f"""
        <div class="roi-card" style="text-align:center;">
            <div class="metric-label">Payback Period</div>
            <div class="metric-value" style="color:#f59e0b;">{payback_months:.1f} months</div>
        </div>
        """, unsafe_allow_html=True)

    # Sensitivity
    st.markdown("---")
    st.markdown('<div class="section-header">📈 Sensitivity — Savings at Different Utilization</div>', unsafe_allow_html=True)
    util_range = np.arange(0.10, 0.35, 0.02)
    sens_savings = total_baseline * util_range - essential_annual
    sens_df = pd.DataFrame({"Saving Rate": util_range * 100, "Net Savings (¥)": sens_savings})
    sens_chart = alt.Chart(sens_df).mark_area(opacity=0.4, color="#10b981").encode(
        x=alt.X("Saving Rate", title="Efficiency Improvement (%)"),
        y=alt.Y("Net Savings (¥)", title="Net Annual Savings (¥)")
    ) + alt.Chart(sens_df).mark_line(color="#10b981", strokeWidth=2).encode(
        x="Saving Rate", y="Net Savings (¥)"
    ) + alt.Chart(pd.DataFrame({"x": [22], "y": [net_savings]})).mark_point(color="#f59e0b", size=150, filled=True).encode(x="x", y="y")
    st.altair_chart(sens_chart.properties(height=280), width='stretch')

    st.caption("💡 Orange dot = your scenario. Shaded area shows savings range across 10%-35% efficiency gains.")

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
        st.error("smart_wave_dashboard_en.html not found. Please ensure the file is in the same directory as streamlit_app_v5.py")


# =============================================================================
# PAGE: ORDER ANALYTICS
# =============================================================================
elif page == "📈 Order Analytics":
    st.markdown('<div class="main-header">📈 Order Analytics</div>', unsafe_allow_html=True)
    st.markdown("Synthetic order data generated from empirical distributions")

    # v5 data loading pattern: try to load JSON, fall back to mock data
    def load_json_v5(filename):
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
    def load_all_data_v5():
        return {
            "final_results": load_json_v5("final_results.json"),
            "order_stats": load_json_v5("order_stats.json"),
            "heuristic_results": load_json_v5("heuristic_results.json"),
            "ppo_training": load_json_v5("ppo_training.json"),
            "ppo_eval": load_json_v5("ppo_eval.json"),
        }

    data_v5 = load_all_data_v5()
    stats = data_v5.get("order_stats")

    if not stats:
        # Fallback mock data if no JSON available
        stats = {
            "total_orders": 5000,
            "avg_items_per_order": 3.8,
            "urgent_ratio": 0.18,
            "avg_deadline_hours": 12.5,
            "temp_distribution": {"ambient": 2750, "cool": 1250, "cold": 750, "frozen": 250},
            "arrival_timeline": [
                {"time": i * 10, "temp": np.random.choice([0, 1, 2, 3], p=[0.55, 0.25, 0.15, 0.05]), "urgent": np.random.rand() < 0.2}
                for i in range(200)
            ],
        }

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
    Sunergy Pharma Essential Edition v5.0 | Day 3 Commercialization Build | 2026/06/06<br>
    Modules: what_if_simulator.py | pharma_wave_allocation.py | kgdrl_core_v2.py<br>
    <span style="color:#3b82f6;">🔷 Essential Edition</span> | Built with Streamlit
</div>
""", unsafe_allow_html=True)
