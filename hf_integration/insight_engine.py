"""
HF Integration — Insight Engine
=================================
Natural-language decision explanations for:
  - Algorithm Arena benchmark results
  - Strategy Optimizer Pareto points
  - Live Adaptive Intelligence adjustments
  - SLA trend summaries

Usage:
    from hf_integration.insight_engine import explain_benchmark, explain_pareto
    text = explain_benchmark(scenario="Emergency", best_algo="KGDRL", ...)
"""

from typing import Optional

from .client import chat_completion
from .prompts import render_prompt


def explain_benchmark(
    scenario: str,
    best_algo: str,
    best_metric: str,
    best_value: float,
    baseline_algo: str,
    baseline_metric: str,
    baseline_value: float,
    improvement: str,
    lang: str = "zh",
) -> str:
    """Generate a natural-language conclusion for Algorithm Arena benchmark comparison."""
    system, user = render_prompt(
        "insight_algorithm_arena",
        lang=lang,
        scenario=scenario,
        best_algo=best_algo,
        best_metric=best_metric,
        best_value=best_value,
        baseline_algo=baseline_algo,
        baseline_metric=baseline_metric,
        baseline_value=baseline_value,
        improvement=improvement,
    )
    return chat_completion(user, task="insight", lang=lang, system=system)


def explain_pareto(
    cost: float,
    time: float,
    compliance: float,
    cost_w: float,
    time_w: float,
    compliance_w: float,
    action: str,
    lang: str = "zh",
) -> str:
    """Generate an explanation for a selected NSGA-II Pareto strategy point."""
    system, user = render_prompt(
        "insight_strategy_optimizer",
        lang=lang,
        cost=cost,
        time=time,
        compliance=compliance,
        cost_w=cost_w,
        time_w=time_w,
        compliance_w=compliance_w,
        action=action,
    )
    return chat_completion(user, task="insight", lang=lang, system=system)


def explain_adaptive_adjustment(
    current_time: str,
    predicted_orders: int,
    old_capacity: int,
    new_capacity: int,
    trigger_reason: str,
    lang: str = "zh",
) -> str:
    """Generate an operational summary for a Live Adaptive capacity adjustment."""
    system, user = render_prompt(
        "insight_live_adaptive",
        lang=lang,
        current_time=current_time,
        predicted_orders=predicted_orders,
        old_capacity=old_capacity,
        new_capacity=new_capacity,
        trigger_reason=trigger_reason,
    )
    return chat_completion(user, task="insight", lang=lang, system=system)


def explain_sla_trend(
    period: str,
    avg_otd: float,
    delta_otd: float,
    worst_zone: str,
    top_delay_reason: str,
    lang: str = "zh",
) -> str:
    """Generate an insight from SLA trend data."""
    system, user = render_prompt(
        "insight_sla_trend",
        lang=lang,
        period=period,
        avg_otd=avg_otd,
        delta_otd=delta_otd,
        worst_zone=worst_zone,
        top_delay_reason=top_delay_reason,
    )
    return chat_completion(user, task="insight", lang=lang, system=system)


def explain_3d_command_center(
    profit: float,
    cost: float,
    on_time_rate: float,
    active_strategy: str,
    lang: str = "zh",
) -> str:
    """Generate a smart insight card for the 3D Command Center (Pro)."""
    system_zh = "你是一位医药仓储运营指挥官，正在查看3D Profit Mountain视图。"
    system_en = "You are a warehouse operations commander viewing the 3D Profit Mountain."
    system = system_zh if lang == "zh" else system_en

    if lang == "zh":
        user = (
            f"当前3D视图核心数据：利润¥{profit:,.0f}，成本¥{cost:,.0f}，准时率{on_time_rate:.1%}，"
            f"激活策略：{active_strategy}。请生成一段不超过50字的中文战术解读，"
            f"说明当前盈利点的关键成功因素和下一步关注重点。"
        )
    else:
        user = (
            f"Current 3D view: Profit ¥{profit:,.0f}, Cost ¥{cost:,.0f}, "
            f"OTD {on_time_rate:.1%}, Active strategy: {active_strategy}. "
            f"Generate a max 40-word tactical insight on key success factors and next focus."
        )

    return chat_completion(user, task="insight", lang=lang, system=system)
