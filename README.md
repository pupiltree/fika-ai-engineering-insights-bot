
# 🧠 Dev Performance Bot (LangGraph + LangChain LLM + Streamlit + Discord)


Track weekly GitHub engineering performance with AI. This project features a Streamlit UI for generating dev reports and a Discord bot for viewing them directly in chat.

---

## 🔥 Key Features

### 🌐 Streamlit Web App
- Agent-powered `/dev-report` summary from GitHub metrics
- Weekly code churn chart with matplotlib
- Stores reports in local SQLite DB
- Built using LangGraph + LangChain

### 🤖 Discord Bot (Optional)
- `/dev_report` shows the latest weekly summary in chat
- `/dev_chart` sends a churn chart image for the last 7 days
- Lightweight, command-driven, and works from the same database

---

## 📸 Demo

> 🖼️ Add a screenshot or Loom link here

---

## 🧠 Tech Stack

- Python 3.11+
- LangGraph + LangChain
- Streamlit
- Matplotlib
- SQLite
- `discord.py` & `app_commands`
- Together AI or OpenAI (LLM backend)

---

## 🚀 How to Run

### 1️⃣ Install dependencies

```bash
pip install -r requirements.txt



2️⃣ Run Streamlit App
streamlit run main.py
3️⃣ Run Discord Bot
python bot.py



