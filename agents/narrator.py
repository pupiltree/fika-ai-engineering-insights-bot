import os
import requests

class InsightNarrator:
    def __init__(self):
        # Choose which LLM provider to use: "builtin", "openai", "llama", or "groq"
        self.llm_provider = os.environ.get("LLM_PROVIDER", "builtin").lower()

    def generate_narrative(self, commits_metrics, prs_metrics, forecasted_churn):
        """
        Generate a DORA-aligned narrative including a forecast of next week's churn,
        optionally enhanced by an LLM provider.
        """
        base_summary = (
            f"🚀 *Deployment Frequency:* {prs_metrics['total_prs']} PRs merged in this period.\n"
            f"⏱ *Lead Time for Changes:* Average review latency is {prs_metrics['avg_review_latency_hours']:.1f} hours.\n"
            f"📈 *Change Churn:* Average churn per commit is {commits_metrics['avg_churn']:.1f} lines.\n"
            f"⚠️ *Change Failure Risk:* {commits_metrics['churn_spikes']} churn spikes detected (possible defect risk).\n"
            f"🔮 *Forecasted Churn Next Week:* ~{forecasted_churn} lines per commit."
        )
        print(f"[🐞] Detected LLM_PROVIDER: {self.llm_provider}")

        if self.llm_provider == "openai":
            print("[🔗] Using OpenAI to generate narrative...")
            return self._generate_with_openai(base_summary)
        elif self.llm_provider == "llama":
            print("[🔗] Using local Llama to generate narrative...")
            return self._generate_with_llama(base_summary)
        elif self.llm_provider == "groq":
            print("[🔗] Using Groq to generate narrative...")
            return self._generate_with_groq(base_summary)
        else:
            print("[ℹ️] Using built-in Python narrative.")
            return base_summary

    def _generate_with_openai(self, prompt):
        from openai import OpenAI
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a DevOps analyst generating DORA insights."},
                {"role": "user", "content": f"Polish and professionalize this summary:\n{prompt}"}
            ]
        )
        return resp.choices[0].message.content.strip()

    def _generate_with_llama(self, prompt):
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": f"Polish and professionalize this summary:\n{prompt}",
                "stream": False
            },
            timeout=60
        )
        data = resp.json()
        return data.get("response", "[❌] Llama generation failed.")

    def _generate_with_groq(self, prompt):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            return "[❌] GROQ_API_KEY not set."
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {
            "model": "llama3-8b-8192",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a senior DevOps engineer and technical writer who generates professional, concise, "
                        "and insightful engineering reports. Your task is to turn raw DORA metrics and churn analysis "
                        "into clear, actionable summaries for engineering leadership. Keep the tone formal, informative, "
                        "and focused on key takeaways. Avoid repetition and unnecessary words."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Here are the raw DORA and code churn insights:\n\n{prompt}\n\n"
                        "Please rewrite them into a polished report summary with bullet points or short paragraphs, "
                        "suitable for sharing with CTOs and engineering managers. Clearly highlight deployment frequency, "
                        "lead time, change churn, change failure risk, and the forecasted churn for next week. "
                        "Conclude with recommendations if any metrics indicate potential risks or areas for improvement."
                    )
                }
            ]
        }
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        print(f"[🐞] Groq raw response: {resp.status_code} {resp.text}")
        data = resp.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "[❌] Groq generation failed.").strip()


if __name__ == "__main__":
    # Example test data
    commits_metrics = {
        "total_commits": 50,
        "total_churn": 21331,
        "avg_churn": 426.6,
        "churn_spikes": 0
    }
    prs_metrics = {
        "total_prs": 20,
        "avg_review_latency_hours": 23.15
    }
    forecasted_churn = 430.12

    narrator = InsightNarrator()
    narrative = narrator.generate_narrative(commits_metrics, prs_metrics, forecasted_churn)
    print("[✔] Generated Insight Narrative:")
    print(narrative)
