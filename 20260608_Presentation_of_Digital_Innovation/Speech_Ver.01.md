# Maverick-SORT Pro — 10-Minute Solo Pitch Script (v3 Final)

> **Speaker:** Junyuan (Roger) Luo[cite: 4]
> **Format:** Solo Pitch (PPT + Live Demo)[cite: 1]
> **Total Time:** ~10 minutes[cite: 1, 4]
> **Key Focus:** Problem, Live Demo (What-If, Arena, AI Copilot), AI Division of Labor, TOE Adoption, Open Question[cite: 1, 4]

---

## 📊 Timing Overview
* **0:00 - 1:30 | Part 1 (PPT):** The Problem & The Origin (Hook & Patent)[cite: 4]
* **1:30 - 7:30 | Part 2 (Live Demo):** What-If Simulator -> Algorithm Arena -> HF Copilot[cite: 4]
* **7:30 - 10:00 | Part 3 (PPT):** Building with AI, TOE Framework & Open Question[cite: 1, 4]

---

## 🎙️ The Pitch Script

### Part 1: The Problem & The Origin (PPT | 1.5 min)

*(Screen shows: First PPT slide - Li Wei's constraints & KGDRL patent)*[cite: 4]

**[Spoken]**
"Good afternoon, everyone. I’m Roger, and today I’m presenting Maverick-SORT. 

Let's start with the specific person we are building for. Meet Li Wei, a Warehouse Operations Manager at a tier-1 pharmaceutical distributor in China[cite: 4]. Every morning at 06:30, Li Wei oversees a logistics puzzle of 90,000 daily orders and 423,000 SKUs[cite: 4]. His binding constraints? 38% of his inventory requires strict GSP temperature compliance, and 88% must be delivered by the next day[cite: 4]. 

If he gets his daily wave allocation wrong, his temporary workers suffer fatigue, leading to a 0.35% picking error rate[cite: 4]. That sounds small, but it costs his company 9 Million RMB a year in returns and compliance fines[cite: 4]. 

Anyone can build a basic routing app using open-source tools[cite: 4]. **But what is hard to copy about Maverick is our core engine.**[cite: 1, 4] Our scheduling logic is powered by Knowledge-Guided Deep Reinforcement Learning (KGDRL)[cite: 4]. This is not just a theoretical concept for this class—**it is a proprietary optimization framework that has already entered the substantive examination phase for a national patent.**[cite: 4] 

But Li Wei doesn't care about my patent. He cares about his warehouse. So, let’s leave the slides and look at the live product."[cite: 4]

---

### Part 2: The Live Product Demo (Streamlit | 6 min)

*(⚠️ Action: Use `Alt+Tab` to switch from PPT to the full-screen Streamlit Pro v5 browser interface)*[cite: 4]

**[Spoken]**
"This is the Maverick Professional Dashboard[cite: 4]. We are not aiming to replace human judgment with a black-box AI; we are giving Li Wei a decision-support system to reveal the invisible[cite: 4].

*(⚠️ Action: Click left sidebar `Smart Scheduling Engine` -> switch to `What-If Scenario Lab`)*[cite: 2, 4]

**Feature 1: What-If Simulator (Value & ROI)**
The first feature is the What-If Simulator[cite: 4]. The CFO won't pay for this software unless we prove the ROI. And Li Wei won't use it unless he trusts it[cite: 4]. 
*(Drag a slider on the interface, e.g., Wave Capacity or Worker count)*[cite: 4]
Here, Li Wei can simulate the future[cite: 4]. Let’s say there's a sudden demand surge[cite: 4]. He adjusts the capacity, and the system instantly recalculates the projected cost, SLA compliance, and worker fatigue[cite: 4]. We price this system at 8,999 RMB per month[cite: 4]. Under conservative estimates, this feature helps the warehouse break even by Month 5[cite: 4]. 

*(⚠️ Action: Click left sidebar `Tech Showcase` -> switch to `Algorithm Arena`)*[cite: 2, 4]

**Feature 2: Algorithm Arena (Academic Validation)**
But how do we know the underlying AI is actually better? We built the Algorithm Arena to validate our assumptions using simulated pharma data[cite: 4]. 
*(Point to the data in the charts)*[cite: 4]
Here, we pit our KGDRL algorithm against traditional heuristics like FCFS[cite: 4]. Our ablation studies reveal a harsh truth: A standard 'Vanilla PPO' RL model might give you the highest theoretical reward, but it causes 4.4 deadline misses per episode[cite: 4]. In the pharma cold chain, one miss can ruin a batch of vaccines[cite: 4]. Our KGDRL sacrifices raw distance metrics to guarantee **zero deadline misses** and strict temperature compliance[cite: 4]. 

*(⚠️ Action: Open the `🤖 Maverick Copilot` chat box on the sidebar or main interface)*[cite: 2, 4]

**Feature 3: Hugging Face AI Copilot (Where we use GenAI)**
Now, looking at these complex Pareto frontiers, a warehouse manager might get overwhelmed[cite: 4]. This is where we leverage Generative AI. We deeply integrated Hugging Face's Qwen2.5 LLM into the platform[cite: 2]. 

*(Type or click a preset question, e.g., "Explain why KGDRL is safer than PPO today")*[cite: 4]
Instead of a generic chatbot, this is an **AI Insight Engine**[cite: 2]. It reads the live metrics on the screen and translates them into plain business English[cite: 4]. 

**And here is what happens when the AI gets it wrong or breaks:**[cite: 1] We know cloud APIs fail. If this Hugging Face API times out, our system does not crash[cite: 4]. It automatically falls back to a locally hosted quantized model, and if that fails, it drops to pre-written heuristic rules[cite: 4]. We never let the AI act autonomously—human override is mandatory because legal compliance always rests with the manager, not the vendor."[cite: 4]

---

### Part 3: Building with AI & Honest Reflection (PPT | 2.5 min)

*(⚠️ Action: Switch back to PPT)*[cite: 4]

**[Spoken]**
"To build this in just a few weeks, I had to divide the labor between AI and human judgment[cite: 4]. 

**How we built it with AI:** I handed the execution to Claude[cite: 4]. It generated over 2,900 lines of Python and CSS, built the simulator framework, and handled the LLM API integration[cite: 4].
**Where human judgment did the real work:** Claude doesn't know pharmaceutical GSP laws[cite: 4]. I had to manually design the MDP state space and dictate that a cold-chain violation penalty must be 100 times heavier than a distance penalty (alpha-temp = 100)[cite: 4]. The AI wrote the code, but I decided what code was worth writing[cite: 4].

**Adoption & The TOE Framework:**[cite: 1]
Looking at adoption through the TOE framework: The Technology is resolved (KGDRL works end-to-end), and the Environment is a catalyst (GSP fines force digitalization)[cite: 4]. **Our binding constraint is Organizational.**[cite: 4] Temporary warehouse workers have extremely high turnover[cite: 4]. The main obstacle to adoption isn't the algorithm—it's whether a temp worker can follow complex AI routing on their handheld scanner without three days of training[cite: 4].

*(Switch to the final PPT slide: The Open Question)*[cite: 4]

**The Open Question:**[cite: 1]
Which brings me to my final open question, especially for our guests from Moonshot and Kimi[cite: 1, 4]. 

Our entire product assumes that warehouse managers want to *see* the algorithm's reasoning and play with 'What-If' scenarios to build trust[cite: 4]. But I am not sure if that is entirely true[cite: 4]. 
**My question is:** In your experience with B2B enterprise adoption, do operational managers actually value this level of transparency and scenario-testing, or do they ultimately just want a simple 'Print Optimal Schedule' button and an API integration certificate?[cite: 4]

Thank you. I'm ready for your questions."[cite: 4]