# insight_narrator.py
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def insight_narrator_node(state):
    print("\n🧠 [InsightNarratorAgent] Generating summary with Gemini...")

    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-2.0-flash")

    analysis = state.get("analysis", {})
    if not analysis:
        print("⚠️ No analysis found.")
        state["summary"] = "No summary available."
        return state

    formatted = "\n".join([
        f"{user} → {stats['commits']} commits, +{stats['lines_added']} / -{stats['lines_deleted']} lines"
        for user, stats in analysis.items()
    ])

    prompt = f"""
    Generate a weekly engineering productivity report based on the following commit activity:

    {formatted}

    Highlight who contributed most, summarize code churn, and whether it’s a productive or risky week.
    """

    response = model.generate_content(prompt)
    print("📄 Summary:\n")
    print(response.text)

    state["summary"] = response.text
    return state
