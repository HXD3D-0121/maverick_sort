"""
HF Integration — Report Generator
===================================
Auto-generate natural-language summaries for:
  - What-If scenario comparison reports
  - Full business analysis reports (Pro)

Usage:
    from hf_integration.report_generator import summarize_what_if, generate_business_report
"""

from .client import chat_completion
from .prompts import render_prompt


def summarize_what_if(
    baseline_name: str,
    baseline_cost: float,
    baseline_time: float,
    baseline_compliance: float,
    scenario_name: str,
    scenario_cost: float,
    scenario_time: float,
    scenario_compliance: float,
    lang: str = "zh",
) -> str:
    """Generate an executive summary for a What-If scenario comparison."""
    delta_cost = ((scenario_cost - baseline_cost) / baseline_cost * 100) if baseline_cost else 0
    delta_time = ((scenario_time - baseline_time) / baseline_time * 100) if baseline_time else 0
    delta_compliance = ((scenario_compliance - baseline_compliance) / baseline_compliance * 100) if baseline_compliance else 0

    system, user = render_prompt(
        "report_what_if",
        lang=lang,
        baseline_name=baseline_name,
        baseline_cost=baseline_cost,
        baseline_time=baseline_time,
        baseline_compliance=baseline_compliance,
        scenario_name=scenario_name,
        scenario_cost=scenario_cost,
        scenario_time=scenario_time,
        scenario_compliance=scenario_compliance,
        delta_cost=delta_cost,
        delta_time=delta_time,
        delta_compliance=delta_compliance,
    )
    return chat_completion(user, task="report", lang=lang, system=system)


def generate_business_report(
    roi: float,
    payback: float,
    tco_advantage: str,
    differentiation: str,
    target_customer: str,
    best_strategy: str,
    key_risk: str,
    lang: str = "zh",
) -> str:
    """Generate a structured business analysis report (Pro only)."""
    system, user = render_prompt(
        "report_business_full",
        lang=lang,
        roi=roi,
        payback=payback,
        tco_advantage=tco_advantage,
        differentiation=differentiation,
        target_customer=target_customer,
        best_strategy=best_strategy,
        key_risk=key_risk,
    )
    return chat_completion(user, task="report", lang=lang, system=system)
