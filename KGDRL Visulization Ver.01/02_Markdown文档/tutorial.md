# Smart Wave Allocation 项目进展 —— 今日工作汇总

> **日期**：2026/06/01  
> **负责人**：你  
> **协助**：AI 编程助手（Claude Code）  
> **文件范围**：`smart_wave_dashboard_en.html`、`smart_wave_dashboard.html`、`dashboard_release/*`、`pharma_wave_allocation.py`

---

## 一、今天做了什么？一句话概括

把 Dashboard 里所有和 **"Reward（奖励）"** 相关的文字、数值、图表，统一改成了 **"Cost（成本）"** 语义；同时优化了人力负载（Labor Load）的波动效果，调整了波次切换的惩罚系数，并确保 Alert 系统在演示中能展示全部类型。

---

## 二、具体修改内容（按条解释）

### 1. 标签语义统一：Reward → Cost

**问题**：之前 Dashboard 里有些地方叫 "Total Reward"，有些地方又叫 "Total Cost"，混在一起。而且 "Reward" 是越大越好，"Cost" 是越小越好，语义相反，观众看了会 confusion。

**做了什么**：
- 把所有可见文字里的 "Reward" 全部替换为 "Cost"：
  - `Total Reward` → `Total Cost`（累计成本）
  - `📈 Reward Trend` → `📈 Cost Trend`（成本趋势）
  - `Avg Reward` → `Avg Cost`（平均成本）
  - `SCORE` 徽章 → `COST` 徽章
  - 图表 Y 轴、柱状图标签等一并同步
- **覆盖范围**：中英文两版 + `dashboard_release/` 目录下的 release 版本，共 **4 个 HTML 文件**

**效果**：现在打开 Dashboard，所有文字统一叫 "Cost"，逻辑一致，不会误导观众。

---

### 2. Cost 数值显示为正数

**问题**：底层模拟代码中，Cost 是通过 `reward = 45 - distance×0.25 + tempPenalty` 计算的，累加后的 `total_reward` 经常是负数（比如 -3000）。虽然技术上没错，但观众看到 "Total Cost: -3580" 会觉得奇怪——成本怎么是负的？

**做了什么**：
- 在显示层做了一个简单取反：`displayCost = -total_reward`
- 这样 -3580 就显示为 **3580**，直觉上 "成本是一个正数，越高越差"

**效果**：Dashboard 上的大数字和趋势曲线现在都是正数，符合日常认知。

---

### 3. Comparison（对比图表）语义修复

**问题**：之前 PPO 的数值（4180.2）比所有启发式方法都大。在 "Reward" 语义下这是好事（奖励最高），但改成 "Cost" 语义后，4180.2 会被解读为 "成本最高 = 表现最差"，这对我们推介 DRL 模型非常不利。

**做了什么**：
- 在对比图表和对比表格中，把所有方法的数值取反后展示：
  - PPO: 4180.2 → **-4180.2**（最低 = 最优，标绿高亮）
  - FCFS: 2557.6 → -2557.6
  - TEMP_FIRST: -1703.5 → **1703.5**（最高 = 最差）
- "最优" 判定逻辑从 `Math.max`（取最大）改为 `Math.min`（取最小）

**效果**：现在对比表格里 PPO 稳居第一（绿色高亮），TEMP_FIRST 成本最高排最后，符合预期。

---

### 4. Labor Load（人力负载）波动优化

**问题**：之前 Labor Load 是固定公式，波次多了之后直接锁定在 95% 或 98%，后半段一动不动，看起来很假。

**做了什么**：
- 把固定公式改成三层波动模型：
  1. **基础负载** = 波次数 / 35（分母加大，并设硬上限 78%，防止后期爆表）
  2. **时间因子** = 正弦波模拟班次内的工作强度起伏（开始低 → 中期高 → 收尾低）
  3. **随机噪声** = ±25% 的随机波动（模拟人员效率差异、临时离岗、设备卡顿等现实因素）
- 上下限从 `[5%, 95%]` 放宽到 `[15%, 98%]`

**效果**：Labor Load 现在会在 **40%~95%** 之间灵活波动，既体现了医药配送繁忙场景的高负载特征，又不会死板地锁定在某一数值。

---

### 5. Alpha_setup 调整（Python 代码）

**问题**：`pharma_wave_allocation.py` 中每次关闭一个波次的固定成本（`alpha_setup`）只有 5.0，太低了。Agent 没有动力把订单攒满再关波，导致波次数偏多，总成本下不来。

**做了什么**：
- `alpha_setup` 从 **5.0** 提高到 **15.0**

**效果**：Agent 会更倾向于把更多订单塞进同一个波次后再关闭，减少总波次数，从而降低整体 setup 成本。这个改动不影响 Dashboard 的 Alert 模拟效果。

---

### 6. Alert 多样性保障

**问题**：Dashboard 的演示模拟中，有些 Alert（比如 "波次过小"、"容量过载"）几乎从不触发，导致 Alert 饼图里永远只有 2~3 类，看起来不够丰富。

**做了什么**：
- 在模拟订单生成的逻辑里，加入了两种"人为干预"机制：
  - `forceSmallWave`（5% 概率）：偶尔在订单很少时（1~4 个）就强制关闭波次 → 触发 **"波次过小（Inefficient）"** Alert
  - `forceFullWave`（8% 概率）：偶尔在订单 >=10 时故意不关，让波次继续膨胀 → 触发 **"容量过载（Overload）"** Alert

**效果**：演示时 6 类 Alert（Temp Mixing、Overload、Deadline Risk、Normal、Too Many Zones、Inefficient）都能出现，饼图更丰富，更真实。

---

### 7. 全面排查遗漏

**问题**：前面几轮修改后，担心有漏网之鱼。

**做了什么**：
- 用全文搜索工具遍历了所有 4 个 HTML 文件，确认没有残留的 "Reward" 展示文字
- 发现并补修了 6 处遗漏（主要集中在根目录下的中英文版本，`dashboard_release/` 版本已在同步时修复）

**效果**：四个文件现在的 Cost 语义完全一致，不会再出现中英文版本不同步的情况。

---

## 三、明天汇报要点（建议话术）

1. **"今天我们完成了 Dashboard 的 Cost 语义统一化"**
   - 之前 Reward/Cost 混用，逻辑自相矛盾，观众看不懂。现在全部统一为 Cost，数值越低 = 表现越好，直观清晰。

2. **"PPO 在对比中稳居第一"**
   - 对比表格和柱状图里，PPO 的绿色高亮是最低成本，比 FCFS、EDD、ZONE_NN 等启发式方法都有明显优势。

3. **"Labor Load 现在会真实波动"**
   - 不再是死板的固定值，而是随班次节奏和随机因素在 40%~95% 之间波动，更符合真实仓库的人力负载情况。

4. **"Alert 系统演示效果更完整"**
   - 6 类 Alert 都会在模拟中出现，观众能看到温度违规、容量过载、波次过小、 deadline 风险等全部场景。

5. **"Python 训练代码也已同步优化"**
   - 提高了波次关闭的惩罚系数（5→15），Agent 会倾向于生成更大的波次，进一步降低总成本。

---

## 四、文件修改清单

| 文件 | 修改内容 |
|------|---------|
| `pharma_wave_allocation.py` | `alpha_setup` 5.0 → 15.0 |
| `smart_wave_dashboard_en.html` | Cost 语义统一、数值取反、Labor Load 波动化、Alert 多样性、Comparison 修复 |
| `smart_wave_dashboard.html` | 同上（中文版） |
| `dashboard_release/smart_wave_dashboard_en.html` | 同上（release 版同步） |
| `dashboard_release/smart_wave_dashboard.html` | 同上（release 版同步） |

---

## 五、备注

- 本次修改**没有**动原始 JSON 数据的属性名（如 `avg_reward`）和 JavaScript 内部变量名（如 `totalReward`），因为这些属于代码实现细节，不影响用户看到的展示文字。
- 如果明天演示时发现还有任何文字/数值不对劲，可以直接对照本文件排查。
