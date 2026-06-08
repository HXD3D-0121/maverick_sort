# Sunergy Pharma — Hugging Face 大模型集成技术路径

> **集成日期**：2026/06/08（Day 5）  
> **项目分支**：`Code-for-Deep-Reinforcement-Learning`  
> **核心目标**：将"演示级 AI 标签"升级为"功能级 AI 生产力"，实现自然语言决策解释、RAG 根因分析、智能 Copilot 等能力。

---

## 一、整体架构：三级降级链

```
Tier 1: HF Inference API  (Qwen2.5-7B-Instruct)
    ↓ 网络故障 / API 限流
Tier 2: Local transformers (Qwen2.5-1.5B-Instruct, CPU 可跑)
    ↓ 依赖未安装
Tier 3: Rule-based fallback (预置模板文本，始终可用)
```

**设计哲学**：任何页面调用 AI 功能时，用户永远能看到输出，不会因为网络或环境问题白屏。

---

## 二、模块结构：`hf_integration/` 包（9 个文件）

| 文件 | 职责 | 代码量 |
|------|------|--------|
| `__init__.py` | 包入口，统一暴露 `chat_completion`, `is_llm_ready`, `render_prompt` 等 API | ~50 行 |
| `config.py` | API Key 解析（st.secrets → env → .env 文件三级探测）、依赖可用性检测、模型注册表、任务级超参配置 | ~120 行 |
| `client.py` | **核心**：统一 LLM 调用封装。含 `_call_hf_api()`、`_call_local()`、`_format_prompt_qwen()`、流式输出 `chat_completion_stream()` | ~250 行 |
| `prompts.py` | 10 组中英双语 PromptTemplate 数据类，支持 `{var}` 格式化替换 | ~320 行 |
| `insight_engine.py` | 决策自然语言解释（Algorithm Arena / Strategy Optimizer / Live Adaptive / SLA Trend / 3D Command Center 5 个场景） | ~140 行 |
| `report_generator.py` | 自动报告摘要（What-If 对比摘要 + 商业分析全报告） | ~70 行 |
| `copilot.py` | 智能助手：FAQ 缓存模式（标准版）+ 上下文感知模式（Pro 版） | ~95 行 |
| `alert_analyzer.py` | **Pro 版**：轻量 RAG 根因分析（sentence-transformers 嵌入 + faiss/brute-force 检索） | ~170 行 |
| `demand_forecaster.py` | **Pro 版**：时序预测（预留 TimesFM，当前用 EWMA 兜底 + LLM 解读） | ~145 行 |

---

## 三、关键实现细节

### 3.1 API Key 解析链（`config.py`）

密钥解析采用"探测链"而非单点硬编码：

```python
# 优先级：Streamlit secrets > 环境变量 > .env 文件
HF_TOKEN = st.secrets.get("HF_TOKEN")           # 生产/Cloud
HF_TOKEN = os.environ.get("HF_TOKEN")           # 本地开发
HF_TOKEN = parse_dot_env("HF_TOKEN=")           # 项目根目录 .env
```

**优点**：同一套代码在本地开发、Streamlit Cloud、Docker 容器三种环境无缝切换。

### 3.2 统一 LLM 客户端（`client.py`）

核心函数签名：

```python
def chat_completion(
    prompt: str,
    *,
    task: str = "insight",      # 控制 max_tokens / temperature
    lang: str = "zh",
    system: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
) -> str
```

**内部三选逻辑**：

```python
if HF_AVAILABLE and HF_TOKEN:
    # Tier 1: HF Inference API（chat_completion 格式）
    return _call_hf_api(messages, model="Qwen/Qwen2.5-7B-Instruct")
elif LOCAL_MODEL_AVAILABLE:
    # Tier 2: 本地 transformers pipeline
    prompt_text = _format_prompt_qwen(messages)   # Qwen2.5 chat template
    return _call_local(prompt_text, model="Qwen/Qwen2.5-1.5B-Instruct")
else:
    # Tier 3: 预置回退文案
    return get_fallback_message(task, lang)
```

**本地模型加载策略**：Lazy Singleton + 设备自动探测（CUDA → CPU），`torch.float16` / `float32` 自动适配。

### 3.3 Prompt 模板设计（`prompts.py`）

采用 `dataclass` 封装双语模板：

```python
@dataclass
class PromptTemplate:
    name: str
    system_zh: str
    system_en: str
    user_zh: str
    user_en: str

    def render(self, lang: str = "zh", **kwargs) -> tuple[Optional[str], str]:
```

**覆盖的 10 个场景**：

| 类别 | 模板名 | 用途 |
|------|--------|------|
| Insight | `insight_algorithm_arena` | benchmark 结果 → 中文策略结论 |
| Insight | `insight_strategy_optimizer` | NSGA-II 帕累托点 → 业务解释 |
| Insight | `insight_live_adaptive` | 容量调整 → 运营解读 |
| Insight | `insight_sla_trend` | SLA 趋势 → 问题洞察 |
| Report | `report_what_if` | What-If 对比 → 执行摘要 |
| Report | `report_business_full` | 财务模型 → 投资者级报告 |
| Copilot | `copilot_faq` | 通用 FAQ 问答 |
| Copilot | `copilot_context` | 结合当前页面数据的上下文回答 |
| Alert | `alert_analyze` | 告警 + 历史案例 → 根因 + 建议 |
| Forecast | `forecast_summary` | 预测结果 → 运营建议 |

**Prompt 工程原则**：每条都强制字数限制（30~150 字），防止模型啰嗦；中文优先，英文对齐。

### 3.4 RAG 轻量实现（`alert_analyzer.py`）

Pro 版功能，不依赖重量级框架：

```python
class AlertRAG:
    def __init__(self, embedding_model="sentence-transformers/all-MiniLM-L6-v2"):
        # 支持 faiss（快）或 brute-force（无额外依赖）
        self._index = None  # faiss.IndexFlatIP or "brute_force"
```

**数据向量化流程**：
1. 从 SLA / tasks / alerts DataFrame 抽取文本摘要
2. `SentenceTransformer.encode()` 生成嵌入
3. `faiss.IndexFlatIP` 构建索引（faiss 不可用时回退 brute-force cosine）
4. 告警发生时，检索 Top-3 相似历史案例注入 Prompt

### 3.5 Copilot 双模式设计（`copilot.py`）

**标准版**：预置 8 条 FAQ（中英文），模糊匹配 → 命中则直接返回，未命中再走 LLM。零 Token 消耗解决 80% 常见问题。

**Pro 版**：上下文感知，调用时传入当前页面名 + 页面关键数据，LLM 基于具体数字回答。

### 3.6 需求预测（`demand_forecaster.py`）

当前架构预留了 `google/timesfm-1.0-200m`，实际先用 EWMA 兜底：

```python
def predict(orders_df, date_col="order_date", value_col="quantity", horizon=7):
    # 自动列名兼容（支持 qty / amount / 数量 等别名）
    # EWMA 预测 + 趋势外推 + 正态噪声
    # 结果交给 LLM 生成自然语言解读
```

---

## 四、产品差异化矩阵

| 功能 | 标准版 v7.0 | 专业版 v5.0 |
|------|------------|------------|
| AI Insight Engine | Algorithm Arena / SLA Analytics | + Strategy Optimizer / Live Adaptive / 3D Command Center |
| AI Report Generator | What-If Lab 摘要 | + Business Analysis 全报告 |
| AI Root Cause Analysis (RAG) | ❌ | Alert Center 上传数据后可用 |
| AI Demand Forecasting | ❌ | Data Center 上传 orders.csv 后可用 |
| Sunergy Copilot | FAQ 模式（预置 8 问） | 上下文感知（结合当前页面数据） |

---

## 五、Streamlit 集成方式

### 5.1 全局 Copilot（Sidebar）

- **位置**：sidebar 品牌信息下方，无需滚动即可见
- **视觉**：蓝紫粉三色拉渐变卡片 + 紫色发光阴影 + 悬停放大
- **状态标签**：绿色"Online" / 黄色"Offline"胶囊
- **交互**：折叠/展开 + 4 个快捷问题 + 自由输入 + 最近 6 轮历史

### 5.2 各页面调用点

- **Algorithm Arena** → `insight_engine.explain_benchmark()`
- **Strategy Optimizer** → `insight_engine.explain_pareto()`
- **Live Adaptive** → `insight_engine.explain_adaptive_adjustment()`
- **SLA Analytics** → `insight_engine.explain_sla_trend()`
- **Alert Center** → `alert_analyzer.analyze_alert()`（Pro）
- **Data Center** → `demand_forecaster.predict()` + `summarize()`（Pro）

---

## 六、依赖配置（`requirements.txt` 新增）

```
huggingface_hub>=0.23.0
transformers>=4.40.0
torch>=2.0.0
sentence-transformers>=3.0.0   # Pro 版 RAG 用
faiss-cpu>=1.8.0               # Pro 版向量检索用
```

---

## 七、踩坑记录（Day 5 当天）

| 时间 | 问题 | 根因 | 修复 |
|------|------|------|------|
| 11:25 | `huggingface_hub` 未安装 | 环境缺少依赖 | `pip install -r requirements.txt` |
| 11:26 | `is_llm_ready` 导入错误 | `__init__.py` 从错误模块导入 | 修正到 `config.py` |
| 11:36 | 渐变色框乱码 | Bash `>` 转义残留为 `>t;` | 全局替换 `>t;` → `>` |
| 11:37 | `pro_v5` IndentationError | 旧 Copilot 块未完全删除 | 清理残留代码 |
| 11:39 | `use_container_width` 弃用警告 | Streamlit 1.58 规范变更 | 批量替换为 `width='stretch'` |

---

## 八、运行方式

```bash
# 安装依赖
pip install -r requirements.txt

# 标准版 v7.0（18 页，AI Insight + FAQ Copilot）
streamlit run streamlit_app_v7.py

# 专业版 v5.0（23 页，全功能 AI + RAG + 预测）
streamlit run streamlit_app_pro_v5.py
```

---

## 九、Git 提交信息

```
Day 5: Hugging Face AI Integration — v7/v5 + hf_integration modules + Copilot sidebar

新增 11 个文件，修改 5 个文件（shared.py, scheduling.py, operations.py, tech_showcase.py, requirements.txt）
```

---

> **文档版本**：v1.0  
> **整理时间**：2026/06/08  
> **适用场景**：技术分享、团队内部交接、朋友借鉴参考
