import os
import discord
from discord.ext import commands

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise RuntimeError("Missing TOKEN")


def create_bot():
    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print(f"BOT ONLINE: {bot.user} ({bot.user.id})")

    @bot.event
    async def on_message(message):
        if message.author.bot:
            return

        print(f"[MSG] {message.author}: {message.content}")

        await bot.process_commands(message)

    return bot


def run():
    bot = create_bot()

    try:
        bot.run(TOKEN)
    except Exception as e:
        print("BOT CRASHED:", repr(e))


if __name__ == "__main__":
    run()
