"""
Sunergy Pharma — Shared Page Utilities
========================================
Common CSS, data generators, session-state helpers, and constants
used across all page modules.

NOTE: All UI text is English. Each functional block is wrapped in
clear section comments so it can be removed independently later.
"""

import json
import time
import random
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
from pathlib import Path
from datetime import datetime, timedelta

# =============================================================================
# SECTION: Global Constants & Configuration
# Can be trimmed if downstream pages are removed.
# =============================================================================

TEMP_ZONES = ["Ambient", "Cool", "Cold", "Frozen", "Deep Frozen"]
TEMP_COLORS = {
    "Ambient": "#22c55e",
    "Cool": "#3b82f6",
    "Cold": "#06b6d4",
    "Frozen": "#8b5cf6",
    "Deep Frozen": "#6366f1",
}

CLIENT_TYPES = ["Public Hospital", "Chain Pharmacy", "Independent Pharmacy", "Primary Healthcare"]

ZONE_LETTERS = [f"Zone {chr(65 + i)}" for i in range(8)]

MEDICATIONS = [
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

# =============================================================================
# SECTION: Pro Theme CSS
# Remove this section if you switch to a different design system.
# =============================================================================

PRO_CSS = """
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
    .metric-delta { font-size: 0.75rem; margin-top: 0.2rem; }
    .delta-up { color: #10b981; }
    .delta-down { color: #ef4444; }

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

    .roi-card { background: linear-gradient(135deg, #064e3b 0%, #111827 100%); border-radius: 12px; padding: 1.5rem; border: 1px solid rgba(16,185,129,0.3); }

    .zone-card { background: #111827; border-radius: 10px; padding: 1rem; border: 1px solid var(--border); }
    .zone-title { font-size: 1rem; font-weight: 700; color: #f8fafc; }
    .zone-metric { font-size: 1.1rem; font-weight: 700; color: #e2e8f0; }

    .badge { display: inline-block; padding: 2px 10px; border-radius: 6px; font-size: 0.7rem; font-weight: 700; }
    .badge-exception { background: rgba(239, 68, 68, 0.15); color: #f87171; }
    .badge-pending { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
    .badge-active { background: rgba(59, 130, 246, 0.15); color: #60a5fa; }
    .badge-completed { background: rgba(16, 185, 129, 0.15); color: #34d399; }

    .alert-critical { background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; padding: 1rem; border-radius: 8px; margin-bottom: 0.6rem; }
    .alert-warning { background: rgba(245, 158, 11, 0.1); border-left: 4px solid #f59e0b; padding: 1rem; border-radius: 8px; margin-bottom: 0.6rem; }
    .alert-info { background: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6; padding: 1rem; border-radius: 8px; margin-bottom: 0.6rem; }
    .alert-success { background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10b981; padding: 1rem; border-radius: 8px; margin-bottom: 0.6rem; }

    .patent-card { background: #111827; border-radius: 10px; padding: 1.2rem; border: 1px solid var(--border); margin-bottom: 0.8rem; }
    .timeline-dot { width: 12px; height: 12px; border-radius: 50%; background: #f59e0b; display: inline-block; margin-right: 8px; }
    .timeline-line { width: 2px; background: rgba(245, 158, 11, 0.3); margin-left: 5px; }

    [data-testid="stSidebar"] { background: #0f172a; }
</style>
"""

# =============================================================================
# SECTION: Session State Helpers
# =============================================================================

def ensure_state(key: str, default):
    """Initialize session state key if missing."""
    if key not in st.session_state:
        st.session_state[key] = default


def init_pro_session_state():
    """Call once at app startup to initialize all Pro session keys."""
    ensure_state("pro_pareto_front", None)
    ensure_state("pro_pareto_scheduler", None)
    ensure_state("pro_adaptive_results", None)
    ensure_state("pro_adaptive_controller", None)
    ensure_state("pro_what_if_results", None)
    ensure_state("pro_billing", "monthly")
    ensure_state("roi_inputs", {"orders": 2000, "wage": 45, "warehouses": 1, "violation": 3000})
    ensure_state("demo_slide_index", 0)
    ensure_state("demo_auto_play", False)


# =============================================================================
# SECTION: Data Generators
# Remove any generator below if its consuming page is removed.
# =============================================================================

def generate_orders_basic(n: int = 30, seed: int = 42) -> pd.DataFrame:
    """Basic order table for dashboard and operations."""
    np.random.seed(seed)
    temps = ["Ambient", "Cool", "Cold", "Frozen"]
    clients = ["Hospital", "Clinic", "Pharmacy", "Distributor"]
    data = []
    for i in range(n):
        data.append({
            "Order ID": f"ORD-{20260000 + i}",
            "Client": np.random.choice(clients),
            "SKU Count": np.random.choice([3, 4, 5], p=[0.4, 0.35, 0.25]),
            "Temperature": np.random.choice(temps, p=[0.55, 0.25, 0.15, 0.05]),
            "Deadline (h)": round(np.random.exponential(12) + 2, 1),
            "Priority": "Urgent" if np.random.rand() < 0.2 else "Standard",
            "Volume": np.random.randint(10, 100),
            "Status": np.random.choice(
                ["Pending", "Picking", "Packed", "Dispatched"],
                p=[0.3, 0.3, 0.25, 0.15]
            ),
        })
    return pd.DataFrame(data)


def generate_order_log(n: int = 100, seed=None) -> pd.DataFrame:
    """Omni-channel order log with timestamps."""
    if seed is not None:
        np.random.seed(seed)
    temps = ["Ambient", "Cool", "Cold", "Frozen", "Deep Frozen"]
    times = ["Morning Peak", "Afternoon", "Night Peak"]
    now = datetime.now()
    rows = []
    for i in range(n):
        ts = now - timedelta(minutes=np.random.randint(0, 480))
        sku_count = np.random.choice([1, 2, 3, 4, 5], p=[0.15, 0.25, 0.30, 0.20, 0.10])
        rows.append({
            "Order ID": f"ORD-{np.random.randint(100000, 999999)}",
            "Client Type": np.random.choice(CLIENT_TYPES, p=[0.35, 0.30, 0.20, 0.15]),
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


def generate_inventory_data(seed=None) -> pd.DataFrame:
    """Warehouse inventory with expiry tracking."""
    if seed is not None:
        np.random.seed(seed)
    rows = []
    today = datetime.now()
    for name, cat, temp in MEDICATIONS:
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
    """12-month SLA history + 14-day forecast."""
    months = pd.date_range(end=datetime.now(), periods=12, freq="MS").strftime("%b %Y").tolist()
    history = {}
    for client in CLIENT_TYPES:
        base = np.random.uniform(85, 95)
        trend = np.random.uniform(-0.5, 0.5, 12)
        seasonal = 3 * np.sin(np.linspace(0, 2 * np.pi, 12))
        noise = np.random.normal(0, 1.5, 12)
        history[client] = np.clip(base + trend + seasonal + noise, 80, 99.5)

    forecast_days = pd.date_range(start=datetime.now(), periods=14, freq="D").strftime("%m-%d").tolist()
    forecast = {}
    for client in CLIENT_TYPES:
        last = history[client][-1]
        trend = np.random.uniform(-0.2, 0.3, 14)
        forecast[client] = np.clip(last + np.cumsum(trend), 75, 99)

    return months, history, forecast_days, forecast


def generate_picking_tasks(n: int = 30) -> pd.DataFrame:
    """Warehouse picking tasks with optimized paths."""
    skus = ["Insulin Pen", "Amoxicillin", "Ibuprofen", "Metformin", "Aspirin", "Salbutamol", "Omeprazole", "Cefuroxime"]
    tasks = []
    for i in range(n):
        zone = np.random.choice(ZONE_LETTERS)
        client = np.random.choice(CLIENT_TYPES)
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


def generate_labor_data() -> pd.DataFrame:
    """Labor headcount and efficiency by zone."""
    fulltime = np.random.randint(25, 35)
    temp = np.random.randint(10, 25)
    peak_cap = int(fulltime * 2.5)
    efficiency = []
    for z in ZONE_LETTERS:
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
# SECTION: Alert Generator (NEW for Alert Center)
# Can be removed if Alert Center page is removed.
# =============================================================================

def generate_alert_feed(n: int = 12) -> pd.DataFrame:
    """Generate simulated alert events for the Smart Alert Center."""
    np.random.seed(int(time.time()) // 60)
    alert_types = [
        ("Temperature Deviation", "critical", "Cold chain threshold exceeded in Zone C"),
        ("Batch Delay", "warning", "Wave #42 release delayed by 18 min"),
        ("Low Inventory", "warning", "Insulin Glargine stock below safety level"),
        ("High Order Surge", "info", "Order arrival rate 2.4x above baseline"),
        ("Picker Idle", "info", "3 workers idle >15 min in Zone F"),
        ("GSP Compliance", "success", "Daily temperature audit passed"),
    ]
    rows = []
    now = datetime.now()
    for i in range(n):
        typ, severity, msg = random.choice(alert_types)
        ts = now - timedelta(minutes=np.random.randint(1, 120))
        rows.append({
            "Alert ID": f"ALT-{np.random.randint(10000, 99999)}",
            "Type": typ,
            "Severity": severity,
            "Message": msg,
            "Timestamp": ts.strftime("%H:%M:%S"),
            "Zone": np.random.choice(ZONE_LETTERS),
            "Acknowledged": np.random.choice([True, False], p=[0.6, 0.4]),
        })
    df = pd.DataFrame(rows)
    # Sort: critical first, then by time
    sev_order = {"critical": 0, "warning": 1, "info": 2, "success": 3}
    df["sev_rank"] = df["Severity"].map(sev_order)
    df = df.sort_values(["sev_rank", "Timestamp"]).drop("sev_rank", axis=1).reset_index(drop=True)
    return df


# =============================================================================
# SECTION: Competitor Data (NEW for Competitor Radar)
# Can be removed if Competitor Radar page is removed.
# =============================================================================

def get_competitor_data() -> pd.DataFrame:
    """Static competitor benchmark data for radar chart."""
    return pd.DataFrame([
        {"Vendor": "Sunergy (Us)", "Price": 85, "Intelligence": 95, "GSP_Compliance": 98, "Time_to_Deploy": 90, "Real_Time": 92, "Explainability": 96},
        {"Vendor": "SAP EWM", "Price": 20, "Intelligence": 55, "GSP_Compliance": 80, "Time_to_Deploy": 30, "Real_Time": 60, "Explainability": 40},
        {"Vendor": "Manhattan", "Price": 25, "Intelligence": 65, "GSP_Compliance": 75, "Time_to_Deploy": 35, "Real_Time": 70, "Explainability": 45},
        {"Vendor": "Blue Yonder", "Price": 30, "Intelligence": 70, "GSP_Compliance": 70, "Time_to_Deploy": 40, "Real_Time": 75, "Explainability": 50},
        {"Vendor": "FLUX WMS", "Price": 70, "Intelligence": 45, "GSP_Compliance": 60, "Time_to_Deploy": 65, "Real_Time": 50, "Explainability": 35},
        {"Vendor": "Rule-Based", "Price": 95, "Intelligence": 20, "GSP_Compliance": 50, "Time_to_Deploy": 85, "Real_Time": 30, "Explainability": 25},
    ])


# =============================================================================
# SECTION: Patent / Research Timeline Data
# Can be removed if Patent Wall page is removed.
# =============================================================================

def get_patent_timeline() -> list:
    """Patent and research milestone timeline."""
    return [
        {"year": "2024", "title": "KGDRL Paradigm Proposed", "desc": "Knowledge-Graph-guided DRL for pharma wave allocation.", "type": "research"},
        {"year": "2024", "title": "TZU Heuristic Published", "desc": "Temperature-Zone-Urgency priority rule benchmark.", "type": "research"},
        {"year": "2025", "title": "PPO Baseline Validated", "desc": "Vanilla PPO outperforms all heuristics on synthetic data.", "type": "research"},
        {"year": "2025", "title": "GAT Encoder Integrated", "desc": "Graph Attention Network replaces MLP state encoding.", "type": "tech"},
        {"year": "2026", "title": "Patent Application Filed", "desc": "CNIPA invention patent entered substantive examination.", "type": "patent"},
        {"year": "2026", "title": "NSGA-II Multi-Objective", "desc": "Pareto frontier for cost-time-compliance trade-offs.", "type": "tech"},
        {"year": "2026", "title": "Federated Architecture", "desc": "Cross-warehouse collaborative learning design.", "type": "tech"},
        {"year": "2027", "title": "SaaS Commercial Launch", "desc": "Target: 3 pilot pharma distributors.", "type": "milestone"},
    ]


# =============================================================================
# SECTION: JSON Data Loader (for Order Analytics)
# =============================================================================

@st.cache_data
def load_all_json_data() -> dict:
    """Load pre-computed JSON data from ./data directory."""
    base = Path(".") / "data"
    result = {}
    for filename in ["final_results.json", "order_stats.json", "heuristic_results.json", "ppo_training.json", "ppo_eval.json"]:
        path = base / filename
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    result[filename.replace(".json", "")] = json.load(f)
            except Exception:
                result[filename.replace(".json", "")] = None
        else:
            result[filename.replace(".json", "")] = None
    return result


# =============================================================================
# SECTION: Module Import Helpers
# Attempt to import real algorithm modules; gracefully degrade if missing.
# =============================================================================

def try_import_what_if():
    try:
        from what_if_simulator import WhatIfSimulator, ScenarioConfig, ScenarioResult
        return WhatIfSimulator, ScenarioConfig, ScenarioResult, True
    except Exception:
        return None, None, None, False


def try_import_mos():
    try:
        from multi_objective_scheduler import MultiObjectiveScheduler, MultiObjectiveConfig, STRATEGY_PROFILES, ParetoSolution
        return MultiObjectiveScheduler, MultiObjectiveConfig, STRATEGY_PROFILES, ParetoSolution, True
    except Exception:
        return None, None, None, None, False


def try_import_adaptive():
    try:
        from adaptive_policy import AdaptivePolicyController, AdaptiveConfig, ArrivalRateEstimator, AdaptiveWaveCapacity, OnlinePolicyUpdater, PolicyEnsemble, FederatedCoordinator
        return AdaptivePolicyController, AdaptiveConfig, True
    except Exception:
        return None, None, False


def try_import_hf():
    """
    Import Hugging Face integration modules with graceful degradation.
    Returns a dict of available modules and an is_ready flag.
    """
    import traceback
    result = {
        "insight_engine": None,
        "report_generator": None,
        "copilot": None,
        "alert_analyzer": None,
        "demand_forecaster": None,
        "is_ready": False,
        "msg": "HF integration unavailable",
    }
    try:
        from hf_integration import (
            insight_engine, report_generator, copilot,
            alert_analyzer, demand_forecaster, is_llm_ready,
        )
        result["insight_engine"] = insight_engine
        result["report_generator"] = report_generator
        result["copilot"] = copilot
        result["alert_analyzer"] = alert_analyzer
        result["demand_forecaster"] = demand_forecaster
        result["is_ready"] = is_llm_ready()
        result["msg"] = "HF integration ready" if is_llm_ready() else "HF modules loaded but no LLM backend available"
    except Exception:
        result["msg"] = f"HF integration error: {traceback.format_exc()}"
    return result


# =============================================================================
# SECTION: Data Upload Router Layer (NEW for Pro v4.0)
# Centralized data source switching: mock <-> uploaded.
# All P0/P1 pages should call get_*_data() instead of direct generators.
# =============================================================================

def init_upload_session_state():
    """Initialize session state keys for data upload. Call alongside init_pro_session_state()."""
    ensure_state("data_source", "mock")  # "mock" or "upload"
    ensure_state("uploaded_orders", None)
    ensure_state("uploaded_inventory", None)
    ensure_state("uploaded_tasks", None)
    ensure_state("uploaded_workers", None)
    ensure_state("uploaded_sla", None)
    ensure_state("uploaded_alerts", None)
    ensure_state("upload_validation", {})


def get_data_source() -> str:
    """Return current data source mode."""
    return st.session_state.get("data_source", "mock")


def set_data_source(mode: str):
    """Set data source mode and trigger rerun if changed."""
    if mode != get_data_source():
        st.session_state.data_source = mode
        st.rerun()


# --- Data routers: each returns DataFrame (or compatible structure) ---

def _standardize_df_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Convert snake_case CSV column names to Title Case with spaces."""
    if df is None or df.empty:
        return df
    rename_map = {}
    for col in df.columns:
        new_col = col.replace('_', ' ').title()
        special = {
            'Sku': 'SKU',
            'Sku Count': 'SKU Count',
            'Sku Checklist': 'SKU Checklist',
            'Order Id': 'Order ID',
            'Task Id': 'Task ID',
            'Alert Id': 'Alert ID',
            'Est Duration Min': 'Est. Duration (min)',
        }
        new_col = special.get(new_col, new_col)
        rename_map[col] = new_col
    return df.rename(columns=rename_map)


def _map_time_window(val):
    """Map full time-window labels to shortened filter values."""
    val_str = str(val)
    if 'Morning' in val_str or 'Early' in val_str:
        return 'Morning Peak'
    elif 'Afternoon' in val_str:
        return 'Afternoon'
    else:
        return 'Night Peak'


def get_orders_data(n: int = 100, seed=None) -> pd.DataFrame:
    """Route to uploaded orders or mock generator."""
    if get_data_source() == "upload" and st.session_state.get("uploaded_orders") is not None:
        df = st.session_state.uploaded_orders.copy()
        df = _standardize_df_columns(df)
        if 'Time Window' in df.columns:
            df['Time Window'] = df['Time Window'].apply(_map_time_window)
        return df
    return generate_order_log(n=n, seed=seed)


def get_inventory_data(seed=None) -> pd.DataFrame:
    """Route to uploaded inventory or mock generator."""
    if get_data_source() == "upload" and st.session_state.get("uploaded_inventory") is not None:
        df = st.session_state.uploaded_inventory.copy()
        df = _standardize_df_columns(df)
        # Derive Days Left and Risk Level from Expiry Date
        if 'Expiry Date' in df.columns:
            df['Expiry Date'] = pd.to_datetime(df['Expiry Date'], errors='coerce')
            today = pd.Timestamp.now().normalize()
            df['Days Left'] = (df['Expiry Date'] - today).dt.days
            df['Days Left'] = df['Days Left'].fillna(0).astype(int)
            def _risk(days):
                if days <= 30:
                    return 'Critical'
                elif days <= 60:
                    return 'Warning'
                elif days <= 90:
                    return 'Notice'
                return 'Normal'
            df['Risk Level'] = df['Days Left'].apply(_risk)
        # Rename Name to SKU if needed
        if 'Name' in df.columns and 'SKU' not in df.columns:
            df = df.rename(columns={'Name': 'SKU'})
        return df
    return generate_inventory_data(seed=seed)


def get_tasks_data(n: int = 30) -> pd.DataFrame:
    """Route to uploaded tasks or mock generator."""
    if get_data_source() == "upload" and st.session_state.get("uploaded_tasks") is not None:
        df = st.session_state.uploaded_tasks.copy()
        df = _standardize_df_columns(df)
        # Derive Optimized Path if missing
        if 'Optimized Path' not in df.columns:
            def _make_path(row):
                zone = row.get('Source Zone', '')
                checklist = str(row.get('SKU Checklist', ''))
                items = checklist.replace(';', ', ')
                return f"Path: {zone} → Pick [{items}] → Pack → Dispatch"
            df['Optimized Path'] = df.apply(_make_path, axis=1)
        return df
    return generate_picking_tasks(n=n)


def get_labor_data() -> pd.DataFrame:
    """Route to uploaded workers or mock generator."""
    if get_data_source() == "upload" and st.session_state.get("uploaded_workers") is not None:
        df = st.session_state.uploaded_workers.copy()
        df = _standardize_df_columns(df)
        # If workers list uploaded, aggregate to labor stats by zone
        if 'Worker ID' in df.columns:
            agg = df.groupby('Zone').size().reset_index(name='Total Headcount')
            agg['Full-Time Staff'] = agg['Total Headcount']
            agg['Temporary Staff'] = 0
            agg['Peak Season Cap'] = (agg['Total Headcount'] * 2.5).astype(int)
            agg['SKUs/Hour/Person'] = round(np.random.uniform(45, 75), 1)
            agg['Shift'] = 'Morning'
            return agg
        return df
    return generate_labor_data()


def get_alert_data(n: int = 12) -> pd.DataFrame:
    """Route to uploaded alerts or mock generator."""
    if get_data_source() == "upload" and st.session_state.get("uploaded_alerts") is not None:
        df = st.session_state.uploaded_alerts.copy()
        df = _standardize_df_columns(df)
        return df
    return generate_alert_feed(n=n)


def get_orders_basic(n: int = 30, seed: int = 42) -> pd.DataFrame:
    """Route to uploaded orders (sampled) or basic mock generator."""
    if get_data_source() == "upload" and st.session_state.get("uploaded_orders") is not None:
        df = st.session_state.uploaded_orders
        if len(df) > n:
            return df.sample(n=n, random_state=seed).reset_index(drop=True)
        return df
    return generate_orders_basic(n=n, seed=seed)


def get_sla_dataframe() -> pd.DataFrame:
    """Return SLA data as DataFrame (for uploaded mode compatibility)."""
    if get_data_source() == "upload" and st.session_state.get("uploaded_sla") is not None:
        return st.session_state.uploaded_sla
    # Build from mock generator and convert to DataFrame
    months, history, forecast_days, forecast = generate_sla_history()
    rows = []
    for client in history:
        for i, month in enumerate(months):
            rows.append({
                "Period": month, "Client": client, "SLA (%)": round(history[client][i], 1), "Type": "Historical"
            })
        for i, day in enumerate(forecast_days):
            rows.append({
                "Period": day, "Client": client, "SLA (%)": round(forecast[client][i], 1), "Type": "AI Forecast"
            })
    return pd.DataFrame(rows)


def get_sla_history_tuple():
    """Legacy tuple return for backwards compatibility."""
    return generate_sla_history()


# =============================================================================
# SECTION: Upload Validators
# Return dict with keys: valid (bool), errors (list), warnings (list), row_count
# =============================================================================

def validate_orders(df: pd.DataFrame) -> dict:
    errors, warnings = [], []
    required = ["order_id", "client_type", "sku_count", "temperature", "deadline_hours"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        errors.append(f"Missing required columns: {', '.join(missing)}")
    if "temperature" in df.columns:
        invalid = set(df["temperature"].dropna().unique()) - set(TEMP_ZONES)
        if invalid:
            errors.append(f"Invalid temperature values: {invalid}. Expected: {TEMP_ZONES}")
    if "sku_count" in df.columns and (df["sku_count"] < 1).any():
        warnings.append(f"Found {(df['sku_count'] < 1).sum()} rows with sku_count < 1")
    if "client_type" in df.columns:
        invalid_clients = set(df["client_type"].dropna().unique()) - set(CLIENT_TYPES)
        if invalid_clients:
            warnings.append(f"Unrecognized client types: {invalid_clients}. Standard values: {CLIENT_TYPES}")
    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings, "row_count": len(df)}


def validate_inventory(df: pd.DataFrame) -> dict:
    errors, warnings = [], []
    required = ["sku", "name", "temperature_zone", "stock_qty", "expiry_date"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        errors.append(f"Missing required columns: {', '.join(missing)}")
    if "temperature_zone" in df.columns:
        invalid = set(df["temperature_zone"].dropna().unique()) - set(TEMP_ZONES)
        if invalid:
            errors.append(f"Invalid temperature_zone values: {invalid}")
    if "stock_qty" in df.columns and (df["stock_qty"] < 0).any():
        errors.append("Found negative stock_qty values")
    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings, "row_count": len(df)}


def validate_tasks(df: pd.DataFrame) -> dict:
    errors, warnings = [], []
    required = ["task_id", "source_zone", "target_client", "priority", "status"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        errors.append(f"Missing required columns: {', '.join(missing)}")
    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings, "row_count": len(df)}


def validate_workers(df: pd.DataFrame) -> dict:
    errors, warnings = [], []
    required = ["worker_id", "zone"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        errors.append(f"Missing required columns: {', '.join(missing)}")
    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings, "row_count": len(df)}


def validate_sla(df: pd.DataFrame) -> dict:
    errors, warnings = [], []
    required = ["period", "client_category", "on_time_rate"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        errors.append(f"Missing required columns: {', '.join(missing)}")
    if "on_time_rate" in df.columns:
        if (df["on_time_rate"] < 0).any() or (df["on_time_rate"] > 100).any():
            errors.append("on_time_rate must be between 0 and 100")
    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings, "row_count": len(df)}


def validate_alerts(df: pd.DataFrame) -> dict:
    errors, warnings = [], []
    required = ["alert_id", "type", "severity", "message"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        errors.append(f"Missing required columns: {', '.join(missing)}")
    if "severity" in df.columns:
        valid_sev = {"critical", "warning", "info", "success"}
        invalid = set(df["severity"].dropna().unique()) - valid_sev
        if invalid:
            warnings.append(f"Non-standard severity values: {invalid}. Recommended: {valid_sev}")
    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings, "row_count": len(df)}


# =============================================================================
# SECTION: CSV Template Generators
# Provide downloadable empty templates with correct column headers.
# =============================================================================

def generate_template_csv(data_type: str) -> str:
    """Return CSV string for a given template type."""
    templates = {
        "orders": "order_id,client_type,sku_count,temperature,deadline_hours,priority,volume,status,timestamp,time_window\nORD-20260001,Public Hospital,4,Cool,12.5,Urgent,45,Pending Dispatch,08:30:00,Morning Peak",
        "inventory": "sku,name,category,temperature_zone,stock_qty,expiry_date\nINS-001,Insulin Glargine,Cold Chain Insulin,Cold,1200,2026-06-15",
        "tasks": "task_id,source_zone,target_client,sku_checklist,priority,status,assigned_worker,est_duration_min\nTSK-12345,Zone B,Public Hospital,Insulin Pen x2;Amoxicillin x1,Urgent,Pending,Worker-01,15",
        "workers": "worker_id,zone,shift,employment_type\nWorker-01,Zone A,Morning,Full-Time",
        "sla_history": "period,client_category,orders_fulfilled,orders_total,on_time_rate,next_day_rate,temp_compliance_rate,exception_rate\n2026-01,Public Hospital,15234,16000,97.2,99.1,99.8,0.3",
        "alerts": "alert_id,type,severity,message,timestamp,zone,acknowledged\nALT-001,Temperature Deviation,critical,Cold chain threshold exceeded in Zone C,14:30:00,Zone C,False",
    }
    return templates.get(data_type, "")


def get_upload_summary() -> dict:
    """Return a summary dict of all uploaded files for UI display."""
    files = {
        "orders": st.session_state.get("uploaded_orders"),
        "inventory": st.session_state.get("uploaded_inventory"),
        "tasks": st.session_state.get("uploaded_tasks"),
        "workers": st.session_state.get("uploaded_workers"),
        "sla": st.session_state.get("uploaded_sla"),
        "alerts": st.session_state.get("uploaded_alerts"),
    }
    summary = {}
    for key, df in files.items():
        if df is not None:
            summary[key] = {"rows": len(df), "cols": len(df.columns), "loaded": True}
        else:
            summary[key] = {"rows": 0, "cols": 0, "loaded": False}
    return summary
