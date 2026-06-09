# Maverick-SORT Pro — 10-Minute Solo Pitch Script (v3 Final)

> **Speaker:** Junyuan (Roger) Luo
> **Format:** Solo Pitch (PPT + Live Demo)
> **Total Time:** ~10 minutes
> **Key Focus:** Problem, Live Demo (What-If, Arena, AI Copilot), AI Division of Labor, TOE Adoption, Open Question

---

## Timing Overview
* **0:00 - 1:30 | Part 1 (PPT):** The Problem & The Origin (Hook & Patent)
* **1:30 - 7:30 | Part 2 (Live Demo):** What-If Simulator -> Algorithm Arena -> HF Copilot
* **7:30 - 10:00 | Part 3 (PPT):** Building with AI, TOE Framework & Open Question

---

## The Pitch Script

### Part 1: The Problem & The Origin (PPT | 1.5 min)

*(Screen shows: First PPT slide - Li Wei's constraints & KGDRL patent)*

**[Spoken]**
"Good afternoon, everyone. I’m Roger, and today I’m presenting Maverick-SORT—an AI-driven intelligent decision-support system based on deep and reinforcement learning designed to eliminate picking errors and compliance risks in pharmaceutical logistics.

Let's start with the specific person we are building for. Meet Li Wei, a Warehouse Operations Manager at a tier-1 pharmaceutical distributor in China. Every morning at 06:30, Li Wei oversees a logistics puzzle of 90,000 daily orders and 423,000 SKUs. His binding constraints? 38% of his inventory requires strict GSP temperature compliance, and 88% must be delivered by the next day. 

If he gets his daily wave allocation wrong, his temporary workers suffer fatigue, leading to a 0.35% picking error rate. That sounds small, but it costs his company 9 Million RMB a year in returns and compliance fines. 

Anyone can build a basic routing app using open-source tools. **But what is hard to copy about Maverick is our core engine.** Our scheduling logic is powered by Knowledge-Guided Deep Reinforcement Learning (KGDRL). This is not just a theoretical concept for this class—**it is a proprietary optimization framework that has already entered the substantive examination phase for a national patent.** 

But Li Wei doesn't care about my patent. He cares about his warehouse. So, let’s leave the slides and look at the live product."

---

### Part 2: The Live Product Demo (Streamlit | 6 min)

*(Action: Use Alt+Tab to switch from PPT to the full-screen Streamlit Pro v5 browser interface)*

**[Spoken]**
"This is the Maverick Professional Dashboard. We are not aiming to replace human judgment with a black-box AI; we are giving Li Wei a decision-support system to reveal the invisible.

*(Action: Click left sidebar Smart Scheduling Engine -> switch to What-If Scenario Lab)*

**Feature 1: What-If Simulator (Value & ROI)**
The first feature is the What-If Simulator. The CFO won't pay for this software unless we prove the ROI. And Li Wei won't use it unless he trusts it. 
*(Drag a slider on the interface, e.g., Wave Capacity or Worker count)*
Here, Li Wei can simulate the future. Let’s say there's a sudden demand surge. He adjusts the capacity, and the system instantly recalculates the projected cost, SLA compliance, and worker fatigue. We price this system at 8,999 RMB per month. Under conservative estimates, this feature helps the warehouse break even by Month 5. 

*(Action: Click left sidebar Tech Showcase -> switch to Algorithm Arena)*

**Feature 2: Algorithm Arena (Academic Validation)**
But how do we know the underlying AI is actually better? We built the Algorithm Arena to validate our assumptions using simulated pharma data. 
*(Point to the data in the charts)*
Here, we pit our KGDRL algorithm against traditional heuristics like FCFS. Our ablation studies reveal a harsh truth: A standard 'Vanilla PPO' RL model might give you the highest theoretical reward, but it causes 4.4 deadline misses per episode. In the pharma cold chain, one miss can ruin a batch of vaccines. Our KGDRL sacrifices raw distance metrics to guarantee **zero deadline misses** and strict temperature compliance. 

*(Action: Open the Maverick Copilot chat box on the sidebar or main interface)*

**Feature 3: Hugging Face AI Copilot (Where we use GenAI)**
Now, looking at these complex Pareto frontiers, a warehouse manager might get overwhelmed. This is where we leverage Generative AI. We deeply integrated Hugging Face's Qwen2.5 LLM into the platform. 

*(Type or click a preset question, e.g., "Explain why KGDRL is safer than PPO today")*
Instead of a generic chatbot, this is an **AI Insight Engine**. It reads the live metrics on the screen and translates them into plain business English. 

**And here is what happens when the AI gets it wrong or breaks:** We know cloud APIs fail. If this Hugging Face API times out, our system does not crash. It automatically falls back to a locally hosted quantized model, and if that fails, it drops to pre-written heuristic rules. We never let the AI act autonomously—human override is mandatory because legal compliance always rests with the manager, not the vendor."

---

### Part 3: Building with AI & Honest Reflection (PPT | 2.5 min)

*(Action: Switch back to PPT)*

**[Spoken]**
"To build this in just a few weeks, I had to divide the labor between AI and human judgment. 

**How we built it with AI:** I handed the execution to Claude. It generated over 2,900 lines of Python and CSS, built the simulator framework, and handled the LLM API integration.
**Where human judgment did the real work:** Claude doesn't know pharmaceutical GSP laws. I had to manually design the MDP state space and dictate that a cold-chain violation penalty must be 100 times heavier than a distance penalty (alpha-temp = 100). The AI wrote the code, but I decided what code was worth writing.

**Adoption & The TOE Framework:**
Looking at adoption through the TOE framework: The Technology is resolved (KGDRL works end-to-end), and the Environment is a catalyst (GSP fines force digitalization). **Our binding constraint is Organizational.** Temporary warehouse workers have extremely high turnover. The main obstacle to adoption isn't the algorithm—it's whether a temp worker can follow complex AI routing on their handheld scanner without three days of training.

*(Switch to the final PPT slide: The Open Question)*

**The Open Question:**
Which brings me to my final open question, especially for our guests from Moonshot and Kimi. 

Our entire product assumes that warehouse managers want to *see* the algorithm's reasoning and play with 'What-If' scenarios to build trust. But I am not sure if that is entirely true. 
**My question is:** In your experience with B2B enterprise adoption, do operational managers actually value this level of transparency and scenario-testing, or do they ultimately just want a simple 'Print Optimal Schedule' button and an API integration certificate?

Thank you. I'm ready for your questions."