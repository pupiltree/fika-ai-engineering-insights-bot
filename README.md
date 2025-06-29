# FIKA AI Engineering Productivity MVP

## Quick Start

1. Clone repo & set Slack tokens in .env
2. Run: `docker compose up`
3. Invite the bot to your Slack and use `/dev-report`
4. See sample data instantly (seeded)

## Architecture

[Insert architecture diagram here]

## Agents
- Data Harvester: Pulls GitHub data
- Diff Analyst: Computes code churn, flags spikes
- Insight Narrator: Summarizes DORA metrics

## Storage
- SQLite for demo

## Visualization
- matplotlib charts auto-generated

## Seed Data
- Run `python data/seed_github_events.py` to generate fake events

## Contact
Questions? founder@powersmy.biz
