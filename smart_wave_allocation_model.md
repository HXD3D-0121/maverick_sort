# Smart Wave Allocation for Pharmaceutical Distribution: A Deep Reinforcement Learning Approach

## 1. Background and Problem Description

### 1.1 Enterprise Context

The case enterprise is one of China's leading pharmaceutical distribution companies, operating a nationwide integrated wholesale-retail-storage-distribution system with the following key metrics:

| Metric | Data |
|--------|------|
| Logistics Centers | 128 (incl. 6 central warehouses) |
| Distribution Stations | 856 |
| Warehouse Area | 2.65M sqm (GSP-standard) |
| Annual Throughput | >90M cases |
| Product Lines (SKU) | 423,600 |
| Daily Orders | >90,000 |
| Next-Day Delivery Rate | >88% |

### 1.2 Core Challenges

1. **SKU Complexity**: 38% are near-expiry managed items with varying temperature requirements (ambient, cool, cold, frozen)
2. **Order Fragmentation**: >36,000 daily active customers, mostly small-batch multi-SKU orders averaging 3-5 items
3. **Time Pressure**: >88% next-day delivery requires same-day sorting and dispatch; peak periods spike volume by 280%
4. **Labor Bottleneck**: Manual sorting with ~0.35% error rate and annual return losses exceeding RMB 9M
5. **Temperature Segregation**: Pharmaceutical products require strict temperature-zone compliance during picking

### 1.3 Smart Wave Allocation Problem

**Smart wave allocation** refers to the real-time grouping of incoming orders into "waves" (batches) for coordinated picking operations. Each wave is assigned to a picker or picking team, and the quality of wave allocation directly determines:

- **Picking path efficiency**: Orders with SKUs in proximate locations should be grouped together
- **Temperature compliance**: Orders with similar temperature requirements should be batched to avoid cross-zone contamination
- **Throughput capacity**: Wave size must balance picker capacity and conveyor system limits
- **Delivery deadline satisfaction**: Orders with tighter deadlines must be prioritized into earlier waves

---

## 2. Applicability Analysis: KGDRL Paradigm for Order Dispatch

### 2.1 KGDRL Core Characteristics

The Knowledge-Guided Deep Reinforcement Learning (KGDRL) paradigm, as demonstrated in the Job Shop Reconfiguration Scheduling (JSRS) problem, features:

1. **Structured Action Space**: Actions are drawn from a discrete, combinatorial set of (machine, job, stage) tuples
2. **Domain Knowledge Integration**: Shortest-Transfer-Shortest-Process (STSP) heuristics guide action selection probabilities
3. **Masking Mechanism**: Illegal actions are masked out via action validity indicators
4. **Graph-based State Representation**: Job-machine-stage relationships are encoded as heterogeneous graphs

### 2.2 Applicability to Smart Wave Allocation

| Dimension | JSRS (Original KGDRL) | Smart Wave Allocation | Assessment |
|-----------|----------------------|----------------------|------------|
| **Decision Timing** | Event-driven (machine idle) | Discrete time steps or order arrival events | Adaptable |
| **Action Structure** | (machine, job, stage) | (order, wave) assignment or (zone, priority) | Analogous |
| **Domain Knowledge** | STSP: shortest transfer/setup time | Temperature-first, zone-proximity, EDD | Transferable |
| **State Complexity** | Static job routes, known processing times | Dynamic order arrivals, stochastic demand | More complex |
| **Constraints** | Machine eligibility, precedence | Temperature segregation, capacity, deadlines | Comparable |
| **Objective** | Minimize makespan | Minimize total picking cost + deadline penalties | Similar structure |

### 2.3 Verdict: Conditional Applicability

**KGDRL is applicable to smart wave allocation with the following adaptations:**

1. **State Space Extension**: Must incorporate temporal features (deadline urgency) and zone topology
2. **Knowledge Rules Redesign**: STSP rules must be replaced by pharmaceutical-specific heuristics (temperature-matching, zone-co-location, earliest-due-date)
3. **Online Learning Setting**: Unlike JSRS where all jobs are known upfront, wave allocation must handle streaming order arrivals

**Alternative Application Domain**: If the stochastic and online nature of order arrivals makes convergence too slow, the KGDRL paradigm can be readily redirected to **Dynamic Inventory Management** (Case 2), where:
- State = inventory levels across echelons
- Action = replenishment quantities
- Knowledge = (s, S) policies or base-stock heuristics
- The problem structure more closely resembles traditional inventory control MDPs

For this document, we proceed with the **Smart Wave Allocation** formulation, noting that the same algorithmic framework can be repurposed for dynamic inventory management by swapping the environment definition.

---

## 3. Mathematical Modeling

### 3.1 Notation and Sets

| Symbol | Description |
|--------|-------------|
| $\mathcal{T} = \{1, 2, \dots, T\}$ | Discrete time periods (e.g., 30-minute slots) |
| $\mathcal{O}_t$ | Set of orders arriving at time $t$ |
| $\mathcal{W}$ | Set of waves (batches) |
| $\mathcal{Z} = \{1, \dots, Z\}$ | Warehouse zones/aisles |
| $\mathcal{K} = \{\text{ambient}, \text{cool}, \text{cold}, \text{frozen}\}$ | Temperature categories |
| $o \in \mathcal{O}$ | An individual order |
| $w \in \mathcal{W}$ | An individual wave |

**Order Attributes:**
- $n_o$: Number of SKUs in order $o$
- $z(o) \subseteq \mathcal{Z}$: Set of zones required by order $o$
- $\tau(o) \in \mathcal{K}$: Dominant temperature requirement of order $o$
- $d_o$: Delivery deadline (in time periods from now)
- $v_o$: Order volume/weight

**Wave Attributes:**
- $O_w \subseteq \mathcal{O}$: Orders assigned to wave $w$
- $t_w^{\text{start}}$: Start time of wave $w$
- $C_w^{\text{max}}$: Maximum capacity (orders or volume) of wave $w$

**Zone Topology:**
- $D(z_i, z_j)$: Distance (or travel time) between zones $z_i$ and $z_j$
- $p_z \in \mathbb{R}^2$: Physical coordinates of zone $z$

### 3.2 Problem Statement

Given a stream of orders arriving over time, dynamically assign each order to a wave such that:

1. **Temperature Compliance**: Orders in the same wave should share compatible temperature requirements
2. **Zone Proximity**: Orders requiring proximate zones should be batched together
3. **Capacity Limits**: Each wave respects picker capacity and conveyor throughput
4. **Deadline Satisfaction**: High-urgency orders are assigned to earlier waves
5. **Minimize Total Cost**: Picking travel distance + temperature violation penalties + deadline miss penalties + wave setup costs

### 3.3 Markov Decision Process (MDP) Formulation

We formulate smart wave allocation as a **finite-horizon Markov Decision Process** $M = (\mathcal{S}, \mathcal{A}, \mathcal{P}, \mathcal{R}, \gamma)$.

#### 3.3.1 State Space $\mathcal{S}$

A state $s_t \in \mathcal{S}$ at time $t$ comprises:

$$s_t = \left( s_t^{\text{wave}},\ s_t^{\text{pool}},\ s_t^{\text{time}},\ s_t^{\text{history}} \right)$$

**Current Wave State** $s_t^{\text{wave}}$:
- $N_w^t$: Number of orders currently in the active wave
- $V_w^t$: Total volume in the active wave
- $\mathbf{z}_w^t \in \{0,1\}^Z$: Binary zone coverage vector
- $\mathbf{k}_w^t \in \{0,1\}^4$: Binary temperature category coverage vector
- $t_w^{\text{age}}$: Time since current wave was opened

**Order Pool State** $s_t^{\text{pool}}$:
For each candidate order $o$ in the pool (truncated to top-$K$ candidates by urgency):
- $n_o$: SKU count
- $\bar{d}_o = d_o - t$: Remaining time until deadline
- $\tau(o)$: Temperature category (one-hot encoded)
- Centroid zone coordinates: $(\bar{x}_o, \bar{y}_o)$
- Compatibility scores with current wave

**Temporal State** $s_t^{\text{time}}$:
- $\rho_t = \frac{|\mathcal{O}_t^{\text{urgent}}|}{|\mathcal{O}_t|}$: Proportion of urgent orders (deadline $< \theta$)
- $\delta_t$: Time until next shift change or cutoff
- $\lambda_t$: Current order arrival rate (estimated)

#### 3.3.2 Action Space $\mathcal{A}$

The action $a_t \in \mathcal{A}$ at each step is:

$$a_t = \begin{cases}
o^* & \text{Add order } o^* \text{ from pool to current active wave} \\
\text{CLOSE} & \text{Close current wave, dispatch for picking, start new wave}
\end{cases}$$

If the action is to add an order, it must satisfy:
1. $N_w^t + 1 \leq C^{\text{max}}$ (capacity constraint)
2. Temperature compatibility (soft constraint, penalized if violated)

If no orders are in the pool, the only valid action is CLOSE or WAIT.

#### 3.3.3 State Transition $\mathcal{P}$

The transition $s_{t+1} \sim P(\cdot | s_t, a_t)$ follows:

1. If $a_t = o^*$: Order $o^*$ is removed from the pool and added to the active wave; wave state updates accordingly
2. If $a_t = \text{CLOSE}$: The active wave is dispatched; a new empty wave is created; the time advances by the wave processing time
3. New orders may arrive according to a Poisson process with rate $\lambda_t$

#### 3.3.4 Reward Function $\mathcal{R}$

The reward $r(s_t, a_t, s_{t+1})$ is designed to balance efficiency, compliance, and timeliness:

$$r(s_t, a_t, s_{t+1}) = r^{\text{efficiency}} + r^{\text{compliance}} + r^{\text{timeliness}} + r^{\text{setup}}$$

**Efficiency Component** (picking path):

$$r^{\text{efficiency}} = -\alpha_1 \cdot \Delta L$$

where $\Delta L$ is the incremental increase in the estimated picking tour length. We approximate this using the centroid distance:

$$L(w) \approx c_0 + c_1 \cdot \sum_{z \in Z_w} D(z_{\text{entry}}, z) + c_2 \cdot \text{TSP-approx}(Z_w)$$

For simplicity, we use the spanning-tree lower bound or nearest-neighbor heuristic.

**Compliance Component** (temperature segregation):

$$r^{\text{compliance}} = -\alpha_2 \cdot \sum_{k \in \mathcal{K}} \mathbb{1}_{[|O_w \cap \mathcal{O}_k| > 0 \text{ and } |\mathcal{K}_w| > 1]}$$

This penalizes waves that mix incompatible temperature categories.

**Timeliness Component** (deadline satisfaction):

$$r^{\text{timeliness}} = \alpha_3 \cdot \sum_{o \in O_w^{\text{closed}}} \mathbb{1}_{[t_w^{\text{finish}} \leq d_o]} - \alpha_4 \cdot \sum_{o \in O_w^{\text{closed}}} \max(0,\ t_w^{\text{finish}} - d_o)$$

**Setup Component**:

$$r^{\text{setup}} = -\alpha_5 \cdot \mathbb{1}_{[a_t = \text{CLOSE}]}$$

This penalizes closing a wave (equipment setup cost).

#### 3.3.5 Objective

The agent seeks to maximize the expected discounted cumulative reward:

$$\max_{\pi} \mathbb{E}\left[ \sum_{t=0}^{T} \gamma^t r(s_t, a_t, s_{t+1}) \mid s_0 \right]$$

where $\pi: \mathcal{S} \rightarrow \Delta(\mathcal{A})$ is the policy mapping states to action distributions.

### 3.4 Alternative: Dynamic Inventory Management MDP

If applied to dynamic inventory management (Case 2), the MDP becomes:

- **State**: Inventory levels $I_t \in \mathbb{R}^{|SKU|}$, pipeline orders, demand forecasts
- **Action**: Replenishment quantities $q_t \in \mathbb{R}^{|SKU|}$
- **Reward**: $r_t = -h \cdot I_t^+ - p \cdot I_t^- - c \cdot q_t$ (holding + stockout + ordering costs)
- **Transition**: $I_{t+1} = I_t + q_{t-L} - D_t$ (with lead time $L$)

This is a classical inventory control MDP more amenable to standard DRL methods.

---

## 4. Heuristic Algorithm Design

### 4.1 Rule-Based Baseline Heuristics

Before deploying DRL, we establish rule-based baselines adapted from classical scheduling and bin-packing heuristics:

| Heuristic | Rule | Pharmaceutical Interpretation |
|-----------|------|------------------------------|
| **TEMP-FIRST** | Group orders by dominant temperature category | Ensures GSP compliance |
| **ZONE-NN** | Add order minimizing distance to current wave centroid | Minimizes picking path |
| **EDD** | Prioritize orders with earliest due date | Maximizes on-time delivery |
| **FCFS** | First-come-first-serve | Simple baseline |
| **TEMP+ZONE** | Temperature-first, then zone-proximity within category | Two-level hierarchical |

### 4.2 Knowledge-Guided Heuristic for DRL

Inspired by the STSP (Shortest-Transfer-Shortest-Process) rule in KGDRL, we define a **pharmaceutical domain heuristic** called **TZU (Temperature-Zone-Urgency)**:

For each candidate order $o$ and current wave $w$, compute:

$$\text{TZU}(o, w) = \beta_1 \cdot \underbrace{\mathbb{1}_{[\tau(o) = \tau(w)]}}_{\text{Temperature Match}} + \beta_2 \cdot \underbrace{\frac{1}{1 + d(o, w)}}_{\text{Zone Proximity}} + \beta_3 \cdot \underbrace{\frac{1}{\bar{d}_o}}_{\text{Urgency}}$$

where $d(o, w)$ is the zone centroid distance between order $o$ and wave $w$.

This heuristic can be used in two ways:
1. **Standalone**: Select order maximizing TZU at each step
2. **DRL Guidance**: Initialize the policy network's action probabilities using TZU as a prior (knowledge injection)

For this initial implementation, we do **not** deploy the knowledge-guided structure; we use TZU only as a baseline comparison.

### 4.3 PPO-Based Deep Reinforcement Learning Algorithm

We adopt **Proximal Policy Optimization (PPO)** as the base algorithm, following the KGDRL implementation structure but without the knowledge graph module.

#### 4.3.1 Network Architecture

**Actor Network (Policy)** $\pi_\theta(a|s)$:
```
Input: State vector s_t (flattened)
  → FC(state_dim, hidden_dim) → ReLU
  → FC(hidden_dim, hidden_dim*2) → ReLU
  → FC(hidden_dim*2, hidden_dim) → ReLU
  → FC(hidden_dim, action_dim) → ReLU
  → Masked Softmax (over valid actions)
Output: Action probabilities
```

**Critic Network (Value)** $V_\phi(s)$:
```
Input: State vector s_t
  → FC(state_dim, hidden_dim) → ReLU
  → FC(hidden_dim, hidden_dim*2) → ReLU
  → FC(hidden_dim*2, hidden_dim) → ReLU
  → FC(hidden_dim, 1)
Output: State value estimate
```

**Key Design Choices**:
- **Action Masking**: Invalid actions (capacity exceeded, empty pool) are masked with zero probability
- **State Normalization**: L2 normalization over state features
- **Advantage Estimation**: GAE (Generalized Advantage Estimation) with $\lambda = 0.95$

#### 4.3.2 Training Procedure

```
Algorithm: PPO for Smart Wave Allocation
─────────────────────────────────────────
Initialize: Actor network π_θ, Critic network V_φ
            Replay buffer B
            Environment E

For episode = 1 to N:
    s_0 ← E.reset()
    trajectory ← []
    
    While not done:
        // State encoding
        state_vec, avail_mask ← encode_state(s_t)
        
        // Action selection
        prob ← π_θ(state_vec)
        prob_masked ← mask(prob, avail_mask)
        a_t ~ Categorical(prob_masked)
        
        // Environment step
        s_{t+1}, r_t, done ← E.step(a_t)
        
        // Store transition
        trajectory.append((s_t, a_t, r_t, s_{t+1}, prob, avail_mask, done))
    
    // Compute advantages
    For t = T-1 downto 0:
        δ_t = r_t + γ·V_φ(s_{t+1}) - V_φ(s_t)
        A_t = δ_t + γ·λ·A_{t+1}
    
    // PPO update (K epochs)
    For epoch = 1 to K:
        Sample minibatch from trajectory
        Compute ratio: ratio = π_θ_new(a|s) / π_θ_old(a|s)
        Compute surrogate objectives:
            L^CLIP = -min(ratio·A, clip(ratio, 1-ε, 1+ε)·A)
        Update actor: θ ← θ - α_θ · ∇_θ L^CLIP
        Update critic: φ ← φ - α_φ · ∇_φ (V_φ(s) - R)^2
        
        // Gradient clipping
        clip_grad_norm(∇_θ, 0.5)
        clip_grad_norm(∇_φ, 0.5)
```

#### 4.3.3 State Encoding Details

The state vector is constructed by concatenating:

| Component | Dimension | Description |
|-----------|-----------|-------------|
| Wave features | 4 | Orders count, volume, age, zone spread |
| Wave zone mask | Z | One-hot covered zones |
| Wave temp mask | 4 | One-hot covered temperatures |
| Top-K order features | K × 6 | Per order: SKU count, deadline, temp, x, y, urgency |
| Global stats | 3 | Urgent ratio, time to cutoff, arrival rate |
| **Total** | **7 + Z + 4 + 6K** | (e.g., Z=8, K=10 → ~79 dim) |

---

## 5. Data Generation via Empirical Distributions

### 5.1 Empirical Distributions from Casebook

Based on the enterprise data, we construct the following generative model:

**Order Arrival Process**:
- Base rate: $\lambda_{\text{base}} \sim \text{Poisson}(\mu = 90,000/\text{day})$
- Peak multiplier: With probability $p_{\text{peak}} = 0.05$, $\lambda_{\text{peak}} = 2.8 \times \lambda_{\text{base}}$
- Time-of-day pattern: Bimodal (9AM and 2PM peaks)

**Order Size Distribution**:
- $n_o \sim \text{Discrete}(\{3,4,5\},\ p = \{0.4, 0.35, 0.25\})$ (items per order)

**Temperature Category Distribution**:
- Ambient: 55%
- Cool: 25%
- Cold: 15%
- Frozen: 5%

**Zone Distribution**:
- Zones $Z = 8$, arranged in a 2×4 grid
- Each SKU assigned to one zone uniformly at random
- Each order draws $n_o$ zones with replacement

**Deadline Distribution**:
- Standard orders: $d_o \sim \text{Uniform}(8, 24)$ hours
- Urgent orders: $d_o \sim \text{Uniform}(2, 6)$ hours (20% of orders)

**Warehouse Topology**:
- Zones arranged in a grid with Manhattan distances
- Entry/exit point at corner

### 5.2 Simulation Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| Simulation horizon | 8 hours / 480 minutes | One shift |
| Time step | 1 minute | Decision granularity |
| Wave capacity (orders) | 20-50 | Picker capacity |
| Wave capacity (volume) | 500 units | Tote/cart limit |
| Picking speed | 60 m/min | Industry standard |
| Setup time per wave | 10 min | Equipment preparation |
| Temperature penalty | -100 | GSP violation cost |
| Deadline miss penalty | -50 per hour | Customer satisfaction |

---

## 6. Numerical Experiment Design

### 6.1 Experiment Setup

1. **Training Phase**: Train PPO agent for 500 episodes on synthetic data
2. **Validation Phase**: Evaluate on 50 hold-out instances
3. **Benchmarking**: Compare against rule-based heuristics (TEMP-FIRST, ZONE-NN, EDD, FCFS, TZU)

### 6.2 Evaluation Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| **Total Cost** | $\sum_w (L_w + P_w^{\text{temp}} + P_w^{\text{deadline}} + S_w)$ | Minimize |
| **On-Time Rate** | $\frac{|\{o: t_w(o) \leq d_o\}|}{|\mathcal{O}|}$ | >88% |
| **Temperature Compliance** | $\frac{|\{w: |\mathcal{K}_w| = 1\}|}{|\mathcal{W}|}$ | 100% |
| **Avg Wave Size** | $\frac{1}{|\mathcal{W}|} \sum_w |O_w|$ | Maximize (up to capacity) |
| **Picking Efficiency** | $\frac{\text{Total items picked}}{\text{Total picking distance}}$ | Maximize |

### 6.3 Expected Results

Based on JSRS experience:
- PPO should outperform random and simple FCFS by 15-25%
- PPO should match or slightly exceed composite heuristics (TZU)
- Knowledge injection (future work) should provide additional 5-10% improvement

---

## 7. Extension Path to Full KGDRL

The current implementation uses "vanilla" PPO without knowledge guidance. The extension to full KGDRL involves:

1. **Knowledge Graph Construction**:
   - Nodes: Orders, Zones, Temperature categories
   - Edges: Zone adjacency, temperature compatibility, order similarity

2. **Graph Neural Network (GNN) Encoder**:
   - Replace MLP state encoder with Graph Attention Network (GAT)
   - Capture relational structure between orders and warehouse topology

3. **Heuristic Policy Prior**:
   - Initialize actor output with TZU scores
   - Add KL-divergence regularization: $L_{\text{KG}} = D_{\text{KL}}(\pi_\theta || \pi_{\text{TZU}})$

4. **Structured Action Sampling**:
   - Use hierarchical action selection: first temperature, then zone, then specific order

---

## 8. Conclusion

This document presents a complete MDP formulation of the Smart Wave Allocation problem for pharmaceutical distribution, adapted from the KGDRL research paradigm. The key contributions are:

1. **Problem Analysis**: KGDRL is conditionally applicable; the core challenge is the online, stochastic nature of order arrivals
2. **Mathematical Model**: A structured MDP with pharmaceutical-specific state features, action constraints, and multi-objective rewards
3. **Algorithm Design**: PPO-based DRL with action masking, following the KGDRL implementation pattern without the knowledge module
4. **Data Generation**: Empirical distributions grounded in the casebook enterprise data
5. **Evaluation Framework**: Comprehensive metrics balancing efficiency, compliance, and timeliness

The implementation (Jupyter notebook) provides a runnable prototype for experimentation and classroom demonstration.
