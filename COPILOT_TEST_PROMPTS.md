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
| 15 | `What can I do with Sunergy Pharma?` | 介绍系统功能（调度优化、波次分配、What-if 模拟等），不是 "I don't know" |
| 16 | `How does the system save money?` | 提到降低拣货距离、减少人力成本、优化波次 |
| 17 | `What is the pricing?` | 提到 Essential ¥2,999、Pro ¥8,999（或类似商业信息） |
| 18 | `Who is the target customer?` | 提到医药流通企业、仓储物流中心 |
| 19 | `Summarize the project in one sentence` | 一句概括：医药智能波次分配 + KGDRL + 多目标优化 |

**✅ 通过标准**：回答体现 Sunergy Pharma 项目知识，不是通用 Wikipedia 式回答。

---

## 第四组：边界测试

| # | 输入 | 期望行为 |
|---|------|---------|
| 20 | （空输入，直接回车） | 不触发任何回复，输入框保持空 |
| 21 | `???` | 走 LLM fallback，给出礼貌回应或请求澄清 |
| 22 | `hello` | 走 LLM fallback，Sunergy Copilot 自我介绍 |
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
