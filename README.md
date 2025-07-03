<<<<<<< HEAD
# PowerBiz Developer Analytics

An AI-powered developer analytics platform using LangChain + LangGraph agents to track engineering performance and deliver insights through Slack.

## Features

### Core MVP Features ✅
- **Multi-agent system** with Data Harvester, Diff Analyst, and Insight Narrator agents
- **GitHub data integration** for tracking commits, PRs, and code changes
- **DORA metrics tracking** for lead time, deploy frequency, change failure rate, and MTTR
- **Slack bot integration** with `/dev-report` commands for instant insights
- **Code churn analysis** linking patterns to defect risk
- **Developer performance analytics** for both technical contributions and business value
- **One-command bootstrap** with Docker Compose
- **Seed data** for instant demo experience

### Stretch Goals Implemented 🚀
- **📈 Forecasting**: Predict next week's cycle time and code churn based on historical trends
- **🕸️ Influence Map**: Code review collaboration graph showing knowledge bottlenecks
- **🎯 Advanced Analytics**: PR size risk assessment, defect correlation analysis
- **📊 Comprehensive DORA**: Full four-key metrics with performance categorization
- **🤖 Prompt Logging**: All LLM interactions logged for auditability

### Technical Highlights
- **LangGraph orchestration** with deterministic agent handoffs
- **SQLite/PostgreSQL** flexible storage backend
- **Matplotlib/Plotly** visualization pipeline
- **Async processing** for GitHub API efficiency
- **Type-safe** Python 3.10+ with Pydantic models

## Architecture

```
                   ┌───────────────┐
                   │   GitHub API  │
                   └───────┬───────┘
                           │
                           ▼
┌────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐
│ Data Harvester ├─▶│  Diff Analyst   ├─▶│ Insight Narrator │─▶│   Slack Bot   │
│     Agent      │  │     Agent       │  │      Agent      │  │               │
└────────────────┘  └─────────────────┘  └─────────────────┘  └───────────────┘
                           │                     │                     │
                           │                     │                     │
                           ▼                     ▼                     ▼
                    ┌─────────────┐       ┌────────────┐       ┌─────────────┐
                    │ Code Metrics│       │  Analytics │       │ Charts/Data │
                    │  Database   │       │ & Insights │       │  Rendering  │
                    └─────────────┘       └────────────┘       └─────────────┘
```

## Quick Start

### Prerequisites

- Python 3.10+
- Docker and Docker Compose (optional)
- GitHub API token ([create here](https://github.com/settings/tokens))
- Slack Bot token ([setup guide below](#slack-app-setup))
- OpenAI API key ([get here](https://platform.openai.com/api-keys))

### One-Command Bootstrap

```bash
# Clone and start with Docker
git clone https://github.com/yourusername/powerbiz.git
cd powerbiz
cp .env.example .env
# Edit .env with your API tokens
docker-compose up --build
```

### Manual Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/powerbiz.git
   cd powerbiz
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your GitHub token, Slack credentials, and OpenAI API key
   ```

3. Install and run:
   ```bash
   make install
   make seed    # Populate with demo data
   make run     # Start the Slack bot
   ```

   Or manually:
   ```bash
   pip install -r requirements.txt
   python seed_data/seed.py
   python -m powerbiz
   ```

## Slack Commands

- `/dev-report daily` - Get daily developer performance insights
- `/dev-report weekly` - Get weekly team performance report with DORA metrics
- `/dev-report monthly` - Get monthly engineering performance overview
- `/dev-report engineer @username` - Get performance details for a specific engineer

## Development

### Project Structure
```
powerbiz/
├── powerbiz/
│   ├── agents/              # LangChain + LangGraph agents
│   │   ├── data_harvester.py    # GitHub data collection & analysis
│   │   ├── diff_analyst.py      # Code churn & defect risk analysis  
│   │   ├── insight_narrator.py  # Performance narrative generation
│   │   └── workflow.py          # LangGraph orchestration
│   ├── database/            # Database models and operations
│   ├── github_api/          # GitHub API integration
│   ├── slack_bot/           # Slack bot integration
│   └── visualization/       # Charts and visualization tools
├── tests/                   # Test suite
├── seed_data/               # Seed data for demo purposes
├── docker/                  # Docker configuration
├── .env.example             # Environment configuration template
├── docker-compose.yml       # Docker Compose configuration
└── Makefile                 # Development commands
```

### Running Tests

```bash
# Run all tests
make test

# Or manually
python -m pytest tests/ -v
```

### Development Commands

```bash
make help          # Show all available commands
make install       # Install dependencies
make run           # Run the application
make test          # Run tests
make seed          # Populate database with demo data
make clean         # Clean up generated files
make docker-run    # Run with Docker Compose
```

## ⚡ Smoke Test Ready

This MVP is ready for immediate evaluation. Run the smoke test to verify everything works:

```bash
# Quick smoke test (no dependencies needed)
python smoke_test.py

# Expected output: "🎉 All smoke tests passed!"
```

### For Evaluators/Reviewers

**Zero-setup demo experience:**

1. **Clone & Test:**
   ```bash
   git clone https://github.com/yourusername/powerbiz.git
   cd powerbiz
   python smoke_test.py  # Verify core functionality
   ```

2. **Demo Mode (no API keys needed):**
   ```bash
   export DEMO_MODE=true
   export SLACK_BOT_TOKEN=demo
   export SLACK_SIGNING_SECRET=demo
   export SLACK_APP_TOKEN=demo
   python -m powerbiz
   ```

3. **With Demo Data:**
   ```bash
   pip install -r requirements.txt
   python seed_data/seed.py  # Creates SQLite DB with sample data
   python -m powerbiz
   ```

**Key features to test:**
- `/dev-report weekly` - Returns demo engineering report
- Agent architecture - DataHarvester → DiffAnalyst → InsightNarrator
- DORA metrics - Lead time, deployment frequency, etc.
- Stretch goals - Forecasting, influence maps, defect risk analysis

## API Documentation

### Agent Architecture

The PowerBiz platform uses a multi-agent architecture orchestrated by LangGraph:

1. **DataHarvesterAgent**: Collects and processes GitHub repository data
   - Fetches commits, pull requests, and repository metadata
   - Calculates DORA metrics and code churn statistics
   - Handles rate limiting and async processing

2. **DiffAnalystAgent**: Analyzes code changes for quality and risk
   - Performs defect risk assessment based on code churn patterns
   - Generates influence maps showing collaboration networks
   - Tracks technical debt accumulation

3. **InsightNarratorAgent**: Creates business-focused performance narratives
   - Transforms technical metrics into actionable insights
   - Generates forecasts for cycle time and deployment frequency
   - Creates executive-friendly performance summaries

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | OpenAI API key for LLM functionality | Yes | - |
| `GITHUB_TOKEN` | GitHub personal access token | Yes | - |
| `SLACK_BOT_TOKEN` | Slack bot token (xoxb-...) | Yes | - |
| `SLACK_SIGNING_SECRET` | Slack app signing secret | Yes | - |
| `SLACK_APP_TOKEN` | Slack app token (xapp-...) | Yes | - |
| `DATABASE_URL` | Database connection string | No | `sqlite:///powerbiz.db` |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | No | `INFO` |
| `ENVIRONMENT` | Environment (development, production) | No | `development` |
| `DEMO_MODE` | Enable demo mode (true/false) | No | `false` |

### Slack App Setup

To set up the Slack bot in your workspace:

1. **Create a Slack App**:
   - Go to [api.slack.com/apps](https://api.slack.com/apps)
   - Click "Create New App" → "From scratch"
   - Name your app "PowerBiz Analytics" and select your workspace

2. **Configure Bot Permissions**:
   - Go to "OAuth & Permissions"
   - Add these Bot Token Scopes:
     - `app_mentions:read`
     - `channels:history`
     - `chat:write`
     - `commands`
     - `users:read`

3. **Create Slash Commands**:
   - Go to "Slash Commands"
   - Create `/dev-report` command
   - Request URL: `https://your-domain.com/slack/events`

4. **Enable Socket Mode** (for development):
   - Go to "Socket Mode" and enable it
   - Generate an App-Level Token with `connections:write` scope

5. **Install to Workspace**:
   - Go to "Install App" and click "Install to Workspace"
   - Copy the tokens to your `.env` file

### Troubleshooting

**Common Issues:**

1. **"Module not found" errors**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Database errors**:
   ```bash
   make clean  # Remove old database
   make seed   # Recreate with demo data
   ```

3. **Slack authentication errors**:
   - Verify all tokens in `.env` are correct
   - Check bot permissions in Slack app settings
   - Ensure Socket Mode is enabled for development

4. **GitHub API rate limiting**:
   - Use a personal access token with appropriate permissions
   - Consider upgrading to GitHub Enterprise for higher limits

### Security & Privacy

**Data Handling:**
- All GitHub data is processed locally or in your cloud environment
- No sensitive code content is sent to external services
- LLM interactions use only aggregated metrics and metadata
- Configurable data retention policies

**API Key Security:**
- Store API keys in environment variables, never in code
- Use `.env` files for local development
- Consider using secrets management for production deployments
- Rotate keys regularly according to your security policies

**Network Security:**
- HTTPS required for production Slack endpoints
- GitHub API calls use TLS encryption
- Consider VPN or private networking for sensitive environments

## Performance & Scaling

### Database Optimization
- SQLite for development and small teams
- PostgreSQL recommended for production
- Indexed queries for performance at scale
- Configurable retention policies for historical data

### Monitoring & Observability
- Structured logging with configurable levels
- LLM prompt and response logging for auditability
- Performance metrics tracking
- Error reporting and alerting capabilities

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run the test suite: `make test`
5. Run the smoke test: `python smoke_test.py`
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For questions or issues:
- Create an issue on GitHub
- Review the troubleshooting section above
- Check the smoke test output for diagnostic information

---

**Built with ❤️ using LangChain, LangGraph, and modern Python tooling.**
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
