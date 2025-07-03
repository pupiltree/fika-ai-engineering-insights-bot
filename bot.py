import discord
from discord.ext import commands
import asyncio
from workflow import build_flow  #LangGraph pipeline

import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True  # Required for message reading
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command(name="devreport")
async def dev_report(ctx):
    await ctx.send("📊 Generating your weekly engineering insights...")

    try:
        result = build_flow(return_result=True)  # Must return a dict

        summary = result.get("summary", "No summary found.")
        pr_insights=result.get("pr_insights","No PRs found")
        embed = discord.Embed(
            title="Weekly Report",
            description=summary,
            color=0x00ff99,

        )
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f" Error while generating report:\n```{str(e)}```")

bot.run(DISCORD_TOKEN)
