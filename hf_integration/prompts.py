"""
HF Integration — Bilingual Prompt Templates
============================================
All prompts are structured for Qwen2.5-Instruct (Chinese-primary, English-secondary).
Each template supports variable substitution via `.format(**kwargs)`.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PromptTemplate:
    """A bilingual prompt template with system + user parts."""
    name: str
    system_zh: str
    system_en: str
    user_zh: str
    user_en: str

    def render(self, lang: str = "zh", **kwargs) -> tuple[Optional[str], str]:
        """Return (system_prompt, user_prompt) for the given language."""
        system = self.system_zh if lang == "zh" else self.system_en
        user = self.user_zh if lang == "zh" else self.user_en
        # Only format if kwargs provided
        if kwargs:
            user = user.format(**kwargs)
        return (system if system else None, user)


# =============================================================================
# ① Insight Engine — Decision Explanation
# =============================================================================

INSIGHT_ALGORITHM_ARENA = PromptTemplate(
    name="insight_algorithm_arena",
    system_zh="你是一位医药仓储智能调度系统的AI分析师，擅长用简洁通俗的中文解释算法性能差异。",
    system_en="You are an AI analyst for a pharmaceutical warehouse scheduling system. Explain algorithm differences concisely in English.",
    user_zh="""请根据以下算法 benchmark 结果，生成一段不超过80字的中文结论：

场景：{scenario}
最优算法：{best_algo}（{best_metric}={best_value}）
对比算法：{baseline_algo}（{baseline_metric}={baseline_value}）
提升幅度：{improvement}

要求：1) 点明最优算法的核心优势；2) 用一句话建议何时选用该算法；3) 语气专业但易懂。""",
    user_en="""Based on the benchmark below, generate a concise English conclusion (max 60 words):

Scenario: {scenario}
Best algorithm: {best_algo} ({best_metric}={best_value})
Baseline: {baseline_algo} ({baseline_metric}={baseline_value})
Improvement: {improvement}

Requirements: 1) Highlight the best algorithm's key advantage; 2) One-sentence recommendation on when to use it; 3) Professional but accessible tone.""",
)

INSIGHT_STRATEGY_OPTIMIZER = PromptTemplate(
    name="insight_strategy_optimizer",
    system_zh="你是一位供应链策略分析师，擅长将NSGA-II多目标优化结果翻译成业务语言。",
    system_en="You are a supply-chain strategy analyst translating NSGA-II Pareto results into business language.",
    user_zh="""请解释以下策略配置：

- 成本得分：{cost:.2f}，时效得分：{time:.2f}，合规得分：{compliance:.2f}
- 权重配置：成本{cost_w:.0%} / 时效{time_w:.0%} / 合规{compliance_w:.0%}
- 推荐动作：{action}

生成一段不超过60字的中文解释，包含：1) 适合的业务场景；2) 主要权衡点；3) 一句执行建议。""",
    user_en="""Explain this strategy configuration:

- Cost score: {cost:.2f}, Time score: {time:.2f}, Compliance score: {compliance:.2f}
- Weights: Cost {cost_w:.0%} / Time {time_w:.0%} / Compliance {compliance_w:.0%}
- Recommended action: {action}

Generate a max 50-word English explanation covering: 1) Suitable business scenario; 2) Key trade-off; 3) One actionable recommendation.""",
)

INSIGHT_LIVE_ADAPTIVE = PromptTemplate(
    name="insight_live_adaptive",
    system_zh="你是一位仓库运营分析师，正在实时监控波次调度系统。",
    system_en="You are a warehouse operations analyst monitoring wave scheduling in real time.",
    user_zh="""系统刚刚完成一次自适应调整，请生成一段不超过60字的中文运营解读：

- 当前时间：{current_time}
- 预测订单量：{predicted_orders}
- 调整前波次容量：{old_capacity}
- 调整后波次容量：{new_capacity}
- 触发原因：{trigger_reason}

要求：1) 说明调整的业务意义；2) 预估对准时率的影响；3) 一句值班建议。""",
    user_en="""The system just performed an adaptive adjustment. Generate a max 50-word English operational summary:

- Current time: {current_time}
- Predicted orders: {predicted_orders}
- Old wave capacity: {old_capacity}
- New wave capacity: {new_capacity}
- Trigger reason: {trigger_reason}

Requirements: 1) Business meaning of the adjustment; 2) Estimated on-time impact; 3) One duty-room recommendation.""",
)

INSIGHT_SLA_TREND = PromptTemplate(
    name="insight_sla_trend",
    system_zh="你是一位医药冷链物流质量分析师。",
    system_en="You are a pharmaceutical cold-chain logistics quality analyst.",
    user_zh="""请根据以下SLA趋势数据生成一段不超过50字的中文洞察：

- 统计周期：{period}
- 平均准时率：{avg_otd:.1%}
- 环比变化：{delta_otd:+.1%}
- 最差温度区：{worst_zone}
- 主要延误原因：{top_delay_reason}

要求：1) 点明核心问题；2) 给出一个聚焦的改进建议。""",
    user_en="""Generate a max 40-word English insight from this SLA trend:

- Period: {period}
- Avg OTD: {avg_otd:.1%}
- WoW change: {delta_otd:+.1%}
- Worst zone: {worst_zone}
- Top delay reason: {top_delay_reason}

Requirements: 1) Identify the core issue; 2) One focused improvement suggestion.""",
)

# =============================================================================
# ② Report Generator — Auto Summarization
# =============================================================================

REPORT_WHAT_IF = PromptTemplate(
    name="report_what_if",
    system_zh="你是一位供应链咨询顾问，擅长将模拟数据提炼为决策摘要。",
    system_en="You are a supply-chain consultant who distills simulation data into decision briefs.",
    user_zh="""请根据以下What-If场景对比结果，生成一段中文执行摘要（不超过100字）：

基准场景：{baseline_name}
{baseline_name}指标：成本={baseline_cost}，时效={baseline_time}，合规={baseline_compliance}

对比场景：{scenario_name}
{scenario_name}指标：成本={scenario_cost}，时效={scenario_time}，合规={scenario_compliance}

变化：成本{delta_cost:+.1f}%，时效{delta_time:+.1f}%，合规{delta_compliance:+.1f}%

要求：1) 一句话总结最优选择；2) 解释关键差异的成因；3) 给出一个可落地的行动建议。""",
    user_en="""Generate an English executive summary (max 80 words) from this What-If comparison:

Baseline: {baseline_name}
  Cost={baseline_cost}, Time={baseline_time}, Compliance={baseline_compliance}

Scenario: {scenario_name}
  Cost={scenario_cost}, Time={scenario_time}, Compliance={scenario_compliance}

Changes: Cost {delta_cost:+.1f}%, Time {delta_time:+.1f}%, Compliance {delta_compliance:+.1f}%

Requirements: 1) One-sentence optimal choice; 2) Explain key driver; 3) One actionable recommendation.""",
)

REPORT_BUSINESS_FULL = PromptTemplate(
    name="report_business_full",
    system_zh="你是一位资深医药供应链投资分析师，正在撰写商业分析报告。",
    system_en="You are a senior pharmaceutical supply-chain investment analyst writing a business report.",
    user_zh="""请基于以下数据生成一段结构化商业分析（不超过150字）：

【财务模型】
- 5年ROI：{roi:.1f}%
- 投资回收期：{payback}年
- TCO优势 vs 竞品：{tco_advantage}

【竞争定位】
- 核心差异化：{differentiation}
- 目标客户：{target_customer}

【策略建议】
- 最优调度策略：{best_strategy}
- 预期风险：{key_risk}

要求：使用"投资亮点—核心数据—策略建议"三段式结构，语言专业、有说服力。""",
    user_en="""Generate a structured business analysis (max 120 words):

[Financial]
- 5Y ROI: {roi:.1f}%
- Payback: {payback} years
- TCO advantage vs competitors: {tco_advantage}

[Competitive Positioning]
- Key differentiation: {differentiation}
- Target customer: {target_customer}

[Strategic Recommendation]
- Optimal strategy: {best_strategy}
- Key risk: {key_risk}

Use "Investment Highlight → Core Data → Strategy" structure. Professional and persuasive tone.""",
)

# =============================================================================
# ③ Copilot — FAQ & Context-Aware Assistant
# =============================================================================

COPILOT_FAQ = PromptTemplate(
    name="copilot_faq",
    system_zh="""你是Sunergy Pharma智能仓储系统的AI助手，名字叫"Sunergy Copilot"。
你的职责是帮助用户理解系统功能、算法原理和业务价值。
回答要简洁（不超过80字），专业但易懂。如果问题超出系统范围，礼貌引导用户联系支持团队。""",
    system_en="""You are Sunergy Copilot, the AI assistant for the Sunergy Pharma smart warehouse system.
Help users understand system features, algorithm principles, and business value.
Keep answers concise (max 60 words), professional yet accessible. If the question is out of scope, politely guide users to contact support.""",
    user_zh="{question}",
    user_en="{question}",
)

COPILOT_CONTEXT = PromptTemplate(
    name="copilot_context",
    system_zh="""你是Sunergy Pharma的上下文感知AI助手。你可以看到用户当前正在浏览的页面数据。
回答时要结合当前页面的具体数据给出建议，不要泛泛而谈。
保持简洁（不超过100字），中文回答。""",
    system_en="""You are Sunergy Pharma's context-aware AI assistant. You can see the user's current page data.
Provide advice grounded in the specific data shown on the page. Avoid generic responses.
Keep it concise (max 80 words), answer in English.""",
    user_zh="""用户当前所在页面：{page_name}
页面关键数据：{page_context}

用户问题：{question}

请基于上述数据回答。""",
    user_en="""User is on page: {page_name}
Page context: {page_context}

User question: {question}

Please answer based on the data above.""",
)

# =============================================================================
# ④ Alert Analyzer — Root-Cause Analysis
# =============================================================================

ALERT_ANALYZE = PromptTemplate(
    name="alert_analyze",
    system_zh="你是一位医药仓储异常诊断专家，擅长结合历史数据和知识库进行根因分析。",
    system_en="You are a pharmaceutical warehouse anomaly diagnosis expert skilled in root-cause analysis using historical data and knowledge bases.",
    user_zh="""请对以下告警进行根因分析和处置建议：

【告警信息】
- 告警ID：{alert_id}
- 类型：{alert_type}
- 严重级别：{severity}
- 发生时间：{alert_time}
- 关联区域：{zone}
- 描述：{description}

【历史相似案例】
{similar_cases}

请输出：
1. 根因推断（不超过30字）
2. 处置建议（不超过30字）
3. 预防措施（不超过20字）""",
    user_en="""Perform root-cause analysis and remediation for this alert:

[Alert]
- ID: {alert_id}
- Type: {alert_type}
- Severity: {severity}
- Time: {alert_time}
- Zone: {zone}
- Description: {description}

[Historical Similar Cases]
{similar_cases}

Output:
1. Root cause (max 25 words)
2. Remediation (max 25 words)
3. Prevention (max 15 words)""",
)

# =============================================================================
# ⑤ Demand Forecaster — Time-Series Explanation
# =============================================================================

FORECAST_SUMMARY = PromptTemplate(
    name="forecast_summary",
    system_zh="你是一位医药需求预测分析师，擅长解读时间序列预测结果。",
    system_en="You are a pharmaceutical demand forecasting analyst interpreting time-series results.",
    user_zh="""请解读以下需求预测结果：

- 预测时间范围：未来{horizon}天
- 预测总订单量：{forecast_total}
- 日均订单：{avg_daily:.0f}
- 峰值日：{peak_day}（{peak_value}单）
- 趋势判断：{trend}

请生成一段不超过50字的中文运营建议。""",
    user_en="""Interpret this demand forecast:

- Horizon: next {horizon} days
- Total forecast: {forecast_total}
- Daily avg: {avg_daily:.0f}
- Peak day: {peak_day} ({peak_value} orders)
- Trend: {trend}

Generate a max 40-word English operations recommendation.""",
)

# =============================================================================
# Prompt registry
# =============================================================================

PROMPT_REGISTRY = {
    "insight_algorithm_arena": INSIGHT_ALGORITHM_ARENA,
    "insight_strategy_optimizer": INSIGHT_STRATEGY_OPTIMIZER,
    "insight_live_adaptive": INSIGHT_LIVE_ADAPTIVE,
    "insight_sla_trend": INSIGHT_SLA_TREND,
    "report_what_if": REPORT_WHAT_IF,
    "report_business_full": REPORT_BUSINESS_FULL,
    "copilot_faq": COPILOT_FAQ,
    "copilot_context": COPILOT_CONTEXT,
    "alert_analyze": ALERT_ANALYZE,
    "forecast_summary": FORECAST_SUMMARY,
}


def render_prompt(name: str, lang: str = "zh", **kwargs) -> tuple[Optional[str], str]:
    """Lookup and render a prompt template by name."""
    if name not in PROMPT_REGISTRY:
        raise KeyError(f"Unknown prompt template: {name}. Available: {list(PROMPT_REGISTRY.keys())}")
    return PROMPT_REGISTRY[name].render(lang=lang, **kwargs)
