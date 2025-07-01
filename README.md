# FIKA AI Engineering Productivity Intelligence Bot

A chat-first, AI-powered engineering productivity insights bot built with **LangChain + LangGraph** agents. Delivers DORA metrics and code churn analysis directly in Slack.

## Quick Start

### One-Command Bootstrap

**Option 1: Docker Compose (Recommended)**
```bash
docker-compose up --build
```

**Option 2: Make**
```bash
make run
```

**Option 3: Manual Setup**
```bash
pip install -r requirements.txt
python data/seed_github_events.py
python bot/slack_bot.py
```

## Prerequisites

- Python 3.10+
- Slack workspace and app (see Bot Installation Guide below)
- Docker (optional, for containerized deployment)

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  DataHarvester  │───▶│  DiffAnalyst    │───▶│ InsightNarrator │
│  (LangChain)    │    │  (LangChain)    │    │  (LangChain)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ GitHub Data     │    │ Churn Analysis  │    │ DORA Narratives │
│ (Commits, PRs)  │    │ Risk Detection  │    │ Slack Messages  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │     LangGraph           │
                    │   State Management      │
                    │   Agent Orchestration   │
                    └─────────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │     Slack Bot           │
                    │  /dev-report weekly     │
                    └─────────────────────────┘
```

### Agent Workflow

The system uses three specialized agents working together:

1. **DataHarvester**: Pulls GitHub events (commits, PRs) from our SQLite database
2. **DiffAnalyst**: Crunches the numbers on code churn, spots unusual spikes, flags authors with high activity
3. **InsightNarrator**: Takes all that data and turns it into readable reports with DORA metrics
4. **LangGraph**: Handles the coordination between agents and manages state throughout the workflow

## Bot Installation Guide

### 1. Create Slack App

1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name your app (e.g., "FIKA AI Bot") and select your workspace

### 2. Configure App Permissions

**OAuth & Permissions → Bot Token Scopes:**
- `commands`
- `chat:write`
- `chat:write.public` (optional)

**App-Level Tokens:**
- Create token with `connections:write` scope

### 3. Enable Socket Mode

1. Go to **Socket Mode** → Enable Socket Mode
2. Use the App-Level Token created above

### 4. Add Slash Commands

**Create `/dev-report` command:**
- Command: `/dev-report`
- Request URL: `https://example.com` (placeholder for Socket Mode)
- Short Description: `Get engineering productivity insights`
- Usage Hint: `weekly`

**Create `/test` command:**
- Command: `/test`
- Request URL: `https://example.com`
- Short Description: `Test bot connection`

### 5. Install App

1. Go to **Install App** → **Install to Workspace**
2. Copy the **Bot User OAuth Token** (starts with `xoxb-`)
3. Copy the **App-Level Token** (starts with `xapp-`)

### 6. Set Environment Variables

Create `.env` file in project root:
```env
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-level-token-here
```

## Features

### What It Tracks
- **Commit Analysis**: Total commits and breakdown by author
- **PR Throughput**: How fast pull requests move through the pipeline
- **Code Churn**: Lines added/deleted and files touched
- **Risk Detection**: Spots unusual churn spikes and identifies outlier authors

### DORA Metrics Implementation
- **Lead Time**: Average time from PR creation to merge
- **Deploy Frequency**: Number of deployments (we count PR merges)
- **Change Failure Rate**: Percentage of failed CI builds
- **MTTR**: Mean time to recovery (placeholder for now)

### Available Commands
- `/dev-report weekly`: Get the full productivity report
- `/test`: Check if the bot is working
- `@mention`: Get help and see what commands are available

## Development

### Project Structure
```
fika-ai-engineering-insights-bot/
├── fika_agents/           # LangChain agents
│   ├── data_harvester.py  # GitHub data fetching
│   ├── diff_analyst.py    # Code churn analysis
│   ├── insight_narrator.py # Narrative generation
│   └── workflow.py        # LangGraph orchestration
├── bot/                   # Slack bot
│   └── slack_bot.py       # Bot entry point
├── fika_db/              # Database layer
│   └── database.py        # SQLite operations
├── data/                  # Data seeding
│   └── seed_github_events.py # Fake data generator
├── utils/                 # Utilities
│   └── metrics.py         # Metric calculations
├── docker-compose.yml     # Container orchestration
├── Dockerfile            # Container definition
├── Makefile              # Build automation
└── requirements.txt       # Python dependencies
```

### Testing the System
```bash
# Test the full analytics pipeline
python main.py

# Generate some fake data first
python data/seed_github_events.py
```

### Database Schema
We use SQLite with two main tables:
- **commits**: id, author, message, additions, deletions, changed_files, timestamp
- **pull_requests**: id, author, title, additions, deletions, changed_files, created_at, merged_at, review_latency, ci_status

## Configuration

### Environment Variables
You'll need these two tokens from your Slack app:
- `SLACK_BOT_TOKEN`: Bot User OAuth Token from Slack app
- `SLACK_APP_TOKEN`: App-Level Token with connections:write scope

### Database Setup
The system creates a SQLite database (`fika_ai_insights.db`) automatically. Run the seed script to populate it with sample data for testing.

## Sample Output

Here's what a typical weekly report looks like:

```
Weekly Engineering Productivity Report:
Total commits: 20
Commits per author:
  - alice: 5
  - bob: 7
  - carol: 4
  - dave: 4
PR throughput: 5
Average review latency: 12.30 hours
Code churn: +500 / -200
Files touched: 30
Churn spikes detected in 2 commits (possible risk)
Outlier authors (high churn): bob

DORA Metrics:
  - Lead time (avg): 10.50 hours
  - Deploy frequency: 5
  - Change failure rate: 20.0%
  - MTTR: 0.0 (not enough data for real value)
```

## Deployment Options

### For Development
```bash
make run
```

### Production with Docker
```bash
docker-compose up -d
```

### Manual Production Setup
```bash
pip install -r requirements.txt
python data/seed_github_events.py
python bot/slack_bot.py
```

## Tech Stack

- **Language**: Python 3.10+
- **Agent Framework**: LangChain ≥ 0.1.0 + LangGraph
- **Chat Integration**: Slack Bolt for Python
- **Database**: SQLite
- **Containerization**: Docker + Docker Compose
- **Build System**: Make

## License

This project is part of the FIKA AI Engineering Challenge.

---

**Ready to get better insights into your team's productivity? Fork this repo and get started.**