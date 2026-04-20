from plugins.antispam.limiter import check_spam
from plugins.punishment.mute import mute_user

async def handle_antispam(event, bot):

    if check_spam(event["user_id"], event["guild_id"]):

        try:
            await mute_user(event, duration=None)

            await event["message"].channel.send(
                f"⚠️ {event['message'].author.mention} bị hạn chế do spam."
            )

        except Exception as e:
            print("ANTISPAM ERROR:", repr(e))

        return True

    return False
