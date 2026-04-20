import asyncio
import time

class Scheduler:

    def __init__(self, state_manager):
        self.state = state_manager
        self.running = False

    async def start(self):

        self.running = True

        while self.running:
            try:
                self.run_decay()
            except Exception as e:
                print("SCHEDULER ERROR:", repr(e))

            await asyncio.sleep(30)

    def stop(self):
        self.running = False

    def run_decay(self):

        now = time.time()

        for key, user in list(self.state.cache.items()):

            reset_at = user.get("reset_at")

            if reset_at and now >= reset_at:

                user["level"] = max(0, user.get("level", 0) - 1)

                if user["level"] == 0:
                    user["reset_at"] = None
                else:
                    user["reset_at"] = now + 300
