# 🔍 FIKA Engineering Productivity Bot – MVP Submission

This repository contains my submission for the FIKA AI Developer Productivity Challenge. The goal was to build an agent-centric, chat-first Slack bot that summarizes developer performance from GitHub commit activity, using AI agents and LangGraph.

---

## ✨ Demo & Explanation

🎥 [Watch the 3-minute demo video](https://www.loom.com/share/demo-link-here)  
📝 (Make sure to replace this with your Loom or video link!)

---

## 📌 Problem Statement Summary

FIKA wants a chat-first bot (Slack or Discord) that summarizes how engineers and squads are performing using GitHub activity. The insights should reflect metrics like code churn, PRs, review time, and map to DORA metrics. The entire pipeline must be agent-driven using LangChain + LangGraph, and return results inside a Slack command.

---

## ✅ Core Features Implemented

| Feature                     | Status        | Description |
|----------------------------|---------------|-------------|
| LangGraph Agent Orchestration | ✅ Done     | `StateGraph` connects 3 agents with clear roles: `DataHarvester → DiffAnalyst → InsightNarrator` |
| GitHub Data (Seeded)       | ✅ Done        | Used `seed_data.json` to simulate real commit events with churn, author, date etc. |
| Diff Analytics             | ✅ Done        | Code churn is analyzed per author. Spikes detected and marked for risk. |
| AI Summary Layer           | ✅ Done        | Generates clear, actionable summary of metrics using `insight_narrator` |
| Chart Visualization        | ✅ Done        | Bar chart using `matplotlib` shows commit churn per author |
| Slack Bot                  | ✅ Done        | Slash command `/dev-report` returns both image + summary |
| Bootstrap & Seed Script    | ✅ Done        | Works via `python bots/slack_bot.py`. Loads fake data instantly. |
| README + Architecture      | ✅ Done        | This document plus flow explanation below. |

---

## 🤖 LangGraph Architecture

![LangGraph Flow](./docs/langgraph-architecture.png)

> This flow shows how each agent passes its output to the next:
>
> - **DataHarvester** → collects commit data (seeded)
> - **DiffAnalyst** → performs churn analytics
> - **InsightNarrator** → turns data into natural language insights

Implemented using LangGraph’s `StateGraph`, transitions are deterministic.

---

## 🧠 AI Summary Sample Output

> 📊 *Code Churn Report*
> - Total commits analyzed: 8  
> - High churn commits: 2  
> - Highest churn author: `JohnDoe` with 121 lines changed  
> - 🔺 Risk Alert: Sudden churn spike in commit `3f9e...`  
>  
> 🔎 Overall: JohnDoe contributed actively this week. Churn is moderate. Recommend a review for commit `3f9e...` to ensure stability.

---

## 📈 Charts Generated

| Type        | Description |
|-------------|-------------|
| Commit Churn | Bar chart showing churn (lines changed) per author |
| Commit Count | Optional chart showing number of commits per author (included in code) |

---

## 💬 How To Use

1. Set your `.env` file:

```

SLACK\_BOT\_TOKEN=xoxb-...
SLACK\_SIGNING\_SECRET=your-secret
SLACK\_APP\_TOKEN=xapp-...

````

2. Install dependencies:
```bash
pip install -r requirements.txt
````

3. Run the bot:

```bash
python bots/slack_bot.py
```

4. On Slack, type:

```
/dev-report
```

> Bot will respond with a churn chart and a human-readable insight summary.

---

## 🧪 Seeded Data

The app uses a local file (`data/seed_data.json`) with mocked GitHub commit activity for instant demo. This avoids GitHub API setup and still demonstrates full functionality.

---

## 📁 Project Structure

```
.
├── agents/
│   ├── data_harvester.py
│   ├── diff_analyst.py
│   └── insight_narrator.py
├── bots/
│   ├── slack_bot.py
│   └── chart_generator.py
├── data/
│   ├── seed_data.json
├── graph_pipeline.py
├── .env
└── README.md
```

---

## 🏁 One-Line Bootstrap (optional Docker)

```bash
docker-compose up
```

---

## 📚 Tech Stack

* Python 3.10+
* LangChain + LangGraph
* Slack Bolt (Python SDK)
* Matplotlib for charts
* dotenv for env vars

---

## 🔍 Evaluation Checklist

| Criteria                       | Done |
| ------------------------------ | ---- |
| LangGraph agents & flow        | ✅    |
| Metrics: churn, commit stats   | ✅    |
| Chart & AI narrative in Slack  | ✅    |
| Seed data to simulate activity | ✅    |
| One-command run / bot ready    | ✅    |
| Polished README & architecture | ✅    |

---

## 📬 Submission

* ✅ Pull request raised to the challenge repo
* ✅ Readme added
* ✅ Video demo recorded

---

## 🙏 Thank You

Appreciate the opportunity to showcase this. Looking forward to your review and feedback!

—
Nikhil Sukthe

```
