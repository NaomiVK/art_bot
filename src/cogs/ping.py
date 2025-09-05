import discord
from discord.ext import commands

class Ping(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.slash_command(description="Check if the bot is alive")
    async def ping(self, ctx: discord.ApplicationContext):
        await ctx.respond("Pong! 🏓")

def setup(bot: commands.Bot):
    bot.add_cog(Ping(bot))
