# Sunergy Pharma — 产品审查与演示指南

> **文档性质**：LLM 功能差异化审查 + 企业汇报演示脚本  
> **适用版本**：Essential v7.0（标准版）+ Professional v5.0（专业版）  
> **更新日期**：2026/06/08

---

## 一、LLM 调用权限差异化矩阵

| AI 功能模块 | 标准版 v7 | 专业版 pro_v5 | 差异说明 |
|------------|----------|--------------|---------|
| **Sidebar Copilot** | ✅ FAQ 问答 | ✅ FAQ 问答 | 两版本代码相同 |
| **AI Copilot 页面** | ✅ FAQ 页面 | ✅ FAQ 页面 | 两版本代码相同 |
| **Algorithm Arena** | ✅ `explain_benchmark` | ✅ `explain_benchmark` | 自动生成算法对比结论 |
| **Scenario Simulator** | ✅ `summarize_what_if` | ✅ `summarize_what_if` | 自动生成 What-If 报告 |
| **SLA Analytics** | ✅ `explain_sla_trend` | ✅ `explain_sla_trend` | 自动解读 SLA 趋势 |
| **Alert Center** | ✅ `analyze_alert` | ✅ `analyze_alert` | RAG 根因分析 |
| **Strategy Optimizer** | ❌ | ✅ `explain_pareto` | **Pro 专属**：帕累托策略解释 |
| **Live Adaptive** | ❌ | ✅ `explain_adaptive_adjustment` | **Pro 专属**：自适应调整解读 |
| **Data Center** | ❌ | ✅ `demand_forecaster` | **Pro 专属**：AI 需求预测 |
| **Command Center** | ❌ | ✅ `explain_3d_command_center` | **Pro 专属**：3D 战术解读 |
| **Business Analysis** | ❌ | ✅ `generate_business_report` | **Pro 专属**：投资者级报告 |

**核心差异总结**：
- **标准版**：6 个 AI 功能点，覆盖日常运营辅助
- **专业版**：10 个 AI 功能点，在标准版基础上增加**预测性 AI**和**深度策略 AI**

---

## 二、Copilot 交互修复记录

本次迭代对 Copilot 进行了以下修复，两版本同步更新：

| 修复项 | 修复前 | 修复后 |
|--------|--------|--------|
| 快捷问题按钮调用路径 | `ask_with_context()`（LLM 瞎猜） | `ask_faq()`（命中预设缓存） |
| 自由输入调用路径 | `ask_with_context()`（无上下文） | `ask_faq()`（FAQ 缓存 + LLM fallback） |
| `_fuzzy_match()` 匹配逻辑 | 死板整句包含 | 新增关键词触发映射（`nsga`/`kgdrl`/`adaptive` 等） |
| 输入框 rerun 循环 | 无清空 → 死循环 | `del session_state` → 单次触发 |
| 消息渲染顺序 | 历史在上、输入在下 | 输入在上、历史在下（回复向下生长） |
| 离线提示 | 笼统文字 | 显示 `hf['msg']` 具体原因 |

---

## 三、企业汇报演示脚本（中文）

### 第一步：打开标准版 v7（展示基础 AI 能力）

> "这是 **Essential 标准版**，面向中小仓库。AI 能力覆盖日常运营决策辅助。"

**演示动作**：
1. 侧边栏点击 **"🤖 Sunergy Copilot"** → 输入 `What is KGDRL?` → 展示秒回预设答案
2. 进入 **Algorithm Arena** → 点击任意 benchmark 对比 → 页面底部自动生成 AI 策略结论（绿色高亮）
3. 进入 **Scenario Simulator** → 运行一个 What-If 场景 → 自动生成 AI 执行摘要

**话术**：
> "标准版已经内置了 6 个 AI 决策辅助点：Copilot 问答、算法结论、What-If 报告、SLA 洞察、告警分析。这些都是开箱即用的。"

### 第二步：切换到专业版 pro_v5（展示进阶 AI 能力）

> "这是 **Pro 专业版**，面向中大型仓库和集团客户。在标准版基础上，增加了**预测性 AI**和**深度策略 AI**。"

**演示动作**：
1. 进入 **Strategy Optimizer** → 运行 NSGA-II → 点击某个帕累托点 → 展示 AI 自动解释"这个策略点为什么适合成本优先场景"
2. 进入 **Data Center** → 上传 orders.csv → 点击 AI Forecast → 展示未来 7 天需求预测 + AI 自然语言解读
3. 进入 **Live Adaptive** → 触发一次容量调整 → 展示 AI 自动解读"为什么系统在这个时间点扩容"

**话术**：
> "Pro 版新增了 4 个深度 AI 功能：策略优化解释、实时自适应解读、需求预测、3D 战术解读。这些不是通用聊天机器人，而是**嵌入在业务流程中的领域 AI**——每一个结论都基于实时计算数据。"

### 第三步：差异化总结（给负责人的关键信息）

| 维度 | 标准版 | 专业版 |
|------|--------|--------|
| AI 数量 | 6 个功能点 | 10 个功能点 |
| AI 深度 | 解释已有结果 | **预测未来** + 解释策略 |
| 适用场景 | 日常运营辅助 | 集团级战略决策 |
| 定价 | ¥2,999/仓/月 | ¥8,999/仓/月 |

---

## 四、调用 LLM 的必要文件清单

以下文件必须完整提交，否则 AI 功能无法工作：

```
hf_integration/
├── __init__.py              # 包入口
├── config.py                # API 密钥解析、模型配置
├── client.py                # 统一 LLM 客户端（三级降级）
├── prompts.py               # 10 组中英双语 Prompt 模板
├── insight_engine.py        # 决策自然语言解释（5 个场景）
├── report_generator.py      # 自动报告摘要
├── copilot.py               # 智能助手（FAQ + 关键词触发）
├── alert_analyzer.py        # RAG 根因分析
└── demand_forecaster.py     # 时序预测

page_modules/shared.py         # try_import_hf() 统一导入封装
streamlit_app_pro_v5.py       # Pro 版入口（含 Data Center、Strategy Optimizer 等）
streamlit_app_v7.py           # 标准版入口
requirements.txt              # 必须包含 huggingface_hub、transformers、torch、plotly
```

---

## 五、启动方式

```bash
# 标准版
.venv\Scripts\streamlit.exe run streamlit_app_v7.py

# 专业版
.venv\Scripts\streamlit.exe run streamlit_app_pro_v5.py

# 或双击运行
run_app.bat
```

---

> **文档版本**：v1.0  
> **最后更新**：2026/06/08
