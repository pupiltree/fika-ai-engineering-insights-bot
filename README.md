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
