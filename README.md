# Composio App Research — Agent Toolkit Feasibility Audit

Research pipeline that evaluates 100 apps across 10 categories for agent-toolkit
buildability: auth method, self-serve vs gated access, API surface, and a
buildability verdict with evidence.

**Live case study:** https://composio-app-research-wine.vercel.app/

## What's in this repo

data/apps_list.json          - the 100 apps, categorized
schema/app_schema.json       - the JSON shape every researched app follows
agent/research_agent.py      - main research agent (Groq + openai/gpt-oss-20b)
agent/resume_research.py     - retries only failed apps from a previous run
agent/verify_agent.py        - automated link-checker for cited evidence URLs
analysis/classify_verification.py  - flags apps by verification risk
analysis/fix_categories.py   - backfills category field onto results
analysis/patterns.py         - computes headline patterns from results
output/                      - all pipeline outputs
docs/index.html              - the deployed case study page

## How to run it

1. Install dependencies
   python -m venv venv
   venv\Scripts\Activate.ps1
   pip install groq python-dotenv requests

2. Set your API key - create a .env file in the root:
   GROQ_API_KEY=your_key_here
   Get a free key at https://console.groq.com - no billing required.

3. Run the research agent (all 100 apps):
   python agent/research_agent.py
   Output: output/results_v1_groq.json

4. Retry any failures:
   python agent/resume_research.py

5. Backfill categories, then run pattern analysis:
   python analysis/fix_categories.py
   python analysis/patterns.py
   Output: output/pattern_summary.json

6. Run the automated link-verification pass:
   python agent/verify_agent.py
   python analysis/classify_verification.py
   Output: output/link_check_report.json

7. Human verification - manually check flagged high-risk apps against real
   docs. Results logged in output/human_verification.json.

## Design decisions worth knowing

- Access model uses 5 buckets, not a self-serve/gated binary - added after
  finding apps like Salesforce that are free for a dev trial but paid in
  production.
- No paid API tiers were used anywhere in this pipeline - the agent runs on
  Groq's free tier (openai/gpt-oss-20b), without live web search, by design.
- Verification is two-layered: an automated HTTP check on every cited
  evidence URL, followed by a targeted human check on the highest-risk apps.

## Known limitations

- Evidence URLs are drawn from model knowledge, not live search - roughly a
  third of cited URLs across the 100 apps did not resolve on direct HTTP check.
- 2 of 100 apps (iPayX, NotebookLM) hit hard pipeline errors on first pass
  and required a manual retry.
- The 10-app human-verification sample is prioritized by risk, not randomly
  sampled.
