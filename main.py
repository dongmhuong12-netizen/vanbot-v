import os
import time
import sys
from core.bot import create_bot

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise RuntimeError("Missing TOKEN")

# =========================
# DEPLOY MARKER (chống restart loop Render)
# =========================
print("DEPLOY VERSION: 2026-04-20-STABLE-ANTI_LOOP")

# chống Render restart spam login
BOOT_LOCK = "/tmp/bot.lock"

if os.path.exists(BOOT_LOCK):
    print("BOT BLOCKED: restart loop detected")
    time.sleep(999999)
    sys.exit(0)

with open(BOOT_LOCK, "w") as f:
    f.write(str(time.time()))

# =========================
# BOT RUNNER
# =========================
def run_bot():
    while True:
        try:
            bot = create_bot()

            print("BOT STARTING...")

            bot.run(TOKEN)

        except Exception as e:
            print("BOT CRASHED:", repr(e))

            # nếu crash → đợi lâu để tránh Discord rate limit
            time.sleep(90)

            # restart lại bot instance an toàn
            continue


if __name__ == "__main__":
    run_bot()
