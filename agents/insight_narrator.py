from langchain_core.runnables import Runnable

class InsightNarratorAgent(Runnable):
    def invoke(self, input, config=None):
        stats = input.get("stats", {})

        if not stats:
            return {"summary": "No activity found for the given period."}

        summary_lines = []
        total_churn = 0
        top_contributor = None
        max_churn = 0

        for author, data in stats.items():  # ✅ FIXED: .items()
            churn = data["churn"]
            spike_flag = "⚠️" if data["spike"] else ""
            summary_lines.append(
                f"- {author} made {data['additions']} additions, "
                f"{data['deletions']} deletions across {data['files_changed']} files. "
                f"Churn: {churn} {spike_flag}"
            )
            total_churn += churn
            if churn > max_churn:
                max_churn = churn
                top_contributor = author

        summary = "\n".join(summary_lines)
        header = (
            f"📊 Weekly Engineering Summary:\n\n"
            f"Total team churn: {total_churn}\n"
            f"Top contributor: {top_contributor}\n\n"
        )

        return {"summary": header + summary}
