# bot/audit/events.py

class AuditEventType:
    WARN = "WARN"
    ANTI_SPAM = "ANTI_SPAM"
    MUTE = "MUTE"
    KICK = "KICK"
    BAN = "BAN"
    UNMUTE = "UNMUTE"
    UNBAN = "UNBAN"

    BOT_ERROR = "BOT_ERROR"
    ADMIN_ACTION = "ADMIN_ACTION"
