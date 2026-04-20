# bot/audit/formatter.py

def format_log(payload: dict):

    data = payload.get("data", {})

    return {
        "time": payload["timestamp"],
        "type": payload["type"],
        "user": data.get("user"),
        "action": data.get("action"),
        "reason": data.get("reason")
    }
