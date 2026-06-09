"""
Maverick-SORT — Essential Edition v6.0
=========================================
Standard Tier Streamlit Application

Derived from Pro v4 architecture but with Pro-exclusive modules hidden.
Reuses page_modules/ shared codebase for maintainability.

Pages (17 total, vs 22 in Pro):
  - Orders & Inventory, Smart Scheduling (2 pages), Operations
  - Tech Deep Dive (2 pages), Business Value (2 pages), Demo

All UI text is English. Remove any NAV_STRUCTURE entry to drop the page.
Author: AI-assisted implementation
Date: 2026/06/07
"""

import streamlit as st

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="Maverick-SORT | Essential Edition v6",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# IMPORT SHARED UTILITIES
# =============================================================================
from page_modules.shared import (
    PRO_CSS, init_pro_session_state,
    try_import_what_if, try_import_mos, try_import_adaptive,
)

# =============================================================================
# IMPORT PAGE MODULES (Essential subset)
# NOTE: Remove any import below (and its routing entry) to drop that page.
# =============================================================================
from page_modules.orders_inventory import (
    render_omnichannel_orders,
    render_order_analytics,
    render_warehouse_zones,
)
from page_modules.operations import (
    render_operations_dashboard,
    render_sla_analytics,
    render_task_workstation,
    render_alert_center,
)
from page_modules.scheduling import (
    render_algorithm_arena,
    render_scenario_lab,
)
from page_modules.tech_showcase import (
    render_kgdrl_framework,
    render_patent_wall,
)
from page_modules.business import (
    render_roi_calculator,
    render_plans_pricing,
)
from page_modules.demo import render_realtime_simulation

# =============================================================================
# INIT SESSION STATE & CSS
# =============================================================================
init_pro_session_state()
st.markdown(PRO_CSS, unsafe_allow_html=True)

# =============================================================================
# SIDEBAR: ESSENTIAL NAVIGATION (Pro features hidden)
# =============================================================================

NAV_STRUCTURE = {
    "🏠 Overview": [
        ("Dashboard", "dashboard"),
        ("User Guide", "user_guide"),
    ],
    "📦 Orders & Inventory": [
        ("Omni-Channel Orders", "omni_orders"),
        ("Order Analytics", "order_analytics"),
        ("Warehouse & Zones", "warehouse_zones"),
    ],
    "⚙️ Smart Scheduling": [
        ("Algorithm Arena", "algo_arena"),
        ("Scenario Simulator", "scenario_sim"),
    ],
    "📊 Operations": [
        ("Operations Dashboard", "ops_dashboard"),
        ("SLA Analytics", "sla_analytics"),
        ("Task Workstation", "task_station"),
        ("Alert Center", "alert_center"),
    ],
    "🔬 Tech Deep Dive": [
        ("KGDRL Framework", "kgdrl_framework"),
        ("Patent & Research Wall", "patent_wall"),
    ],
    "💼 Business Value": [
        ("ROI Calculator", "roi_calc"),
        ("Plans & Pricing", "plans_pricing"),
    ],
    "⚡ Demo & Simulation": [
        ("Real-Time Simulation", "rt_sim"),
    ],
}

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; margin-bottom:1.5rem;">
        <div style="font-size:1.4rem; font-weight:800; color:#f8fafc;">🔷 Maverick-SORT</div>
        <div style="font-size:0.8rem; color:#94a3b8;">Essential Edition v6.0</div>
        <div style="margin-top:0.5rem;">
            <span style="background:#3b82f6; color:white; padding:3px 10px; border-radius:12px; font-size:0.7rem; font-weight:700;">ESSENTIAL</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # --- Category selector ---
    category = st.radio("Category", list(NAV_STRUCTURE.keys()), index=0)

    st.markdown("---")

    # --- Page selector within category ---
    pages_in_cat = NAV_STRUCTURE[category]
    page_labels = [p[0] for p in pages_in_cat]
    page_keys = [p[1] for p in pages_in_cat]

    selected_page_label = st.radio("Page", page_labels, index=0)
    selected_page_key = page_keys[page_labels.index(selected_page_label)]

    st.markdown("---")

    # --- Module load status ---
    _, _, _, what_if_ok = try_import_what_if()

    st.markdown(f"""
    <div style="font-size:0.75rem; color:#64748b; text-align:center;">
        <div style="font-weight:700; margin-bottom:0.5rem;">Module Status</div>
        <div>{'🟢' if what_if_ok else '🔴'} What-If Simulator</div>
        <div style="font-size:0.7rem; color:#475569; margin-top:0.5rem;">
            Essential Edition | v6.0.0<br>
            2026/06/07
        </div>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# ROUTING
# =============================================================================

# --- Overview ---
if selected_page_key == "dashboard":
    st.markdown('<div class="main-header">Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Smart Wave Allocation for Small-to-Medium Warehouses</div>', unsafe_allow_html=True)

    col_title, col_badge = st.columns([3, 1])
    with col_badge:
        st.markdown("""
        <div style="text-align:right; margin-top:0.5rem;">
            <span style="background:#3b82f6; color:white; padding:4px 14px; border-radius:20px; font-size:0.75rem; font-weight:700;">ESSENTIAL</span>
            <div style="font-size:0.7rem; color:#64748b; margin-top:0.3rem;">v6.0.0</div>
        </div>
        """, unsafe_allow_html=True)

    cols = st.columns(4)
    for i, (label, value, delta, color) in enumerate([
        ("Orders Today", "94,328", "+12%", "#3b82f6"),
        ("Active Waves", "87", "-3%", "#06b6d4"),
        ("Avg Time", "4.2 min", "-18%", "#10b981"),
        ("Est. Savings", "¥47,600", "vs TZU", "#f59e0b"),
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
    st.markdown('<div class="section-header">🔷 Essential Capabilities</div>', unsafe_allow_html=True)

    features = [
        ("What-If Scenario Lab", "Test any parameter change before committing. Real simulation engine, zero-risk analysis.", "Essential"),
        ("Algorithm Arena", "Compare KGDRL against 5 heuristic baselines. Transparent, investor-ready performance data.", "Essential"),
        ("Operations Dashboard", "Real-time order flow, warehouse zones, and SLA tracking. Industrial-grade SCADA-style UI.", "Essential"),
        ("ROI Calculator", "Input your warehouse parameters and see projected annual savings instantly.", "Essential"),
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

    # Upgrade prompt
    st.markdown("---")
    st.markdown('<div class="section-header">⬆️ Upgrade to Professional</div>', unsafe_allow_html=True)
    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.markdown("""
        <div style="background:#111827; border-radius:12px; padding:1.2rem;">
            <div style="font-weight:700; color:#f8fafc; margin-bottom:0.5rem;">What you get with Pro:</div>
            <div style="font-size:0.85rem; color:#94a3b8; line-height:2;">
                <div>✓ Multi-Objective NSGA-II Optimization</div>
                <div>✓ Real-Time Adaptive (EWMA) Capacity</div>
                <div>✓ Online Learning + EWC Anti-Forgetting</div>
                <div>✓ API Integration (RESTful)</div>
                <div>✓ Federated Learning Architecture</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_right:
        st.markdown("""
        <div style="background:linear-gradient(135deg, #1e3a5f, #111827); border-radius:12px; padding:1.5rem; border:1px solid rgba(245,158,11,0.3);">
            <div style="font-weight:700; color:#f59e0b; font-size:1.2rem;">¥8,999 / month</div>
            <div style="font-size:0.8rem; color:#64748b; margin-bottom:1rem;">per warehouse</div>
            <div style="background:linear-gradient(135deg, #f59e0b, #ec4899); color:white; padding:10px; border-radius:8px; text-align:center; font-weight:700;">Compare Plans</div>
        </div>
        """, unsafe_allow_html=True)

elif selected_page_key == "user_guide":
    st.markdown('<div class="main-header">User Guide</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">How to use Maverick-SORT Essential for operational excellence</div>', unsafe_allow_html=True)

    guide_sections = [
        (
            "📦 Orders & Inventory",
            "#3b82f6",
            [
                ("Omni-Channel Orders", "Real-time visibility into order intake across all channels. Identify demand surges early and prevent stockouts."),
                ("Order Analytics", "Historical patterns and temperature distribution analytics. Optimize procurement budgets by predicting seasonal demand."),
                ("Warehouse & Zones", "Zone utilization and near-expiry FIFO control. Minimize write-offs from expired inventory and ensure GSP compliance."),
            ]
        ),
        (
            "⚙️ Smart Scheduling",
            "#06b6d4",
            [
                ("Algorithm Arena", "Side-by-side comparison of KGDRL against 5 heuristics. Justify technology investment with transparent performance data."),
                ("Scenario Simulator", "What-if testing before committing to operational changes. Zero-risk experimentation for wave capacity and peak season planning."),
            ]
        ),
        (
            "📊 Operations",
            "#10b981",
            [
                ("Operations Dashboard", "Live warehouse overview with zone utilization and order status. Reduce supervisory overhead with a single-pane view."),
                ("SLA Analytics", "12-month fulfillment trends + AI forecast. Predict SLA breaches before they happen."),
                ("Task Workstation", "DRL-optimized picking paths and labor deployment. Increase picker throughput per hour."),
                ("Alert Center", "Real-time anomaly detection with root cause analysis. Prevent small issues from becoming expensive disasters."),
            ]
        ),
        (
            "🔬 Tech Deep Dive",
            "#8b5cf6",
            [
                ("KGDRL Framework", "Visual explanation of the core AI architecture. Demonstrate explainable, auditable decision-making to stakeholders."),
                ("Patent & Research Wall", "Patent status and academic publications. Demonstrate legally protected and academically validated technology."),
            ]
        ),
        (
            "💼 Business Value",
            "#ec4899",
            [
                ("ROI Calculator", "Instant savings estimate based on warehouse parameters. Walk prospects through their exact payback period during a demo."),
                ("Plans & Pricing", "Tiered pricing with transparent feature comparison. Self-serve quote evaluation."),
            ]
        ),
    ]

    for cat_title, cat_color, items in guide_sections:
        st.markdown(f'<div class="section-header" style="border-color:{cat_color}; color:{cat_color};">{cat_title}</div>', unsafe_allow_html=True)
        for item_title, item_desc in items:
            st.markdown(f"""
            <div style="background:#111827; border-radius:10px; padding:1rem; margin-bottom:0.6rem; border-left:3px solid {cat_color};">
                <div style="font-weight:700; color:#f8fafc; font-size:0.95rem;">{item_title}</div>
                <div style="font-size:0.85rem; color:#94a3b8; margin-top:0.3rem; line-height:1.5;">{item_desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.info("Tip: Navigate to any section using the sidebar on the left. Each section is self-contained.")

# --- Orders & Inventory ---
elif selected_page_key == "omni_orders":
    render_omnichannel_orders()
elif selected_page_key == "order_analytics":
    render_order_analytics()
elif selected_page_key == "warehouse_zones":
    render_warehouse_zones()

# --- Smart Scheduling ---
elif selected_page_key == "algo_arena":
    render_algorithm_arena()
elif selected_page_key == "scenario_sim":
    render_scenario_lab()

# --- Operations ---
elif selected_page_key == "ops_dashboard":
    render_operations_dashboard()
elif selected_page_key == "sla_analytics":
    render_sla_analytics()
elif selected_page_key == "task_station":
    render_task_workstation()
elif selected_page_key == "alert_center":
    render_alert_center()

# --- Tech Deep Dive ---
elif selected_page_key == "kgdrl_framework":
    render_kgdrl_framework()
elif selected_page_key == "patent_wall":
    render_patent_wall()

# --- Business Value ---
elif selected_page_key == "roi_calc":
    render_roi_calculator()
elif selected_page_key == "plans_pricing":
    render_plans_pricing()

# --- Demo & Simulation ---
elif selected_page_key == "rt_sim":
    render_realtime_simulation()

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align:center; font-size:0.7rem; color:#475569; padding:1rem 0;">
    Maverick-SORT Essential Edition v6.0 | Day 4 Commercialization Build | 2026/06/07<br>
    Modular Architecture: page_modules/ | Built with Streamlit<br>
    <span style="color:#3b82f6;">🔷 Essential Edition</span>
</div>
""", unsafe_allow_html=True)
