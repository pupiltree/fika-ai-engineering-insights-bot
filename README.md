# Discord Engineering Productivity Bot

A powerful Discord bot that analyzes GitHub data to generate comprehensive engineering productivity reports using LangChain and LangGraph agents. The bot provides DORA metrics, forecasting, and code review influence maps to help teams understand their development performance.

## 🚀 Features

### 📊 Engineering Metrics
- **DORA Metrics**: Deployment frequency, lead time, change failure rate, and time to restore service
- **Code Quality Metrics**: Commit churn, PR throughput, review latency, and cycle time
- **CI/CD Analysis**: Build failure rates and pipeline performance

### 🔮 Predictive Analytics
- **Cycle Time Forecasting**: Predict next week's average PR cycle time using time series analysis
- **Churn Prediction**: Forecast code churn trends to identify potential issues
- **Trend Analysis**: Identify improving or declining performance patterns

### 👥 Team Collaboration Insights
- **Code Review Influence Map**: Visualize reviewer relationships and influence patterns
- **Developer Activity Analysis**: Track individual and team contributions
- **Collaboration Networks**: Understand team dynamics and knowledge sharing

### 📈 Visual Reports
- **Weekly Report Charts**: Beautiful visualizations of key metrics
- **Influence Network Graphs**: Interactive maps showing code review relationships
- **Trend Analysis Plots**: Time-series visualizations of performance trends

## 🛠️ Prerequisites

Before setting up the bot, ensure you have:

- **Python 3.8+** installed on your system
- **Git** for version control
- **Discord Bot Token** (see setup instructions below)
- **GitHub Personal Access Token** (see setup instructions below)

## 📋 Installation

### Step 1: Clone the Repository
```bash
git clone <your-repository-url>
cd discord_bot
```

### Step 2: Create Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Setup
Create a `.env` file in the root directory:
```env
DISCORD_TOKEN=your_discord_bot_token_here
GITHUB_TOKEN=your_github_personal_access_token_here
```

## 🔧 Discord Bot Setup

### Step 1: Create a Discord Application
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Navigate to the "Bot" section
4. Click "Add Bot"
5. Copy the bot token and add it to your `.env` file

### Step 2: Configure Bot Permissions
1. In the Bot section, scroll down to "Privileged Gateway Intents"
2. Enable "Message Content Intent"
3. Go to "OAuth2" → "URL Generator"
4. Select scopes: `bot` and `applications.commands`
5. Select permissions: `Send Messages`, `Read Message History`, `Use Slash Commands`
6. Use the generated URL to invite the bot to your server

### Step 3: Bot Permissions in Discord
1. Invite the bot using the generated URL
2. In your Discord server, go to Server Settings → Roles
3. Find your bot's role and ensure it has permission to:
   - Send messages in the channel where you'll use it
   - Read message history
   - Use slash commands

## 🔑 GitHub Token Setup

### Step 1: Create Personal Access Token
1. Go to [GitHub Settings](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Give it a descriptive name (e.g., "Discord Bot Analytics")
4. Select scopes:
   - `repo` (Full control of private repositories)
   - `read:org` (Read organization data)
   - `read:user` (Read user profile data)
5. Click "Generate token"
6. Copy the token and add it to your `.env` file

### Step 2: Token Security
- **Never commit your tokens to version control**
- Keep your `.env` file in `.gitignore`
- Rotate tokens regularly for security

## 🚀 Running the Bot

### Development Mode
```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Run the bot
python bot/main.py
```

### Production Mode
```bash
# Using Docker (if available)
docker-compose up -d

# Or run directly
python bot/main.py
```

### Verification
1. Check that the bot appears online in your Discord server
2. Look for "Bot is running" message in the console
3. Test the command: `/dev_report`

## 📖 Usage Guide

### Basic Commands

#### `/dev_report`
Generates a comprehensive weekly engineering productivity report.

**What it does:**
- Fetches GitHub data from the last 7 days
- Calculates DORA metrics and code quality indicators
- Generates forecasts for next week's performance
- Creates visual charts and influence maps
- Posts everything to Discord as formatted messages

**Example Output:**
```
📊 Weekly Engineering Report

🚀 DORA Metrics:
• Deployment Frequency: 3 deployments/week
• Lead Time: 2.5 days average
• Change Failure Rate: 5% (excellent!)
• Time to Restore: 4 hours

📈 Code Quality:
• Commit Churn: 1,250 lines (healthy)
• PR Throughput: 8 PRs/week
• Review Latency: 6 hours average
• Cycle Time: 18 hours average

🔮 Next Week Forecast:
📈 Cycle Time: 20.5 hours (🟡 medium confidence)
📉 Total Churn: 1,100 lines (🟢 high confidence)

👥 Code Review Influence:
• Top Reviewers: @alice, @bob, @charlie
• Most Influential: @alice (15 reviews, 8 approvals)
• Collaboration Network: 12 active reviewers
```

### Understanding the Reports

#### DORA Metrics Explained
- **Deployment Frequency**: How often code is deployed to production
- **Lead Time**: Time from code commit to production deployment
- **Change Failure Rate**: Percentage of deployments causing failures
- **Time to Restore**: How long it takes to fix production issues

#### Code Quality Metrics
- **Commit Churn**: Lines added + deleted (indicates code stability)
- **PR Throughput**: Number of pull requests merged per week
- **Review Latency**: Time between PR creation and first review
- **Cycle Time**: Time from PR creation to merge

#### Forecasting Insights
- **High Confidence**: Model has good historical data for accurate predictions
- **Medium Confidence**: Some uncertainty due to limited data
- **Low Confidence**: Insufficient data for reliable predictions

#### Influence Map Interpretation
- **Node Size**: Larger nodes = more active reviewers
- **Edge Thickness**: Thicker lines = more frequent collaborations
- **Node Color**: Different colors represent different teams or roles

## 🔍 Troubleshooting

### Common Issues

#### Bot Not Responding
```bash
# Check if bot is running
python bot/main.py

# Verify token in .env file
echo $DISCORD_TOKEN  # Should show your token
```

#### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python version
python --version  # Should be 3.8+
```

#### GitHub API Errors
```bash
# Verify GitHub token has correct permissions
# Check token in .env file
echo $GITHUB_TOKEN  # Should show your token
```

#### Missing Charts/Images
```bash
# Install matplotlib dependencies
pip install matplotlib seaborn

# On Windows, you might need:
pip install pillow
```

### Debug Mode
Enable detailed logging by modifying `bot/main.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Environment Variables Check
```bash
# Verify all required variables are set
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('DISCORD_TOKEN:', 'SET' if os.getenv('DISCORD_TOKEN') else 'MISSING')
print('GITHUB_TOKEN:', 'SET' if os.getenv('GITHUB_TOKEN') else 'MISSING')
"
```

## 📁 Project Structure

```
discord_bot/
├── bot/
│   ├── main.py              # Discord bot entry point
│   ├── agents.py            # LangChain/LangGraph workflow
│   ├── github.py            # GitHub API integration
│   ├── forecasting.py       # Time series forecasting
│   ├── influence_map.py     # Code review influence analysis
│   ├── visualization.py     # Chart generation
│   └── storage.py           # Data persistence
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (create this)
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🔧 Configuration Options

### Customizing Analysis Period
Modify the time range in `bot/github.py`:
```python
# Change from 7 days to 14 days
days_back = 14
```

### Adding New Metrics
1. Add calculation logic in `bot/agents.py`
2. Update the report generation in the workflow
3. Add visualization in `bot/visualization.py`

### Customizing Forecasts
Modify forecasting parameters in `bot/forecasting.py`:
```python
# Change forecast period from 7 to 14 days
future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=14, freq='D')
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the console output for error messages
3. Verify your environment variables are set correctly
4. Ensure all dependencies are installed
5. Check Discord and GitHub API status

For additional help, please open an issue in the repository with:
- Your operating system
- Python version
- Error messages
- Steps to reproduce the issue

## 🎯 Use Cases

### For Engineering Managers
- Track team productivity trends
- Identify bottlenecks in development process
- Make data-driven decisions about process improvements
- Monitor code quality and review practices

### For Development Teams
- Understand collaboration patterns
- Identify knowledge sharing opportunities
- Track individual and team performance
- Celebrate improvements and achievements

### For DevOps Teams
- Monitor deployment frequency and stability
- Track CI/CD pipeline performance
- Identify areas for automation improvement
- Measure time to restore service

---

**Happy coding! 🚀** 