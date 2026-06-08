"""
HF Integration — Alert Analyzer (Pro Edition)
===============================================
RAG-based root-cause analysis for uploaded alert data.
Lightweight implementation: sentence-transformers embeddings + faiss CPU index.

Usage:
    from hf_integration.alert_analyzer import AlertRAG, analyze_alert
    rag = AlertRAG()
    rag.index_historical(sla_df, tasks_df)
    result = analyze_alert(alert_row, rag, lang="zh")
"""

import warnings
from typing import List, Optional

import numpy as np
import pandas as pd

from .client import chat_completion
from .prompts import render_prompt


class AlertRAG:
    """Lightweight RAG for alert root-cause analysis."""

    def __init__(self, embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.embedding_model_name = embedding_model
        self._embedder = None
        self._index = None
        self._docs: List[str] = []
        self._meta: List[dict] = []

    def _load_embedder(self):
        if self._embedder is not None:
            return self._embedder
        try:
            from sentence_transformers import SentenceTransformer
            self._embedder = SentenceTransformer(self.embedding_model_name)
            return self._embedder
        except ImportError:
            warnings.warn("sentence-transformers not installed. RAG will use keyword fallback.")
            return None

    def index_historical(
        self,
        sla_df: Optional[pd.DataFrame] = None,
        tasks_df: Optional[pd.DataFrame] = None,
        alerts_df: Optional[pd.DataFrame] = None,
    ):
        """Build a knowledge base from historical SLA, task, and alert data."""
        embedder = self._load_embedder()
        docs = []
        meta = []

        if sla_df is not None and not sla_df.empty:
            for _, row in sla_df.head(200).iterrows():
                text = f"SLA记录：日期{row.get('date','')}, 准时率{row.get('on_time_rate','')}, " \
                       f"延误原因{row.get('delay_reason','')}, 区域{row.get('zone','')}."
                docs.append(text)
                meta.append({"type": "sla", "source": "sla_history"})

        if tasks_df is not None and not tasks_df.empty:
            for _, row in tasks_df.head(200).iterrows():
                text = f"工单记录：任务{row.get('task_id','')}, 状态{row.get('status','')}, " \
                       f"耗时{row.get('duration_min','')}分钟, 类型{row.get('task_type','')}."
                docs.append(text)
                meta.append({"type": "task", "source": "tasks"})

        if alerts_df is not None and not alerts_df.empty:
            for _, row in alerts_df.head(200).iterrows():
                text = f"历史告警：类型{row.get('alert_type','')}, 级别{row.get('severity','')}, " \
                       f"描述{row.get('description','')}, 处置{row.get('resolution','')}."
                docs.append(text)
                meta.append({"type": "alert", "source": "alerts"})

        self._docs = docs
        self._meta = meta

        if embedder and docs:
            embeddings = embedder.encode(docs, convert_to_numpy=True, show_progress_bar=False)
            try:
                import faiss
                dim = embeddings.shape[1]
                self._index = faiss.IndexFlatIP(dim)
                faiss.normalize_L2(embeddings)
                self._index.add(embeddings)
            except ImportError:
                warnings.warn("faiss not installed. Using brute-force cosine fallback.")
                self._index = "brute_force"
                self._embeddings = embeddings

    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        """Retrieve top-k similar historical cases."""
        if not self._docs:
            return []

        embedder = self._load_embedder()
        if embedder is None:
            # Keyword fallback
            return [d for d in self._docs if any(w in d for w in query.split()[:3])][:top_k]

        q_emb = embedder.encode([query], convert_to_numpy=True)

        if self._index == "brute_force":
            # Brute-force cosine similarity
            norms = np.linalg.norm(self._embeddings, axis=1) * np.linalg.norm(q_emb, axis=1)
            scores = np.dot(self._embeddings, q_emb.T).flatten() / (norms + 1e-8)
            top_idx = np.argsort(scores)[::-1][:top_k]
        else:
            import faiss
            faiss.normalize_L2(q_emb)
            scores, top_idx = self._index.search(q_emb, top_k)
            top_idx = top_idx.flatten()

        return [self._docs[i] for i in top_idx if i < len(self._docs)]


def analyze_alert(
    alert_id: str,
    alert_type: str,
    severity: str,
    alert_time: str,
    zone: str,
    description: str,
    rag: Optional[AlertRAG] = None,
    lang: str = "zh",
) -> str:
    """Analyze a single alert with optional RAG augmentation."""
    similar_cases = "无历史相似案例。"
    if rag is not None:
        cases = rag.retrieve(f"{alert_type} {description}", top_k=3)
        if cases:
            similar_cases = "\n".join(f"- {c}" for c in cases)

    system, user = render_prompt(
        "alert_analyze",
        lang=lang,
        alert_id=alert_id,
        alert_type=alert_type,
        severity=severity,
        alert_time=alert_time,
        zone=zone,
        description=description,
        similar_cases=similar_cases,
    )
    return chat_completion(user, task="alert", lang=lang, system=system)


def batch_analyze_alerts(alerts_df: pd.DataFrame, rag: Optional[AlertRAG] = None, lang: str = "zh") -> pd.DataFrame:
    """Analyze a batch of alerts and append 'ai_analysis' column."""
    results = []
    for _, row in alerts_df.iterrows():
        analysis = analyze_alert(
            alert_id=str(row.get("alert_id", "")),
            alert_type=str(row.get("alert_type", "")),
            severity=str(row.get("severity", "")),
            alert_time=str(row.get("alert_time", "")),
            zone=str(row.get("zone", "")),
            description=str(row.get("description", "")),
            rag=rag,
            lang=lang,
        )
        results.append(analysis)
    alerts_df = alerts_df.copy()
    alerts_df["ai_analysis"] = results
    return alerts_df
