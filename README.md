## 🚀 GitOps Insight Bot (Slack + LangGraph Engineering Productivity MVP)

This is a chat-first, AI-powered engineering productivity bot designed to work inside Slack. It analyzes GitHub commit data, extracts metrics, and generates weekly team performance summaries with insights from Gemini (Google's LLM). The bot is orchestrated using LangGraph agents and can generate interactive charts and detailed reports.

---

## 🔎 Features

* **Multi-Agent System (LangGraph)**:
  * `DataHarvesterAgent` - Fetches GitHub commit metadata (live or sample file)
  * `DiffAnalystAgent` - Analyzes code changes, churn, and risk factors
  * `InsightNarratorAgent` - Generates human-readable reports using Gemini
  * `QueryAgent` - Handles natural language queries about the repository
  * `WorkPatternAnalyzer` - Analyzes team work patterns and productivity metrics

* **Interactive Slack Integration**:
  * `/dev-report` - Generate detailed engineering reports
  * `/dev-ask` - Ask natural language questions about your repository
  * Interactive chart generation and sharing
  * Threaded conversations for better context

* **Advanced Analytics**:
  * Code churn analysis
  * Author contribution metrics
  * Risk assessment of changes
  * Work pattern analysis
  * Interactive visualizations

* **Flexible Deployment**:
  * Supports both live GitHub API and sample data modes
  * Configurable through environment variables
  * Asynchronous processing for better performance

---

## ⚙️ Project Setup

### 1. ♻️ Clone & Environment Setup

```bash
git clone https://github.com/YOUR_USERNAME/your-repo.git
cd your-repo
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. 👁‍🗨 .env Configuration

Create a `.env` file in the root:

```ini
# GitHub API
GITHUB_TOKEN=ghp_yourtokenhere
GITHUB_REPO=owner/repo-name

# Slack
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...

# Gemini API
GEMINI_API_KEY=your_gemini_key

```

---

## 🐳 Docker Setup

### Prerequisites
- Docker installed on your system
- Docker Compose (usually comes with Docker Desktop)

### 1. Build and Run with Docker Compose

The easiest way to run the application is using Docker Compose:

```bash
# Start the application
# This will build the Docker image and start the container
docker-compose up --build

# To run in detached mode (in the background)
# docker-compose up --build -d

# To stop the application
# docker-compose down
```

### 2. Environment Variables with Docker

Create a `.env` file in the project root (if not already present) with your configuration:

```ini
# GitHub API
GITHUB_TOKEN=your_github_token
GITHUB_REPO=owner/repo-name

# Slack
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...

# Gemini API
GEMINI_API_KEY=your_gemini_key

# Optional: Port configuration (default: 3000)
PORT=3000
```

### 3. Building the Docker Image Manually

If you prefer to build and run without Docker Compose:

```bash
# Build the Docker image
docker build -t github-agent .

# Run the container
docker run -p 3000:3000 --env-file .env github-agent
```

### 4. Development with Docker

For development, you might want to mount your local source code into the container for live reloading:

```bash
docker-compose -f docker-compose.dev.yml up --build
```

Make sure you have a `docker-compose.dev.yml` file configured for development with volume mounts.

### 5. Viewing Logs

To view the application logs:

```bash
# When running with docker-compose
docker-compose logs -f

# When running with docker directly
docker logs <container_id>
```

---

## 💬 Slack Bot Setup

### Step 1: Create Slack App

1. Go to: [https://api.slack.com/apps](https://api.slack.com/apps)
2. Click **Create New App** → From scratch
3. Name: `Agents`, workspace: your Slack team

### Step 2: Enable Socket Mode

* Navigate to **Socket Mode**
* Toggle "Enable Socket Mode" ON
* Copy `App Level Token` (`xapp-...`) and add to `.env`

### Step 3: Add Scopes

Under **OAuth & Permissions** → **Bot Token Scopes**, add:

* `commands`
* `chat:write`
* `chat:write.public`
* `files:write`

### Step 4: Create Slash Command

* Go to **Slash Commands**
* Add command `/dev-report`

  * Request URL: `http://localhost:3000/slack/events` *(can be ignored for Socket Mode)*
  * Short description: "Weekly engineering summary"

### Step 5: Install the App

* Go to **Install App**
* Click **Install to Workspace** and authorize
* Copy `SLACK_BOT_TOKEN` from OAuth screen and add to `.env`

### Step 6: Invite Bot to Channel

In Slack:

```
/invite @Agents
```

---

## 🔄 Running the Bot

```bash
python slack_bot/app.py
```

Then in Slack:

```
/dev-report
```

This triggers the LangGraph, analyzes GitHub commit data, and posts a summary.

---

## 📚 Directory Structure

```
.
├── agents/                    # LangGraph agents
│   ├── data_harvester.py      # Fetches GitHub commit data
│   ├── diff_analyst.py        # Analyzes code changes and risks
│   ├── insight_narrator.py    # Generates reports using Gemini
│   ├── query_agent.py         # Handles natural language queries
│   ├── sample_data_harvester.py  # Loads sample data for testing 
│
├── utils/                     # Utility functions
│   └── chart_generator.py     # Generates visualizations
│
├── public/                    # Static files and generated content
│   └── graph.png              # Default chart output
│
├── data/                      # Data files
│   └── commits.json           # Sample commit data
│
├── main.py                    # Main application entry point
├── requirements.txt           # Python dependencies
└── .env.example              # Example environment configuration
```

---

## 📊 Sample Data Seeding (For MVP Review)

If running without GitHub credentials:

Use `sample_data_harvester` agent in main.py
 
---

## 💡 Architecture Diagram

![LangGraph Workflow](public/graph.png)

---

## 🤖 Available Commands

### `/dev-report`
Generate a comprehensive engineering report with metrics and insights.

### `/dev-ask [question]`
Ask natural language questions about your repository, such as:
- "Who are the top contributors this month?"
- "What files have the most changes?"
- "Show me the riskiest files in the codebase"


---

## 🌟 Credits

Built with:

* Python 3.10+
* LangChain + LangGraph
* Slack Bolt SDK
* Plotly / Matplotlib (for charts)
* Google Gemini API

---

## 🚀 Ready to impress

Fork → Build → PR → Slackbot Magic ✔
