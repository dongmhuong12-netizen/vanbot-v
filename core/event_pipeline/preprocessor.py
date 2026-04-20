def preprocess(message):

    return {
        "guild_id": message.guild.id if message.guild else None,
        "user_id": message.author.id,
        "channel_id": message.channel.id,
        "message": message,
        "content": message.content
    }
