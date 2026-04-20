class EventContext:
    def __init__(self, message):
        self.guild_id = message.guild.id if message.guild else None
        self.user_id = message.author.id
        self.channel_id = message.channel.id
        self.message = message
        self.content = message.content
        self.author = message.author
