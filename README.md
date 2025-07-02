\documentclass{article}
\usepackage{geometry}
\geometry{margin=1in}
\usepackage{hyperref}
\usepackage{listings}
\usepackage{color}

\title{Fika AI Engineering Insights Bot Documentation}
\author{Pulkit Arora}
\date{\today}

\begin{document}

\maketitle

\section*{Overview}

This project implements a Discord bot delivering AI-powered, DORA-aligned engineering insights, as required for the FIKA AI Research MVP challenge. The bot processes commit and PR data through a LangChain-inspired agent pipeline, generates metrics, produces visualizations, and posts results to Discord on command.

\section*{Features}

\begin{itemize}
    \item \textbf{Agent Architecture}:
    \begin{itemize}
        \item DataHarvester: fetches commit and PR data.
        \item DiffAnalyst: calculates metrics, churn, and detects churn spikes.
        \item InsightNarrator: generates DORA-aligned AI insights.
    \end{itemize}
    \item Seed script with fake GitHub events for instant evaluation.
    \item Discord bot slash command \texttt{/devreport}:
    \begin{itemize}
        \item Posts AI-generated summaries.
        \item Attaches PNG charts of commits vs PRs and churn per author.
    \end{itemize}
    \item One-command bootstrap: \texttt{./run.sh}.
\end{itemize}

\section*{Architecture Diagram}

\begin{verbatim}
[Seed Script] → [SQLite DB]
      ↓              ↓
[DataHarvester] → [DiffAnalyst] → [InsightNarrator]
                                 ↓
                          [Discord Bot]
\end{verbatim}

\section*{Requirements}

\begin{itemize}
    \item Python 3.10+
    \item Discord server with permissions to add bots
\end{itemize}

\section*{Quick Start}

\begin{enumerate}
    \item Clone your fork:
    \begin{lstlisting}[language=bash]
git clone https://github.com/YOUR_USERNAME/fika-ai-engineering-insights-bot.git
cd fika-ai-engineering-insights-bot
    \end{lstlisting}

    \item Create virtual environment and install requirements:
    \begin{lstlisting}[language=bash]
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
    \end{lstlisting}

    \item Add environment variables to \texttt{.env}:
    \begin{lstlisting}
export DISCORD_BOT_TOKEN="your-bot-token-here"
export DISCORD_GUILD_ID="your-server-id-here"
    \end{lstlisting}

    \item Load your environment:
    \begin{lstlisting}[language=bash]
source .env
    \end{lstlisting}

    \item Bootstrap the system:
    \begin{lstlisting}[language=bash]
./run.sh
    \end{lstlisting}
\end{enumerate}

\section*{Discord Bot Setup}

\begin{enumerate}
    \item Visit the \href{https://discord.com/developers/applications}{Discord Developer Portal}.
    \item Create a new application and add a Bot.
    \item Copy the bot token.
    \item Under OAuth2 → URL Generator:
    \begin{itemize}
        \item Scopes: \texttt{bot}, \texttt{applications.commands}
        \item Permissions: Send Messages, Use Slash Commands
    \end{itemize}
    \item Generate the OAuth2 invite URL and add the bot to your server.
\end{enumerate}

\section*{Slash Command Usage}

Type \texttt{/devreport} in your Discord server:
\begin{itemize}
    \item The bot will generate AI insights.
    \item The bot will post narrative summaries along with commit and churn charts.
\end{itemize}

\section*{Project Structure}

\begin{verbatim}
.
├── agents/
│   ├── harvester.py
│   ├── analyst.py
│   └── narrator.py
├── bot/
│   └── main.py
├── reports/
│   └── plot.py
├── scripts/
│   └── seed_fake_data.py
├── pipeline.py
├── run.sh
└── README.md
\end{verbatim}

\section*{Demo}

Record a GIF or Loom video demonstrating:
\begin{itemize}
    \item Bot startup
    \item Typing \texttt{/devreport} in Discord
    \item Bot's narrative and charts response
\end{itemize}

\section*{License}

This MVP code is provided as part of the FIKA AI Research challenge submission and intended for evaluation only.

\end{document}
