# Plan: Smart Batch Allocation for Pharma Warehouse

## 1. Problem Analysis

From the case background, the core batch allocation challenge is:

- **423,600 SKUs** across 5 temperature zones (ambient 60-70%, cool 15-20%, cold 5%, frozen <1%, controlled vault)
- **90,000+ orders/day**, mostly small-batch multi-SKU (3-5 items/order)
- **~38% near-expiry items** requiring strict FEFO (First-Expired-First-Out) at lot level
- **Multiple picking models**: Zone-picking with conveyor (primary), G2P, batch/cart picking
- **Peak volume spikes 280%** causing conveyor saturation, zone imbalance, tote shortage
- **SLA constraints**: Hospital morning delivery, pharmacy afternoon, B2B evening

The "smart batch allocation" problem = **grouping orders into waves/batches** such that:
1. Picking efficiency is maximized (minimize zone transitions, balance zone workload)
2. FEFO compliance is enforced (near-expiry lots get picked first)
3. Temperature compliance is maintained (minimize cross-zone tote movements)
4. SLA deadlines are met (hospital orders prioritized)
5. Peak capacity constraints are respected (conveyor throughput, zone picker limits)

## 2. Proposed Solution: Affinity-Score Wave Allocator (ASWA)

### Core Concept
Each order is assigned an **affinity fingerprint** (zones needed, temp classes, SLA urgency, size class). Orders with similar fingerprints are clustered into the same wave. Within each wave, a **FEFO lot pre-allocator** assigns specific lots to order lines before picking begins. Waves are then **dynamically sized** based on real-time zone capacity.

### Key Innovations
1. **Order Fingerprinting**: Vector representation capturing zone set, temperature mix, SLA tier, item count, controlled-substance flag
2. **Affinity Clustering**: Greedy clustering algorithm that maximizes intra-wave similarity (same zones = fewer tote transitions; same SLA = easier cutoff management)
3. **FEFO-Lot Pre-Allocator**: Before wave release, every order line is assigned a specific lot/bin. Near-expiry lots get priority. If a near-expiry lot is in reserve storage, the wave is flagged for pre-replenishment.
4. **Dynamic Wave Sizer**: Caps wave size based on (a) zone picker capacity, (b) conveyor tote capacity, (c) packing station throughput. During peaks, smaller waves are released more frequently to prevent bottlenecks.
5. **Bottleneck-Aware Release**: Predicts which zone will saturate based on wave composition, and throttles waves heavy in that zone.

### Why This Works for Pharma
- **FEFO compliance is built in**, not an afterthought
- **Temperature integrity**: clustering by temp zone minimizes cross-zone tote movements (critical for 2-8°C and -20°C items with time-out-of-zone limits)
- **Peak resilience**: dynamic wave sizing prevents the conveyor jams and zone flooding described in the case
- **Explainable**: affinity scores are transparent, important for GSP audit trails

## 3. Architecture

### Tech Stack
- **Backend**: Python + FastAPI
- **Data**: SQLite (demo data seeded from case metrics)
- **Optimization**: Pure Python heuristics (no heavy solvers — fast, explainable, easy to demo)
- **Frontend**: React + Recharts
- **Simulation**: Built into backend with configurable parameters

### Directory Structure
```
backend/
  app/
    main.py              # FastAPI entry point
    models.py            # Pydantic models (Order, SKU, Lot, Wave, Batch)
    allocator/
      fingerprint.py     # Order fingerprinting logic
      clustering.py      # Affinity clustering algorithm
      lot_allocator.py   # FEFO lot pre-allocation
      wave_sizer.py      # Dynamic wave sizing & bottleneck prediction
    data/
      generator.py       # Demo data generator
      db.py              # SQLite connection
    simulation/
      engine.py          # What-if scenario runner
    api/
      routes.py          # REST endpoints
frontend/
  src/
    pages/
      Dashboard.jsx      # Real-time wave status, zone load
      WavePlanner.jsx    # Create/view waves, affinity scores
      Simulation.jsx     # Run what-if scenarios
    components/
      ZoneLoadChart.jsx
      WaveTable.jsx
      OrderClusterMap.jsx
```

## 4. Algorithm Design

### Step 1: Order Fingerprinting
For each order, compute:
- `zones`: set of zones required (from SKU temp requirements)
- `temp_signature`: weighted vector of temp classes
- `sla_tier`: 0=hospital (urgent), 1=pharmacy, 2=B2B
- `size_class`: small (1-2 items), medium (3-5), large (6+)
- `controlled`: boolean
- `near_expiry_count`: number of items with expiry < 90 days

### Step 2: FEFO Lot Pre-Allocation
For each order line (SKU, qty):
1. Query available lots for that SKU, sorted by expiry date (ascending)
2. Allocate from oldest lot first
3. If oldest lot is in reserve (not forward pick), flag for replenishment
4. Record allocated lot_id and bin_location

### Step 3: Affinity Clustering (Greedy)
```
waves = []
for sla in [0, 1, 2]:  # hospital first
    sla_orders = orders with this sla
    sort sla_orders by near_expiry_count desc
    
    while sla_orders not empty:
        seed = first order
        wave = [seed]
        remaining_capacity = compute_zone_capacity(seed.zones)
        
        for candidate in sla_orders[1:]:
            if zone_capacity_exceeded(wave + candidate): continue
            affinity = compute_affinity(seed, candidate)
            if affinity > THRESHOLD:
                wave.append(candidate)
                remaining_capacity -= candidate.zone_load
        
        waves.append(wave)
        remove wave orders from sla_orders
```

Affinity score = weighted combination of:
- Zone overlap (Jaccard similarity)
- Temp signature cosine similarity
- Size class match
- Same customer type bonus

### Step 4: Dynamic Wave Sizing
Each wave gets a `release_score` based on:
- Zone workload balance (penalize waves overloading cool/cold zones)
- Conveyor tote estimate (penalize waves needing > available totes)
- Picking time estimate vs SLA cutoff

Waves with score < threshold are split or deferred.

## 5. Demo Scenario

**"Flu Season Peak"**: A regional warehouse normally handles 700 orders/day. During flu season, it spikes to 1,960 orders/day (280%). The demo shows:
1. Normal day: 10 waves, balanced zone load, 4.2% near-expiry pick rate
2. Peak day: 28 waves, dynamic sizing prevents cool zone bottleneck, FEFO picks spike to 12%, conveyor saturation avoided by wave throttling
3. What-if: "What if we had 2 more cool zone pickers?" → simulation shows throughput increase and bottleneck shift

## 6. Implementation Phases

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| 1 | 1-2 days | Data models + demo data generator (500 SKUs, 1000 orders) |
| 2 | 2-3 days | Core allocator (fingerprint + clustering + FEFO lot allocation) |
| 3 | 2 days | API endpoints + wave/batch CRUD |
| 4 | 2-3 days | React dashboard (zone load, wave table, order cluster map) |
| 5 | 2 days | Simulation engine + what-if scenarios |
| 6 | 1-2 days | Flu season peak demo scenario + polish |

## 7. Alternative Approach (Simpler)

**Streamlined Heuristic (No Clustering)**: Skip the affinity clustering and simply sort all orders by (SLA urgency, then near-expiry count, then zone count), then slice into fixed-size waves. This is less optimal but extremely simple to implement and still respects FEFO + SLA. Good if the team is less technical or time-constrained.
