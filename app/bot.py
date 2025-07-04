import discord
from discord.ext import commands,tasks
import datetime
import asyncio
from workflow import build_flow  #LangGraph pipeline

import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID=1000349478613680150

intents = discord.Intents.default()
intents.message_content = True  # Required for message reading
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    friday_report.start()

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
@tasks.loop(hours=1)
async def friday_report():
    now = datetime.datetime.now()
    # Friday = weekday 4, Hour = 9
    if now.weekday() == 4 and now.hour == 9 :
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            await channel.send("📆 It's Friday! Generating your automatic weekly dev report...")
            try:
                result = build_flow(return_result=True)
                summary = result.get("summary", "No summary found.")
                pr_insights = result.get("pr_report", [])
                embed = discord.Embed(
                    title="🧠 Friday Auto Dev Report",
                    description=summary,
                    color=0x00ccff
                )
                await channel.send(embed=embed)
            except Exception as e:
                await channel.send(f"❌ Auto-report failed:\n```{str(e)}```")

bot.run(DISCORD_TOKEN)
