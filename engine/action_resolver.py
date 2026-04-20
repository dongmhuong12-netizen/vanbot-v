from plugins.punishment.mute import mute_user
from plugins.punishment.kick import kick_user
from plugins.punishment.ban import ban_user

async def execute_action(action, event):

    msg = event["message"]

    try:

        if action["action"] == "mute":
            await mute_user(event, action.get("duration"))

        elif action["action"] == "kick":
            await kick_user(event)

        elif action["action"] == "ban":
            await ban_user(event)

        elif action["action"] == "warn":
            await msg.channel.send(
                f"⚠️ Cảnh cáo: {msg.author.mention}"
            )

    except Exception as e:
        print("ACTION ERROR:", repr(e))
