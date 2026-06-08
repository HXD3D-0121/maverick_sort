# Sunergy Pharma 录屏演示脚本 / Screen Recording Demo Script

> **版本 / Version**: Pro v5.0 + Essential v7.0
> **建议时长 / Recommended Duration**: 6–8 分钟
> **录制对象 / Recording Target**: Streamlit App（优先录 Pro 版，如网络不稳则录 v7）
> **语言 / Language**: 英文为主（课程要求），关键术语可中英文对照

---

## 零、录制前准备 / Pre-Recording Checklist

1. 打开浏览器，访问 Pro 版链接：https://appappprov5py-uxccwitlyufth7n4nyg6nv.streamlit.app/
2. 确认页面加载正常，侧边栏无报错。
3. 屏幕录制软件设置：录制整个浏览器窗口，分辨率建议 1920×1080。
4. 麦克风测试：语速适中，每段解说后留 1–2 秒停顿，方便后期剪辑。

---

## 一、开场（0:00–0:45）/ Introduction

**【画面】** 浏览器打开 Streamlit App，停留在 **Command Center** 首页。

**【解说词 / Script】**

> "Hello everyone. I'm presenting **Sunergy Pharma** — an intelligent wave allocation system for pharmaceutical distribution, powered by Knowledge-Graph-Guided Deep Reinforcement Learning, or **KGDRL**.
>
> Every day, pharma warehouses process tens of thousands of orders. They must respect strict cold-chain rules, meet tight delivery deadlines, and balance labor and vehicle costs. Traditional WMS systems rely on static rules that break down under real-world variability.
>
> Our solution uses **KGDRL** to automatically optimize wave allocation — grouping orders into waves that minimize total operational cost while guaranteeing drug quality and GSP compliance."

**【要点提示】**
- 手指向侧边栏顶部的 "Sunergy Pharma Pro v5.0" 标识。
- 强调 "KGDRL" 这个词，这是核心技术关键词。

---

## 二、Command Center 概览（0:45–1:45）/ Dashboard Overview

**【画面】** 保持在 **Command Center** 页面，缓慢向下滚动，展示 3D 可视化。

**【解说词 / Script】**

> "This is the **3D Command Center**. On the left, you see the **Operational Profit Mountain** — a 3D surface showing net profit across five temperature zones and six time slots. The peak hours are morning and evening rushes, while deep-frozen products yield the highest margin per order.
>
> On the right, the **Investment Trajectory Ribbon** compares four scenarios over five years: doing nothing, or adopting Sunergy under conservative, neutral, and optimistic assumptions. Even the conservative case turns profitable within six months. The neutral case shows a **340% ROI** with a **5.8-month payback**.
>
> These numbers are calibrated against real-world pharma logistics cost structures, not fantasy projections."

**【要点提示】**
- 鼠标悬停在 3D 图表上，轻微拖动旋转，展示交互性。
- 强调 "340% ROI" 和 "5.8-month payback" 两个数字。

---

## 三、订单与库存（1:45–2:30）/ Orders & Inventory

**【画面】** 点击侧边栏 **Omni-Channel Orders**，展示订单表格；然后点击 **Order Analytics**，展示图表。

**【解说词 / Script】**

> "Let's look at the order side. In **Omni-Channel Orders**, the system ingests orders from hospitals, retail pharmacies, and e-commerce platforms simultaneously. Each order carries a temperature tag — ambient, cool, cold, frozen, or deep frozen — and a hard delivery deadline.
>
> In **Order Analytics**, we visualize arrival patterns, SKU distribution, and deadline pressure. You can see the morning peak at 8 to 12 o'clock, where order volume triples. The temperature pie chart shows that cold-chain products account for nearly 40% of volume — exactly why mixing rules matter so much."

**【要点提示】**
- 快速展示订单表格的几行数据，强调 temperature 和 deadline 列。
- 在 Order Analytics 页面，鼠标悬停在柱状图和饼图上，展示 tooltip 数据。

---

## 四、算法竞技场（2:30–3:45）/ Algorithm Arena

**【画面】** 点击侧边栏 **Algorithm Arena**（在 Smart Scheduling 分类下）。

**【解说词 / Script】**

> "Now we reach the heart of the system — the **Algorithm Arena**. Here we benchmark our KGDRL algorithm against five classical heuristics: FCFS, EDD, SPT, temperature-priority, and zone-clustering.
>
> The bar chart shows **total cost** across all methods. Lower is better. Our KGDRL algorithm sits at the bottom — that's the green-highlighted bar — with the lowest cost. The table below ranks every method by four metrics: total cost, distance penalty, time penalty, and temperature violation count.
>
> Notice that KGDRL cuts temperature violations by **85%** compared to FCFS, and reduces total picking distance by **18%**. These are not marginal gains; they translate directly into labor savings and reduced drug loss.
>
> The radar chart on the right visualizes the same comparison across six dimensions. KGDRL dominates the outer ring — meaning it achieves the best balance across all objectives."

**【要点提示】**
- 手指向 KGDRL 的绿色柱状条。
- 在对比表格中，强调 KGDRL 行的绿色高亮。
- 雷达图可以简单转一圈展示。

---

## 五、场景模拟器（3:45–4:30）/ Scenario Simulator

**【画面】** 点击侧边栏 **Scenario Simulator**。

**【解说词 / Script】**

> "For warehouse managers who want to ask 'what-if' before making changes, we built the **Scenario Simulator**. You can drag these sliders to adjust wave capacity, staff count, temperature strictness, and peak multiplier.
>
> Let me demonstrate: I'll reduce wave capacity from 20 to 15 and increase the peak multiplier to 1.5. Click Run Simulation. The system recomputes the schedule instantly and shows the impact on cost, SLA compliance, and labor load.
>
> You can see that smaller waves improve SLA but increase total cost — a clear trade-off. This empowers managers to make **data-driven decisions** without touching the live system."

**【要点提示】**
- 拖动 1–2 个滑块，点击 Run Simulation。
- 等待结果出现后，手指向变化前后的数字对比。

---

## 六、运营监控与预警（4:30–5:15）/ Operations & Alerts

**【画面】** 点击侧边栏 **Operations Dashboard**，然后点击 **Alert Center**。

**【解说词 / Script】**

> "In daily operations, the **Operations Dashboard** gives real-time visibility into wave progress, picker utilization, and vehicle loading. The labor load curve here fluctuates naturally between 40% and 95% — reflecting shift rhythms and real-world disturbances like staff absences or brief equipment failures.
>
> The **Alert Center** monitors six anomaly types: temperature violations, capacity overloads, deadline risks, inefficient batches, too many zones, and normal status. In this demo, all six types are represented — proving the system catches risks before they become incidents.
>
> Each alert includes root-cause analysis and a recommended action, so operators don't just see a red flag — they know exactly what to do."

**【要点提示】**
- 在 Operations Dashboard 展示人力负载曲线和实时 KPI 卡片。
- 在 Alert Center 展示预警饼图和下方的预警列表，点击一条查看详情。

---

## 七、AI Copilot（5:15–5:50）/ AI Copilot

**【画面】** 点击侧边栏 **AI Copilot**（在 Tech Deep Dive 分类下）。

**【解说词 / Script】**

> "One feature I'm particularly proud of is the **AI Copilot**, powered by Hugging Face large language models. Warehouse managers don't need to understand reinforcement learning. They can simply type a question in plain English — or Chinese — and get an instant, human-readable explanation.
>
> For example, if I ask: 'Why did the system close Wave 3 so early?' The Copilot answers: 'Wave 3 was closed at minute 12 because it already contained 14 orders covering zones A and B, and the next peak arrival window was only 6 minutes away. Keeping it open would risk deadline violations.'
>
> This bridges the gap between AI optimization and human trust."

**【要点提示】**
- 如果 Copilot 在线，输入一个预设问题（如 "What is KGDRL?"），展示回答。
- 如果 Copilot 离线，简单介绍其功能即可，不要浪费时间等待。

---

## 八、专利与研究墙（5:50–6:20）/ Patent & Research Wall

**【画面】** 点击侧边栏 **Patent & Research Wall**。

**【解说词 / Script】**

> "Finally, the **Patent & Research Wall** documents our intellectual property and academic foundations. Our core KGDRL algorithm is protected by an invention patent that has been formally accepted by the China National Intellectual Property Administration and entered substantive examination.
>
> The timeline shows our research trajectory from the original MDP formulation, through PPO-based implementation, to the current knowledge-graph-guided architecture. We also maintain active research on multi-objective optimization and Birkhoff-von Neumann decomposition for theoretical performance guarantees.
>
> This is not a course project with a deadline — it's a technology platform with a roadmap."

**【要点提示】**
- 缓慢滚动展示专利信息和研究时间线。
- 强调 "substantive examination" 和 "invention patent"。

---

## 九、结尾（6:20–6:45）/ Closing

**【画面】** 回到 **Command Center** 首页，或者停留在 Patent Wall。

**【解说词 / Script】**

> "To summarize: Sunergy Pharma delivers **intelligent wave allocation** for pharmaceutical distribution, combining **KGDRL** for decision optimization, **real-time dashboards** for operational visibility, and **AI Copilot** for human-AI collaboration.
>
> For a mid-size warehouse handling 5,000 orders per day, our simulations project **¥142,000 annual net savings** with a payback period under six months.
>
> Thank you for your attention. I'm happy to take any questions."

**【要点提示】**
- 微笑，语速放慢，给出一个明确的结束感。
- 停顿 2 秒后停止录制。

---

## 附录 A：如果 Pro 版无法加载，改用 v7 的录制路径 / Backup Route (v7)

若 Pro 版网络不稳定，请使用 **Essential v7** 链接：https://appappv7py-8pbgzhy5fjmswmefmz5jfz.streamlit.app/

v7 的页面结构与 Pro 版基本一致，但缺少以下页面：
- Data Center（Pro 独有）
- Strategy Optimizer（Pro 独有）
- Live Adaptive Intelligence（Pro 独有）
- AI Learning Engine（Pro 独有）
- Multi-Warehouse Network（Pro 独有）

**替代方案**：
1. Algorithm Arena → 同 Pro 版，展示算法对比
2. Scenario Simulator → 同 Pro 版，展示 What-if 模拟
3. ROI Calculator（v7 独有，在 Business Value 分类下）→ 替代 Command Center 的 3D 图表，直接展示 ROI 数字
4. Real-Time Simulation（v7 独有，在 Demo & Simulation 分类下）→ 展示 HTML Dashboard 嵌入效果

---

## 附录 B：录制注意事项 / Recording Tips

| 事项 | 建议 |
|------|------|
| **语速** | 每分钟约 120–140 词，关键数字放慢 |
| **鼠标** | 移动轨迹要慢、要稳，不要快速晃动 |
| **滚动** | 每次滚动 1–2 屏，给用户消化时间 |
| **停顿** | 每切换一个页面，停顿 1 秒再开始解说 |
| **错误处理** | 如果某页面加载失败，直接跳过，不要等 |
| **时长控制** | 如果超过 8 分钟，压缩 Scenario Simulator 和 Alert Center 段落 |
| **文件命名** | `Sunergy_Demo_Backup_20260608.mp4` |
| **上传目标** | 用户提到的 "same address"（请确认具体地址：是邮件、云盘还是 Teams?） |

---

## 附录 C：关键数字速查表 / Key Numbers Cheat Sheet

| 指标 | 数值 | 用途 |
|------|------|------|
| ROI | 340% | 投资回报率 |
| Payback Period | 5.8 months | 回收期 |
| Annual Savings | ¥142,000 | 年节省额 |
| Distance Reduction | -18% | 拣货距离减少 |
| Violation Reduction | -85% | 温控违规减少 |
| Decision Latency | <100 ms | 单次决策延迟 |
| Labor Load Range | 40%–95% | 人力负载波动区间 |
| Orders/Day (demo) | ~5,000 | 演示日单量 |
| Temperature Zones | 5 | 温区数量 |
| Alert Types | 6 | 预警类型数 |

---

> **最后建议**：先通读一遍脚本，然后对着 App 练习一次（不出声，走一遍页面），最后再正式录制。这样 6–8 分钟可以一气呵成，不需要后期剪辑。
>
> 如需我帮你把脚本转成 PPT 备注页格式，或翻译成纯英文演讲稿，随时告诉我。
