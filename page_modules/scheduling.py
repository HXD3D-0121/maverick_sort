"""
Sunergy Pharma — Scheduling Engine Module
===========================================
Pages:
  - Algorithm Arena
  - Scenario Simulator (What-If Lab)
  - Strategy Optimizer (Pareto/NSGA-II)
  - Live Adaptive Intelligence (EWMA)

NOTE: All UI text is English. Each page can be dropped independently.
"""

import time
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
from .shared import try_import_what_if, try_import_mos, try_import_adaptive


# =============================================================================
# PAGE: Algorithm Arena
# =============================================================================

def render_algorithm_arena():
    st.markdown('<div class="main-header">Algorithm Arena</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">KGDRL vs 5 Heuristics - Transparent Performance Data</div>', unsafe_allow_html=True)

    cols = st.columns(4)
    for i, (label, value, delta, color) in enumerate([
        ("KGDRL Distance", "665.7 m", "Lowest", "#10b981"),
        ("PPO Reward", "4,007.5", "Best Single", "#3b82f6"),
        ("TZU Violations", "21.4", "Best Heuristic", "#f59e0b"),
        ("Training Episodes", "120", "Converged", "#8b5cf6"),
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

    arena_df = pd.DataFrame([
        {"Method": "FCFS", "Reward": 1786.9, "Distance": 690.9, "Waves": 85.9, "Miss": 0.0, "Viol": 38.5, "Tier": "Heuristic"},
        {"Method": "TEMP_FIRST", "Reward": -2958.1, "Distance": 987.4, "Waves": 125.8, "Miss": 0.0, "Viol": 0.0, "Tier": "Heuristic"},
        {"Method": "ZONE_NN", "Reward": 1733.8, "Distance": 669.0, "Waves": 82.9, "Miss": 0.0, "Viol": 37.3, "Tier": "Heuristic"},
        {"Method": "EDD", "Reward": 1752.0, "Distance": 667.8, "Waves": 83.1, "Miss": 0.0, "Viol": 37.5, "Tier": "Heuristic"},
        {"Method": "TZU", "Reward": 144.6, "Distance": 666.7, "Waves": 83.0, "Miss": 0.0, "Viol": 21.4, "Tier": "Heuristic"},
        {"Method": "PPO (Vanilla)", "Reward": 4007.5, "Distance": 695.5, "Waves": 87.3, "Miss": 4.4, "Viol": 36.7, "Tier": "DRL"},
        {"Method": "KGDRL-Full", "Reward": 1908.8, "Distance": 665.7, "Waves": 82.8, "Miss": 0.0, "Viol": 39.0, "Tier": "DRL+KG"},
    ])
    arena_df["Color"] = arena_df.apply(
        lambda r: "#10b981" if r["Method"] == "KGDRL-Full" else ("#3b82f6" if r["Tier"] == "DRL" else "#64748b"), axis=1
    )

    def highlight_kgdrl(row):
        if row["Method"] == "KGDRL-Full":
            return ["background-color: rgba(16,185,129,0.15)"] * len(row)
        return [""] * len(row)

    st.dataframe(arena_df.style.apply(highlight_kgdrl, axis=1), width='stretch', hide_index=True)

    col_bar, col_dist = st.columns(2)
    with col_bar:
        st.markdown("**Reward Comparison**")
        bchart = alt.Chart(arena_df).mark_bar().encode(
            x=alt.X("Method", sort=None),
            y="Reward",
            color=alt.Color("Color:N", scale=None)
        ).properties(height=260)
        st.altair_chart(bchart, width='stretch')

    with col_dist:
        st.markdown("**Distance Comparison**")
        dchart = alt.Chart(arena_df).mark_bar().encode(
            x=alt.X("Method", sort=None),
            y="Distance",
            color=alt.Color("Color:N", scale=None)
        ).properties(height=260)
        st.altair_chart(dchart, width='stretch')


# =============================================================================
# PAGE: Scenario Simulator (What-If Lab)
# =============================================================================

def render_scenario_lab():
    st.markdown('<div class="main-header">What-If Scenario Lab</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Real simulation engine - test hypotheses before committing</div>', unsafe_allow_html=True)

    WhatIfSimulator, ScenarioConfig, ScenarioResult, available = try_import_what_if()

    col_params, col_results = st.columns([1, 2])

    with col_params:
        st.markdown('<div class="section-header">Scenario Parameters</div>', unsafe_allow_html=True)

        template = st.selectbox("Quick Template", [
            "Custom (manual)", "Wave Capacity Sweep", "Setup Cost Sensitivity",
            "Peak Season Comparison", "Policy Showdown",
        ])

        if template == "Custom (manual)":
            n_scenarios = st.number_input("Scenarios", 2, 6, 3)
            scenario_configs = []
            for i in range(n_scenarios):
                with st.expander(f"Scenario {i+1}", expanded=(i == 0)):
                    name = st.text_input(f"Name {i+1}", f"Scenario {i+1}", key=f"sc_name_{i}")
                    cap = st.slider(f"Capacity {i+1}", 8, 35, 15 + i * 5, key=f"sc_cap_{i}")
                    setup = st.slider(f"Setup Cost {i+1}", 5.0, 40.0, 10.0 + i * 5, 2.5, key=f"sc_setup_{i}")
                    peak = st.slider(f"Peak {i+1}", 1.0, 5.0, 1.5 + i * 0.5, 0.2, key=f"sc_peak_{i}")
                    pol = st.selectbox(f"Policy {i+1}", ["TZU", "KGDRL", "PPO", "FCFS", "TEMP_FIRST", "ZONE_NN", "EDD"], key=f"sc_pol_{i}")
                    if available and ScenarioConfig:
                        scenario_configs.append(ScenarioConfig(
                            name=name, max_wave_orders=cap, alpha_setup=setup,
                            peak_multiplier=peak, policy_type=pol
                        ))
        else:
            scenario_configs = None
            st.info("Click Run to execute template")

        n_instances = st.slider("Instances", 1, 10, 3)
        run_btn = st.button("Run Real Simulation", type="primary", use_container_width=True)

    with col_results:
        st.markdown('<div class="section-header">Results</div>', unsafe_allow_html=True)

        if run_btn:
            if not available or WhatIfSimulator is None:
                st.error("What-If Simulator module not available. Please ensure what_if_simulator.py is present.")
            else:
                with st.spinner("Running What-If Simulator..."):
                    start = time.time()
                    sim = WhatIfSimulator(output_dir="./what_if_results")

                    if template == "Custom (manual)" and scenario_configs:
                        scenarios = scenario_configs
                    elif template == "Wave Capacity Sweep":
                        scenarios = [ScenarioConfig(name=f"Cap={c}", max_wave_orders=c) for c in [10, 15, 20, 25, 30]]
                    elif template == "Setup Cost Sensitivity":
                        scenarios = [ScenarioConfig(name=f"Setup={c:.0f}", alpha_setup=c) for c in [5.0, 10.0, 15.0, 20.0, 30.0]]
                    elif template == "Peak Season Comparison":
                        scenarios = [
                            ScenarioConfig(name="Normal", peak_multiplier=1.0),
                            ScenarioConfig(name="Flu Season", peak_multiplier=2.8),
                            ScenarioConfig(name="Double 11", peak_multiplier=4.0),
                        ]
                    else:
                        scenarios = [ScenarioConfig(name=f"Policy={p}", policy_type=p) for p in ["FCFS", "TEMP_FIRST", "ZONE_NN", "EDD", "TZU", "KGDRL", "PPO"]]

                    results = sim.compare_scenarios(scenarios, n_instances=n_instances, verbose=False)
                    elapsed = time.time() - start
                    st.session_state.pro_what_if_results = results
                    st.success(f"Done in {elapsed:.1f}s")

        if st.session_state.pro_what_if_results:
            rows = []
            for name, r in st.session_state.pro_what_if_results.items():
                rows.append({
                    "Scenario": name, "Cost": round(r.total_cost, 0),
                    "Distance": round(r.total_distance, 0), "Waves": r.n_waves,
                    "Viol%": round(r.violation_rate, 1), "OnTime%": round(r.on_time_rate, 1),
                })
            df = pd.DataFrame(rows)
            st.dataframe(df, width='stretch', hide_index=True)

            best_idx = df["Cost"].idxmin()
            best = df.iloc[best_idx]
            st.markdown(f"""
            <div style="background:#111827; border-radius:8px; padding:1rem; border-left:4px solid #10b981;">
                <div style="font-weight:700; color:#10b981;">Best: {best['Scenario']} | Cost=¥{best['Cost']:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)

            c1 = alt.Chart(df).mark_bar().encode(
                x=alt.X("Scenario", sort=None), y="Cost",
                color=alt.condition(alt.datum.Scenario == best["Scenario"], alt.value("#10b981"), alt.value("#3b82f6"))
            ).properties(height=260)
            st.altair_chart(c1, width='stretch')
        else:
            st.info("Configure parameters and click Run to see results")


# =============================================================================
# PAGE: Strategy Optimizer (NSGA-II Pareto)
# =============================================================================

def render_strategy_optimizer():
    st.markdown('<div class="main-header">Multi-Objective Optimizer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">NSGA-II powered Pareto frontier - Cost x Time x Compliance</div>', unsafe_allow_html=True)

    MultiObjectiveScheduler, MultiObjectiveConfig, STRATEGY_PROFILES, ParetoSolution, available = try_import_mos()

    col_ctrl, col_viz = st.columns([1, 2])

    with col_ctrl:
        st.markdown('<div class="section-header">NSGA-II Config</div>', unsafe_allow_html=True)

        strategy = st.radio("Strategy Mode", [
            ("Cost First", "cost_first"), ("Time First", "time_first"),
            ("Compliance First", "compliance_first"), ("Balanced", "balanced")
        ], format_func=lambda x: x[0], index=3)

        st.markdown("---")
        pop_size = st.slider("Population", 20, 100, 50, 10)
        n_gen = st.slider("Generations", 20, 200, 80, 10)
        cx_rate = st.slider("Crossover Rate", 0.5, 1.0, 0.9, 0.05)
        mut_rate = st.slider("Mutation Rate", 0.05, 0.3, 0.15, 0.05)

        run_btn = st.button("Run NSGA-II", type="primary", use_container_width=True)

    with col_viz:
        st.markdown('<div class="section-header">Pareto Front</div>', unsafe_allow_html=True)

        if run_btn:
            if not available or MultiObjectiveScheduler is None:
                st.error("Multi-objective scheduler module not available.")
            else:
                with st.spinner(f"Evolving {pop_size} individuals for {n_gen} generations..."):
                    start = time.time()
                    config = MultiObjectiveConfig(
                        pop_size=pop_size, n_generations=n_gen,
                        crossover_rate=cx_rate, mutation_rate=mut_rate
                    )
                    scheduler = MultiObjectiveScheduler(config=config, n_orders=80)
                    front = scheduler.optimize(verbose=False)
                    st.session_state.pro_pareto_front = front
                    st.session_state.pro_pareto_scheduler = scheduler
                    elapsed = time.time() - start
                    st.success(f"NSGA-II complete in {elapsed:.1f}s | Front size: {len(front)}")

        if st.session_state.pro_pareto_front and available:
            front = st.session_state.pro_pareto_front
            scheduler = st.session_state.pro_pareto_scheduler

            pareto_data = []
            for sol in front:
                pareto_data.append({
                    "Cost": sol.objectives[0],
                    "Miss Rate": sol.objectives[1],
                    "Violations": sol.objectives[2],
                })
            pareto_df = pd.DataFrame(pareto_data)

            scat = alt.Chart(pareto_df).mark_circle(size=80, opacity=0.7).encode(
                x=alt.X("Cost", scale=alt.Scale(domain=[pareto_df["Cost"].min() * 0.9, pareto_df["Cost"].max() * 1.1])),
                y=alt.Y("Miss Rate", scale=alt.Scale(domain=[-0.005, max(pareto_df["Miss Rate"].max() * 1.2, 0.05)])),
                size=alt.Size("Violations", scale=alt.Scale(range=[30, 300])),
                color=alt.Color("Violations", scale=alt.Scale(scheme="plasma")),
                tooltip=["Cost", "Miss Rate", "Violations"]
            ).properties(height=320)
            st.altair_chart(scat, width='stretch')
            st.caption("Bubble size = Violations | Color = Violations | NSGA-II rank-0 front")

            if scheduler:
                mode = strategy[1]
                recs = scheduler.get_all_strategy_recommendations()
                if mode in recs:
                    rec = recs[mode]
                    p = rec["profile"]
                    s = rec["summary"]
                    st.markdown(f"""
                    <div style="background:#111827; border-radius:8px; padding:1rem; border-left:4px solid {p.color};">
                        <div style="font-weight:700; color:{p.color};">{p.icon} {p.name}</div>
                        <div style="font-size:0.85rem; color:#94a3b8; margin-top:0.3rem;">
                            Cost=¥{s['estimated_cost']:.0f} | Miss={s['miss_rate']:.3f} | Viol={s['violations']:.0f} | Waves={s['n_waves']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Configure NSGA-II and click Run")


# =============================================================================
# PAGE: Live Adaptive Intelligence (EWMA)
# =============================================================================

def render_live_adaptive():
    st.markdown('<div class="main-header">Real-Time Adaptive Monitor</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">EWMA prediction + Dynamic capacity + 24-hour simulation</div>', unsafe_allow_html=True)

    AdaptivePolicyController, AdaptiveConfig, available = try_import_adaptive()

    cols = st.columns(4)
    for i, (label, value, unit, color) in enumerate([
        ("Current Capacity", "20", "orders/wave", "#3b82f6"),
        ("EWMA Rate", "5.8", "ord/min", "#06b6d4"),
        ("Trend", "+12%", "next 15min", "#10b981"),
        ("Peak Alert", "Moderate", "15:00-17:00", "#f59e0b"),
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

    col_cfg, col_run = st.columns([1, 1])
    with col_cfg:
        st.markdown('<div class="section-header">Adaptive Config</div>', unsafe_allow_html=True)
        ewma_alpha = st.slider("EWMA Alpha", 0.1, 0.5, 0.3, 0.05)
        base_cap = st.slider("Base Capacity", 10, 30, 20, 1)
        min_cap = st.slider("Min Capacity", 5, 15, 8, 1)
        max_cap = st.slider("Max Capacity", 25, 50, 35, 1)
        run_sim = st.button("Run 24-Hour Simulation", type="primary", use_container_width=True)

    with col_run:
        st.markdown('<div class="section-header">Status</div>', unsafe_allow_html=True)
        if available:
            st.success("adaptive_policy.py loaded")
        else:
            st.error("adaptive_policy.py not available")

    if run_sim and available and AdaptivePolicyController is not None:
        with st.spinner("Simulating 24 hours..."):
            config = AdaptiveConfig(
                ewma_alpha=ewma_alpha, base_capacity=base_cap,
                min_capacity=min_cap, max_capacity=max_cap
            )
            ctrl = AdaptivePolicyController(config)
            np.random.seed(42)
            base_rate = 3.0
            sim_results = []

            for hour in range(24):
                peak_factor = 1.0
                if 8 <= hour <= 11:
                    peak_factor = 2.8
                elif 13 <= hour <= 15:
                    peak_factor = 1.8
                elif 0 <= hour <= 5:
                    peak_factor = 0.2

                observed = base_rate * peak_factor * (0.8 + np.random.rand() * 0.4)
                load = min(0.95, 0.3 + peak_factor * 0.2 + np.random.rand() * 0.1)
                decision = ctrl.step(observed, load, hour)
                sim_results.append({
                    "Hour": hour, "Observed Rate": observed,
                    "Capacity": decision["capacity"],
                    "Release Threshold": decision["release_threshold"],
                    "Predicted Rate": decision["predicted_rate"],
                    "Peak": decision["peak_detected"],
                    "Valley": decision["valley_detected"],
                    "Reason": decision["reason"],
                })

            st.session_state.pro_adaptive_results = pd.DataFrame(sim_results)
            st.session_state.pro_adaptive_controller = ctrl
            st.success(f"24-hour simulation complete | {len(sim_results)} steps recorded")

    if st.session_state.pro_adaptive_results is not None:
        df = st.session_state.pro_adaptive_results

        melted = df.melt(id_vars=["Hour"], value_vars=["Observed Rate", "Predicted Rate"],
                         var_name="Metric", value_name="Value")
        line1 = alt.Chart(melted).mark_line(strokeWidth=2).encode(
            x="Hour", y="Value", color="Metric",
            tooltip=["Hour", "Metric", "Value"]
        ).properties(height=280)
        st.altair_chart(line1, width='stretch')

        cap_chart = alt.Chart(df).mark_line(color="#f59e0b", strokeWidth=2).encode(
            x="Hour", y="Capacity",
            tooltip=["Hour", "Capacity", "Reason"]
        ).properties(height=200)
        st.altair_chart(cap_chart, width='stretch')

        st.markdown("<div class='section-header'>Adjustment Log</div>", unsafe_allow_html=True)
        log_df = df[df["Reason"].str.contains("peak|valley|high_load", case=False, na=False)][["Hour", "Capacity", "Predicted Rate", "Reason"]]
        if not log_df.empty:
            st.dataframe(log_df, width='stretch', hide_index=True)
        else:
            st.info("No significant adjustments triggered in this simulation.")
    else:
        st.info("Configure and click Run 24-Hour Simulation")
