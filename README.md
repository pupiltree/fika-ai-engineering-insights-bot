<<<<<<< HEAD
# 🤖 FIKA AI — Engineering Productivity Insights Bot

FIKA AI is an AI-powered **engineering productivity insights dashboard and Slack bot** that analyzes GitHub activity to surface meaningful developer metrics. It helps engineering teams gain visibility into commits, pull requests, churn, cycle times, and review relationships through a beautifully visualized dashboard and Slack integration.

---

## 📌 Key Features

### ✅ **1. Developer Dashboard (Streamlit)**
- Displays **commit stats**, **pull request summaries**, and **forecast trends**.
- Auto-generates:
  - 📈 **Weekly churn forecast** (based on lines added/deleted)
  - 🕒 **Cycle time prediction** (for PRs)
  - 🧠 **Code Review Influence Map** using graph network visualization
- 🔎 **Developer-level analytics**: Search and filter developers to see their individual contribution stats and visual breakdowns.

### ✅ **2. AI Agent Pipeline (LangGraph-based)**
- `LangGraph`-based stateful agent workflow includes:
  - 📦 `DataHarvester`: loads and stores GitHub data (commits & PRs)
  - 📊 `DiffAnalyst`: performs statistical analysis on contributions
  - 🧠 `InsightNarrator`: generates weekly AI-written reports

### ✅ **3. Slack Integration**
- Slack bot runs using `SocketMode`, sends reports or metrics, and can be extended for automated queries or notifications.

### ✅ **4. Dummy Data & Seeding**
- Comes with `seed_dummy_commits.py` and `seed_dummy_prs.py` to auto-generate realistic dummy commit/PR data
- Allows testing full functionality even without a live GitHub connection

---

## 🛠️ Tech Stack

| Category      | Tools / Frameworks                                 |
|---------------|-----------------------------------------------------|
| Frontend      | Streamlit (Dashboard UI)                           |
| Backend       | Python, SQLite (via SQLAlchemy ORM)                |
| AI/Agent      | LangGraph, LangChain                               |
| Data Analysis | Pandas, Matplotlib, Seaborn, Statsmodels           |
| DevOps        | Docker                                             |
| Messaging     | Slack API (via Slack Bolt)                         |
| Others        | dotenv, NetworkX (for influence maps), JSON        |

---

## 📂 Project Structure

🛠 Step 1: Build and Start the Containers
bash
Copy
Edit
docker-compose up --build
✅ This command will:

🔨 Build the Docker image from the Dockerfile

🚀 Start all services defined in docker-compose.yml

🖥 Launch the Streamlit Dashboard at:
👉 http://localhost:

🤖 Start the Slack bot (ensure your .env tokens are correct)



🚀 Advanced Features I worked on : 

Engineering Productivity Insights Bot comes packed with intelligent, production-ready analytics. Here's what it offers:

📈 Forecasting & Time Series Analysis
Weekly Churn Forecast
Predict next week’s total code churn using the Holt-Winters Exponential Smoothing Model.

Cycle Time Forecasting
Get predictive insights into the average time developers take to close PRs over time.

🧠 Code Review Influence Map
Visualizes Review Dynamics
Shows which developers influence others in PR reviews using a NetworkX graph.

Interactive Graph
Dynamic node sizing and color mapping help visually assess review intensity and central developers.

👤 Developer-Centric Insights
Searchable Developer Panel
Select a developer from a dropdown to view their personal:

Total commits and PRs

Average churn and cycle time

Pie chart: Additions vs Deletions

Bar chart: Weekly contribution trends

Visual Performance Breakdown
Track individual productivity using pie charts and bar plots embedded in the Streamlit UI.

📊 Rich, Interactive Dashboard (Built with Streamlit)
Clean, responsive interface

Interactive charts, graphs, and tables

Filters and sliders to control data range (days)

Easy to extend with more metrics

🧠 Automated AI Agent Pipeline (LangGraph)
Agent 1: DataHarvester – Loads and stores GitHub activity

Agent 2: DiffAnalyst – Analyzes the code changes

Agent 3: InsightNarrator – Summarizes activity into readable reports

🤖 Slack Integration
SocketMode Slack Bot
Sends summaries directly to your Slack workspace.

Weekly Reports in Slack
See top contributors, code churn, PR summaries, and more inside your team’s Slack channel.

🐳 Dockerized for Simplicity
=======
## FIKA AI Research — Engineering-Productivity Intelligence **MVP** Challenge

*[Learn more at **powersmy.biz**](https://powersmy.biz/)*

### 🚀 Hiring Opportunity

**We're hiring!** This challenge is part of our recruitment process for engineering positions. We offer both **remote** and **on-site** work options to accommodate your preferences and lifestyle.

### 1 ✦ Context

We need a chat-first, AI-powered view of how every engineer and squad are performing—both technically and in terms of business value shipped. Build a **minimum-viable product (MVP)** in fewer than seven days that delivers these insights inside Slack **or** Discord.

### 2 ✦ Core MVP Requirements (non-negotiables)

| Area                     | Requirement                                                                                                                                                                                                                                                   |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Agent-centric design** | Use **LangChain + LangGraph** agents written in **Python 3.10+**. Provide at least two clear roles—*Data Harvester* and *Diff Analyst*—handing off to an *Insight Narrator* agent via LangGraph edges.                                                        |
| **Data ingestion**       | Pull GitHub events via REST or webhooks. The commits API exposes `additions`, `deletions`, `changed_files` per commit ([docs.github.com][3]); the *List PR files* endpoint gives the same per-file counts ([docs.github.com][4]).                             |
| **Metrics**              | Track commits, PR throughput, review latency, cycle time, CI failures **plus per-author diff stats** (lines ±, files touched). Optionally fall back to `git log --numstat` for local analysis ([stackoverflow.com][5]).                                       |
| **Diff analytics layer** | Your *Diff Analyst* agent aggregates churn, flags spikes, and links code-churn outliers to defect risk (research shows churn correlates with bugs) ([stackoverflow.com][6]).                                                                                  |
| **AI insight layer**     | Agents transform data into daily, weekly, monthly narratives that map to DORA’s four keys (lead-time, deploy frequency, change-failure, MTTR) ([dora.dev][7]). Log every prompt/response for auditability.                                                    |
| **Chat-first output**    | A **Slack bot** (Bolt Python SDK) ([api.slack.com][8]) or **Discord bot** (discord.js slash-command with embeds) ([discordjs.guide][9]) must, on `/dev-report weekly`, post a chart/table + the agent summary. JSON API is optional but the bot is mandatory. |
| **MVP polish**           | One-command bootstrap (`docker compose up` or `make run`). Include a seed script with fake GitHub events so reviewers see data instantly.                                                                                                                     |
| **Docs**                 | `README.md` with bot install guide and an architecture diagram showing LangGraph nodes/edges, storage and chat layer.                                                                                                                                         |

### 3 ✦ Tech Stack (required)

* **Language:** Python 3.10+
* **Agent Frameworks:** LangChain ≥ 0.1.0 ([python.langchain.com][1]) and LangGraph service or OSS package ([langchain.com][2])
* **Chat SDK:** Slack Bolt-Python **or** discord.js (node sidecar acceptable) ([api.slack.com][8], [discordjs.guide][9])
* **Storage:** any Python-friendly store (Postgres, SQLite, DuckDB, TinyDB).
* **Viz:** matplotlib, Plotly, or quick-chart PNGs.

### 4 ✦ Stretch Goals (optional)

* Forecast next week’s cycle time or churn.
* Code-review “influence map” graph.
* Pluggable LLM driver (OpenAI ↔ local Llama) in < 15 min.
* Scheduled digests (bot auto-drops Monday summary).

### 5 ✦ Deliverables

1. **Pull Request** to the challenge repo containing code + docs.
2. ≤ 3-minute Loom/GIF demo (encouraged).

### 6 ✦ Timeline

*Fork today → PR in **72 hours** (extensions on request).*
We’ll smoke-test your bot in our workspace, then book your interview.

### 7 ✦ Evaluation Rubric (100 pts)

| Category                         | Pts | What we look for                                                |
| -------------------------------- | --- | --------------------------------------------------------------- |
| LangGraph agent architecture     | 25  | Clear roles, deterministic edges, minimal hallucination.        |
| MVP completeness & correctness   | 25  | Metrics and diff stats accurate; bot responds; seed data works. |
| Code quality & tests             | 20  | Idiomatic Python, CI green.                                     |
| Insight value & business mapping | 15  | Narratives help leadership act.                                 |
| Dev X & docs                     | 10  | Fast start, clear setup, diagrams.                              |
| Stretch innovation               | 5   | Any wow factor.                                                 |

### 8 ✦ Interview Flow

1. **Code/architecture dive (45 min)**
2. **Edge-case & scaling Q\&A (30 min)**
3. **Product thinking & culture fit (15 min)**

### 9 ✦ Ground Rules

Original work only; public libs are fine. Don’t commit real secrets. We may open-source the winning MVP with credit.

> **Ready?** Fork ✦ Build ✦ PR ✦ Impress us.
> Questions → **[founder@powersmy.biz](mailto:founder@powersmy.biz)**

---

### Quick Reference Links

* LangChain docs ([python.langchain.com][1]) – prompt, tool and memory helpers.
* LangGraph overview ([langchain.com][2]) – stateful orchestration patterns.
* GitHub Commits API (`additions`/`deletions`) ([docs.github.com][3])
* GitHub PR Files API (per-file diff) ([docs.github.com][4])
* Slack slash-commands guide ([api.slack.com][8])
* Discord embeds guide ([discordjs.guide][9])
* Git diff `--numstat` usage ([stackoverflow.com][5])
* DORA four-key metrics ([dora.dev][7])
* Code-churn research on defects ([stackoverflow.com][6])

These resources should cover everything you need—happy hacking!

[1]: https://python.langchain.com/docs/introduction/?utm_source=chatgpt.com "Python LangChain"
[2]: https://www.langchain.com/langgraph?utm_source=chatgpt.com "LangGraph - LangChain"
[3]: https://docs.github.com/rest/commits/commits?utm_source=chatgpt.com "REST API endpoints for commits - GitHub Docs"
[4]: https://docs.github.com/en/rest/pulls/pulls?utm_source=chatgpt.com "REST API endpoints for pull requests - GitHub Docs"
[5]: https://stackoverflow.com/questions/9933325/is-there-a-way-of-having-git-show-lines-added-lines-changed-and-lines-removed?utm_source=chatgpt.com "Is there a way of having git show lines added, lines changed and ..."
[6]: https://stackoverflow.com/questions/56941641/using-githubs-api-to-get-lines-of-code-added-deleted-per-commit-on-a-branch?utm_source=chatgpt.com "Using GitHub's API to get lines of code added/deleted per commit ..."
[7]: https://dora.dev/guides/dora-metrics-four-keys/?utm_source=chatgpt.com "DORA's software delivery metrics: the four keys"
[8]: https://api.slack.com/interactivity/slash-commands?utm_source=chatgpt.com "Enabling interactivity with Slash commands - Slack API"
[9]: https://discordjs.guide/popular-topics/embeds?utm_source=chatgpt.com "Embeds | discord.js Guide"
>>>>>>> eddd19b4351bad0688fc7c782e39e9b2ec944911
