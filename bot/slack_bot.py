from slack_bolt import App

app = App(token="SLACK_BOT_TOKEN", signing_secret="SLACK_SIGNING_SECRET")

@app.command("/dev-report")
def handle_dev_report(ack, say):
    ack()
    # Fetch latest metrics and narrative
    summary = generate_narrative(get_latest_metrics())
    say(summary)

if __name__ == "__main__":
    app.start(port=3000)
