import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from agents import workflow
from visualization import generate_weekly_report_chart
import io

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable not set")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.command()
async def dev_report(ctx):
    # Run the LangGraph workflow
    result = workflow.invoke({})
    # The result contains the final state with all keys
    summary = result.get("summary", "No summary available")
    forecast_summary = result.get("forecast_summary", "")
    influence_summary = result.get("influence_summary", "")
    influence_chart = result.get("influence_chart", None)
    
    # Combine all summaries
    full_summary = f"{summary}\n\n{forecast_summary}\n\n{influence_summary}"
    
    analytics = result  # The entire result is the analytics
    print(analytics)
    
    # Generate weekly report chart
    chart_buf = generate_weekly_report_chart(analytics)
    chart_file = discord.File(fp=chart_buf, filename="weekly_report.png")
    
    # Send main report
    await ctx.send(content=f"**Weekly Engineering Report**\n{full_summary}", file=chart_file)
    
    # Send influence map if available
    if influence_chart:
        influence_file = discord.File(fp=influence_chart, filename="influence_map.png")
        await ctx.send(content="**Code Review Influence Map**", file=influence_file)

if __name__ == '__main__':
    bot.run(TOKEN) 
    print("Bot is running")