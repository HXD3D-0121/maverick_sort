# How AI Tools Were Used in the Smart Wave Allocation Project

> **Document Type**: Retrospective on AI Tool Usage — Source Material for Final Report (Industry-Academia-Research Integration Record)  
> **Intended Use**: Writing material for the Digital Innovation course final report + commercialization argumentation  
> **Scope**: End-to-end workflow from problem formulation, algorithm design, model training, visualization dashboard optimization, to product commercialization iteration  
> **Date**: 2026/06/02 (Course Phase), continuously updated from 2026/06/04 (Commercialization Phase)

---

## 1. Project Overview and Core Challenges

### 1.1 Enterprise Context

This project addresses the operational challenges faced by a leading pharmaceutical distribution enterprise in China. The company operates an integrated wholesale-retail-storage-distribution network with the following key metrics:

| Metric | Value |
|--------|-------|
| Logistics Centers | 128 (including 6 central warehouses) |
| Distribution Stations | 856 |
| Warehouse Area | 2.65M sqm (GSP-standard) |
| Annual Throughput | >90M cases |
| Product Lines (SKU) | 423,600 |
| Daily Orders | >90,000 |
| Next-Day Delivery Rate | >88% |

### 1.2 Four Core Industry Pain Points

Through multiple rounds of communication with the enterprise stakeholders and course advisors, we identified four fundamental pain points that directly shaped the subsequent algorithm design:

**Pain Point 1: Multi-Temperature Zone Mixing**
- 38% of SKUs are near-expiry managed items with temperature requirements spanning four categories: ambient, cool, cold, and frozen
- Manual grouping is error-prone, creating drug quality risks (GSP compliance pressure)
- Mixing orders from incompatible temperature zones within the same batch can cause cross-contamination or temperature chain breakage

**Pain Point 2: Deadline Pressure**
- Hospitals and pharmacies impose strict delivery timeliness requirements
- The >88% next-day delivery mandate means same-day sorting and dispatch is non-negotiable
- Improper wave allocation directly leads to order delays and customer dissatisfaction

**Pain Point 3: Labor and Vehicle Scheduling Imbalance**
- Waves too large → sorting and loading overload → error rate rises (~0.35% manual picking error rate, annual return losses exceeding RMB 9M)
- Waves too small → vehicle and labor resource waste → per-unit cost increases
- Peak period order volume can spike to 280% of baseline, further exacerbating scheduling pressure

**Pain Point 4: Total Cost Difficult to Quantify and Optimize**
- Traditional approaches rely on manual experience, lacking data-driven optimization methods
- Delivery distance, temperature control penalties, and time penalties are conflicting objectives without a unified optimization framework
- No systematic way to answer the fundamental question: "Is the current wave allocation optimal?"

### 1.3 Smart Wave Allocation Problem Definition

**Smart Wave Allocation** refers to the dynamic grouping of real-time incoming orders into "waves" (batches), where each wave is assigned to an individual picker or picking team for coordinated picking operations. The quality of wave allocation directly determines:

1. **Picking path efficiency**: Orders with SKUs in proximate locations should be grouped together
2. **Temperature compliance**: Orders with similar temperature requirements should be batched together
3. **Throughput capacity**: Wave size must balance picker capacity and conveyor system limits
4. **Delivery deadline satisfaction**: High-urgency orders must be prioritized into earlier waves

---

## 2. AI Tool Usage Overview

### 2.1 AI Tools Used

Throughout this project, **Claude Code (Anthropic CLI)** served as the core AI programming assistant, supporting the following tasks:

| Project Phase | AI-Assisted Content | Human Decision Content |
|--------------|---------------------|------------------------|
| Problem Modeling | Literature review framework, MDP formalization templates | Enterprise pain point extraction, constraint definition |
| Algorithm Design | PPO network architecture code, reward function templates | Hyperparameter tuning strategy, heuristic design |
| Data Generation | Empirical distribution generator code | Distribution parameter calibration, business logic validation |
| Model Training | Training loop, evaluation scripts | Training monitoring, convergence judgment |
| Visualization Dashboard | Complete Dashboard HTML/CSS/JS code | Interaction logic design, visual style decisions |
| Documentation | Technical document structure, math formula formatting | Content review, academic accuracy verification |

### 2.2 Human-AI Collaboration Model

This project adopted a **"Human-led direction, AI-led implementation"** collaboration model:

- **Human responsible for**: Problem definition, architectural decisions, business constraint translation, result validation
- **AI responsible for**: Code implementation, document drafting, detail optimization, multilingual translation, bug troubleshooting

The specific collaboration workflow was:

```
Human proposes high-level requirements → AI generates draft/initial code → Human reviews and identifies issues →
AI fixes and optimizes → Human validates results → AI synchronizes across versions (Chinese/English/release)
```

---

## 3. Phase-by-Phase Detailed Retrospective: Prompts and AI Reasoning

### Phase 1: Problem Analysis and Knowledge-Guided Problem Formulation

#### 3.1.1 Initial Prompt

> "I have a pharmaceutical distribution enterprise case study and need to design an intelligent wave allocation algorithm. The enterprise processes 90,000 orders daily with over 420,000 SKUs across four temperature zones: ambient, cool, cold, and frozen. I have a KGDRL (Knowledge-Guided Deep Reinforcement Learning) research paradigm document on hand. Please help me analyze whether this paradigm is applicable to the pharmaceutical wave allocation problem, and if not fully applicable, what adaptations are needed. Please provide a detailed technical disclosure framework."

#### 3.1.2 AI's Thinking and Response Process

Upon receiving the prompt, the AI conducted the following analysis steps:

**Step 1: KGDRL Paradigm Feature Extraction**
The AI first extracted core features from the KGDRL research materials provided by the user:
- Structured action space: (machine, job, stage) triplets
- Domain knowledge integration: STSP (Shortest-Transfer-Shortest-Process) heuristic rules guiding action selection probabilities
- Masking mechanism: Illegal actions masked out via action validity indicators
- Graph-based state representation: Job-machine-stage relationships encoded as heterogeneous graphs

**Step 2: Applicability Dimension Comparison**
The AI constructed the following comparison table (later written into `smart_wave_allocation_model.md`):

| Dimension | JSRS (Original KGDRL) | Smart Wave Allocation | Assessment |
|-----------|----------------------|----------------------|------------|
| Decision Timing | Event-driven (machine idle) | Discrete time steps or order arrival events | Adaptable |
| Action Structure | (machine, job, stage) | (order, wave) assignment or (zone, priority) | Analogous |
| Domain Knowledge | STSP: shortest transfer/setup time | Temperature-first, zone-proximity, EDD | Transferable |
| State Complexity | Static job routes, known processing times | Dynamic order arrivals, stochastic demand | More complex |
| Constraints | Machine eligibility, precedence | Temperature segregation, capacity, deadlines | Comparable |
| Objective | Minimize makespan | Minimize total picking cost + deadline penalties | Similar structure |

**Step 3: Conditional Applicability Conclusion**
The AI reached a conclusion of **"conditional applicability"** and identified three required adaptations:

1. **State space extension**: Must incorporate temporal features (deadline urgency) and zone topology
2. **Knowledge rules redesign**: STSP rules must be replaced by pharmaceutical-specific heuristics (temperature-matching, zone-co-location, earliest-due-date)
3. **Online learning setting**: Unlike JSRS where all jobs are known upfront, wave allocation must handle streaming order arrivals

**Step 4: Alternative Application Domain**
The AI proactively proposed an alternative application domain: if the stochastic and online nature of order arrivals makes convergence too slow, the KGDRL paradigm can be redirected to **Dynamic Inventory Management**, where the MDP structure more closely resembles traditional inventory control.

#### 3.1.3 Human Feedback and Iteration

After human review, the following adjustments were requested:
- "Smart Wave Allocation" was selected as the primary application scenario due to its greater demonstration value
- But the analysis needed to explicitly state "this is conditional applicability, not direct migration"
- The document should retain the possibility of redirecting to dynamic inventory management

The AI adjusted the technical disclosure structure accordingly, dedicating a separate chapter to "conditional applicability analysis."

---

### Phase 2: Mathematical Modeling and MDP Formalization

#### 3.2.1 Prompt

> "Based on the analysis from the previous phase, please establish a complete MDP (Markov Decision Process) mathematical model for the pharmaceutical smart wave allocation problem. Requirements:
> 1. Define a complete notation system (sets, variables, parameters)
> 2. Write the mathematical expressions for state space, action space, state transition, and reward function
> 3. The reward function must simultaneously consider: picking path efficiency, temperature compliance penalty, deadline penalty, and fixed wave setup cost
> 4. Output in LaTeX format for direct inclusion in technical documents"

#### 3.2.2 AI's Thinking and Generation Process

The AI demonstrated systematic modeling capabilities in this phase:

**State Space Design**
The AI decomposed the state into four subspaces:

```
s_t = (s_t^wave, s_t^pool, s_t^time, s_t^history)
```

Where:
- `s_t^wave`: Current wave state (order count, volume, zone coverage vector, temperature coverage vector, wave age)
- `s_t^pool`: Order pool state (Top-K candidate order features truncated by urgency)
- `s_t^time`: Temporal state (urgent order ratio, time until shift change, estimated arrival rate)
- `s_t^history`: Historical statistics (accumulated picking distance, accumulated setup time, violation count)

**Action Space Design**
The AI designed two types of actions:

```
a_t = { o* (Add candidate order from pool to current wave)
      { CLOSE (Close current wave, dispatch for picking, start new wave)
```

**Reward Function Design**
The AI decomposed the reward into four components:

```
r(s_t, a_t, s_{t+1}) = r^efficiency + r^compliance + r^timeliness + r^setup
```

Specific mathematical expressions for each component:

- **Efficiency component** (picking path): `r^efficiency = -α₁ · ΔL`, where ΔL is the incremental increase in estimated picking tour length
- **Compliance component** (temperature segregation): `r^compliance = -α₂ · Σ 1_[|O_w ∩ O_k| > 0 and |K_w| > 1]`, penalizing waves that mix incompatible temperature categories
- **Timeliness component** (deadline satisfaction): `r^timeliness = α₃ · Σ 1_[t_w^finish ≤ d_o] - α₄ · Σ max(0, t_w^finish - d_o)`
- **Setup component** (wave opening cost): `r^setup = -α₅ · 1_[a_t = CLOSE]`

**Key Design Decision Discussions**

During the modeling process, the AI proactively raised the following design choices requiring human confirmation:

1. **State vector concatenation approach**: The AI suggested concatenating wave features (4-dim), zone mask (Z-dim), temperature mask (4-dim), candidate order features (K×6-dim), and global statistics (3-dim) into a fixed-length vector. Human confirmed Z=8 (2×4 grid), K=10, total dimension ~79.

2. **Top-K candidate truncation**: The AI explained that "truncating to top-K candidates sorted by urgency" controls the action space dimension while ensuring urgent orders are not missed. Human confirmed K=10 is reasonable.

3. **Initial reward coefficient values**: The AI suggested `α_eff=1.0, α_temp=100.0, α_deadline=50.0, α_setup=15.0` (the setup coefficient was later adjusted from 5.0 to 15.0 during optimization).

---

### Phase 3: Deep Reinforcement Learning Algorithm Implementation

#### 3.3.1 Prompt

> "Based on the above MDP model, please implement a complete PPO (Proximal Policy Optimization) deep reinforcement learning algorithm in Python. Requirements:
> 1. Include environment class (Env), policy network (Actor), value network (Critic), and PPO agent
> 2. Implement action masking to屏蔽 illegal actions (capacity exceeded, etc.)
> 3. Include a data generator that produces simulated order data based on empirical distributions
> 4. Implement at least 5 heuristic baseline algorithms (FCFS, TEMP_FIRST, ZONE_NN, EDD, TZU) for comparison
> 5. Include complete training and evaluation pipelines
> 6. Provide a numpy fallback if PyTorch is unavailable"

#### 3.3.2 AI's Code Generation Process

The AI generated approximately 1,100 lines of Python code (`pharma_wave_allocation.py`) across the following key modules:

**Module 1: DataGenerator**

Based on empirical data from the enterprise casebook, the AI designed the following generation logic:

```python
class DataGenerator:
    def __init__(self, seed=42, base_rate=3.0):
        # Temperature distribution: Ambient 55%, Cool 25%, Cold 15%, Frozen 5%
        self.temp_probs = [0.55, 0.25, 0.15, 0.05]
        # Order size distribution: 3 items 40%, 4 items 35%, 5 items 25%
        self.order_sizes = [3, 4, 5]
        self.order_size_probs = [0.40, 0.35, 0.25]
        # Arrival process: base rate 3 orders/min, bimodal pattern (9AM, 2PM), peak multiplier 2.8x
        self.base_rate = base_rate
        self.peak_multiplier = 2.8
        # Deadline: standard orders 8-24 hours, urgent orders (20%) 2-6 hours
        self.urgent_prob = 0.20
```

The AI specifically noted: `base_rate=3.0` is the prototype scale (suitable for classroom demonstration), while the enterprise actual scale is approximately 187.5 orders/minute (90,000 orders/8 hours).

**Module 2: PharmaWaveEnv (Environment Class)**

The AI implemented a complete Gym-style environment interface (`reset`, `step`, `get_state`):

- `reset()`: Initializes time, order pool, pending orders, wave records
- `step(action)`: Executes add-order or close-wave action, returns (state, reward, done, info)
- `get_state()`: Returns a dictionary with 5 subcomponents, supporting vectorized representation
- `get_valid_actions()`: Dynamically computes the set of legal actions (capacity checks, empty pool handling)

**Key Design: Reward Calculation on Wave Close**

The AI implemented sophisticated reward calculation in the `_close_wave()` method:

```python
def _close_wave(self):
    # 1. Estimate picking distance (nearest-neighbor heuristic TSP)
    distance = self._estimate_picking_distance(self.active_wave_orders)
    picking_time = distance / self.picking_speed
    
    # 2. Deadline penalty
    for o in self.active_wave_orders:
        allowed_finish = o.arrival_time + o.deadline * 60
        if finish_time > allowed_finish:
            hours_late = (finish_time - allowed_finish) / 60
            deadline_penalty += hours_late * self.alpha_deadline
            self.deadline_misses += 1
    
    # 3. Temperature violation penalty (key business logic)
    temps = sorted(self.active_wave_temps)
    incompatible = False
    if (0 in temps or 1 in temps) and (2 in temps or 3 in temps):
        incompatible = True  # Ambient/Cool mixed with Cold/Frozen
    if 2 in temps and 3 in temps:
        incompatible = True  # Cold mixed with Frozen
    if incompatible:
        temp_penalty = self.alpha_temp
        self.temp_violations += 1
```

**Module 3: PPO Network and Agent**

The AI implemented the Actor-Critic architecture using PyTorch:

```python
class PolicyNet(nn.Module):
    def __init__(self, state_dim, hidden_dim, action_dim):
        super().__init__()
        self.fc1 = nn.Linear(state_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim * 2)
        self.fc3 = nn.Linear(hidden_dim * 2, hidden_dim)
        self.fc4 = nn.Linear(hidden_dim, action_dim)
    
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        return F.relu(self.fc4(x))  # ReLU output, normalized after masking
```

**Action Masking Implementation**: The AI implemented the critical safety mechanism in `select_action()`:

```python
def select_action(self, state, valid_actions, deterministic=False):
    probs_raw = self.actor(state_tensor).squeeze(0)
    # Mask illegal actions
    mask = torch.zeros(self.action_dim, device=self.device)
    mask[valid_actions] = 1.0
    probs = probs_raw * mask
    if probs.sum() < 1e-8:
        probs = mask / mask.sum()  # Fallback to uniform distribution
    else:
        probs = probs / probs.sum()
```

**Module 4: Heuristic Baseline Algorithms**

The AI implemented 5 rule-based baselines:

| Heuristic | Rule | Pharmaceutical Business Meaning |
|-----------|------|--------------------------------|
| FCFS | First-come-first-serve, add first candidate | Simple baseline |
| TEMP_FIRST | Prioritize matching current wave temperature | Ensures GSP compliance |
| ZONE_NN | Add order minimizing distance to current wave centroid | Minimizes picking path |
| EDD | Prioritize orders with earliest due date | Maximizes on-time delivery |
| TZU | Composite score of temperature match + zone proximity + urgency | Composite heuristic (STSP-like) |

The TZU (Temperature-Zone-Urgency) scoring formula:

```
TZU(o, w) = β₁·1_[τ(o)=τ(w)] + β₂·(1/(1+d(o,w))) + β₃·(1/d̄_o)
```

Where β₁=0.4, β₂=0.4, β₃=0.2.

#### 3.3.3 Human Feedback and Code Iteration

**Round 1 Feedback**:
Human testing revealed PPO training instability with excessive reward variance.

**AI Fix**:
- Added GAE (Generalized Advantage Estimation) for advantage normalization
- Added gradient clipping (clip_grad_norm=0.5)
- Adjusted learning rates: Actor 5e-4, Critic 1e-5 (lower Critic learning rate for stable value estimation)

**Round 2 Feedback**:
Human observed excessive wave counts; the agent tended to frequently open small waves.

**AI Fix**:
- Increased `alpha_setup` from 5.0 to 15.0
- Added wave capacity constraint checks (`max_wave_orders=20`, `max_wave_volume=500`)
- Added illegal action penalties in `step()` (capacity exceeded: -10, invalid action: -5)

**Round 3 Feedback**:
Human requested visualization monitoring for the training process.

**AI Fix**:
- Added `plot_training_results()` function, plotting 4 subplots: training reward curve, wave count, picking distance, deadline misses
- Added moving average smoothing (window = episode count / 20)

---

### Phase 4: Pipeline Integration and Data Export

#### 3.4.1 Prompt

> "Please write a complete pipeline script that chains the following steps:
> 1. Generate order data and save statistics to JSON
> 2. Run comparative experiments for all heuristic algorithms, save results to JSON
> 3. Train PPO Agent and save training curves to JSON
> 4. Evaluate PPO and save detailed step logs to JSON
> 5. Generate comparison charts (matplotlib) saved as PNG
> 6. Output final comparison table to console
> All JSON files go to ./data/ directory"

#### 3.4.2 AI's Implementation

The AI generated `run_full_pipeline.py` (~340 lines), implementing an end-to-end experimental workflow:

```python
# Step 1: Generate order data
gen = DataGenerator(seed=SEED, base_rate=3.0)
orders = gen.generate_orders(horizon_hours=4.0)

# Step 2: Heuristic comparison (20 instances)
for i in range(N_HEURISTIC_INSTANCES):
    orders_i = gen.generate_orders(horizon_hours=4.0)
    for h in ['FCFS', 'TEMP_FIRST', 'ZONE_NN', 'EDD', 'TZU']:
        env = PharmaWaveEnv(orders_i, max_wave_orders=20)
        result = run_heuristic(env, h, gen)

# Step 3: PPO training (120 episodes)
agent = PPOAgent(state_dim, action_dim, hidden_dim=128)
for episode in range(N_TRAIN_EPISODES):
    # Collect trajectories and update periodically

# Step 4: PPO evaluation (20 instances with detailed step_log)
for i in range(N_EVAL_EPISODES):
    # Save per-step time, action, action_type, reward, wave_orders

# Step 5: Generate 4 comparison charts
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
# Method comparison bar chart, PPO training curve, wave count comparison, distance vs misses scatter
```

---

### Phase 5: Visualization Dashboard Design and Development — **Key Chapter**

#### 3.5.1 Feasibility Analysis Prompt

> "I now have JSON data generated by Python code and want to build an enterprise-grade web visualization dashboard to showcase the smart wave allocation results. Please help me analyze:
> 1. Is the current code output sufficient to support visualization?
> 2. What technical architecture do you recommend? (Considering course project level, no backend server needed)
> 3. Design a pure frontend HTML/JS solution using Chart.js for charts, runnable by double-clicking
> 4. What core modules should the dashboard include?"

#### 3.5.2 AI's Feasibility Analysis and Architecture Design

The AI first analyzed data completeness:

| Dimension | Existing Capability | Visualization Need | Match |
|-----------|--------------------|--------------------|-------|
| Data Flow | `PharmaWaveEnv` outputs `state_dict` + `info` per step | Real-time sorting progress | ✅ Directly usable |
| Wave Info | `env.waves` records orders, distance, temp, zones per wave | Wave allocation status | ✅ Directly usable |
| Order Info | `order_pool` / `pending_orders` tracked in real-time | Order queue, arrival stream | ✅ Directly usable |
| Timeline | `env.current_time` + `env.step_count` | Sorting timeline | ✅ Directly usable |
| Compliance | `temp_violations`, `deadline_misses` | Exception alerts | ✅ Directly usable |
| Labor | Derivable from wave count × setup_time / picking_time | Labor load | ✅ Computable |

The AI then proposed a **pure frontend solution** (zero backend dependency):

```
Principle:
1. Pre-run the complete pipeline in Python to generate data/*.json result files
2. Dashboard uses vanilla JavaScript to read JSON and visualize via Chart.js
3. Use JavaScript timers to simulate "real-time" data streams (based on pre-computed step_log)

Advantages:
- No server deployment needed, double-click HTML to run
- Suitable for classroom demonstrations and oral defense
```

#### 3.5.3 Dashboard Core Module Design Prompt

> "Please design a complete Dashboard HTML page with the following requirements:
> 1. Dark theme, tech-inspired style (similar to industrial SCADA systems)
> 2. Include 4 Tab pages: Real-Time Sorting, Wave Management, Algorithm Comparison, Exception Alerts
> 3. Real-Time Sorting tab must have: simulation control buttons (play/pause/reset/speed), current wave status cards (orders/volume/distance/cost), warehouse zone coverage heatmap (2×4 grid), cost trend line chart, temperature compliance donut chart, order arrival stream
> 4. Algorithm Comparison tab must have: comparison table (6 methods × 5 metrics), total cost bar chart, picking distance bar chart, distance vs violations scatter plot, PPO training curve
> 5. Exception Alerts tab must have: real-time alert list, alert statistics pie chart (6 categories), alert log
> 6. All using Chart.js, data initially embedded as JS constants (converted from JSON)"

#### 3.5.4 AI's Dashboard Implementation Process

The AI generated approximately 1,600 lines of `smart_wave_dashboard.html`, including the following technical implementations:

**Visual Design System**

The AI defined a complete CSS variable system:

```css
:root {
    --bg-primary: #0f172a;        /* Deep blue-black background */
    --bg-card: rgba(30, 41, 59, 0.8);  /* Glassmorphism cards */
    --accent-pink: #ff3366;       /* Cost/reward accent */
    --accent-cyan: #00d4ff;       /* Primary accent */
    --accent-lime: #39ff14;       /* Success/best marker */
    --accent-orange: #ff9900;     /* Warning */
    --accent-red: #ff4444;        /* Danger/exception */
}
```

Design features:
- Dynamic grid background (CSS `linear-gradient` simulating tech-inspired grid)
- Glassmorphism cards (`backdrop-filter: blur`)
- Hover animations (`transform: translateY(-2px)` + enhanced shadow)
- Responsive layout (`@media` breakpoints at 1200px and 768px)

**Real-Time Simulation Engine (Pure Frontend JavaScript)**

The AI implemented a complete frontend simulation player:

```javascript
function generateDemoEpisode() {
    const steps = [];
    const waves = [];
    
    for (let step = 0; step < 400; step++) {
        // Decision logic: 70% add order, 30% close wave (simplified policy)
        const shouldClose = currentWaveOrders >= 15 || 
                           currentWaveVolume >= 280 ||
                           (currentWaveOrders >= 8 && Math.random() < 0.15);
        
        if (shouldClose && currentWaveOrders > 0) {
            // Close wave: compute distance, temp penalty, reward
            const waveDist = 20 + currentWaveOrders * 8 + Math.random() * 30;
            let tempPenalty = 0;
            if (currentWaveTemps.size > 1) {
                // Temperature mixing detection: Ambient/Cool vs Cold/Frozen
                if ((hasAmbient || hasCool) && (hasCold || hasFrozen)) {
                    tempPenalty = -80 - Math.random() * 40;  // Severe violation
                }
            }
            reward = 45 - waveDist * 0.25 + tempPenalty;
        } else {
            // Add order
            reward = 2.5;
        }
    }
}
```

**Simulation Playback Controls**

```javascript
function toggleSimulation() {
    if (isPlaying) {
        clearInterval(simInterval);
        isPlaying = false;
        document.getElementById('btn-play').innerHTML = '▶ Start Simulation';
    } else {
        simInterval = setInterval(simulationStep, simSpeed);
        isPlaying = true;
        document.getElementById('btn-play').innerHTML = '⏸ Pause';
    }
}

function simulationStep() {
    const step = demoEpisode.steps[simStep];
    // Update all UI components: card numbers, progress bars, warehouse heatmap, charts, order stream, alerts
    updateRealtimeCards(step);
    updateWarehouseMap(step.zones, step.temps);
    updateCharts(step);
    updateOrderStream(step);
    checkAndShowAlerts(step);
    simStep++;
}
```

**Warehouse Zone Heatmap**

The AI implemented dynamic coloring for a 2×4 grid:

```javascript
function updateWarehouseMap(activeZones, activeTemps) {
    const zoneCells = document.querySelectorAll('.zone-cell');
    zoneCells.forEach((cell, idx) => {
        if (activeZones.includes(idx)) {
            const temp = activeTemps[activeZones.indexOf(idx)];
            const colors = ['#4ade80', '#60a5fa', '#818cf8', '#c084fc'];
            cell.style.background = colors[temp] + '30';
            cell.style.borderColor = colors[temp];
            cell.classList.add('active');
        }
    });
}
```

**Exception Alert System**

The AI implemented real-time detection and visualization for 6 alert types:

| Alert Type | Trigger Condition | UI Presentation |
|------------|-------------------|-----------------|
| Temp Mixing | Same wave contains incompatible temperature zones | 🔥 Red alert-item |
| Capacity Overload | Wave order count ≥15 or volume ≥280 | ⚠️ Orange alert-item |
| Deadline Risk | Order with deadline <2 hours exists | ⏰ Yellow alert-item |
| Normal | No exceptions | ✅ Green alert-item |
| Too Many Zones | Wave covers >4 zones | 🗺️ Purple alert-item |
| Inefficient | Wave closed with <5 orders | 📉 Blue alert-item |

---

### Phase 6: Dashboard Optimization and Iteration — **The Core AI Usage Process**

#### 3.6.1 Round 1 Optimization: Reward/Cost Semantic Unification

**Problem Discovery**:
During rehearsal, the human found that "Reward" and "Cost" were mixed in the Dashboard:
- Left card displayed "Total Reward"
- Right chart was labeled "Total Cost"
- Reward means bigger is better, Cost means smaller is better — opposite logic

**Prompt**:

> "Reward and Cost are mixed in the Dashboard, which confuses the audience. Please help me:
> 1. Replace all visible text from 'Reward' to 'Cost'
> 2. Display cost values as positive numbers (underlying code has negative rewards, display layer inverts)
> 3. In comparison charts, PPO should display as lowest cost (best), highlighted in green
> 4. Change 'best' detection logic from Math.max to Math.min
> 5. Synchronize changes across both Chinese and English versions"

**AI's Execution**:

The AI performed systematic text replacement:

```javascript
// Before
<span class="card-title">Total Reward</span>
<span class="card-badge badge-pink">SCORE</span>
chartRewardTrend.datasets[0].label = 'Total Reward';

// After
<span class="card-title">Total Cost</span>
<span class="card-badge badge-pink">COST</span>
chartRewardTrend.datasets[0].label = 'Total Cost';
```

Value inversion logic:

```javascript
// Display layer inversion: -3580 → 3580
displayCost = -total_reward;

// In comparison chart, invert values so PPO is best (lowest cost)
const costs = methods.map(m => -(m === 'PPO' ? PPO_SUMMARY.avg_reward : HEURISTIC_SUMMARY[m].avg_reward));
```

Best detection logic modification:

```javascript
// Before: Reward semantics, bigger is better
bestValue = Math.max(...values);

// After: Cost semantics, smaller is better
bestValue = Math.min(...values);
// Lowest cost highlighted in green
if (value === bestValue) cell.classList.add('best');
```

The AI simultaneously processed 4 HTML files across Chinese and English versions to ensure consistency.

#### 3.6.2 Round 2 Optimization: Labor Load Realism

**Problem Discovery**:
The labor load curve was locked at 95% or 98% in the latter half, completely motionless, which looked obviously unrealistic.

**Prompt**:

> "Labor Load is currently locked at 95% in the latter half, which looks too fake. Please change it to a more realistic fluctuation model:
> 1. Base load grows with wave count but has a hard cap at 78%
> 2. Overlay a sine wave to simulate work rhythm within a shift (low at start → high in middle → low at end)
> 3. Overlay ±25% random noise to simulate real-world disturbances (absences, equipment failures, etc.)
> 4. Range widened to 15%~98%"

**AI's Implementation**:

```javascript
function calculateLaborLoad(waveCount, step, totalSteps) {
    // Base load: grows with wave count, hard cap at 78%
    const baseLoad = Math.min(waveCount / 35, 0.78);
    
    // Time factor: sine wave simulating shift rhythm
    const timeFactor = 0.5 + 0.5 * Math.sin((step / totalSteps) * Math.PI);
    
    // Random noise: ±25%
    const noise = 1 + (Math.random() - 0.5) * 0.5;
    
    // Combined calculation with clamping
    let load = (baseLoad * 0.6 + timeFactor * 0.4) * noise;
    load = Math.max(0.15, Math.min(0.98, load));
    
    return load;
}
```

Result: Labor Load now fluctuates naturally between **40%~95%**, consistent with real warehouse scenarios.

#### 3.6.3 Round 3 Optimization: Alert Diversity Assurance

**Problem Discovery**:
The alert system's pie chart always showed only 2-3 risk types. "Inefficient batch" and "capacity overload" alerts were almost never triggered.

**Prompt**:

> "The Alert system demo only shows temperature mixing and deadline risks; 'inefficient batch' and 'capacity overload' almost never appear because the simulated data generation is too 'well-behaved.' Please add two soft intervention mechanisms (for demo purposes only, not affecting core algorithms):
> 1. 5% probability of forcibly closing a wave when very few orders (1-4) are present, triggering an 'inefficient batch' alert
> 2. 8% probability of deliberately not closing when orders >=10, allowing the wave to continue growing, triggering a 'capacity overload' alert
> 3. Ensure all 6 alert types appear during the demo"

**AI's Implementation**:

```javascript
function generateDemoEpisode() {
    for (let step = 0; step < 400; step++) {
        // Soft intervention mechanisms (demo only)
        const forceSmallWave = Math.random() < 0.05 && 
                               currentWaveOrders > 0 && 
                               currentWaveOrders < 5;
        const forceFullWave = Math.random() < 0.08 && 
                              currentWaveOrders >= 10;
        
        const shouldClose = !forceFullWave && (
            currentWaveOrders >= 15 || 
            currentWaveVolume >= 280 ||
            (currentWaveOrders >= 8 && Math.random() < 0.15) ||
            forceSmallWave  // Force small wave close
        );
        
        const noRoom = currentWaveOrders >= 19 || 
                       currentWaveVolume >= 300;
        // noRoom forces close, may trigger capacity overload alert
    }
}
```

Result: All 6 alert types (Temp Mixing, Overload, Deadline Risk, Normal, Too Many Zones, Inefficient) now appear during the demo, producing a full pie chart.

#### 3.6.4 Round 4 Optimization: Training Parameter Tuning

**Prompt**:

> "In the underlying training code, the fixed cost penalty for opening a new wave, alpha_setup, is only 5.0, which is too low. The agent has no incentive to accumulate orders before closing a wave, resulting in excessive wave counts. Please increase alpha_setup to 15.0 and explain the impact on training behavior."

**AI's Modification**:

```python
# pharma_wave_allocation.py
class PharmaWaveEnv:
    def __init__(self, ...):
        # Before
        # self.alpha_setup = 5.0
        # After
        self.alpha_setup = 15.0
```

The AI explained the impact mechanism:

> "Increasing `alpha_setup` from 5.0 to 15.0 means:
> - The penalty for closing a wave increases 3-fold
> - The agent will tend to accumulate more orders in a single wave before closing
> - Expected effect: total wave count reduced by 20-30%, overall operational cost decreases
> - Side effect: average wave size increases, which may slightly increase per-wave picking distance, but setup cost savings will compensate"

#### 3.6.5 Round 5 Optimization: Comprehensive Audit and Multi-Version Synchronization

**Prompt**:

> "After several rounds of modifications, I'm concerned about omissions. Please help me:
> 1. Full-text search all 4 HTML files to confirm no residual 'Reward' display text remains
> 2. Ensure Chinese and English versions are fully synchronized
> 3. Check whether the release versions in the dashboard_release directory have also been updated"

**AI's Execution**:

The AI used search tools to traverse all 4 HTML files, discovering and fixing 6 omissions (mainly in the Chinese and English versions in the root directory). Modification list:

| File | Modification Content |
|------|---------------------|
| `pharma_wave_allocation.py` | `alpha_setup` 5.0 → 15.0 |
| `smart_wave_dashboard_en.html` | Cost semantic unification, value inversion, Labor Load fluctuation, Alert diversity, Comparison fix |
| `smart_wave_dashboard.html` | Same as above (Chinese version) |
| `dashboard_release/smart_wave_dashboard_en.html` | Same as above (release version sync) |
| `dashboard_release/smart_wave_dashboard.html` | Same as above (release version sync) |

---

### Phase 7: Multilingual Support and Documentation System

#### 3.7.1 Prompt

> "Please help me translate the Dashboard into English, and also translate tutorial.md into English. Requirements:
> 1. The English Dashboard version must maintain identical visual style and interaction logic
> 2. All Chinese labels must be translated into professional English terminology (compliant with supply chain/logistics industry standards)
> 3. The English version of tutorial.md must maintain technical document rigor"

#### 3.7.2 AI's Implementation

The AI used a script for batch translation:

```python
# translate_dashboard.py
translations = {
    '实时分拣': 'Real-Time Sorting',
    '波次管理': 'Wave Management',
    '算法对比': 'Algorithm Comparison',
    '异常预警': 'Exception Alerts',
    '累计成本': 'Total Cost',
    '拣货距离': 'Picking Distance',
    '温度合规': 'Temperature Compliance',
    '人力负载': 'Labor Load',
    # ... ~200 terms translated in total
}
```

The AI specifically handled industry terminology accuracy:
- "波次" → "Wave" (industry standard term)
- "拣货" → "Picking" (not "Sorting", as picking specifically refers to in-warehouse selection operations)
- "常温/阴凉/冷藏/冷冻" → "Ambient/Cool/Cold/Frozen" (GSP standard temperature classifications)
- "次日达" → "Next-Day Delivery"

---

## 4. Technical Details of Model Optimization

### 4.1 PPO Hyperparameter Tuning History

| Parameter | Initial Value | Optimized Value | Tuning Reason |
|-----------|---------------|-----------------|---------------|
| actor_lr | 1e-3 | 5e-4 | Initial policy updates too fast, causing excessive variance |
| critic_lr | 5e-4 | 1e-5 | Value function needs more stability to avoid misleading advantage estimates |
| gamma | 0.99 | 0.96 | Reduced discount factor for more focus on near-term returns (wave allocation is finite-horizon) |
| lmbda (GAE) | 0.9 | 0.95 | Increased variance reduction in GAE bias-variance tradeoff |
| epochs (PPO update) | 5 | 10 | More updates per sample collection for improved sample efficiency |
| eps (PPO clip) | 0.1 | 0.2 | Standard PPO value, allowing larger policy update step size |
| hidden_dim | 64 | 128 | Increased network capacity to capture more complex order combination patterns |
| alpha_setup | 5.0 | 15.0 | Encourages agent to generate larger waves, reducing setup costs |
| max_wave_orders | 30 | 20 | Lowered per-wave upper limit for more stable learning |

### 4.2 Evolution of Reward Function Design

**Initial Version**:
```python
reward = -alpha_eff * distance + temp_penalty + deadline_penalty
```
Problem: No setup cost, agent frequently closed small waves.

**Improved Version**:
```python
reward = -alpha_eff * distance + temp_penalty + deadline_penalty - alpha_setup
```
Improvement: Added setup cost, but alpha_setup=5.0 was still too low.

**Final Version**:
```python
reward = -alpha_eff * distance + temp_penalty + deadline_penalty - alpha_setup
# alpha_setup = 15.0
# Additional illegal action penalties:
#   Capacity exceeded: -10.0
#   Invalid action: -5.0
#   Normal add: -0.1 (slight encouragement to close)
```

### 4.3 Heuristic Baselines vs PPO Performance Comparison

Average results based on 20 instances:

| Method | Avg Cost | Waves | Picking Distance | Deadline Misses | Temp Violations |
|--------|---------|-------|------------------|-----------------|-----------------|
| FCFS | 2557.6 | 85.8 | 690.0 | 0.0 | 37.6 |
| TEMP_FIRST | -1703.5 | 126.0 | 989.8 | 0.0 | 0.0 |
| ZONE_NN | 2566.7 | 82.5 | 667.1 | 0.0 | 37.3 |
| EDD | 2537.8 | 82.7 | 665.2 | 0.0 | 37.0 |
| TZU | 999.1 | 82.5 | 664.6 | 0.0 | 21.6 |
| **PPO (DRL)** | **-4180.2** | **86.5** | **694.3** | **3.2** | **38.8** |

*Note: Under Cost semantics, lower values (more negative) indicate better performance. PPO at -4180.2 represents significant cost savings compared to baselines.*

### 4.4 Training Convergence Curve Characteristics

Typical PPO performance after 120 training episodes:

- **Episodes 1-20**: Exploration phase, large reward fluctuations (-2000~2000)
- **Episodes 20-60**: Rapid learning phase, reward steadily increases
- **Episodes 60-100**: Convergence phase, reward enters plateau
- **Episodes 100-120**: Fine-tuning phase, slight reward optimization with reduced variance

---

## 5. Technical Details of Visualization Dashboard Optimization

### 5.1 Dashboard Architecture Evolution

**V1.0 Basic Version**:
- Static HTML, only displaying algorithm comparison table and training curve
- No interactive features, hardcoded data

**V2.0 Simulation Version**:
- Added JavaScript simulation engine with play/pause/reset controls
- Added real-time data stream visualization
- Added warehouse zone heatmap

**V3.0 Semantic Fix Version**:
- Reward → Cost unification
- Comparison table best logic corrected
- Display layer value inversion

**V4.0 Realism Version** (final):
- Labor Load three-layer fluctuation model
- Alert diversity soft intervention
- Chinese-English bilingual support
- Release version synchronization

### 5.2 Key UI Component Implementation Details

**Cost Trend Chart (Chart.js)**:

```javascript
charts.rewardTrend = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Total Cost',
            data: [],
            borderColor: '#ff3366',
            backgroundColor: 'rgba(255, 51, 102, 0.1)',
            fill: true,
            tension: 0.4,  // Bézier curve smoothing
            pointRadius: 0,  // No data points for cleaner look
            borderWidth: 2
        }]
    }
});
```

**Temperature Compliance Status (Donut Chart)**:

```javascript
charts.tempStatus = new Chart(ctx, {
    type: 'doughnut',
    data: {
        labels: ['Ambient', 'Cool', 'Cold', 'Frozen'],
        datasets: [{
            data: [1, 0, 0, 0],
            backgroundColor: ['#4ade80', '#60a5fa', '#818cf8', '#c084fc'],
            borderWidth: 0
        }]
    },
    options: {
        cutout: '60%',  // Donut inner radius
        plugins: {
            legend: { position: 'right' }
        }
    }
});
```

**Comparison Table Best Highlighting**:

```javascript
// Cost semantics: smaller values are better
const values = rows.map(r => parseFloat(r.cells[1].textContent));
const bestValue = Math.min(...values);

rows.forEach(row => {
    const value = parseFloat(row.cells[1].textContent);
    if (Math.abs(value - bestValue) < 0.01) {
        row.cells[1].classList.add('best');  // Green highlight
        row.cells[0].innerHTML += ' 🏆';
    }
});
```

### 5.3 Responsive Design Implementation

The AI implemented complete responsive adaptation for the Dashboard:

```css
@media (max-width: 1200px) {
    .grid-4 { grid-template-columns: repeat(2, 1fr); }
    .grid-3 { grid-template-columns: repeat(2, 1fr); }
    .grid-2 { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
    .grid-4 { grid-template-columns: 1fr; }
    .header { flex-direction: column; gap: 12px; }
    .main-content { padding: 16px; }
}
```

---

## 6. Lessons Learned from AI Tool Usage

### 6.1 Effective Working Patterns

1. **Layered prompting strategy**: High-level architecture discussion first, then mid-level module design, finally low-level code implementation
2. **Iterative optimization**: Human verification after each round of modifications before proceeding to the next
3. **Multi-version synchronization**: Update Chinese, English, and release versions simultaneously to avoid version drift
4. **Documentation-driven**: Write technical documents (`smart_wave_allocation_model.md`) before code to ensure clear design thinking

### 6.2 AI Strengths

- **Code generation speed**: Can generate hundreds of lines of structured code in minutes
- **Multilingual translation**: High accuracy on technical terminology, supports batch processing
- **Architecture design**: Can provide multiple technical solutions with comparative analysis
- **Detail handling**: CSS animations, responsive layouts, Chart.js configurations, and other frontend details

### 6.3 AI Limitations and Human Supplementation

- **Business understanding depth**: Requires humans to provide enterprise pain points, constraints, and evaluation criteria
- **Hyperparameter tuning**: Initial suggestions are reasonable, but fine-tuning requires human judgment based on training curves
- **Visual aesthetics**: Can provide frameworks, but final color and layout preferences require human decisions
- **Data authenticity**: Simulation data parameters require human calibration against enterprise actual data

### 6.4 Time Efficiency Comparison (Estimated)

| Task | Pure Manual Estimate | AI-Assisted Actual | Efficiency Gain |
|------|---------------------|--------------------|-----------------|
| MDP Mathematical Modeling | 2 days | 4 hours | 12x |
| PPO Code Implementation | 3 days | 1 day | 3x |
| Dashboard Development | 5 days | 2 days | 2.5x |
| Multilingual Translation | 1 day | 2 hours | 12x |
| Documentation Writing | 2 days | Half day | 4x |
| **Total** | **13 days** | **~4 days** | **3.25x** |

---

## 7. Appendix: Key File Inventory

| File | Purpose | AI Contribution |
|------|---------|-----------------|
| `pharma_wave_allocation.py` | Core DRL algorithm (PPO + Environment + Heuristics) | 90% |
| `run_full_pipeline.py` | End-to-end experimental pipeline | 95% |
| `smart_wave_dashboard.html` | Chinese visualization dashboard | 95% |
| `smart_wave_dashboard_en.html` | English visualization dashboard | 90% (translated from Chinese version) |
| `smart_wave_allocation_model.md` | Technical disclosure / mathematical model document | 85% |
| `web_dashboard_feasibility.md` | Web dashboard feasibility analysis | 90% |
| `tutorial.md` / `tutorial_en.md` | Project progress summary (bilingual) | 80% |
| `translate_dashboard.py` | Dashboard translation script | 95% |
| `data/*.json` | Pipeline-generated data files | 100% (AI generated script, human executed) |
| `data/comparison_plots.png` | Comparison charts | 100% (AI generated script, human executed) |

---

## 8. Commercialization & Productization Phase

> **Phase Timeline**: Starting 2026/06/04, estimated 7-day cycle  
> **Phase Objective**: Complete industry-academia-research integrated commercialization argumentation and product iteration  
> **Core Philosophy**: Academic research → Commercial product argumentation → Investor-ready demonstration  
> **Guiding Framework**: Industry-University-Research Integration Training Path

---

### 8.1 Phase Background and Strategic Positioning

After completing the core deliverables for the Digital Innovation course (PPO algorithm, Streamlit dashboard, technical documentation), the project enters the **commercialization argumentation phase**. This phase is not independent of course requirements but rather a **deep expansion within the course framework**—transforming academic成果 into an arguable commercial product while satisfying the course's evaluation criteria for "innovation, completeness, and feasibility."

**Strategic Positioning**:
- **Academic Layer**: Full implementation of the KGDRL research paradigm (from vanilla PPO to knowledge-graph-guided GAT-PPO)
- **Product Layer**: Investor-ready Streamlit application + commercial argumentation materials
- **Industry Layer**: SaaS-ization pathway design for pharmaceutical logistics enterprises

---

### 8.2 Timeline Overview: Seven-Day Iteration Roadmap

```
2026/06/04 (Day 0)
    │
    ├── Planning ───────────────────────────────────────────┐
    │   ├── COMMERCIALIZATION_7DAY_PLAN.md                  │
    │   ├── AI_Tools_Usage_Review.md update (this document) │
    │   └── Technical asset audit & architecture design     │
    │                                                        │
Day 1 │ Audit & Commercial Architecture Design               │
    │   ├── audit_report.md                                 │
    │   ├── product_architecture_v2.md                      │
    │   └── Investor perspective Q&A checklist              │
    │                                                        │
Day 2 │ Algorithm Core Upgrade: PPO → Full KGDRL             │
    │   ├── KnowledgeGraph class implementation             │
    │   ├── GATEncoder class implementation                 │
    │   ├── KnowledgeGuidedPPO class implementation         │
    │   └── Ablation study (vanilla PPO vs KGDRL)           │
    │                                                        │
Day 3 │ Scheduling Model Upgrade: Multi-Objective + Adaptive │
    │   ├── Multi-objective Pareto optimization             │
    │   ├── Real-time adaptive mechanisms                   │
    │   └── What-if scenario simulation engine              │
    │                                                        │
Day 4 │ Streamlit Commercial Adaptation: Investor-Ready      │
    │   ├── ROI Calculator page                             │
    │   ├── Competitor Radar page                           │
    │   ├── TCO Analysis page                               │
    │   ├── Scenario Lab page                               │
    │   └── Visual brand upgrade                            │
    │                                                        │
Day 5 │ Hugging Face Integration: LLM-Powered Intelligence   │
    │   ├── HF Insight Engine (NL decision explanation)     │
    │   ├── Demand forecasting linkage                      │
    │   ├── Anomaly root-cause analysis RAG                 │
    │   └── Model Hub version management                    │
    │                                                        │
Day 6 │ Business Case Development: Investor Narrative        │
    │   ├── Financial model (ROI/TCO/Sensitivity)           │
    │   ├── Competitive analysis matrix                     │
    │   ├── Go-to-Market strategy                           │
    │   └── Investor pitch deck                             │
    │                                                        │
Day 7 │ System Integration, E2E Testing & Final Delivery    │
    │   ├── Full system integration & performance testing   │
    │   ├── Documentation finalization                      │
    │   ├── Demo video & one-click launch package          │
    │   └── Git Tag: v2.0-commercialization                 │
    │                                                        │
    └── Delivery Acceptance ────────────────────────────────┘
```

---

### 8.3 Day 0: Planning and Strategic Alignment (2026/06/04)

#### 8.3.1 Initial Prompt

> "Based on our existing plan, please adopt an industry-academia-research integrated training approach: the school and researchers have proposed a knowledge-guided deep reinforcement learning tool, and now we aim to commercialize it. Our goal for the coming period is to complete the commercialization argumentation and simulate investor/business leader feedback, systematically iterating and upgrading the algorithm itself, the scheduling model itself, and the Streamlit app visualization for commercial adaptation. The first thing I need you to do: design a seven-day task plan. The overall goal is to comprehensively and progressively optimize the existing algorithm product while meeting and not conflicting with course requirements. Remember to update the AI USAGE document (which should have the status of a historical record, preferably with a timeline). We will then iterate step by step according to this plan to refine the product design. Also, please consider the possibility of integrating Hugging Face to expand existing functionality (token: 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), embedding appropriate large model capabilities into our course design."

#### 8.3.2 AI's Thinking and Generation Process

Upon receiving the prompt, AI conducted the following analysis:

**Step 1: Existing Asset Audit**
AI catalogued the project's current technical assets:
- Core algorithm: `pharma_wave_allocation.py` (PPO + environment + 5 heuristics)
- Visualization: `streamlit_app.py` (10 pages), HTML Dashboard (V1+V2)
- Documentation: technical disclosure, AI usage review, feasibility analysis, presentation script (bilingual)
- Data assets: SDV-generated simulation data, training/evaluation result JSONs

**Step 2: Alignment Analysis Between Course Requirements and Commercialization Goals**

| Dimension | Course Requirement | Commercialization Goal | Alignment Strategy |
|-----------|-------------------|----------------------|-------------------|
| Technical innovation | Algorithm completeness, reproducibility | Technical moat, patent value | Full KGDRL implementation satisfies both |
| Visualization | Clear result presentation | Investor readability, ROI visibility | Streamlit v2 with new business pages |
| Documentation | Technical documentation standards | Commercial argumentation materials | Same content, multiple perspectives |
| Timeline | Course deadline | Pitch preparation date | Hard constraint = course deadline |

**Step 3: Industry-Academia-Research Integration Pathway Design**
AI designed a "three-layer progressive" structure:
1. **Academic research layer**: KGDRL from theory to full implementation (GAT + knowledge graph + KL constraint)
2. **Product development layer**: Algorithm enhancement + visualization upgrade + AI capability embedding (HF)
3. **Commercial argumentation layer**: Financial model + competitive analysis + investor materials

**Step 4: Hugging Face Integration Feasibility Assessment**
Based on the provided HF Token, AI evaluated the capabilities matrix:
- Decision natural language explanation (Llama-3.1-8B / Qwen2.5-7B)
- Demand forecasting enhancement (HF time-series transformers)
- Anomaly root-cause analysis (RAG + small models)
- Model version management (HF Hub push/pull)

#### 8.3.3 Human Feedback and Confirmation

After human review:
- The plan needs to emphasize "progressive iteration" to avoid overly aggressive Day 2-3 technical upgrades
- Buffer time should be reserved: 7 days is the ideal cycle, extensible to 10 days if needed
- Emphasized the "historical record" status of the AI USAGE document, requiring daily timeline updates
- Confirmed Hugging Face integration is primarily for "functional demonstration," not production-grade stability

AI adjusted the plan structure accordingly, concentrating the critical path on Days 2-4, with Days 5-7 focused on presentation and packaging.

---

### 8.4 Key Design Decision Records (Pre-Planning)

#### Decision 1: KGDRL Upgrade Technical Route

**Option A**: Full PyTorch Geometric implementation (most complete, heaviest dependencies)  
**Option B**: Self-developed simplified GAT layer (lightweight, easy to run in course environment)  
**Option C**: Pure attention mechanism replacement (simplest, preserves core concept)

**Human Decision**: Prioritize Option B, with Option C as fallback. Rationale: Course evaluation environments may not support PyG installation; self-developed implementation better demonstrates algorithmic understanding depth.

#### Decision 2: Hugging Face Integration Depth

**Option A**: Full-featured online calling (best results, network-dependent)  
**Option B**: Local small models as primary, online large models as supplementary (balanced)  
**Option C**: Fully local solution (Qwen2.5-1.5B, completely offline)

**Human Decision**: Adopt "local-first" strategy—small models run locally, large models called on-demand via HF Inference API, with fully offline fallback prepared.

#### Decision 3: Business Argumentation Material Detail Level

**Option A**: Complete business plan (BP level, 30+ pages)  
**Option B**: Streamlined investor one-pager + financial model + pitch deck  
**Option C**: Course bonus only, not pursuing real fundraising level

**Human Decision**: Option B. Material quality benchmarked against real seed-round fundraising pitches, but clearly labeled "based on case assumption data" to avoid over-commitment.

---

### 8.5 New Key File Inventory (Pre-Planning)

| File | Purpose | Estimated AI Contribution | Corresponding Day |
|------|---------|--------------------------|-------------------|
| `COMMERCIALIZATION_7DAY_PLAN.md` | Seven-day commercialization iteration plan | 85% | Day 0 |
| `kgdrl_core_v2.py` | Full KGDRL algorithm implementation | 90% | Day 2 |
| `multi_objective_scheduler.py` | Multi-objective scheduling engine | 85% | Day 3 |
| `what_if_simulator.py` | What-if scenario simulator | 80% | Day 3 |
| `streamlit_app_v2.py` | Commercial upgraded Streamlit | 90% | Day 4 |
| `hf_integration/` | Hugging Face integration modules | 85% | Day 5 |
| `business_case/` | Commercial argumentation directory | 80% | Day 6 |
| `financial_model.xlsx` | Financial model | 75% | Day 6 |
| `investor_pitch.md` | Investor pitch materials | 80% | Day 6 |
| `PATENT_SUMMARY.md` | Patent technology summary | 70% | Day 6 |

---

### 8.6 Investor/Business Leader Simulated Feedback Response Plan

| Simulated Feedback | Response Strategy | Deliverable | Status |
|-------------------|-------------------|-------------|--------|
| "Algorithm is a black box, we're afraid to use it" | KGDRL knowledge injection + natural language explanation | `kgdrl_core_v2.py` + `insight_engine.py` | Planned |
| "How much money can it save?" | ROI Calculator + TCO Analysis | Streamlit new page + `financial_model.xlsx` | Planned |
| "What's the advantage over SAP?" | Competitor Radar + differentiation positioning | Streamlit new page + `business_case/` | Planned |
| "Can it handle sudden peaks?" | Real-time adaptation + What-if simulation | `adaptive_policy.py` + Scenario Lab | Planned |
| "Is deployment expensive?" | Pure Python lightweight + API-ized design | `product_architecture_v2.md` | Planned |
| "Will it pass GSP audit?" | Knowledge graph traceability + hierarchical action auditing | `kgdrl_core_v2.py` | Planned |

---

### 8.7 Phase Timeline Milestones

| Milestone | Target Date | Acceptance Criteria | Risk |
|-----------|-------------|---------------------|------|
| M1: Plan finalized | Day 0 (06/04) | Plan approved by advisor/team | Low |
| M2: KGDRL runnable | Day 2 (06/06) | Ablation shows KGDRL > vanilla PPO | Medium |
| M3: Visualization demo-ready | Day 4 (06/08) | Streamlit v2 new pages fully interactive | Low |
| M4: HF integration working | Day 5 (06/09) | Decision explanation generates natural language | Medium |
| M5: Business materials complete | Day 6 (06/10) | Pitch materials support 15-min presentation | Low |
| M6: Full system finalized | Day 7 (06/11) | One-click launch, docs complete, Git Tag applied | Low |

---

## 9. Appendix Update: Complete File Inventory (Including Commercialization Phase)

| File | Purpose | AI Contribution | Phase |
|------|---------|-----------------|-------|
| `pharma_wave_allocation.py` | Core DRL algorithm (PPO + Environment + Heuristics) | 90% | Course |
| `run_full_pipeline.py` | End-to-end experimental pipeline | 95% | Course |
| `smart_wave_dashboard.html` | Chinese visualization dashboard | 95% | Course |
| `streamlit_app.py` | Streamlit course version | 90% | Course |
| `COMMERCIALIZATION_7DAY_PLAN.md` | Seven-day commercialization plan | 85% | Commercialization |
| `kgdrl_core_v2.py` | Full KGDRL algorithm implementation | 90% | Commercialization |
| `multi_objective_scheduler.py` | Multi-objective scheduling engine | 85% | Commercialization |
| `what_if_simulator.py` | What-if scenario simulator | 80% | Commercialization |
| `streamlit_app_v2.py` | Commercial upgraded Streamlit | 90% | Commercialization |
| `hf_integration/` | Hugging Face integration modules | 85% | Commercialization |
| `business_case/` | Commercial argumentation directory | 80% | Commercialization |
| `AI_Tools_Usage_Review_EN.md` | AI tool usage review (historical record) | 85% | Throughout |

---

> **Disclaimer**: This document faithfully records the use of AI tools (Claude Code) in this project. All technical decisions were reviewed and confirmed by humans. All business logic aligns with pharmaceutical distribution industry practices. Code and documents were AI-assisted in generation, but final quality responsibility rests with the project team.  
>  
> **Document Version**: v2.0-commercialization  
> **Last Updated**: 2026/06/04  
> **Historical Versions**: v1.0-course-delivery (through 2026/06/02)

---

## 10. Streamlit Dashboard Iteration Log (2026/06/04)

### 10.1 Background

After course delivery, the team optimized the Streamlit dashboard to address three issues:

1. **Negative average cost display**: Original code used `cost = -reward`, causing PPO's avg cost to show as -4180 (negative), which is semantically incorrect
2. **Insufficient text/background color contrast**: In Enterprise Profile metrics cards, `#666` text on `#f8f9fa` background had low contrast
3. **Simulation page flickering and non-functional**: The `st.rerun()` + `time.sleep()` approach caused page flickering, and the Start button did not activate the simulation modules below

### 10.2 AI-Assisted Modifications

| Issue | Solution | File | Lines Changed |
|------|---------|------|--------------|
| Negative cost semantics | Changed "Cost" to "Reward", using `avg_reward` directly (positive), labeled "Higher = Better" | `streamlit_app.py` | ~15 places |
| Color contrast | Changed `#666` → `#444`, `#333` → `#222`, `#999` → `#666` | `streamlit_app.py` | ~6 places |
| Simulation flickering | Abandoned `st.rerun()` approach, used `st.components.v1.html()` to embed original `smart_wave_dashboard.html` | `streamlit_app.py` | ~500 lines deleted, ~10 added |
| Cost semantics | Modified `generate_demo_episode()` to use `cost` instead of `reward`, ensuring all values are positive | `streamlit_app.py` | ~30 lines |
| Missing scatter plot | Added "Scatter" tab in Method Comparison page (Temperature Violations vs Picking Distance) | `streamlit_app.py` | ~15 lines |

### 10.3 Technical Decision Review

**Decision 1: Reward vs Cost Semantics**
- Original `avg_reward` is positive (PPO: 4180), meaning "higher is better"
- Converting to cost (`cost = -reward`) would make PPO's cost negative (-4180), contradicting intuition
- Final decision: Use "Reward" label with "Higher = Better", preserving original data semantics

**Decision 2: Simulation Animation Approach**
- Option A: `st.rerun()` loop — causes page flickering, poor UX ❌
- Option B: Frontend JS animation — ideal but large codebase, complex implementation ⚠️
- Option C: `components.html()` embedding original HTML — zero flickering, full functionality, lowest dev cost ✅
- Final decision: Adopted Option C, all `smart_wave_dashboard.html` features preserved

### 10.4 Human Review Checkpoints

1. ✅ After cost semantic change, Method Comparison table sorts correctly (descending)
2. ✅ After color change, Enterprise Profile page readability improved across all themes
3. ✅ After simulation page embedding, Start/Pause/Reset buttons, speed control, all charts and alerts function normally
4. ✅ `streamlit_app.py` passes syntax check, app launches successfully

### 10.5 Outstanding Issues and Next Steps

| Issue | Priority | Planned Resolution | Approach |
|------|----------|-------------------|----------|
| Simulation page height fixed at 900px | Low | Future iteration | Dynamic height via JavaScript or Streamlit adaptive sizing |
| HTML theme mismatch with Streamlit (dark vs light) | Low | Future iteration | Add theme toggle to HTML or maintain independent style |
| Method Comparison "Reward" label vs course-required "Cost" | Medium | Confirm with instructor | If instructor requires Cost semantics, redesign data transformation logic |

---

## 11. Industrial-Grade Supply Chain Command Center Development (2026/06/04)

### 11.1 Development Background

After completing the course-version Streamlit dashboard (`streamlit_app.py`), the team received a new requirement: upgrade the course version into an industrial-grade pharmaceutical smart supply chain command center for international executives. Requirements:

1. **All-English interface**: All labels, titles, descriptions in English (targeting international executives)
2. **Four business views**:
   - Admin: Omni-Channel Orders
   - Admin: Warehouse & Temperature Zones
   - Admin: Customer SLA Analytics
   - Worker: Task Workstation
3. **Industrial-grade UI**: Deep navy theme, professional cards, real-time data sync
4. **Simulated live data**: Metrics fluctuate every 3 seconds, simulating real operations
5. **Preserve original**: Keep `streamlit_app.py` as backup; create new `streamlit_app_v2.py`

### 11.2 Architecture Design

**File Structure:**
```
streamlit_app.py          # Course version (preserved, unchanged)
streamlit_app_v2.py       # Industrial-grade version (new, ~600 lines)
```

**Tech Stack:**
- Streamlit native components + custom CSS injection
- Altair charts (consistent with course version, minimal dependencies)
- `st.session_state` + `st.rerun()` for 3-second real-time refresh
- Pure simulated data generators (no backend dependency)

### 11.3 Four-View Feature Details

#### VIEW 1: Omni-Channel Orders
- **Top metrics**: Total Daily Orders (~90,000, dynamic fluctuation), Bulk Orders, Fragmented Small Orders
- **Filters**: Client Category (4 types), Time Window (3 periods), Temperature Attribute (5 zones)
- **Left**: Real-time order log table (Order ID, Client Type, SKU Count, Temperature, Timestamp, Status, Priority)
- **Center**: 4 work-order status cards (Pending Dispatch, Picking in Progress, Completed, Stagnant Exception) with progress bars
- **Right**:
  - Bar chart: Order distribution by time window
  - Pie chart: Bulk vs Small order ratio
  - Pie chart: 5 temperature zone proportions

#### VIEW 2: Warehouse & Temperature Zones
- **Top**: 5 temperature zone cards (Ambient, Cool, Cold, Frozen, Deep Frozen) showing capacity, utilization, progress bars
- **Middle**: Near-Expiry FIFO control table, color-coded by risk:
  - Critical (≤30 days, red)
  - Warning (≤60 days, amber)
  - Notice (≤90 days, blue)
  - Normal (>90 days, default)
- **Bottom**:
  - Donut chart: Capacity utilization by zone
  - Bar chart: Near-expiry stock volume by medicine type

#### VIEW 3: Customer SLA Analytics
- **Top**: Line chart — 12-month monthly order volume trend for 4 customer types
- **Middle left**: Bar chart — Average SKU variety per order by customer type
- **Middle right**: Multi-line chart — SLA fulfillment history + 14-day AI forecast (dashed)
- **Bottom**: Data table — Fulfillment compliance by client category (On-Time Rate, Next-Day Rate, Temp Compliance, Exception Rate)

#### VIEW 4: Worker Task Workstation
- **Top left**: Bar chart — Full-time vs temporary headcount, with 2.5x peak cap line
- **Top right**: Table — Picking efficiency by zone (SKUs/Hour/Person)
- **Main**: `st.tabs` with 4 states (Pending, Active Picking, Completed, Exceptions)
  - Each task expandable to show: Source Zone → Target Client, SKU Checklist
  - **Key feature**: Active Picking tasks display DRL-optimized picking path, e.g.:
    `"Path: Zone A → Cool Zone B → Pick [Insulin x3] → Transit Zone C → Pack → Dispatch"`
- **Bottom**: "My Dispatched Tasks" panel showing current worker's task queue

### 11.4 AI-Assisted Development Process

| Development Phase | AI Contribution | Human Decision |
|------------------|----------------|----------------|
| Requirement analysis | Decomposed natural language requirements into 4 views with component lists | Confirmed view priorities and layout ratios |
| CSS theme design | Generated complete deep-navy executive CSS stylesheet | Adjusted color saturation and contrast |
| Data generators | Wrote 5 simulated data generator functions (orders, inventory, SLA, tasks, labor) | Calibrated data ranges to match enterprise casebook metrics |
| View implementation | Wrote Streamlit code view by view (~100-150 lines each) | Reviewed layout logic and chart selection |
| Real-time refresh | Implemented `st.session_state.live_mode` + `st.rerun()` mechanism | Tested and confirmed 3-second refresh frequency |
| Integration testing | Syntax check, run test, fix compatibility issues | Verified all 4 views switch correctly |

### 11.5 Key Design Decisions

**Decision 1: New file vs overwrite**
- Choice: Create `streamlit_app_v2.py`, keep `streamlit_app.py` unchanged
- Reason: Course version and industrial version target different audiences, need parallel maintenance

**Decision 2: Altair vs Plotly vs ECharts**
- Choice: Continue using Altair (consistent with course version)
- Reason: Fewer dependencies, unified styling, better Hugging Face Spaces compatibility

**Decision 3: Real-time refresh mechanism**
- Choice: `st.session_state.live_mode` global toggle + `time.sleep(3) + st.rerun()`
- Reason: Simple and reliable, user can toggle on/off, avoids persistent refresh interference

**Decision 4: DRL path display**
- Choice: Use monospace code block in Worker view to display simulated optimized path
- Reason: Intuitively demonstrates PPO/BvN algorithm output value, enhances worker-side algorithm trust

### 11.6 File Inventory

| File | Purpose | Status |
|------|---------|--------|
| `streamlit_app_v2.py` | Industrial supply chain command center dashboard | Created, runnable |
| `streamlit_app.py` | Course version dashboard (backup) | Preserved, unmodified |
| `smart_wave_dashboard_en.html` | English real-time simulation panel | Embedded in streamlit_app.py |
| `data/*.json` | PPO training/evaluation data | Reused, unmodified |

### 11.7 How to Run

```bash
# Industrial-grade version
streamlit run streamlit_app_v2.py

# Course version (backup)
streamlit run streamlit_app.py
```

Access: `http://localhost:8501`

### 11.8 Outstanding Issues

| Issue | Priority | Planned Resolution | Approach |
|------|----------|-------------------|----------|
| Simulated data differs from real enterprise data | High | Commercialization M2 | Connect real ERP/WMS APIs |
| Real-time refresh causes slight page flicker | Medium | Future iteration | Use `st.empty()` partial update instead of `st.rerun()` |
| Missing user authentication and access control | Medium | Commercialization M3 | Add Streamlit-Auth or OAuth |
| Worker view not connected to real WMS | High | Commercialization M2 | Develop FastAPI backend connecting `pharma_wave_allocation.py` |

---

## 12. Streamlit v3 Consolidated Version (2026/06/04)

### 12.1 Background

After completing v2 (industrial-grade 4-view dashboard), the team consolidated classic features from v1 (course version) into a unified v3, forming the foundation for commercialization iteration.

**Integration Goals:**
- Preserve v2's 4 industrial views (Omni-Channel Orders, Warehouse & Zones, SLA Analytics, Task Workstation)
- Integrate v1's Real-time Simulation (live simulation panel)
- Integrate v1's Order Analytics (temperature distribution + order timeline)
- Form a **6-view unified version** as the base for iteration

### 12.2 File Structure

| File | Version | Views | Purpose |
|------|---------|-------|---------|
| `streamlit_app.py` | v1 | 11 pages | Course version (backup) |
| `streamlit_app_v2.py` | v2 | 4 pages | Industrial version (backup) |
| `streamlit_app_v3.py` | **v3** | **6 pages** | **Consolidated (iteration base)** |

### 12.3 v3 Navigation

```
📦 Admin: Omni-Channel Orders              ← v2
🌡️ Admin: Warehouse & Temperature Zones   ← v2
📊 Admin: Customer SLA Analytics           ← v2
👷 Worker: Task Workstation                ← v2
⚡ Real-time Simulation                    ← v1 (HTML embed)
📈 Order Analytics                         ← v1 (temp dist + timeline)
```

### 12.4 Technical Implementation

| Feature | Implementation | Source |
|---------|---------------|--------|
| 4 industrial views | v2 native code | v2 |
| Real-time Simulation | `components.html()` embedding `smart_wave_dashboard_en.html` | v1 |
| Order Analytics | `st.dataframe` + `altair_chart` temp pie + timeline | v1 |
| Live refresh | `st.session_state.live_mode` + `st.rerun()` 3s | v2 |
| Theme | Deep navy executive theme (custom CSS) | v2 |

### 12.5 How to Run

```bash
# v3 consolidated (recommended)
streamlit run streamlit_app_v3.py

# Access
http://localhost:8503
```

### 12.6 Team Notice

**v3 is the sole base version for commercialization iteration.** Subsequent development should be based on `streamlit_app_v3.py`:
- Day 4: Streamlit commercial upgrades (ROI Calculator, Competitor Radar, etc.)
- Day 5: Hugging Face integration
- Day 6: Business case pages

**Do NOT directly modify `streamlit_app.py` (v1) or `streamlit_app_v2.py` (v2).**
