import streamlit as st
from storage.database import Database
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import networkx as nx
import os

# --- Initialize ---
db = Database()
st.set_page_config(layout="wide")

# --- Sidebar ---
st.sidebar.title("🔍 Filters")
days = st.sidebar.slider("Select number of days", min_value=1, max_value=90, value=14)

# --- Fetch data ---
commits = db.get_commits(days)
prs = db.get_prs(days)

# --- Developer Filter and Insights ---
st.sidebar.markdown("---")
st.sidebar.subheader("👤 Developer Insights")

# Unique developer names from commits and PRs
dev_names = sorted(set([c.author for c in commits] + [p.author for p in prs]))

selected_dev = st.sidebar.selectbox("Select Developer", dev_names if dev_names else ["No Developers"])

# --- Header ---
st.title("📊 Engineering Productivity Dashboard")
st.markdown(f"### Showing Data from Last **{days}** Days")

# --- Developer Summary ---
if selected_dev and selected_dev != "No Developers":
    st.subheader(f"📌 Stats for: `{selected_dev}`")

    # --- Developer Commit Stats ---
    dev_commits = [c for c in commits if c.author == selected_dev]
    dev_commit_df = pd.DataFrame([{
        "Date": c.date.strftime("%Y-%m-%d"),
        "Additions": c.additions,
        "Deletions": c.deletions,
        "Churn": c.additions + c.deletions
    } for c in dev_commits])

    if not dev_commit_df.empty:
        total_add = dev_commit_df["Additions"].sum()
        total_del = dev_commit_df["Deletions"].sum()
        total_churn = dev_commit_df["Churn"].sum()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Additions", total_add)
        col2.metric("Total Deletions", total_del)
        col3.metric("Total Churn", total_churn)

        # ✅ Pie chart (reduced size)
        pie_fig, pie_ax = plt.subplots(figsize=(3, 3))  # 🔽 size reduced
        pie_ax.pie([total_add, total_del], labels=["Additions", "Deletions"],
                   autopct="%1.1f%%", colors=["#4CAF50", "#F44336"])
        pie_ax.set_title("Code Contributions Breakdown", fontsize=10)
        st.pyplot(pie_fig)

        # Bar chart for churn per day
        churn_daily = dev_commit_df.groupby("Date")["Churn"].sum()
        bar_fig, bar_ax = plt.subplots(figsize=(8, 3))
        churn_daily.plot(kind="bar", color="#2196F3", ax=bar_ax)
        bar_ax.set_title("Daily Churn")
        bar_ax.set_ylabel("Lines Changed")
        bar_ax.set_xlabel("Date")
        bar_ax.tick_params(axis='x', rotation=45)
        st.pyplot(bar_fig)
    else:
        st.info(f"No commits found for **{selected_dev}**.")

# --- Commits Section ---
st.subheader("📝 Commits Overview")
st.write(f"Total Commits: **{len(commits)}**")

if commits:
    commit_df = pd.DataFrame([{
        "SHA": c.sha,
        "Author": c.author,
        "Date": c.date.strftime("%Y-%m-%d"),
        "Additions": c.additions,
        "Deletions": c.deletions,
        "Churn": c.additions + c.deletions,
        "Files Changed": c.files_changed
    } for c in commits])

    st.dataframe(commit_df)

    # --- Churn Chart ---
    st.subheader("📈 Weekly Churn Forecast")
    churn_by_day = commit_df.groupby("Date")["Churn"].sum().asfreq("D", fill_value=0)

    if len(churn_by_day) > 3:
        model = ExponentialSmoothing(churn_by_day, trend="add", seasonal=None).fit()
        forecast = model.forecast(7)

        fig, ax = plt.subplots(figsize=(8, 3))
        churn_by_day.plot(label="Historical", ax=ax)
        forecast.plot(label="Forecast", ax=ax)
        ax.set_title("Churn Forecast")
        ax.set_ylabel("Lines Changed")
        ax.legend()
        st.pyplot(fig)

# --- PRs Section ---
st.subheader("🔀 Pull Requests Overview")
st.write(f"Total PRs: **{len(prs)}**")

if prs:
    pr_df = pd.DataFrame([{
        "Number": pr.number,
        "Author": pr.author,
        "Created": pr.created_at.strftime("%Y-%m-%d"),
        "Closed": pr.closed_at.strftime("%Y-%m-%d") if pr.closed_at else None,
        "State": pr.state,
        "Reviewers": ", ".join(pr.reviewers) if pr.reviewers else "-",
        "Cycle Time (hrs)": round((pr.closed_at - pr.created_at).total_seconds() / 3600, 2)
            if pr.closed_at else None
    } for pr in prs])

    st.dataframe(pr_df)

    # --- Cycle Time Forecast ---
    pr_df = pr_df.dropna(subset=["Cycle Time (hrs)"])
    if not pr_df.empty:
        cycle_series = pr_df.groupby("Created")["Cycle Time (hrs)"].mean().asfreq("D", fill_value=0)

        if len(cycle_series) > 3:
            model = ExponentialSmoothing(cycle_series, trend="add", seasonal=None).fit()
            forecast = model.forecast(7)

            fig, ax = plt.subplots(figsize=(7, 3))
            cycle_series.plot(label="Historical", ax=ax)
            forecast.plot(label="Forecast", ax=ax)
            ax.set_title("Cycle Time Forecast")
            ax.set_ylabel("Hours")
            ax.legend()
            st.pyplot(fig)

# --- Code Review Influence Map ---
st.subheader("🧠 Code Review Influence Map")

G = nx.DiGraph()
for pr in prs:
    author = pr.author
    for reviewer in pr.reviewers:
        if reviewer != author:
            G.add_edge(reviewer, author)

if G.number_of_edges() > 0:
    fig, ax = plt.subplots(figsize=(7, 3))  # Smaller graph
    pos = nx.spring_layout(G, seed=42)

    # Dynamic node size based on degree
    degrees = dict(G.degree())
    node_sizes = [500 + degrees[n] * 200 for n in G.nodes()]

    # Draw nodes with color map
    nx.draw_networkx_nodes(
        G, pos,
        node_size=node_sizes,
        node_color=range(len(G.nodes())),
        cmap=plt.cm.viridis,
        alpha=0.9,
        ax=ax
    )

    # Draw edges
    nx.draw_networkx_edges(
        G, pos,
        arrowstyle='-|>',
        arrowsize=15,
        edge_color='gray',
        width=1.5,
        ax=ax
    )

    # Draw labels
    nx.draw_networkx_labels(
        G, pos,
        font_size=9,
        font_color='black',
        font_weight='bold',
        ax=ax
    )

    plt.title("Code Review Influence Map", fontsize=12)
    plt.axis("off")
    plt.tight_layout()
    st.pyplot(fig)
else:
    st.info("No review relationships found to plot.")

# --- Footer ---
st.markdown("---")
st.markdown("🔧 Built with ❤️ by Faazil")
