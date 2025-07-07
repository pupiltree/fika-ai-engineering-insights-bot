# Dev Insights Bot (MVP)

This bot ingests GitHub commit data, analyzes churn, and delivers a DORA-style summary into Slack.

## 🔧 Setup

```bash
git clone <your-fork>
cd mvp-dev-insights-bot
docker compose up
```

## 🚀 Usage

- In Slack, type `/dev-report` to get the weekly summary.

## 📊 Architecture

```bash

DataHarvester → DiffAnalyst → InsightNarrator → SlackBot
```

LangGraph handles orchestration. See `main.py` for graph setup.

## 🕸 Architecture Diagram

```mermaid
graph TD
    A[Slack Command] --> B[LangGraph Flow]
    B --> C[Data Harvester Node]
    C --> D[Diff Analyst Node]
    D --> E[Insight Narrator Node]
    E --> F[Slack Response]

## Note

/src/storage/insights.txt holds a sample result I got from testing it once with dummy data

and .github/workflows/ci.yml file contains automatic test and validate flows..

