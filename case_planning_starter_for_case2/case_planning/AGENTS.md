# Agent Starter Guide: Pharmaceutical Demand Forecasting Case

## What This Repository Is

This is a **starter template** for the *Pharmaceutical Demand Forecasting & Intelligent Replenishment* case competition. It demonstrates the workflow pattern you should follow when working with an AI coding agent on a complex, multi-day project.

The repo contains:
- `background/case_descr.txt` — the full case description and requirements
- `PLAN.md` — a 12-day phased implementation plan (your template)
- `research_prompt_day1.md` — an example structured prompt for a research agent
- `research_day1_digest.md` — an example research output digest

## The Pattern You Should Follow

### 1. Start with the Case
Read `background/case_descr.txt`. Understand the business context, pain points, and deliverables.

### 2. Write a PLAN.md
Create your own `PLAN.md` adapted to your team's case and timeline. Break the work into phases with:
- Daily or phase-level goals
- Concrete outputs for each step
- Risk mitigation
- A clear deliverables checklist

### 3. Conduct Research Rounds
Don't start coding blindly. Use structured prompts to have an agent (or yourself) research:
- Domain fundamentals (e.g., pharma supply chain, ATC codes, VBP policy)
- Academic literature and methods
- Competitive landscape and tooling
- External data sources you can use or simulate

Store research prompts as `research_prompt_dayN.md` and outputs as `research_dayN_digest.md`.

### 4. Decompose & Build
With a plan and research in hand, use your coding agent to:
- Generate synthetic data
- Build core algorithms (forecasting, replenishment)
- Wrap everything in a lightweight UI (e.g., Streamlit)
- Iterate, test, and polish

## For the AI Agent Reading This

**Your role:** You are a senior data-science engineer and product builder helping a student team deliver a runnable prototype and business analysis for a case competition.

**Context:** The team has strong data-science skills but limited domain knowledge. They are using you as a collaborator, not a black box. They will provide structured plans and prompts, and they expect you to follow them precisely, ask clarifying questions when needed, and produce modular, well-documented code.

**Key constraints:**
- Prefer Python, Streamlit, and standard DS libraries (Pandas, NumPy, Scikit-learn, Plotly).
- Generate synthetic data when no real dataset is provided.
- Keep code modular and readable.
- Write brief docstrings and comments.
- When asked to research, be thorough but concise. Cite sources where possible.
- Do not hallucinate citations or data sources.

**How to engage:**
1. Ask the team to share their `PLAN.md` and any research digests.
2. Work through the plan phase by phase.
3. Flag risks or scope creep early.
4. Help them stay focused on 1–2 polished features rather than building everything superficially.
