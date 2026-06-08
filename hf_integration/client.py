"""
HF Integration — Unified LLM Client
====================================
Three-tier invocation:
  1. Hugging Face Inference API (serverless, fastest)
  2. Local pipeline via transformers (offline, CPU-friendly with 1.5B models)
  3. Rule-based mock (always works, returns template text)

Usage:
    from hf_integration import chat_completion, is_llm_ready
    if is_llm_ready():
        text = chat_completion(prompt, task="insight", lang="zh")
"""

import time
import warnings
from typing import Optional, Iterator

from .config import (
    HF_AVAILABLE,
    LOCAL_MODEL_AVAILABLE,
    HF_TOKEN,
    DEFAULT_MODEL_API,
    DEFAULT_MODEL_LOCAL,
    get_llm_config,
    get_fallback_message,
)

# =============================================================================
# Lazy imports & singleton caches
# =============================================================================

_local_pipeline = None
_local_model_name: Optional[str] = None


def _load_local_pipeline(model_name: str = DEFAULT_MODEL_LOCAL):
    """Lazy-load a local transformers pipeline. Cached singleton."""
    global _local_pipeline, _local_model_name
    if _local_pipeline is not None and _local_model_name == model_name:
        return _local_pipeline

    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

        device = 0 if torch.cuda.is_available() else -1
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            trust_remote_code=True,
            torch_dtype=torch.float16 if device == 0 else torch.float32,
            device_map="auto" if device == 0 else None,
        )
        _local_pipeline = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            device=device,
        )
        _local_model_name = model_name
        return _local_pipeline
    except Exception as e:
        warnings.warn(f"Failed to load local model {model_name}: {e}")
        return None


def _call_hf_api(
    messages: list,
    model: str = DEFAULT_MODEL_API,
    max_tokens: int = 256,
    temperature: float = 0.3,
    top_p: float = 0.9,
    stream: bool = False,
) -> str:
    """Call Hugging Face Inference API (chat completion style)."""
    if not HF_TOKEN:
        raise RuntimeError("HF_TOKEN not available.")

    from huggingface_hub import InferenceClient

    client = InferenceClient(token=HF_TOKEN, timeout=60)

    if stream:
        # Return generator
        return client.chat_completion(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stream=True,
        )

    response = client.chat_completion(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        stream=False,
    )
    return response.choices[0].message.content


def _call_local(
    prompt_text: str,
    model: str = DEFAULT_MODEL_LOCAL,
    max_tokens: int = 256,
    temperature: float = 0.3,
) -> str:
    """Call local transformers pipeline."""
    pipe = _load_local_pipeline(model)
    if pipe is None:
        raise RuntimeError("Local model pipeline unavailable.")

    outputs = pipe(
        prompt_text,
        max_new_tokens=max_tokens,
        temperature=temperature,
        do_sample=temperature > 0,
        return_full_text=False,
    )
    return outputs[0]["generated_text"].strip()


def _build_chat_messages(prompt_text: str, system: Optional[str] = None) -> list:
    """Build HF chat-completion message list."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt_text})
    return messages


def _format_prompt_qwen(messages: list) -> str:
    """Format messages into Qwen chat template string for local inference."""
    # Qwen2.5-Instruct format
    parts = []
    for m in messages:
        role = m["role"]
        content = m["content"]
        if role == "system":
            parts.append(f"<|im_start|>system\n{content}<|im_end|>")
        elif role == "user":
            parts.append(f"<|im_start|>user\n{content}<|im_end|>")
        elif role == "assistant":
            parts.append(f"<|im_start|>assistant\n{content}<|im_end|>")
    parts.append("<|im_start|>assistant\n")
    return "\n".join(parts)


# =============================================================================
# Public API
# =============================================================================

def chat_completion(
    prompt: str,
    *,
    task: str = "insight",
    lang: str = "zh",
    system: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
) -> str:
    """
    Generate a text completion with automatic backend selection.

    Args:
        prompt: The user prompt text.
        task: One of insight, report, copilot, alert, forecast (affects max_tokens/temp).
        lang: "zh" or "en" — used for fallback messages.
        system: Optional system prompt.
        max_tokens, temperature: Override defaults.

    Returns:
        Generated text string, or a fallback message if all backends fail.
    """
    cfg = get_llm_config(task)
    max_tokens = max_tokens or cfg["max_tokens"]
    temperature = temperature if temperature is not None else cfg["temperature"]

    # ── Tier 1: HF Inference API ─────────────────────────────────────────────
    if HF_AVAILABLE and HF_TOKEN:
        try:
            messages = _build_chat_messages(prompt, system=system)
            return _call_hf_api(
                messages,
                model=DEFAULT_MODEL_API,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        except Exception as e:
            warnings.warn(f"HF API call failed: {e}. Falling back to local model.")

    # ── Tier 2: Local transformers ───────────────────────────────────────────
    if LOCAL_MODEL_AVAILABLE:
        try:
            messages = _build_chat_messages(prompt, system=system)
            prompt_text = _format_prompt_qwen(messages)
            return _call_local(
                prompt_text,
                model=DEFAULT_MODEL_LOCAL,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        except Exception as e:
            warnings.warn(f"Local model call failed: {e}. Falling back to rule-based mock.")

    # ── Tier 3: Rule-based fallback ──────────────────────────────────────────
    return get_fallback_message(task, lang)


def chat_completion_stream(
    prompt: str,
    *,
    task: str = "copilot",
    system: Optional[str] = None,
) -> Iterator[str]:
    """
    Stream text completion token-by-token. Only works with HF Inference API.
    Falls back to yielding the full string at once for local models.
    """
    cfg = get_llm_config(task)

    if HF_AVAILABLE and HF_TOKEN:
        try:
            messages = _build_chat_messages(prompt, system=system)
            stream = _call_hf_api(
                messages,
                model=DEFAULT_MODEL_API,
                max_tokens=cfg["max_tokens"],
                temperature=cfg["temperature"],
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
            return
        except Exception as e:
            warnings.warn(f"HF API stream failed: {e}. Falling back to non-stream.")

    # Non-stream fallback
    text = chat_completion(prompt, task=task, system=system)
    # Simulate streaming by yielding characters with tiny delay
    for char in text:
        yield char
        time.sleep(0.005)
