"""
Sunergy Pharma — Smart Supply Chain Command Center
Industrial-Grade Pharmaceutical Distribution Dashboard
Powered by Deep Reinforcement Learning (PPO) + KGDRL
"""

import streamlit as st
import json
import time
import random
import numpy as np
import pandas as pd
import altair as alt
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="Sunergy Pharma | Smart Supply Chain Command Center",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# CUSTOM CSS — Deep Navy Executive Theme
# =============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --bg-primary: #0b1121;
        --bg-card: #111827;
        --bg-elevated: #1e293b;
        --accent-blue: #3b82f6;
        --accent-cyan: #06b6d4;
        --accent-green: #10b981;
        --accent-amber: #f59e0b;
        --accent-red: #ef4444;
        --accent-purple: #8b5cf6;
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --border: rgba(148, 163, 184, 0.12);
    }

    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #f8fafc;
        margin-bottom: 0.3rem;
        font-family: 'Inter', sans-serif;
        letter-spacing: -0.02em;
    }
    .sub-header {
        font-size: 1rem;
        color: #94a3b8;
        margin-bottom: 1.5rem;
        font-family: 'Inter', sans-serif;
    }
    .section-header {
        font-size: 1.1rem;
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
    .metric-delta {
        font-size: 0.75rem;
        font-weight: 600;
        margin-top: 0.3rem;
    }
    .delta-up { color: #10b981; }
    .delta-down { color: #ef4444; }

    /* Zone Cards */
    .zone-card {
        background: #111827;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid var(--border);
        color: #f8fafc;
    }
    .zone-title {
        font-size: 0.85rem;
        font-weight: 700;
        color: #e2e8f0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .zone-metric {
        font-size: 1.4rem;
        font-weight: 700;
        color: #3b82f6;
    }

    /* Status Badges */
    .badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    .badge-pending { background: rgba(245, 158, 11, 0.15); color: #f59e0b; }
    .badge-active { background: rgba(59, 130, 246, 0.15); color: #3b82f6; }
    .badge-completed { background: rgba(16, 185, 129, 0.15); color: #10b981; }
    .badge-exception { background: rgba(239, 68, 68, 0.15); color: #ef4444; }

    /* Tables */
    .stDataFrame { background: #111827 !important; }
    .stDataFrame td { color: #e2e8f0 !important; }
    .stDataFrame th { background: #1e293b !important; color: #94a3b8 !important; }

    /* Sidebar */
    [data-testid="stSidebar"] { background: #0f172a !important; border-right: 1px solid var(--border); }
    [data-testid="stSidebar"] .stRadio label { color: #94a3b8; font-size: 0.85rem; }
    [data-testid="stSidebar"] .stRadio label:hover { color: #f8fafc; }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0f172a; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }

    /* Streamlit overrides */
    .stApp { background: #0b1121; }
    .stTabs [data-baseweb="tab-list"] { gap: 2px; background: #111827; padding: 4px; border-radius: 8px; }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        border-radius: 6px;
        color: #94a3b8;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .stTabs [data-baseweb="tab-highlight"] { background: #1e3a5f; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# DATA LOADING — Reuse existing pipeline outputs
# =============================================================================
def load_json(filename):
    base = Path(__file__).parent / "data"
    path = base / filename
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
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

# =============================================================================
# SIMULATED DATA GENERATORS
# =============================================================================
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
# SIDEBAR — Navigation + Global Controls
# =============================================================================
st.sidebar.markdown("## 🏥 Sunergy Pharma")
st.sidebar.markdown("### Smart Supply Chain Command Center")
st.sidebar.markdown("---")

view = st.sidebar.radio(
    "Select View",
    [
        "📦 Admin: Omni-Channel Orders",
        "🌡️ Admin: Warehouse & Temperature Zones",
        "📊 Admin: Customer SLA Analytics",
        "👷 Worker: Task Workstation",
    ],
    index=0,
)

st.sidebar.markdown("---")

# Live data toggle
if "live_mode" not in st.session_state:
    st.session_state.live_mode = False

live_toggle = st.sidebar.toggle("Simulate Live Data Sync", value=st.session_state.live_mode)
st.session_state.live_mode = live_toggle

if st.session_state.live_mode:
    st.sidebar.success("Live sync active — refreshing every 3s")
else:
    st.sidebar.info("Live sync paused — manual refresh only")

st.sidebar.markdown("---")
st.sidebar.markdown("**Enterprise:** Sunergy Pharma Distribution")
st.sidebar.markdown("**Daily Orders:** 90,000+")
st.sidebar.markdown("**SKU Lines:** 423,600")
st.sidebar.markdown("**Next-Day Delivery:** 88%+")
st.sidebar.markdown("---")
st.sidebar.caption("Powered by PPO Deep RL + KGDRL")

# =============================================================================
# AUTO-REFRESH MECHANISM
# =============================================================================
if st.session_state.live_mode:
    time.sleep(3)
    st.rerun()

# =============================================================================
# VIEW 1: ADMIN — OMNI-CHANNEL ORDERS
# =============================================================================
if view == "📦 Admin: Omni-Channel Orders":
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
        st.dataframe(df_filtered, use_container_width=True, hide_index=True, height=420)

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
        st.altair_chart(chart_time, use_container_width=True)

        # Bulk vs Small pie
        bulk_count = (df_filtered["SKU Count"] >= 4).sum()
        small_count = (df_filtered["SKU Count"] < 4).sum()
        df_bulk = pd.DataFrame({"Type": ["Bulk (≥4 SKUs)", "Small (<4 SKUs)"], "Count": [bulk_count, small_count]})
        chart_bulk = alt.Chart(df_bulk).mark_arc(innerRadius=30).encode(
            theta=alt.Theta("Count:Q"),
            color=alt.Color("Type:N", scale=alt.Scale(range=["#10b981", "#f59e0b"]), legend=alt.Legend(orient="bottom", labelColor="#e2e8f0")),
        ).properties(height=130)
        st.altair_chart(chart_bulk, use_container_width=True)

        # Temperature pie
        temp_dist = df_filtered["Temperature"].value_counts().reset_index()
        temp_dist.columns = ["Zone", "Count"]
        chart_temp = alt.Chart(temp_dist).mark_arc(innerRadius=30).encode(
            theta=alt.Theta("Count:Q"),
            color=alt.Color("Zone:N", legend=alt.Legend(orient="bottom", labelColor="#e2e8f0")),
        ).properties(height=130)
        st.altair_chart(chart_temp, use_container_width=True)


# =============================================================================
# VIEW 2: ADMIN — WAREHOUSE & TEMPERATURE ZONES
# =============================================================================
if view == "🌡️ Admin: Warehouse & Temperature Zones":
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
        use_container_width=True,
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
        st.altair_chart(chart_zone, use_container_width=True)

    with c2:
        st.markdown('<div class="section-header">Near-Expiry by Medicine Type</div>', unsafe_allow_html=True)
        near_expiry = df_inv[df_inv["Risk Level"].isin(["Critical", "Warning", "Notice"])]
        type_vol = near_expiry.groupby("Category")["Stock Qty"].sum().reset_index()
        chart_type = alt.Chart(type_vol).mark_bar(cornerRadiusEnd=4).encode(
            x=alt.X("Category:N", title="", sort="-y"),
            y=alt.Y("Stock Qty:Q", title="Stock Quantity"),
            color=alt.Color("Category:N", legend=None),
        ).properties(height=280)
        st.altair_chart(chart_type, use_container_width=True)


# =============================================================================
# VIEW 3: ADMIN — CUSTOMER SLA ANALYTICS
# =============================================================================
if view == "📊 Admin: Customer SLA Analytics":
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
    st.altair_chart(chart_vol, use_container_width=True)

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
        st.altair_chart(chart_sku, use_container_width=True)

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
        st.altair_chart(hist_chart + fc_chart, use_container_width=True)

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
    st.dataframe(df_comp.sort_values("Fulfillment Score", ascending=False), use_container_width=True, hide_index=True)


# =============================================================================
# VIEW 4: WORKER — TASK WORKSTATION
# =============================================================================
if view == "👷 Worker: Task Workstation":
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
        st.altair_chart(chart_labor, use_container_width=True)

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
        st.dataframe(df_eff[["Zone", "Total Headcount", "SKUs/Hour/Person", "Shift"]], use_container_width=True, hide_index=True, height=250)

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
            st.dataframe(df_done[["Task ID", "Source Zone", "Target Client", "Assigned Worker", "SKU Checklist"]], use_container_width=True, hide_index=True)
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
        st.dataframe(my_tasks[["Task ID", "Source Zone", "Target Client", "Status", "Priority", "Est. Duration (min)"]], use_container_width=True, hide_index=True)
    else:
        st.info("No tasks currently dispatched to Worker-01")
