# 订单智能分配网页终端可行性分析

## 1. 现有代码结果是否支撑企业级可视化？

### 结论：**完全可以支撑**。原因如下：

| 维度 | 现有能力 | 可视化需求 | 匹配度 |
|------|---------|-----------|--------|
| **数据流** | `PharmaWaveEnv` 每一步输出 `state_dict` + `info`（含 action_type, wave_info） | Real-time sorting progress | ✅ 直接可用 |
| **波次信息** | `env.waves` 记录每个波次的订单数、距离、温度、区域、完成时间 | Wave allocation status | ✅ 直接可用 |
| **订单信息** | `order_pool` / `pending_orders` 实时追踪 | Order queue, arrival stream | ✅ 直接可用 |
| **时间线** | `env.current_time` + `env.step_count` | Sorting timeline | ✅ 直接可用 |
| **合规性** | `temp_violations`, `deadline_misses` | Exception alerts | ✅ 直接可用 |
| **劳动力** | 波次数 × setup_time / picking_time 可推导 picker 负载 | Labor load | ✅ 可计算 |

### 关键数据接口

```python
# 每步可获取的实时数据
{
    "current_time": env.current_time,           # 当前仿真时间
    "active_wave_orders": len(env.active_wave_orders),  # 当前波次订单数
    "active_wave_zones": list(env.active_wave_zones),   # 当前覆盖区域
    "active_wave_temps": list(env.active_wave_temps),   # 当前温度类别
    "order_pool_size": len(env.order_pool),     # 待分配订单池
    "pending_orders": len(env.pending_orders),  # 未到货订单
    "waves_completed": len(env.waves),          # 已完成波次
    "total_distance": env.total_picking_distance,  # 累计拣货距离
    "deadline_misses": env.deadline_misses,     # 超时次数
    "temp_violations": env.temp_violations,     # 温度违规次数
}
```

---

## 2. 企业级网页终端架构设计

### 2.1 系统架构（推荐）

```
┌─────────────────────────────────────────────────────────────┐
│                    前端 (Frontend)                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ 实时看板  │ │ 波次管理  │ │ 异常预警  │ │ 决策分析  │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│                    Vue.js / React + Chart.js                │
└────────────────────────┬────────────────────────────────────┘
                         │ WebSocket / REST API
┌────────────────────────┴────────────────────────────────────┐
│                    后端 (Backend)                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  FastAPI / Flask 服务层                              │   │
│  │  - /api/simulate/step      (单步仿真)                │   │
│  │  - /api/simulate/batch     (批量波次分配)            │   │
│  │  - /api/status/realtime    (实时状态)                │   │
│  │  - /api/alerts/active      (活跃异常)                │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  DRL Engine (PPO Agent)                              │   │
│  │  - 加载预训练模型                                     │   │
│  │  - 接收订单流，输出波次分配决策                        │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  PharmaWaveEnv (仿真环境)                             │   │
│  │  - 维护订单池、波次状态、时间线                        │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 前端核心模块

#### Module A: Real-Time Sorting Progress (实时分拣进度)

**功能**：
- 订单到达瀑布图（时间轴上显示订单流入）
- 当前活跃波次卡片（订单数、SKU数、温度覆盖、预计完成时间）
- 已完成波次列表（历史记录）

**数据来源**：`env.active_wave_*`, `env.waves`, `order_pool`

#### Module B: Labor Load (劳动力负载)

**功能**：
- 各温区 Picker 负载热力图
- 波次处理时间分布
- 人力缺口预警（当待处理波次 > 可用picker数时报警）

**计算方式**：
```python
# 简化的劳动力模型
picker_capacity = 5  # 每个picker同时处理的波次数
active_pickers = 12  # 当前在岗人数
labor_load = len(env.waves) / (active_pickers * picker_capacity)
```

#### Module C: Smart Wave Allocation (智能波次分配)

**功能**：
- 可视化展示 DRL/启发式 如何分组订单
- 对比模式：同时运行 PPO vs EDD，实时对比奖励差异
- "What-if" 模拟：调整容量约束、奖励系数，观察波次变化

#### Module D: Exception Alerts (异常预警)

**功能**：
- 温度混装实时报警（红色高亮）
- 超时风险订单列表（距离截止时间 < 2小时的订单）
- 峰值负载预警（订单到达率 > 基线 200%）

---

## 3. 课程项目级别的简化实现方案

对于本次 Digital Innovation 课程作业，推荐以下**最小可行方案**：

### 方案：纯前端 HTML/JS Dashboard（零后端依赖）

**原理**：
1. 预先用 Python 运行完整 pipeline，生成 `data/*.json` 结果文件
2. Dashboard 用原生 JavaScript 读取 JSON，通过 Chart.js / ECharts 可视化
3. 用 JavaScript 定时器模拟"实时"数据流（基于预计算的 step_log）

**优势**：
- 无需部署服务器，双击 HTML 即可运行
- 适合课堂演示和口头答辩
- 易于集成到现有 dashboard.html 框架中

**文件清单**：
| 文件 | 作用 |
|------|------|
| `smart_wave_dashboard.html` | 主看板页面 |
| `data/order_stats.json` | 订单统计 |
| `data/heuristic_results.json` | 启发式对比结果 |
| `data/ppo_eval.json` | PPO评估结果（含 step_log） |
| `data/ppo_training.json` | 训练曲线 |
| `data/comparison_plots.png` | 对比图 |

---

## 4. 实时数据流模拟设计

为了让看板具有"实时感"，我们基于 `ppo_eval.json` 中的 `step_log` 设计前端模拟：

```javascript
// step_log 结构（每步记录）
{
    "time": 45.0,           // 仿真时间（分钟）
    "action": 3,            // 选择的动作索引
    "action_type": "add",   // add / close / invalid
    "reward": -0.1,         // 即时奖励
    "wave_orders": 7        // 当前波次订单数
}

// 前端用 setInterval 每 200ms 播放一步
// 实现"实时分拣进度"动画效果
```

---

## 5. 与现有 dashboard.html 的集成建议

现有 `dashboard.html` 是通用仓储看板，建议：
1. **新增导航标签页**：在现有看板中加入 "Smart Wave Allocation" Tab
2. **复用样式系统**：沿用现有的 CSS 变量（`--accent-pink`, `--accent-cyan` 等）
3. **复用 Chart.js**：已有 Chart.js CDN 引用，无需额外引入
4. **复用布局网格**：沿用现有的 `.grid-container` 布局系统

---

## 6. 结论

**现有代码完全具备支撑企业级可视化的能力**。具体体现在：

1. ✅ **数据完备**：每一步仿真都产生丰富的状态、动作、奖励信息
2. ✅ **模型可导出**：PPO Agent 可以保存为 `.pt` 文件，后端加载推理
3. ✅ **可扩展性强**：MDP 框架天然支持 "What-if" 模拟和参数敏感性分析
4. ✅ **实时性可模拟**：基于 step_log 可在前端实现逼真的实时演示

对于课程项目，建议采用**纯前端方案**（预计算 JSON + JS 动画），既展示了算法能力，又提供了出色的可视化体验，且无需复杂的服务器部署。
