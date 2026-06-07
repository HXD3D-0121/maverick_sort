"""
Sunergy Pharma — Business Value Module
========================================
Pages:
  - ROI Calculator
  - TCO Analysis (NEW)
  - Competitor Radar (NEW)
  - Plans & Pricing

NOTE: All UI text is English. Each page is a standalone render_* function.
"""

import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
from .shared import get_competitor_data


# =============================================================================
# PAGE: ROI Calculator
# =============================================================================

def render_roi_calculator():
    st.markdown('<div class="main-header">ROI Calculator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Input your warehouse parameters and see projected annual savings</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-header">Your Parameters</div>', unsafe_allow_html=True)
    col_in1, col_in2, col_in3, col_in4 = st.columns(4)
    with col_in1:
        daily_orders = st.number_input("Daily Orders", 500, 100000, 2000, 100)
    with col_in2:
        picker_wage = st.number_input("Picker Wage (CNY/hr)", 15, 150, 45, 5)
    with col_in3:
        warehouses = st.number_input("Warehouses", 1, 50, 1, 1)
    with col_in4:
        violation_cost = st.number_input("Violation Cost (CNY)", 500, 10000, 3000, 500)

    # Calculate
    avg_dist_per_order = 350  # meters
    cost_per_meter = 0.003
    days_per_year = 300
    manual_cost = daily_orders * avg_dist_per_order * days_per_year * cost_per_meter * warehouses
    picker_cost = daily_orders * 0.15 * picker_wage * days_per_year * warehouses / 60
    violation_cost_annual = (daily_orders / 1000 * 5 * violation_cost) * warehouses

    total_baseline = manual_cost + picker_cost + violation_cost_annual
    # Pro tier uses 25% vs Essential 22%
    saving_pct = 0.25
    total_savings = total_baseline * saving_pct
    pro_annual = 8999 * 12 * warehouses
    net_savings = total_savings - pro_annual
    payback_months = pro_annual / (total_savings / 12) if total_savings > 0 else 0

    st.markdown("---")
    st.markdown('<div class="section-header">Annual Impact</div>', unsafe_allow_html=True)

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

    st.markdown("---")
    st.markdown('<div class="section-header">Sensitivity - Savings at Different Utilization</div>', unsafe_allow_html=True)
    util_range = np.arange(0.10, 0.35, 0.02)
    sens_savings = total_baseline * util_range - pro_annual
    sens_df = pd.DataFrame({"Saving Rate": util_range * 100, "Net Savings (CNY)": sens_savings})
    sens_chart = alt.Chart(sens_df).mark_area(opacity=0.4, color="#10b981").encode(
        x=alt.X("Saving Rate", title="Efficiency Improvement (%)"),
        y=alt.Y("Net Savings (CNY)", title="Net Annual Savings (CNY)")
    ) + alt.Chart(sens_df).mark_line(color="#10b981", strokeWidth=2).encode(
        x="Saving Rate", y="Net Savings (CNY)"
    ) + alt.Chart(pd.DataFrame({"x": [25], "y": [net_savings]})).mark_point(color="#f59e0b", size=150, filled=True).encode(x="x", y="y")
    st.altair_chart(sens_chart.properties(height=280), width='stretch')

    st.caption("Orange dot = your scenario. Shaded area shows savings range across 10%-35% efficiency gains.")

    st.markdown("---")
    st.markdown('<div class="section-header">Cost Breakdown Comparison</div>', unsafe_allow_html=True)
    breakdown_df = pd.DataFrame({
        "Category": ["Manual Distance", "Picker Labor", "Violation Penalties", "Software Subscription"],
        "Current (CNY)": [manual_cost, picker_cost, violation_cost_annual, 0],
        "With Sunergy (CNY)": [manual_cost * 0.75, picker_cost * 0.75, violation_cost_annual * 0.4, pro_annual],
    })
    breakdown_melt = breakdown_df.melt(id_vars=["Category"], var_name="Scenario", value_name="Amount")
    bchart = alt.Chart(breakdown_melt).mark_bar(cornerRadiusEnd=4).encode(
        x=alt.X("Category:N", title="", sort=None),
        y=alt.Y("Amount:Q", title="CNY / Year"),
        color=alt.Color("Scenario:N", scale=alt.Scale(domain=["Current (CNY)", "With Sunergy (CNY)"], range=["#64748b", "#f59e0b"])),
        xOffset="Scenario:N",
    ).properties(height=300)
    st.altair_chart(bchart, width='stretch')


# =============================================================================
# PAGE: TCO Analysis (NEW)
# =============================================================================

def render_tco_analysis():
    st.markdown('<div class="main-header">TCO Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">5-Year Total Cost of Ownership: Manual vs Sunergy Pro</div>', unsafe_allow_html=True)

    col_cfg, _ = st.columns([1, 2])
    with col_cfg:
        st.markdown('<div class="section-header">Scenario Assumptions</div>', unsafe_allow_html=True)
        daily_orders = st.number_input("Daily Orders / WH", 500, 100000, 5000, 500, key="tco_orders")
        wage_growth = st.slider("Annual Wage Growth (%)", 0.0, 10.0, 3.5, 0.5) / 100
        warehouses = st.number_input("Warehouses", 1, 20, 3, 1, key="tco_wh")

    years = list(range(1, 6))

    # Baseline (manual) costs
    base_picker_cost = daily_orders * 0.15 * 50 * 300 * warehouses / 60
    base_violation = daily_orders / 1000 * 5 * 5000 * warehouses
    base_distance = daily_orders * 350 * 300 * 0.003 * warehouses
    base_total = base_picker_cost + base_violation + base_distance

    manual_costs = []
    sunergy_costs = []
    for y in years:
        manual_y = base_total * ((1 + wage_growth) ** (y - 1))
        sub_y = 8999 * 12 * warehouses * ((1 + 0.05) ** (y - 1))  # 5% annual price increase
        implementation = 50000 if y == 1 else 0
        sunergy_y = sub_y + implementation + (manual_y * 0.25)  # 25% residual manual cost
        manual_costs.append(manual_y)
        sunergy_costs.append(sunergy_y)

    tco_df = pd.DataFrame({
        "Year": years,
        "Manual Operations": manual_costs,
        "Sunergy Pro": sunergy_costs,
    })
    tco_melt = tco_df.melt(id_vars=["Year"], var_name="Scenario", value_name="Cost")

    # Cumulative TCO chart
    tco_df["Cumulative Manual"] = np.cumsum(tco_df["Manual Operations"])
    tco_df["Cumulative Sunergy"] = np.cumsum(tco_df["Sunergy Pro"])
    tco_df["Savings"] = tco_df["Cumulative Manual"] - tco_df["Cumulative Sunergy"]

    st.markdown("---")
    st.markdown('<div class="section-header">Annual Cost Comparison</div>', unsafe_allow_html=True)
    ann_chart = alt.Chart(tco_melt).mark_bar(cornerRadiusEnd=4).encode(
        x=alt.X("Year:O", title="Year"),
        y=alt.Y("Cost:Q", title="CNY / Year"),
        color=alt.Color("Scenario:N", scale=alt.Scale(domain=["Manual Operations", "Sunergy Pro"], range=["#64748b", "#f59e0b"])),
        xOffset="Scenario:N",
    ).properties(height=300)
    st.altair_chart(ann_chart, width='stretch')

    st.markdown("---")
    st.markdown('<div class="section-header">Cumulative TCO & Breakeven</div>', unsafe_allow_html=True)
    cum_df = pd.DataFrame({
        "Year": years * 2,
        "Scenario": ["Manual"] * 5 + ["Sunergy Pro"] * 5,
        "Cumulative": list(tco_df["Cumulative Manual"]) + list(tco_df["Cumulative Sunergy"]),
    })
    cum_chart = alt.Chart(cum_df).mark_line(strokeWidth=3, point=True).encode(
        x=alt.X("Year:O", title="Year"),
        y=alt.Y("Cumulative:Q", title="Cumulative CNY"),
        color=alt.Color("Scenario:N", scale=alt.Scale(domain=["Manual", "Sunergy Pro"], range=["#64748b", "#f59e0b"])),
    ).properties(height=320)
    st.altair_chart(cum_chart, width='stretch')

    # Breakeven year
    breakeven = None
    for i, row in tco_df.iterrows():
        if row["Cumulative Sunergy"] < row["Cumulative Manual"]:
            breakeven = row["Year"]
            break

    if breakeven:
        st.success(f"Breakeven achieved in Year {int(breakeven)}. Total 5-year savings: ¥{tco_df['Savings'].iloc[-1]:,.0f}")
    else:
        st.warning("Breakeven not achieved within 5 years under current assumptions.")

    st.markdown("---")
    st.markdown('<div class="section-header">Sensitivity - TCO at Different Wage Growth Rates</div>', unsafe_allow_html=True)
    wage_scenarios = [0.02, 0.035, 0.05, 0.07, 0.10]
    sens_rows = []
    for wg in wage_scenarios:
        mc = sum([base_total * ((1 + wg) ** (y - 1)) for y in years])
        sc = sum([8999 * 12 * warehouses * ((1 + 0.05) ** (y - 1)) + (base_total * ((1 + wg) ** (y - 1)) * 0.25) for y in years]) + 50000
        sens_rows.append({"Wage Growth": f"{wg*100:.1f}%", "Manual TCO": mc, "Sunergy TCO": sc, "Net Savings": mc - sc})
    sens_df = pd.DataFrame(sens_rows)
    sens_melt = sens_df.melt(id_vars=["Wage Growth"], value_vars=["Manual TCO", "Sunergy TCO"], var_name="Scenario", value_name="TCO")

    sens_chart = alt.Chart(sens_melt).mark_bar(cornerRadiusEnd=4).encode(
        x=alt.X("Wage Growth:N", title="Annual Wage Growth"),
        y=alt.Y("TCO:Q", title="5-Year TCO (CNY)"),
        color=alt.Color("Scenario:N", scale=alt.Scale(domain=["Manual TCO", "Sunergy TCO"], range=["#64748b", "#f59e0b"])),
        xOffset="Scenario:N",
    ).properties(height=280)
    st.altair_chart(sens_chart, width='stretch')

    st.dataframe(sens_df[["Wage Growth", "Net Savings"]].style.format({"Net Savings": "¥{:,.0f}"}), hide_index=True)


# =============================================================================
# PAGE: Competitor Radar (NEW)
# =============================================================================

def render_competitor_radar():
    st.markdown('<div class="main-header">Competitor Radar</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">How Sunergy stacks up against traditional WMS and enterprise suites</div>', unsafe_allow_html=True)

    comp_df = get_competitor_data()

    # --- Radar Chart using Altair (transformed to line marks on polar-like layout) ---
    # For simplicity in Streamlit + Altair, we use a parallel coordinates style
    st.markdown('<div class="section-header">Capability Comparison Matrix</div>', unsafe_allow_html=True)

    dimensions = ["Price", "Intelligence", "GSP_Compliance", "Time_to_Deploy", "Real_Time", "Explainability"]
    dim_labels = ["Price/Value", "AI Intelligence", "GSP Compliance", "Time to Deploy", "Real-Time", "Explainability"]

    melted = comp_df.melt(id_vars=["Vendor"], value_vars=dimensions, var_name="Dimension", value_name="Score")
    # Map dimension names to labels
    dim_map = dict(zip(dimensions, dim_labels))
    melted["Dimension"] = melted["Dimension"].map(dim_map)

    # Highlight Sunergy
    melted["Color"] = melted["Vendor"].apply(
        lambda v: "#f59e0b" if v == "Sunergy (Us)" else "#64748b"
    )

    radar_chart = alt.Chart(melted).mark_line(strokeWidth=2.5, opacity=0.8).encode(
        x=alt.X("Dimension:N", sort=dim_labels, title=""),
        y=alt.Y("Score:Q", scale=alt.Scale(domain=[0, 100]), title="Score (0-100)"),
        color=alt.Color("Vendor:N", legend=alt.Legend(orient="top", labelColor="#e2e8f0")),
        tooltip=["Vendor", "Dimension", "Score"],
    ).properties(height=400)

    points = alt.Chart(melted).mark_circle(size=80).encode(
        x=alt.X("Dimension:N", sort=dim_labels),
        y=alt.Y("Score:Q"),
        color=alt.Color("Vendor:N"),
        tooltip=["Vendor", "Dimension", "Score"],
    )

    st.altair_chart(radar_chart + points, width='stretch')

    st.markdown("---")

    # --- Differentiation Narrative ---
    st.markdown('<div class="section-header">Key Differentiators</div>', unsafe_allow_html=True)

    diffs = [
        ("AI-Native vs Rule-Based", "Traditional WMS relies on static rules. Sunergy uses KGDRL that adapts to order patterns in real time.", "#3b82f6"),
        ("GSP Compliance Built-In", "Temperature isolation and near-expiry FIFO are enforced at the algorithm level, not as afterthoughts.", "#10b981"),
        ("Explainable Decisions", "Every wave allocation is auditable: why this temperature, why this zone, why this order. GSP inspectors love it.", "#f59e0b"),
        ("Fast Deployment", "Pure Python + Streamlit. No SAP consultants, no 6-month implementation. Live in 2 weeks.", "#8b5cf6"),
    ]

    for title, desc, color in diffs:
        st.markdown(f"""
        <div style="background:#111827; border-radius:10px; padding:1.2rem; margin-bottom:0.8rem; border-left:4px solid {color};">
            <div style="font-weight:700; color:#f8fafc; font-size:1rem;">{title}</div>
            <div style="font-size:0.85rem; color:#94a3b8; margin-top:0.3rem; line-height:1.5;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Feature Matrix</div>', unsafe_allow_html=True)
    st.dataframe(comp_df.set_index("Vendor"), width='stretch')


# =============================================================================
# PAGE: Plans & Pricing
# =============================================================================

def render_plans_pricing():
    st.markdown('<div class="main-header">Plans & Pricing</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Pro pricing + Group deployment calculator</div>', unsafe_allow_html=True)

    billing = st.segmented_control("Billing", ["Monthly", "Annual (Save 25%)"], default="Monthly")
    is_annual = (billing == "Annual (Save 25%)")
    discount = 0.75 if is_annual else 1.0

    st.markdown("---")

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

    st.markdown("---")
    st.markdown('<div class="section-header">Group Deployment Calculator</div>', unsafe_allow_html=True)

    col_g1, col_g2, col_g3, col_g4 = st.columns(4)
    with col_g1:
        group_warehouses = st.number_input("Warehouses", 1, 100, 5, 1, key="grp_wh")
    with col_g2:
        group_orders = st.number_input("Orders/Day/WH", 1000, 100000, 15000, 1000, key="grp_ord")
    with col_g3:
        group_wage = st.number_input("Picker Wage CNY/hr", 15, 150, 50, 5, key="grp_wage")
    with col_g4:
        group_violation = st.number_input("Violation Cost CNY", 500, 20000, 5000, 500, key="grp_viol")

    days = 300
    dist_per_order = 400
    manual_cost_wh = group_orders * dist_per_order * days * 0.003
    picker_cost_wh = group_orders * 0.15 * group_wage * days / 60
    viol_cost_wh = (group_orders / 1000 * 5 * group_violation)
    total_baseline_wh = manual_cost_wh + picker_cost_wh + viol_cost_wh

    saving_rate = 0.25
    savings_wh = total_baseline_wh * saving_rate
    pro_monthly_wh = 8999 * discount
    if group_orders > 5000:
        per_order = group_orders * 30 * 0.08 * discount
        pro_monthly_wh = min(pro_monthly_wh, per_order)

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
        st.success(f"Group discount applied: {int((1-group_discount)*100)}% off per warehouse for {group_warehouses} warehouses")

    if group_orders > 3750 and group_orders <= 5000:
        st.info("At this volume, per-warehouse billing is optimal. Consider per-order billing (¥0.08/order) for >5,000 orders/day.")
