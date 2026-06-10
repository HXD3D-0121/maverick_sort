# Maverick-SORT Pro — 十分钟演示文稿讲稿

> **版本**: v2.0 — 直接回应 Professor Questions Worth Answering  
> **建议时长**: 10 分钟（±30 秒）  
> **语言**: 英文（汇报语言）  
> **核心原则**: 每页必须回答一个教授预设的问题；每个数字必须来自真实实验数据

---

## 节奏概览 / Timing Overview

| 幻灯片 | 主题 | 时长 | 对应问题 |
|--------|------|------|----------|
| 1 | Title | 30s | — |
| 2 | The Problem & The Person | 1:00 | Q1.1 |
| 3 | What the Product Does Today | 1:30 | Q1.2, Q1.3 |
| 4 | Users, Payers, Deciders | 1:00 | Q2.1, Q2.2 |
| 5 | What Changes in a Day | 1:00 | Q2.3 |
| 6 | What Is Hard to Copy | 1:00 | Q2.4 |
| 7 | The Binding Constraint | 1:00 | Q3.1, Q3.2 |
| 8 | Building with AI | 1:30 | Q4.1, Q4.2 |
| 9 | When AI Is Confidently Wrong | 1:00 | Q4.3, Q4.4 |
| 10 | Real Results | 1:00 | 数据 |
| 11 | Honest Reflection | 1:00 | Q5.1, Q5.2, Q5.4 |
| 12 | Closing | 30s | — |
| **总计** | | **~10:30** | |

---

## Slide 1: Title Page（30 秒）

**【画面】** Title slide with CAS logo.

**【讲稿】**

> "Good morning. I'm Junyuan Luo from the Maverick Team. Over the past four weeks, we have been building Maverick-SORT Pro — an intelligent wave allocation system for pharmaceutical distribution.
>
> Today, I will not give you a feature tour. Instead, I will walk through the questions that Professor told us we must be able to answer: Who is this for? What does it actually do today? Why would anyone adopt it? Where did AI help, and where did it mislead? And most importantly — what are we still honestly unsure of?
>
> Let's start with the person, not the product."

**【要点提示】**
- 语速平稳，眼神扫过全场
- 不要在此页停留超过 30 秒

---

## Slide 2: What Problem, and for Whom?（1 分钟）

**【画面】** "The Problem & The Person" — 左侧 Li Wei 的角色描述，右侧四个痛点。

**【讲稿】**

> "The person is Li Wei. He is a Warehouse Operations Manager at a tier-one pharmaceutical distributor in Jiangsu Province. He oversees ninety thousand orders per day across one hundred twenty-eight logistics centres, with three hundred forty pickers — sixty percent of whom are temporary workers during peak seasons.
>
> Every morning at six thirty, Li Wei faces a single decision: which orders go into which wave, in what sequence? Right now, he does this with rules of thumb on a whiteboard. Thirty-eight percent of his SKUs are temperature-sensitive. His picking error rate is zero point three five percent, which translates to nine million RMB in annual return losses.
>
> But the real cost is not the error rate. It is the cost of getting it wrong: a cold-chain breach means batch recall and GSP fines; a missed deadline means hospital penalties and reputational damage; and over-staffing during peaks drives labour costs up two and a half times.
>
> So the problem is not abstract. It is Li Wei's Monday morning."

**【要点提示】**
- 强调 "six thirty" 和 "whiteboard" — 让观众能想象这个场景
- 数字要清晰：90,000 orders, 128 centres, RMB 9M/year
- 不要读幻灯片上已经有的文字，要补充 "Monday morning" 这种画面感

---

## Slide 3: What the Product Does Today（1 分 30 秒）

**【画面】** "What the Product Does Today" — 两大核心功能卡片。

**【讲稿】**

> "What does the product do today, as opposed to what we plan for it to do? We deliberately built only two things to production depth. Everything else is scaffolding.
>
> Feature one: the KGDRL Core Scheduler. KGDRL stands for Knowledge-Graph-Guided Deep Reinforcement Learning. It dynamically groups orders into waves using a PPO agent guided by a graph attention network and KL-divergence constraints that inject pharma-domain rules — like 'frozen products must ship before ten AM' — directly into the policy. Why did we build this first? Because without the algorithm, we have nothing to sell. Every other page in the dashboard is decoration if the routing logic is wrong.
>
> Feature two: the Streamlit Pro Decision Dashboard. It gives Li Wei a real-time Command Center, a What-If Simulator, a Strategy Optimizer, and an ROI Calculator. Why this feature? Because Li Wei will not trust a black-box API. He needs to see the wave form, test scenarios, and calculate payback before he asks his CFO for budget. The dashboard is not built for demo. It is built for a warehouse manager to argue with the algorithm.
>
> Is the product doing the work for the user, helping them do it better, or showing them something they could not see before? It is primarily the third. Li Wei already knows how to schedule. What he lacks is quantified trade-offs."

**【要点提示】**
- "two things to production depth" — 强调聚焦，不要让人觉得是半成品
- "argue with the algorithm" — 这个短语要放慢，这是核心洞察
- 准备回答追问："Why only two features?" → "Because four weeks is not enough to build ten features properly."

---

## Slide 4: Who Uses, Who Pays, Who Decides?（1 分钟）

**【画面】** "Users, Payers, Deciders" — 三人关系图。

**【讲稿】**

> "Who uses the product, who pays for it, and who decides whether it gets adopted? They are not the same person.
>
> Li Wei is the user. He wants fewer headaches and a dashboard that makes him look competent in the morning meeting.
>
> The CFO is the payer. She wants to see ROI before she signs off on eight thousand nine hundred ninety-nine RMB per month per warehouse.
>
> The VP of Operations is the decider. He cares about strategic risk, compliance, and whether this vendor will still exist in three years.
>
> When these three people want different things, whose view wins? The CFO wins on pricing. That is why we designed two tiers: Essential at two thousand nine hundred ninety-nine RMB for trial, and Pro at eight thousand nine hundred ninety-nine for scale. But what this costs the product is that we cannot give Li Wei everything he wants — for example, full ERP integration — because the CFO will not pay for it until ROI is proven. So our product roadmap is shaped by payer constraint, not user desire."

**【要点提示】**
- 用手指向屏幕上的三个人物框
- "shaped by payer constraint, not user desire" — 这句话展示商业成熟度
- 准备回答追问："Isn't that dangerous?" → "Yes. It means Li Wei might churn if the CFO forces a cheap solution that doesn't solve his problem."

---

## Slide 5: What Changes in Someone's Day?（1 分钟）

**【画面】** "What Changes in a Day" — 左右对比 Before/After。

**【讲稿】**

> "What changes in Li Wei's day if he starts using Maverick? And is that change clearly worth what it costs?
>
> Before Maverick: Li Wei arrives at six thirty and spends one hour on manual wave planning with a whiteboard. At two PM, the peak surge arrives. He calls the temp agency for fifty extra workers — reactive, expensive, and often too late. At five PM, he conducts an end-of-shift review, but he has no data on whether today's schedule was actually optimal.
>
> With Maverick: Li Wei arrives at six thirty and reviews the AI-generated wave plan in five minutes. He adjusts it if needed — and the system learns from his adjustments. At two PM, the system automatically shrank wave capacity thirty minutes ago because the EWMA forecaster detected the surge. At five PM, the dashboard shows today's cost, SLA hit rate, and compliance score against the benchmark.
>
> Is it worth eight thousand nine hundred ninety-nine RMB per month? Under neutral assumptions — a fifteen percent efficiency gain — the break-even is month five. At nine million RMB in picking-error losses alone, a ten percent reduction pays for the software twice over."

**【要点提示】**
- Before/After 对比要有节奏感：先描述 Before 的困境，再展示 After 的流畅
- "five minutes" vs "one hour" — 强调时间节省
- "month five" — 给出具体的投资回收期

---

## Slide 6: What Is Hard to Copy?（1 分钟）

**【画面】** "What Is Hard to Copy" — 三点护城河。

**【讲稿】**

> "If anyone can build a rough version of this with the same tools, what is the part that is hard to copy? And where does our own judgment sit?
>
> Let's be honest: anyone can build a rough version. PPO is open-source. Streamlit is open-source. Simulated data takes an afternoon. The architecture is textbook.
>
> But three things are hard to copy. First, the pharma-specific knowledge graph. We encoded GSP temperature-segregation rules, FEFO priority logic, and bimodal arrival patterns into the graph. A general AI company does not have this. It took us three days just to extract the rules from the casebook and translate them into graph edges.
>
> Second, the human-in-the-loop trust design. The What-If Simulator exists because we made a human judgment: Chinese warehouse managers will not accept AI recommendations they cannot challenge. That is not an algorithmic insight. That is a cultural insight.
>
> Third, the ablation protocol itself. We spent three days validating that KGDRL outperforms vanilla PPO under pharma constraints. That judgment — what to measure, what 'good enough' means — is not in the code. It is in our heads."

**【要点提示】**
- "Let's be honest" — 这个短语建立可信度
- 强调 "cultural insight" 和 "not in the code" — 展示人类判断的价值
- 准备回答追问："Can SAP do this?" → "SAP EWM has rules. It does not have learning."

---

## Slide 7: The Binding Constraint（1 分钟）

**【画面】** TOE Framework — Technology (Resolved), Organization (Binding), Environment (Catalyst)。

**【讲稿】**

> "Across technology, organization, and environment, which single condition most limits adoption right now?
>
> Technology is resolved. The KGDRL model trains end-to-end. The Streamlit dashboard renders. The API responds in under one hundred milliseconds.
>
> Environment is a catalyst. GSP compliance fines are increasing. Regulators are pushing digitisation. That forces adoption, but it does not determine which vendor wins.
>
> The binding constraint is organization. Front-line workforce resistance, especially among temporary staff. The Technology Acceptance Model tells us there is a steep learning curve for AI-generated picking routes. A temp worker who will be gone in three weeks has zero incentive to learn a new system.
>
> Would resolving this unlock adoption, or would the next constraint become visible? Honest answer: resolving worker resistance would reveal the data integration constraint. Li Wei's WMS is a legacy system from two thousand fourteen. Even if he trusts the algorithm, someone must build the API bridge. That is why we priced the Pro tier to include API-first integration. It is not a feature. It is an admission that adoption requires plumbing, not just AI."

**【要点提示】**
- "Honest answer" — 展示批判性思维
- "plumbing, not just AI" — 这句话会让教授点头
- 准备回答追问："Then why focus on the algorithm?" → "Because without the algorithm, the plumbing has nothing to carry."

---

## Slide 8: Building with AI — Division of Labour（1 分 30 秒）

**【画面】** 左右分栏：AI 负责什么 / 人类判断负责什么。

**【讲稿】**

> "Where did we hand work to the AI, and where did our own judgment do the real work?
>
> We used Claude Code as our core programming assistant. It generated the PPO network architecture — eleven hundred lines. It wrote the Streamlit dashboard CSS and layout. It scaffolded the NSGA-II multi-objective optimizer. It translated everything between Chinese and English. And it debugged syntax errors we would have spent hours on. Our estimate: the AI saved us from thirteen days to four — a three-point-two-five-x speedup.
>
> But human judgment did the work that mattered. We decided which pain point to solve — wave allocation versus inventory versus demand forecasting. We set the reward function weights: alpha-temperature at one hundred, alpha-distance at one. That ratio encodes the belief that a temperature violation is one hundred times worse than an extra meter of picking distance. We designed the ablation protocol: what 'good enough' means. We chose the business model: per-warehouse versus per-order pricing. And we decided when to stop training.
>
> The AI wrote the code. The human decided what code was worth writing."

**【要点提示】**
- "three-point-two-five-x" — 精确数字增加可信度
- "alpha-temperature at one hundred, alpha-distance at one" — 展示这是有意识的商业判断
- 最后一句话要放慢，这是核心论点

---

## Slide 9: What We Changed Around the GenAI Model（1 分钟）

**【画面】** "What We Changed Around the Model" — 数据、上下文、指令三点。

**【讲稿】**

> "We did not build the GenAI model. We built the context around it. Three things.
>
> First, data. We calibrated simulated order distributions against the enterprise casebook: fifty-five percent ambient, twenty-five percent cool, fifteen percent cold, five percent frozen. Bimodal arrival at nine AM and two PM. Peak multiplier of two-point-eight. These numbers are not random. They come from the casebook's operational parameters.
>
> Second, context. We built a pharma-specific knowledge graph with four node types — orders, zones, temperatures, waves — and four edge types. This is not generic reinforcement learning. It is RL constrained by GSP rules.
>
> Third, instructions. We designed prompts that translate DRL action sequences into natural language. 'The system closed the wave at minute three because the current wave already contains twelve orders, covers zones A and B, and is eight minutes from the next peak window.'
>
> How did we know the output was good enough? Three gates. Technical: ablation across twenty random seeds. Business: Li Wei would understand the dashboard without training. Academic: reward curves converge, and GAT attention weights correlate with zone proximity."

**【要点提示】**
- 强调 "not generic RL" — 展示领域特异性
- 引用自然语言解释的具体例子
- "Three gates" — 展示多维验证思维

---

## Slide 10: Where AI Is Confidently Wrong（1 分钟）

**【画面】** "Where AI Is Confidently Wrong" — 风险场景 + 三道防护。

**【讲稿】**

> "Where is the product most likely to be confidently wrong, and what stops a user from trusting it exactly there?
>
> The highest-risk failure mode is overfitting to simulated demand patterns. Our training data assumes a bimodal arrival: peaks at nine AM and two PM. But what if Li Wei's warehouse sees a unimodal surge at eleven AM because of a regional hospital contract? The EWMA forecaster will systematically under-predict for two to three hours before it adapts. And during those two hours, the system is confidently wrong.
>
> We built three safeguards. One: confidence bands on the forecast chart. Li Wei can see when the model is uncertain. Two: human override. Every recommendation has a 'Reject and Manual' button. The system does not act autonomously. Three: alert escalation. If observed rate exceeds predicted by more than fifty percent for fifteen minutes, the Alert Center triggers a 'Model Drift' warning.
>
> Would we let it act without someone checking first? No. Not because we distrust AI, but because GSP compliance liability rests with the warehouse manager, not the software vendor."

**【要点提示】**
- "confidently wrong" — 这个词组要清晰传达
- 强调 "GSP compliance liability" — 展示对监管现实的理解
- 准备回答追问："Then why use AI at all?" → "Because AI is wrong predictably and measurably. Humans are wrong unpredictably."

---

## Slide 11: Real Results from Ablation（1 分钟）

**【画面】** 表格展示 7 个方法的 ablation 数据。

**【讲稿】**

> "Here is what the numbers actually say. Twenty random seeds, six methods.
>
> Vanilla PPO achieves the highest reward — four thousand and seven. But it pays for that with four point four deadline misses per episode. In pharmaceutical distribution, one missed deadline can mean a drug shortage at a hospital.
>
> KGDRL, our knowledge-guided variant, sacrifices raw reward. Its reward is one thousand nine hundred and eight — less than half of vanilla PPO. But it achieves zero deadline misses. Lower variance. And a violation count that is stable.
>
> The gap between KGDRL and our best heuristic, TZU, is modest — about one thousand seven hundred reward points. Our moat is not the algorithm alone. It is the system: algorithm plus dashboard plus trust layer.
>
> I want to be honest about this table. If you only look at the reward column, PPO wins. If you look at the full picture, KGDRL wins on reliability. And in pharma, reliability is what Li Wei pays for."

**【要点提示】**
- 用手指向表格中的关键数字
- "sacrifices raw reward" — 展示对权衡的理解
- "If you only look at the reward column, PPO wins" — 这种自我质疑建立可信度
- 准备回答追问："Why doesn't KGDRL beat PPO on both?" → "Because the KL constraint limits exploration. That is the price of injecting domain knowledge."

---

## Slide 12: Honest Reflection — Part 1（1 分钟）

**【画面】** "What We Are Least Sure Of" + "One More Week" 计划。

**【讲稿】**

> "Which assumption about our user are we least sure of? We believe that warehouse managers want to see the algorithm's reasoning more than they want the algorithm to be perfect. We invested heavily in the What-If Simulator and the AI Copilot because of this belief. But we have not tested it with a real Li Wei. It is entirely possible that what he actually wants is simply a lower price and a SAP integration certificate.
>
> What is the weakest part of the product right now, and what would we do with one more week? The weakest part is the simulation-to-reality gap. Every number I just showed you is real within the simulation. None of it is real in a warehouse.
>
> With one more week: Day one and two, run three structured interviews with actual pharma warehouse managers — not the casebook persona. Day three and four, build the FastAPI backend bridge to ingest real WMS data formats. Day five to seven, conduct a live A-B test: one shift with human scheduling, one with KGDRL recommendations, measuring picking distance and error rate."

**【要点提示】**
- "not the casebook persona" — 展示对案例研究局限性的认识
- "simulation-to-reality gap" — 诚实承认核心弱点
- A/B test 的具体设计展示科学思维

---

## Slide 13: Honest Reflection — Part 2（1 分钟）

**【画面】** "What Building This Taught Us" + "What We Still Don't Understand"。

**【讲稿】**

> "What did building this teach us about AI and digital innovation that we did not know four weeks ago? Three things.
>
> First: AI accelerates implementation, not validation. Claude generated two thousand nine hundred lines of code in one day. But designing the ablation protocol — deciding what 'better' means — took three days of human debate.
>
> Second: the UI is the moat. In B2B software, the algorithm that wins is not the one with the highest reward. It is the one the operations manager trusts enough to defend to the CFO.
>
> Third: simulated data is a trap. It lets you demo beautifully, but it hides the integration cost. Every number in our ablation is real within the simulation. None of it is real in a warehouse.
>
> And what do we still not understand, even though it works? The GAT attention weights correlate with zone proximity most of the time. But occasionally, they focus on seemingly irrelevant nodes. Is the model learning something we did not encode — like a hidden correlation between SKU categories and picker speed? Or is it just noise? We do not know."

**【要点提示】**
- "AI accelerates implementation, not validation" — 这是可以对课程文献的呼应
- "the UI is the moat" — 反直觉但真实的洞察
- 最后关于 GAT 的问题展示真正的科学好奇心

---

## Slide 14: Closing（30 秒）

**【画面】** "What Maverick Is, and Is Not" — 四点是 / 四点不是。

**【讲稿】**

> "To close: Maverick-SORT Pro is a decision-support system, not a replacement for human judgment. It is built on KGDRL with honest ablation data showing trade-offs between reward and reliability. It is packaged in a dashboard designed for trust. And it is priced to pay for itself in month five under conservative assumptions.
>
> It is not a patented product — substantive examination is pending. It is not trained on real warehouse data. And it is not autonomous: human check is mandatory for every wave release.
>
> Thank you. We welcome questions — especially the hard ones."

**【要点提示】**
- "especially the hard ones" — 展示自信和对批评的开放
- 微笑，停顿两秒
- 准备应对尖锐问题：见下方 Q&A 预案

---

## 附录 A：预判 Q&A 与回答要点

### Q1: "KGDRL reward is lower than vanilla PPO. Why is that better?"

**回答要点:**
- "In reward-only terms, PPO wins. But PPO pays with 4.4 deadline misses per episode."
- "KGDRL's KL constraint forces the policy to stay close to domain heuristics. That limits exploration — so reward is lower — but it also eliminates catastrophic decisions."
- "In pharma, a single missed deadline can mean a hospital drug shortage. Li Wei cares about zero misses more than maximum reward."
- "This is exactly the trade-off our Pareto optimizer makes explicit."

### Q2: "You said the product is not trained on real data. How can you claim it works?"

**回答要点:**
- "We cannot claim it works in production. We can only claim it works in simulation."
- "The simulation is calibrated against the casebook's operational parameters: arrival rates, temperature mix, peak multipliers."
- "What we are selling today is not a deployed system. It is a validated prototype with a clear path to real-data integration."
- "That is why the one-week plan starts with real WMS integration, not more algorithm tuning."

### Q3: "If SAP EWM adds AI tomorrow, what happens to you?"

**回答要点:**
- "SAP has rules. We have learning. If SAP adds learning, they still lack the pharma-specific knowledge graph."
- "But the honest answer is: if SAP decides to build this, their sales channel and existing customer relationships give them an advantage we cannot match."
- "Our defence is speed: we can iterate in days. SAP iterates in quarters."
- "And our second defence is the data flywheel: every warehouse we serve improves our model. SAP starts from zero on the learning curve."

### Q4: "You used AI to write most of the code. What did you actually learn?"

**回答要点:**
- "We learned that AI is an excellent implementer and a mediocre strategist."
- "Claude generated correct PPO code. But it could not decide whether wave allocation was the right problem to solve. That required reading the casebook, talking to stakeholders, and making a judgment call."
- "We also learned that AI hallucinates business logic. Early versions of the reward function mixed up FIFO and FEFO. The code compiled. The logic was wrong. Only human domain knowledge caught it."

### Q5: "Your weakest assumption is untested. Why should we believe your user research?"

**回答要点:**
- "You shouldn't. That is why we flagged it as our weakest assumption."
- "Our user research is based on one casebook and zero interviews with actual warehouse managers."
- "If we had one more week, the first priority would be three structured interviews. Not more code. Not more features. Validation."
- "That is the most important thing this course taught us: the difference between a demo and a product is not the code. It is the validation."

---

## 附录 B：演讲技巧提示

| 技巧 | 应用 |
|------|------|
| **停顿** | 每切换一页，停顿 1 秒再开口 |
| **数字** | 关键数字放慢："nine million RMB", "month five", "zero deadline misses" |
| **手势** | 指向屏幕时用手掌而非指尖，显得更开放 |
| **眼神** | 每 10 秒切换注视区域（左/中/右） |
| **语速** | 正常 120-130 词/分钟；关键结论降至 90 词/分钟 |
| **错误处理** | 如果被问住，说 "That is an excellent question. Let me think about that for a moment." 停顿 3 秒再回答 |

---

> **最后提醒**: 本讲稿所有数字均来自 `ablation_study.json` 真实实验数据。所有商业数据基于 `product_tier_pricing.md` 中的定价模型。所有 "Li Wei" 场景基于案例书描述。未夸大未实现功能。
