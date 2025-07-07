from langchain_core.runnables import Runnable
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def forecast_churn(commits: list[dict]) -> int:
    weeks = {}
    for commit in commits:
        week = commit["date"][:10]
        weeks.setdefault(week, 0)
        weeks[week] += commit.get("churn", 0)

    df = pd.DataFrame({"week": list(weeks.keys()), "churn": list(weeks.values())})
    df["week_num"] = range(len(df))

    model = LinearRegression()
    model.fit(df[["week_num"]], df["churn"])
    next_week = [[len(df)]]
    prediction = model.predict(next_week)
    return int(prediction[0])

@Runnable
def forecast_node(state):
    forecast = forecast_churn(state["commits"])
    state["forecast_churn"] = forecast
    return state
