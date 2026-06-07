"""
Sunergy Pharma — Professional Edition v3.0
=============================================
Refactored Pro Tier Streamlit Application

Architecture:
  - page_modules/shared.py        Common CSS, data, session state
  - page_modules/orders_inventory.py  Orders & Inventory pages
  - page_modules/operations.py    Operations Monitoring pages
  - page_modules/scheduling.py    Smart Scheduling Engine pages
  - page_modules/tech_showcase.py Tech Deep Dive pages
  - page_modules/business.py      Business Value pages
  - page_modules/demo.py          Demo & Simulation pages

All UI text is English. Each page module can be removed independently.
Author: AI-assisted implementation
Date: 2026/06/07
"""

import streamlit as st

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="Sunergy Pharma | Professional Edition v3",
    page_icon="🔶",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# IMPORT SHARED UTILITIES
# =============================================================================
from page_modules.shared import PRO_CSS, init_pro_session_state, try_import_what_if, try_import_mos, try_import_adaptive

# =============================================================================
# IMPORT PAGE MODULES
# NOTE: Remove any import below (and its routing entry) to drop that module.
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
    render_strategy_optimizer,
    render_live_adaptive,
)
from page_modules.tech_showcase import (
    render_kgdrl_framework,
    render_ai_learning_engine,
    render_multi_warehouse,
    render_patent_wall,
)
from page_modules.business import (
    render_roi_calculator,
    render_tco_analysis,
    render_competitor_radar,
    render_plans_pricing,
)
from page_modules.demo import (
    render_realtime_simulation,
    render_demo_mode,
)

# =============================================================================
# INIT SESSION STATE & CSS
# =============================================================================
init_pro_session_state()
st.markdown(PRO_CSS, unsafe_allow_html=True)

# =============================================================================
# SIDEBAR: GROUPED NAVIGATION
# Structure: Category -> Page mapping
# Remove any entry tuple to hide that page from navigation.
# =============================================================================

NAV_STRUCTURE = {
    "🏠 Overview": [
        ("Command Center", "cmd_center"),
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
        ("Strategy Optimizer", "strategy_opt"),
        ("Live Adaptive Intelligence", "live_adaptive"),
    ],
    "📊 Operations": [
        ("Operations Dashboard", "ops_dashboard"),
        ("SLA Analytics", "sla_analytics"),
        ("Task Workstation", "task_station"),
        ("Alert Center", "alert_center"),
    ],
    "🔬 Tech Deep Dive": [
        ("KGDRL Framework", "kgdrl_framework"),
        ("AI Learning Engine", "ai_learning"),
        ("Multi-Warehouse Network", "multi_wh"),
        ("Patent & Research Wall", "patent_wall"),
    ],
    "💼 Business Value": [
        ("ROI Calculator", "roi_calc"),
        ("TCO Analysis", "tco_analysis"),
        ("Competitor Radar", "comp_radar"),
        ("Plans & Pricing", "plans_pricing"),
    ],
    "⚡ Demo & Simulation": [
        ("Real-Time Simulation", "rt_sim"),
        ("Demo Mode", "demo_mode"),
    ],
}

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; margin-bottom:1.5rem;">
        <div style="font-size:1.4rem; font-weight:800; color:#f8fafc;">🔶 Sunergy Pharma</div>
        <div style="font-size:0.8rem; color:#94a3b8;">Professional Edition v3.0</div>
        <div style="margin-top:0.5rem;">
            <span style="background:linear-gradient(135deg, #f59e0b, #ec4899); color:white; padding:3px 10px; border-radius:12px; font-size:0.7rem; font-weight:700;">PRO</span>
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
    _, _, _, _, mos_ok = try_import_mos()
    _, _, adaptive_ok = try_import_adaptive()

    st.markdown(f"""
    <div style="font-size:0.75rem; color:#64748b; text-align:center;">
        <div style="font-weight:700; margin-bottom:0.5rem;">Module Status</div>
        <div>{'🟢' if what_if_ok else '🔴'} What-If Simulator</div>
        <div>{'🟢' if mos_ok else '🔴'} Multi-Objective Scheduler</div>
        <div>{'🟢' if adaptive_ok else '🔴'} Adaptive Policy</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div style="font-size:0.7rem; color:#475569; text-align:center;">
        Sunergy Pharma Pro v3.0<br>
        Day 4 Commercialization Build<br>
        2026/06/07
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# ROUTING: Map selected_page_key -> render function
# Remove any case below to disable that page.
# =============================================================================

# --- Overview ---
if selected_page_key == "cmd_center":
    st.markdown('<div class="main-header">Command Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Enterprise-Grade Multi-Objective Optimization + Real-Time Adaptation</div>', unsafe_allow_html=True)

    col_title, col_badge = st.columns([3, 1])
    with col_badge:
        st.markdown("""
        <div style="text-align:right; margin-top:0.5rem;">
            <span style="background:linear-gradient(135deg, #f59e0b, #ec4899); color:white; padding:4px 14px; border-radius:20px; font-size:0.75rem; font-weight:700;">PROFESSIONAL</span>
            <div style="font-size:0.7rem; color:#64748b; margin-top:0.3rem;">v3.0.0</div>
        </div>
        """, unsafe_allow_html=True)

    cols = st.columns(5)
    for i, (label, value, delta, color) in enumerate([
        ("Orders", "94,328", "+12%", "#3b82f6"),
        ("Pareto Front", "47 pts", "NSGA-II", "#f59e0b"),
        ("Adaptive Cap", "20", "Auto-adjusted", "#10b981"),
        ("Compliance", "99.2%", "Zero Violations", "#8b5cf6"),
        ("Est. Savings", "¥142,000", "Pro vs Baseline", "#f59e0b"),
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
    st.markdown('<div class="section-header">Pro Exclusive Capabilities</div>', unsafe_allow_html=True)

    features = [
        ("Multi-Objective Optimizer", "NSGA-II powered Pareto frontier. Cost x Time x Compliance trade-offs with one-click strategy switching.", "Pro"),
        ("Real-Time Adaptive Monitor", "EWMA-based arrival prediction + dynamic wave capacity adjustment. Peak seasons handled automatically.", "Pro"),
        ("Online Learning (EWC)", "Experience replay + Elastic Weight Consolidation prevents catastrophic forgetting. Gets smarter every shift.", "Pro"),
        ("Federated Learning Ready", "Multi-warehouse collaborative training architecture. Data stays local, intelligence goes global.", "Pro"),
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

    st.markdown("---")
    st.markdown('<div class="section-header">Quick Navigation</div>', unsafe_allow_html=True)
    st.markdown("Use the sidebar to explore:")
    st.markdown("""
    - **Orders & Inventory** - Live order feeds, analytics, and warehouse zone monitoring
    - **Smart Scheduling** - Algorithm comparison, What-If simulation, Pareto optimization, and adaptive control
    - **Operations** - Dashboard, SLA tracking, task management, and smart alerts
    - **Tech Deep Dive** - KGDRL architecture, online learning, federated network, and patent portfolio
    - **Business Value** - ROI calculator, TCO analysis, competitor radar, and pricing
    - **Demo & Simulation** - Real-time HTML simulation and auto-play demo mode
    """)

# --- User Guide ---
elif selected_page_key == "user_guide":
    st.markdown('<div class="main-header">User Guide</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">How to use Sunergy Pharma Pro for operational excellence and profitability</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="background:#111827; border-radius:12px; padding:1.5rem; margin-bottom:1.5rem;">
        <div style="font-weight:700; color:#f8fafc; font-size:1.1rem; margin-bottom:0.5rem;">Welcome</div>
        <div style="font-size:0.9rem; color:#94a3b8; line-height:1.6;">
            Sunergy Pharma Professional Edition is an AI-native warehouse wave allocation system
            designed for pharmaceutical distributors. This guide explains each module from a
            <b>business operations and profitability</b> perspective.
        </div>
    </div>
    """, unsafe_allow_html=True)

    guide_sections = [
        (
            "📦 Orders & Inventory",
            "#3b82f6",
            [
                ("Omni-Channel Orders", "Real-time visibility into order intake across all channels (hospitals, pharmacies, clinics). Business value: identify demand surges early, prevent stockouts, and prioritize high-margin urgent orders before competitors."),
                ("Order Analytics", "Historical patterns and temperature distribution analytics. Business value: optimize procurement budgets by predicting seasonal demand (e.g., flu season cold-chain spikes), reducing emergency replenishment costs by 15-20%."),
                ("Warehouse & Zones", "Zone utilization and near-expiry FIFO control. Business value: minimize write-offs from expired inventory (typically 2-4% of pharma revenue) and ensure GSP-compliant temperature segregation to avoid regulatory penalties."),
            ]
        ),
        (
            "⚙️ Smart Scheduling",
            "#f59e0b",
            [
                ("Algorithm Arena", "Side-by-side comparison of KGDRL against 5 heuristics. Business value: justify the technology investment with transparent performance data. Show stakeholders exactly how much distance, labor, and violation costs are reduced."),
                ("Scenario Simulator", "What-if testing before committing to operational changes. Business value: zero-risk experimentation. Test 'what if wave capacity drops to 15?' or 'what if flu season doubles order volume?' without disrupting live operations."),
                ("Strategy Optimizer", "NSGA-II multi-objective Pareto frontier. Business value: one-click switching between cost-first, time-first, or compliance-first modes. Adapt strategy instantly during audit periods vs. normal operations vs. peak seasons—no manual reconfiguration needed."),
                ("Live Adaptive Intelligence", "Real-time EWMA-based capacity adjustment. Business value: automatic handling of demand surges without hiring temporary staff. The system shrinks waves during peak hours and expands them during lulls, maintaining SLA commitments while controlling labor costs."),
            ]
        ),
        (
            "📊 Operations",
            "#10b981",
            [
                ("Operations Dashboard", "Live warehouse overview with zone utilization and order status. Business value: reduce supervisory overhead. Warehouse managers get a single-pane view instead of walking the floor or checking 4 separate systems."),
                ("SLA Analytics", "12-month fulfillment trends + 14-day AI forecast. Business value: predict SLA breaches before they happen. Use forecast data to negotiate realistic delivery commitments with clients, reducing penalty payments and protecting renewal rates."),
                ("Task Workstation", "DRL-optimized picking paths and labor deployment. Business value: increase picker throughput per hour by 18-25%. Optimized paths mean less walking distance, less fatigue, and higher output with the same headcount."),
                ("Alert Center", "Real-time anomaly detection with root cause analysis. Business value: prevent small issues from becoming expensive disasters. A temperature deviation caught in 5 minutes saves a cold-chain batch worth tens of thousands."),
            ]
        ),
        (
            "🔬 Tech Deep Dive",
            "#8b5cf6",
            [
                ("KGDRL Framework", "Visual explanation of the core AI architecture. Business value: <b>investor-ready technical credibility</b>. Demonstrate to due diligence teams that your system is not a black box—it is explainable, auditable, and built on peer-reviewed principles."),
                ("AI Learning Engine", "Online learning and anti-forgetting mechanisms. Business value: the system improves with every shift without expensive retraining. Each warehouse's strategy becomes a proprietary asset that competitors cannot copy."),
                ("Multi-Warehouse Network", "Federated learning architecture for multi-site deployments. Business value: enterprise scalability. Deploy to 10 warehouses without 10x cloud costs. Intelligence aggregates centrally while sensitive order data never leaves the local site."),
                ("Patent & Research Wall", "Patent status and academic publications. Business value: <b>defensible moat</b>. During investor discussions or procurement RFPs, this page demonstrates that the technology is legally protected and academically validated."),
            ]
        ),
        (
            "💼 Business Value",
            "#ec4899",
            [
                ("ROI Calculator", "Instant savings estimate based on warehouse parameters. Business value: <b>sales enablement</b>. Account executives can walk prospects through their exact payback period during a 15-minute demo, accelerating deal closure."),
                ("TCO Analysis", "5-year total cost of ownership comparison. Business value: overcome procurement objections. Show CFOs that despite subscription fees, the cumulative 5-year cost is 30-40% lower than manual operations—and breakeven happens in under 6 months."),
                ("Competitor Radar", "Capability matrix vs. SAP EWM, Manhattan, Blue Yonder, and rule-based systems. Business value: <b>differentiation clarity</b>. Use in competitive sales situations to show why legacy WMS cannot match AI-native adaptability at this price point."),
                ("Plans & Pricing", "Tiered pricing with group deployment calculator. Business value: transparent pricing reduces negotiation friction. The group calculator lets multi-warehouse enterprises self-serve their quote, shortening the sales cycle."),
            ]
        ),
        (
            "⚡ Demo & Simulation",
            "#06b6d4",
            [
                ("Real-Time Simulation", "Embedded HTML warehouse simulation. Business value: <b>visual proof of concept</b>. Use during client site visits to show live wave allocation behavior without exposing the client's real data."),
                ("Demo Mode", "Auto-play investor pitch slides. Business value: <b>consistent messaging</b>. Every investor, every conference, every course defense delivers the same polished narrative: problem → solution → impact. No dependency on the presenter's memory."),
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
    st.info("Tip: Navigate to any section using the sidebar on the left. Each section is self-contained and can be demonstrated independently.")

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
elif selected_page_key == "strategy_opt":
    render_strategy_optimizer()
elif selected_page_key == "live_adaptive":
    render_live_adaptive()

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
elif selected_page_key == "ai_learning":
    render_ai_learning_engine()
elif selected_page_key == "multi_wh":
    render_multi_warehouse()
elif selected_page_key == "patent_wall":
    render_patent_wall()

# --- Business Value ---
elif selected_page_key == "roi_calc":
    render_roi_calculator()
elif selected_page_key == "tco_analysis":
    render_tco_analysis()
elif selected_page_key == "comp_radar":
    render_competitor_radar()
elif selected_page_key == "plans_pricing":
    render_plans_pricing()

# --- Demo & Simulation ---
elif selected_page_key == "rt_sim":
    render_realtime_simulation()
elif selected_page_key == "demo_mode":
    render_demo_mode()

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align:center; font-size:0.7rem; color:#475569; padding:1rem 0;">
    Sunergy Pharma Professional Edition v3.0 | Day 4 Commercialization Build | 2026/06/07<br>
    Modular Architecture: page_modules/ | Built with Streamlit + Real Algorithm Engines<br>
    <span style="color:#f59e0b;">Professional Edition</span>
</div>
""", unsafe_allow_html=True)
