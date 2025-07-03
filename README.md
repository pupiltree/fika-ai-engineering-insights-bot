# FIKA AI Engineering Productivity Insights Bot

**A modular, agent-based Python system for actionable engineering analytics, DORA metrics, and Slack reporting.**

---

## 🚀 Quick Docker Setup

1. **Clone the repository:**
   ```sh
   git clone <[this-repo-url](https://github.com/Dheena731/fika-ai-engineering-insights-bot.git)>
   cd fika-ai-engineering-insights-bot
   ```
2. **Copy and edit the environment file:**
   ```sh
   cp env_example .env
   # Edit .env and fill in your Slack, GitHub, and LLM credentials
   ```
3. **Build and run with Docker Compose:**
   ```sh
   docker compose up --build
   ```
   - The bot will install all dependencies, initialize the database, and start listening for Slack commands.

---

## 🏗️ Architecture Diagram

![Architecture Diagram](Flowchart%20(1).jpg)

- **LangGraph agents:** DataHarvester → DiffAnalyzer → InsightNarrator
- **Storage:** All data and reports in SQLite
- **Chat Layer:** Slack bot for interactive reporting

---

## 🤖 Slack Bot Setup & Usage

### 1. **Create a Slack App**
- Go to https://api.slack.com/apps and click "Create New App".
- Choose "From scratch" and give it a name (e.g., `fika-insights-bot`).
- Add the following **Bot Token Scopes** under "OAuth & Permissions":
  - `commands`
  - `chat:write`
  - `files:write`
  - `app_mentions:read`
  - `channels:read`
  - `groups:read`
  - `im:read`
  - `mpim:read`
- Install the app to your workspace and copy the **Bot User OAuth Token** and **App-Level Token** (for Socket Mode).

### 2. **Configure Your .env File**
- Paste your tokens into `.env`:
  ```env
  SLACK_BOT_TOKEN=xoxb-...
  SLACK_APP_TOKEN=xapp-...
  # ...other variables as needed
  ```

### 3. **Invite the Bot to Your Channel**
- In Slack, type `/invite @fika-insights-bot` in the channel where you want reports.

### 4. **Use the Bot Commands**
- In any channel where the bot is present, type:
  - `/dev-report-weekly` — Get a weekly engineering report and charts
  - `/daily-report` — Get a daily summary
  - `/dev-monthly-report` — Get a monthly report
- The bot will reply with a summary and upload relevant charts (PNG files).

### 5. **Troubleshooting**
- If the bot does not respond:
  - Check that it is running (`docker compose ps`)
  - Check your `.env` tokens
  - Ensure the bot is invited to the channel
  - Check logs with `docker compose logs -f`

---

## 🧠 Pluggable LLM (OpenAI ↔ Local Llama)

This bot supports both OpenAI (via OpenRouter) and local Llama models for generating insights.

- **To use OpenAI (default):**
  - Set in your `.env`:
    ```env
    LLM_PROVIDER=openai
    OPENROUTER_API_KEY=your_openrouter_api_key
    ```
- **To use a local Llama model:**
  - Download a compatible Llama model (e.g., `llama-2-7b-chat.ggmlv3.q4_0.bin`).
  - Set in your `.env`:
    ```env
    LLM_PROVIDER=llama
    LLAMA_MODEL_PATH=/app/models/llama-2-7b-chat.ggmlv3.q4_0.bin
    ```
  - Mount your model file into the container if using Docker.

---

## 🔄 Using Real GitHub Data (Disable Seed)

By default, the bot uses seed data for instant demo. To use real GitHub data:

1. Set your GitHub repo and token in `.env`:
   ```env
   GITHUB_TOKEN=your_github_token
   GITHUB_REPO=org/repo
   ```
2. Set `use_seed` to `false` in the pipeline (or via environment/command if supported):
   - Edit the code or set in your environment:
     ```env
     USE_SEED=false
     ```
   - The bot will now fetch live data from GitHub on each run.

---

## 📈 Forecasting

The bot includes forecasting for code churn and lead time:
- **Forecasts** are shown in each report (weekly, daily, monthly) and predict the next period’s churn and lead time based on recent trends.
- Forecasting is automatic and requires no extra setup.
- If using real GitHub data, forecasts will reflect your actual engineering activity.

---

## 🛠️ Extending & Customizing
- **Agents:** Add new agents in `agents/` and wire them in `graph/graph.py`
- **Charts:** Add new chart functions in `viz/charts.py`
- **DB:** Extend schema/queries in `storage/db.py`
- **LLM:** Add new drivers in `llm/llm_client.py`
- **Slack:** Add new commands in `bot/slack_bot.py`

---

## 📝 References
- LangChain: https://python.langchain.com/
- LangGraph: https://www.langchain.com/langgraph
- Slack Bolt: https://slack.dev/bolt-python/
- DORA Metrics: https://dora.dev/guides/dora-metrics-four-keys/

---

## 👥 Credits
- Built for the FIKA AI Research MVP Challenge
- Author: Dhinakaran Thangaraj
---

