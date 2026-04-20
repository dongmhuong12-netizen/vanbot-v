import os
import time
import threading
import discord
from aiohttp import web

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise RuntimeError("Missing TOKEN")

# =========================
# KEEP-ALIVE WEB SERVER (Render requirement)
# =========================
async def handle(request):
    return web.Response(text="Bot is alive")

def run_web():
    app = web.Application()
    app.add_routes([web.get("/", handle)])
    web.run_app(app, host="0.0.0.0", port=10000)

# =========================
# DISCORD BOT
# =========================
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

class MyBot(discord.Client):
    async def on_ready(self):
        print(f"BOT ONLINE: {self.user} | ID: {self.user.id}")

    async def on_message(self, message):
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

# =========================
# START BOTH
# =========================
if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    run_bot()
