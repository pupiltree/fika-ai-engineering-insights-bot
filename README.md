
# 🚀 Engineering Productivity Intelligence MVP

AI-powered engineering productivity analytics using **LangGraph agents** and **Gemini AI**. Get instant insights into your team's productivity metrics through Slack.

---

## ✨ Features

* **🤖 Agent Pipeline** (LangChain + LangGraph):
  `Data Harvester → Diff Analyst → Insight Narrator`
* **📊 DORA Metrics**: Lead time, deployment frequency, change failure rate, MTTR
* **🔍 Code Churn & Risk Analysis**: Per-author metrics and anomalies
* **💬 Slack Integration**: Slash command `/dev-report` with charts + summaries
* **⚡ Real-Time GitHub Analysis**: Commits, PRs, diff stats
* **🎯 Actionable Insights**: AI-generated team productivity reports via Gemini

---

## 🎥 Demo Video (Local)

To preview the MVP in action, [watch this video](demo/fika-demo.mp4).

It walks through the Slack command usage, GitHub metrics processing, LangGraph agent pipeline, and AI insights.

---


## 🧠 System Architecture

```plaintext
┌──────────────────────────────┐
│        Slack User            │
│   (uses /dev-report)         │
└────────────┬─────────────────┘
             ▼
      ┌───────────────────┐
      │  Flask Web Server │ ◄─── Socket Mode
      │  (manage.py run)  │
      └──────┬────────────┘
             ▼
     ┌────────────────────────┐
     │ LangGraph Workflow     │
     └──────┬───────┬─────────┘
            ▼       ▼
    ┌────────────┐ ┌───────────────┐
    │ Data       │ │ Diff Analyst  │
    │ Harvester  │ │ → DORA + Churn│
    └────┬───────┘ └───────────────┘
         ▼
  ┌────────────────────┐
  │ Insight Narrator   │ ──► Gemini AI
  └─────────┬──────────┘
            ▼
    ┌────────────────────┐
    │ Slack Formatter    │ ──► Slack API (summary + chart)
    └────────────────────┘
```

---

## 🏗️ Project Structure

```
engineering-productivity-mvp/
├── .env.example
├── manage.py                   # CLI tool: run, seed, setup, test, etc.
├── requirements.txt
├── data/
│   ├── productivity.db         # SQLite DB
│   └── seed/sample_github_events.json
├── scripts/
│   ├── run_local.py
│   ├── seed_data.py
│   └── setup_db.py
└── src/
    ├── agents/                 # LangGraph agents
    ├── graph/                  # Workflow logic
    ├── data/                   # GitHub API, DB models
    ├── chat/                   # Slack bot integration
    ├── viz/                    # Charts (Plotly)
    └── config.py               # Config loader
```

---

## 🚀 Quick Start

### 1. Prerequisites

* Python 3.10+
* GitHub token (`repo` or `public_repo` scope)
* Gemini API key
* Slack workspace with **bot installed**
* Slack App-level Token for **Socket Mode**

---

### 2. Installation

```bash
# Clone the repo
git clone https://github.com/JORDAN-RYAN1/Engineering-Productivity-Intelligence-MVP-Challenge.git
cd engineering-productivity-mvp

# Create a virtual environment (named 'venv' here)
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows (cmd):
venv\Scripts\activate.bat
# Or on Windows (PowerShell):
venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Copy env config
cp .env.example .env
```

---

### 3. Configure `.env`

```env
# Required
GITHUB_TOKEN=ghp_xxx
GEMINI_API_KEY=AIza...

SLACK_BOT_TOKEN=xoxb-...
SLACK_SIGNING_SECRET=...
SLACK_APP_TOKEN=xapp-...

# GitHub defaults
DEFAULT_REPO_OWNER=your-github-username
DEFAULT_REPO_NAME=your-repo-name
```

---
## 🔐 4. API Keys Setup

### 🔑 GitHub Personal Access Token

1. Visit [GitHub Personal Access Tokens](https://github.com/settings/tokens)
2. Click **"Generate new token (classic)"**
3. Select scopes:

   * `repo` → for private repositories
   * `public_repo` → for public repositories only
4. Copy the token (starts with `ghp_` or `github_pat_`)

### 🤖 Google Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click **"Create API key"**
3. Copy the key (starts with `AIza`)


### 🔑 Slack Tokens Setup

> You’ll need to **create a Slack App** from scratch with **Socket Mode enabled**.

#### 1. Create Slack App

* Go to: [https://api.slack.com/apps](https://api.slack.com/apps)
* Click **"Create New App"** → From scratch
* App name: `DevReportBot`
* Workspace: your Slack workspace

#### 2. Add Bot Token Scopes

Navigate to **OAuth & Permissions** → Under **Bot Token Scopes**, add:

```
app_mentions:read
channels:join
channels:read
chat:write
chat:write.public
commands
files:read
files:write
```

> After adding scopes, click **“Install to Workspace”**
> Copy your **Bot Token** (starts with `xoxb-`)

```env
SLACK_BOT_TOKEN=xoxb-...
```

---

#### 3. Get the Slack Signing Secret

* Go to **"Basic Information"** in your Slack App settings
* Under **App Credentials**, copy the **Signing Secret**

```env
SLACK_SIGNING_SECRET=...
```

---

#### 4. Enable Socket Mode

* Go to **"Socket Mode"** → Toggle **ON**
* Click **"App-Level Tokens"** → Create new token:

  * Name: `socket-connection`
  * Scope: `connections:write`

> Copy the token (starts with `xapp-`)

```env
SLACK_APP_TOKEN=xapp-...
```

---

#### 5. Add Slash Command

* Go to **"Slash Commands"** → Create new command:

```
Command: /dev-report
Short Description: Get engineering productivity metrics and insights
Usage Hint: [weekly|daily|monthly] [repo-name] [author]
Request URL: (leave blank — Socket Mode handles this)
```

---

## 🔗 Add Slack Bot to a Channel

1. In your Slack workspace, navigate to the channel (e.g. `#engineering`)
2. Use `/invite` command:

```bash
/invite @DevReportBot
```

3. Now the bot can respond in that channel when `/dev-report` is used.

---

## 💬 Slack Integration Details

### 🔧 Command Usage

```bash
/dev-report                       # Weekly report for default repo
/dev-report monthly               # Monthly report  
/dev-report weekly my-repo        # Weekly report for specific repo
/dev-report daily owner/repo      # Daily report for owner/repo
/dev-report weekly repo author    # Report for a specific author
```

### 5. Setup Database

```bash
python manage.py setup    # Creates SQLite schema
python manage.py seed     # (Optional) Seed with sample GitHub events
```


---
### 6. Run Locally

```bash
python manage.py run      # Starts Flask + Socket Mode listener
```

Slack bot should now respond to `/dev-report` in your workspace.

---


## 📊 Metrics Tracked

### DORA Metrics ([https://dora.dev](https://dora.dev))

* 🚀 Deployment Frequency
* ⏱️ Lead Time
* ❌ Change Failure Rate
* 🔧 MTTR

### Developer Insights

* Commit counts, PRs, code churn
* Author-level activity and trends
* Risk detection based on churn spikes

---
## ⚡ Performance

* ⏱️ **Analysis time**: 30–60 seconds
* 📈 **Charts per report**: 4
* 🧪 **AI requests per run**: \~6 (Gemini API)
* 💾 **Data sources**: GitHub API + SQLite

---

## 📈 Example Slack Output

```
📊 Weekly Productivity Report: microsoft/vscode

🎯 Executive Summary
5 contributors delivered 42 commits this week.

📊 DORA Metrics:
🚀 Deploys/day: 1.2
⏱️ Lead time: 18.5 hrs
❌ Failure rate: 15.8%
🔧 MTTR: 4.2 hrs

🏆 Top Contributors:
1. alice.smith - 15 commits
2. bob.jones - 12 commits

🎯 Actions:
- Recognize alice.smith
- Improve review bottlenecks
```
## 📈 Generated Charts

The system automatically creates:

* 📅 **Commit Activity Timeline** — Daily commit patterns
* 🧑‍🤝‍🧑 **Contributor Comparison** — Per-author productivity
* 📊 **DORA Metrics Dashboard** — Four key metrics visualized
* 🔁 **Code Churn Analysis** — Risk spikes and anomalies

Charts are uploaded directly to Slack with each report.



---


## 🧰 Troubleshooting

### ⚠️ "Slack command not responding"

* ✅ Ensure **Socket Mode** is enabled in Slack app
* ✅ Double-check `SLACK_APP_TOKEN` in `.env`
* ✅ Verify bot is invited to the target Slack channel
* ✅ Confirm you've installed the app to the workspace
* ✅ Server must be running locally (`python manage.py run`)

---

### 📭 "No events found"

* 🔍 Ensure `GITHUB_TOKEN` has correct scopes
* ✅ Check repo name and owner in `.env` or command
* 🕒 Try increasing `DEFAULT_LOOKBACK_DAYS` to expand time window

---

### 📉 "Charts not uploading"

* ✅ Confirm `files:write` scope is in Slack app
* 🔁 Reinstall the Slack app after adding scopes
* 🔐 Double-check Slack Bot Token is up to date

---

### 🤖 "LLM API errors"

* ✅ Verify your Gemini API key is correct
* 📊 Check if you've hit your Gemini API quota limit
* 🧪 For local testing, set:

```env
DISABLE_AI=true
```

This will skip all Gemini-related output.



---

## 📝 License

This MVP is part of the **FIKA AI Research – Engineering Productivity Intelligence Challenge**
Built with ❤️ using **LangGraph**, **LangChain**, and **Gemini AI**

---

