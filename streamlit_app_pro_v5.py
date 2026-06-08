"""
Sunergy Pharma — Professional Edition v5.0 (HF AI Enhanced)
============================================================
Refactored Pro Tier with Unified Data Upload Hub + Hugging Face AI Integration

New in v5.0:
  - 🤖 Sunergy Copilot: global sidebar assistant + dedicated FAQ page
  - AI Insight Engine on Algorithm Arena, Strategy Optimizer, Live Adaptive, SLA Analytics
  - AI Report Generator on What-If Lab + Business Analysis
  - AI Root Cause Analysis with lightweight RAG on Alert Center
  - AI Demand Forecasting in Data Center (HF time-series models)
  - All powered by Hugging Face Qwen2.5-Instruct with graceful offline fallback

Architecture:
  - page_modules/shared.py        CSS, data generators, UPLOAD ROUTERS, validators
  - page_modules/orders_inventory.py  Orders & Inventory (upload-aware)
  - page_modules/operations.py    Operations Monitoring (upload-aware)
  - page_modules/scheduling.py    Smart Scheduling Engine
  - page_modules/tech_showcase.py Tech Deep Dive
  - page_modules/business.py      Business Value
  - page_modules/demo.py          Demo & Simulation
  - hf_integration/               NEW: Hugging Face LLM client, prompts, insight, copilot, RAG, forecast

All UI text is English. Each page module can be removed independently.
Author: AI-assisted implementation
Date: 2026/06/08
"""

import io
import json
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Optional 3D visualization
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="Sunergy Pharma | Professional Edition v4",
    page_icon="🔶",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# IMPORT SHARED UTILITIES
# =============================================================================
from page_modules.shared import (
    PRO_CSS, init_pro_session_state, init_upload_session_state,
    get_data_source, set_data_source,
    validate_orders, validate_inventory, validate_tasks, validate_workers, validate_sla, validate_alerts,
    generate_template_csv, get_upload_summary,
    try_import_what_if, try_import_mos, try_import_adaptive,
    try_import_hf,
)

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
    render_hf_copilot,
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
init_upload_session_state()

# --- Copilot sidebar state ---
if "copilot_expanded" not in st.session_state:
    st.session_state.copilot_expanded = False
if "copilot_history" not in st.session_state:
    st.session_state.copilot_history = []

st.markdown(PRO_CSS, unsafe_allow_html=True)

# =============================================================================
# LIVE DATA BADGE (visible when upload mode is active)
# =============================================================================
if get_data_source() == "upload":
    st.markdown("""
    <div style="position:fixed; top:12px; right:12px; z-index:9999;
                background:rgba(16,185,129,0.15); border:1px solid rgba(16,185,129,0.4);
                color:#10b981; padding:4px 14px; border-radius:20px;
                font-size:0.75rem; font-weight:700; backdrop-filter:blur(4px);">
        🟢 Live Data Mode
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# SIDEBAR: DATA HUB + GROUPED NAVIGATION
# =============================================================================

NAV_STRUCTURE = {
    "🏠 Overview": [
        ("Command Center", "cmd_center"),
        ("Data Center", "data_center"),
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
        ("🤖 AI Copilot", "hf_copilot"),
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


def render_data_hub():
    """Render the centralized Data Hub panel in the sidebar with differentiated upload ports."""
    st.markdown('<div class="section-header" style="font-size:0.95rem; margin-top:0;">📂 Data Hub</div>', unsafe_allow_html=True)

    # Data source toggle
    source_options = ["Demo Data", "Upload My Data"]
    current_idx = 1 if get_data_source() == "upload" else 0
    selected_source = st.radio("Data Source", source_options, index=current_idx, label_visibility="collapsed")

    if selected_source == "Upload My Data":
        st.session_state.data_source = "upload"

        # ── Required Files ──
        with st.expander("📦 Required Files", expanded=True):
            st.markdown('<div style="font-size:0.75rem; color:#64748b; margin-bottom:0.8rem;">These two files power the core operational dashboards.</div>', unsafe_allow_html=True)

            # 1. Orders
            st.markdown('<div style="font-weight:700; color:#f8fafc; font-size:0.85rem;">📋 1. Order Stream</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size:0.7rem; color:#94a3b8; margin-bottom:0.3rem;">Feeds: Omni-Channel Orders, Order Analytics, Operations Dashboard</div>', unsafe_allow_html=True)
            up_orders = st.file_uploader("Select orders.csv", type=["csv"], key="fu_orders", label_visibility="collapsed")
            if up_orders is not None:
                try:
                    df = pd.read_csv(up_orders)
                    result = validate_orders(df)
                    if result["valid"]:
                        st.session_state.uploaded_orders = df
                        st.markdown(f'<div style="font-size:0.75rem; color:#10b981;">✅ Loaded: {result["row_count"]:,} orders</div>', unsafe_allow_html=True)
                    else:
                        st.session_state.uploaded_orders = None
                        st.markdown(f'<div style="font-size:0.75rem; color:#ef4444;">❌ {result["errors"][0]}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.session_state.uploaded_orders = None
                    st.markdown(f'<div style="font-size:0.75rem; color:#ef4444;">❌ Parse error: {e}</div>', unsafe_allow_html=True)
            elif st.session_state.get("uploaded_orders") is not None:
                rows = len(st.session_state.uploaded_orders)
                st.markdown(f'<div style="font-size:0.75rem; color:#10b981;">✅ Cached: {rows:,} orders</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="font-size:0.75rem; color:#64748b;">⬜ Waiting for upload...</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # 2. Inventory
            st.markdown('<div style="font-weight:700; color:#f8fafc; font-size:0.85rem;">🌡️ 2. Inventory Master</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size:0.7rem; color:#94a3b8; margin-bottom:0.3rem;">Feeds: Warehouse & Zones, Near-Expiry FIFO</div>', unsafe_allow_html=True)
            up_inventory = st.file_uploader("Select inventory.csv", type=["csv"], key="fu_inventory", label_visibility="collapsed")
            if up_inventory is not None:
                try:
                    df = pd.read_csv(up_inventory)
                    result = validate_inventory(df)
                    if result["valid"]:
                        st.session_state.uploaded_inventory = df
                        st.markdown(f'<div style="font-size:0.75rem; color:#10b981;">✅ Loaded: {result["row_count"]:,} SKUs</div>', unsafe_allow_html=True)
                    else:
                        st.session_state.uploaded_inventory = None
                        st.markdown(f'<div style="font-size:0.75rem; color:#ef4444;">❌ {result["errors"][0]}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.session_state.uploaded_inventory = None
                    st.markdown(f'<div style="font-size:0.75rem; color:#ef4444;">❌ Parse error: {e}</div>', unsafe_allow_html=True)
            elif st.session_state.get("uploaded_inventory") is not None:
                rows = len(st.session_state.uploaded_inventory)
                st.markdown(f'<div style="font-size:0.75rem; color:#10b981;">✅ Cached: {rows:,} SKUs</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="font-size:0.75rem; color:#64748b;">⬜ Waiting for upload...</div>', unsafe_allow_html=True)

        # ── Operational Files ──
        with st.expander("🔧 Operational Files", expanded=False):
            st.markdown('<div style="font-size:0.75rem; color:#64748b; margin-bottom:0.8rem;">Enhance Task Workstation, SLA Analytics, and Alert Center.</div>', unsafe_allow_html=True)

            # 3. Tasks
            st.markdown('<div style="font-weight:700; color:#f8fafc; font-size:0.85rem;">👷 3. Picking Tasks</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size:0.7rem; color:#94a3b8; margin-bottom:0.3rem;">Feeds: Task Workstation, Operation Queue</div>', unsafe_allow_html=True)
            up_tasks = st.file_uploader("Select tasks.csv", type=["csv"], key="fu_tasks", label_visibility="collapsed")
            if up_tasks is not None:
                try:
                    df = pd.read_csv(up_tasks)
                    result = validate_tasks(df)
                    if result["valid"]:
                        st.session_state.uploaded_tasks = df
                        st.markdown(f'<div style="font-size:0.75rem; color:#10b981;">✅ Loaded: {result["row_count"]:,} tasks</div>', unsafe_allow_html=True)
                    else:
                        st.session_state.uploaded_tasks = None
                        st.markdown(f'<div style="font-size:0.75rem; color:#ef4444;">❌ {result["errors"][0]}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.session_state.uploaded_tasks = None
                    st.markdown(f'<div style="font-size:0.75rem; color:#ef4444;">❌ Parse error: {e}</div>', unsafe_allow_html=True)
            elif st.session_state.get("uploaded_tasks") is not None:
                rows = len(st.session_state.uploaded_tasks)
                st.markdown(f'<div style="font-size:0.75rem; color:#10b981;">✅ Cached: {rows:,} tasks</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="font-size:0.75rem; color:#64748b;">⬜ Optional — not uploaded</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # 4. Workers
            st.markdown('<div style="font-weight:700; color:#f8fafc; font-size:0.85rem;">👤 4. Labor Roster</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size:0.7rem; color:#94a3b8; margin-bottom:0.3rem;">Feeds: Task Workstation, Labor Efficiency</div>', unsafe_allow_html=True)
            up_workers = st.file_uploader("Select workers.csv", type=["csv"], key="fu_workers", label_visibility="collapsed")
            if up_workers is not None:
                try:
                    df = pd.read_csv(up_workers)
                    result = validate_workers(df)
                    if result["valid"]:
                        st.session_state.uploaded_workers = df
                        st.markdown(f'<div style="font-size:0.75rem; color:#10b981;">✅ Loaded: {result["row_count"]:,} workers</div>', unsafe_allow_html=True)
                    else:
                        st.session_state.uploaded_workers = None
                        st.markdown(f'<div style="font-size:0.75rem; color:#ef4444;">❌ {result["errors"][0]}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.session_state.uploaded_workers = None
                    st.markdown(f'<div style="font-size:0.75rem; color:#ef4444;">❌ Parse error: {e}</div>', unsafe_allow_html=True)
            elif st.session_state.get("uploaded_workers") is not None:
                rows = len(st.session_state.uploaded_workers)
                st.markdown(f'<div style="font-size:0.75rem; color:#10b981;">✅ Cached: {rows:,} workers</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="font-size:0.75rem; color:#64748b;">⬜ Optional — not uploaded</div>', unsafe_allow_html=True)

        # ── Analytics Files ──
        with st.expander("📊 Analytics Files", expanded=False):
            st.markdown('<div style="font-size:0.75rem; color:#64748b; margin-bottom:0.8rem;">Replace historical mock data with your own records.</div>', unsafe_allow_html=True)

            # 5. SLA History
            st.markdown('<div style="font-weight:700; color:#f8fafc; font-size:0.85rem;">📈 5. SLA History</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size:0.7rem; color:#94a3b8; margin-bottom:0.3rem;">Feeds: SLA Analytics, Compliance Trends</div>', unsafe_allow_html=True)
            up_sla = st.file_uploader("Select sla_history.csv", type=["csv"], key="fu_sla", label_visibility="collapsed")
            if up_sla is not None:
                try:
                    df = pd.read_csv(up_sla)
                    result = validate_sla(df)
                    if result["valid"]:
                        st.session_state.uploaded_sla = df
                        st.markdown(f'<div style="font-size:0.75rem; color:#10b981;">✅ Loaded: {result["row_count"]:,} records</div>', unsafe_allow_html=True)
                    else:
                        st.session_state.uploaded_sla = None
                        st.markdown(f'<div style="font-size:0.75rem; color:#ef4444;">❌ {result["errors"][0]}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.session_state.uploaded_sla = None
                    st.markdown(f'<div style="font-size:0.75rem; color:#ef4444;">❌ Parse error: {e}</div>', unsafe_allow_html=True)
            elif st.session_state.get("uploaded_sla") is not None:
                rows = len(st.session_state.uploaded_sla)
                st.markdown(f'<div style="font-size:0.75rem; color:#10b981;">✅ Cached: {rows:,} records</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="font-size:0.75rem; color:#64748b;">⬜ Optional — not uploaded</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # 6. Alerts
            st.markdown('<div style="font-weight:700; color:#f8fafc; font-size:0.85rem;">🔔 6. Alert Log</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size:0.7rem; color:#94a3b8; margin-bottom:0.3rem;">Feeds: Alert Center, Exception Tracking</div>', unsafe_allow_html=True)
            up_alerts = st.file_uploader("Select alerts.csv", type=["csv"], key="fu_alerts", label_visibility="collapsed")
            if up_alerts is not None:
                try:
                    df = pd.read_csv(up_alerts)
                    result = validate_alerts(df)
                    if result["valid"]:
                        st.session_state.uploaded_alerts = df
                        st.markdown(f'<div style="font-size:0.75rem; color:#10b981;">✅ Loaded: {result["row_count"]:,} alerts</div>', unsafe_allow_html=True)
                    else:
                        st.session_state.uploaded_alerts = None
                        st.markdown(f'<div style="font-size:0.75rem; color:#ef4444;">❌ {result["errors"][0]}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.session_state.uploaded_alerts = None
                    st.markdown(f'<div style="font-size:0.75rem; color:#ef4444;">❌ Parse error: {e}</div>', unsafe_allow_html=True)
            elif st.session_state.get("uploaded_alerts") is not None:
                rows = len(st.session_state.uploaded_alerts)
                st.markdown(f'<div style="font-size:0.75rem; color:#10b981;">✅ Cached: {rows:,} alerts</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="font-size:0.75rem; color:#64748b;">⬜ Optional — not uploaded</div>', unsafe_allow_html=True)

        st.markdown("---")

        # Overall status
        summary = get_upload_summary()
        loaded = [k for k, v in summary.items() if v["loaded"]]
        total = len(summary)
        st.markdown(f'<div style="font-size:0.8rem; color:#94a3b8; text-align:center;">{len(loaded)} of {total} file types loaded</div>', unsafe_allow_html=True)

        if st.button("Clear All Uploads", width='stretch'):
            st.session_state.uploaded_orders = None
            st.session_state.uploaded_inventory = None
            st.session_state.uploaded_tasks = None
            st.session_state.uploaded_workers = None
            st.session_state.uploaded_sla = None
            st.session_state.uploaded_alerts = None
            st.session_state.data_source = "mock"
            st.rerun()

    else:
        if st.session_state.data_source != "mock":
            st.session_state.data_source = "mock"
        st.markdown('<div style="font-size:0.8rem; color:#64748b;">Using synthetic demo data. Switch to "Upload My Data" to analyze your own warehouse.</div>', unsafe_allow_html=True)


with st.sidebar:
    st.markdown("""
    <div style="text-align:center; margin-bottom:1.5rem;">
        <div style="font-size:1.4rem; font-weight:800; color:#f8fafc;">🔶 Sunergy Pharma</div>
        <div style="font-size:0.8rem; color:#94a3b8;">Professional Edition v5.0</div>
        <div style="margin-top:0.5rem;">
            <span style="background:linear-gradient(135deg, #f59e0b, #ec4899); color:white; padding:3px 10px; border-radius:12px; font-size:0.7rem; font-weight:700;">PRO</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- Sunergy Copilot (top sidebar, collapsible) ---
    hf = try_import_hf()
    copilot_ready = hf.get("is_ready") and hf.get("copilot")
    status_color = "#10b981" if copilot_ready else "#f59e0b"
    status_text = "Online" if copilot_ready else "Offline"

    toggle_arrow = "▲" if st.session_state.copilot_expanded else "▼"
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                border-radius: 12px; padding: 0.7rem 1rem; margin: 0.5rem 0;
                cursor: pointer; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
                display: flex; justify-content: space-between; align-items: center;
                transition: all 0.3s ease;">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <span style="font-size: 1.1rem;">🤖</span>
            <span style="font-weight: 700; color: white; font-size: 0.9rem;">Sunergy Copilot</span>
            <span style="background: rgba(255,255,255,0.25); color: white; padding: 1px 8px;
                       border-radius: 10px; font-size: 0.6rem; font-weight: 600; margin-left: 4px;">
                {status_text}
            </span>
        </div>
        <span style="color: white; font-size: 0.8rem; opacity: 0.9;">{toggle_arrow}</span>
    </div>
    """, unsafe_allow_html=True)

    if st.button(toggle_arrow, key="copilot_toggle_pro5", width='stretch'):
        st.session_state.copilot_expanded = not st.session_state.copilot_expanded
        st.rerun()

    if st.session_state.copilot_expanded:
        quick_qs = ["What is KGDRL?", "Explain NSGA-II", "Adaptive policy?", "Upload my data?"]
        q_cols = st.columns(2)
        for i, q in enumerate(quick_qs):
            with q_cols[i % 2]:
                if st.button(q, key=f"cq_pro5_{i}", width='stretch'):
                    st.session_state.copilot_history.append(("user", q))
                    if copilot_ready:
                        _page_key = locals().get("selected_page_key", "Unknown")
                        page_ctx = f"Current page: {_page_key}"
                        ans = hf["copilot"].ask_with_context(q, page_name=_page_key, page_context=page_ctx, lang="en")
                    else:
                        ans = f"🤖 Copilot is offline.\n\n**Reason:** {hf.get('msg', 'Unknown')}\n\nPlease install dependencies (`pip install -r requirements.txt`) and configure HF_TOKEN."
                    st.session_state.copilot_history.append(("ai", ans))
                    st.rerun()

        for role, msg in st.session_state.copilot_history[-6:]:
            if role == "user":
                st.markdown(f'<div style="text-align:right; font-size:0.8rem; color:#3b82f6; margin:0.3rem 0;">💬 {msg}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="background:#111827; border-radius:6px; padding:0.5rem; font-size:0.8rem; color:#e2e8f0; line-height:1.5; margin:0.3rem 0;">🤖 {msg}</div>', unsafe_allow_html=True)

        user_q = st.text_input("Ask anything...", key="copilot_input_pro5", label_visibility="collapsed")
        if user_q:
            st.session_state.copilot_history.append(("user", user_q))
            if copilot_ready:
                _page_key = locals().get("selected_page_key", "Unknown")
                page_ctx = f"Current page: {_page_key}"
                ans = hf["copilot"].ask_with_context(user_q, page_name=_page_key, page_context=page_ctx, lang="en")
            else:
                ans = f"🤖 Copilot is offline.\n\n**Reason:** {hf.get('msg', 'Unknown')}\n\nPlease install dependencies (`pip install -r requirements.txt`) and configure HF_TOKEN."
            st.session_state.copilot_history.append(("ai", ans))
            st.rerun()

        if st.button("Clear Chat", key="copilot_clear_pro5", width='stretch'):
            st.session_state.copilot_history = []
            st.rerun()

    st.markdown("---")

    # --- DATA HUB (centralized, always visible) ---
    render_data_hub()
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
        Sunergy Pharma Pro v5.0<br>
        Day 4 Commercialization Build<br>
        2026/06/08
    </div>
    """)

# =============================================================================
# HELPER: Data source banner for operational pages
# =============================================================================

def render_data_source_banner():
    """Show a subtle banner indicating current data source."""
    if get_data_source() == "upload":
        summary = get_upload_summary()
        loaded = [k for k, v in summary.items() if v["loaded"]]
        if loaded:
            st.info(f"📂 Live Data Mode | Active files: {', '.join(loaded)}")
        else:
            st.warning("📂 Upload Mode selected but no files loaded yet. Using demo data as fallback.")
    else:
        st.caption("🎲 Using demo data. Upload your own CSVs in the Data Hub to see real metrics.")


# =============================================================================
# 3D COMMAND CENTER DASHBOARD
# =============================================================================

def render_3d_command_center():
    """Render an immersive 3D dashboard using Plotly with auto-rotate animation."""
    if not PLOTLY_AVAILABLE:
        st.info("💡 Install plotly for 3D visualization: pip install plotly>=5.0")
        return

    st.markdown('<div class="section-header">🌌 Immersive 3D Command Center</div>', unsafe_allow_html=True)
    st.caption("Drag to explore. Click Play to animate. All figures show enterprise-value metrics.")

    # =============================================================================
    # DATA GENERATION
    # =============================================================================
    np.random.seed(42)

    # --- Chart 1: Operational Profit Mountain ---
    zones = ["Ambient", "Cool", "Cold", "Frozen", "Deep Frozen"]
    hours = ["Night\n(0-6h)", "Early\n(6-8h)", "Morning\nPeak\n(8-12h)", "Afternoon\n(12-16h)", "Evening\nPeak\n(16-20h)", "Late\n(20-24h)"]
    margin_per_order = {"Ambient": 12, "Cool": 18, "Cold": 28, "Frozen": 45, "Deep Frozen": 60}
    labor_cost_per_shift = {"Ambient": 3200, "Cool": 4800, "Cold": 8000, "Frozen": 14000, "Deep Frozen": 20000}
    order_share = [0.05, 0.10, 0.35, 0.25, 0.20, 0.05]
    base_daily = 2000

    profit_grid = np.zeros((len(zones), len(hours)))
    for i, z in enumerate(zones):
        for j, _ in enumerate(hours):
            orders = base_daily * order_share[j] * np.random.uniform(0.85, 1.15)
            revenue = orders * margin_per_order[z]
            cost = labor_cost_per_shift[z] + orders * 0.02 * np.random.choice([0, 50, 200, 800])
            profit_grid[i, j] = revenue - cost

    # --- Chart 2: Investment Trajectory Ribbon ---
    months = np.arange(0, 61)
    scenario_params = {
        "Without Sunergy": {"gain": 0.0, "fee": 0, "impl": 0, "color": "#64748b"},
        "Conservative": {"gain": 0.15, "fee": 8999, "impl": 50000, "color": "#3b82f6"},
        "Neutral": {"gain": 0.25, "fee": 8999, "impl": 50000, "color": "#f59e0b"},
        "Optimistic": {"gain": 0.35, "fee": 8999, "impl": 50000, "color": "#10b981"},
    }
    base_monthly_cost = 150000
    trajectories = {}
    for name, p in scenario_params.items():
        cum = []
        running = -p["impl"]
        for m in months:
            saving = base_monthly_cost * p["gain"] * (1 - np.exp(-m / 6))
            running += saving - p["fee"]
            cum.append(running)
        trajectories[name] = np.array(cum)

    # =============================================================================
    # PHASE A + B: Operational Profit Mountain (3D Surface + Play/Pause)
    # =============================================================================
    col3d_1, col3d_2 = st.columns(2)

    with col3d_1:
        st.markdown('<div style="font-weight:700; color:#f8fafc; font-size:0.9rem; margin-bottom:0.3rem;">🏔️ Operational Profit Mountain</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.75rem; color:#94a3b8; margin-bottom:0.5rem;">X=Time of Day | Y=Temp Zone | Z=Net Profit (CNY/shift)</div>', unsafe_allow_html=True)

        fig1 = go.Figure(data=[go.Surface(
            z=profit_grid,
            x=hours,
            y=zones,
            colorscale=[
                [0, "#7f1d1d"], [0.25, "#ef4444"], [0.45, "#f59e0b"],
                [0.55, "#eab308"], [0.75, "#22c55e"], [1, "#064e3b"]
            ],
            showscale=True,
            colorbar=dict(title=dict(text="CNY", font=dict(color="#94a3b8")), tickfont=dict(color="#94a3b8"), thickness=15),
            hovertemplate="Time: %{x}<br>Zone: %{y}<br>Profit: %{z:,.0f} CNY<extra></extra>",
            contours=dict(
                z=dict(show=True, usecolormap=True, highlightcolor="#f8fafc", project=dict(z=True)),
            ),
            lighting=dict(ambient=0.6, diffuse=0.8, specular=0.5, roughness=0.4),
        )])

        fig1.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=30, b=0),
            height=420,
            scene=dict(
                xaxis=dict(title="", color="#94a3b8", tickfont=dict(size=9)),
                yaxis=dict(title="", color="#94a3b8", tickfont=dict(size=9)),
                zaxis=dict(title="Profit (CNY)", color="#94a3b8", gridcolor="rgba(148,163,184,0.1)"),
                bgcolor="rgba(17,24,39,0.6)",
                camera=dict(eye=dict(x=1.6, y=0.8, z=1.1)),
                aspectratio=dict(x=1.2, y=0.8, z=0.6),
            ),
        )
        st.plotly_chart(fig1, width='stretch', config=dict(displayModeBar=False))

    # =============================================================================
    # PHASE A + C: Investment Trajectory Ribbon (3D Lines + Play/Pause)
    # =============================================================================
    with col3d_2:
        st.markdown('<div style="font-weight:700; color:#f8fafc; font-size:0.9rem; margin-bottom:0.3rem;">📈 Investment Trajectory Ribbon</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.75rem; color:#94a3b8; margin-bottom:0.5rem;">X=Month | Y=Scenario | Z=Cumulative Cash Flow (CNY)</div>', unsafe_allow_html=True)

        fig2 = go.Figure()
        for idx, (name, vals) in enumerate(trajectories.items()):
            y_offset = idx * 150000
            fig2.add_trace(go.Scatter3d(
                x=months,
                y=[idx] * len(months),
                z=vals,
                mode="lines",
                name=name,
                line=dict(color=scenario_params[name]["color"], width=5),
                hovertemplate="Month: %{x}<br>Scenario: " + name + "<br>Cash Flow: %{z:,.0f} CNY<extra></extra>",
            ))
            # Add breakeven dot
            cross = np.where(vals > 0)[0]
            if len(cross) > 0 and name != "Without Sunergy":
                first = cross[0]
                fig2.add_trace(go.Scatter3d(
                    x=[months[first]], y=[idx], z=[vals[first]],
                    mode="markers",
                    marker=dict(size=6, color=scenario_params[name]["color"], symbol="diamond"),
                    showlegend=False,
                    hovertemplate=name + " breaks even at Month " + str(months[first]) + "<extra></extra>",
                ))

        # Breakeven plane at Z=0
        fig2.add_trace(go.Mesh3d(
            x=[0, 60, 60, 0], y=[-0.5, -0.5, 3.5, 3.5], z=[0, 0, 0, 0],
            color="#ef4444", opacity=0.08, hoverinfo="skip", showlegend=False,
        ))

        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=30, b=0),
            height=420,
            showlegend=True,
            legend=dict(
                orientation="h", yanchor="bottom", y=-0.05, xanchor="center", x=0.5,
                font=dict(color="#94a3b8", size=10), bgcolor="rgba(17,24,39,0.6)",
            ),
            scene=dict(
                xaxis=dict(title="Month", color="#94a3b8", gridcolor="rgba(148,163,184,0.1)"),
                yaxis=dict(title="", color="#94a3b8", tickvals=[0, 1, 2, 3], ticktext=list(scenario_params.keys()), tickfont=dict(size=9)),
                zaxis=dict(title="Cash Flow (CNY)", color="#94a3b8", gridcolor="rgba(148,163,184,0.1)"),
                bgcolor="rgba(17,24,39,0.6)",
                camera=dict(eye=dict(x=2.0, y=1.0, z=1.2)),
                aspectratio=dict(x=1.5, y=0.8, z=0.7),
            ),
        )
        st.plotly_chart(fig2, width='stretch', config=dict(displayModeBar=False))

    st.markdown("---")

    # =============================================================================
    # BONUS: 2D Heatmap Summary (complements 3D views)
    # =============================================================================
    st.markdown('<div style="font-weight:700; color:#f8fafc; font-size:0.9rem; margin-bottom:0.3rem;">🔥 Profitability Heatmap (2D Summary)</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.75rem; color:#94a3b8; margin-bottom:0.5rem;">Zone-Time matrix: darker green = higher profit; red = loss zone</div>', unsafe_allow_html=True)

    fig3 = go.Figure(data=go.Heatmap(
        z=profit_grid,
        x=hours,
        y=zones,
        colorscale=[
            [0, "#7f1d1d"], [0.2, "#ef4444"], [0.4, "#f59e0b"],
            [0.6, "#eab308"], [0.8, "#22c55e"], [1, "#064e3b"]
        ],
        showscale=True,
        colorbar=dict(title=dict(text="CNY", font=dict(color="#94a3b8")), tickfont=dict(color="#94a3b8"), thickness=15),
        hovertemplate="Zone: %{y}<br>Time: %{x}<br>Profit: %{z:,.0f} CNY<extra></extra>",
    ))
    fig3.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        height=260,
        xaxis=dict(color="#94a3b8", tickfont=dict(size=10)),
        yaxis=dict(color="#94a3b8", tickfont=dict(size=10)),
    )
    st.plotly_chart(fig3, width='stretch', config=dict(displayModeBar=False))

    st.markdown("---")


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
            <div style="font-size:0.7rem; color:#64748b; margin-top:0.3rem;">v4.0.0</div>
        </div>
        """, unsafe_allow_html=True)

    # --- 3D Immersive Dashboard ---
    render_3d_command_center()

    # --- Key Metrics ---
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

# --- Data Center (NEW in v4.0) ---
elif selected_page_key == "data_center":
    st.markdown('<div class="main-header">Data Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Upload review, validation, and CSV templates</div>', unsafe_allow_html=True)

    render_data_source_banner()

    st.markdown("---")

    # --- Templates download section ---
    st.markdown('<div class="section-header">CSV Templates</div>', unsafe_allow_html=True)
    st.markdown("Download empty templates with correct column headers, fill them with your warehouse data, then upload via the Data Hub.")

    template_types = ["orders", "inventory", "tasks", "workers", "sla_history", "alerts"]
    template_names = ["Orders", "Inventory", "Tasks", "Workers", "SLA History", "Alerts"]
    cols = st.columns(3)
    for i, (key, name) in enumerate(zip(template_types, template_names)):
        with cols[i % 3]:
            csv_content = generate_template_csv(key)
            st.download_button(
                label=f"Download {name} Template",
                data=csv_content,
                file_name=f"template_{key}.csv",
                mime="text/csv",
                width='stretch',
            )

    st.markdown("---")

    # --- Upload review section ---
    st.markdown('<div class="section-header">Upload Review</div>', unsafe_allow_html=True)

    summary = get_upload_summary()
    any_loaded = any(v["loaded"] for v in summary.values())

    if not any_loaded:
        st.info("No data uploaded yet. Use the Data Hub in the sidebar to upload your CSV files.")
    else:
        for key, info in summary.items():
            if info["loaded"]:
                df = st.session_state.get(f"uploaded_{key}")
                with st.expander(f"📄 {key.replace('_', ' ').title()} — {info['rows']} rows x {info['cols']} columns", expanded=True):
                    st.dataframe(df.head(20), hide_index=True, width='stretch')
                    st.caption(f"Showing first 20 of {info['rows']} rows")

                    # Column stats
                    st.markdown("**Column Statistics:**")
                    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
                    if numeric_cols:
                        st.dataframe(df[numeric_cols].describe().transpose(), width='stretch')

    st.markdown("---")

    # --- Validation report ---
    st.markdown('<div class="section-header">Validation Report</div>', unsafe_allow_html=True)

    validators = {
        "orders": (validate_orders, "uploaded_orders"),
        "inventory": (validate_inventory, "uploaded_inventory"),
        "tasks": (validate_tasks, "uploaded_tasks"),
        "workers": (validate_workers, "uploaded_workers"),
        "sla": (validate_sla, "uploaded_sla"),
        "alerts": (validate_alerts, "uploaded_alerts"),
    }

    for key, (validator, state_key) in validators.items():
        df = st.session_state.get(state_key)
        if df is not None:
            result = validator(df)
            col1, col2 = st.columns([1, 4])
            with col1:
                if result["valid"]:
                    st.markdown("✅ **Valid**")
                else:
                    st.markdown("❌ **Errors**")
            with col2:
                st.markdown(f"**{key.replace('_', ' ').title()}**: {result['row_count']} rows")
                if result["errors"]:
                    for err in result["errors"]:
                        st.error(err)
                if result["warnings"]:
                    for warn in result["warnings"]:
                        st.warning(warn)

    if not any_loaded:
        st.caption("Upload files to see validation results.")

    # --- AI Demand Forecasting (HF-powered, Pro only) ---
    st.markdown("---")
    st.markdown('<div class="section-header">🤖 AI Demand Forecasting</div>', unsafe_allow_html=True)

    hf = try_import_hf()
    orders_uploaded = st.session_state.get("uploaded_orders")
    if orders_uploaded is not None and not orders_uploaded.empty and hf["is_ready"] and hf["demand_forecaster"]:
        horizon = st.slider("Forecast Horizon (days)", 3, 14, 7, key="df_horizon")
        if st.button("Run AI Forecast", type="primary", width='stretch'):
            with st.spinner("Running demand forecast via HF model..."):
                try:
                    forecaster = hf["demand_forecaster"].DemandForecaster()
                    forecast_df = forecaster.predict(orders_uploaded, horizon=horizon)
                    summary = forecaster.summarize(forecast_df, historical_df=orders_uploaded, lang="en")

                    col_f1, col_f2 = st.columns([2, 1])
                    with col_f1:
                        st.line_chart(forecast_df.set_index("date")["forecast"])
                    with col_f2:
                        st.markdown(f"""
                        <div style="background:#111827; border-radius:10px; padding:1rem; border-left:4px solid #10b981;">
                            <div style="font-weight:700; color:#10b981; font-size:0.9rem; margin-bottom:0.5rem;">📊 Forecast Summary</div>
                            <div style="font-size:0.8rem; color:#e2e8f0; line-height:1.6;">{summary}</div>
                        </div>
                        """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Forecast failed: {e}")
    else:
        if orders_uploaded is None:
            st.info("Upload orders.csv to enable AI demand forecasting.")
        elif not hf["is_ready"]:
            st.info(hf.get("msg", "AI forecasting requires Hugging Face integration."))
        else:
            st.info("AI forecasting ready. Configure horizon and click Run.")

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
    render_data_source_banner()
    render_omnichannel_orders()
elif selected_page_key == "order_analytics":
    render_data_source_banner()
    render_order_analytics()
elif selected_page_key == "warehouse_zones":
    render_data_source_banner()
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
    render_data_source_banner()
    render_operations_dashboard()
elif selected_page_key == "sla_analytics":
    render_data_source_banner()
    render_sla_analytics()
elif selected_page_key == "task_station":
    render_data_source_banner()
    render_task_workstation()
elif selected_page_key == "alert_center":
    render_data_source_banner()
    render_alert_center()

# --- Tech Deep Dive ---
elif selected_page_key == "kgdrl_framework":
    render_kgdrl_framework()
elif selected_page_key == "ai_learning":
    render_ai_learning_engine()
elif selected_page_key == "multi_wh":
    render_multi_warehouse()
elif selected_page_key == "hf_copilot":
    render_hf_copilot()
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
# GLOBAL: AI Copilot Floating Widget (Pro Edition)
# =============================================================================
hf = try_import_hf()
if hf["is_ready"] and hf["copilot"]:
    with st.sidebar:
        st.markdown("---")
        st.markdown('<div style="font-weight:700; color:#8b5cf6; font-size:0.9rem;">🤖 Sunergy Copilot</div>', unsafe_allow_html=True)
        copilot_q = st.text_input("Ask anything...", key="global_copilot_q", label_visibility="collapsed")
        if copilot_q:
            with st.spinner("Thinking..."):
                # Context-aware: include current page name
                page_ctx = f"User is on page: {selected_page_key}"
                answer = hf["copilot"].ask_with_context(
                    question=copilot_q,
                    page_name=selected_page_key,
                    page_context=page_ctx,
                    lang="en",
                )
            st.markdown(f"""
            <div style="background:#111827; border-radius:8px; padding:0.8rem; border-left:3px solid #8b5cf6; margin-top:0.5rem;">
                <div style="font-size:0.8rem; color:#e2e8f0; line-height:1.5;">{answer}</div>
            </div>
            """, unsafe_allow_html=True)

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align:center; font-size:0.7rem; color:#475569; padding:1rem 0;">
    Sunergy Pharma Professional Edition v5.0 | Day 4 Commercialization Build | 2026/06/08<br>
    Modular Architecture: page_modules/ | Data Upload Hub Enabled | HF AI Powered<br>
    <span style="color:#f59e0b;">Professional Edition</span>
</div>
""", unsafe_allow_html=True)
