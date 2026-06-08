# Sunergy Pharma 录屏演示脚本 v2（Pro 专业版为主）

> **版本 / Version**: Pro v5.0（专业版）为主，Essential v7.0（基础版）一笔带过  
> **建议时长 / Recommended Duration**: 6–8 分钟  
> **录制对象 / Recording Target**: Streamlit Pro 版  
> **语言 / Language**: 英文为主  
> **核心原则**: 每页演示必须对应一个"解决的实际问题"，禁止夸大未实现功能

---

## 零、录制前准备 / Pre-Recording Checklist

1. 打开浏览器，访问 Pro 版链接：https://appappprov5py-uxccwitlyufth7n4nyg6nv.streamlit.app/
2. 确认页面加载正常，侧边栏无报错。
3. **【预留：测试数据上传链路】** 如需展示真实数据效果，提前进入侧边栏 **Data Hub**，将 6 类 CSV 文件（Orders / Inventory / Tasks / Workers / SLA History / Alerts）拖入对应端口，确认上传成功后切回各页面查看。上传完成后，侧边栏会显示 "X of 6 file types loaded"。
4. 屏幕录制软件设置：录制整个浏览器窗口，分辨率建议 1920×1080。
5. 麦克风测试：语速适中，每段解说后留 1–2 秒停顿。

---

## 一、开场（0:00–0:40）/ Introduction

**【画面】** 浏览器打开 Streamlit App，停留在 **Command Center** 首页。

**【解说词 / Script】**

> "Hello everyone. Today I'm presenting **Sunergy Pharma Pro** — an intelligent wave allocation system for pharmaceutical distribution, powered by Knowledge-Graph-Guided Deep Reinforcement Learning, or **KGDRL**.
>
> We offer two product tiers. The **Essential Edition** is a lightweight entry point with core what-if simulation and ROI visualization — ideal for small warehouses exploring intelligent scheduling. The **Professional Edition**, which I'll focus on today, adds multi-objective optimization, real-time adaptive capacity, and enterprise-grade analytics for mid-to-large pharma distributors.
>
> Let's start with the problem we're solving."

**【要点提示】**
- 手指向侧边栏顶部的 "Sunergy Pharma Pro" 标识和 PRO 徽章。
- 开场即建立"Pro 是主角"的叙事，v7 仅一句话带过。

---

## 二、研发背景（0:40–1:40）/ Research Foundation

**【画面】** 保持在 **Command Center**，缓慢向下滚动，展示 3D 可视化下方的文字说明。

**【解说词 / Script】**

> "In pharmaceutical distribution, warehouses process tens of thousands of orders daily. Each order carries a temperature tag — ambient, cool, cold, frozen, or deep frozen — and a hard delivery deadline. The challenge is grouping these orders into waves: batches that are sorted, picked, and loaded together.
>
> Traditional WMS systems use static rules. They break down when faced with four real-world complexities:
> - **Multi-temperature mixing**: Cold-chain and ambient products must not be mixed; manual grouping is error-prone.
> - **Deadline pressure**: Hospitals demand strict delivery windows; a missed batch means drug shortages.
> - **Labor and vehicle imbalance**: Waves too large overload pickers; waves too small waste vehicles.
> - **Cost opacity**: Managers can't quantify whether today's schedule was actually optimal.
>
> Our core technology, **KGDRL**, injects domain expert knowledge — like 'frozen products must ship before 10 AM' — directly into the deep reinforcement learning policy via a knowledge graph and KL-divergence constraints. The algorithm framework originates from our research group's ongoing work on pharmaceutical cold-chain scheduling."

**【要点提示】**
- 说"ongoing work"而非"已授权专利"，避免未经核实的内容。
- 手指向 Command Center 的 4 张"Pro Exclusive Capabilities"卡片，建立预期。

---

## 三、核心功能逐项演示（1:40–6:20）/ Feature Walkthrough

---

### 功能 1：Command Center — 决策者全局视图

**【页面】** 🏠 Overview → **Command Center**

**【解决的问题】** "决策者看不到全局——利润在哪里、投资何时回本，全凭经验猜。"

**【解说词 / Script】**

> "The Command Center gives executives a single-pane view. On the left, the **Operational Profit Mountain** is a 3D surface plot showing net profit across five temperature zones and six time slots. You can drag to rotate it. The peaks are morning and evening rush hours; deep-frozen products yield the highest margin per order but also the highest labor cost.
>
> On the right, the **Investment Trajectory Ribbon** tracks cumulative cash flow over five years. We compare four scenarios: doing nothing, or adopting Sunergy under conservative, neutral, and optimistic efficiency assumptions. The neutral scenario shows payback within roughly six months."

**【演示提示词 / Demo Cues】**
- 🖱️ **拖拽旋转 3D Profit Mountain**，展示交互性。
- 🖱️ **悬停在 Investment Trajectory 的曲线上**，展示 tooltip 数值。

**【注意】** 这些图表基于模拟参数（订单量、毛利率、人工成本），用于演示可视化能力，非真实企业财报。

---

### 功能 2：Omni-Channel Orders + Order Analytics — 订单统筹

**【页面】** 📦 Orders & Inventory → **Omni-Channel Orders** → **Order Analytics**

**【解决的问题】** "订单来源复杂——医院、连锁药店、基层医疗的订单混在一起，难以快速分类和识别瓶颈。"

**【解说词 / Script】**

> "Under Orders and Inventory, the **Omni-Channel Orders** page ingests orders from four client types: public hospitals, chain pharmacies, independent pharmacies, and primary healthcare centers. Each row shows the temperature requirement, deadline, priority, and current status.
>
> **【预留：测试数据上传链路】** If you've uploaded your own orders CSV through the Data Hub sidebar, this table reflects your real data. Otherwise, it runs on simulated order logs that refresh periodically.
>
> The filters on the left let you slice by client category, time window, and temperature zone. The distribution charts below show arrival patterns across the day and the temperature mix. Cold-chain products account for roughly 40% of volume — which is exactly why automated temperature-aware grouping matters."

**【演示提示词 / Demo Cues】**
- 🖱️ **在 Client Category 多选框中取消勾选一项**，观察表格和图表实时过滤。
- 🖱️ **切换到 Order Analytics**，展示温度分布饼图和到达时间线。

---

### 功能 3：Warehouse & Zones — 库存效期管理

**【页面】** 📦 Orders & Inventory → **Warehouse & Zones**

**【解决的问题】** "库存效期管理靠人工盘点，近效期药品容易被遗忘，造成报损。"

**【解说词 / Script】**

> "The **Warehouse & Zones** page tracks five temperature zones with real-time utilization bars. Below that, the **Near-Expiry Inventory Control** table color-codes every SKU by risk level: red for critical — expiry within 30 days; orange for warning — within 60; yellow for notice — within 90; and green for normal.
>
> For a pharmaceutical warehouse, this is not just a convenience. GSP regulations mandate first-expiry-first-out, and temperature deviations during prolonged storage can void entire batches. The system flags risk before it becomes a compliance incident."

**【演示提示词 / Demo Cues】**
- 🖱️ **滚动到 Near-Expiry Inventory 表格**，手指向红色 Critical 行。
- 🖱️ **查看右侧的 Zone Capacity Utilization 环形图**。

---

### 功能 4：Scenario Simulator — 调整前的沙盒实验

**【页面】** ⚙️ Smart Scheduling → **Scenario Simulator**

**【解决的问题】** "仓库经理想调整波次容量或人员配置，但怕影响实际生产，没有地方先试错。"

**【解说词 / Script】**

> "The **Scenario Simulator** is a what-if sandbox. You can configure up to six parallel scenarios, each with its own wave capacity, setup cost, peak multiplier, and scheduling policy. Hit 'Run Real Simulation' and the system computes cost, distance, wave count, violation rate, and on-time percentage for every scenario side by side.
>
> For example, if I reduce wave capacity from 20 to 15 and raise the peak multiplier to 1.5, you can see immediately whether SLA improves enough to justify the higher operational cost. The best scenario is highlighted in green.
>
> **【预留：测试数据上传链路】** If real order data is uploaded, the simulator uses your actual arrival patterns instead of synthetic defaults, making the what-if results far more relevant to your operation."

**【演示提示词 / Demo Cues】**
- 🖱️ **拖动 Wave Capacity 滑块从 20 到 15**。
- 🖱️ **点击 "Run Real Simulation"**，等待结果出现后手指向 Best Scenario 卡片。
- 💬 **LLM 穿插**: "After running scenarios, you can ask the AI Copilot: 'Why does smaller wave capacity improve SLA but raise cost?'"

---

### 功能 5：Strategy Optimizer — 多目标冲突时的科学决策

**【页面】** ⚙️ Smart Scheduling → **Strategy Optimizer**

**【解决的问题】** "成本、时效、合规三个目标经常冲突——日常要省钱，流感季要速度，审计期要合规，人工调度无法快速切换策略。"

**【解说词 / Script】**

> "The **Strategy Optimizer** runs NSGA-II multi-objective optimization. Instead of a single fixed policy, it maintains a Pareto frontier of trade-offs between cost, miss rate, and compliance violations.
>
> You choose a strategy mode — Cost First, Time First, Compliance First, or Balanced — and the optimizer recalculates the recommended operating point. The scatter plot shows every candidate solution: blue bubbles near the bottom-left are cheap and accurate; red bubbles are high-risk.
>
> During flu season, switch to Time First. During GSP audit periods, switch to Compliance First. The system adapts its recommendation without retraining from scratch."

**【演示提示词 / Demo Cues】**
- 🖱️ **切换 Strategy Mode 从 "Balanced" 到 "Time First"**。
- 🖱️ **点击 "Run NSGA-II"**，观察帕累托前沿散点图变化。
- 🖱️ **指向 Strategy Recommendation 卡片**。

---

### 功能 6：Live Adaptive Intelligence — 高峰期的自动应对

**【页面】** ⚙️ Smart Scheduling → **Live Adaptive Intelligence**

**【解决的问题】** "订单高峰来临时，波次容量固定不变，导致要么爆仓要么空转，经理只能靠打电话临时调人。"

**【解说词 / Script】**

> "**Live Adaptive Intelligence** uses EWMA — Exponentially Weighted Moving Average — to predict order arrival rates hour by hour. When the predicted rate exceeds baseline by a threshold, the system automatically shrinks wave capacity and increases release frequency to prevent backlog.
>
> Here you configure the EWMA alpha, base capacity, and min-max bounds. Then run a 24-hour simulation. The top chart shows observed versus predicted arrival rates; the bottom chart shows how capacity adjusts in real time. The adjustment log records every trigger: peak detected, valley detected, or high-load sustained.
>
> This is not a pre-scheduled plan. It's a closed-loop system that responds to actual demand fluctuations within the shift."

**【演示提示词 / Demo Cues】**
- 🖱️ **微调 EWMA Alpha 滑块**（如从 0.3 到 0.4）。
- 🖱️ **点击 "Run 24-Hour Simulation"**。
- 🖱️ **指向 Capacity Adjustment 曲线图中的上升/下降段**。

---

### 功能 7：Alert Center — 从被动救火到主动预防

**【页面】** 📊 Operations → **Alert Center**

**【解决的问题】** "异常发生后才被发现——温度超标、批次延误、库存告急，全是事后补救。"

**【解说词 / Script】**

> "The **Alert Center** monitors six anomaly types in real time: temperature deviations, capacity overloads, deadline risks, inefficient batches, too many zones, and low stock. Alerts are color-coded by severity — critical in red, warning in yellow, info in blue.
>
> Each alert is expandable. When you open one, you see the root cause and recommended actions. For example, a temperature deviation alert explains which zone exceeded threshold, for how long, and whether adjacent batches are at risk.
>
> **【预留：测试数据上传链路】** If alerts CSV is uploaded from your WMS, the feed reflects your actual historical or live alert stream. Without upload, it runs on a realistic simulated feed."

**【演示提示词 / Demo Cues】**
- 🖱️ **展开一条 critical  severity 的预警**，展示 Root Cause 和 Recommended Actions。
- 🖱️ **滚动查看 Active Alert Feed 列表**。

---

### 功能 8：AI Copilot（穿插演示）— 打破算法黑箱

**【页面】** 🔬 Tech Deep Dive → **🤖 AI Copilot**

**【解决的问题】** "仓库经理和决策者看不懂强化学习算法，不敢信任系统的自动决策。"

**【解说词 / Script】**

> "A common objection to AI scheduling is: 'The algorithm is a black box. My operators won't trust it.' That's why we built the **AI Copilot**, powered by Hugging Face large language models.
>
> You don't need to understand PPO or graph attention networks. Just type a question in plain English, and the Copilot explains the system's logic in human language. Let me demonstrate."

**【演示提示词 / Demo Cues】**
- 🖱️ **点击快捷问题按钮 "What is KGDRL?"**，等待回答展示。
- ⌨️ **或自由输入**: *"Why should I trust AI scheduling over manual experience?"*
- 🖱️ **展示回答后，补充**: "The Copilot can also answer in Chinese, making it accessible to frontline warehouse staff who may not read English technical documentation."

**【注意】** Copilot 需要 Hugging Face Token 配置。如果当前离线，改为介绍功能即可，不必等待。

---

### 功能 9：ROI Calculator + TCO Analysis — 算清投资回报

**【页面】** 💼 Business Value → **ROI Calculator** → **TCO Analysis**

**【解决的问题】** "采购部门问'能省多少钱'，技术团队说不出具体数字，导致项目拿不到预算。"

**【解说词 / Script】**

> "Finally, the business case. The **ROI Calculator** takes four inputs: daily orders, picker hourly wage, number of warehouses, and average cost per temperature violation. It outputs current annual cost, estimated savings, net savings after subscription, and payback period.
>
> The sensitivity area chart below shows how net savings change across a range of efficiency improvement rates — from 10% to 35%. Even at the conservative end, the system pays for itself within the first year.
>
> In **TCO Analysis**, we extend this to a five-year comparison. Manual operation costs rise with wage inflation; Sunergy Pro subscription rises much more slowly. The cumulative chart shows the breakeven point — typically in month five or six."

**【演示提示词 / Demo Cues】**
- 🖱️ **修改 Daily Orders 输入框**（如从 5000 到 8000），观察右侧数字实时更新。
- 🖱️ **切换到 TCO Analysis**，展示 5 年成本对比柱状图。
- 🖱️ **指向 Cumulative TCO 线图中的盈亏平衡点**。

---

### 功能 10：Competitor Radar + Plans & Pricing — 差异化定位

**【页面】** 💼 Business Value → **Competitor Radar** → **Plans & Pricing**

**【解决的问题】** "客户不清楚 Sunergy 与 SAP EWM、Manhattan Associates 等传统 WMS 的区别，也不知道该选哪个版本。"

**【解说词 / Script】**

> "The **Competitor Radar** compares six capabilities across vendors: price-to-value, AI intelligence, GSP compliance, deployment speed, real-time adaptability, and explainability. Traditional WMS systems score high on basic compliance but low on AI and real-time features. Sunergy Pro is designed specifically for pharmaceutical cold-chain complexity.
>
> **Plans & Pricing** offers three tiers. Essential starts at roughly 3,000 RMB per month per warehouse for small operations. Professional, at roughly 9,000 RMB, adds multi-objective optimization and real-time adaptation. Enterprise is custom-priced for multi-warehouse federated deployments.
>
> The group deployment calculator at the bottom lets you input your warehouse count, daily orders, and labor costs to see total net savings and ROI before signing."

**【演示提示词 / Demo Cues】**
- 🖱️ **在 Plans & Pricing 页面切换 Monthly / Annual 计费周期**。
- 🖱️ **在 Group Deployment Calculator 中修改 Warehouses 数量**，观察 ROI 变化。

---

## 四、结尾总结（6:20–6:50）/ Closing

**【画面】** 回到 **Command Center** 首页。

**【解说词 / Script】**

> "To summarize what Sunergy Pharma Pro delivers:
>
> - **Command Center** gives executives a 3D financial view.
> - **Orders and Warehouse** modules unify omni-channel demand and expiry-risk inventory.
> - **Scenario Simulator** lets managers test changes before committing to them.
> - **Strategy Optimizer** resolves multi-objective conflicts with scientific trade-offs.
> - **Live Adaptive Intelligence** responds to demand peaks in real time.
> - **Alert Center** shifts operations from reactive firefighting to proactive prevention.
> - **AI Copilot** builds trust by explaining every decision in natural language.
> - **ROI and TCO tools** translate technical benefits into boardroom numbers.
>
> The Essential Edition covers what-if simulation and basic ROI for smaller warehouses. The Professional Edition, which you've seen today, adds the optimization engine, real-time adaptation, and enterprise analytics that mid-to-large pharma distributors need to stay competitive.
>
> Thank you for your attention. I'm happy to take questions."

**【要点提示】**
- 语速放慢，每点之间停顿半秒。
- 微笑，给出明确的结束感，停顿 2 秒后停止录制。

---

## 附录 A：v7 基础版一句话介绍（如被问起）

> "The **Essential Edition** is our entry-level tier. It includes the core what-if scenario simulator, basic order analytics, the KGDRL framework visualization, and the ROI calculator — enough for a small warehouse to evaluate intelligent scheduling before upgrading to Pro."

---

## 附录 B：【预留：测试数据上传链路】详细操作

若需在录屏中展示真实数据效果，按以下步骤操作：

1. 打开 App，在侧边栏找到 **Data Hub** 区域。
2. 将以下 6 个 CSV 文件拖入对应端口：
   - `orders.csv` → Orders Upload
   - `inventory.csv` → Inventory Upload
   - `tasks.csv` → Tasks Upload
   - `workers.csv` → Workers Upload
   - `sla_history.csv` → SLA History Upload
   - `alerts.csv` → Alerts Upload
3. 上传成功后，侧边栏显示 "X of 6 file types loaded"。
4. 切换到 **Data Center** 页面，可查看上传数据的审查报告和统计信息。
5. 返回各功能页面，图表和表格将优先使用上传数据而非模拟数据。
6. 如需清除，点击 Data Hub 中的 **Clear All Uploads**。

**CSV 列名要求**（必须与以下完全一致）：

| 文件 | 必需列 | 可选列 |
|------|--------|--------|
| orders.csv | `order_id`, `client_type`, `sku_count`, `temperature`, `deadline_hours` | `priority`, `volume`, `status`, `timestamp`, `time_window` |
| inventory.csv | `sku`, `name`, `temperature_zone`, `stock_qty`, `expiry_date` | `category` |
| tasks.csv | `task_id`, `source_zone`, `target_client`, `priority`, `status` | `sku_checklist`, `assigned_worker`, `est_duration_min` |
| workers.csv | `worker_id`, `zone` | `shift`, `employment_type` |
| sla_history.csv | `period`, `client_category`, `on_time_rate` | `orders_fulfilled`, `orders_total`, `next_day_rate`, `temp_compliance_rate`, `exception_rate` |
| alerts.csv | `alert_id`, `type`, `severity`, `message` | `timestamp`, `zone`, `acknowledged` |

**temperature / temperature_zone 合法值**: `Ambient`, `Cool`, `Cold`, `Frozen`, `Deep Frozen`  
**client_type 合法值**: `Public Hospital`, `Chain Pharmacy`, `Independent Pharmacy`, `Primary Healthcare`  
**severity 合法值**: `critical`, `warning`, `info`

---

## 附录 C：演示提示词汇总 / Demo Cues Quick Reference

| 页面 | 提示词 |
|------|--------|
| Command Center | 🖱️ 拖拽旋转 3D Profit Mountain |
| Omni-Channel Orders | 🖱️ 在 Client Category 筛选器中取消勾选一项 |
| Warehouse & Zones | 🖱️ 滚动查看红色 Critical 近效期行 |
| Scenario Simulator | 🖱️ 拖动 Wave Capacity 滑块 → 点击 Run Simulation |
| Strategy Optimizer | 🖱️ 切换 Strategy Mode → 点击 Run NSGA-II |
| Live Adaptive | 🖱️ 调 EWMA Alpha → 点击 Run 24-Hour Simulation |
| Alert Center | 🖱️ 展开一条 critical 预警看 Root Cause |
| AI Copilot | 🖱️ 点击 "What is KGDRL?" 快捷按钮 |
| ROI Calculator | 🖱️ 修改 Daily Orders 数字，看实时变化 |
| Plans & Pricing | 🖱️ 切换 Monthly / Annual，修改 Warehouses 数量 |

---

## 附录 D：录制注意事项 / Recording Tips

| 事项 | 建议 |
|------|------|
| **语速** | 每分钟约 120–140 词，关键数字放慢 |
| **鼠标** | 移动轨迹要慢、要稳 |
| **滚动** | 每次滚动 1–2 屏，给观众消化时间 |
| **停顿** | 每切换一个页面，停顿 1 秒再开始解说 |
| **错误处理** | 如果某页面加载失败或报错，直接跳过，不要等 |
| **时长控制** | 若超过 8 分钟，压缩 TCO / Competitor Radar 段落 |
| **文件命名** | `Sunergy_Pro_Demo_Backup_20260608.mp4` |

---

> **最后提醒**：本讲稿所有功能描述均已逐页核实代码。Algorithm Arena 和 Patent & Research Wall 已从导航中移除，讲稿中不再提及。所有"AI预测"均为模拟演示效果，提及时应使用"simulated forecast"或"demonstration"等措辞，避免被误解为真实ML模型输出。
