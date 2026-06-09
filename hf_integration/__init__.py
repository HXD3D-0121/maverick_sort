"""
Maverick-SORT — Hugging Face Integration Module
=================================================
Unified LLM client with graceful degradation:
  HF Inference API (primary) → Local transformers (fallback) → Rule-based (last resort)

Modules:
  - config:     Model configs, API keys, availability flags
  - client:     Unified LLM call wrapper
  - prompts:    Bilingual (CN/EN) prompt templates
  - insight_engine:    Natural-language decision explanations
  - report_generator:  Auto-report summarization
  - copilot:           AI assistant (FAQ + context-aware)
  - alert_analyzer:    RAG-based root-cause analysis (Pro only)
  - demand_forecaster: Time-series forecasting via HF models (Pro only)
"""

from .config import (
    HF_AVAILABLE,
    LOCAL_MODEL_AVAILABLE,
    HF_TOKEN,
    DEFAULT_MODEL_API,
    DEFAULT_MODEL_LOCAL,
    TIMESERIES_MODEL,
    EMBEDDING_MODEL,
    get_llm_config,
    is_llm_ready,
)
from .client import (
    chat_completion,
    chat_completion_stream,
)
from .prompts import (
    render_prompt,
    PromptTemplate,
)

__all__ = [
    "HF_AVAILABLE",
    "LOCAL_MODEL_AVAILABLE",
    "HF_TOKEN",
    "DEFAULT_MODEL_API",
    "DEFAULT_MODEL_LOCAL",
    "TIMESERIES_MODEL",
    "EMBEDDING_MODEL",
    "get_llm_config",
    "chat_completion",
    "chat_completion_stream",
    "is_llm_ready",
    "render_prompt",
    "PromptTemplate",
]
