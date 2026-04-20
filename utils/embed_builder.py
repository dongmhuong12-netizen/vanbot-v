import discord

def warn_embed(user, level, reason):

    embed = discord.Embed(
        title="WARNING | CẢNH CÁO",
        description="Hệ thống quản lý kỷ luật",
        color=discord.Color.orange()
    )

    embed.add_field(name="Đối tượng", value=str(user), inline=False)
    embed.add_field(name="Cấp độ", value=str(level), inline=True)
    embed.add_field(name="Lý do", value=reason, inline=False)

    return embed


def antispam_embed(user):

    embed = discord.Embed(
        title="WARNING | CHỐNG SPAM",
        description="Hệ thống phát hiện hành vi spam tự động",
        color=discord.Color.red()
    )

    embed.add_field(name="Đối tượng", value=str(user), inline=False)
    embed.add_field(
        name="Hành vi",
        value="Spam tin nhắn vượt ngưỡng hệ thống",
        inline=False
    )

    return embed
