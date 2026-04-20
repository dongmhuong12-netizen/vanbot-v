import os
import time
import sys
import discord

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise RuntimeError("Missing TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

class MyBot(discord.Client):
    async def on_ready(self):
        print(f"BOT ONLINE: {self.user} | ID: {self.user.id}")

    async def on_message(self, message):
        # test bot sống
        if message.author.bot:
            return

        if message.content == "!ping":
            await message.channel.send("pong")

def run_bot():
    while True:
        try:
            bot = MyBot(intents=intents)
            bot.run(TOKEN)

        except Exception as e:
            print("BOT CRASHED:", repr(e))
            time.sleep(60)
            continue


if __name__ == "__main__":
    run_bot()
