import os
import logging
import discord
from discord.ext import commands

# Basic logging so we can see what's happening on Railway
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is not set. Provide it via environment variable.")

# Intents: for slash-commands we don't need message content
intents = discord.Intents.default()

# Use commands.Bot. We'll register slash cmds via cogs.
bot = commands.Bot(intents=intents, command_prefix="!")

# Optional: during development, restrict /command registration to certain guilds for instant updates
_guild_ids_env = os.getenv("GUILD_IDS", "").strip()
GUILD_IDS = [int(x) for x in _guild_ids_env.split(",") if x.strip().isdigit()]

@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    logging.info("Bot is ready. Slash commands will appear shortly.")

# Load cogs
INITIAL_EXTENSIONS = [
    "cogs.ping",
    "cogs.art_style",
]

for ext in INITIAL_EXTENSIONS:
    try:
        bot.load_extension(ext)
        logging.info(f"Loaded extension: {ext}")
    except Exception as e:
        logging.exception(f"Failed to load extension {ext}: {e}")

# A helper sync command (owner-only) to force slash command sync if needed
@bot.command(name="sync")
@commands.is_owner()
async def sync(ctx: commands.Context):
    try:
        if GUILD_IDS:
            synced = await bot.tree.sync(guild=discord.Object(id=GUILD_IDS[0]))
        else:
            synced = await bot.tree.sync()
        await ctx.send(f"Synced {len(synced)} commands ✅")
    except Exception as e:
        logging.exception("Sync failed")
        await ctx.send(f"Sync failed: {e}")

# Start the bot
bot.run(TOKEN)
