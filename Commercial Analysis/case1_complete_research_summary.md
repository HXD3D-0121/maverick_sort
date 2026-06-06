# Case 1: Complete Research Summary
## Smart Warehouse Sorting & Dispatch System

**Course:** Digital Innovation | SDC MSc Innovation Management  
**Case Enterprise:** Large Chinese Pharmaceutical Logistics Enterprise  
**Compiled:** June 2026

---

## 1. THE ENTERPRISE AT A GLANCE

| Metric | Value |
|--------|-------|
| Annual Revenue | RMB 138.76 billion |
| Logistics Centers | 128 (incl. 6 central warehouses) |
| Distribution Stations | 856 |
| Warehouse Area | 2.65 million sqm (GSP-standard) |
| Annual Throughput | >90 million cases |
| Product Lines (SKUs) | 423,600 |
| Partner Manufacturers | 8,600 |
| Public Hospital Clients | 12,800 |
| Chain Pharmacy Clients | 5,832 |
| Independent Pharmacy Clients | 196,500 |
| Primary Healthcare Clients | 357,400 |
| B2B Registered Users | >580,000 |
| Daily Active Customers | >36,000 |
| Daily Orders | >90,000 |
| Average Items per Order | 3–5 |
| Next-Day Delivery Rate | >88% |

---

## 2. THE BUSINESS: PHARMACEUTICAL WHOLESALE

### What Is Pharma Wholesale?
Pharmaceutical wholesale is the intermediary between drug manufacturers and healthcare providers. The enterprise buys drugs in bulk, stores them in compliant warehouses, and distributes to hospitals, pharmacies, and clinics.

### The Margin Reality
This is a **high-volume, low-margin** business:
- Gross margins: **3–8%** (and eroding)
- Operating margins: **1.5–2.5%**
- In the US, even as the "Big Three" wholesalers grew sales by $100B, their gross profit **declined 12%**
- **Operational efficiency is the ONLY competitive lever**

### China's Game-Changing Policies

| Policy | Year | Impact on Ordering |
|--------|------|-------------------|
| **Two-Invoice System** | 2016 | Eliminated multi-layer distribution; 60%+ small distributors exited; market concentrated among giants |
| **Volume-Based Procurement (VBP)** | 2018 | Government centralized bargaining cut generic prices **30–60%**; forced wholesalers to compete on volume, not margin |

### Competitive Landscape (China's "Big Four")

| Company | Type | 2024 Revenue | Market Share |
|---------|------|-------------|--------------|
| Sinopharm (国药控股) | SOE | ~RMB 270B | ~25% |
| Shanghai Pharma (上海医药) | SOE | ~RMB 220B | ~8–10% |
| China Resources Pharma (华润医药) | SOE | ~RMB 130B | ~5–7% |
| Jointown (九州通) | Private | ~RMB 140B | ~7–8% |

> The case enterprise is comparable in scale to **Jointown** — China's largest private pharma distributor.

---

## 3. THE CUSTOMERS: WHO ORDERS & HOW

### Four Customer Segments

| Segment | Count | Typical Order | Frequency | Key Trait |
|---------|-------|---------------|-----------|-----------|
| **Public Hospitals** | 12,800 | 50–500+ items | 2–4×/week | Government procurement; VBP compliance; next-morning delivery |
| **Chain Pharmacies** | 5,832 | 20–100 items | 2–3×/week | Centralized purchasing; data-driven; promotion-sensitive |
| **Independent Pharmacies** | **196,500** | **3–10 items** | **Daily/every 2 days** | Small, cash-constrained; experience-based ordering |
| **Primary Healthcare** | 357,400 | 5–20 items | Weekly/bi-weekly | Government-funded; limited drug list; rural |

### The Big Insight: Why 3–5 Items per Order?

**The 196,500 independent pharmacies drive the order volume.** They:
- Have tiny shops with **no storage space**
- Have **no cash** to buy in bulk
- Fear **expiry** — can't risk slow-moving stock
- Order **3–10 items at a time, daily**

> This is why you have **>36,000 daily active customers** placing **>90,000 orders/day** with only **3–5 items per order**.

### Ordering Timing Patterns

| When | What Happens |
|------|-------------|
| **Monday** | Highest volume — restocking after weekend |
| **Morning (9–12 PM)** | Peak ordering — all segments active |
| **Afternoon (2–5 PM)** | Second peak — chains place consolidated orders |
| **Evening (5–8 PM)** | Independents order after store closes |
| **Flu Season (Oct–Mar)** | **+280% volume spike** — all segments, all products |

---

## 4. THE WAREHOUSE: PHYSICAL DESIGN

### Five Core Functional Zones

```
RECEIVING → STORAGE → PICKING → PACKING → SHIPPING
```

### Pharma-Specific Additional Zones

| Zone | Purpose |
|------|---------|
| **Quarantine Area** | Hold incoming goods pending QC inspection |
| **Released Area** | Approved stock ready for picking |
| **Rejected Area** | Failed inspection batches |
| **Recalled Area** | Products subject to recall |
| **Controlled Substance Vault** | Narcotics, psychotropics — dual-lock, cameras, biometric |
| **Dangerous Goods Area** | Flammables — flame-proof cabinets |
| **Returns Processing** | Returned products — cannot restock directly |

### Temperature Zones

| Zone | Temperature | % of SKUs | Products |
|------|------------|-----------|----------|
| **Ambient** | 15–25°C | 60–70% | Tablets, capsules, most oral meds |
| **Cool** | 8–15°C | 5–10% | Certain antibiotics, TCM |
| **Cold** | 2–8°C | 15–20% | Vaccines, insulin, biologics |
| **Frozen** | -15 to -25°C | ~5% | Frozen biologics |
| **Ultra-Low** | -40 to -80°C | <1% | mRNA vaccines, cell therapies |

> **Critical constraint**: Moving between zones requires airlocks (30–60 seconds). Cold items have strict time-out-of-zone limits — exceed them and the product is destroyed.

### Layout Flow Patterns

**U-Shaped Flow** (most common for pharma DCs):
```
    ┌─────────────────────────────┐
    │  RECEIVING    SHIPPING      │
    │     ↓            ↑          │
    │  [Storage → Picking → Pack] │
    └─────────────────────────────┘
         Same side of building
```
- Receiving and shipping share dock doors
- Excellent security control
- Facilitates cross-docking

**I-Shaped / Through Flow**:
```
RECEIVING → Storage → Picking → Packing → SHIPPING
   [Dock]                                    [Dock]
   Opposite ends of building
```
- No confusion between inbound and outbound
- Better for very large facilities

### Storage Systems by SKU Velocity

| Category | % of SKUs | % of Picks | Storage System | Location |
|----------|-----------|------------|----------------|----------|
| **A (Fast movers)** | 20% | 80% | Carton flow rack | Forward pick, ground level, nearest shipping |
| **B (Medium movers)** | 30% | 15% | Selective pallet rack | Mid-level, moderate distance |
| **C (Slow movers)** | 50% | 5% | High-bay rack / AS/RS | Upper levels, farthest from shipping |

---

## 5. THE OPERATIONS: PICKING & FULFILLMENT

### Three Picking Models Used Simultaneously

#### Model A: Zone Picking with Conveyor Consolidation (Most Common)
- Warehouse divided into pick zones (ambient fast, ambient slow, cool, cold)
- Tote assigned to one order, travels on conveyor between zones
- Pickers stay in one zone, pick items for passing totes
- After all zones, tote goes to consolidation/packing

#### Model B: Goods-to-Person (G2P)
- Robot retrieves bin/case, brings to stationary picker
- Eliminates walking entirely
- Used for medium-velocity SKUs

#### Model C: Batch/Cart Picking
- Picker takes cart with 8–12 totes, walks aisles
- Only model where wave batching and route optimization apply directly
- Used for: slow movers, bulk case picks, overflow during peaks, cold zone

### Wave Planning

Orders grouped into "waves" based on:
- **Cutoff times** — Hospital orders must be picked by 4 PM for next-morning delivery
- **Truck departure schedules**
- **Conveyor capacity** — Too many waves causes jams
- **Zone workload balance**

### End-to-End Order Flow

```
Order Ingestion → Order Promising → Wave Planning → Tote Induction
                                                            ↓
Shipping Sortation ← Outbound Loading ← Packing ← Zone Picking
```

### Technology Stack

| Layer | System | Function |
|-------|--------|----------|
| **ERP** | SAP, Oracle, Yonyou, Kingdee | Order entry, customer master, pricing |
| **WMS** | SAP EWM, Manhattan, Blue Yonder | Inventory by lot/bin, wave creation, pick tasks |
| **WES** | Emerging layer | Dynamic wave release, workload balancing, tote routing |
| **WCS** | Conveyor controls, pick-to-light | Controls physical equipment, scanners, robots |
| **TMS** | Route planning, truck scheduling | Plans delivery routes |

---

## 6. THE CHALLENGES (Your System Must Solve)

### Challenge 1: SKU Complexity
- **423,600 SKUs** — 38% are near-expiry managed
- Varying temperature requirements, controlled substances, prescription/OTC flags

### Challenge 2: Order Fragmentation
- **>36,000 daily active customers**, mostly small-batch multi-SKU orders
- **Average 3–5 items per order**, yet **>90,000 total daily orders**

### Challenge 3: Time Pressure
- **>88% next-day delivery** promise requires same-day sorting and dispatch
- Peak periods (flu season): **order volume spikes 280%**

### Challenge 4: Labor Bottleneck
- Sorting relies heavily on manual labor
- Peak periods require **2.5× temporary staffing**
- **~0.35% error rate** (annual average); spikes to **1%+ during peaks**
- **Annual return losses exceeding RMB 9 million**

### Challenge 5: Inventory Turnover & Expiry
- **Near-expiry scrap rates ~4.8%** for some products
- **FEFO (First Expired, First Out)** is mandatory — not just FIFO

### Challenge 6: What Breaks During Peaks

| Bottleneck | What Happens |
|-----------|-------------|
| **Conveyor saturation** | Totes back up at induction; pick stations starve or flood |
| **Zone imbalance** | Cool zone (2 stations) becomes bottleneck while ambient (10 stations) sits idle |
| **Tote shortage** | Finite resource; more waves = more totes in system |
| **Packing bottleneck** | Picking scales with staff; packing does not scale linearly |
| **Truck capacity** | Even if picked, not enough trucks/drivers for 280% volume |
| **Temp picker quality** | 2.5× temp staff = 2.5× error rate from inexperience |

---

## 7. REGULATORY REQUIREMENTS

### GSP (Good Supply Practice)
- China's national standard for pharmaceutical storage and distribution
- Mandatory certification to operate
- Obtaining certification can take up to 24 months

### GDP (Good Distribution Practice)
- International quality assurance guidelines
- Enforced by FDA (US), EMA (Europe), WHO (global)
- Key requirements: temperature control, qualified equipment, documentation, traceability

### Serialization & Traceability
- China requires 2D Data Matrix codes on individual saleable units
- Every unit scanned at pick must match national traceability database

### GSP Audit Trail
Every action must be recorded: **who, what, when, where, lot, expiry, temperature**

---

## 8. DASHBOARD DESIGN: WHAT TO DISPLAY

Based on all research, here is what your visual dashboard should show:

### 8.1 Real-Time Operations View

| KPI | Why It Matters | Target/Benchmark |
|-----|---------------|------------------|
| **Orders Received (Today)** | Total order intake vs. capacity | Track against forecast |
| **Orders Picked (Today)** | Throughput progress | 90,000+/day baseline |
| **Orders Packed (Today)** | Packing bottleneck indicator | Should match picking rate |
| **Orders Shipped (Today)** | Final output | >88% next-day SLA |
| **Current Wave Status** | Which wave is active, how many pending | Visual wave timeline |
| **Pick Rate (lines/hour)** | Labor productivity | 150–200 permanent; 50–80 temp |
| **Error Rate (%)** | Quality control | <0.35% annual; spike to 1%+ in peaks |

### 8.2 Zone Workload Balance

| KPI | Why It Matters |
|-----|---------------|
| **Ambient Zone Utilization** | 60–70% of SKUs; 10 pick stations |
| **Cool Zone Utilization** | 15–20% of SKUs; 2 pick stations — **WATCH THIS** |
| **Cold Zone Utilization** | 5% of SKUs; limited access |
| **Zone Bottleneck Alert** | Flag when one zone is saturated while others idle |
| **Cross-Zone Pick Count** | Minimize for efficiency |

> **Critical**: During flu season, cool zone (vaccines, antibiotics) becomes the bottleneck. The dashboard must highlight this.

### 8.3 Temperature Compliance

| KPI | Why It Matters |
|-----|---------------|
| **Temperature by Zone** | Real-time monitoring of all 5 zones |
| **Temperature Excursions** | Any deviation from range — immediate alert |
| **Time Out of Zone** | Cold items exceeding safe exposure time |
| **Cold Chain Compliance Rate** | Must be >99.9% |

### 8.4 Labor Management

| KPI | Why It Matters |
|-----|---------------|
| **Staff by Zone** | How many pickers in each zone |
| **Permanent vs. Temp Staff** | Temp ratio spikes to 2.5× in peak |
| **Picker Productivity by Zone** | Identify underperforming zones/stations |
| **Labor Cost per Order** | Efficiency metric |

### 8.5 Inventory Health

| KPI | Why It Matters |
|-----|---------------|
| **Near-Expiry Items (%)** | 38% of SKUs are near-expiry managed |
| **FEFO Compliance Rate** | Are we picking oldest expiry first? |
| **Scrap Rate** | Currently ~4.8%; target reduction |
| **Inventory Turnover by Category** | Slow movers (>165 days) vs. fast movers |
| **Stockout Alerts** | Impending stockouts by SKU |

### 8.6 Customer Segment View

| KPI | Why It Matters |
|-----|---------------|
| **Orders by Segment** | Hospitals vs. chains vs. independents vs. primary care |
| **Orders by Size** | Small (1–5 items) vs. medium (6–20) vs. large (20+) |
| **Orders by Temperature Requirement** | Ambient-only vs. mixed-zone |
| **SLA Compliance by Segment** | Hospitals need next-morning; others next-day |
| **Cutoff Time Compliance** | Hospital orders: 4 PM; B2B: 8 PM |

### 8.7 Exception Alerts

| Alert Type | Trigger |
|-----------|---------|
| **Conveyor Saturation** | Tote queue > threshold at any point |
| **Zone Imbalance** | One zone >90% utilized, another <30% |
| **Tote Shortage** | Available totes < minimum for next wave |
| **Packing Backlog** | Packed boxes waiting > threshold |
| **Temperature Excursion** | Any zone out of range |
| **High Error Rate** | Current shift error rate > 0.5% |
| **Late Orders** | Orders approaching cutoff without wave assignment |

### 8.8 Simulation / What-If Analysis

| Scenario | What to Model |
|----------|--------------|
| **Flu Season Peak (280% volume)** | Conveyor capacity, zone balance, labor needs, tote requirements |
| **Cool Zone Failure** | What if refrigeration fails? Redirect to backup? |
| **Staff Shortage** | Impact of 20% fewer pickers on throughput |
| **Large Hospital Order Surge** | Priority handling vs. regular orders |
| **New SKU Introduction** | Where to slot? Which zone? Impact on picking |

---

## 9. KEY METRICS & BENCHMARKS

### Operational Benchmarks

| Metric | Current | Target |
|--------|---------|--------|
| Daily Orders | 90,000+ | Handle 250,000+ at peak |
| Items per Order | 3–5 | Optimize pick path for this profile |
| Pick Rate (permanent) | — | 150–200 lines/hour |
| Pick Rate (temp) | — | 50–80 lines/hour |
| Error Rate | 0.35% | <0.1% with automation |
| Next-Day Delivery | >88% | Maintain or improve |
| Near-Expiry Scrap | 4.8% | Reduce by 25–40% via FEFO |
| Annual Return Losses | RMB 9M+ | Reduce via accuracy |

### Financial Benchmarks

| Metric | Industry Benchmark |
|--------|-------------------|
| Gross Margin | 3–8% (eroding) |
| Operating Margin | 1.5–2.5% |
| Automation Capex (Jointown) | RMB 1.2B annually |
| Cold Chain Investment | RMB 2.1B |
| Regulatory Compliance Cost | ~RMB 280M/year |

---

## 10. STRATEGIC INSIGHTS FOR YOUR PROTOTYPE

### Wave Allocation Algorithm
1. **Prioritize hospitals** — next-morning delivery SLA
2. **Group by cutoff time** — hospital orders (4 PM) vs. B2B orders (8 PM)
3. **Minimize cross-zone picks** — group orders with similar temperature requirements
4. **Balance zone workload** — don't flood cool zone while ambient sits idle
5. **Account for order size** — large hospital orders in dedicated waves; small pharmacy orders batched
6. **Dynamic wave sizing** — smaller waves during normal, larger waves during peak

### Dynamic Inventory Scheduling
1. **Real-time bin-level tracking** — every SKU, every lot, every expiry date
2. **FEFO enforcement** — pick nearest expiry first, regardless of receipt date
3. **Smart replenishment** — move from reserve to forward pick based on velocity
4. **Reallocation recommendations** — shift inventory between centers based on regional demand

### Near-Expiry Alert System
1. **Expiry warnings** — flag items approaching expiry (30/60/90 days)
2. **Promotion suggestions** — recommend discounts to accelerate movement
3. **Reallocation suggestions** — move near-expiry stock to higher-velocity locations
4. **Destruction scheduling** — plan write-offs before expiry

### Simulation Engine
1. **Flu season peak** — 280% volume, model conveyor saturation, zone imbalance, labor needs
2. **Staffing scenarios** — impact of temp staff ratio on error rates
3. **Zone failure** — what if cool zone goes down?
4. **New SKU introduction** — slotting optimization

---

## 11. ONE-PAGE SUMMARY: THE FULL PICTURE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CASE 1: SMART WAREHOUSE SYSTEM                           │
│                     The Complete Picture                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  THE BUSINESS                                                               │
│  ├─ Pharma wholesale: buy bulk from 8,600 manufacturers                     │
│  ├─ Store in 128 GSP-compliant warehouses (2.65M sqm)                       │
│  ├─ Distribute to 572,000+ customers nationwide                             │
│  └─ Razor-thin margins (3–8% gross) → efficiency is everything              │
│                                                                             │
│  THE CUSTOMERS (who places 90,000+ orders/day?)                             │
│  ├─ Hospitals (12,800): large orders, government rules, next-morning        │
│  ├─ Chain pharmacies (5,832): medium orders, centralized buying             │
│  ├─ Independent pharmacies (196,500): TINY orders (3–10 items), DAILY       │
│  │   └─>>> THESE DRIVE YOUR ORDER VOLUME <<<                               │
│  └─ Primary care (357,400): small orders, government-funded, rural          │
│                                                                             │
│  THE WAREHOUSE                                                              │
│  ├─ 5 temperature zones: ambient (60–70%), cool, cold, frozen, ultra-low    │
│  ├─ U-shaped flow: receiving & shipping share dock doors                    │
│  ├─ Zone picking + conveyor consolidation: most common model                │
│  └─ Forward pick (A-items) + reserve storage (C-items)                      │
│                                                                             │
│  THE CHALLENGES                                                             │
│  ├─ 423,600 SKUs, 38% near-expiry managed                                   │
│  ├─ 90,000+ orders/day, 3–5 items each → massively fragmented               │
│  ├─ >88% next-day delivery → same-day pick, pack, ship                      │
│  ├─ Flu season: +280% volume → everything breaks                            │
│  ├─ 0.35% error rate, RMB 9M annual return losses                            │
│  └─ 4.8% near-expiry scrap rate → need FEFO, not just FIFO                  │
│                                                                             │
│  YOUR SYSTEM MUST DO                                                        │
│  ├─ Smart wave allocation: group orders by zone, SLA, cutoff time           │
│  ├─ Dynamic inventory: real-time bin tracking, FEFO enforcement             │
│  ├─ Near-expiry alerts: warnings, promotions, reallocation                  │
│  ├─ Visual dashboard: zone balance, labor, exceptions, KPIs                 │
│  └─ Simulation: what-if at 280% volume, zone failure, staffing              │
│                                                                             │
│  THE DASHBOARD MUST SHOW                                                    │
│  ├─ Real-time: orders in/picked/packed/shipped, pick rate, error rate       │
│  ├─ Zone balance: utilization per zone, bottleneck alerts                   │
│  ├─ Temperature: compliance, excursions, time-out-of-zone                   │
│  ├─ Labor: staff by zone, permanent vs. temp, productivity                  │
│  ├─ Inventory: near-expiry %, FEFO compliance, scrap rate                   │
│  ├─ Customer: orders by segment, size, temperature, SLA compliance          │
│  ├─ Exceptions: conveyor saturation, zone imbalance, tote shortage          │
│  └─ Simulation: flu season peak, cool zone failure, staff shortage          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

*This summary consolidates research from four deep-dive reports:*
1. *Pharmaceutical Wholesale Deep Research*
2. *Warehouse Types & Pharmaceutical Storage*
3. *China Pharmacy & Hospital Ordering Culture*
4. *Background materials from the casebook*

*All sources cited in individual research files.*
