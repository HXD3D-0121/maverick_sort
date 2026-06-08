# AI Tools Usage Review — Day 5: Hugging Face 大模型集成

**Date:** 2026-06-08  
**Scope:** 为标准版 (v7) 和专业版 (v5) 接入 Hugging Face AI 大模型能力  
**HF Token:** 配置于 `.env` 文件（已从 commit 中排除）  

---

## 一、目标与成果概览

### 1.1 设计目标
- 差异化大模型功能：标准版轻量够用，专业版深度闭环
- 全局可访问：在 sidebar 顶部放置可折叠的 AI Copilot，任何页面都能直接调用
- 优雅降级：API 不可用 → 本地模型 → 规则回退，三级容错
- 视觉美观：渐变色卡片设计，与现有暗色主题融合

### 1.2 交付成果

| 交付项 | 数量 | 说明 |
|--------|------|------|
| 新建核心模块 | 9 个文件 | `hf_integration/` 完整 LLM 调用封装 |
| 修改共享模块 | 4 个文件 | `shared.py`, `scheduling.py`, `operations.py`, `tech_showcase.py` |
| 新建入口文件 | 2 个文件 | `streamlit_app_v7.py` + `streamlit_app_pro_v5.py` |
| 依赖更新 | 1 个文件 | `requirements.txt` 新增 5 个包 |
| 环境配置 | 1 个文件 | `.env` 更新 HF Token |

---

## 二、架构设计

### 2.1 三级降级链

```
Tier 1: HF Inference API (Qwen2.5-7B-Instruct) — 在线，效果最好
    ↓ (网络故障/API限流)
Tier 2: Local transformers (Qwen2.5-1.5B-Instruct) — 离线，CPU可运行
    ↓ (依赖未安装)
Tier 3: Rule-based fallback — 预置模板文本，始终可用
```

### 2.2 模块结构

```
hf_integration/
├── __init__.py              # 包入口，导出公共API
├── config.py                # 模型配置、API密钥读取、可用性检测
├── client.py                # 统一LLM调用：chat_completion + stream
├── prompts.py               # 10组中英双语Prompt模板（dataclass封装）
├── insight_engine.py        # 决策自然语言解释（4种场景）
├── report_generator.py      # 自动报告摘要（What-If / 商业分析）
├── copilot.py               # 智能助手：FAQ缓存 + 上下文感知问答
├── alert_analyzer.py        # RAG根因分析（sentence-transformers + faiss）
└── demand_forecaster.py     # 时序预测（EWMA兜底，预留TimesFM接口）
```

---

## 三、功能差异化矩阵

### 3.1 标准版 v7.0（18页）

| 功能 | 位置 | 实现方式 |
|------|------|---------|
| AI Insight Engine | Algorithm Arena | benchmark结果生成中文策略结论 |
| AI Report Generator | What-If Scenario Lab | 对比结果自动生成执行摘要 |
| AI Insight Engine | SLA Analytics | 历史趋势数据AI解读 |
| 🤖 Sunergy Copilot | 全局Sidebar | FAQ问答模式（预置8个问题） |

### 3.2 专业版 v5.0（23页）

| 功能 | 位置 | 实现方式 |
|------|------|---------|
| AI Insight Engine | Algorithm Arena + Strategy Optimizer + Live Adaptive | 覆盖全部调度场景 |
| AI Report Generator | What-If Lab + Business Analysis | 一键生成投资者级报告 |
| AI Root Cause Analysis (RAG) | Alert Center | 基于上传数据构建轻量向量知识库 |
| AI Demand Forecasting | Data Center | 对上传orders.csv进行时序预测 |
| 🤖 Sunergy Copilot | 全局Sidebar | 上下文感知（结合当前页面数据） |

---

## 四、关键设计决策

### 决策1：模型选型
- **在线主模型**：`Qwen/Qwen2.5-7B-Instruct`（HF Inference API，中英双语极佳）
- **本地降级**：`Qwen/Qwen2.5-1.5B-Instruct`（1.5B可在CPU运行）
- **时序预留**：`google/timesfm-1.0-200m`（200M轻量，当前用EWMA兜底）

### 决策2：Copilot 交互设计
- **位置**：sidebar 顶部（品牌信息下方），无需滚动即可见
- **视觉**：蓝紫粉三色拉渐变卡片 + 紫色发光阴影 + 悬停放大效果
- **状态**：绿色"Online"/黄色"Offline"胶囊标签
- **交互**：折叠/展开按钮 + 4个快捷问题 + 自由输入 + 最近6轮历史

### 决策3：版本策略
- 保留 `streamlit_app_v6.py` 和 `streamlit_app_pro_v4.py` 不变
- 新建 `streamlit_app_v7.py` 和 `streamlit_app_pro_v5.py` 作为 AI 增强版
- 两个新版共享同一套 `page_modules/` 和 `hf_integration/`

---

## 五、Bug 修复记录

| 时间 | 问题 | 原因 | 修复 |
|------|------|------|------|
| 11:25 | huggingface_hub 未安装 | 环境缺少依赖 | `pip install` 安装全部包 |
| 11:26 | `is_llm_ready` 导入错误 | `__init__.py` 从错误模块导入 | 修正到 `config.py` |
| 11:36 | 渐变色框乱码 | Bash脚本 `>` 转义残留为 `>t;` | 全局替换 `>t;` → `>` |
| 11:37 | pro_v5 IndentationError | 旧Copilot块未完全删除 | 清理残留代码 |
| 11:39 | `use_container_width` 弃用警告 | Streamlit 1.58 规范变更 | 批量替换为 `width='stretch'` |

---

## 六、运行方式

```bash
# 安装依赖
pip install -r requirements.txt

# 标准版 v7.0（18页，AI Copilot + Insight + Report）
streamlit run streamlit_app_v7.py

# 专业版 v5.0（23页，全量HF AI功能）
streamlit run streamlit_app_pro_v5.py
```

---

## 七、环境依赖

```
huggingface_hub >= 0.23.0
transformers    >= 4.40.0
torch           >= 2.0.0
sentence-transformers >= 3.0.0
faiss-cpu       >= 1.8.0
```

---

## 八、文件变更清单

### 新增文件（Untracked）
- `hf_integration/__init__.py`
- `hf_integration/config.py`
- `hf_integration/client.py`
- `hf_integration/prompts.py`
- `hf_integration/insight_engine.py`
- `hf_integration/report_generator.py`
- `hf_integration/copilot.py`
- `hf_integration/alert_analyzer.py`
- `hf_integration/demand_forecaster.py`
- `streamlit_app_v7.py`
- `streamlit_app_pro_v5.py`

### 修改文件（Modified）
- `.env` — 更新 HF Token
- `requirements.txt` — 新增5个依赖
- `page_modules/shared.py` — 添加 `try_import_hf()`
- `page_modules/scheduling.py` — 注入 Insight Engine + Report Generator
- `page_modules/operations.py` — 注入 SLA Insight + Alert RAG
- `page_modules/tech_showcase.py` — 新增 `render_hf_copilot()`

---

> **备注**：本集成以"功能演示"为目标，非生产级稳定性。HF Inference API free tier 有速率限制，大规模使用建议升级为 HF Pro 或部署本地模型。
