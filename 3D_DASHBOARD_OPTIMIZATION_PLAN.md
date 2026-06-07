# Sunergy Pharma Pro v4.0 — 3D Dashboard Optimization Plan

> **Status:** Analysis Phase — Awaiting Approval Before Implementation  
> **Date:** 2026/06/07  
> **Scope:** Command Center 3D Visualization Refactor

---

## 1. Current State Diagnosis

### 1.1 Animation Bugs

| Symptom | Root Cause |
|---------|-----------|
| Warehouse Zone Cube rotates | JS `setInterval` on `plotly-graph-div[0]` works |
| Order Flow Galaxy **static** | JS `setInterval` on `plotly-graph-div[1]` fails — likely because `to_html()` generates isolated iframes/divs without guaranteed index ordering |
| No user control | Animation starts immediately on page load; no pause/resume mechanism |
| Distracting UX | Auto-rotation on load interrupts user reading metric cards below |

### 1.2 Data Readability Issues

**Chart 1: Warehouse Zone Cube (Current)**
```
X = Temperature Zone     (5 discrete values: Ambient, Cool, Cold, Frozen, Deep Frozen)
Y = "Warehouse"          (constant — wastes a dimension)
Z = Stock Qty            (single-metric, no time dimension)
```
**Problems:**
- Only 5 data points in 3D space — barely justifies a 3D visualization
- Y-axis carries zero information
- "Stock Qty" is operational, but not **strategic** — investors and CFOs don't care about absolute stock levels

**Chart 2: Order Flow Galaxy (Current)**
```
X = Order Sequence       (0-200 index, no intuitive meaning)
Y = SKU Count            (1-5, tightly clustered)
Z = Deadline Hours       (2-24, overlaps heavily)
```
**Problems:**
- 150 scatter points overlap in a narrow corridor (Y: 1-5, Z: 2-24)
- Color-by-temperature adds a 4th dimension but worsens clutter
- No clear business question answered — "So what?" factor is low

---

## 2. Optimization Strategy

### 2.1 Guiding Principle

> **"Every 3D axis must answer an investor or operations director question."**

| Stakeholder | Questions They Ask | 3D Axis Mapping |
|-------------|-------------------|-----------------|
| **CFO** | "Where do we make/lose money? When do we break even?" | Z-axis = Cash Flow / Cumulative ROI |
| **COO** | "Which shift/zone is most efficient? Where are our bottlenecks?" | X/Y axes = Time × Zone |
| **Investor** | "What's the downside? What's the upside?" | Y-axis = Scenario (Conservative→Optimistic) |
| **Warehouse Manager** | "When should I allocate more pickers?" | Z-axis = Workload Density |

---

## 3. Proposed New 3D Charts

### 3.1 Chart 1: Operational Profit Mountain
**Replaces:** Warehouse Zone Cube

**Concept:** A 3D surface/mountain showing **where and when profit is generated** across temperature zones and time periods.

```
X-axis: Time of Day (0h – 24h, 4-hour bins: Night/Early/Morning Peak/Afternoon/Evening)
Y-axis: Temperature Zone (Ambient, Cool, Cold, Frozen, Deep Frozen)
Z-axis: Net Operational Value (CNY/hour)
        = (Orders Processed × Avg Margin per Order)
          – (Picker Labor Cost)
          – (Temperature Violation Penalties)
          – (Expired Inventory Write-off)
```

**Why this matters:**
- **CFO** sees which shift/zone combinations are most profitable
- **COO** identifies loss-making periods (e.g., "Deep Frozen at Night costs more than it earns")
- **Investor** sees operational efficiency as a **surface** rather than a table

**Visual Design:**
- 3D Surface plot with `go.Surface`
- Color scale: deep red (loss) → yellow (break-even) → green (profit)
- Peaks = high-profit zone-time combinations
- Valleys = inefficiencies to address
- **Animation:** Time-lapse sweep (optional) showing how the mountain changes from Monday→Sunday

**Data Source:**
- Uploaded `orders.csv` + `inventory.csv` → compute margins and costs
- Fallback: mock data with realistic pharma margins (Ambient: ¥12/order, Cold: ¥28/order, Frozen: ¥45/order)

---

### 3.2 Chart 2: Investment Trajectory Ribbon
**Replaces:** Order Flow Galaxy

**Concept:** A 3D ribbon/surface showing **cumulative cash flow over 5 years under 4 scenarios**.

```
X-axis: Time (Months 0 – 60)
Y-axis: Scenario
        1 = Without Sunergy (status quo, baseline cost growth)
        2 = Conservative (15% efficiency gain, slow adoption)
        3 = Neutral (25% efficiency gain, expected adoption)
        4 = Optimistic (35% efficiency gain, rapid scaling)
Z-axis: Cumulative Cash Flow (CNY)
        = Saved Labor + Saved Violations + Saved Write-offs
          – Sunergy Subscription Fees
          – Implementation Cost (Month 0)
```

**Why this matters:**
- **Investor** sees exact breakeven month under each scenario
- **CFO** sees worst-case (Conservative) still yields positive ROI by Month 14
- **Sales** uses this in demos: "Even if we're wrong by 50%, you still break even in under a year."

**Visual Design:**
- 3D Line plot with `go.Scatter3d`, mode='lines'
- 4 colored ribbons (gray=baseline, blue=conservative, amber=neutral, green=optimistic)
- Horizontal plane at Z=0 = breakeven line
- Vertical annotation at first positive-crossing point
- **Animation:** "Draw" the lines from Month 0 → Month 60, revealing trajectory progressively

**Data Source:**
- Derived from ROI Calculator parameters (daily orders, wage, warehouses)
- Computed in real-time from user inputs — no CSV upload needed

---

## 4. Animation Control Design

### 4.1 Desired Behavior

| State | Behavior |
|-------|----------|
| **Initial Load** | Both charts are **static** (camera fixed at optimal angle) |
| **User Hover** | Standard Plotly tooltip works normally |
| **User Click Play** | Smooth 360° orbit rotation begins (15 seconds per revolution) |
| **User Click Pause** | Rotation freezes at current angle |
| **User Drag** | Manual orbit overrides auto-rotation; resume from new angle on Play |

### 4.2 Implementation Approach

**Problem:** Plotly's JS auto-rotate via `setInterval` is fragile across iframe boundaries.

**Recommended Solution:** Use Plotly's built-in `updatemenus` with `frame` animations.

```python
fig.update_layout(
    updatemenus=[dict(
        type="buttons",
        showactive=False,
        buttons=[
            dict(label="▶ Play",
                 method="animate",
                 args=[None, {"frame": {"duration": 50, "redraw": False},
                               "fromcurrent": True,
                               "transition": {"duration": 0}}]),
            dict(label="⏸ Pause",
                 method="animate",
                 args=[[None], {"frame": {"duration": 0, "redraw": False},
                                "mode": "immediate",
                                "transition": {"duration": 0}}]),
        ],
        x=0.1, y=0, xanchor="left", yanchor="top"
    )]
)

# Pre-compute rotation frames
frames = []
for angle in range(0, 360, 2):
    r = 1.8
    x = r * np.cos(np.radians(angle))
    y = r * np.sin(np.radians(angle))
    frames.append(go.Frame(
        layout=dict(scene=dict(camera=dict(eye=dict(x=x, y=y, z=1.0))))
    ))
fig.frames = frames
```

**Advantages:**
- Native Plotly buttons — no custom JS injection
- Works reliably inside Streamlit `components.html`
- User can drag to explore, then click Play to resume auto-orbit
- Clean separation of concern: Python generates frames, Plotly handles playback

---

## 5. Implementation Scope

### Phase A: Animation Fix (Low Effort, High UX Impact)
- Remove fragile `setInterval` JS injection
- Add Plotly `updatemenus` Play/Pause buttons
- Set initial camera to static, optimal angle
- Ensure both charts have identical control mechanics

### Phase B: Chart 1 — Operational Profit Mountain (Medium Effort)
- Build `compute_profit_surface()` function in `shared.py`
- Generate 5 (zones) × 6 (time bins) grid
- Map to `go.Surface` with Viridis→RdYlGn color scale
- Connect to uploaded orders/inventory if available

### Phase C: Chart 2 — Investment Trajectory Ribbon (Medium Effort)
- Build `compute_cash_flow_trajectory()` function
- Generate 4 scenarios × 60 months
- Map to `go.Scatter3d` with mode='lines'
- Add breakeven plane annotation
- Auto-link to ROI Calculator inputs for real-time updates

### Phase D: Polish (Low Effort)
- Responsive height for mobile/tablet
- Loading spinner while 3D renders
- "Reset View" button

**Estimated Total Effort: 1 day**

---

## 6. Risk & Fallback

| Risk | Mitigation |
|------|-----------|
| `go.Surface` performance on large grids | Grid is only 5×6 = 30 points — negligible |
| Play/Pause buttons not visible in dark theme | Custom button styling via `updatemenus.buttonargs` |
| User has older Plotly version without `updatemenus` | Feature-detect and fall back to static 3D |
| 3D charts feel gimmicky to conservative investors | Phase A ensures static default; animation is opt-in |

---

## 7. Decision Required

Please confirm:

1. **Approve Phase A** (animation fix + Play/Pause controls)?
2. **Approve Phase B** (Operational Profit Mountain replacing Zone Cube)?
3. **Approve Phase C** (Investment Trajectory Ribbon replacing Order Galaxy)?
4. **Approve all three** and proceed with implementation?

Once approved, I will implement in `streamlit_app_pro_v4.py` without modifying the underlying page modules.
