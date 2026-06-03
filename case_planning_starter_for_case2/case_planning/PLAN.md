# 12-Day Plan: Pharmaceutical Demand Forecasting & Intelligent Replenishment System

## Overview
Build a runnable prototype of a demand forecasting & intelligent replenishment tool for a large pharma B2B platform. The team has a data science background but limited pharma domain knowledge. The plan leverages that strength by focusing on a **Streamlit-based analytics application** with a robust Python backend, avoiding heavy web development. We will heavily invest in **synthetic data generation** to create a realistic demo environment, as no real dataset is provided.

**Plan Storage:** The master plan is stored in the repo as `PLAN.md`. The deep-research prompt for Day 1 is stored as `research_prompt_day1.md`.

**Core Philosophy:** Focus on polishing 2 primary features—**Multi-Factor Demand Forecasting** and **Intelligent Replenishment Recommendations**—with excellent visualizations and an interactive UI. Secondary features (Inventory Diagnosis, Policy Simulator, Alerts) will be integrated but kept functionally concise.

---

## Phase 1: Discovery, Research & Foundation (Days 1–3)

**Goal:** Deeply research the domain and market, then define the data model and set up the tech stack.

### Day 1: Pharma 101 & Structured Deep Research — Round 1 (Literature & Methods)
- **Domain Concepts:**
  - Understand key pharma supply chain concepts: OOH (Out-of-Hospital), Volume Procurement (集采), SKU longevity/expiry, terminal inventory, ATC drug classification.
  - Research how volume procurement works in China (price cuts, demand spikes/shifts to generic alternatives).
- **Academic & Industry Research:**
  - Search for recent papers and industry reports on **pharmaceutical demand forecasting** (e.g., use of machine learning in pharma supply chains, hierarchical forecasting for SKUs, handling long-tail/intermittent demand).
  - Research best practices for **inventory optimization in healthcare/pharma** (safety stock policies, expiry-aware replenishment, multi-echelon inventory).
  - Look for case studies from companies like IQVIA, McKesson, or pharma B2B platforms in Asia.
- **Outputs:** A research digest document summarizing 3-5 key methodologies found, their pros/cons, and how they apply to this case.

### Day 2: Deep Research — Round 2 (Market, Competitors & Policy)
- **Market & Competitive Landscape:**
  - Research the China pharma B2B market: major players (e.g., YaoFangWang, KangAiDuo), their platform features, and whether they offer forecasting or replenishment tools.
  - Analyze the competitive moat: why would a franchise pharmacy pay for this? What is missing in current offerings?
- **Policy & Regulatory Deep Dive:**
  - Research specifics of China's National Volume-Based Procurement (VBP) programs: which drug classes are affected, typical price reduction magnitudes, demand shift patterns (hospital vs. retail), and historical batch lists.
  - Identify external data sources for the demo: public flu surveillance data (e.g., China CDC weekly reports), seasonal allergy patterns, holiday effects, and publicly available policy calendars.
- **Outputs:** A 1-page competitor map, a policy impact summary, and a curated list of external data signals.

### Day 3: Tech Stack Setup & Data Architecture
- **Tech Stack:**
  - **Backend:** Python, Pandas, NumPy, Scikit-learn, Statsmodels/Prophet, LightGBM (optional for advanced model).
  - **Frontend:** Streamlit (rapid, interactive, Python-native).
  - **Viz:** Plotly (interactive time-series charts).
  - **Env:** `venv`, `requirements.txt`, GitHub repo.
- **Data Architecture:**
  - Design the synthetic data generator, informed by research findings. We need 3 layers of data:
    1.  **Master Data:** ~500 representative SKUs across 5-6 therapeutic categories (e.g., Cardiovascular, Antibiotics, Diabetes, Respiratory, CNS). Include attributes: **ATC-1 through ATC-4 codes**, price, expiry window, volume-procurement status, and generic vs. branded flag.
    2.  **Sales Transaction Data:** 2 years of daily/weekly sales for these SKUs across different pharmacy types (Hospital, Chain, Independent). Must embed realistic patterns: trend, seasonality (flu season, allergy season), spikes (epidemics), and structural breaks (policy shocks).
    3.  **External Signals:** **China CDC weekly ILI%** (influenza-like illness), **Baidu Index** flu search trends, **VBP batch implementation dates** (known structural breaks), and China public holiday calendars.
- **Output:** Initialized repo, working data generator skeleton, and a research bibliography.

---

## Phase 2: Data & Core Algorithm Development (Days 4–7)

**Goal:** Generate realistic data and build the forecasting + replenishment engine.

### Day 4: Synthetic Data Generator (Critical Path)
- Build a modular Python script to generate the full synthetic dataset.
- **SKU Profiles:**
  - *Fast-Movers:* High volume, low noise (e.g., common chronic disease meds).
  - *Seasonal:* Demand tied to external signals (e.g., Oseltamivir for flu season).
  - *Slow-Movers / Long-Tail:* Very low volume, intermittent demand (e.g., rare disease drugs).
  - *Policy-Shocked:* SKUs that experience a sudden ~50% price drop and subsequent **hospital-to-retail demand spillover** at a specific VBP batch date.
- **Pharmacy Profiles:** Different base demand levels and variability for Hospitals vs. Chains vs. Independents.
- **Demand Segmentation (ADI):** Compute **Average Inter-Demand Interval (ADI)** for each SKU and classify into: *Smooth* (ADI < 1.32), *Intermittent* (1.32 ≤ ADI < 5), and *Lumpy* (ADI ≥ 5). This determines the forecasting method assigned.
- **Validation:** Visually inspect generated time series to ensure they look realistic. Save data to Parquet/CSV.

### Day 5: Demand Forecasting Engine — Baseline
- Implement a **hierarchical forecasting** approach using the **ATC-1 to ATC-4 hierarchy**. Reconcile bottom-up, top-down, and middle-out forecasts (e.g., via `hierarchicalforecast` or similar).
- **Segmented Models by Demand Pattern:**
  - *Smooth SKUs (ADI < 1.32):* **Exponential Smoothing (ETS)** or **Prophet** for seasonality.
  - *Intermittent / Long-Tail SKUs (ADI ≥ 1.32):* **Croston's method**, **SBA (Syntetos-Boylan Approximation)**, or **TSB** to handle sparse demand and avoid bias.
- **Advanced Model (for demo SKU):**
  - A supervised learning model (e.g., **XGBoost** or **LightGBM**) using lag features, rolling statistics, ATC hierarchy features, and external regressors (**China CDC ILI%**, **Baidu Index**, **VBP batch binary flags**, month-of-year).
- **Evaluation:** MAPE, RMSE, SMAPE. Use a rolling origin validation setup.
- **Output:** A Python module that takes SKU ID + pharmacy type and returns a 30-day forecast with confidence intervals.

### Day 6: Intelligent Replenishment Engine
- Translate forecasts into actionable recommendations.
- **Policy:** Use **periodic review (R, S)**—review every **R = 7 or 14 days**, order up to level **S**—which aligns with real pharmacy replenishment practice.
- **Safety Stock by Demand Type:**
  - *Smooth SKUs:* Standard formula: $Z \times \sigma_d \times \sqrt{L}$ (normal lead-time demand).
  - *Intermittent SKUs:* Use **negative-binomial–Bernoulli (NBB)** lead-time demand or Croston-based safety stock to avoid overstocking zero-demand periods. [^18^][^23^]
- **Order Quantity:** Order-up-to level $S$ = forecasted demand over (review period + lead time) + safety stock. Constrain by **days-to-expiry** (FEFO logic: do not order if expected demand exceeds remaining shelf life buffer).
- **Expiry Logic:** Apply **First-Expired-First-Out (FEFO)** picking rules in inventory health diagnosis; flag lots nearing expiry (< 6 months) and model discard cost as a penalty.
- **Personalization:** Adjust service level $Z$ and review period $R$ based on pharmacy type (e.g., Hospitals get higher service levels, shorter $R$ for cold-chain SKUs).
- **Output:** A module that takes current inventory levels and returns a prioritized restock list with quantities, timing, risk flags, and rationale.

### Day 7: SKU-Level Demo Preparation & Model Tuning
- Select the **demo SKU** (e.g., a chronic disease medication like Metformin or Amlodipine, or a seasonal one like an antiviral).
- Tune the advanced forecasting model specifically for this SKU.
- Generate a 3-month historical forecast vs. actual comparison to showcase in the final demo.
- Build the **Inventory Health Diagnosis** module (simpler): ABC analysis (by revenue), XYZ analysis (by demand volatility), and expiry risk flagging.
- *End-of-Phase Checkpoint:* You should be able to run a Python script that outputs a forecast plot and a replenishment recommendation table.

---

## Phase 3: Application Development & UX (Days 8–10)

**Goal:** Wrap the engine in an interactive Streamlit application.

### Day 8: Streamlit Shell & Forecasting Dashboard
- **App Structure (Multi-page Streamlit or sidebar navigation):**
  - Demand Forecasting
  - Replenishment Recommendations
  - Inventory Health
  - Policy Simulator
- **Forecasting Page:**
  - Dropdown to select SKU and Pharmacy Type.
  - Interactive Plotly chart showing historical sales, 30-day forecast, and confidence intervals.
  - Display key metrics (Forecast MAPE, trend direction).
  - Show feature importance (if using tree-based model) to explain *why* the forecast is what it is.

### Day 9: Replenishment & Inventory Dashboards
- **Replenishment Page:**
  - Input fields for current inventory levels (or simulate them).
  - Display a prioritized restock list: SKU, current stock, days of supply remaining, recommended order quantity, recommended order date, risk level (Stockout/Healthy/Overstock).
  - Visual indicators (red/yellow/green) for urgency.
- **Inventory Health Page:**
  - Interactive ABC/XYZ matrix (scatter plot).
  - Tables for slow-moving / near-expiry items.
  - Summary KPIs (overall inventory turnover, stockout risk count).

### Day 10: Policy Simulator, Alerts, & Polish
- **Policy Simulator Page:**
  - Use **real VBP batch dates** (e.g., 10th round Apr 2025 covering cardiovascular/diabetes) as default scenario presets.
  - Simulate **hospital-to-retail demand spillover**: when a drug is selected in VBP, model the drop in hospital demand and the corresponding spike in OOH/retail demand for non-selected alternatives.
  - Show before/after impact on demand, revenue, and inventory reallocation needs.
- **Alerts Module:**
  - Proactive notifications for impending stockouts (predicted within 5-7 days) and expiry overages (lots > 6 months old with no demand).
- **UX Polish:** Add a professional title, clean layout, helper tooltips explaining pharma terms (ATC, VBP, FEFO), and a concise "How to Use" section.

---

## Phase 4: Business Analysis & Integration (Days 11–12)

**Goal:** Answer "who will pay for this?" and prepare the final narrative.

### Day 11: Business Feasibility Analysis Document
- **Target Users:**
  - *Primary:* The Enterprise B2B platform (as a value-add to their 340k active users).
  - *Secondary:* Procurement managers at franchise pharmacies and chain stores.
- **Value Proposition:**
  - Reduce the RMB 420m annual stockout loss by X% via better forecasting.
  - Reduce inventory holding costs and expiry write-offs for slow-moving items using FEFO-aware replenishment.
  - Fill the competitive whitespace: **SAP IBP and IQVIA serve large manufacturers and hospital chains**, but no major player offers long-tail-aware, VBP-responsive forecasting for China's OOH B2B franchise networks.
- **Go-To-Market Strategy:**
  - *Phase 1:* Integrate as a premium feature within the existing B2B e-commerce platform (freemium basic alerts, subscription for advanced forecasting).
  - *Phase 2:* White-label solution for large chain pharmacies.
  - *Pricing:* SaaS subscription tiered by number of SKUs/pharmacies managed.
- **Financial Projection:** Rough bottom-up estimate of savings.

### Day 12: End-to-End Testing & Demo Rehearsal
- Run the full application end-to-end.
- Record a 3-5 minute walkthrough video or rehearse the live demo flow.
- Ensure the SKU-level demo (3-month forecast vs. actual) is prominently featured and narrated clearly.
- Fix any bugs. Optimize slow queries/calculations (use Streamlit caching aggressively).
- **Deliverables Check:**
  - [ ] Runnable prototype (Streamlit app).
  - [ ] SKU-level forecast demo (integrated in the app).
  - [ ] Business feasibility analysis (Markdown/PDF).

---

## Phase 5: Buffer & Final Delivery (Extra if needed)

- **Buffer Day:** Handle unexpected issues, improve model accuracy if time permits, or enhance UI aesthetics.
- Final code cleanup, README with setup instructions.
- Package deliverables for submission.

---

## Key Technical Decisions & Rationale

1.  **Synthetic Data over Real Data:** No dataset was provided. A high-quality synthetic generator is faster than data hunting and allows us to perfectly inject the business problems (long-tail, policy shocks) into the data.
2.  **Streamlit over React/Angular:** The team has data science, not frontend engineering, expertise. Streamlit allows building a polished, interactive data app in pure Python.
3.  **Segmented Modeling by Demand Pattern:** Use **ADI classification** to assign methods: ETS/Prophet for smooth SKUs, **Croston/SBA/TSB** for intermittent/long-tail SKUs, and XGBoost for the demo SKU. This is the academically supported standard for large pharma portfolios.
4.  **Hierarchical ATC Reconciliation:** Model demand at **ATC-1 through ATC-4** levels and reconcile forecasts (bottom-up / top-down / optimal) to borrow strength across related drugs and handle substitution effects.
5.  **Periodic Review (R,S) Replenishment:** Pharmacies review inventory weekly or bi-weekly, not continuously. The replenishment engine mirrors this real-world practice.
6.  **FEFO Inventory Logic:** Pharma uses **First-Expired-First-Out**, not FIFO. The inventory health module must flag near-expiry lots and constrain orders by shelf-life remaining.

## Risk Mitigation

- **Risk: Pharma domain knowledge gap.**
  - *Mitigation:* Spend Day 1 intensively reading up on ATC codes, volume procurement mechanics, and supply chain KPIs. Use AI tools to accelerate this research.
- **Risk: Forecasting models are inaccurate due to synthetic data artifacts.**
  - *Mitigation:* Keep models relatively simple (less prone to overfitting noise). Focus on interpretability and business logic (safety stock) rather than claiming 99% accuracy.
- **Risk: Scope creep (trying to build too many features).**
  - *Mitigation:* Strictly prioritize the Forecasting and Replenishment pages. The Policy Simulator and Inventory Health are secondary and can be simplified to table-level visualizations if needed.

## Deliverables Summary

| Deliverable | Location / Format |
| :--- | :--- |
| Runnable Prototype | Streamlit App (`app.py`) |
| Forecasting & Replenishment Engine | Python modules (`forecast_engine.py`, `replenishment_engine.py`) |
| Synthetic Data Generator | Python script (`data_generator.py`) + generated Parquet files |
| SKU-Level Demo | Embedded in Streamlit app (3-month forecast vs. actual chart) |
| Business Feasibility Analysis | Markdown document (`BUSINESS_ANALYSIS.md`) |
| Setup & Run Instructions | `README.md` |
