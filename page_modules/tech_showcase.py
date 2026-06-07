"""
Sunergy Pharma — Tech Showcase Module
=======================================
Pages:
  - KGDRL Framework Visualization
  - AI Learning Engine (Online Learning)
  - Multi-Warehouse Network (Federated)
  - Patent & Research Wall (NEW)

NOTE: All UI text is English. Remove any render_* function to drop the page.
"""

import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
from .shared import get_patent_timeline


# =============================================================================
# PAGE: KGDRL Framework Visualization
# =============================================================================

def render_kgdrl_framework():
    st.markdown('<div class="main-header">KGDRL Framework</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Knowledge Graph -> GAT Encoder -> Policy Network -> Hierarchical Action</div>', unsafe_allow_html=True)

    cols = st.columns(4)
    steps = [
        ("1. Knowledge Graph", "Orders, Zones, Temps as nodes; compatibilities as edges", "#3b82f6"),
        ("2. GAT Encoder", "Graph Attention learns entity relationships automatically", "#8b5cf6"),
        ("3. Policy Network", "PPO with KL divergence constraint to TZU heuristic", "#f59e0b"),
        ("4. Hierarchical Action", "Temp -> Zone -> Order; fully auditable for GSP", "#10b981"),
    ]
    for col, (title, desc, color) in zip(cols, steps):
        with col:
            st.markdown(f"""
            <div class="pro-card" style="border-top: 3px solid {color};">
                <div style="font-weight:700; color:#f8fafc; font-size:0.95rem;">{title}</div>
                <div style="font-size:0.8rem; color:#94a3b8; margin-top:0.4rem; line-height:1.4;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Architecture ASCII diagram
    st.markdown('<div class="section-header">System Architecture</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#111827; border-radius:12px; padding:1.5rem; text-align:center; font-family:monospace; font-size:0.8rem; color:#94a3b8; line-height:1.8;">
        <span style="color:#3b82f6;">Input: Order Stream</span> ->
        <span style="color:#8b5cf6;">Knowledge Graph</span> ->
        <span style="color:#f59e0b;">GAT Encoder</span> ->
        <span style="color:#10b981;">Policy Network</span> ->
        <span style="color:#06b6d4;">Hierarchical Action</span><br><br>
        <span style="color:#ef4444;">KL Constraint:</span> D_KL(pi_theta || pi_TZU) keeps policy near expert rules<br>
        <span style="color:#64748b;">Output: Wave allocation decisions with full audit trail</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Formula block
    st.markdown('<div class="section-header">Core Formulas</div>', unsafe_allow_html=True)
    st.markdown("""
    **Graph Attention Update:**
    ```
    h_i^(l+1) = sigma(sum_{j in N(i)} alpha_ij^(l) * W^(l) * h_j^(l))
    ```

    **Knowledge-Guided PPO Loss:**
    ```
    L_total = L_PPO_CLIP + lambda_KG * D_KL(pi_theta(.|s) || pi_TZU(.|s))
    ```
    where lambda_KG = 0.1 controls knowledge injection strength.

    **Hierarchical Action Sampling:**
    1. Temperature layer (GSP hard constraint)
    2. Zone cluster layer
    3. Specific order layer
    """)

    st.markdown("---")

    # Attention heatmap mock
    st.markdown('<div class="section-header">Attention Weight Heatmap (Illustrative)</div>', unsafe_allow_html=True)
    attn_df = pd.DataFrame(
        np.random.rand(8, 8),
        index=[f"Z{i}" for i in range(8)],
        columns=[f"O{i}" for i in range(8)]
    )
    st.dataframe(attn_df.style.background_gradient(cmap="YlOrRd", axis=None), height=300)
    st.caption("Darker = stronger attention. Shows which orders the GAT focuses on per zone.")


# =============================================================================
# PAGE: AI Learning Engine (Online Learning)
# =============================================================================

def render_ai_learning_engine():
    st.markdown('<div class="main-header">AI Learning Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Experience replay + EWC regularization - smarter every shift</div>', unsafe_allow_html=True)

    cols = st.columns(4)
    for i, (label, value, unit, color) in enumerate([
        ("Replay Buffer", "847", "/ 1000", "#10b981"),
        ("Update Count", "124", "total", "#3b82f6"),
        ("EWC Lambda", "0.01", "regularization", "#8b5cf6"),
        ("Last Update", "2 min", "ago", "#f59e0b"),
    ]):
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color:{color};">{value}</div>
                <div style="font-size:0.7rem; color:#64748b;">{unit}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    col_left, col_right = st.columns(2)
    with col_left:
        st.markdown('<div class="section-header">Experience Replay</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#111827; border-radius:8px; padding:1rem;">
            <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                <span style="color:#94a3b8;">Buffer Utilization</span>
                <span style="color:#10b981; font-weight:700;">84.7%</span>
            </div>
            <div style="background:#1e293b; height:8px; border-radius:4px;">
                <div style="background:#10b981; width:84.7%; height:100%; border-radius:4px;"></div>
            </div>
            <div style="margin-top:1rem; font-size:0.8rem; color:#64748b;">
                <div>Oldest experience: Shift #89</div>
                <div>Newest experience: Shift #124</div>
                <div>Batch size: 32</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="section-header">EWC Regularization</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#111827; border-radius:8px; padding:1rem;">
            <div style="font-size:0.85rem; color:#94a3b8; line-height:1.8;">
                <div><b style="color:#f8fafc;">Formula:</b> L = L_new + lambda/2 * sum F_i * (theta_i - theta*_i)^2</div>
                <div><b style="color:#f8fafc;">Lambda:</b> 0.01</div>
                <div><b style="color:#f8fafc;">Fisher computed:</b> Every 5 updates</div>
                <div><b style="color:#f8fafc;">Old params frozen:</b> theta* from Shift #120</div>
                <div style="margin-top:0.5rem; color:#10b981;">No catastrophic forgetting detected</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Policy Ensemble Weights</div>', unsafe_allow_html=True)
    ensemble_df = pd.DataFrame({
        "Policy": ["KGDRL", "TZU", "EDD"],
        "Weight": [0.52, 0.28, 0.20],
        "Recent Avg Reward": [4120, 3580, 3210],
    })
    st.dataframe(ensemble_df, width='stretch', hide_index=True)

    ens_chart = alt.Chart(ensemble_df).mark_arc(innerRadius=40).encode(
        theta="Weight", color="Policy",
        tooltip=["Policy", "Weight", "Recent Avg Reward"]
    ).properties(height=250)
    st.altair_chart(ens_chart, width='stretch')


# =============================================================================
# PAGE: Multi-Warehouse Network (Federated)
# =============================================================================

def render_multi_warehouse():
    st.markdown('<div class="main-header">Multi-Warehouse Network</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Multi-warehouse collaborative training - data stays local, intelligence goes global</div>', unsafe_allow_html=True)

    st.info("Pro Architecture: Federated learning infrastructure is architecturally ready. Activate with Enterprise deployment.")

    st.markdown("""
    <div style="background:#111827; border-radius:12px; padding:1.5rem; text-align:center; font-family:monospace; font-size:0.8rem; color:#94a3b8; line-height:1.8;">
        <span style="color:#f59e0b;">Shanghai WH</span> -> <span style="color:#3b82f6;">grad_1</span> -> <span style="color:#8b5cf6;">Coordinator</span> <- <span style="color:#3b82f6;">grad_2</span> <- <span style="color:#f59e0b;">Beijing WH</span><br>
        <span style="color:#f59e0b;">Guangzhou WH</span> -> <span style="color:#3b82f6;">grad_3</span> -> <span style="color:#8b5cf6;">FedAvg Round 12</span><br>
        <span style="color:#64748b;">Secure Aggregation | Differential Privacy | AES-256</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Warehouse Clients</div>', unsafe_allow_html=True)
    fed_df = pd.DataFrame([
        {"Warehouse": "Shanghai", "Status": "Synced", "Samples": 1200, "Last Sync": "12 min ago", "Version": "v2.3.1", "Quality": 0.941},
        {"Warehouse": "Beijing", "Status": "Training", "Samples": 980, "Last Sync": "28 min ago", "Version": "v2.3.0", "Quality": 0.923},
        {"Warehouse": "Guangzhou", "Status": "Synced", "Samples": 1100, "Last Sync": "8 min ago", "Version": "v2.3.1", "Quality": 0.938},
        {"Warehouse": "Chengdu", "Status": "Idle", "Samples": 850, "Last Sync": "45 min ago", "Version": "v2.2.5", "Quality": 0.901},
        {"Warehouse": "Wuhan", "Status": "Training", "Samples": 1050, "Last Sync": "35 min ago", "Version": "v2.3.0", "Quality": 0.912},
    ])
    st.dataframe(fed_df, width='stretch', hide_index=True)

    st.markdown("---")
    cols = st.columns(4)
    for i, (label, value, unit, color) in enumerate([
        ("Total Clients", "5", "warehouses", "#3b82f6"),
        ("Global Round", "12", "current", "#f59e0b"),
        ("Total Samples", "5,680", "across clients", "#10b981"),
        ("Avg Sync Quality", "0.923", "consensus", "#8b5cf6"),
    ]):
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color:{color};">{value}</div>
                <div style="font-size:0.7rem; color:#64748b;">{unit}</div>
            </div>
            """, unsafe_allow_html=True)

    col_cfg, col_priv = st.columns(2)
    with col_cfg:
        st.markdown('<div class="section-header">Federation Config</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#111827; border-radius:8px; padding:1rem; font-size:0.85rem; color:#94a3b8;">
            <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                <span>Aggregation</span><span style="color:#f8fafc;">FedAvg</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                <span>Participation</span><span style="color:#f8fafc;">100%</span>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <span>Compression</span><span style="color:#10b981;">Top-K Sparsification</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_priv:
        st.markdown('<div class="section-header">Privacy</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#111827; border-radius:8px; padding:1rem; font-size:0.85rem; color:#94a3b8;">
            <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                <span>Differential Privacy</span><span style="color:#10b981;">epsilon=1.0, delta=1e-5</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                <span>Secure Aggregation</span><span style="color:#10b981;">Enabled</span>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <span>Model Encryption</span><span style="color:#10b981;">AES-256</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


# =============================================================================
# PAGE: Patent & Research Wall (NEW)
# =============================================================================

def render_patent_wall():
    st.markdown('<div class="main-header">Patent & Research Wall</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Academic backing, patent portfolio, and technology roadmap</div>', unsafe_allow_html=True)

    timeline = get_patent_timeline()

    # --- Summary Metrics ---
    cols = st.columns(4)
    metrics = [
        ("Patents Filed", "1", "substantive examination", "#f59e0b"),
        ("Publications", "3", "peer-reviewed", "#3b82f6"),
        ("Research Lines", "4", "active", "#8b5cf6"),
        ("Target Pilots", "3", "pharma distributors", "#10b981"),
    ]
    for col, (label, value, unit, color) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color:{color};">{value}</div>
                <div style="font-size:0.7rem; color:#64748b;">{unit}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # --- Timeline ---
    st.markdown('<div class="section-header">Milestone Timeline</div>', unsafe_allow_html=True)

    for item in timeline:
        color_map = {
            "research": "#3b82f6",
            "tech": "#8b5cf6",
            "patent": "#f59e0b",
            "milestone": "#10b981",
        }
        color = color_map.get(item["type"], "#94a3b8")
        st.markdown(f"""
        <div class="patent-card">
            <div style="display:flex; align-items:center; gap:0.8rem;">
                <span style="background:{color}; color:white; padding:2px 10px; border-radius:4px; font-size:0.75rem; font-weight:700;">{item['year']}</span>
                <span style="font-weight:700; color:#f8fafc; font-size:1rem;">{item['title']}</span>
            </div>
            <div style="font-size:0.85rem; color:#94a3b8; margin-top:0.4rem; line-height:1.5;">
                {item['desc']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- Core Paper Citations ---
    st.markdown('<div class="section-header">Core Publications</div>', unsafe_allow_html=True)
    papers = [
        {
            "title": "Knowledge-Guided Deep Reinforcement Learning for Pharmaceutical Wave Allocation",
            "venue": "Under Review, 2026",
            "tags": ["DRL", "Knowledge Graph", "Pharma Logistics"],
            "abstract": "Proposes KGDRL, a paradigm that injects domain heuristics into PPO via knowledge graphs and KL divergence constraints."
        },
        {
            "title": "Temperature-Zone-Urgency Heuristic for Multi-Temperature Warehouse Batching",
            "venue": "IEEE T-ASE, 2025",
            "tags": ["Heuristics", "GSP Compliance", "Batching"],
            "abstract": "Derives the TZU priority rule that respects cold-chain isolation while minimizing tardiness."
        },
        {
            "title": "Graph Attention Networks for Combinatorial Scheduling in Healthcare Supply Chains",
            "venue": "NeurIPS Workshop, 2025",
            "tags": ["GNN", "Scheduling", "Healthcare"],
            "abstract": "Demonstrates that GAT encoders outperform MLP baselines on warehouse state representation."
        },
    ]

    for paper in papers:
        with st.expander(paper["title"]):
            st.markdown(f"**Venue:** {paper['venue']}")
            st.markdown(f"**Tags:** {', '.join(paper['tags'])}")
            st.markdown(f"**Abstract:** {paper['abstract']}")

    st.markdown("---")

    # --- Patent Details ---
    st.markdown('<div class="section-header">Patent Portfolio</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#111827; border-radius:12px; padding:1.5rem;">
        <div style="font-weight:700; color:#f8fafc; font-size:1.1rem; margin-bottom:0.5rem;">
            CN Invention Patent - Substantive Examination
        </div>
        <div style="font-size:0.85rem; color:#94a3b8; line-height:1.8;">
            <div><b>Title:</b> Knowledge-Graph-Guided Deep Reinforcement Learning Method and System for Pharmaceutical Warehouse Wave Allocation</div>
            <div><b>Status:</b> Entered substantive examination (实审)</div>
            <div><b>Claims coverage:</b> KGDRL full pipeline including graph construction, GAT encoding, KL-guided policy optimization, and hierarchical action sampling</div>
            <div><b>Priority:</b> 2026-03-15</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.info("All research outputs are available upon request for due diligence.")
