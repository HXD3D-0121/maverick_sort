"""
HF Integration — Sunergy Copilot
==================================
AI assistant with two modes:
  1. FAQ mode (Standard): Pre-loaded Q&A for common questions
  2. Context-aware mode (Pro): Responds based on current page data

Usage:
    from hf_integration.copilot import ask_faq, ask_with_context
    answer = ask_faq("什么是KGDRL？")
"""

import json
from typing import Optional

from .client import chat_completion, chat_completion_stream
from .prompts import render_prompt


# =============================================================================
# Pre-loaded FAQ cache (Standard Edition)
# =============================================================================

FAQ_DATABASE_ZH = {
    "什么是KGDRL": "KGDRL（Knowledge-Guided Deep Reinforcement Learning）是本项目核心算法，它将知识图谱与图注意力网络（GAT）嵌入PPO策略中，使AI调度器在学习过程中继承专家规则（如TZU启发式），从而在新环境中更快收敛、更稳定。",
    "KGDRL和PPO有什么区别": "PPO是通用强化学习算法，从零探索；KGDRL在PPO基础上增加了知识引导层——用知识图谱编码领域专家经验，通过KL散度约束确保策略不会偏离合理范围。实验显示KGDRL在紧急订单场景下比PPO提升15-23%。",
    "TZU和FCFS有什么区别": "FCFS（先到先服务）是最简单的排队规则，不考虑订单优先级；TZU（温度-紧急度-单位价值）是我们设计的启发式规则，优先处理高价值、紧急、温控要求严格的订单。TZU通常比FCFS提升10-15%准时率。",
    "什么是波次分配": "波次分配（Wave Allocation）是将一天内的订单按时间窗聚合成'波次'，再分配给不同库区/工作站处理。合理的波次划分能平衡产能、减少冷链断链风险、提升车辆装载率。",
    "系统支持哪些温度区": "系统支持5个温度区：常温（Ambient, 15-25°C）、阴凉（Cool, 2-8°C）、冷藏（Cold, 2-8°C）、冷冻（Frozen, -20°C）、深冻（Deep Frozen, -80°C）。每个区有独立的容量约束和合规检查。",
    "什么是NSGA-II": "NSGA-II（非支配排序遗传算法II）是多目标优化算法，用于在成本、时效、合规三个互相冲突的目标之间寻找Pareto最优前沿。用户可以在前沿上选择最符合自身业务偏好的策略点。",
    "如何上传自己的数据": "点击左侧边栏'Data Upload Hub'，上传orders.csv、inventory.csv等文件。系统会自动验证列名和数据类型，验证通过后即可在实时模式下查看基于真实数据的分析结果。（专业版功能）",
    "什么是自适应策略": "自适应策略（Adaptive Policy）通过EWMA指数加权移动平均预测订单到达率，动态调整每波次的容量上限。当检测到异常峰值时，系统会自动扩容或提前触发波次，减少订单积压。（专业版功能）",
}

FAQ_DATABASE_EN = {
    "What is KGDRL": "KGDRL (Knowledge-Guided Deep RL) is the core algorithm of this system. It embeds a Knowledge Graph and Graph Attention Network (GAT) into a PPO policy, enabling the AI scheduler to inherit expert heuristics (like TZU) for faster and more stable learning.",
    "What is the difference between KGDRL and PPO": "PPO is a general RL algorithm that explores from scratch. KGDRL adds a knowledge-guided layer—encoding domain expertise into a knowledge graph and using KL-divergence constraints to keep policies reasonable. KGDRL outperforms PPO by 15-23% in emergency-order scenarios.",
    "What is wave allocation": "Wave Allocation clusters daily orders into time-window 'waves' and assigns them to zones/workstations. Proper wave design balances capacity, reduces cold-chain breakage risk, and improves vehicle loading rates.",
    "What temperature zones are supported": "The system supports 5 zones: Ambient (15-25°C), Cool (2-8°C), Cold (2-8°C), Frozen (-20°C), and Deep Frozen (-80°C). Each zone has independent capacity constraints and compliance checks.",
    "What is NSGA-II": "NSGA-II is a multi-objective genetic algorithm that finds the Pareto-optimal frontier across conflicting goals like cost, timeliness, and compliance. Users can select the strategy point that best matches their business preference.",
    "How do I upload my own data": "Click the 'Data Upload Hub' in the left sidebar to upload orders.csv, inventory.csv, etc. The system auto-validates columns and data types; once passed, you can view real-data analytics in Live Mode. (Pro feature)",
    "What is adaptive policy": "Adaptive Policy uses EWMA to forecast order arrival rates and dynamically adjusts wave capacity. When abnormal peaks are detected, the system auto-scales or triggers waves early to reduce backlog. (Pro feature)",
}


def _fuzzy_match(question: str, lang: str) -> Optional[str]:
    """Simple fuzzy match against FAQ database."""
    db = FAQ_DATABASE_ZH if lang == "zh" else FAQ_DATABASE_EN
    q_lower = question.lower().strip()
    for key, answer in db.items():
        if key.lower() in q_lower or q_lower in key.lower():
            return answer
    return None


def ask_faq(question: str, lang: str = "zh") -> str:
    """
    Answer a FAQ question.
    First tries cached answers; if no match, falls back to LLM.
    Standard Edition uses this primarily.
    """
    # 1. Try exact/fuzzy cache match
    cached = _fuzzy_match(question, lang)
    if cached:
        return cached

    # 2. Fallback to LLM
    system, user = render_prompt("copilot_faq", lang=lang, question=question)
    return chat_completion(user, task="copilot", lang=lang, system=system)


def ask_with_context(
    question: str,
    page_name: str,
    page_context: str,
    lang: str = "zh",
) -> str:
    """
    Answer a question with awareness of current page data.
    Professional Edition uses this for the global floating Copilot.
    """
    system, user = render_prompt(
        "copilot_context",
        lang=lang,
        question=question,
        page_name=page_name,
        page_context=page_context,
    )
    return chat_completion(user, task="copilot", lang=lang, system=system)


def stream_copilot(question: str, lang: str = "zh") -> str:
    """Stream a copilot response token-by-token (for UI typing effect)."""
    system, user = render_prompt("copilot_faq", lang=lang, question=question)
    yield from chat_completion_stream(user, task="copilot", system=system)
