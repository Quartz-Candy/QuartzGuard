import discord
from discord.ext import commands
from datetime import datetime
from utils.logger import DiscordLogger


class UserCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = DiscordLogger("UserCommands")

    async def cog_load(self):
        self.logger.write("info", "loaded")

    async def cog_unload(self):
        self.logger.write("info", "unloaded")

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(
            description="```\nq.help   - shows available commands and what they do\nq.source - get the link to the GitHub repository\n```",
            colour=0x00b0f4,
            timestamp=datetime.now())

        embed.set_author(name="User Commands")
        await ctx.send(embed=embed)

    @commands.command()
    async def source(self, ctx):
        await ctx.send("https://github.com/Quartz-Candy/QuartzGuard")

async def setup(bot):
    await bot.add_cog(UserCommands(bot))