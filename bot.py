import discord
from discord.ext import commands
import matplotlib.pyplot as plt
import sqlite3
import io
import datetime
import json
import os

from discord import app_commands


from dotenv import load_dotenv
from main import graph  # Import your LangGraph pipeline

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not DISCORD_TOKEN:
    raise ValueError("Missing DISCORD_BOT_TOKEN in .env")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree  # Needed to register slash commands

@bot.event
async def on_ready():
    await tree.sync()
    print(f"🤖 Bot is online as {bot.user}")

@tree.command(name="dev_report", description="Show this week's dev performance report")
async def dev_report(interaction: discord.Interaction):
    try:
        # Connect to SQLite
        conn = sqlite3.connect("dev_reports.db")
        cursor = conn.cursor()

        # Get the most recent report
        cursor.execute("SELECT date, summary FROM reports ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()

        if row:
            date, summary = row
            response = f"📅 **{date}**\n\n📋 **Weekly Dev Report:**\n{summary}"
        else:
            response = "⚠️ No reports found in the database."

    except Exception as e:
        response = f"❌ Database error: {str(e)}"

    await interaction.response.send_message(response, ephemeral=True)

@tree.command(name="dev_chart", description="📈 Show the weekly churn chart from the latest report")
async def dev_chart(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)

    try:
        # 1. Fetch latest churn data from SQLite
        conn = sqlite3.connect("dev_reports.db")
        cursor = conn.cursor()
        row = cursor.execute("SELECT date, churn FROM reports ORDER BY id DESC LIMIT 1").fetchone()
        conn.close()

        if not row:
            await interaction.followup.send("No report data found.")
            return

        date, churn_json = row
        churn = json.loads(churn_json)

        # 2. Create matplotlib chart
        days = [f"Day {i+1}" for i in range(len(churn))]
        fig, ax = plt.subplots()
        ax.plot(days, churn, marker='o', color='blue')
        ax.set_title(f"Code Churn - Week of {date}")
        ax.set_ylabel("Lines Changed")
        ax.set_xlabel("Day")
        ax.grid(True)

        ax.set_facecolor("#f9f9f9")
        ax.spines["top"].set_visible(False)

        ax.axhline(200, color="red", linestyle="--")


        ax.text(0.5,210 , "Risky threshold", color= 'red', fontsize=10 ,ha='center')




        # 3. Save plot to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plt.close()

        # 4. Send image to Discord
        file = discord.File(fp=buf, filename="churn_chart.png")
        await interaction.followup.send(content="📊 Here’s the weekly code churn chart:", file=file)

    except Exception as e:
        await interaction.followup.send(f"Error: {e}")

bot.run(DISCORD_TOKEN)
