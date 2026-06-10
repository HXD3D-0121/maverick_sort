# Research Day 1 Digest: Pharmaceutical Demand Forecasting & Intelligent Replenishment

## Executive Summary

- **The China VBP policy is the dominant demand shock mechanism.** Ten national batches since 2018 have cut prices **48–59%** on **436+ drugs**, forcing demand to shift from hospital channels to retail/OOH channels when patented drugs lose tenders or patients bypass public hospitals for perceived quality. [^1^][^56^] Any forecasting model must treat VBP batch implementation dates as **structural break points** with asymmetric effects across drug classes.

- **Hierarchical forecasting using the ATC classification system is the established paradigm for large pharma SKU portfolios.** Academic work demonstrates that grouping 380K+ SKUs by **ATC level 1–4** and reconciling bottom-up / top-down forecasts captures substitution patterns and shared seasonality far better than SKU-level models alone. [^14^][^60^]

- **Intermittent demand methods (Croston family) are essential for the long tail.** For the **~78% low-frequency SKUs**, standard exponential smoothing fails. The **Syntetos-Boylan Approximation (SBA)** and **TSB** methods, combined with **negative-binomial lead-time demand** models, are the practical standard and can reduce safety stock **15–25%** while maintaining service levels. [^18^][^23^]

- **External signals (flu surveillance, VBP dates, holidays) are high-value feature candidates.** China CDC publishes weekly ILI data; VBP batch histories are publicly documented; and Spring Festival creates predictable demand dips. Models that incorporate these signals (e.g., **KG-GCN-LSTM**, **hybrid ARIMA-LSTM**) consistently outperform pure time-series baselines by **3–6 percentage points** in SMAPE. [^68^][^13^]

- **The competitive gap is in B2B-specific, long-tail-aware, policy-responsive forecasting.** SAP IBP and IQVIA serve large manufacturers and hospital chains with enterprise-grade S&OP tools but do not address the **franchise-pharmacy, 380K-SKU, VBP-shock** context of China’s OOH B2B platforms. [^26^][^49^]

---

## 1. Domain Primer: Pharma Supply Chain Fundamentals

### 1.1 Out-of-Hospital (OOH) / Retail Pharmacy vs. Hospital Distribution

**Definition:** In China, pharmaceutical distribution splits into two fundamentally different channels. **Hospital distribution** serves public institutions (tertiary, secondary, and primary hospitals) through centralized provincial tender processes and national VBP schemes. Hospitals historically accounted for **~70% of drug sales** in 2023. [^1^] **OOH / retail pharmacy distribution** serves community pharmacies, clinics, and increasingly, patients directly through B2B e-commerce platforms. The OOH channel captures the remaining **~30%** of sales but is growing rapidly as patients bypass hospital channels for convenience, price comparison, or access to non-VBP drugs. [^1^]

**Why it matters for forecasting:** Hospital demand is driven by physician prescribing patterns, reimbursement policies, and VBP tender volumes. It is relatively predictable at the aggregate level but opaque at the SKU level due to centralized procurement. OOH demand, by contrast, is driven by **patient self-selection**, seasonal illness patterns, promotional activity, and the **spillover effect** from VBP—when patients cannot obtain their preferred brand in hospital, they purchase it at retail. [^1^][^67^] This creates a **two-tier market** where the same molecule may see surging retail demand precisely when its hospital demand collapses.

**Data-modeling implications:** A model trained only on historical sales from one channel will fail when policy shifts demand between channels. The team should treat **channel-specific demand series** as separate but coupled time series, or at minimum, include **VBP-selection status** as a binary feature. The B2B platform sits in the OOH channel and captures downstream demand from **dispensing terminals** (pharmacies, clinics); understanding that these terminals hold their own inventory introduces a **wholesaler-demand vs. true patient-demand** distinction. [^80^][^94^]

### 1.2 National Volume-Based Procurement (VBP) / 集采

**Mechanics:** The National Healthcare Security Administration (NHSA) organizes centralized tenders where manufacturers bid to supply selected drugs to public hospitals at guaranteed volumes. The lowest bidders win, and their drugs become the **reimbursed standard** in hospitals. [^1^][^3^] VBP covers only **off-patent drugs** (generics and mature molecules), not innovative drugs. As of late 2024, **10 national batches** covering **436 products** have been implemented, with price reductions averaging **50–60%** per batch. [^56^][^58^]

**Batch history (simplified):**

| Batch | Date | Products | Avg. Price Cut |
|-------|------|----------|----------------|
| Pilot (4+7) | Dec 2018 | 25 | 52% |
| 1st Expansion | Sep 2019 | 25 | 59% |
| 2nd | Jan 2020 | 32 | 53% |
| 3rd | Aug 2020 | 55 | 53% |
| 4th | Feb 2021 | 45 | 52% |
| 5th | Jun 2021 | 61 | 56% |
| 6th (Insulin) | Nov 2021 | 16 | 48% |
| 7th | Jul 2022 | 60 | 48% |
| 8th | Apr 2023 | 39 | 56% |
| 9th | Nov 2023 | 41 | 58% |
| 10th | Nov 2024 | 62 | ~61% |
| 11th | Oct 2025 | 55 | ~61% |

*Sources: [^56^][^58^][^52^][^62^]*

**Demand-shifting dynamics:** When a drug is selected in VBP, its **hospital demand surges** (due to guaranteed volumes and physician targets) while its **retail demand may collapse** if the winning brand is a cheap generic that patients perceive as lower quality. Conversely, when an **original branded drug loses** the VBP tender, its hospital demand plummets but its **retail/OOH demand often spikes** as patients purchase it out-of-pocket. [^1^][^15^] Studies using DID models confirm VBP drug expenditures fell **42.19%** while alternative (non-VBP) drug expenditures rose **11.52%** post-policy. [^15^]

**Data-modeling implications:** VBP implementation dates should be encoded as **known intervention points** in the time series. A difference-in-differences (DID) or interrupted time-series framework can quantify the shift. For the demo, simulating a VBP shock on a selected drug class (e.g., statins, antihypertensives) and showing demand reallocation to retail would be a powerful storytelling device. The 10th round (April 2025 implementation) covering cardiovascular, diabetes, and oncology drugs is a recent, well-documented case. [^52^][^12^]

### 1.3 ATC Classification System

**Definition:** The **Anatomical Therapeutic Chemical (ATC)** classification, maintained by the WHO Collaborating Centre for Drug Statistics Methodology, groups drugs into a five-level hierarchy. Level 1 divides drugs into **14 anatomical main groups** (A = Alimentary tract, C = Cardiovascular, J = Anti-infectives, N = Nervous system, etc.). Level 2 indicates therapeutic subgroups, Level 3 pharmacological subgroups, Level 4 chemical subgroups, and Level 5 the individual chemical substance. [^14^]

**Why it matters for forecasting:** In a portfolio of **380,000 SKUs**, individual SKU histories are sparse. The ATC hierarchy provides a principled way to **"borrow strength"** across related products. Drugs within the same ATC-4 group (e.g., all statins, C10AA) share indication, patient population, and often seasonality. Forecasting at higher ATC levels and reconciling downward (top-down) captures macro trends (e.g., cardiovascular drug demand growth) that individual SKU models miss. [^14^][^60^]

**Data-modeling implications:** The team should map every SKU to its **ATC-1 through ATC-5 codes** and use these as features in a **hierarchical forecasting framework**. Rob Hyndman’s **forecast reconciliation** methods (bottom-up, top-down, middle-out, and optimal reconciliation) are the standard approach and are implemented in open-source libraries like `hts` in R and hierarchicalforecast in Python. [^14^] The KG-GCN-LSTM paper also demonstrates that encoding **drug-substitution and co-prescription relationships** (which naturally map onto ATC groupings) via a knowledge graph improves forecast accuracy substantially. [^68^]

### 1.4 SKU Attributes That Matter for Inventory

| Attribute | Why It Matters | Modeling Implication |
|-----------|---------------|---------------------|
| **Shelf life / Expiry window** | Drugs expire and become unsellable; short-dated stock must be liquidated or destroyed. Typical pharma shelf life: **24–36 months** from manufacture, but retail pharmacies often require **>12 months** remaining at receipt. [^51^] | Include **days-to-expiry** as a feature; use **FEFO** (First-Expired-First-Out) picking logic; model discard cost as a penalty term in replenishment optimization. |
| **Cold-chain requirements** | Vaccines, biologics, insulin require **2–8°C** storage. Cold-chain capacity is limited and expensive. | Segregate cold-chain SKUs; model storage capacity as a constraint; shorter replenishment cycles for temperature-sensitive items. |
| **Narcotic / Controlled-substance scheduling** | Controlled drugs (e.g., opioids, psychotropics) face strict purchase quotas, special licensing, and mandatory tracking. | Demand may be capped by regulatory quotas rather than market demand; include **scheduling class** as a categorical feature. |
| **Generic vs. Branded substitution** | Generics are substitutable; branded drugs (especially imported) may retain loyal patients post-VBP. [^1^] | Model **cross-price elasticity** between generic and branded versions of the same molecule; VBP-selection status affects substitution patterns. |

### 1.5 Terminal Inventory: Ownership and Data Availability

**What it is:** In China’s OOH pharmaceutical market, **terminal inventory** refers to the stock held at the point of care: **franchise pharmacies** (加盟店), independent community pharmacies, clinics, and small hospitals. These are the "dispensing terminals" that purchase from the B2B platform. [^67^]

**Ownership structure:** The B2B platform (the case client) operates as an **intermediary**—it sources from manufacturers/distributors and sells to franchise pharmacies. The **platform owns the inventory** in its central warehouse, but **franchise pharmacies own their own shelf stock**. [^67^] This creates a classic **multi-echelon** structure where the platform sees its own outbound sales (wholesaler demand) but not the true patient-level demand at the terminal.

**Data-availability challenges:** The platform has complete visibility of **its own inventory** and **outbound shipments** to each franchise. It may have limited or delayed visibility of **terminal sell-through** (true demand), depending on whether franchises share point-of-sale data. The HKEX prospectus of a similar OOH pharma B2B company notes that direct e-commerce store operations now provide **first-hand transaction data** on purchasing patterns and inventory turnover at the terminal level. [^67^] For the demo, the team should assume access to **platform outbound sales** (the target variable) and optionally **terminal inventory snapshots** (a valuable feature, per Zhu et al. 2021). [^80^]

---

## 2. Literature Review

### 2.1 Zhu, Ninh, Zhao & Liu (2021) — Cross-Series ML Forecasting with Supply-Chain Information

**Citation:** Zhu, X., Ninh, A., Zhao, H., & Liu, Z. (2021). Demand forecasting with supply-chain information and machine learning: Evidence in the pharmaceutical industry. *Production and Operations Management*, 30(9), 3231–3252. https://doi.org/10.1111/poms.13426 [^80^][^95^]

**Summary:** This is the **landmark paper** at the intersection of machine learning and pharmaceutical demand forecasting. The authors propose a **cross-series training framework** that "borrows" time-series data from many related products and trains gradient-boosted tree models (XGBoost, LightGBM) to predict demand. They further enhance performance by incorporating **non-demand features**: downstream inventory levels across products, supply-chain structure (distribution network topology), and domain knowledge (ATC class, drug form, dosage). Tested on two large datasets from major pharma manufacturers, the framework consistently outperformed traditional statistical methods.

**Key findings:** The paper provides **empirical evidence that downstream inventory information improves forecast accuracy**—a critical insight for the case, since the platform has visibility into franchise inventory. The cross-series approach is especially valuable for **short-history or new SKUs** (the "cold-start" problem), which is pervasive in a 380K-SKU portfolio.

**Pros/cons:** Highly relevant methodology; strong empirical validation. Limitation: focuses on manufacturer-to-distributor demand, not the B2B-to-franchise context. Requires substantial feature engineering infrastructure.

**Relevance to case:** Directly applicable. The team can replicate the cross-series + downstream-inventory feature approach using the platform’s SKU hierarchy and franchise inventory data.

### 2.2 Rathipriya et al. (2023) — Neural Networks for ATC-Classified Pharma Demand

**Citation:** Rathipriya, R., Abdul Rahman, A. A., Dhamodharavadhani, S., Meero, A., & Yoganandan, G. (2023). Demand forecasting model for time-series pharmaceutical data using shallow and deep neural network model. *Neural Computing and Applications*, 35, 1945–1957. [^60^]

**Summary:** The authors work with a Kaggle pharmaceutical sales dataset of **600,000 sales instances across 57 drugs** (2014–2019). They classify drugs into **8 ATC categories** and compare shallow neural networks (RBF, GRNN) with deep LSTM models. The LSTM architecture captures nonlinear temporal patterns and seasonal effects in drug demand, outperforming shallow networks on RMSE.

**Key findings:** LSTM models are effective at capturing **seasonal demand fluctuations** in pharmaceutical sales. The ATC-level grouping demonstrates that **hierarchical aggregation** improves model stability for sparse SKUs.

**Pros/cons:** Accessible methodology using standard deep-learning frameworks. Limitation: dataset is relatively small and lacks external features (epidemiological, policy).

**Relevance to case:** Validates the ATC-hierarchical approach. Provides a baseline architecture (LSTM) that the team can extend with external signals and cross-SKU features.

### 2.3 Fourkiotis & Tsadiras (2024) — ML vs. Statistical Methods for Pharma Sales

**Citation:** Fourkiotis, K. P., & Tsadiras, A. (2024). Applying machine learning and statistical forecasting methods for enhancing pharmaceutical sales predictions. *Forecasting*, 6(1), 170–186. https://doi.org/10.3390/forecast6010010 [^97^][^111^]

**Summary:** A direct **benchmarking study** comparing XGBoost, Random Forest, SVR, ARIMA, and Exponential Smoothing on pharmaceutical sales data. XGBoost emerged as the top performer for **seasonality and volatility management**, while ARIMA performed adequately for stable, linear trends.

**Key findings:** Machine learning methods (especially **XGBoost**) excel at handling **nonlinear seasonality** and **promotional spikes** in pharmaceutical demand. The hybrid approach—using statistical methods for stable SKUs and ML for volatile ones—outperforms any single method across the portfolio.

**Pros/cons:** Practical, implementation-oriented findings. Limitation: single-country (Greek) dataset; may not generalize to China’s VBP-driven dynamics.

**Relevance to case:** Supports a **segmented modeling strategy**: statistical baselines for high-volume chronic meds, ML models for acute/seasonal/volatile SKUs. XGBoost is a strong candidate for the demo given its speed and interpretability.

### 2.4 Lu, Chen, Zhang & Wan (2026) — KG-GCN-LSTM for Pharma Demand

**Citation:** Lu, G., Chen, X., Zhang, H., & Wan, J. (2026). Pharmaceutical demand forecasting via GCN-LSTM: A knowledge graph-based approach. *Scientific Reports*. [^68^][^69^]

**Summary:** Proposes a **hybrid KG-GCN-LSTM architecture** that integrates a **pharmaceutical knowledge graph** (encoding drug-drug substitution and drug-symptom relationships) with Graph Convolutional Networks (GCN) for relational feature extraction and LSTM for temporal modeling. The knowledge graph contributes approximately **half of the model’s performance improvement**.

**Key findings:** Achieves **SMAPE of 8.24%** vs. 11.86% for NBEATS and comparable performance to TimeMixer. The clipping operation on GCN layers focuses attention on the target drug’s most relevant substitutes.

**Pros/cons:** State-of-the-art accuracy; highly interpretable via knowledge-graph visualization. Limitation: requires constructing and maintaining a drug knowledge graph; computationally heavier than XGBoost.

**Relevance to case:** Highly relevant for the **policy-impact simulation** feature. The knowledge graph naturally encodes VBP-driven substitution patterns (e.g., when atorvastatin goes VBP, demand shifts to rosuvastatin).

### 2.5 Schisa & Farnè (2025) / Frontiers Hybrid ML Review (2026)

**Citation:** Schisa, F., & Farnè, M. (2025). Weekly demand for respiratory drugs: MBB-RF, LSTM, Prophet comparison. *Journal of Forecasting*; and Frontiers in AI (2026) review. [^13^]

**Summary:** These studies systematically review and benchmark forecasting methods for pharmaceutical supply chains under **seasonal disruption** (flu seasons) and **regulatory shocks** (VBP-like policies). The Frontiers paper specifically identifies **hybrid models** (ARIMA + LSTM, statistical + ML combinations) as the most robust approach for healthcare supply chains facing dual uncertainty from epidemiological and policy drivers.

**Key findings:** **LSTM and MBB-RF** excel at capturing nonlinear fluctuations. Hybrid ARIMA-LSTM models outperform standalone models by combining linear trend capture with nonlinear pattern detection. [^13^]

**Pros/cons:** Comprehensive methodological survey. Limitation: review papers lack novel empirical contribution.

**Relevance to case:** Provides the theoretical justification for the team’s proposed **multi-factor, hybrid forecasting architecture**.

---

## 3. Inventory & Replenishment Methods

### 3.1 Safety-Stock Policies: Intermittent vs. Smooth Demand

**For smooth-demand SKUs (chronic medications, high-frequency):** The standard **continuous-review (R,Q) policy** with normally distributed lead-time demand is appropriate. Safety stock is calculated as:

$$\text{Safety Stock} = Z \times \sigma_d \times \sqrt{L}$$

where $Z$ is the service-level factor (1.28 for 90%, 1.65 for 95%, 2.33 for 99%), $\sigma_d$ is the standard deviation of daily demand, and $L$ is the lead time in days. [^99^]

**For intermittent-demand SKUs (long-tail, 78% of portfolio):** Standard safety-stock formulas fail because demand is mostly zero with occasional spikes. The **Croston method** and its extensions are the practical standard. [^18^][^23^]

| Method | Core Idea | Best For |
|--------|-----------|----------|
| **Croston (1972)** | Separately smooths inter-demand interval and demand size; forecast = size/interval | Moderate intermittency (ADI 1.32–5) |
| **SBA (Syntetos-Boylan Approx., 2005)** | Corrects Croston’s positive bias with factor (1 − α/2) | Same as Croston, better accuracy |
| **TSB (Teunter-Syntetos-Babai, 2011)** | Replaces interval with demand-occurrence probability; handles obsolescence | Declining-demand / end-of-life SKUs |
| **SK / SK-SSA (2025)** | Non-parametric occurrence probability + Singular Spectrum Analysis for lumpy series | Highly lumpy demand [^23^] |

The **Average Inter-Demand Interval (ADI)** classifies items: **ADI < 1.32** → standard methods; **1.32 ≤ ADI < 5** → Croston family; **ADI ≥ 5** → extremely intermittent (consider make-to-order or pure statistical approaches). [^18^] For replenishment policy, a **negative-binomial–Bernoulli (NBB) lead-time demand** specification links forecasts directly to safety-stock and backorder trade-offs. [^23^]

### 3.2 Expiry-Aware Replenishment

**The FEFO principle:** Pharmaceutical inventory rotation follows **First-Expired-First-Out (FEFO)**, not FIFO. Items closest to expiration are picked and shipped first, regardless of arrival date. [^51^] This requires **lot-level expiry tracking** at every node in the supply chain.

**Discard cost modeling:** When inventory expires before sale, the entire investment is lost. The **discard cost** = unit cost + disposal cost + potential regulatory penalty. Practitioners model this by constraining order quantities such that **expected demand during [order cycle + safety period] < remaining shelf life**. For a drug with 18 months shelf life and a 30-day replenishment cycle, the maximum order quantity should not exceed expected demand over ~15 months (allowing a buffer for the last few months when pharmacies reject short-dated stock).

**Practical implementation:** Modern WMS and pharmacy management systems automate FEFO picking and generate **expiry alerts** at configurable thresholds (e.g., 6 months, 3 months, 1 month to expiry). [^51^][^54^] For the demo, the team should include **days-to-expiry** as a replenishment constraint and model the **cost of expiry-driven write-offs** (~RMB 420m annual loss in the case description) as a KPI.

### 3.3 Multi-Echelon Inventory Optimization

The platform operates a **two-echelon** structure: **central warehouse → franchise pharmacies**. The academic literature and industry practice converge on several relevant approaches:

**Base-stock policies:** Each echelon maintains a target inventory position (base-stock level). When inventory drops below the target, an order is placed to restore it. The optimal base-stock level balances holding cost against stockout cost and depends on the **lead-time demand distribution** at each echelon.

**DDMRP (Demand-Driven Material Requirements Planning):** SAP’s implementation of DDMRP uses **strategic decoupling points** and **dynamically managed buffer levels** to absorb demand and supply variability. [^22^] Buffers are sized based on variability (lead time, demand, supply) and adjusted dynamically. DDMRP is designed precisely for the **bullwhip-effect mitigation** challenge in multi-echelon pharma supply chains.

**Practical fit for the case:** The franchise pharmacy network (28,600 stores) is too large for full centralized base-stock optimization. A practical approach is **cluster-based replenishment**: group pharmacies by region/demand pattern, set cluster-level safety stocks, and allow individual pharmacies to trigger replenishment when their inventory hits a reorder point. The platform’s role is to **aggregate demand signals** across clusters and **coordinate upstream orders** with manufacturers.

### 3.4 Replenishment Frequency

Pharmacy retail typically uses **periodic review** (weekly or bi-weekly) rather than continuous review, because:
- Order consolidation reduces transportation cost
- Weekly review aligns with manufacturer delivery schedules
- Franchise pharmacies lack real-time inventory monitoring infrastructure

For the demo, a **7-day or 14-day review period** with an **(R,S) policy** (review every R days, order up to level S) is realistic. High-value or cold-chain SKUs may warrant **continuous review (R,Q)** with lower reorder points.

---

## 4. External Data Sources

| Data Source | URL / Access Method | Update Frequency | How to Integrate |
|-------------|---------------------|-----------------|------------------|
| **China CDC Weekly Influenza Surveillance** | https://ivdc.chinacdc.cn/cnic/zyzx/lgzb/ (weekly reports) [^98^][^112^] | Weekly | Download weekly ILI% and positivity rates; merge by region and week as time-series features for respiratory/antiviral drug demand models |
| **WHO FluNet (Global Influenza Surveillance)** | https://www.who.int/tools/flunet [^71^] | Weekly | Cross-validate China CDC data; useful for comparing northern vs. southern China flu patterns |
| **Baidu Index (Search Trends)** | http://index.baidu.com [^17^] | Daily | Query keywords like "flu" (流感), "influenza" for proxy of public health concern; lagged correlation with OTC demand |
| **China VBP Batch Release Dates** | NHSA official announcements; compiled summaries at ChemLinked, IQVIA [^52^][^53^] | Irregular (1–2 batches/year) | Encode as binary intervention variables; use batch implementation date as structural break point |
| **China Public Holiday Calendar** | Standard calendar data (Spring Festival, Golden Week, etc.) | Annual | Model as demand-suppression events (pharmacies closed/reduced hours during Spring Festival week) |
| **NRDL (National Reimbursement Drug List) Updates** | NHSA announcements [^53^] | Annual | New additions drive hospital demand; deletions shift demand to OOH channels |
| **Pharmaceutical Sales Datasets (Open)** | Kaggle pharma sales datasets [^60^]; IQVIA market data (commercial) | Varies | Kaggle dataset useful for validating demand distribution shapes and ATC-level seasonality patterns |

---

## 5. Competitive Landscape

### 5.1 SAP Integrated Business Planning (IBP)

**What it does:** SAP IBP is a cloud-based S&OP platform that combines demand forecasting, supply planning, inventory optimization, and demand-driven replenishment (DDMRP). [^26^][^31^] It serves **1,000+ companies** globally across industries including pharmaceuticals.

**Forecasting method:** Claims **25% forecast accuracy improvement** for pharma using **Hybrid Gradient Boosting of Decision Trees (HGBDT)** and **xGBoost** for demand sensing, combined with statistical time-series models. [^28^] Also offers automated outlier correction using Isolation Forest and DBSCAN.

**Pricing/deployment:** Cloud SaaS; starter edition ~USD 30K for 3 months; enterprise pricing scales with user count and modules. [^45^] Requires SAP S/4HANA integration for full functionality.

**Gap left:** SAP IBP is designed for **large pharmaceutical manufacturers** and **hospital chains** with centralized ERP infrastructure. It does not address the **franchise-pharmacy, 380K-SKU, long-tail, VBP-shock** context of China’s OOH B2B platforms. The implementation cost and complexity are prohibitive for mid-size B2B operators.

### 5.2 IQVIA Market & Pipeline Visibility

**What it does:** IQVIA offers **Trade Distribution Data** (sales and inventory reporting with days-on-hand calculations) and **Pipeline Visibility** (downstream inventory monitoring) through its Market Visibility platform. [^49^]

**Forecasting method:** Primarily **statistical and trend-based** forecasting using proprietary pharmaceutical sales data. Focuses on **market-level demand** rather than SKU-level replenishment.

**Pricing/deployment:** Subscription-based; pricing varies by data scope and market coverage. Enterprise-focused.

**Gap left:** IQVIA provides **market intelligence**, not operational replenishment recommendations. It does not offer machine-learning-driven demand forecasting at the individual SKU-franchise level, nor does it integrate VBP policy simulation or expiry-aware replenishment.

### 5.3 Tecsys / Omnicell / TraceLink / Oracle

**Tecsys:** Pharmacy supply chain software with **demand sensing and shortage risk identification** capabilities. Focuses on **hospital pharmacy** inventory optimization and connectivity between clinical, supply chain, and financial data. [^65^]

**Omnicell:** Automated dispensing and inventory management systems for hospital and retail pharmacies. Strong in **physical automation** (robots, smart cabinets), less advanced in predictive analytics. [^63^]

**TraceLink:** Cloud-based **serialization and traceability** platform for pharmaceutical supply chains. Ensures regulatory compliance (DSCSA, etc.) but does not focus on demand forecasting. [^63^]

**Oracle Fusion Cloud (Healthcare):** Added AI-powered supply chain capabilities in 2025, focusing on inventory management and procurement automation. [^63^] General-purpose, not pharma-specific.

**Collective gap:** None of these platforms address the specific combination of **(a) 380K long-tail SKUs, (b) intermittent demand, (c) VBP policy shock simulation, (d) franchise-pharmacy network optimization, and (e) 14–30 day multi-factor forecasting** that the case requires. The demo prototype can credibly claim to fill this whitespace.

---

## 6. Bibliography

1. CI Process. (2025). Effects of China volume-based procurement on medicines. Retrieved from https://www.ciprocess.com/effects-china-volume-based-procurement-medicines.htm

2. FL Cube. (2025). China drug procurement: Centralized rules shape 11th round of VBP. Retrieved from https://flcube.com/?p=42122

3. HKEX Prospectus — Sichuan Biokin Pharmaceutical Co., Ltd. (2025). Centralized tender process and volume-based procurement.

4. Growing Science. (2026). Supply chain coordination under VBP. *International Journal of Industrial Engineering Computations*.

5. MPRA Paper 123015. Evaluating the impact of national volume-based procurement.

6. PLOS ONE. (2025). Impact of Chinese national centralized VBP policy on health costs and utilization. https://doi.org/10.1371/journal.pone.0330296

7. Pacific Bridge Medical. (2023). China announces 8th drug national volume based procurement (VBP). https://www.pacificbridgemedical.com/news-brief/china-announces-8th-national-volume-based-procurement-vbp/

8. ChemLinked. (2025). China announces results of the 10th round of VBP. https://baipharm.chemlinked.com/news/china-announces-results-of-the-10th-round-of-volume-based-drug-procurement-vbp

9. PLOS ONE. (2024). Pharmaceutical expenditure changes under VBP policy. https://doi.org/10.1371/journal.pone.0330296

10. Hyndman, R. J. (2017). Hierarchical forecasting. *Beijing Workshop on Forecasting*. https://robjhyndman.com/files/3-Hierarchical.pdf

11. Frontiers in Artificial Intelligence. (2026). Hybrid machine learning forecasting for resilient pharmaceutical supply chains. https://doi.org/10.3389/frai.2026.1803863

12. ASC Software. (2026). The complete guide to FEFO inventory management. https://ascsoftware.com/blog/fefo-inventory-management-guide/

13. MDPI Applied Sciences. (2025). A new approach to forecast intermittent demand and SKU-level optimization. https://doi.org/10.3390/app152212030

14. Microsoft Dynamics 365. (2025). Croston's method forecasting. https://learn.microsoft.com/en-us/dynamics365/supply-chain/demand-planning/croston-method

15. SAP Community. (2026). S/4HANA demand driven MRP (DDMRP) functionality. https://community.sap.com/t5/enterprise-resource-planning-blog-posts-by-members/s-4hana-demand-driven-mrp-ddmrp-functionality/ba-p/13388450

16. Team IDEA Group. (2026). Supply chain planning based on SAP IBP. https://teamideagroup.com/solutions/supply-chain-planning-based-on-sap-ibp/

17. SAP. (n.d.). Integrated business planning software for supply chain. https://www.sap.com/products/scm/integrated-business-planning.html

18. SAP Community. (2025). SAP IBP: A machine learning-driven framework. https://community.sap.com/t5/technology-blog-posts-by-members/sap-integrated-business-planning-ibp-a-machine-learning-driven-framework/ba-p/13995232

19. Fortune Business Insights. (2026). Pharmacy supply chain software market size, share [2034]. https://www.fortunebusinessinsights.com/pharmacy-supply-chain-software-market-116022

20. Pharmaceutical Commerce. (2026). AI "demand sensing" and integrated data systems drive early wins in pharmacy shortage forecasting. https://www.pharmaceuticalcommerce.com/view/ai-demand-sensing-integrated-data-systems-pharmacy-shortage-forecasting

21. JMIR. (2026). A deep learning framework for using search engine data to predict influenza-like illness. https://www.jmir.org/2025/1/e71786

22. PMC. (2024). Updated surveillance data for influenza activity. https://pmc.ncbi.nlm.nih.gov/articles/PMC11499725/

23. Nature Scientific Reports. (2026). Pharmaceutical demand forecasting via GCN-LSTM. https://doi.org/10.3389/frai.2026.1803863

24. Production and Operations Management. (2021). Demand forecasting with supply-chain information and machine learning. https://doi.org/10.1111/poms.13426

25. Neural Computing and Applications. (2023). Demand forecasting model for time-series pharmaceutical data. https://doi.org/10.1007/s00521-022-07902-5

26. Forecasting. (2024). Applying machine learning and statistical forecasting methods for enhancing pharmaceutical sales predictions. https://doi.org/10.3390/forecast6010010

27. Netstock. (2026). How to calculate safety stock using standard deviation. https://www.netstock.com/blog/safety-stock-meaning-formula-how-to-calculate/

28. Intuition Labs. (2026). Pharmacy management SaaS: Architecture & market analysis. https://intuitionlabs.ai/articles/pharmacy-management-saas-architecture-market

29. EPRA International Journal. (2024). AI in pharmaceutical supply chain management.

30. IQVIA. (2025). The global use of medicines 2025: Outlook to 2029. https://www.iqvia.com/-/media/iqvia/pdfs/events/presentation_global-meds-webinar_public.pdf

31. China Galaxy Securities Research. (2024). China healthcare — overall. VBP round results.

32. NAVLIN by EVERSANA. (2024). China unveils 10th VBP list.

33. EVERSANA. (2022). China VBP round 7 includes 58 varieties. https://www.eversana.com/zh/2022/02/17/news-alert-china-vbp-round-7-includes-58-varieties-covering-208-product-specifications/

34. ChemLinked. (2024). China launches the 10th round of VBP. https://baipharm.chemlinked.com/news/china-launches-the-10th-round-of-volume-based-drug-procurement-vbp

35. HKEX. (2025). Listed company disclosure — VBP batch history.

36. NAVLIN by EVERSANA. (2025). China 11th VBP preliminary results.

37. Chinese National Influenza Center. (2025). Chinese weekly influenza surveillance report. https://ivdc.chinacdc.cn/cnic/en/Surveillance/WeeklyReport/

38. HKEX Prospectus. (2025). OOH pharmaceutical B2B e-commerce platform business model.

39. IIETA. (2023). Machine learning approaches for pharmaceutical demand forecasting: A bibliometric review. https://www.iieta.org/journals/isi/paper/10.18280/isi.310117
