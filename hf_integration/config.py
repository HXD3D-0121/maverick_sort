"""
HF Integration — Configuration & Availability Detection
========================================================
Three-tier fallback:
  1. HF Inference API  (serverless, requires HF_TOKEN + internet)
  2. Local transformers (CPU/GPU, requires torch+transformers)
  3. Rule-based mock    (always available, returns template text)
"""

import os
import warnings
import importlib.util

# =============================================================================
# API Key resolution order: st.secrets > env var > .env file > None
# =============================================================================

HF_TOKEN = None

# 1. Try Streamlit secrets (production / Streamlit Cloud)
try:
    import streamlit as st
    HF_TOKEN = st.secrets.get("HF_TOKEN") or st.secrets.get("huggingface", {}).get("token")
except Exception:
    pass

# 2. Try environment variable
if not HF_TOKEN:
    HF_TOKEN = os.environ.get("HF_TOKEN")

# 3. Try .env file (simple key=value or "Key: value" format)
if not HF_TOKEN:
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("HF_TOKEN="):
                    HF_TOKEN = line.split("=", 1)[1].strip().strip('"')
                elif "hf_" in line and len(line) > 20:
                    # heuristic: extract any hf_... token from the line
                    for part in line.split():
                        if part.startswith("hf_") and len(part) > 20:
                            HF_TOKEN = part.strip()
                            break

# =============================================================================
# Dependency availability flags
# =============================================================================

HF_AVAILABLE = False
LOCAL_MODEL_AVAILABLE = False

# Hugging Face Hub (for Inference API)
try:
    import huggingface_hub  # noqa: F401

    HF_AVAILABLE = True
except ImportError:
    warnings.warn("huggingface_hub not installed. HF Inference API unavailable.")

# Local transformers — use find_spec to avoid triggering transformers'
# internal model-registry scan (which crashes on missing torchvision).
try:
    _has_transformers = importlib.util.find_spec("transformers") is not None
    _has_torch = importlib.util.find_spec("torch") is not None
    if _has_transformers and _has_torch:
        # Only import transformers when BOTH are present; this still triggers
        # the scan, but at least we know torch is there so torchvision is
        # likely installed too. If the scan still fails, we catch it below.
        import transformers  # noqa: F401
        import torch  # noqa: F401

        LOCAL_MODEL_AVAILABLE = True
    else:
        warnings.warn(
            "transformers/torch not installed. Local model fallback unavailable."
        )
except Exception as _e:
    warnings.warn(
        f"transformers import failed (likely missing torchvision): {_e}. "
        "Local model fallback unavailable."
    )

# =============================================================================
# Model registry
# =============================================================================

DEFAULT_MODEL_API = "Qwen/Qwen2.5-7B-Instruct"      # serverless inference
DEFAULT_MODEL_LOCAL = "Qwen/Qwen2.5-1.5B-Instruct"   # CPU-friendly fallback
TIMESERIES_MODEL = "google/timesfm-1.0-200m"          # time-series forecasting
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # RAG embeddings

# Max tokens for different use-cases
MAX_TOKENS = {
    "insight": 256,
    "report": 512,
    "copilot": 512,
    "alert": 384,
    "forecast": 128,
}


def get_llm_config(task: str = "insight") -> dict:
    """Return a config dict for the given task type."""
    return {
        "model_api": DEFAULT_MODEL_API,
        "model_local": DEFAULT_MODEL_LOCAL,
        "max_tokens": MAX_TOKENS.get(task, 256),
        "temperature": 0.3 if task in ("insight", "forecast") else 0.7,
        "top_p": 0.9,
    }


def is_llm_ready() -> bool:
    """Return True if at least one LLM backend is available."""
    return HF_AVAILABLE or LOCAL_MODEL_AVAILABLE


def get_fallback_message(task: str = "insight", lang: str = "zh") -> str:
    """Return a graceful fallback message when no LLM is available."""
    messages = {
        "zh": {
            "insight": "🤖 AI 分析服务暂不可用。请检查网络连接或安装 transformers 库以启用本地模型。",
            "report": "🤖 报告生成服务暂不可用。请检查环境配置。",
            "copilot": "🤖 AI 助手暂不可用。您可以先浏览页面上的预置说明。",
            "alert": "🤖 异常分析服务暂不可用。",
            "forecast": "🤖 需求预测服务暂不可用。",
        },
        "en": {
            "insight": "🤖 AI analysis is temporarily unavailable. Check your network or install transformers for local fallback.",
            "report": "🤖 Report generation is temporarily unavailable.",
            "copilot": "🤖 AI Copilot is temporarily unavailable. Browse the on-page instructions instead.",
            "alert": "🤖 Alert analysis is temporarily unavailable.",
            "forecast": "🤖 Demand forecasting is temporarily unavailable.",
        },
    }
    return messages.get(lang, messages["zh"]).get(task, messages["zh"]["insight"])
