📊 FIKA Dev Bot — Engineering Insights in Slack
A chat-first, LangGraph-powered bot that analyzes GitHub activity and posts weekly developer summaries directly in Slack.

🚀 Features
Tracks commits, code churn, CI failures, and contributors.

Slash command /dev-report posts a chart + insight summary.

Uses LangGraph agents: Data Harvester → Diff Analyst → Insight Narrator.

Fully local + seedable with fake GitHub data for fast testing.

⚙️ Prerequisites
Python 3.10+

A Slack workspace with a bot + slash command

GitHub repo access (optional for real data)

🛠️ Setup Instructions
Clone the Repo

bash
Copy
Edit
git clone https://github.com/your-org/fika-ai-engineering-insights-bot.git
cd fika-ai-engineering-insights-bot
Create Virtual Environment

bash
Copy
Edit
python3 -m venv .venv
source .venv/bin/activate
Install Dependencies

bash
Copy
Edit
pip install -r requirements.txt
Configure Environment Variables

Create a .env file in the root:

env
Copy
Edit
SLACK_BOT_TOKEN=your-bot-token
SLACK_APP_TOKEN=your-app-token
SLACK_SIGNING_SECRET=your-signing-secret
GITHUB_TOKEN=your-github-token  # Optional if using real GitHub data
Run the Bot

bash
Copy
Edit
make run
💡 Usage
Once the bot is running:

Invite the bot to a Slack channel.

Type /dev-report to trigger a summary.

You'll see:

A chart image 📊

Weekly summary text 📡

🧪 Fake Data Mode
No GitHub setup? No problem.

By default, the bot generates fake commit data for 4 authors (alice, bob, carol, jai.v). This helps demo functionality instantly.

🧼 Clean Build
bash
Copy
Edit
make clean
Deletes all generated outputs, logs, and cache.

🧩 Architecture
mermaid
Copy
Edit
graph TD
  A[Slack Slash Command] --> B(FIKA Dev Bot)
  B --> C[LangGraph]
  C --> D[Data Harvester]
  D --> E[Diff Analyst]
  E --> F[Insight Narrator]
  F --> G[Chart + Summary Output]

