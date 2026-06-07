# Sunergy Pharma Pro v3.0 — Real-Time Data Upload Feasibility Analysis

> **Document Type:** Technical Feasibility Study  
> **Scope:** Assess the necessity, architecture, and implementation path for enterprise data upload interfaces across all 20+ functional pages.  
> **Date:** 2026/06/07  
> **Status:** For Review

---

## 1. Executive Summary

### 1.1 Core Question

> **Does adding real-time data upload interfaces materially improve the project's commercial viability and generalizability?**

**Answer: Yes — with tiered prioritization.**

Adding data upload capability transforms Sunergy Pharma from a **demo-grade simulation tool** into a **pilot-ready analytics platform**. For pharmaceutical enterprises evaluating the system, the ability to "plug in their own numbers" is often the decisive factor between "interesting prototype" and "viable vendor."

However, not all 20+ pages require real data. A **tiered approach** (P0/P1/P2) balances development effort with commercial impact.

### 1.2 Key Findings at a Glance

| Finding | Detail |
|---------|--------|
| **Pages requiring real data** | 10 of 21 (P0 + P1) |
| **Recommended upload format** | CSV / Excel (.xlsx) via `st.file_uploader()` |
| **Estimated dev effort** | 2-3 days for P0 core schema; 4-5 days for full P0+P1 |
| **Commercial impact** | High — enables pilot deployments and shortens sales cycles |
| **Technical risk** | Low — Streamlit natively supports file upload; Pandas handles validation |
| **Data privacy risk** | Medium — pharmaceutical order data is sensitive; local processing only |

---

## 2. Current Data Architecture Audit

### 2.1 Data Source Taxonomy

Every page in Pro v3.0 currently draws from one of four source categories:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CURRENT DATA ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────┤
│  A. Deterministic Mock Generators                                    │
│     ├── generate_orders_basic()      → Operations Dashboard         │
│     ├── generate_order_log()         → Omni-Channel Orders          │
│     ├── generate_inventory_data()    → Warehouse & Zones            │
│     ├── generate_picking_tasks()     → Task Workstation             │
│     ├── generate_labor_data()        → Task Workstation             │
│     ├── generate_alert_feed()        → Alert Center                 │
│     └── generate_sla_history()       → SLA Analytics                │
│                                                                      │
│  B. Pre-Computed JSON Assets                                         │
│     └── load_all_json_data()         → Order Analytics              │
│         (final_results.json, order_stats.json, etc.)                │
│                                                                      │
│  C. Hard-Coded Static Data                                           │
│     ├── arena_df (Algorithm Arena)                                  │
│     ├── competitor matrix (Competitor Radar)                        │
│     ├── patent timeline (Patent Wall)                               │
│     └── pricing tiers (Plans & Pricing)                             │
│                                                                      │
│  D. Real Algorithm Modules (with synthetic input)                    │
│     ├── what_if_simulator.py         → Scenario Simulator           │
│     ├── multi_objective_scheduler.py → Strategy Optimizer           │
│     └── adaptive_policy.py           → Live Adaptive Intelligence   │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Dependency Matrix by Page

| # | Page | Current Source | Real Data Needed? | Priority |
|---|------|---------------|-------------------|----------|
| 1 | Command Center | Mixed | Low | P2 |
| 2 | **User Guide** | Static | No | — |
| 3 | **Omni-Channel Orders** | `generate_order_log()` | **Yes** | **P0** |
| 4 | **Order Analytics** | `load_all_json_data()` / mock | **Yes** | **P0** |
| 5 | **Warehouse & Zones** | `generate_inventory_data()` | **Yes** | **P0** |
| 6 | **Operations Dashboard** | `generate_orders_basic()` + hardcode | **Yes** | **P0** |
| 7 | **SLA Analytics** | `generate_sla_history()` | **Yes** | **P0** |
| 8 | **Task Workstation** | `generate_picking_tasks()` + `labor_data()` | **Yes** | **P0** |
| 9 | **Alert Center** | `generate_alert_feed()` | **Yes** | **P1** |
| 10 | Algorithm Arena | Hard-coded `arena_df` | No | P2 |
| 11 | **Scenario Simulator** | Real engine + synthetic input | **Yes** | **P1** |
| 12 | **Strategy Optimizer** | Real engine + synthetic input | **Yes** | **P1** |
| 13 | **Live Adaptive Intelligence** | Real engine + synthetic input | **Yes** | **P1** |
| 14 | KGDRL Framework | Static visualization | No | P2 |
| 15 | AI Learning Engine | Hard-coded metrics | No | P2 |
| 16 | Multi-Warehouse Network | Hard-coded table | No | P2 |
| 17 | Patent & Research Wall | Hard-coded timeline | No | P2 |
| 18 | ROI Calculator | User input only | No | P2 |
| 19 | TCO Analysis | User input only | No | P2 |
| 20 | Competitor Radar | Hard-coded matrix | No | P2 |
| 21 | Plans & Pricing | User input only | No | P2 |
| 22 | Real-Time Simulation | HTML embed | Partial | P1 |
| 23 | Demo Mode | Hard-coded slides | No | P2 |

**Summary:** 9 pages are P0/P1 (require or strongly benefit from real data). 14 pages are P2 (static or user-input driven).

---

## 3. Priority Tier Analysis

### 3.1 P0 — Core Operational Pages (Must-Have for Pilots)

These pages answer the question: *"What is happening in my warehouse RIGHT NOW?"* Without real data, they are unconvincing to operational stakeholders.

| Page | Required Data Entities | Business Value of Real Data |
|------|------------------------|----------------------------|
| **Omni-Channel Orders** | Order master table (client, SKU count, temp, deadline, status) | Buyers can see **their actual order mix** — hospital vs. pharmacy ratios, peak hour patterns, urgent order proportions |
| **Order Analytics** | Aggregated order statistics, arrival timeline | Validates the **empirical distributions** used in simulation; builds trust that the AI was trained on realistic patterns |
| **Warehouse & Zones** | SKU inventory master (name, category, temp zone, stock qty, expiry date) | **Prevents real write-offs** by surfacing near-expiry inventory that needs FIFO prioritization |
| **Operations Dashboard** | Live order status + zone utilization + near-expiry queue | **Single pane of glass** for warehouse managers; replaces walking the floor or checking 4 separate systems |
| **SLA Analytics** | Historical fulfillment records (on-time, next-day, temp compliance) by client category | Shows **actual performance gaps** and justifies investment with baseline metrics |
| **Task Workstation** | Active picking tasks + worker assignments + zone efficiency | Optimizes **real labor deployment**; DRL paths reduce actual walking distance for real workers |

**P0 Schema Coverage:**
- `orders.csv` — Order master data
- `inventory.csv` — SKU stock levels and expiry
- `tasks.csv` — Active picking tasks (optional for pilot phase)
- `workers.csv` — Labor roster and zone assignments (optional)
- `sla_history.csv` — Monthly/daily SLA fulfillment records

### 3.2 P1 — Algorithm Input Pages (Strongly Enhances Value)

These pages run real algorithms. They work with synthetic data, but their output becomes dramatically more credible when seeded with the prospect's actual order patterns.

| Page | Required Data | Business Value of Real Data |
|------|--------------|----------------------------|
| **Scenario Simulator** | Order arrival trace (time, temp, urgency) | "What-if" scenarios using **their actual peak-day data** instead of synthetic flu-season curves |
| **Strategy Optimizer** | Order batch characteristics | Pareto frontier optimized for **their specific cost structure** (not generic defaults) |
| **Live Adaptive Intelligence** | Real-time arrival rate stream | EWMA predictions trained on **their demand patterns**, not Poisson approximations |
| **Alert Center** | Exception log + sensor data | Alerts based on **their actual HVAC, picker, and temperature sensor feeds** |
| **Real-Time Simulation** | Order stream feed | HTML dashboard animation driven by **their live data** instead of random walk |

### 3.3 P2 — Static/Showcase Pages (Low or No Benefit)

These pages are either:
- **Architecture demonstrations** (KGDRL Framework, AI Learning Engine, Multi-Warehouse Network)
- **Sales tools** (ROI Calculator, TCO Analysis, Competitor Radar, Plans & Pricing)
- **Narrative content** (Patent Wall, Demo Mode, Algorithm Arena)

Adding data upload to these pages adds complexity without proportional value. They should remain static or user-input driven.

---

## 4. Recommended Data Schema Design

### 4.1 Design Principles

1. **CSV-first**: Pharmaceutical IT departments are comfortable with Excel/CSV exports from WMS or ERP systems.
2. **Minimal required columns**: Reduce integration friction by making only 5-6 columns mandatory; the rest are optional enrichments.
3. **Auto-inference**: Where possible, infer missing columns (e.g., derive "Priority" from "Deadline Hours" if not provided).
4. **Local-only processing**: No data leaves the local machine. Critical for GSP audit trails and client NDAs.
5. **Validation feedback**: Immediate, specific error messages (e.g., "Row 847: Temperature 'Room' not recognized — expected one of: Ambient, Cool, Cold, Frozen, Deep Frozen").

### 4.2 Core Schema: `orders.csv` (P0)

| Column | Type | Required? | Description | Example |
|--------|------|-----------|-------------|---------|
| `order_id` | String | Yes | Unique order identifier | ORD-20260001 |
| `client_type` | String | Yes | Customer category | Public Hospital / Chain Pharmacy / Independent Pharmacy / Primary Healthcare |
| `sku_count` | Integer | Yes | Number of line items | 4 |
| `temperature` | String | Yes | Cold-chain requirement | Ambient / Cool / Cold / Frozen / Deep Frozen |
| `deadline_hours` | Float | Yes | Hours until required dispatch | 12.5 |
| `priority` | String | No | Auto-inferred from deadline if missing | Standard / Urgent |
| `volume` | Integer | No | Total carton volume | 45 |
| `status` | String | No | Current fulfillment status | Pending / Picking / Packed / Dispatched |
| `timestamp` | ISO-8601 | No | Order intake time | 2026-06-07T08:23:00 |
| `zone` | String | No | Assigned warehouse zone | Zone A |

**Validation Rules:**
- `temperature` must be in `TEMP_ZONES` list
- `deadline_hours` > 0 and < 168 (7 days)
- `client_type` must match known categories or trigger warning

### 4.3 Core Schema: `inventory.csv` (P0)

| Column | Type | Required? | Description | Example |
|--------|------|-----------|-------------|---------|
| `sku` | String | Yes | Product identifier | INS-001 |
| `name` | String | Yes | Product name | Insulin Glargine |
| `category` | String | No | Therapeutic category | Cold Chain Insulin |
| `temperature_zone` | String | Yes | Storage requirement | Cold |
| `stock_qty` | Integer | Yes | Units on hand | 1200 |
| `expiry_date` | Date (YYYY-MM-DD) | Yes | Lot expiration | 2026-06-15 |

**Derived Column:** `days_left` = `expiry_date` - today (auto-computed)
**Derived Column:** `risk_level` = Critical/Warning/Notice/Normal (auto-computed from `days_left`)

### 4.4 Core Schema: `tasks.csv` (P1)

| Column | Type | Required? | Description | Example |
|--------|------|-----------|-------------|---------|
| `task_id` | String | Yes | Unique task identifier | TSK-12345 |
| `source_zone` | String | Yes | Pick origin | Zone B |
| `target_client` | String | Yes | Delivery destination | Public Hospital |
| `sku_checklist` | String | Yes | Items to pick | Insulin Pen x2, Amoxicillin x1 |
| `priority` | String | Yes | Task urgency | Standard / Urgent / Critical |
| `status` | String | Yes | Current state | Pending / Active Picking / Completed / Exception |
| `assigned_worker` | String | No | Operator ID | Worker-01 |
| `est_duration_min` | Integer | No | Estimated minutes | 15 |

### 4.5 Core Schema: `workers.csv` (P1)

| Column | Type | Required? | Description | Example |
|--------|------|-----------|-------------|---------|
| `worker_id` | String | Yes | Employee identifier | Worker-01 |
| `zone` | String | Yes | Primary zone | Zone A |
| `shift` | String | No | Work shift | Morning / Afternoon / Night |
| `employment_type` | String | No | Full-Time / Temporary | Full-Time |

### 4.6 Core Schema: `sla_history.csv` (P0)

| Column | Type | Required? | Description | Example |
|--------|------|-----------|-------------|---------|
| `period` | String | Yes | Month or day | 2026-01 or 2026-01-15 |
| `client_category` | String | Yes | Customer segment | Public Hospital |
| `orders_fulfilled` | Integer | Yes | Completed orders | 15234 |
| `orders_total` | Integer | Yes | Total orders | 16000 |
| `on_time_rate` | Float | Yes | % on-time delivery | 97.2 |
| `next_day_rate` | Float | Yes | % next-day fulfillment | 99.1 |
| `temp_compliance_rate` | Float | Yes | % temperature-compliant | 99.8 |
| `exception_rate` | Float | Yes | % exceptions | 0.3 |

### 4.7 Optional Schema: `alerts.csv` (P1)

| Column | Type | Required? | Description | Example |
|--------|------|-----------|-------------|---------|
| `alert_id` | String | Yes | Alert identifier | ALT-001 |
| `type` | String | Yes | Alert category | Temperature Deviation |
| `severity` | String | Yes | critical / warning / info / success | critical |
| `message` | String | Yes | Human-readable description | Cold chain threshold exceeded in Zone C |
| `timestamp` | ISO-8601 | Yes | When triggered | 2026-06-07T14:30:00 |
| `zone` | String | No | Affected zone | Zone C |
| `acknowledged` | Boolean | No | Has operator confirmed? | False |

---

## 5. Upload Interface Architecture

### 5.1 Component Design

```
┌─────────────────────────────────────────────────────────────────────┐
│                     UPLOAD INTERFACE ARCHITECTURE                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Sidebar (Global Toggle)                                             │
│  ┌─────────────────────────────────────────┐                        │
│  │  Data Source: [● Mock Data  ○ Upload]   │                        │
│  └─────────────────────────────────────────┘                        │
│                              │                                       │
│                              ▼                                       │
│  ┌─────────────────────────────────────────┐                        │
│  │  If Upload selected:                    │                        │
│  │  ┌─────────────────────────────────┐    │                        │
│  │  │ Upload orders.csv               │    │                        │
│  │  │ Upload inventory.csv            │    │                        │
│  │  │ Upload tasks.csv (optional)     │    │                        │
│  │  │ Upload sla_history.csv          │    │                        │
│  │  └─────────────────────────────────┘    │                        │
│  │  [Validate Data] → Validation Report    │                        │
│  └─────────────────────────────────────────┘                        │
│                              │                                       │
│                              ▼                                       │
│  Session State (st.session_state)                                    │
│  ├── data_source: "mock" | "upload"                                  │
│  ├── uploaded_orders: DataFrame | None                               │
│  ├── uploaded_inventory: DataFrame | None                            │
│  ├── uploaded_tasks: DataFrame | None                                │
│  ├── uploaded_sla: DataFrame | None                                  │
│  └── validation_report: dict                                         │
│                              │                                       │
│                              ▼                                       │
│  Page Renderers (conditional logic)                                  │
│  IF data_source == "upload" AND uploaded_orders is not None:         │
│      render_with_uploaded_data()                                     │
│  ELSE:                                                               │
│      render_with_mock_data()                                         │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.2 Implementation Code Pattern

```python
# In shared.py — central data router
def get_orders_data() -> pd.DataFrame:
    if st.session_state.get("data_source") == "upload" and st.session_state.get("uploaded_orders") is not None:
        return st.session_state.uploaded_orders
    return generate_order_log(n=100)

def get_inventory_data() -> pd.DataFrame:
    if st.session_state.get("data_source") == "upload" and st.session_state.get("uploaded_inventory") is not None:
        return st.session_state.uploaded_inventory
    return generate_inventory_data()
```

Each page module then calls `get_orders_data()` instead of directly calling the mock generator. This creates a **single point of switching** with zero change to page rendering logic.

### 5.3 Validation Engine

```python
def validate_orders(df: pd.DataFrame) -> dict:
    errors = []
    warnings = []
    
    # Required columns
    required = ["order_id", "client_type", "sku_count", "temperature", "deadline_hours"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        errors.append(f"Missing required columns: {', '.join(missing)}")
    
    # Temperature values
    if "temperature" in df.columns:
        invalid_temps = set(df["temperature"].unique()) - set(TEMP_ZONES)
        if invalid_temps:
            errors.append(f"Invalid temperature values: {invalid_temps}. Expected: {TEMP_ZONES}")
    
    # SKU count positivity
    if "sku_count" in df.columns and (df["sku_count"] < 1).any():
        warnings.append(f"Found {(df['sku_count'] < 1).sum()} rows with sku_count < 1")
    
    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}
```

---

## 6. "Mock vs Upload" Toggle Mechanism

### 6.1 Global Toggle (Recommended Default)

Place at the **top of the sidebar**, above Categories. This makes the data source selection a first-class navigation decision.

```
┌──────────────────────────────┐
│ 🔶 Sunergy Pharma            │
│ Professional Edition v3.0    │
├──────────────────────────────┤
│ Data Source                  │
│ ○ Use Demo Data              │
│ ○ Upload My Data    ←── NEW  │
├──────────────────────────────┤
│ Category                     │
│ ⚙️ Smart Scheduling          │
│ ...                          │
└──────────────────────────────┘
```

**Behavior:**
- **Mock Data**: All pages use `generate_*()` functions. Suitable for demos, investor pitches, and course presentations.
- **Upload My Data**: Pages with uploaded data switch to real data. Pages without uploaded data gracefully fall back to mock data with an info banner: *"Using demo data — upload [file].csv to see your own metrics."*

### 6.2 Per-Page Override (Advanced Option)

Allow power users to mix sources:
- Orders: uploaded
- Inventory: mock (if not yet ready)
- SLA: uploaded

This is implemented by checking per-file session state keys rather than a single global flag.

### 6.3 Visual Differentiation

When real data is active, add a subtle indicator so the presenter and audience are always aware:

```html
<div style="position:fixed; top:10px; right:10px; background:rgba(16,185,129,0.15); 
            color:#10b981; padding:4px 12px; border-radius:20px; font-size:0.75rem;">
    🟢 Live Data Mode
</div>
```

---

## 7. Privacy, Security & Compliance

### 7.1 Local-Only Processing

| Aspect | Policy | Rationale |
|--------|--------|-----------|
| Data storage | Session-only (`st.session_state`) | Data disappears when browser tab closes |
| Cloud upload | None | No data ever sent to Streamlit Cloud, Hugging Face, or any external API |
| File persistence | None | Uploaded files are not written to disk |
| Log files | No PII logging | Validation errors log row numbers, not order contents |

### 7.2 GSP Compliance Considerations

Pharmaceutical warehouse data is subject to strict audit requirements:
- **Temperature records**: If uploading cold-chain sensor data, ensure the upload interface notes that historical records must be immutable (read-only CSV exports from certified WMS).
- **Order traceability**: The system should not modify uploaded order IDs or timestamps — it is a read-only analytics layer.
- **Audit trail**: Consider adding a "Data Provenance" section showing file name, upload timestamp, and row count for regulatory inspectors.

---

## 8. Implementation Roadmap

### Phase 1: Foundation (Day 1)
- [ ] Add `st.file_uploader()` to sidebar with global toggle
- [ ] Implement `get_*_data()` router functions in `shared.py`
- [ ] Build `validate_orders()` and `validate_inventory()` functions
- [ ] Refactor P0 pages to use router functions

### Phase 2: Core Pages (Day 2)
- [ ] Refactor remaining P0 pages (SLA Analytics, Task Workstation, Operations Dashboard)
- [ ] Add visual "Live Data Mode" indicator
- [ ] Write user-facing upload instructions (CSV template downloads)

### Phase 3: Algorithm Integration (Day 3)
- [ ] Connect uploaded order traces to `what_if_simulator.py`
- [ ] Connect uploaded batches to `multi_objective_scheduler.py`
- [ ] Connect uploaded arrival patterns to `adaptive_policy.py`

### Phase 4: Polish (Day 4)
- [ ] Per-page fallback banners
- [ ] Data Provenance panel
- [ ] Download corrected/augmented CSV (e.g., with derived `risk_level` column)

**Total Estimated Effort: 4 days**

---

## 9. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Client uploads malformed CSV | High | Medium | Robust validation with specific row-level error messages |
| CSV encoding issues (Chinese SKUs) | Medium | Medium | Support UTF-8 and GBK; auto-detect encoding with `chardet` |
| Large file uploads (>100MB) | Low | High | Add row limit warning; recommend sampling for initial pilot |
| Data source confusion during demo | Medium | Medium | Clear visual indicator + presenter training |
| Client expects real-time streaming | Low | High | Document that v3.0 is batch-upload; streaming is Enterprise roadmap |

---

## 10. Conclusion & Recommendation

### 10.1 Is Data Upload Worth It?

**Yes — as a P0 feature for the Pro tier.**

The absence of data upload is the single most common reason pharmaceutical prospects dismiss analytics demos: *"It looks nice, but I need to see it with MY numbers."*

Adding upload capability:
- **Shortens sales cycles** by enabling self-serve pilot evaluations
- **Increases perceived value** from "academic demo" to "production tool"
- **Creates lock-in** because uploaded data + derived insights become proprietary assets
- **Justifies pricing** — a system that runs on real data commands ¥8,999/month; a simulator does not

### 10.2 Recommended Scope

Implement **P0 + P1** (10 pages) with the 6 core schemas outlined in Section 4. Leave P2 pages static. This delivers 80% of the commercial value at 40% of the full-refactor cost.

### 10.3 Next Step

If approved, I will proceed with **Phase 1 implementation**:
1. Extend `shared.py` with upload router functions
2. Add the sidebar upload panel with global toggle
3. Refactor `orders_inventory.py` and `operations.py` to use uploaded data
4. Provide downloadable CSV templates for each schema

---

> **Prepared for:** Course Defense + Investor Readiness  
> **Next Review:** Upon approval for implementation
