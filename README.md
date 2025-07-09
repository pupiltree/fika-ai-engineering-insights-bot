# 🧠 Dev Performance Bot (Streamlit MVP)

An agent-powered MVP that delivers weekly engineering insights via a clean Streamlit interface.

## 💡 Features

- LangGraph-inspired agent architecture:
  - `DataHarvesterAgent`: loads GitHub metrics (from seed)
  - `DiffAnalystAgent`: analyzes churn for risks
  - `InsightNarratorAgent`: generates weekly summary
- Outputs include PRs merged, cycle time, CI failures
- Charts weekly code churn
- Ready for LangChain plug-in

## 📊 Screenshot

> Add a screenshot or Loom link here.

## 🛠️ How to Run

```bash
pip install -r requirements.txt
streamlit run main.py
