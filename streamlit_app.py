"""
Smart Wave Allocation Dashboard
Pharmaceutical Distribution - Deep Reinforcement Learning
Digital Innovation Course Project | SDC MSc Innovation Management
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import time
import numpy as np
import pandas as pd
import altair as alt
from pathlib import Path
from collections import Counter

# Page configuration
st.set_page_config(
    page_title="Smart Wave Allocation Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# KaTeX for LaTeX formula rendering (lightweight, no polyfill needed)
st.markdown("""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
    onload="renderMathInElement(document.body, {
        delimiters: [
            {left: '$$', right: '$$', display: true},
            {left: '$', right: '$', display: false}
        ],
        throwOnError: false
    });"></script>
""", unsafe_allow_html=True)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .highlight-box {
        background-color: #f0f7ff;
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
        color: #333333;
    }
    .warning-box {
        background-color: #fff8e1;
        border-left: 4px solid #ff9800;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
        color: #333333;
    }
    .success-box {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
        color: #333333;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        border-radius: 8px 8px 0 0;
    }
</style>
""", unsafe_allow_html=True)

# Helper: load JSON data
def load_json(filename):
    base = Path(__file__).parent / "data"
    path = base / filename
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

# Load all data
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
# SIDEBAR NAVIGATION
# =============================================================================
st.sidebar.markdown("## 📦 Navigation")
page = st.sidebar.radio(
    "Go to",
    [
        "🏠 Home",
        "⚡ Real-time Simulation",
        "🏢 Enterprise Profile",
        "📦 Order Analytics",
        "🔧 Heuristics & Baselines",
        "🤖 PPO Deep RL",
        "📊 Method Comparison",
        "🧠 KGDRL Framework",
        "🏗️ System Architecture",
        "🛠️ AI Tools Review",
        "📋 Project Docs",
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Course:** Digital Innovation")
st.sidebar.markdown("**Program:** SDC MSc Innovation Management")
st.sidebar.markdown("**Date:** June 2026")
st.sidebar.markdown("---")
st.sidebar.info(
    "This dashboard visualizes the Smart Wave Allocation project "
    "for pharmaceutical distribution using Deep Reinforcement Learning."
)

# =============================================================================
# PAGE: HOME
# =============================================================================
if page == "🏠 Home":
    st.markdown('<div class="main-header">Smart Wave Allocation Dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">'
        'Pharmaceutical Distribution · Deep Reinforcement Learning · Knowledge-Guided DRL'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            '<div class="metric-card">'
            '<div class="metric-value">90,000+</div>'
            '<div class="metric-label">Daily Orders</div></div>',
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            '<div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">'
            '<div class="metric-value">423,600</div>'
            '<div class="metric-label">SKU Product Lines</div></div>',
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            '<div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">'
            '<div class="metric-value">88%+</div>'
            '<div class="metric-label">Next-Day Delivery Rate</div></div>',
            unsafe_allow_html=True
        )

    st.markdown("---")

    st.markdown("### 🎯 Project Mission")
    st.markdown("""
    Design and develop a **smart warehouse sorting & dispatch system** that dynamically groups
    incoming pharmaceutical orders into optimal "waves" (batches) for coordinated picking operations,
    using **Proximal Policy Optimization (PPO)** — a Deep Reinforcement Learning algorithm inspired
    by the Knowledge-Guided Deep Reinforcement Learning (KGDRL) research paradigm.
    """)

    st.markdown("### 🚨 Four Core Pain Points")
    pain_points = [
        ("🌡️ Multi-Temperature Zone Mixing",
         "38% of SKUs are near-expiry managed items with temperature requirements spanning ambient, cool, cold, and frozen. "
         "Manual grouping is error-prone, creating drug quality risks and GSP compliance pressure."),
        ("⏰ Deadline Pressure",
         ">88% next-day delivery mandate means same-day sorting and dispatch is non-negotiable. "
         "Improper wave allocation directly leads to order delays and customer dissatisfaction."),
        ("👷 Labor & Vehicle Scheduling Imbalance",
         "Waves too large → sorting overload → error rate rises (~0.35% manual picking error rate, annual return losses > RMB 9M). "
         "Waves too small → resource waste. Peak periods spike volume by 280%."),
        ("💰 Total Cost Difficult to Optimize",
         "Traditional approaches rely on manual experience. Distance, temperature penalties, and time penalties are conflicting "
         "objectives without a unified optimization framework."),
    ]
    for title, desc in pain_points:
        with st.expander(title):
            st.markdown(desc)

    st.markdown("### 📈 Key Results at a Glance")
    if data["final_results"]:
        fr = data["final_results"]
        c1, c2, c3, c4 = st.columns(4)
        ppo = fr.get("ppo_summary", {})
        # Display as reward (higher = better performance)
        ppo_reward = ppo.get("avg_reward", 0)
        c1.metric("PPO Avg Reward", f"{ppo_reward:,.1f}", "Higher = Better")
        c2.metric("PPO Avg Waves", f"{ppo.get('avg_waves', 0):.1f}")
        c3.metric("PPO Avg Distance", f"{ppo.get('avg_distance', 0):.1f} m")
        c4.metric("PPO Temp Violations", f"{ppo.get('avg_violations', 0):.1f}")

    st.markdown("---")
    st.markdown("### 🗂️ Dashboard Guide")
    st.markdown("""
    | Page | Content |
    |------|---------|
    | **Enterprise Profile** | Company background, key metrics, business scale |
    | **Order Analytics** | Order distributions, temperature breakdown, arrival patterns |
    | **Heuristics & Baselines** | Rule-based algorithms: FCFS, EDD, TEMP_FIRST, ZONE_NN, TZU |
    | **PPO Deep RL** | Training curves, actor/critic losses, evaluation metrics |
    | **Method Comparison** | Side-by-side comparison of all methods with rankings |
    | **KGDRL Framework** | Mathematical MDP formulation, reward design, state space |
    | **System Architecture** | Frontend-backend design, data flow, feasibility analysis |
    | **AI Tools Review** | How AI tools were used throughout the project |
    | **Project Docs** | Model documentation, tutorials, and technical references |
    """)


# =============================================================================
# PAGE: ENTERPRISE PROFILE
# =============================================================================
if page == "🏢 Enterprise Profile":
    st.markdown('<div class="main-header">🏢 Enterprise Profile</div>', unsafe_allow_html=True)
    st.markdown("A leading pharmaceutical distribution enterprise in China")

    st.markdown("---")
    st.markdown("### 📊 Key Business Metrics")

    metrics = [
        ("Logistics Centers", "128", "incl. 6 central warehouses"),
        ("Distribution Stations", "856", "nationwide coverage"),
        ("Warehouse Area", "2.65M sqm", "GSP-standard"),
        ("Annual Throughput", ">90M cases", "across 28 provinces"),
        ("Product Lines (SKU)", "423,600", "Western/TCM/devices"),
        ("Partner Manufacturers", "8,600", "supply chain partners"),
        ("Public Hospital Clients", "12,800", "B2B customers"),
        ("Retail Pharmacy Clients", ">250,000", "incl. 5,832 chain"),
        ("B2B Registered Users", ">580,000", "platform users"),
        ("Daily Orders", ">90,000", "B2B platform"),
        ("Next-Day Delivery Rate", ">88%", "service level commitment"),
        ("Annual Revenue (2025)", "RMB 138.76B", "financial scale"),
    ]

    cols = st.columns(3)
    for i, (label, value, note) in enumerate(metrics):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 10px; margin-bottom: 0.8rem;
                        border-left: 4px solid {'#1f77b4' if i % 2 == 0 else '#ff7f0e'};">
                <div style="font-size: 0.85rem; color: #444;">{label}</div>
                <div style="font-size: 1.6rem; font-weight: 700; color: #222;">{value}</div>
                <div style="font-size: 0.75rem; color: #666;">{note}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🏭 Operational Challenges")

    challenges = {
        "SKU Complexity": "38% are near-expiry managed items with varying temperature requirements (ambient, cool, cold, frozen). Sorting rules are highly complex.",
        "Order Fragmentation": ">36,000 daily active customers, mostly small-batch multi-SKU orders averaging 3-5 items per order.",
        "Time Pressure": ">88% next-day delivery requires same-day sorting and dispatch. Peak periods spike volume by 280%.",
        "Labor Bottleneck": "Manual sorting with ~0.35% error rate and annual return losses exceeding RMB 9 million.",
        "Inventory Turnover": "Some pharmaceutical products have near-expiry scrap rates of ~4.8%, urgently requiring smart dispatch systems.",
    }

    for name, desc in challenges.items():
        st.markdown(f"""
        <div class="warning-box">
            <strong>{name}</strong><br>{desc}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🎯 Task Requirements")
    st.markdown("""
    The smart warehouse sorting & dispatch system must deliver:
    1. **Smart Wave Allocation** — Auto-generate sorting waves based on order characteristics, product attributes, and warehouse layout
    2. **Temperature Compliance** — Ensure GSP-compliant segregation of temperature-sensitive products
    3. **Deadline Awareness** — Prioritize urgent orders to maintain >88% next-day delivery
    4. **Cost Optimization** — Minimize total operational cost (picking distance + penalties + setup)
    """)


# =============================================================================
# PAGE: ORDER ANALYTICS
# =============================================================================
if page == "📦 Order Analytics":
    st.markdown('<div class="main-header">📦 Order Analytics</div>', unsafe_allow_html=True)
    st.markdown("Synthetic order data generated from empirical distributions")

    stats = data.get("order_stats")
    if not stats:
        st.warning("Order statistics data not found.")
        st.stop()

    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Orders", stats.get("total_orders", 0))
    c2.metric("Avg Items/Order", f"{stats.get('avg_items_per_order', 0):.2f}")
    c3.metric("Urgent Ratio", f"{stats.get('urgent_ratio', 0)*100:.1f}%")
    c4.metric("Avg Deadline", f"{stats.get('avg_deadline_hours', 0):.1f} hrs")

    st.markdown("---")
    st.markdown("### 🌡️ Temperature Distribution")

    temp_dist = stats.get("temp_distribution", {})
    # Handle both string keys (from JSON) and integer keys
    temp_names = {"ambient": "Ambient", "cool": "Cool", "cold": "Cold", "frozen": "Frozen",
                  0: "Ambient", 1: "Cool", 2: "Cold", 3: "Frozen"}
    temp_colors = {"ambient": "#ff7f0e", "cool": "#2ca02c", "cold": "#1f77b4", "frozen": "#9467bd",
                   0: "#ff7f0e", 1: "#2ca02c", 2: "#1f77b4", 3: "#9467bd"}

    temp_df = pd.DataFrame([
        {"Category": temp_names.get(k, k), "Count": v, "Percentage": v / stats.get("total_orders", 1) * 100}
        for k, v in temp_dist.items()
    ])

    col_chart, col_table = st.columns([2, 1])
    with col_chart:
        import altair as alt
        chart = alt.Chart(temp_df).mark_arc(innerRadius=50).encode(
            theta=alt.Theta(field="Count", type="quantitative"),
            color=alt.Color(field="Category", type="nominal",
                            scale=alt.Scale(domain=["Ambient", "Cool", "Cold", "Frozen"],
                                            range=["#ff7f0e", "#2ca02c", "#1f77b4", "#9467bd"])),
            tooltip=["Category", "Count", "Percentage"]
        ).properties(height=350)
        st.altair_chart(chart, use_container_width=True)

    with col_table:
        st.dataframe(temp_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### 📈 Order Arrival Timeline")

    timeline = stats.get("arrival_timeline", [])
    if timeline:
        df_time = pd.DataFrame(timeline)
        df_time["temp_name"] = df_time["temp"].map(temp_names)
        df_time["urgent_label"] = df_time["urgent"].map({True: "Urgent", False: "Standard"})

        # Arrival histogram
        hist_chart = alt.Chart(df_time).mark_bar(opacity=0.7).encode(
            x=alt.X("time:Q", bin=alt.Bin(maxbins=30), title="Time (minutes from shift start)"),
            y=alt.Y("count()", title="Order Count"),
            color=alt.Color("temp_name:N", title="Temperature",
                            scale=alt.Scale(domain=["Ambient", "Cool", "Cold", "Frozen"],
                                            range=["#ff7f0e", "#2ca02c", "#1f77b4", "#9467bd"]))
        ).properties(height=350, title="Order Arrivals by Temperature Category")
        st.altair_chart(hist_chart, use_container_width=True)

        # Urgent vs Standard over time
        urgent_chart = alt.Chart(df_time).mark_circle(opacity=0.6, size=30).encode(
            x=alt.X("time:Q", title="Time (minutes)"),
            y=alt.Y("temp:O", title="Temperature Category"),
            color=alt.Color("urgent_label:N", scale=alt.Scale(domain=["Standard", "Urgent"],
                                                               range=["#2ca02c", "#d62728"]),
                            title="Priority"),
            tooltip=["time", "temp_name", "urgent_label"]
        ).properties(height=300, title="Order Priority Over Time")
        st.altair_chart(urgent_chart, use_container_width=True)

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
# PAGE: HEURISTICS
# =============================================================================
if page == "🔧 Heuristics & Baselines":
    st.markdown('<div class="main-header">🔧 Heuristics & Baselines</div>', unsafe_allow_html=True)
    st.markdown("Rule-based algorithms for wave allocation comparison")

    st.markdown("---")
    st.markdown("### 📖 Algorithm Descriptions")

    heuristics = {
        "FCFS (First-Come-First-Serve)": {
            "rule": "Add the first candidate order from the pool to the current wave",
            "pros": "Simple, fair, easy to implement",
            "cons": "Ignores temperature, zone proximity, and urgency",
            "color": "#999",
        },
        "TEMP_FIRST": {
            "rule": "Group orders by dominant temperature category first",
            "pros": "Ensures GSP compliance, zero temperature violations",
            "cons": "Sacrifices zone proximity, creates many small waves",
            "color": "#2ca02c",
        },
        "ZONE_NN (Zone Nearest-Neighbor)": {
            "rule": "Add order minimizing distance to current wave centroid",
            "pros": "Minimizes picking path length",
            "cons": "Ignores temperature and deadline constraints",
            "color": "#1f77b4",
        },
        "EDD (Earliest-Due-Date)": {
            "rule": "Prioritize orders with the most urgent deadline",
            "pros": "Maximizes on-time delivery rate",
            "cons": "May create temperature-mixed waves",
            "color": "#ff7f0e",
        },
        "TZU (Temperature-Zone-Urgency)": {
            "rule": "Composite score: 40% temp match + 40% zone proximity + 20% urgency",
            "pros": "Balances all three objectives simultaneously",
            "cons": "Fixed weights may not adapt to dynamic conditions",
            "color": "#d62728",
        },
    }

    for name, info in heuristics.items():
        with st.expander(f"**{name}**"):
            st.markdown(f"""
            <div style="border-left: 4px solid {info['color']}; padding-left: 1rem;">
                <strong>Rule:</strong> {info['rule']}<br>
                <strong style="color: #2ca02c;">Pros:</strong> {info['pros']}<br>
                <strong style="color: #d62728;">Cons:</strong> {info['cons']}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📊 Heuristic Results Summary")

    hr = data.get("heuristic_results")
    if hr and "summary" in hr:
        summary = hr["summary"]
        rows = []
        for name, s in summary.items():
            rows.append({
                "Heuristic": name,
                "Avg Reward": f"{s['avg_reward']:.1f}",
                "Std Reward": f"{s['std_reward']:.1f}",
                "Avg Distance": f"{s['avg_distance']:.1f}",
                "Avg Waves": f"{s['avg_waves']:.1f}",
                "Misses": f"{s['avg_misses']:.1f}",
                "Violations": f"{s['avg_violations']:.1f}",
            })
        df_h = pd.DataFrame(rows)
        st.dataframe(df_h, use_container_width=True, hide_index=True)

        # Visual comparison
        import altair as alt
        df_viz = pd.DataFrame([
            {"Heuristic": k, "Avg Reward": v["avg_reward"], "Avg Distance": v["avg_distance"],
             "Avg Waves": v["avg_waves"], "Violations": v["avg_violations"]}
            for k, v in summary.items()
        ])

        tab1, tab2, tab3 = st.tabs(["Reward", "Distance", "Waves & Violations"])
        with tab1:
            chart = alt.Chart(df_viz).mark_bar().encode(
                x=alt.X("Heuristic:N", sort="-y"),
                y=alt.Y("Avg Reward:Q", title="Average Reward"),
                color=alt.Color("Heuristic:N", legend=None)
            ).properties(height=400)
            st.altair_chart(chart, use_container_width=True)

        with tab2:
            chart = alt.Chart(df_viz).mark_bar(color="#ff7f0e").encode(
                x=alt.X("Heuristic:N"),
                y=alt.Y("Avg Distance:Q", title="Average Picking Distance (m)")
            ).properties(height=400)
            st.altair_chart(chart, use_container_width=True)

        with tab3:
            chart = alt.Chart(df_viz).mark_bar(color="#2ca02c").encode(
                x=alt.X("Heuristic:N"),
                y=alt.Y("Avg Waves:Q", title="Average Waves per Episode")
            ).properties(height=400)
            st.altair_chart(chart, use_container_width=True)

    else:
        st.info("Heuristic results data not available.")


# =============================================================================
# PAGE: PPO DEEP RL
# =============================================================================
if page == "🤖 PPO Deep RL":
    st.markdown('<div class="main-header">🤖 PPO Deep Reinforcement Learning</div>', unsafe_allow_html=True)
    st.markdown("Proximal Policy Optimization training and evaluation")

    st.markdown("---")
    st.markdown("### 🧠 PPO Algorithm Overview")

    st.markdown("""
    <div class="highlight-box">
        <strong>PPO (Proximal Policy Optimization)</strong> is a policy gradient method that improves training stability
        by limiting the size of policy updates via a clipped surrogate objective.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    **Network Architecture:**
    ```
    Actor Network (Policy π_θ):
        Input(state_dim) → FC(hidden) → ReLU → FC(hidden×2) → ReLU
        → FC(hidden) → ReLU → FC(action_dim) → Masked Softmax

    Critic Network (Value V_φ):
        Input(state_dim) → FC(hidden) → ReLU → FC(hidden×2) → ReLU
        → FC(hidden) → ReLU → FC(1)
    ```

    **Key Hyperparameters:**
    | Parameter | Value |
    |-----------|-------|
    | Hidden dim | 128 |
    | Actor LR | 5×10⁻⁴ |
    | Critic LR | 1×10⁻⁵ |
    | Gamma (γ) | 0.96 |
    | GAE Lambda (λ) | 0.95 |
    | Clip epsilon (ε) | 0.2 |
    | Update epochs | 10 |
    | Gradient clip | 0.5 |
    """)

    st.markdown("---")
    st.markdown("### 📈 Training Curves")

    pt = data.get("ppo_training")
    if pt and "training_metrics" in pt:
        metrics = pt["training_metrics"]
        df_train = pd.DataFrame(metrics)
        df_train["episode"] = range(1, len(df_train) + 1)

        tab1, tab2, tab3 = st.tabs(["Reward & Waves", "Distance & Violations", "Losses"])

        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                chart = alt.Chart(df_train).mark_line(color="#1f77b4", opacity=0.6).encode(
                    x="episode:Q",
                    y=alt.Y("reward:Q", title="Total Reward")
                ).properties(height=350)
                # Add moving average
                window = max(1, len(df_train) // 10)
                df_train["reward_ma"] = df_train["reward"].rolling(window=window, min_periods=1).mean()
                ma = alt.Chart(df_train).mark_line(color="red", strokeWidth=2).encode(
                    x="episode:Q",
                    y="reward_ma:Q"
                )
                st.altair_chart(chart + ma, use_container_width=True)

            with col2:
                chart = alt.Chart(df_train).mark_line(color="#2ca02c").encode(
                    x="episode:Q",
                    y=alt.Y("n_waves:Q", title="Number of Waves")
                ).properties(height=350)
                st.altair_chart(chart, use_container_width=True)

        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                chart = alt.Chart(df_train).mark_line(color="#ff7f0e").encode(
                    x="episode:Q",
                    y=alt.Y("distance:Q", title="Total Picking Distance")
                ).properties(height=350)
                st.altair_chart(chart, use_container_width=True)
            with col2:
                chart = alt.Chart(df_train).mark_line(color="#d62728").encode(
                    x="episode:Q",
                    y=alt.Y("violations:Q", title="Temperature Violations")
                ).properties(height=350)
                st.altair_chart(chart, use_container_width=True)

        with tab3:
            actor_losses = pt.get("actor_losses", [])
            critic_losses = pt.get("critic_losses", [])
            if actor_losses and critic_losses:
                df_loss = pd.DataFrame({
                    "step": range(len(actor_losses)),
                    "Actor Loss": actor_losses,
                    "Critic Loss": critic_losses,
                })
                df_loss_melted = df_loss.melt(id_vars=["step"], var_name="Loss Type", value_name="Value")
                chart = alt.Chart(df_loss_melted).mark_line(opacity=0.7).encode(
                    x="step:Q",
                    y=alt.Y("Value:Q", scale=alt.Scale(type="symlog")),
                    color=alt.Color("Loss Type:N")
                ).properties(height=400)
                st.altair_chart(chart, use_container_width=True)

        # Training summary stats
        st.markdown("---")
        st.markdown("### 📋 Training Summary Statistics")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Episodes", len(df_train))
        c2.metric("Avg Reward", f"{df_train['reward'].mean():.1f}")
        c3.metric("Max Reward", f"{df_train['reward'].max():.1f}")
        c4.metric("Avg Waves", f"{df_train['n_waves'].mean():.1f}")
        c5.metric("Min Waves", f"{df_train['n_waves'].min():.1f}")

    else:
        st.info("PPO training data not available.")

    st.markdown("---")
    st.markdown("### 🧪 PPO Evaluation Results")
    pe = data.get("ppo_eval")
    if pe and "summary" in pe:
        s = pe["summary"]
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Avg Reward", f"{s.get('avg_reward', 0):.1f}")
        c2.metric("Avg Waves", f"{s.get('avg_waves', 0):.1f}")
        c3.metric("Avg Distance", f"{s.get('avg_distance', 0):.1f}")
        c4.metric("Avg Misses", f"{s.get('avg_misses', 0):.1f}")
        c5.metric("Avg Violations", f"{s.get('avg_violations', 0):.1f}")
    else:
        st.info("PPO evaluation data not available.")


# =============================================================================
# PAGE: METHOD COMPARISON
# =============================================================================
if page == "📊 Method Comparison":
    st.markdown('<div class="main-header">📊 Method Comparison</div>', unsafe_allow_html=True)
    st.markdown("Side-by-side comparison of all wave allocation methods")

    fr = data.get("final_results")
    if not fr:
        st.warning("Comparison data not available.")
        st.stop()

    st.markdown("---")

    # Build comparison dataframe
    rows = []
    h_sum = fr.get("heuristic_summary", {})
    for name, s in h_sum.items():
        rows.append({
            "Method": name,
            "Avg Reward": s["avg_reward"],
            "Reward": s["avg_reward"],
            "Std Reward": s["std_reward"],
            "Avg Distance": s["avg_distance"],
            "Avg Waves": s["avg_waves"],
            "Misses": s["avg_misses"],
            "Violations": s["avg_violations"],
            "Type": "Heuristic",
        })

    ppo = fr.get("ppo_summary", {})
    if ppo:
        rows.append({
            "Method": "PPO (DRL)",
            "Avg Reward": ppo.get("avg_reward", 0),
            "Reward": ppo.get("avg_reward", 0),
            "Std Reward": 0,
            "Avg Distance": ppo.get("avg_distance", 0),
            "Avg Waves": ppo.get("avg_waves", 0),
            "Misses": ppo.get("avg_misses", 0),
            "Violations": ppo.get("avg_violations", 0),
            "Type": "Deep RL",
        })

    df_comp = pd.DataFrame(rows)

    st.markdown("### 📋 Comparison Table")
    st.dataframe(df_comp.sort_values("Reward", ascending=False), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### 📈 Visual Comparisons")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Reward Ranking", "Distance", "Waves", "Violations", "Scatter"])

    with tab1:
        df_sorted = df_comp.sort_values("Reward", ascending=False)
        colors = ["#2ca02c" if m == "PPO (DRL)" else "#1f77b4" for m in df_sorted["Method"]]
        chart = alt.Chart(df_sorted).mark_bar().encode(
            x=alt.X("Reward:Q", title="Reward (Higher = Better)"),
            y=alt.Y("Method:N", sort="-x", title=""),
            color=alt.Color("Type:N", scale=alt.Scale(domain=["Heuristic", "Deep RL"],
                                                       range=["#1f77b4", "#2ca02c"]))
        ).properties(height=350, title="Performance Ranking")
        st.altair_chart(chart, use_container_width=True)
        st.markdown("<div class='success-box'><strong>Insight:</strong> PPO achieves the highest reward, outperforming all heuristics.</div>", unsafe_allow_html=True)

    with tab2:
        chart = alt.Chart(df_comp).mark_bar().encode(
            x=alt.X("Method:N", sort="-y"),
            y=alt.Y("Avg Distance:Q", title="Picking Distance (m)"),
            color=alt.Color("Type:N")
        ).properties(height=400)
        st.altair_chart(chart, use_container_width=True)

    with tab3:
        chart = alt.Chart(df_comp).mark_bar().encode(
            x=alt.X("Method:N"),
            y=alt.Y("Avg Waves:Q", title="Number of Waves"),
            color=alt.Color("Type:N")
        ).properties(height=400)
        st.altair_chart(chart, use_container_width=True)

    with tab4:
        chart = alt.Chart(df_comp).mark_bar().encode(
            x=alt.X("Method:N"),
            y=alt.Y("Violations:Q", title="Temperature Violations"),
            color=alt.Color("Type:N")
        ).properties(height=400)
        st.altair_chart(chart, use_container_width=True)

    with tab5:
        scatter_chart = alt.Chart(df_comp).mark_circle(size=100).encode(
            x=alt.X("Avg Distance:Q", title="Picking Distance (m)"),
            y=alt.Y("Violations:Q", title="Temperature Violations"),
            color=alt.Color("Method:N", legend=alt.Legend(title="Method")),
            tooltip=["Method", "Avg Distance", "Violations"]
        ).properties(height=400, title="Temperature Violations vs Picking Distance")
        st.altair_chart(scatter_chart, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🏆 Performance Ranking")

    ranking = df_comp.nlargest(len(df_comp), "Reward")["Method"].tolist()
    for i, method in enumerate(ranking, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        row = df_comp[df_comp["Method"] == method].iloc[0]
        st.markdown(f"""
        <div style="padding: 0.8rem; background: {'#e8f5e9' if i==1 else '#f8f9fa'};
                    border-radius: 8px; margin-bottom: 0.5rem;
                    border-left: 4px solid {'#4caf50' if i==1 else '#999'};">
            <strong>{medal} {method}</strong> — Reward: {row['Reward']:.1f},
            Distance: {row['Avg Distance']:.1f}m, Waves: {row['Avg Waves']:.1f}
        </div>
        """, unsafe_allow_html=True)


# =============================================================================
# PAGE: KGDRL FRAMEWORK
# =============================================================================
if page == "🧠 KGDRL Framework":
    st.markdown('<div class="main-header">🧠 KGDRL Framework</div>', unsafe_allow_html=True)
    st.markdown("Knowledge-Guided Deep Reinforcement Learning for Smart Wave Allocation")

    st.markdown("---")
    st.markdown("### 📐 MDP Formulation")

    st.markdown(r"""
    The smart wave allocation problem is formulated as a **finite-horizon Markov Decision Process**:

    $$M = (S, A, P, R, \gamma)$$
    """)

    st.markdown("#### State Space $S$")
    st.markdown(r"""
    The state at time step $t$ is defined as:

    $$s_t = \left( s_t^{wave},\ s_t^{pool},\ s_t^{time},\ s_t^{history} \right)$$

    | Component | Dimension | Description |
    |-----------|-----------|-------------|
    | Wave features | 4 | Orders count, volume, age, zone spread |
    | Wave zone mask | 8 | One-hot covered zones |
    | Wave temp mask | 4 | One-hot covered temperatures |
    | Top-K order features | K x 6 | SKU count, deadline, temp, x, y, urgency |
    | Global stats | 3 | Urgent ratio, pending ratio, pool size |
    | **Total** | **~79** | (Z=8, K=10) |
    """)

    st.markdown("#### Action Space $A$")
    st.markdown(r"""
    The action at time step $t$ takes one of two forms:

    $$a_t = o^* \quad \text{where } o^* \in \text{Pool} \text{ (add order } o^* \text{ to current wave)}$$

    $$a_t = \text{CLOSE} \quad \text{(close wave, dispatch, start new wave)}$$
    """)

    st.markdown("#### Reward Function $R$")
    st.markdown(r"""
    The total reward is decomposed into four components:

    $$r(s_t, a_t, s_{t+1}) = r_{eff} + r_{comp} + r_{time} + r_{setup}$$

    **Efficiency:** $r_{eff} = -\alpha_1 \cdot \Delta L$ (negative picking distance)

    **Compliance:** $r_{comp} = -\alpha_2 \cdot I_{temp}$ where $I_{temp} = 1$ if temp mixed, else $0$

    **Timeliness:** $r_{time} = -\alpha_4 \cdot \sum \max(0, t_{finish} - d_o)$ (deadline penalty)

    **Setup:** $r_{setup} = -\alpha_5 \cdot I_{close}$ where $I_{close} = 1$ if $a_t = \text{CLOSE}$, else $0$
    """)

    st.markdown("---")
    st.markdown("### 🔧 PPO Update Procedure")
    st.markdown("""
    ```
    For each episode:
        1. Collect trajectory: (s_t, a_t, r_t, s_{t+1}, log_prob, valid_mask)
        2. Compute advantages using GAE:
           delta_t = r_t + gamma * V(s_{t+1}) - V(s_t)
           A_t = delta_t + gamma * lambda * A_{t+1}
        3. PPO update (K epochs):
           ratio = pi_new(a|s) / pi_old(a|s)
           L_CLIP = -min(ratio * A, clip(ratio, 1-eps, 1+eps) * A)
        4. Update critic: MSE(V(s), R)
        5. Clip gradients (norm <= 0.5)
    ```
    """)

    st.markdown("---")
    st.markdown("### 🧮 TZU Heuristic Score")
    st.markdown(r"""
    The **Temperature-Zone-Urgency** heuristic serves as both a standalone baseline and a knowledge prior:

    $$TZU(o, w) = \beta_1 \cdot I_{temp}(o, w) + \beta_2 \cdot \frac{1}{1 + d(o, w)} + \beta_3 \cdot \frac{1}{\bar{d}_o}$$

    where $I_{temp}(o, w) = 1$ if $\tau(o) = \tau(w)$, else $0$

    | Symbol | Meaning |
    |--------|---------|
    | $I_{temp}$ | Indicator: 1 if order and wave have same temperature |
    | $\tau(o)$ | Temperature category of order $o$ |
    | $d(o, w)$ | Distance between order $o$ and wave centroid $w$ |
    | $\bar{d}_o$ | Normalized deadline urgency of order $o$ |
    | $\beta_1, \beta_2, \beta_3$ | Weights: 0.4, 0.4, 0.2 |
    """)

    st.markdown("---")
    st.markdown("### 🔮 Extension to Full KGDRL")
    st.markdown(r"""
    The current PPO implementation is "vanilla" without knowledge guidance. Full KGDRL extension involves:

    1. **Knowledge Graph Construction**
       - Nodes: Orders, Zones, Temperature categories
       - Edges: Zone adjacency, temperature compatibility, order similarity

    2. **Graph Neural Network Encoder**
       - Replace MLP state encoder with Graph Attention Network (GAT)

    3. **Heuristic Policy Prior**
       - Initialize actor output with TZU scores
       - Add KL regularization: $L_{KG} = KL(\pi_\theta \| \pi_{TZU})$

    4. **Structured Action Sampling**
       - Hierarchical: temperature → zone → specific order
    """)


# =============================================================================
# PAGE: SYSTEM ARCHITECTURE
# =============================================================================
if page == "🏗️ System Architecture":
    st.markdown('<div class="main-header">🏗️ System Architecture</div>', unsafe_allow_html=True)
    st.markdown("Enterprise-grade dashboard design and feasibility analysis")

    st.markdown("---")
    st.markdown("### 🏛️ Recommended System Architecture")

    st.markdown("""
    ```
    ┌─────────────────────────────────────────────────────────────┐
    │                    Frontend (Vue.js/React)                   │
    │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
    │  │ Real-Time│ │  Wave    │ │  Alert   │ │ Decision │       │
    │  │ Dashboard│ │ Management│ │  Center  │ │ Analysis │       │
    │  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
    └────────────────────────┬────────────────────────────────────┘
                             │ WebSocket / REST API
    ┌────────────────────────┴────────────────────────────────────┐
    │                    Backend (FastAPI/Flask)                   │
    │  ┌─────────────────────────────────────────────────────┐   │
    │  │  API Layer                                           │   │
    │  │  - /api/simulate/step      (single-step simulation) │   │
    │  │  - /api/simulate/batch     (batch wave allocation)  │   │
    │  │  - /api/status/realtime    (real-time status)       │   │
    │  │  - /api/alerts/active      (active alerts)          │   │
    │  └─────────────────────────────────────────────────────┘   │
    │  ┌─────────────────────────────────────────────────────┐   │
    │  │  DRL Engine (PPO Agent)                              │   │
    │  │  - Load pre-trained model                            │   │
    │  │  - Receive order stream, output wave decisions       │   │
    │  └─────────────────────────────────────────────────────┘   │
    │  ┌─────────────────────────────────────────────────────┐   │
    │  │  PharmaWaveEnv (Simulation Environment)              │   │
    │  │  - Maintain order pool, wave state, timeline         │   │
    │  └─────────────────────────────────────────────────────┘   │
    └─────────────────────────────────────────────────────────────┘
    ```
    """)

    st.markdown("---")
    st.markdown("### 📡 Real-Time Data Interface")
    st.markdown("""
    Every simulation step produces the following real-time data:
    ```python
    {
        "current_time": env.current_time,              # Current simulation time
        "active_wave_orders": len(env.active_wave_orders),  # Orders in active wave
        "active_wave_zones": list(env.active_wave_zones),   # Covered zones
        "active_wave_temps": list(env.active_wave_temps),   # Temperature categories
        "order_pool_size": len(env.order_pool),        # Pending allocation pool
        "pending_orders": len(env.pending_orders),     # Not yet arrived
        "waves_completed": len(env.waves),             # Completed waves
        "total_distance": env.total_picking_distance,  # Cumulative distance
        "deadline_misses": env.deadline_misses,        # Late deliveries
        "temp_violations": env.temp_violations,        # GSP violations
    }
    ```
    """)

    st.markdown("---")
    st.markdown("### ✅ Feasibility Assessment")

    feasibility = [
        ("Data Flow", "PharmaWaveEnv outputs state_dict + info at every step", "Real-time sorting progress", "✅ Directly available"),
        ("Wave Info", "env.waves records orders, distance, temp, zones, finish time", "Wave allocation status", "✅ Directly available"),
        ("Order Info", "order_pool / pending_orders tracks in real-time", "Order queue, arrival stream", "✅ Directly available"),
        ("Timeline", "env.current_time + env.step_count", "Sorting timeline", "✅ Directly available"),
        ("Compliance", "temp_violations, deadline_misses counters", "Exception alerts", "✅ Directly available"),
        ("Labor Load", "Derivable from wave_count × setup_time / picking_time", "Picker load heatmap", "✅ Computable"),
    ]

    df_feas = pd.DataFrame(feasibility, columns=["Dimension", "Existing Capability", "Visualization Need", "Match"])
    st.dataframe(df_feas, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### 🎓 Course Project Simplification")
    st.markdown("""
    <div class="success-box">
        <strong>Recommended for Digital Innovation course:</strong> Pure frontend HTML/JS Dashboard
        (zero backend dependency)
        <ul>
            <li>Pre-run Python pipeline to generate <code>data/*.json</code> result files</li>
            <li>Dashboard reads JSON via native JavaScript, visualizes with Chart.js / ECharts</li>
            <li>JavaScript timers simulate "real-time" data flow from pre-computed step_log</li>
        </ul>
        <strong>Advantages:</strong> No server deployment needed; double-click HTML to run;
        perfect for classroom demos and oral defense.
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# PAGE: AI TOOLS REVIEW
# =============================================================================
if page == "🛠️ AI Tools Review":
    st.markdown('<div class="main-header">🛠️ AI Tools Usage Review</div>', unsafe_allow_html=True)
    st.markdown("Retrospective on how AI tools powered this project")

    st.markdown("---")
    st.markdown("### 🤝 Human-AI Collaboration Model")

    st.markdown("""
    <div class="highlight-box">
        <strong>"Human-led direction, AI-led implementation"</strong>
        <ul>
            <li><strong>Human responsible for:</strong> Problem definition, architectural decisions,
                business constraint translation, result validation</li>
            <li><strong>AI responsible for:</strong> Code implementation, document drafting,
                detail optimization, multilingual translation, bug troubleshooting</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📋 Collaboration Workflow")
    st.markdown("""
    ```
    Human proposes high-level requirements
              ↓
    AI generates draft / initial code
              ↓
    Human reviews and identifies issues
              ↓
    AI fixes and optimizes
              ↓
    Human validates results
              ↓
    AI synchronizes across versions (CN/EN/release)
    ```
    """)

    st.markdown("---")
    st.markdown("### 🛠️ AI-Assisted vs Human Decision Content")

    collab_data = [
        ("Problem Modeling", "Literature review framework, MDP formalization templates", "Enterprise pain point extraction, constraint definition"),
        ("Algorithm Design", "PPO network architecture code, reward function templates", "Hyperparameter tuning strategy, heuristic design"),
        ("Data Generation", "Empirical distribution generator code", "Distribution parameter calibration, business logic validation"),
        ("Model Training", "Training loop, evaluation scripts", "Training monitoring, convergence judgment"),
        ("Visualization", "Complete Dashboard HTML/CSS/JS code", "Interaction logic design, visual style decisions"),
        ("Documentation", "Technical document structure, math formula formatting", "Content review, academic accuracy verification"),
    ]

    df_collab = pd.DataFrame(collab_data, columns=["Phase", "AI-Assisted Content", "Human Decision Content"])
    st.dataframe(df_collab, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### 📊 AI Tool Usage Statistics")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: #f0f7ff; border-radius: 12px;">
            <div style="font-size: 2.5rem;">📝</div>
            <div style="font-size: 1.5rem; font-weight: 700;">6</div>
            <div style="color: #444;">Major Documents</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: #fff8e1; border-radius: 12px;">
            <div style="font-size: 2.5rem;">💻</div>
            <div style="font-size: 1.5rem; font-weight: 700;">4</div>
            <div style="color: #444;">Dashboard Versions</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: #e8f5e9; border-radius: 12px;">
            <div style="font-size: 2.5rem;">🌐</div>
            <div style="font-size: 1.5rem; font-weight: 700;">2</div>
            <div style="color: #444;">Languages (CN/EN)</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🎯 Key AI Contributions")
    contributions = [
        "Formulated the complete MDP mathematical model with pharmaceutical-specific state features and reward design",
        "Implemented the full PPO algorithm with action masking, GAE advantage estimation, and gradient clipping",
        "Built 4 interactive HTML dashboard versions with real-time simulation, comparison charts, and alert systems",
        "Generated all synthetic data from empirical distributions calibrated to enterprise casebook metrics",
        "Created comprehensive technical documentation in both Chinese and English",
        "Performed cost-semantic unification across all dashboards (Reward → Cost conversion)",
    ]
    for i, item in enumerate(contributions, 1):
        st.markdown(f"{i}. {item}")

    st.markdown("---")
    st.markdown("### ⚠️ Limitations & Human Oversight")
    st.markdown("""
    | Aspect | AI Limitation | Human Mitigation |
    |--------|--------------|------------------|
    | Business logic | May miss industry-specific constraints | Manual review of all GSP rules |
    | Hyperparameters | Suggests generic values | Tuned based on simulation feedback |
    | Code correctness | Occasional syntax/logic errors | Systematic testing and debugging |
    | Visual design | Functional but not artistic | Style decisions and branding alignment |
    | Academic rigor | Structure provided | Content accuracy verified against course requirements |
    """)


# =============================================================================
# PAGE: PROJECT DOCS
# =============================================================================
if page == "📋 Project Docs":
    st.markdown('<div class="main-header">📋 Project Documentation</div>', unsafe_allow_html=True)
    st.markdown("Technical documents, tutorials, and reference materials")

    st.markdown("---")
    st.markdown("### 📁 File Inventory")

    docs = [
        ("smart_wave_allocation_model.md", "Complete MDP formulation, PPO algorithm, data generation, experiment design"),
        ("tutorial_en.md", "Daily progress report: Cost semantic unification, labor load fluctuation, alert diversity"),
        ("web_dashboard_feasibility.md", "Feasibility analysis for enterprise-grade web terminal architecture"),
        ("AI_Tools_Usage_Review_EN.md", "Retrospective on AI tool usage across all project phases"),
        ("pharma_wave_allocation.py", "Main implementation: DataGenerator, PharmaWaveEnv, PPOAgent, heuristics"),
        ("run_full_pipeline.py", "End-to-end pipeline: training, evaluation, data export"),
        ("smart_wave_dashboard_en.html", "Interactive English dashboard with real-time simulation"),
        ("dashboard_en.html", "General warehouse dashboard (English)"),
    ]

    df_docs = pd.DataFrame(docs, columns=["File", "Description"])
    st.dataframe(df_docs, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### 📊 Data Files")

    data_files = [
        ("data/final_results.json", "Aggregated heuristic + PPO summary statistics"),
        ("data/order_stats.json", "Order arrival timeline and temperature distribution"),
        ("data/heuristic_results.json", "Raw heuristic evaluation results (20 instances each)"),
        ("data/ppo_training.json", "PPO training metrics, actor/critic losses per episode"),
        ("data/ppo_eval.json", "PPO evaluation results with step-by-step logs"),
        ("data/comparison_plots.png", "Static comparison visualization"),
    ]

    df_data = pd.DataFrame(data_files, columns=["File", "Content"])
    st.dataframe(df_data, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### 📚 Reference Materials")

    st.markdown("""
    | Document | Description |
    |----------|-------------|
    | Enterprise_AI_Development_Casebook.pdf | Original course casebook with enterprise data |
    | KGDRL技术交底书.pdf | KGDRL technical disclosure (Chinese) |
    | KGDRL相关内容.pdf | KGDRL research paper and methodology |
    | casebook_text.txt | Extracted text from casebook |
    """)

    st.markdown("---")
    st.markdown("### 🎓 Course Context")
    st.markdown("""
    <div class="highlight-box">
        <strong>Digital Innovation | SDC MSc Innovation Management</strong><br><br>
        This project was completed as part of the Digital Innovation course at the
        Sino-Danish Center (SDC) MSc Innovation Management program.<br><br>

        <strong>Case:</strong> Smart Warehouse Sorting & Dispatch System<br>
        <strong>Enterprise:</strong> Large Pharmaceutical Logistics Enterprise (China)<br>
        <strong>Technology:</strong> Deep Reinforcement Learning (PPO)<br>
        <strong>Paradigm:</strong> Knowledge-Guided Deep Reinforcement Learning (KGDRL)<br>
        <strong>AI Assistant:</strong> Claude Code (Anthropic)<br>
        <strong>Duration:</strong> 4 weeks<br>
        <strong>Team Size:</strong> 5 students (1-2 technical)
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🔗 How to Run This Dashboard")
    st.code("""
# Activate virtual environment
source .venv/bin/activate  # or .venv\\Scripts\\activate on Windows

# Install dependencies (if needed)
pip install streamlit pandas numpy altair

# Run the app
streamlit run streamlit_app.py
    """, language="bash")


# =============================================================================
# REAL-TIME SIMULATION FUNCTIONS (ported from smart_wave_dashboard.html)
# =============================================================================
def generate_demo_episode():
    """Generate a realistic sample episode for real-time simulation demo."""
    steps = []
    waves = []
    current_wave_orders = 0
    current_wave_volume = 0
    total_dist = 0
    total_cost = 0
    current_wave_zones = set()
    current_wave_temps = set()
    wave_count = 0
    sim_time = 0

    temps_weighted = [0, 0, 0, 0, 0, 1, 1, 1, 2, 2, 3]
    zones = [0, 1, 2, 3, 4, 5, 6, 7]
    order_volumes = [15, 20, 25, 30, 35, 40, 45, 50]

    np.random.seed(42)
    for step_idx in range(400):
        sim_time += 1

        force_small_wave = np.random.random() < 0.05 and current_wave_orders > 0 and current_wave_orders < 5
        force_full_wave = np.random.random() < 0.08 and current_wave_orders >= 10
        should_close = (not force_full_wave and
                       (current_wave_orders >= 15 or
                        current_wave_volume >= 280 or
                        (current_wave_orders >= 8 and np.random.random() < 0.15) or
                        force_small_wave))
        no_room = current_wave_orders >= 19 or current_wave_volume >= 300

        if no_room or (should_close and current_wave_orders > 0):
            wave_dist = 20 + current_wave_orders * 8 + np.random.random() * 30
            total_dist += wave_dist

            temp_violation_cost = 0
            if len(current_wave_temps) > 1:
                temps_arr = list(current_wave_temps)
                has_ambient = 0 in temps_arr
                has_cool = 1 in temps_arr
                has_cold = 2 in temps_arr
                has_frozen = 3 in temps_arr
                if (has_ambient or has_cool) and (has_cold or has_frozen):
                    temp_violation_cost = 80 + np.random.random() * 40
                elif len(temps_arr) >= 3:
                    temp_violation_cost = 40 + np.random.random() * 20
                else:
                    temp_violation_cost = 15 + np.random.random() * 10

            # Cost semantics: positive values only
            step_cost = wave_dist * 0.25 + temp_violation_cost
            action = 10
            action_type = 'close'

            waves.append({
                'orders': current_wave_orders,
                'distance': wave_dist,
                'temps': list(current_wave_temps),
                'zones': list(current_wave_zones),
                'time': sim_time,
                'cost': step_cost
            })

            current_wave_orders = 0
            current_wave_volume = 0
            current_wave_zones = set()
            current_wave_temps = set()
            wave_count += 1
        else:
            vol = order_volumes[np.random.randint(len(order_volumes))]
            temp = temps_weighted[np.random.randint(len(temps_weighted))]
            zone = zones[np.random.randint(len(zones))]

            current_wave_orders += 1
            current_wave_volume += vol
            current_wave_zones.add(zone)
            current_wave_temps.add(temp)

            # Small processing cost for each order added
            step_cost = 0.5
            action = np.random.randint(7)
            action_type = 'add'

        total_cost += step_cost

        steps.append({
            'time': sim_time,
            'action': action,
            'action_type': action_type,
            'cost': step_cost,
            'wave_orders': current_wave_orders,
            'wave_volume': current_wave_volume,
            'total_dist': total_dist,
            'total_cost': total_cost,
            'wave_count': wave_count,
            'zones': list(current_wave_zones),
            'temps': list(current_wave_temps)
        })

    if current_wave_orders > 0:
        wave_dist = 20 + current_wave_orders * 8 + np.random.random() * 30
        total_dist += wave_dist
        # Calculate cost for final wave
        temp_violation_cost = 0
        if len(current_wave_temps) > 1:
            temps_arr = list(current_wave_temps)
            has_ambient = 0 in temps_arr
            has_cool = 1 in temps_arr
            has_cold = 2 in temps_arr
            has_frozen = 3 in temps_arr
            if (has_ambient or has_cool) and (has_cold or has_frozen):
                temp_violation_cost = 80 + np.random.random() * 40
            elif len(temps_arr) >= 3:
                temp_violation_cost = 40 + np.random.random() * 20
            else:
                temp_violation_cost = 15 + np.random.random() * 10
        final_cost = wave_dist * 0.25 + temp_violation_cost
        waves.append({
            'orders': current_wave_orders,
            'distance': wave_dist,
            'temps': list(current_wave_temps),
            'zones': list(current_wave_zones),
            'time': sim_time,
            'cost': final_cost
        })

    return {'steps': steps, 'waves': waves}


TEMP_COLORS = {0: '#4ade80', 1: '#60a5fa', 2: '#818cf8', 3: '#c084fc'}
TEMP_NAMES = {0: 'Ambient', 1: 'Cool', 2: 'Cold', 3: 'Frozen'}


def render_zone_map(zones_list, wave_orders):
    """Render a 2x4 warehouse zone grid."""
    zone_counts = {}
    for z in zones_list:
        zone_counts[z] = zone_counts.get(z, 0) + 1

    cols = st.columns(4)
    for i in range(8):
        with cols[i % 4]:
            count = zone_counts.get(i, 0)
            if count > 0:
                bg_color = f'rgba(0, 212, 255, {0.15 + count * 0.1})'
                border_color = 'rgba(0, 212, 255, 0.4)'
                text_color = '#fff'
            else:
                bg_color = 'rgba(255,255,255,0.05)'
                border_color = 'rgba(148, 163, 184, 0.15)'
                text_color = '#64748b'

            st.markdown(f"""
            <div style="
                aspect-ratio: 1;
                border-radius: 10px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                font-size: 11px;
                font-weight: 700;
                border: 1px solid {border_color};
                background: {bg_color};
                color: {text_color};
                transition: all 0.3s ease;
            ">
                <span style="font-size: 9px; opacity: 0.6; margin-bottom: 2px;">Z{i}</span>
                <span style="font-size: 16px;">{count}</span>
            </div>
            """, unsafe_allow_html=True)


# =============================================================================
# PAGE: REAL-TIME SIMULATION
# =============================================================================
if page == "⚡ Real-time Simulation":
    st.markdown('<div class="main-header">⚡ Real-time Simulation</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Live warehouse sorting & dispatch visualization</div>', unsafe_allow_html=True)

    st.info("The real-time simulation runs in the original HTML dashboard below. Use the controls inside the panel to start/pause/reset the simulation.")

    # Embed the original HTML dashboard via iframe (English version)
    html_path = Path(__file__).parent / "smart_wave_dashboard_en.html"
    if html_path.exists():
        # Read and embed the HTML file directly
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        components.html(html_content, height=900, scrolling=True)
    else:
        st.error("smart_wave_dashboard_en.html not found. Please ensure the file is in the same directory as streamlit_app.py")
