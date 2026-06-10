# Copilot 测试提示词清单

> 用途：验证 FAQ 缓存命中、LLM fallback、关键词触发是否正常
> 测试方法：在 Copilot 输入框中逐条输入，观察回复是否准确

---

## 第一组：FAQ 缓存命中测试（应该秒回，不调用 LLM）

这些问题的答案应该来自预设缓存，回复速度快（无网络延迟），内容准确。

| # | 输入 | 期望答案特征 |
|---|------|-------------|
| 1 | `What is KGDRL?` | 提到 Knowledge Graph、GAT、PPO、TZU 启发式 |
| 2 | `Explain NSGA-II` | 提到非支配排序、Pareto 最优前沿、多目标优化 |
| 3 | `Adaptive policy?` | 提到 EWMA、订单到达率预测、动态调整波次容量 |
| 4 | `Upload my data?` | 提到 Data Upload Hub、orders.csv、验证列名 |
| 5 | `What is wave allocation` | 提到 time-window waves、zones/workstations、冷链 |
| 6 | `KGDRL vs PPO` | 提到知识引导层、KL 散度、15-23% 提升 |
| 7 | `Temperature zones` | 列出 Ambient/Cool/Cold/Frozen/Deep Frozen 五个温区 |
| 8 | `TZU and FCFS difference` | 提到 TZU = 温度-紧急度-单位价值、FCFS = 先到先服务 |

**✅ 通过标准**：回复内容与上表"期望特征"一致，不是通用套话。

---

## 第二组：关键词触发测试（变体输入，应该命中缓存）

这些输入和预设 key 不完全一致，但包含关键词，应该通过 `_fuzzy_match()` 的关键词映射命中缓存。

| # | 输入 | 应该匹配到的预设问题 |
|---|------|---------------------|
| 9 | `Tell me about NSGA` | What is NSGA-II |
| 10 | `How does KGDRL work` | What is KGDRL |
| 11 | `wave assignment` | What is wave allocation |
| 12 | `cold chain zones` | What temperature zones are supported |
| 13 | `how to upload csv` | How do I upload my own data |
| 14 | `dynamic wave capacity` | What is adaptive policy |

**✅ 通过标准**：回复内容与对应的预设答案一致。

---

## 第三组：LLM Fallback 测试（FAQ 未命中，走千问模型）

这些问题不在 FAQ 缓存中，会调用 Qwen2.5-7B 生成回答。需要联网（HF_TOKEN 有效）。

| # | 输入 | 期望回答特征 |
|---|------|-------------|
| 15 | `What can I do with Maverick-SORT?` | 介绍系统功能（调度优化、波次分配、What-if 模拟等），不是 "I don't know" |
| 16 | `How does the system save money?` | 提到降低拣货距离、减少人力成本、优化波次 |
| 17 | `What is the pricing?` | 提到 Essential ¥2,999、Pro ¥8,999（或类似商业信息） |
| 18 | `Who is the target customer?` | 提到医药流通企业、仓储物流中心 |
| 19 | `Summarize the project in one sentence` | 一句概括：医药智能波次分配 + KGDRL + 多目标优化 |

**✅ 通过标准**：回答体现 Maverick-SORT 项目知识，不是通用 Wikipedia 式回答。

---

## 第四组：边界测试

| # | 输入 | 期望行为 |
|---|------|---------|
| 20 | （空输入，直接回车） | 不触发任何回复，输入框保持空 |
| 21 | `???` | 走 LLM fallback，给出礼貌回应或请求澄清 |
| 22 | `hello` | 走 LLM fallback，Maverick Copilot 自我介绍 |
| 23 | `什么是KGDRL`（中文） | 如果系统支持中文，返回中文预设答案；如不支持，走英文 fallback |

---

## 第五组：Stress 测试（连续对话）

快速连续输入以下问题，验证是否出现重复回复或页面卡死：

1. `What is KGDRL?`
2. `Explain NSGA-II`
3. `Adaptive policy?`
4. `Upload my data?`
5. `How does the system save money?`

**✅ 通过标准**：每条回复只出现一次，页面不持续刷新，6 条历史记录正确显示。

---

## 第六组：差异化功能演示提问（标准版 vs 专业版）

> **用途**：向企业负责人演示时，清晰展示两版本在 AI 能力上的层级差异  
> **测试方法**：按顺序先演示标准版（v7），再演示专业版（pro_v5），对比差异

### 6.1 两版共有 — Sidebar Copilot 通用提问（先演示，建立基础认知）

在两版本的侧边栏 Copilot 中输入以下问题，**回复应该完全一致**：

| # | 输入 | 期望回复 |
|---|------|---------|
| S1 | `What is KGDRL?` | 预设 FAQ 答案，提到知识图谱+GAT+PPO |
| S2 | `Explain NSGA-II` | 预设 FAQ 答案，提到非支配排序+Pareto前沿 |
| S3 | `What can I do with Maverick-SORT?` | LLM fallback，介绍系统核心功能 |

**演示话术**：
> "无论是标准版还是专业版，Sidebar Copilot 都内置了相同的 AI 问答能力。预设问题秒回，开放问题走千问大模型。"

### 6.2 标准版 v7 专属 — 页面内嵌 AI（展示日常运营辅助）

打开 `streamlit_app_v7.py`，进入以下页面，**不需要在 Copilot 输入框提问**，AI 结论自动生成：

| # | 页面 | 操作 | 期望出现的 AI 输出 |
|---|------|------|-------------------|
| V1 | **Algorithm Arena** | 运行 benchmark 对比 | 页面底部自动生成绿色高亮的 AI 策略结论（如"KGDRL 在紧急订单场景下优于 PPO 15-23%"） |
| V2 | **Scenario Simulator** | 运行一个 What-If 场景 | 对比表格下方自动生成 AI 执行摘要（如"场景 B 成本降低 12%，建议采用"） |
| V3 | **SLA Analytics** | 查看历史 SLA 趋势 | 页面自动出现 AI 洞察卡片（如"准时率环比下降 2.3%，建议关注冷藏区"） |
| V4 | **Alert Center** | 上传 alerts.csv 后查看 | 每条告警右侧出现 AI 根因分析和处置建议 |

**演示话术**：> "标准版在 4 个核心业务页面嵌入了 AI：算法结论、What-If 报告、SLA 洞察、告警分析。这些都是开箱即用的运营辅助。"

### 6.3 专业版 pro_v5 专属 — 页面内嵌 AI（展示预测与策略深度）

打开 `streamlit_app_pro_v5.py`，进入以下页面，**标准版没有这些页面**：

| # | 页面 | 操作 | 期望出现的 AI 输出 |
|---|------|------|-------------------|
| P1 | **Strategy Optimizer** | 运行 NSGA-II → 点击某个帕累托点 | AI 自动解释该策略点（如"成本优先模式：适合日常运营，可节省 18% 分拣成本"） |
| P2 | **Data Center** | 上传 orders.csv → 点击 AI Forecast | 展示未来 7 天需求预测折线图 + AI 解读（如"预测下周三订单峰值 3,200 单，建议提前扩容"） |
| P3 | **Live Adaptive** | 触发一次容量调整 | 页面出现 AI 运营解读（如"系统在 14:30 将波次容量从 20 调至 28，因预测到达率上升 35%"） |
| P4 | **Command Center** | 查看 3D Profit Mountain | 3D 视图旁出现 AI 战术解读（如"当前盈利点集中在上午冷链区，建议下午增派冷藏区拣货员"） |
| P5 | **Business Analysis** | 填写财务参数 → 生成报告 | 一键生成投资者级商业分析报告（含 ROI、TCO、竞争定位） |

**演示话术**：> "专业版在标准版基础上新增了 5 个深度 AI 功能：策略优化解释、需求预测、实时自适应解读、3D 战术解读、投资者报告。这些不是通用聊天机器人，而是嵌入业务流程的领域 AI——每一个结论都基于实时计算数据。"

### 6.4 差异化对比总结（给负责人的关键信息）

| 维度 | 标准版 v7 | 专业版 pro_v5 |
|------|----------|--------------|
| AI 功能点 | 6 个（Copilot + Algorithm + What-If + SLA + Alert + Task） | 10 个（+ Strategy Optimizer + Live Adaptive + Data Center + Command Center + Business Analysis） |
| AI 深度 | 解释已有结果 | **预测未来** + 解释策略 |
| 是否需要上传数据 | 可选（Alert Center） | 强烈建议（Data Center 预测、Alert RAG） |
| 适用场景 | 日常运营辅助 | 集团级战略决策 |
| 定价 | ¥2,999/仓/月 | ¥8,999/仓/月 |

**✅ 通过标准**：标准版演示时企业负责人能理解"AI 辅助运营"；专业版演示时能理解"AI 驱动决策"。

---

## 故障排查速查表

| 现象 | 可能原因 | 检查项 |
|------|---------|--------|
| 所有回复都是通用套话 | FAQ 缓存未命中 + LLM fallback 走了错误 prompt | 检查 `ask_faq()` 是否被调用 |
| 回复速度慢（>3秒） | 走了 HF Inference API，网络延迟 | 正常现象（LLM fallback） |
| 点击按钮无反应 | `st.rerun()` 死循环或 NameError | 检查浏览器控制台 |
| 出现重复回复 | `copilot_input_pro5` 未清空 | 检查 `del st.session_state["copilot_input_pro5"]` 是否执行 |
| Copilot 显示 Offline | 系统 Python 启动 / 依赖缺失 | 用 `.venv\Scripts\streamlit.exe` 启动 |

---

> **测试通过后**，请勾选 ✅ 并继续下一组。
