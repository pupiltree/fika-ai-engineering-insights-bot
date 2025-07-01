# 🚀 GitOps Insight Bot - FIKA AI Engineering Productivity MVP

A chat-first, AI-powered engineering productivity bot that delivers technical and business value insights directly inside Slack. Built with LangChain + LangGraph agents to analyze GitHub commit data and generate DORA-aligned performance summaries.

---

## 🏗️ Architecture Overview

This MVP uses a multi-agent system orchestrated by LangGraph to transform raw GitHub data into actionable engineering insights:

```
GitHub API → DataHarvesterAgent → DiffAnalystAgent → InsightNarratorAgent → Slack Bot
                    ↓                    ↓                    ↓
              Raw Commit Data    Churn Analysis    DORA-Aligned Reports
```

### LangGraph Agent Architecture

- **DataHarvesterAgent**: Fetches GitHub commit metadata via REST API (commits, PRs, review data)
- **DiffAnalystAgent**: Analyzes code churn, flags outliers, correlates with defect risk
- **InsightNarratorAgent**: Transforms metrics into DORA-aligned narratives (lead time, deploy frequency, MTTR, change failure rate)
- **QueryAgent**: Handles natural language queries about repository performance
- **WorkPatternAnalyzer**: Identifies productivity patterns and cycle time trends

All agent interactions are logged for auditability as required.

---

## 📊 Core Metrics & DORA Alignment

### Tracked Metrics
- **Lead Time**: Commit to deployment time tracking
- **Deploy Frequency**: Release cadence analysis  
- **Change Failure Rate**: CI failure correlation
- **Mean Time to Recovery (MTTR)**: Issue resolution tracking
- **Per-Author Stats**: Lines changed, files touched, review participation
- **Code Churn**: Identifies high-risk changes correlated with defect probability

### Business Value Mapping
The InsightNarratorAgent maps technical metrics to business outcomes:
- Squad velocity trends → delivery predictability
- Code quality signals → maintenance overhead
- Review patterns → knowledge distribution
- Cycle time analysis → customer value delivery speed

---

## 🚀 Quick Start (One-Command Bootstrap)

### Option 1: Docker Compose (Recommended)
```bash
git clone <repo-url>
cd gitops-insight-bot
cp .env.example .env  # Configure your tokens
docker-compose up --build
```

### Option 2: Local Development
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Seed Data for Instant Demo
```bash
# Run with sample data (no GitHub tokens needed)
USE_SAMPLE_DATA=true python main.py
```
The seed script generates 30 days of realistic GitHub events so reviewers can see insights immediately.

---

## 💬 Slack Bot Commands

### Primary Command
- **`/dev-report weekly`** - Generates comprehensive engineering performance report with:
  - DORA metrics visualization
  - Squad performance comparison
  - Code churn risk analysis
  - Actionable insights for leadership

### Interactive Queries
- **`/dev-ask "Who are the top contributors this month?"`**
- **`/dev-ask "What files have the highest churn risk?"`**
- **`/dev-ask "How's our cycle time trending?"`**

All responses include charts, tables, and agent-generated summaries.

---

## ⚙️ Environment Configuration

```ini
# GitHub Data Ingestion
GITHUB_TOKEN=ghp_yourtokenhere
GITHUB_REPO=owner/repo-name

# Slack Integration  
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...

# AI Insights
GEMINI_API_KEY=your_gemini_key

# Optional: Fallback to local git analysis
USE_LOCAL_GIT=false
USE_SAMPLE_DATA=false  # Set true for demo without GitHub access
```

---

## 🔧 Slack Bot Installation Guide

### 1. Create Slack App
1. Visit [https://api.slack.com/apps](https://api.slack.com/apps)
2. **Create New App** → From scratch
3. Name: `GitOps Insight Bot`

### 2. Configure Permissions
**OAuth & Permissions** → **Bot Token Scopes**:
- `commands` (slash commands)
- `chat:write` (post messages)
- `files:write` (upload charts)
- `chat:write.public` (post in channels)

### 3. Enable Socket Mode
- Navigate to **Socket Mode** → Toggle ON
- Generate App Level Token → Copy to `SLACK_APP_TOKEN`

### 4. Add Slash Commands
**Slash Commands** → Create:
- Command: `/dev-report`
- Description: "Generate engineering performance report"
- Usage Hint: `weekly | monthly`

### 5. Install & Invite
1. **Install App** → Install to Workspace
2. Copy **Bot User OAuth Token** to `SLACK_BOT_TOKEN`  
3. In Slack: `/invite @GitOps Insight Bot`

---

## 📁 Project Structure

```
.
├── agents/                    # LangGraph Agent Implementations
│   ├── data_harvester.py      # GitHub API → structured data
│   ├── diff_analyst.py        # Churn analysis & risk scoring
│   ├── insight_narrator.py    # DORA metrics → business narratives
│   ├── query_agent.py         # Natural language query handler
│   └── work_pattern_analyzer.py # Productivity pattern detection
│
├── utils/
│   ├── chart_generator.py     # Plotly visualizations
│   ├── dora_calculator.py     # DORA metrics computation
│   └── github_client.py       # GitHub API wrapper
│
├── data/
│   ├── commits.json           # Sample seed data
│   └── schema.sql             # Database schema
│
├── slack_bot/
│   ├── app.py                 # Slack Bolt application
│   └── handlers.py            # Command handlers
│
├── tests/                     # Unit tests for agents
├── docker-compose.yml         # One-command deployment
├── Dockerfile                 # Container definition
├── requirements.txt           # Python dependencies
└── seed_data.py              # Generates demo GitHub events
```

---

## 🧪 Testing & Data Sources

### Data Ingestion Methods
1. **Live GitHub API**: Real-time commit, PR, and review data
2. **Local Git Analysis**: Fallback using `git log --numstat` 
3. **Sample Data**: 30-day seed dataset for immediate demo

### Test Coverage
```bash
pytest tests/ --cov=agents
```
Covers agent logic, metric calculations, and LangGraph workflows.

---

## 📈 Sample Output

When you run `/dev-report weekly`, expect:

```
📊 Weekly Engineering Summary (Oct 21-28, 2024)

🚀 DORA Metrics:
• Lead Time: 2.3 days (↓15% vs last week)
• Deploy Frequency: 12 releases (↑25%)  
• Change Failure Rate: 8.2% (↓3%)
• MTTR: 4.1 hours (stable)

⚡ Squad Performance:
• Frontend Team: 47 commits, 12 PRs merged
• Backend Team: 31 commits, 8 PRs merged  
• DevOps: 19 commits, 100% CI success

🔍 Code Quality Insights:
• High churn files: auth/login.py, api/users.py
• Review bottleneck: 18hr avg wait time
• Top contributor: @sarah_dev (67 files changed)

💡 Recommendations:
• Consider breaking down large PRs in auth module
• Schedule pair reviews for high-churn areas
• Deploy frequency trending positive—great work!
```

Plus interactive charts showing trends over time.

---

## 🏆 Challenge Requirements Met

✅ **Agent-centric design**: LangChain + LangGraph with clear role separation  
✅ **GitHub data ingestion**: REST API + webhook support  
✅ **DORA metrics**: All four keys tracked and visualized  
✅ **Diff analytics**: Churn analysis with defect risk correlation  
✅ **AI insights**: Gemini-powered narratives with full audit logs  
✅ **Chat-first**: Slack bot with `/dev-report` command  
✅ **One-command bootstrap**: `docker-compose up --build`  
✅ **Seed data**: Instant demo without GitHub tokens  
✅ **Architecture docs**: LangGraph workflow diagram included  

### Stretch Goals Implemented
🎯 **Cycle time forecasting**: Predicts next week's delivery timeline  
🎯 **Scheduled digests**: Auto-posted Monday team summaries  
🎯 **Pluggable LLM**: Swap Gemini ↔ OpenAI in 15 seconds  

---

## 🚀 Demo

[Include 3-minute Loom video here showing:]
1. Bot installation process
2. `/dev-report weekly` command execution  
3. Sample insights and chart generation
4. Natural language queries with `/dev-ask`

---

## 🛠️ Tech Stack

- **Python 3.10+** with asyncio for performance
- **LangChain ≥ 0.1.0** + **LangGraph** for agent orchestration
- **Slack Bolt SDK** for chat integration
- **Plotly** for interactive visualizations  
- **SQLite/PostgreSQL** for metric storage
- **Docker** for deployment simplicity

---

## 📞 Support & Questions

Built for the FIKA AI Engineering Productivity Intelligence MVP Challenge.

For technical questions or demo requests: [your-contact]

---

**Ready to boost your team's engineering productivity? Install the bot and get insights in under 5 minutes! 🚀**