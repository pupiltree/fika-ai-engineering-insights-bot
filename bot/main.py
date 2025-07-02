import os
import discord
from discord import Object, File
from discord.ext import commands
from pipeline import run_pipeline
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

# Load environment variables
TOKEN = os.environ["DISCORD_BOT_TOKEN"]
GUILD_ID = int(os.environ["DISCORD_GUILD_ID"])
CHANNEL_ID = int(os.environ["DISCORD_CHANNEL_ID"])  # Where weekly digests will be posted
GUILD = Object(id=GUILD_ID)

# Set up Discord bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Set up scheduler
scheduler = AsyncIOScheduler()

@bot.event
async def on_ready():
    print(f"[🚀] Discord bot connected as {bot.user}.")
    # Sync slash commands to your guild
    synced = await bot.tree.sync(guild=GUILD)
    print(f"[✔] Synced {len(synced)} command(s) to guild {GUILD_ID}.")
    # Schedule the weekly digest every Monday at 09:00
    scheduler.add_job(send_scheduled_digest, "cron", day_of_week="mon", hour=9, minute=0)
    scheduler.start()
    print("[⏰] Scheduled weekly digest for Mondays at 09:00.")

@bot.tree.command(
    name="devreport",
    description="Get weekly dev report insights",
    guild=GUILD
)
async def dev_report(interaction: discord.Interaction):
    await interaction.response.defer()
    result = run_pipeline()
    chart_files = [File(path) for path in result.get("charts", [])]
    await interaction.followup.send(
        content=result["narrative"],
        files=chart_files
    )

async def send_scheduled_digest():
    print(f"[⏰] Running scheduled digest at {datetime.now().isoformat()}")
    channel = bot.get_channel(CHANNEL_ID) or await bot.fetch_channel(CHANNEL_ID)
    result = run_pipeline()
    chart_files = [File(path) for path in result.get("charts", [])]
    await channel.send(
        content=f"📅 **Weekly Automated Digest**\n\n{result['narrative']}",
        files=chart_files
    )

if __name__ == "__main__":
    if not TOKEN:
        raise EnvironmentError("You must set DISCORD_BOT_TOKEN.")
    if not os.environ.get("DISCORD_CHANNEL_ID"):
        raise EnvironmentError("You must set DISCORD_CHANNEL_ID for scheduled digests.")
    bot.run(TOKEN)
