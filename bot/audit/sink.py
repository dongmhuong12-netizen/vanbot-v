# bot/audit/sink.py

import os
import json
import threading

_lock = threading.Lock()

def write_log(payload: dict):

    guild_id = payload["guild_id"]

    path = f"data/audit/{guild_id}.jsonl"

    os.makedirs("data/audit", exist_ok=True)

    line = json.dumps(payload, ensure_ascii=False)

    with _lock:
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
