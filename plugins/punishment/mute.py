async def mute_user(event, duration=None):

    member = event["message"].author

    try:
        await member.edit(timed_out_until=None)

    except Exception as e:
        print("MUTE ERROR:", repr(e))
