
An AI-powered Slack bot that analyzes GitHub repositories and generates insightful developer performance reports using LangGraph agents and Google Gemini or Mistral LLM.

The agents work on real-time data directly from the this Github Repository.

---

## 🚀 Features

- ✅ Fetches GitHub commit and pull request data
- 🧠 Analyzes code churn, commit frequency, risky files, and tag usage
- 🧾 Summarizes developer performance using Mistral LLM
- 💬 Posts interactive weekly reports to Slack via a slash command (`/dev-report`)
- ♻️ Uses caching to avoid repeated GitHub API calls
- 🧩 Modular architecture built using **LangGraph**, **LangChain**, and **Slack Bolt**
- 👀Analyzed GitHub activity to calculate key DORA metrics like deployment frequency, change volume (churn), and developer commit frequency using commits, pull requests, and timestamps.
---

## 🧩 Agents Overview

### 🛠️ 1. `data_harvester_agent`
- Fetches commits & pull requests using GitHub API
- Uses local JSON cache to avoid refetching

### 📈 2. `diff_analyst_agent`
- Analyzes developer contributions:
  - Commit count
  - Churn: additions, deletions
  - Risky files
  - Commit frequency
  - Structured tag usage (`fix`, `feat`, `refactor`)
- Adds analysis to state as `developer_analysis`

### 🧠 3. `narrator_agent`
- Uses **Mistral LLM** or **Google Gemini** to convert raw analytics into an executive-level markdown report
- Prompts it to sound like an engineering team lead

---

## 💬 Slack Integration

- `/dev-report`: Triggers report generation via slash command
- Posts a "loading" message first
- Updates it with the final report after LangGraph finishes

---

## 🧪 How to Run (Locally)

### 1. 📦 Install dependencies

pip install -r requirements.txt

2. 🧪 Set up environment variables (.env)

Add You env variables

3. 🌐 Start Slack Bot Locally

python insight_agents/slack_bot.py

4. 🔁 Start ngrok

ngrok http 3000

5. ✅ Testing without Slack

You can run the system standalone using:

-test_agent.py

This runs the full LangGraph pipeline and prints the summary report in the terminal.

### 2. 🧠 Technologies Used

    >>> LangGraph

    >>> LangChain

    >>> Slack Bolt for Python

    >>> Json for storing data

    >>> MistralAI via langchain_mistralai

    >>> Google Gemini 

    >>> GitHub REST API (commits + PRs)

    >>> Ngrok for local Slack testing

### 3. Future Improvements
    🧪 Add tests and CI workflows

    📊 Visual dashboards via Slack Canvas or Notion API

    🧠 Fine-tuned summarization models

    ⏱️ Support for weekly/monthly filters via date ranges

    💼 Multi-repo and team-based insights

### Build by
👨‍💻 Rutwik Kadam

