"""
Maverick-SORT — Demo & Simulation Module
===========================================
Pages:
  - Real-Time Simulation (HTML Dashboard Embed)
  - Demo Mode (Auto-play Presentation)

NOTE: All UI text is English. Remove any render_* to drop the page.
"""

import time
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path


# =============================================================================
# PAGE: Real-Time Simulation
# =============================================================================

def render_realtime_simulation():
    st.markdown('<div class="main-header">Real-Time Simulation</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Live warehouse sorting & dispatch visualization</div>', unsafe_allow_html=True)

    st.info("The real-time simulation runs in the original HTML dashboard below. Use the controls inside the panel to start/pause/reset.")

    html_path = Path(".") / "smart_wave_dashboard_en.html"
    if html_path.exists():
        try:
            with open(html_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            if len(html_content) < 1000:
                st.error("HTML dashboard file appears truncated.")
            else:
                components.html(html_content, height=900, scrolling=True)
        except Exception as e:
            st.error(f"Failed to load simulation dashboard: {e}")
    else:
        st.error("smart_wave_dashboard_en.html not found. Please ensure it is in the app directory.")


# =============================================================================
# PAGE: Demo Mode (NEW - Auto-play Presentation)
# =============================================================================

def render_demo_mode():
    st.markdown('<div class="main-header">Demo Mode</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Auto-play presentation for investor pitches and course defense</div>', unsafe_allow_html=True)

    slides = [
        {
            "title": "The Problem: 90,000 Orders/Day Chaos",
            "subtitle": "Manual wave allocation cannot keep up with omni-channel pharma demand.",
            "metrics": [
                ("Orders/Day", "90,000", "#ef4444"),
                ("Temp Violations", "5-8/day", "#f59e0b"),
                ("Picker Idle Time", "23%", "#3b82f6"),
                ("SLA Miss Rate", "12%", "#8b5cf6"),
            ],
            "narrative": "Pharmaceutical warehouses face a perfect storm: rising order volume, strict GSP cold-chain rules, and shrinking delivery windows. Legacy WMS systems use static rules that break down under real-world variability."
        },
        {
            "title": "The Solution: KGDRL Intelligence",
            "subtitle": "Knowledge-Graph-Guided Deep Reinforcement Learning for wave allocation.",
            "metrics": [
                ("Distance Reduced", "-18%", "#10b981"),
                ("Violations Cut", "-85%", "#10b981"),
                ("Decision Latency", "<100 ms", "#10b981"),
                ("Convergence", "120 episodes", "#3b82f6"),
            ],
            "narrative": "KGDRL combines graph neural networks with domain heuristics. The system learns from every shift while staying compliant via KL-divergence constraints to expert rules. Result: faster, cheaper, and fully auditable decisions."
        },
        {
            "title": "The Impact: Proven ROI",
            "subtitle": "Pilot simulations show 25% cost reduction with <6-month payback.",
            "metrics": [
                ("Annual Savings", "¥142K", "#f59e0b"),
                ("Payback Period", "5.8 mo", "#10b981"),
                ("ROI", "340%", "#10b981"),
                ("Uptime", "99.7%", "#3b82f6"),
            ],
            "narrative": "For a mid-size warehouse processing 5,000 orders/day, Maverick Pro delivers ¥142,000 annual net savings after subscription costs. The system pays for itself before the first renewal."
        },
    ]

    # Controls
    col_prev, col_info, col_next = st.columns([1, 3, 1])
    with col_prev:
        if st.button("Previous Slide", use_container_width=True):
            st.session_state.demo_slide_index = max(0, st.session_state.demo_slide_index - 1)
    with col_next:
        if st.button("Next Slide", use_container_width=True):
            st.session_state.demo_slide_index = min(len(slides) - 1, st.session_state.demo_slide_index + 1)
    with col_info:
        st.markdown(f"""
        <div style="text-align:center; padding:0.5rem; color:#94a3b8; font-size:0.9rem;">
            Slide {st.session_state.demo_slide_index + 1} of {len(slides)}
        </div>
        """, unsafe_allow_html=True)

    auto_play = st.toggle("Auto-play (5s per slide)", value=st.session_state.demo_auto_play)
    st.session_state.demo_auto_play = auto_play

    # Display current slide
    idx = st.session_state.demo_slide_index
    slide = slides[idx]

    st.markdown("---")

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1e3a5f 0%, #111827 100%); border-radius: 16px; padding: 2rem; border: 1px solid rgba(245,158,11,0.3); margin-bottom: 1.5rem;"">
        <div style="font-size: 1.8rem; font-weight: 800; color: #f8fafc; margin-bottom: 0.3rem;">{slide['title']}</div>
        <div style="font-size: 1rem; color: #94a3b8;">{slide['subtitle']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Metrics for this slide
    cols = st.columns(4)
    for col, (label, value, color) in zip(cols, slide["metrics"]):
        with col:
            st.markdown(f"""
            <div class="metric-card" style="border-top: 3px solid {color};">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color:{color};">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"""
    <div style="background: #111827; border-radius: 12px; padding: 1.5rem; font-size: 1rem; color: #e2e8f0; line-height: 1.7;">
        {slide['narrative']}
    </div>
    """, unsafe_allow_html=True)

    # Auto-advance logic (using empty + rerun pattern)
    if auto_play:
        time.sleep(0.1)  # Small delay to let UI render
        if idx < len(slides) - 1:
            placeholder = st.empty()
            placeholder.markdown("Auto-advancing...")
            time.sleep(5)
            st.session_state.demo_slide_index = idx + 1
            placeholder.empty()
            st.rerun()
        else:
            st.session_state.demo_auto_play = False
            st.success("Demo complete. Auto-play stopped.")

    st.markdown("---")
    st.caption("Tip: Use this mode during investor pitches or course defenses. Each slide answers a common question.")
