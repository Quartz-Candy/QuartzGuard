from utils.logger import DiscordLogger
from discord.ext import commands
import discord
import os
import asyncio
import sys

logger = DiscordLogger("Main")

try:
    with open("TOKEN", "r", encoding="UTF-8") as token_file:
        TOKEN = token_file.readline().strip()
except FileNotFoundError:
    logger.write("Critical", "Token file not found!")
    sys.exit(1)
except Exception as e:
    logger.write("Critical", f"Error reading token! {e}")
    sys.exit(1)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="q.", intents=intents, help_command=None)


# If only loading two files, delete the __pycache__ folder and it loads all cogs
async def load_extensions():
    for filename in os.listdir("cogs"):
        if filename.endswith(".py"):
            ext = f"cogs.{filename[:-3]}"
            try:
                logger.write("info", f"Loading extension: {ext}")
                await bot.load_extension(ext)
            except Exception as e:
                logger.write("error", f"Failed to load {ext}: {e}")


@bot.event
async def on_ready():
    logger.write("info", f"Logged in as {bot.user}")
    await load_extensions()


@bot.command()
@commands.is_owner()
async def sanity(ctx):
    await ctx.send("✅")


async def main():
    try:
        await bot.start(TOKEN)
    except KeyboardInterrupt:
        logger.write("info", "Keyboard interrupt received. Shutting down...")
        await bot.close()
    except Exception as e:
        logger.write("Critical", f"Bot crashed: {e}")
        await bot.close()
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.write("info", "Bot stopped by user.")
        sys.exit(0)
