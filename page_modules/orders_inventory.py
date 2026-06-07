"""
Sunergy Pharma — Orders & Inventory Module
============================================
Pages:
  - Omni-Channel Orders
  - Order Analytics
  - Warehouse & Temperature Zones

NOTE: All UI text is English. Each page is a standalone render_* function.
Remove any function (and its sidebar entry) to drop the page.
"""

import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
from datetime import datetime
from .shared import (
    get_orders_data, get_inventory_data, get_orders_basic,
    load_all_json_data, TEMP_ZONES, TEMP_COLORS, ZONE_LETTERS, CLIENT_TYPES
)


# =============================================================================
# PAGE: Omni-Channel Orders
# =============================================================================

def render_omnichannel_orders():
    st.markdown('<div class="main-header">Omni-Channel Orders</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Real-time order intake, dispatch status, and channel analytics</div>', unsafe_allow_html=True)

    # --- Summary Metrics Block ---
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

    # --- Filters ---
    st.markdown('<div class="section-header">Filters & Segment Controls</div>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1:
        filter_client = st.multiselect("Client Category", CLIENT_TYPES, default=CLIENT_TYPES)
    with f2:
        filter_time = st.multiselect("Time Window", ["Morning Peak", "Afternoon", "Night Peak"],
                                     default=["Morning Peak", "Afternoon", "Night Peak"])
    with f3:
        filter_temp = st.multiselect("Temperature Attribute", TEMP_ZONES, default=TEMP_ZONES)

    df_orders = get_orders_data(n=100, seed=int(datetime.now().timestamp()) // 10)
    df_filtered = df_orders[
        df_orders["Client Type"].isin(filter_client) &
        df_orders["Time Window"].isin(filter_time) &
        df_orders["Temperature"].isin(filter_temp)
    ]

    st.markdown("---")

    # --- Three-column layout ---
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

        time_dist = df_filtered["Time Window"].value_counts().reindex(["Morning Peak", "Afternoon", "Night Peak"], fill_value=0).reset_index()
        time_dist.columns = ["Window", "Count"]
        # NOTE: height increased to accommodate bottom legends and labels
        chart_time = alt.Chart(time_dist).mark_bar(color="#3b82f6", cornerRadiusEnd=4).encode(
            x=alt.X("Window:N", title="", sort=["Morning Peak", "Afternoon", "Night Peak"],
                    axis=alt.Axis(labelAngle=0, labelLimit=120)),
            y=alt.Y("Count:Q", title="Orders"),
        ).properties(height=160)
        st.altair_chart(chart_time, use_container_width=True)

        bulk_count = (df_filtered["SKU Count"] >= 4).sum()
        small_count = (df_filtered["SKU Count"] < 4).sum()
        df_bulk = pd.DataFrame({"Type": ["Bulk (>=4 SKUs)", "Small (<4 SKUs)"], "Count": [bulk_count, small_count]})
        chart_bulk = alt.Chart(df_bulk).mark_arc(innerRadius=35).encode(
            theta=alt.Theta("Count:Q"),
            color=alt.Color("Type:N", scale=alt.Scale(range=["#10b981", "#f59e0b"]),
                           legend=alt.Legend(orient="bottom", labelColor="#e2e8f0", title=None)),
        ).properties(height=190)
        st.altair_chart(chart_bulk, use_container_width=True)

        temp_dist = df_filtered["Temperature"].value_counts().reset_index()
        temp_dist.columns = ["Zone", "Count"]
        chart_temp = alt.Chart(temp_dist).mark_arc(innerRadius=35).encode(
            theta=alt.Theta("Count:Q"),
            color=alt.Color("Zone:N", legend=alt.Legend(orient="bottom", labelColor="#e2e8f0", title=None)),
        ).properties(height=190)
        st.altair_chart(chart_temp, use_container_width=True)


# =============================================================================
# PAGE: Order Analytics
# =============================================================================

def render_order_analytics():
    st.markdown('<div class="main-header">Order Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Synthetic order data generated from empirical distributions</div>', unsafe_allow_html=True)

    data = load_all_json_data()
    stats = data.get("order_stats")

    if not stats:
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
    st.markdown("### Temperature Distribution")

    temp_dist = stats.get("temp_distribution", {})
    temp_names = {"ambient": "Ambient", "cool": "Cool", "cold": "Cold", "frozen": "Frozen", 0: "Ambient", 1: "Cool", 2: "Cold", 3: "Frozen"}

    if temp_dist:
        temp_df = pd.DataFrame([
            {"Category": temp_names.get(k, k), "Count": v,
             "Percentage": v / max(stats.get("total_orders", 1), 1) * 100}
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

    st.markdown("---")
    st.markdown("### Order Arrival Timeline")

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
            color=alt.Color("urgent_label:N", scale=alt.Scale(domain=["Standard", "Urgent"], range=["#2ca02c", "#d62728"]), title="Priority"),
            tooltip=["time", "temp_name", "urgent_label"]
        ).properties(height=300, title="Order Priority Over Time")
        st.altair_chart(urgent_chart)

    st.markdown("---")
    st.markdown("### Generation Parameters")
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
# PAGE: Warehouse & Temperature Zones
# =============================================================================

def render_warehouse_zones():
    st.markdown('<div class="main-header">Warehouse & Temperature Zones</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Zone capacity, inventory health, and near-expiry FIFO control</div>', unsafe_allow_html=True)

    zones = [
        ("Ambient", "15-25 degC", TEMP_COLORS["Ambient"], 85),
        ("Cool", "8-15 degC", TEMP_COLORS["Cool"], 72),
        ("Cold", "2-8 degC", TEMP_COLORS["Cold"], 68),
        ("Frozen", "-15 to -5 degC", TEMP_COLORS["Frozen"], 55),
        ("Deep Frozen", "<=-20 degC", TEMP_COLORS["Deep Frozen"], 42),
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

    st.markdown('<div class="section-header">Near-Expiry Inventory Control (FIFO)</div>', unsafe_allow_html=True)
    df_inv = get_inventory_data(seed=int(datetime.now().timestamp()) // 30)

    def highlight_risk(row):
        if row["Risk Level"] == "Critical":
            return ["background-color: rgba(239, 68, 68, 0.12); color: #f87171"] * len(row)
        elif row["Risk Level"] == "Warning":
            return ["background-color: rgba(245, 158, 11, 0.12); color: #fbbf24"] * len(row)
        elif row["Risk Level"] == "Notice":
            return ["background-color: rgba(59, 130, 246, 0.12); color: #60a5fa"] * len(row)
        return [""] * len(row)

    st.dataframe(df_inv.style.apply(highlight_risk, axis=1), hide_index=True, height=350)

    risk_counts = df_inv["Risk Level"].value_counts().to_dict()
    r1, r2, r3, r4 = st.columns(4)
    with r1:
        st.markdown(f"<div class='badge badge-exception'>Critical (<=30d): {risk_counts.get('Critical', 0)} SKUs</div>", unsafe_allow_html=True)
    with r2:
        st.markdown(f"<div class='badge badge-pending'>Warning (<=60d): {risk_counts.get('Warning', 0)} SKUs</div>", unsafe_allow_html=True)
    with r3:
        st.markdown(f"<div class='badge badge-active'>Notice (<=90d): {risk_counts.get('Notice', 0)} SKUs</div>", unsafe_allow_html=True)
    with r4:
        st.markdown(f"<div class='badge badge-completed'>Normal (>90d): {risk_counts.get('Normal', 0)} SKUs</div>", unsafe_allow_html=True)

    st.markdown("---")

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
