"""
Sunergy Pharma — Operations Monitoring Module
===============================================
Pages:
  - Operations Dashboard
  - Customer SLA Analytics
  - Task Workstation
  - Smart Alert Center (NEW)

NOTE: All UI text is English. Each page is a standalone render_* function.
"""

import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
from datetime import datetime
from .shared import (
    get_orders_basic, get_sla_history_tuple, get_tasks_data,
    get_labor_data, get_alert_data, get_data_source, ZONE_LETTERS, CLIENT_TYPES
)


# =============================================================================
# PAGE: Operations Dashboard
# =============================================================================

def render_operations_dashboard():
    st.markdown('<div class="main-header">Operations Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Real-time warehouse overview and live order flow</div>', unsafe_allow_html=True)

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

    st.markdown('<div class="section-header">Live Orders</div>', unsafe_allow_html=True)
    df_orders = get_orders_basic(n=25, seed=int(datetime.now().timestamp()) // 30)
    st.dataframe(df_orders, width='stretch', hide_index=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Near-Expiry FIFO Queue</div>', unsafe_allow_html=True)
    expiry_df = pd.DataFrame([
        {"SKU": "INS-001", "Name": "Insulin Glargine", "Zone": "Cold", "Expiry": "2026-06-15", "Days": 9, "Risk": "Critical", "Qty": 1200},
        {"SKU": "VAC-042", "Name": "Influenza Vaccine", "Zone": "Cold", "Expiry": "2026-06-28", "Days": 22, "Risk": "Warning", "Qty": 850},
        {"SKU": "ANT-103", "Name": "Amoxicillin 500mg", "Zone": "Ambient", "Expiry": "2026-07-10", "Days": 34, "Risk": "Notice", "Qty": 3200},
    ])
    st.dataframe(expiry_df, width='stretch', hide_index=True)


# =============================================================================
# PAGE: Customer SLA Analytics
# =============================================================================

def render_sla_analytics():
    st.markdown('<div class="main-header">Customer SLA Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Fulfillment trends, SKU diversity, and AI-forecasted performance</div>', unsafe_allow_html=True)

    months, history, forecast_days, forecast = get_sla_history_tuple()
    clients = list(history.keys())

    st.markdown('<div class="section-header">Monthly Order Volume - Past 12 Months</div>', unsafe_allow_html=True)
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
                sla_data.append({"Period": month, "Client": client, "SLA (%)": round(history[client][i], 1), "Type": "Historical"})
            for i, day in enumerate(forecast_days):
                sla_data.append({"Period": day, "Client": client, "SLA (%)": round(forecast[client][i], 1), "Type": "AI Forecast"})
        df_sla = pd.DataFrame(sla_data)

        hist_chart = alt.Chart(df_sla[df_sla["Type"] == "Historical"]).mark_line(strokeWidth=2, opacity=0.8).encode(
            x=alt.X("Period:N", title="", sort=None),
            y=alt.Y("SLA (%):Q", scale=alt.Scale(domain=[70, 100])),
            color=alt.Color("Client:N", legend=alt.Legend(orient="top", labelColor="#e2e8f0")),
        )
        fc_chart = alt.Chart(df_sla[df_sla["Type"] == "AI Forecast"]).mark_line(strokeWidth=2, strokeDash=[4, 4], opacity=0.9).encode(
            x=alt.X("Period:N", title="", sort=None),
            y=alt.Y("SLA (%):Q"),
            color=alt.Color("Client:N"),
        )
        st.altair_chart(hist_chart + fc_chart)

    st.markdown("---")

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
# PAGE: Task Workstation
# =============================================================================

def render_task_workstation():
    st.markdown('<div class="main-header">Task Workstation</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Labor deployment, picking efficiency, and DRL-optimized task queue</div>', unsafe_allow_html=True)

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
        st.markdown(f"""
        <div style="text-align: center; margin-top: -10px;">
            <span style="font-size: 0.75rem; color: #ef4444; font-weight: 600;">
                Peak Season Temporary Cap: {peak_cap} workers (current: {total})
            </span>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="section-header">Picking Efficiency by Zone</div>', unsafe_allow_html=True)
        df_eff = get_labor_data()
        st.dataframe(df_eff[["Zone", "Total Headcount", "SKUs/Hour/Person", "Shift"]], hide_index=True, height=250)

    st.markdown("---")

    st.markdown('<div class="section-header">Operation Queue</div>', unsafe_allow_html=True)
    df_tasks = get_tasks_data(n=30)

    tab_pending, tab_active, tab_completed, tab_exceptions = st.tabs(["Pending", "Active Picking", "Completed", "Exceptions"])

    with tab_pending:
        df_pending = df_tasks[df_tasks["Status"] == "Pending"]
        if len(df_pending) > 0:
            for _, row in df_pending.iterrows():
                with st.expander(f"{row['Task ID']} - {row['Source Zone']} -> {row['Target Client']}"):
                    st.markdown(f"**Priority:** {row['Priority']}")
                    st.markdown(f"**Assigned Worker:** {row['Assigned Worker']}")
                    st.markdown(f"**SKU Checklist:** {row['SKU Checklist']}")
                    st.markdown(f"**Est. Duration:** {row['Est. Duration (min)']} min")
        else:
            st.info("No pending tasks")

    with tab_active:
        df_active = df_tasks[df_tasks["Status"] == "Active Picking"]
        if len(df_active) > 0:
            for _, row in df_active.iterrows():
                with st.expander(f"{row['Task ID']} - {row['Source Zone']} -> {row['Target Client']}"):
                    st.markdown(f"**Priority:** {row['Priority']}")
                    st.markdown(f"**Assigned Worker:** {row['Assigned Worker']}")
                    st.markdown(f"**SKU Checklist:** {row['SKU Checklist']}")
                    st.markdown(f"**Est. Duration:** {row['Est. Duration (min)']} min")
                    st.markdown("---")
                    st.markdown("##### DRL-Optimized Picking Path")
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
                with st.expander(f"Exception: {row['Task ID']}"):
                    st.markdown(f"**Priority:** {row['Priority']}")
                    st.markdown(f"**Assigned Worker:** {row['Assigned Worker']}")
                    st.markdown(f"**SKU Checklist:** {row['SKU Checklist']}")
                    st.error("Temperature mismatch detected during picking. Zone supervisor notified.")
        else:
            st.success("No exceptions - all operations nominal")

    st.markdown("---")
    st.markdown('<div class="section-header">My Dispatched Tasks</div>', unsafe_allow_html=True)
    my_tasks = df_tasks[df_tasks["Assigned Worker"] == "Worker-01"]
    if len(my_tasks) > 0:
        st.dataframe(my_tasks[["Task ID", "Source Zone", "Target Client", "Status", "Priority", "Est. Duration (min)"]], hide_index=True)
    else:
        st.info("No tasks currently dispatched to Worker-01")


# =============================================================================
# PAGE: Smart Alert Center (NEW)
# =============================================================================

def render_alert_center():
    st.markdown('<div class="main-header">Smart Alert Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Real-time anomaly detection, root cause analysis, and recommended actions</div>', unsafe_allow_html=True)

    df_alerts = get_alert_data(n=12)

    # --- Severity Summary Cards ---
    cols = st.columns(4)
    severities = [("Critical", "#ef4444", "critical"), ("Warning", "#f59e0b", "warning"),
                  ("Info", "#3b82f6", "info"), ("Resolved", "#10b981", "success")]
    for col, (label, color, key) in zip(cols, severities):
        count = len(df_alerts[df_alerts["Severity"] == key])
        with col:
            st.markdown(f"""
            <div class="metric-card" style="border-top: 3px solid {color};">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color:{color};">{count}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # --- Alert Feed with Color Coding ---
    st.markdown('<div class="section-header">Active Alert Feed</div>', unsafe_allow_html=True)

    for _, row in df_alerts.iterrows():
        severity_class = f"alert-{row['Severity']}"
        ack_badge = "<span style='background:#10b981; color:white; padding:2px 8px; border-radius:4px; font-size:0.7rem;'>ACK</span>" if row["Acknowledged"] else "<span style='background:#ef4444; color:white; padding:2px 8px; border-radius:4px; font-size:0.7rem;'>NEW</span>"
        st.markdown(f"""
        <div class="{severity_class}">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:700; color:#f8fafc; font-size:0.9rem;">{row['Type']}</span>
                <span style="font-size:0.75rem; color:#94a3b8;">{ack_badge} {row['Timestamp']}</span>
            </div>
            <div style="font-size:0.85rem; color:#94a3b8; margin-top:0.3rem;">{row['Message']} | Zone: {row['Zone']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- Root Cause & Recommendation Panel ---
    st.markdown('<div class="section-header">Root Cause Analysis & Recommended Actions</div>', unsafe_allow_html=True)

    actions = [
        ("Temperature Deviation in Zone C", "HVAC unit #3 showing 0.8 degC drift above threshold. Correlated with afternoon peak load.",
         ["Dispatch maintenance to HVAC #3", "Temporarily reroute cold-chain orders to Zone D", "Activate backup cooling unit"]),
        ("Wave #42 Release Delay", "Order surge at 14:30 exceeded picker capacity by 23%. EDD heuristic caused batch fragmentation.",
         ["Switch to KGDRL policy for next wave", "Allocate 3 temporary pickers from Zone F", "Split wave into 2 sub-waves"]),
        ("Insulin Glargine Low Stock", "Consumption rate 18% above forecast due to flu-season demand spike.",
         ["Trigger emergency replenishment from supplier", "Reserve remaining stock for urgent orders only", "Update demand forecast model"]),
    ]

    for title, cause, recs in actions:
        with st.expander(title):
            st.markdown(f"**Root Cause:** {cause}")
            st.markdown("**Recommended Actions:**")
            for i, rec in enumerate(recs, 1):
                st.markdown(f"{i}. {rec}")

    st.markdown("---")
    st.info("Alerts are auto-prioritized by severity, potential revenue impact, and GSP compliance risk.")
