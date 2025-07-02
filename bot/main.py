import os
import discord
from discord import Object, File
from discord.ext import commands
from pipeline import run_pipeline

# Load environment variables
TOKEN = os.environ["DISCORD_BOT_TOKEN"]
GUILD_ID = int(os.environ["DISCORD_GUILD_ID"])
GUILD = Object(id=GUILD_ID)

# Set up Discord bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"[🚀] Discord bot connected as {bot.user}.")
    # Sync only to your guild for immediate command registration
    synced = await bot.tree.sync(guild=GUILD)
    print(f"[✔] Synced {len(synced)} command(s) to guild {GUILD_ID}.")

# Register the /devreport command specifically for your guild
@bot.tree.command(
    name="devreport",
    description="Get weekly dev report insights",
    guild=GUILD
)
async def dev_report(interaction: discord.Interaction):
    await interaction.response.defer()  # Acknowledge the slash command immediately

    # Run your full pipeline
    result = run_pipeline()

    # Prepare the generated chart images dynamically
    chart_files = [File(path) for path in result.get("charts", [])]

    # Send narrative + all generated charts as a follow-up message
    await interaction.followup.send(
        content=result["narrative"],
        files=chart_files
    )

if __name__ == "__main__":
    if not TOKEN:
        raise EnvironmentError("You must set DISCORD_BOT_TOKEN.")
    bot.run(TOKEN)
