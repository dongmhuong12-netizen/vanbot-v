# main.py
import os
import asyncio
import discord
from discord.ext import commands, tasks
from aiohttp import web
from motor.motor_asyncio import AsyncIOMotorClient
import time

# ==========================================
# [GIẢI PHÁP TỐI THƯỢNG] TỰ CẠY FILE .ENV
# ==========================================
basedir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(basedir, '.env')

_TOKEN = None
_MONGO_URI = None

if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if line.startswith("TOKEN="):
                _TOKEN = line.split("=", 1)[1].strip(' "\'')
            elif line.startswith("MONGO_URI="):
                _MONGO_URI = line.split("=", 1)[1].strip(' "\'')

if _TOKEN: os.environ["TOKEN"] = _TOKEN
if _MONGO_URI: os.environ["MONGO_URI"] = _MONGO_URI
# ==========================================

TOKEN = os.getenv("TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

class JinBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents, help_command=None, status=discord.Status.idle)
        
        # Tư duy IT: Khởi tạo sẵn thuộc tính để tránh AttributeError khi hệ thống chưa boot xong DB
        self.db_client = None
        self.db = None
        self.status_index = 0

    async def setup_hook(self):
        # 1. Kết nối MongoDB Async
        self.db_client = AsyncIOMotorClient(MONGO_URI)
        self.db = self.db_client.Jin_Ultimate_Database
        
        # 2. Nạp các module hệ thống (Đã bổ sung cogs.warn_setup)
        exts = ['cogs.status', 'cogs.antispam', 'cogs.antispam_config', 'cogs.warn_setup', 'cogs.dev_emojis', 'cogs.antimarket']
        for ext in exts:
            try:
                await self.load_extension(ext)
                print(f"✅ Đã nạp: {ext}")
            except Exception as e:
                print(f"❌ Lỗi nạp {ext}: {e}")

        # 3. Đăng ký Persistent View cho hệ thống Warn (Giữ nút bấm sống vĩnh viễn sau khi restart)
        try:
            from cogs.warn_setup import WarnSetupView
            self.add_view(WarnSetupView(self))
            print("👁️ Đã đăng ký Persistent View cho Warn Setup thành công.")
        except Exception as e:
            print(f"⚠️ Lỗi đăng ký Persistent View: {e}")

    async def on_ready(self):
        print(f"🚀 {self.user.name} đã sẵn sàng trừng phạt.")
        await self.tree.sync()
        
        # Chạy task quét rác 5p/lần
        if not self.decay_cleaner.is_running():
            self.decay_cleaner.start()
            
        # Khởi động vòng lặp trạng thái
        if not self.rotate_status.is_running():
            self.rotate_status.start()

    @tasks.loop(seconds=30)
    async def rotate_status(self):
        """Hệ thống xoay vòng trạng thái tối ưu cho Multi-server"""
        try:
            statuses = ["antispam", "jin system", "hệ thống an ninh"]
            current_text = statuses[self.status_index % len(statuses)]
            self.status_index += 1
            
            activity = discord.CustomActivity(name=current_text)
            await self.change_presence(status=discord.Status.dnd, activity=activity)
        except Exception as e:
            print(f"[STATUS ERROR] {e}", flush=True)

    @rotate_status.before_loop
    async def before_rotate_status(self):
        await self.wait_until_ready()

    @tasks.loop(minutes=5.0)
    async def decay_cleaner(self):
        """Hệ thống tự động dọn dẹp Database (Tư duy IT tối ưu tài nguyên)"""
        if self.db is None: 
            return
            
        now = int(time.time())
        try:
            res = await self.db.discipline_records.delete_many({"reset_at": {"$lt": now, "$ne": 0}})
            if res.deleted_count > 0: 
                print(f"🧹 Đã xóa {res.deleted_count} án phạt hết hạn.")
        except Exception as e: 
            print(f"⚠️ Lỗi Cleaner: {e}")

# --- WEB SERVER KEEPALIVE CHO RENDER ---
async def handle(r): 
    return web.Response(text="Jin Anti-Spam is Live!")

async def main():
    bot = JinBot()
    app = web.Application()
    app.add_routes([web.get("/", handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", 10005).start()
    
    try:
        async with bot: 
            await bot.start(TOKEN)
    finally:
        # Giải phóng Port an toàn khi bot restart/crash trên Render
        print("🛑 Đang đóng Web Server và giải phóng tài nguyên...")
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
