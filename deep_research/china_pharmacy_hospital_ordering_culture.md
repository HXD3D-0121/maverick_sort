# Deep Research: Ordering Culture of Pharmacies & Hospitals in China

## Context
This research supports **Case 1: Smart Warehouse Sorting & Dispatch System** for the SDC MSc Innovation Management course. The case enterprise serves **12,800 public hospitals, 5,832 chain pharmacies, 196,500 independent pharmacies, and 357,400 primary healthcare institutions** — with **>36,000 daily active customers** placing **>90,000 orders per day** averaging **3–5 items each**.

Understanding *who* orders, *how* they order, *when* they order, and *why* they order the way they do is critical to designing a smart wave allocation and dispatch system.

---

## Table of Contents
1. [The Four Customer Segments](#1-the-four-customer-segments)
2. [Public Hospitals: How They Order](#2-public-hospitals-how-they-order)
3. [Chain Pharmacies: How They Order](#3-chain-pharmacies-how-they-order)
4. [Independent Pharmacies: How They Order](#4-independent-pharmacies-how-they-order)
5. [Primary Healthcare Institutions: How They Order](#5-primary-healthcare-institutions-how-they-order)
6. [B2B E-Commerce Platform Ordering Behavior](#6-b2b-e-commerce-platform-ordering-behavior)
7. [Ordering Patterns: Timing, Frequency & Seasonality](#7-ordering-patterns-timing-frequency--seasonality)
8. [What Drives Order Characteristics](#8-what-drives-order-characteristics)
9. [Pain Points in the Ordering Process](#9-pain-points-in-the-ordering-process)
10. [Relevance to Your Smart Warehouse System](#10-relevance-to-your-smart-warehouse-system)
11. [Key Takeaways](#11-key-takeaways)

---

## 1. The Four Customer Segments

Your case enterprise serves four very different types of customers. Each has distinct ordering behaviors, constraints, and expectations:

| Segment | Count | % of Orders | Order Size | Order Frequency | Key Constraint |
|---------|-------|-------------|------------|-----------------|----------------|
| **Public Hospitals** | 12,800 | ~25–30% | Large (50–500+ items) | 2–4x per week | Government procurement rules; VBP compliance |
| **Chain Pharmacies** | 5,832 | ~20–25% | Medium (20–100 items) | 2–3x per week | Centralized purchasing; standardized formularies |
| **Independent Pharmacies** | 196,500 | ~35–40% | Small (3–10 items) | Daily or every 2 days | Cash flow; limited storage; experience-based ordering |
| **Primary Healthcare** | 357,400 | ~15–20% | Small (5–20 items) | Weekly or bi-weekly | Government-funded; limited budgets; basic logistics |

> **Critical insight**: The **196,500 independent pharmacies** are the most fragmented, least predictable segment — but they generate the highest order volume due to their sheer number and frequent small-batch ordering.

---

## 2. Public Hospitals: How They Order

### The Hospital Pharmacy Department

In Chinese public hospitals, the **pharmacy department** (药剂科) is responsible for all drug procurement, storage, and dispensing. It operates as a separate unit within the hospital with its own budget and staff.

### The Ordering Process

```
Step 1: Clinical departments request drugs (based on patient prescriptions/ward stock)
        ↓
Step 2: Pharmacy department reviews requests against hospital formulary
        ↓
Step 3: Check inventory levels → identify what needs reordering
        ↓
Step 4: Place order through government procurement platform OR B2B platform
        ↓
Step 5: Wholesaler (your case enterprise) receives order → picks & ships
        ↓
Step 6: Hospital receives, QC inspects, releases to pharmacy stock
        ↓
Step 7: Dispensed to patients via outpatient pharmacy or ward distribution
```

### Hospital Inventory Management

Hospitals typically use a **reorder point (ROP) system** with periodic review:

| Parameter | Typical Practice |
|-----------|-----------------|
| **Reorder trigger** | Stock falls below minimum threshold (safety stock) |
| **Safety stock** | 1–2 months of usage for critical drugs |
| **Order frequency** | 2–4 times per week for fast movers; weekly for others |
| **Review cycle** | Daily for A-items; weekly for B-items; monthly for C-items |
| **Order size** | Large batches — hospitals have storage space and capital |

> **Example**: A tertiary hospital (三甲医院) might order 500+ line items per order, with quantities of 100–1,000 boxes per drug. Delivery expected next morning.

### Government Procurement Constraints

Since 2018, China's **National Volume-Based Procurement (VBP / 带量采购)** policy has fundamentally changed hospital ordering:

| Before VBP | After VBP |
|-----------|-----------|
| Hospitals negotiated prices individually with suppliers | National government negotiates prices centrally |
| Multiple suppliers for same drug | 1–3 winning bidders per drug |
| Prices high, margins for hospitals | Prices cut 30–60%, sometimes 90%+ |
| Flexible ordering quantities | Pre-committed annual volumes |
| Many brand-name drugs | Mostly generics (96% of winning bids) |

**Impact on ordering behavior**:
- Hospitals **must** purchase VBP-winning drugs to meet quota
- Non-VBP drugs (especially imported brand-name) see reduced orders
- Order volumes for VBP drugs are **predictable** (government-mandated quotas)
- Order volumes for non-VBP drugs are **volatile** (market-driven)

### Hospital Order Characteristics

| Feature | Typical Value |
|---------|--------------|
| **Order size** | 50–500+ line items |
| **Items per order** | High — bulk procurement |
| **Temperature requirements** | Mixed — ambient + cool + cold |
| **Delivery SLA** | Next-morning delivery (critical for inpatient care) |
| **Payment terms** | 30–90 days (hospitals are slow payers) |
| **Order channel** | EDI to government platform → B2B platform → direct |
| **Special requirements** | Lot traceability, temperature certificates, government tender flags |

---

## 3. Chain Pharmacies: How They Order

### Centralized vs. Decentralized Ordering

| Chain Size | Ordering Model | Example |
|-----------|---------------|---------|
| **Large national chains** (1,000+ stores) | Centralized purchasing at HQ; regional distribution centers | Yifeng, LBX, Guoda |
| **Medium regional chains** (100–1,000 stores) | Semi-centralized; regional hubs order from wholesalers | Various provincial chains |
| **Small local chains** (<100 stores) | Decentralized; individual stores or small clusters order | Local franchise groups |

### The Ordering Process (Centralized Chain)

```
Individual store → POS system tracks sales & inventory
        ↓
Central system aggregates demand across all stores
        ↓
HQ purchasing team generates consolidated order
        ↓
Order placed via B2B platform (or direct EDI with major wholesalers)
        ↓
Wholesaler ships to regional distribution center (RDC)
        ↓
RDC cross-docks or stores, then delivers to individual stores
```

### Chain Pharmacy Order Characteristics

| Feature | Typical Value |
|---------|--------------|
| **Order size** | 20–100 line items per store; 1,000+ when consolidated |
| **Items per order** | Medium — mix of fast movers and seasonal |
| **Order frequency** | 2–3 times per week per store |
| **Temperature requirements** | Mostly ambient; some cool (insulin, vaccines) |
| **Delivery SLA** | Next-day or 2-day |
| **Payment terms** | 15–30 days |
| **Order channel** | B2B e-commerce platform, EDI, or sales rep |
| **Special requirements** | Promotional pricing, bundled offers, shelf-life minimums |

### Key Behaviors
- **Formulary-driven**: Chains have standardized drug lists; all stores stock same core SKU set
- **Promotion-sensitive**: Order quantities spike during manufacturer promotions
- **Seasonal planning**: Stock up before flu season, allergy season, etc.
- **Data-driven**: Large chains use sales data and AI for demand forecasting

---

## 4. Independent Pharmacies: How They Order

### The Reality of 196,500 Independent Pharmacies

This is the **most fragmented and challenging segment**. These are small, family-owned or individually operated pharmacies — often just 1–3 stores.

### How They Order (The "Old Way" vs. "New Way")

#### Traditional Ordering (Still Common in Lower-Tier Cities)

```
Pharmacist/owner checks shelves manually
        ↓
Writes order on paper or calls sales rep directly
        ↓
Sales rep from wholesaler visits or calls back with confirmation
        ↓
Order delivered next day or in 2–3 days
        ↓
Pay cash on delivery or via bank transfer
```

#### Modern Ordering (Growing Rapidly)

```
Pharmacist opens B2B e-commerce app (e.g., JD Medicine Procurement)
        ↓
Browses catalog, compares prices, checks availability
        ↓
Adds items to cart (often 3–10 items)
        ↓
Places order with one-click reorder for frequent items
        ↓
Pays via platform (credit, mobile payment)
        ↓
Delivery next day or same-day in urban areas
```

### Independent Pharmacy Order Characteristics

| Feature | Typical Value |
|---------|--------------|
| **Order size** | Very small — 3–10 line items |
| **Items per order** | Low — "top-up" ordering, just what they need |
| **Order frequency** | Daily or every 2 days (limited storage, limited cash) |
| **Temperature requirements** | Almost entirely ambient |
| **Delivery SLA** | Next-day acceptable; same-day preferred in cities |
| **Payment terms** | Prepay or COD (cash on delivery) — no credit |
| **Order channel** | B2B app (growing), phone call to sales rep, WeChat |
| **Special requirements** | Lowest price, free shipping threshold, small minimum order |

### Why Their Orders Are So Small and Frequent

1. **Limited storage space** — Small shops can't hold much inventory
2. **Cash flow constraints** — They buy what they can afford today
3. **Unpredictable demand** — No sales data systems; they guess based on experience
4. **Fear of expiry** — Small shops can't risk slow-moving stock expiring
5. **No credit from wholesalers** — Must pay upfront or COD

> **This is why your case has "3–5 items per order" and ">36,000 daily active customers"** — it's the independent pharmacy segment driving this pattern.

### Geographic Distribution

| Tier | % of Independent Pharmacies | Ordering Behavior |
|------|----------------------------|-------------------|
| **Tier 1–2 cities** (Beijing, Shanghai, etc.) | ~20% | More digital; use B2B apps; expect fast delivery |
| **Tier 3–4 cities** | ~40% | Mixed; some apps, some phone orders |
| **County/town/rural** | ~40% | Mostly phone/fax; limited digital literacy; rely on sales reps |

---

## 5. Primary Healthcare Institutions: How They Order

### What Are They?

- **Township Health Centers (THCs / 乡镇卫生院)** — 30–50 beds, serve rural towns
- **Village Clinics (村卫生室)** — 1–2 staff, basic medicines, serve villages
- **Community Health Centers (社区卫生服务中心)** — Urban primary care

### The Ordering Process

Primary healthcare in China operates under the **National Essential Medicines Policy (NEMP)**:

```
Government defines Essential Medicines List (EML)
        ↓
Primary care facilities can ONLY stock EML drugs (mostly)
        ↓
County-level government pools procurement for all facilities in county
        ↓
Orders placed through government procurement platform
        ↓
Wholesaler delivers to county medical community (CMC) hub
        ↓
Hub distributes to individual THCs and village clinics
```

### Primary Healthcare Order Characteristics

| Feature | Typical Value |
|---------|--------------|
| **Order size** | Small — 5–20 line items per facility |
| **Items per order** | Limited to Essential Medicines List |
| **Order frequency** | Weekly or bi-weekly (government-scheduled) |
| **Temperature requirements** | Mostly ambient; some vaccines (cold) |
| **Delivery SLA** | Weekly scheduled delivery |
| **Payment terms** | Government-funded; delayed payment common |
| **Order channel** | Government procurement platform (mandatory) |
| **Special requirements** | EML compliance, zero-markup pricing, government reporting |

### Key Challenges

1. **Limited drug availability** — Village clinics often have <100 drug types vs. 1,000+ in hospitals
2. **Low profit margins** — Zero-markup policy means no profit from drug sales
3. **Geographic barriers** — Remote mountain villages difficult to reach
4. **Small order sizes** — Not profitable for wholesalers to deliver individually
5. **Delayed payments** — Government reimbursement slow; wholesalers reluctant to serve

> **Policy response**: County Medical Communities (CMCs) consolidate procurement — the county hospital acts as hub, ordering in bulk and redistributing to village clinics.

---

## 6. B2B E-Commerce Platform Ordering Behavior

### The Rise of Pharma B2B E-Commerce

China's pharmaceutical B2B e-commerce market is projected to reach **RMB 375.8 billion by 2025**.

| Platform Type | Market Share | Target Users |
|--------------|-------------|--------------|
| **Third-party platforms** (JD Medicine Procurement, etc.) | 58% | Small/medium pharmacies, clinics |
| **Traditional distributors going digital** | 32% | Existing customers transitioning online |
| **Government-led platforms** | 10% | Public hospitals, primary care (mandatory) |

### Platform Features That Drive Ordering Behavior

| Feature | Impact on Ordering |
|---------|-------------------|
| **Real-time stock visibility** | Pharmacists only order what's available — reduces backorders |
| **Price comparison** | Independent pharmacies shop for lowest price — increases price sensitivity |
| **One-click reorder** | Repeats previous order — speeds up ordering for routine items |
| **AI recommendations** | Suggests related products — increases basket size |
| **Minimum order for free shipping** | Pharmacies add items to reach threshold — increases order size |
| **Credit/payment terms** | Enables larger orders for cash-constrained customers |
| **Mobile app access** | Enables ordering anytime, anywhere — increases order frequency |

### JD Medicine Procurement (Case Study)

- Launched 2017 by JD Health
- Targets **small/medium chain pharmacies and independent drugstores in lower-tier markets**
- ~80% of China's pharmacies are small/independent
- Nearly half of customers are from **4th-tier cities and below**
- Key pain points addressed:
  - Incomplete drug variety available locally
  - Can't compare prices easily
  - Long procurement cycles

> **Result**: "Tianqiong" data platform reduced procurement decision time by 70% and increased inventory turnover by 2.1 cycles annually.

---

## 7. Ordering Patterns: Timing, Frequency & Seasonality

### Daily Order Patterns

| Time Window | Who Orders | Order Characteristics |
|-------------|-----------|----------------------|
| **6:00–9:00 AM** | Hospitals (urgent restock) | STAT orders; small; high priority |
| **9:00–12:00 PM** | All segments | Peak ordering window; mixed order sizes |
| **12:00–2:00 PM** | Reduced activity | Lunch break; fewer orders |
| **2:00–5:00 PM** | All segments | Second peak; chains place consolidated orders |
| **5:00–8:00 PM** | Independent pharmacies | After-store-hours ordering via app |
| **8:00 PM–12:00 AM** | Some chains, online-only | Late orders for next-day delivery |

### Weekly Patterns

| Day | Pattern |
|-----|---------|
| **Monday** | Highest volume — restocking after weekend |
| **Tuesday–Thursday** | Steady volume — normal operations |
| **Friday** | Reduced — facilities don't want weekend stock |
| **Saturday–Sunday** | Minimal — only urgent orders |

### Seasonal Patterns (Critical for Your Case!)

| Season | Demand Driver | Affected Products | Volume Impact |
|--------|--------------|-------------------|---------------|
| **October–March (Flu Season)** | Influenza, respiratory infections | Antivirals, antibiotics, cough/cold meds, vaccines | **+280% peak** |
| **March–May (Allergy Season)** | Pollen allergies | Antihistamines, nasal sprays, eye drops | +50–80% |
| **Summer** | Gastroenteritis, heat-related | Oral rehydration, digestive meds, sun care | +30–50% |
| **Back-to-school (Aug–Sep)** | Pediatric checkups | Vitamins, pediatric meds | +20–30% |
| **Year-end** | Budget spending, stockpiling | All categories | +40–60% |

> **Your case explicitly mentions "peak periods (e.g., flu season) can spike order volume by 280%"** — this is driven by all customer segments ordering more frequently and in larger quantities simultaneously.

---

## 8. What Drives Order Characteristics

### Why Orders Are Small-Batch, Multi-SKU (3–5 Items)

| Factor | Explanation |
|--------|-------------|
| **Independent pharmacy dominance** | 196,500 small shops ordering daily top-ups |
| **Limited storage** | Can't hold inventory; buy what fits on shelves |
| **Cash constraints** | Pay-as-you-go; can't afford large orders |
| **Expiry risk** | Small shops fear slow-moving stock expiring |
| **B2B platform design** | Easy to browse and add a few items; one-click reorder |
| **No minimum order penalty** | Free shipping thresholds encourage small frequent orders |

### Why Orders Are Fragmented Across Temperature Zones

| Customer Type | Typical Temperature Mix |
|--------------|------------------------|
| **Hospitals** | 70% ambient, 20% cool, 10% cold |
| **Chain pharmacies** | 85% ambient, 10% cool, 5% cold |
| **Independent pharmacies** | 95% ambient, 5% cool (insulin only) |
| **Primary care** | 90% ambient, 10% cool/cold (vaccines) |

> Even a simple order of "3–5 items" might need items from 2–3 temperature zones — which is why your tote must visit multiple zones.

---

## 9. Pain Points in the Ordering Process

### From the Customer Side

| Pain Point | Who Affected | Impact |
|-----------|-------------|--------|
| **Stockouts** | All | Lost sales, patient dissatisfaction, switch to competitor |
| **Long delivery times** | Rural primary care | Patients go untreated; facilities run out |
| **Can't compare prices** | Independent pharmacies | Overpay; eroded margins |
| **Limited drug variety** | Rural clinics | Can't treat patients properly |
| **Expiry management** | All | Write-offs; regulatory risk |
| **Complex government procurement** | Hospitals | Administrative burden; compliance risk |
| **Slow payment from government** | Primary care | Cash flow crisis; can't pay wholesalers |

### From the Wholesaler Side (Your Case Enterprise!)

| Pain Point | Root Cause |
|-----------|-----------|
| **90,000+ orders/day to process** | Fragmented customer base; small frequent orders |
| **0.35% error rate** | Manual picking; temp staff during peaks |
| **Zone imbalance during flu season** | Cool zone (vaccines, antibiotics) becomes bottleneck |
| **Conveyor saturation at 280% volume** | Fixed capacity; can't scale linearly |
| **Temp picker quality issues** | 2.5x staffing; inexperienced workers |
| **Near-expiry scrap (4.8%)** | Poor FIFO/FEFO enforcement; slow movers |

---

## 10. Relevance to Your Smart Warehouse System

### How Ordering Culture Shapes Your System Design

| Ordering Culture Insight | System Design Implication |
|-------------------------|--------------------------|
| **3–5 items per order, 90,000+ orders/day** | Zone picking with conveyor consolidation is optimal; batch picking would be too slow |
| **Mixed temperature requirements per order** | Tote must visit multiple zones; routing optimization critical |
| **Independent pharmacies order daily, small** | Wave planning must handle many small waves; can't batch too aggressively |
| **Hospitals order large, need next-morning delivery** | Priority waves for hospital orders; afternoon shift picking for morning delivery |
| **Flu season = 280% volume spike** | Dynamic wave sizing; temp staff scheduling; conveyor capacity planning |
| **B2B platform orders come in real-time, all day** | Waveless or continuous wave release; not fixed batch windows |
| **Next-day delivery promise (>88%)** | Same-day pick, pack, ship; cutoff times strictly enforced |
| **Order cutoff times vary by customer type** | Hospital orders: 4 PM cutoff; B2B orders: 8 PM cutoff; different wave schedules |

### Wave Allocation Should Account For:

1. **Customer type priority** — Hospital orders before pharmacy orders
2. **Delivery SLA** — Morning delivery vs. afternoon vs. next-day
3. **Temperature zone mix** — Group orders with similar zone requirements to minimize cross-zone travel
4. **Order size** — Large hospital orders in dedicated waves; small pharmacy orders batched
5. **Cutoff time** — Orders placed before cutoff vs. after cutoff (next wave)
6. **Seasonality** — Flu season waves need more cool zone capacity

### Dashboard Should Show:

- Orders by customer segment (hospital vs. chain vs. independent vs. primary care)
- Orders by temperature zone requirement
- Real-time order intake vs. wave capacity
- Zone workload balance (is cool zone becoming a bottleneck?)
- Cutoff time compliance (are we meeting SLAs?)
- Peak season simulation (what happens at 280% volume?)

---

## 11. Key Takeaways

### The Ordering Culture in One Picture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CHINA PHARMA ORDERING LANDSCAPE              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  HOSPITALS (12,800)          CHAIN PHARMACIES (5,832)          │
│  ├─ Large orders (50–500+ items)  ├─ Medium orders (20–100)    │
│  ├─ 2–4x/week                     ├─ 2–3x/week                 │
│  ├─ Government/VBP constrained     ├─ Centralized purchasing    │
│  ├─ Next-morning delivery SLA      ├─ Promotion-sensitive       │
│  └─ Slow payer (30–90 days)        └─ 15–30 day payment        │
│                                                                 │
│  INDEPENDENT PHARMACIES (196,500)   PRIMARY CARE (357,400)     │
│  ├─ Tiny orders (3–10 items)        ├─ Small orders (5–20)     │
│  ├─ Daily or every 2 days           ├─ Weekly/bi-weekly        │
│  ├─ Experience-based ordering        ├─ Government-mandated     │
│  ├─ Cash-constrained                 ├─ Zero-markup policy      │
│  ├─ B2B app or phone order           ├─ EML-restricted          │
│  └─ Prepay or COD                    └─ Government-funded       │
│                                                                 │
│  >>> THESE 196,500 SMALL PHARMACIES DRIVE YOUR ORDER VOLUME <<<│
│      (3–5 items × 36,000 daily active = 90,000+ orders/day)    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Critical Insights for Case 1

1. **Your "average 3–5 items per order" is driven by independent pharmacies** — 196,500 of them ordering small daily top-ups
2. **Hospitals place fewer but much larger orders** — they need priority handling and next-morning delivery
3. **Flu season spikes affect ALL segments simultaneously** — not just more orders, but larger orders, more cool-zone items (vaccines, antibiotics)
4. **B2B platform ordering is growing fast** — real-time, all-day order intake means fixed wave windows may not work
5. **Government policies (VBP, NEMP) shape what gets ordered** — VBP drugs = predictable volume; non-VBP = volatile
6. **Payment terms vary dramatically** — hospitals pay in 30–90 days; independents pay immediately — this affects your cash flow, not just operations
7. **Rural primary care is underserved** — small orders, remote locations, government delays — but policy is consolidating through County Medical Communities

---

## Sources & References

### China Healthcare Policy & Procurement
- Zhu, Z. et al. (2023). "The national volume-based procurement policy in China." *BMJ Global Health*.
- Yue, X. (2019). "'4+7' Drug procurement reform in China." *CGD Working Paper*.
- Stanford Law School (2025). "Drug Centralized Procurement in China: Concerns and Implications."
- Lu, W. (2026). "Availability of national centralized drug procurement in regions with different levels of economic development." *Frontiers in Pharmacology*.

### Pharmacy & Hospital Inventory Management
- Ayalew, A.B. (2025). "The application of ABC-VED with multi-criteria analysis." *PMC*.
- Gebicki & Mazur (2009). "Evaluation of Inventory Policies in Hospitals' Medication Management." *IHI Publications*.
- MSH (2012). "Pharmaceutical management for health facilities."
- CPCon Group (2026). "Pharmacy Inventory Management: Complete Guide."

### China Retail Pharmacy Market
- Feng, Z. (2022). "Changes in pharmaceutical retail market and regional centralisation in China." *PMC*.
- HKEX Prospectus — "Industry Overview: Retail Pharmacy Evolution in China" (2022).

### B2B E-Commerce & Digital Ordering
- Dengyue Med (2025). "Unlocking 2025 Blue Ocean — China Pharmacy Wholesale Online."
- JD Corporate Blog (2022). "How JD Health Built the Largest Pharmaceutical Retailer in China."
- Chuangmei Pharmaceutical IPO Prospectus (2015). "Development of Pharmaceutical B2B Industry in China."
- Cloudfy (2025). "Top 5 Features Pharma Companies Need in a B2B eCommerce Platform."

### Primary Healthcare & Rural Supply
- Huo, Z. (2025). "Longitudinal Trends in Medicine Supply, Price and Utilisation in Southwestern China's Rural Primary Care."
- Fan, Z. (2024). "Whether medicine supply is really meeting primary health care needs in Shandong Province, China."
- Wu, S. & Luo, M. "Drug supply and assurance: drug shortage monitoring varieties in China."

---

*Research compiled: June 2026*
*For: SDC MSc Innovation Management — Digital Innovation Course*
*Case: Smart Warehouse Sorting & Dispatch System (Case 1)*
