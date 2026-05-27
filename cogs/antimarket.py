# cogs/antimarket.py
import discord
from discord import app_commands
from discord.ext import commands, tasks
import time
from collections import defaultdict

from constants import DEFAULT_CONFIG
from utils.time_converter import parse_duration, format_seconds

class AntiMarket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Cache lưu vết: self.join_cache[guild_id][user_id] = timestamp
        self.join_cache = defaultdict(dict)
        self.market_cleaner.start()

    def cog_unload(self):
        self.market_cleaner.cancel()

    async def get_guild_config(self, guild_id: int) -> dict:
        """Lazy Loading: Đọc cấu hình từ bộ nhớ RAM hoặc DB"""
        antispam_cog = self.bot.get_cog("AntiSpam")
        if antispam_cog and guild_id in antispam_cog.config_cache:
            return antispam_cog.config_cache[guild_id]
            
        try:
            doc = await self.bot.db.server_settings.find_one({"guild_id": guild_id})
            config = {**DEFAULT_CONFIG, **(doc or {})}
            if antispam_cog:
                antispam_cog.config_cache[guild_id] = config
            return config
        except Exception:
            return DEFAULT_CONFIG

    async def _sync_cache_to_system(self, guild_id: int, key: str, value):
        """Đồng bộ nóng cấu hình mới lên tổng bộ RAM hệ thống"""
        antispam_cog = self.bot.get_cog("AntiSpam")
        if antispam_cog:
            if guild_id not in antispam_cog.config_cache:
                antispam_cog.config_cache[guild_id] = {**DEFAULT_CONFIG}
            antispam_cog.config_cache[guild_id][key] = value

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.bot: return
        self.join_cache[member.guild.id][member.id] = time.time()

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if member.bot: return
        
        guild = member.guild
        gid, uid = guild.id, member.id
        now = time.time()
        
        config = await self.get_guild_config(gid)
        if not config.get("anti_market_active"): return

        # Lấy mốc thời gian vào server
        join_time = self.join_cache[gid].get(uid)
        if not join_time and member.joined_at:
            join_time = member.joined_at.timestamp()

        if not join_time: return

        # Tính toán thời gian trụ lại
        elapsed_seconds = now - join_time
        limit_seconds = parse_duration(config.get("anti_market_limit", "10m"))

        # Kích hoạt thiết quân luật nếu out dưới ngưỡng cấu hình
        if elapsed_seconds < limit_seconds:
            try:
                # Thực thi Ban từ xa thông qua Object ID
                await guild.ban(discord.Object(id=uid), reason=f"Jin Anti-Market: Out quá nhanh ({round(elapsed_seconds)}s)")
                
                # --- EMBED THÔNG BÁO TỐI GIẢN (MINIMALIST) ---
                embed = discord.Embed(
                    title="🔨 Anti-Market Banned",
                    description=f"Đã xử lý trục xuất đối tượng vào ra server quá nhanh.",
                    color=0x010101,
                    timestamp=discord.utils.utcnow()
                )
                embed.add_field(name="User Name", value=f"{member.name}", inline=True)
                embed.add_field(name="User ID", value=f"`{uid}`", inline=True)
                embed.add_field(name="Thời gian tồn tại trong server", value=f"`{round(elapsed_seconds)} giây`", inline=False)
                embed.add_field(name="Giới hạn", value=f"`{config.get('anti_market_limit', '10m')}`", inline=False)
                
                # --- ĐIỀU HƯỚNG KÊNH LOG THÔNG MINH ---
                # Kiểm tra kênh setlog tùy chỉnh, nếu không có thì bốc Kênh hệ thống (guild.system_channel)
                log_id = config.get("anti_market_log_channel")
                chan = guild.get_channel(log_id) if log_id else guild.system_channel
                
                if chan: 
                    try: await chan.send(content=f"Band <@{uid}>", embed=embed)
                    except: pass
                
            except discord.Forbidden:
                print(f"❌ Thiếu quyền Ban Members tại Guild {guild.name}")
            except Exception as e:
                print(f"⚠️ Lỗi Anti-Market: {e}")

        # Xóa dấu vết khỏi RAM ngay lập tức
        self.join_cache[gid].pop(uid, None)
        if not self.join_cache[gid]: 
            self.join_cache.pop(gid, None)

    # ==================== HỆ THỐNG LỆNH ĐIỀU KHIỂN ====================

    @app_commands.command(name="antimarket-toggle", description="Bật/Tắt chế độ chặn ra vào server liên tục")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def market_toggle(self, interaction: discord.Interaction, status: bool):
        await interaction.response.defer(ephemeral=True)
        await self.bot.db.server_settings.update_one(
            {"guild_id": interaction.guild.id}, 
            {"$set": {"anti_market_active": status}}, 
            upsert=True
        )
        await self._sync_cache_to_system(interaction.guild.id, "anti_market_active", status)
        await interaction.followup.send(f"🛡️ Cấu hình Anti-Market -> **{status}**")

    @app_commands.command(name="antimarket-limit", description="Thiết lập thời gian giới hạn tối thiểu (Ít nhất 1 phút)")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def market_limit(self, interaction: discord.Interaction, duration: str):
        await interaction.response.defer(ephemeral=True)
        
        seconds = parse_duration(duration)
        # CHỐT CHẶN BẢO VỆ: Dưới 1 phút (60 giây) là đánh chặn, báo lỗi ngay
        if seconds < 60:
            return await interaction.followup.send("❌ Cấu hình thất bại! Thời gian giới hạn tối thiểu phải là **1 phút (1m)**.")

        await self.bot.db.server_settings.update_one(
            {"guild_id": interaction.guild.id}, 
            {"$set": {"anti_market_limit": duration}}, 
            upsert=True
        )
        await self._sync_cache_to_system(interaction.guild.id, "anti_market_limit", duration)
        await interaction.followup.send(f"⚙️ Đã cập nhật giới hạn thời gian: **{format_seconds(seconds)}**.")

    @app_commands.command(name="antimarket-setlog", description="Cài đặt kênh gửi thông báo ban Anti-Market")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def market_setlog(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        await interaction.response.defer(ephemeral=True)
        
        # Nếu truyền channel -> lưu ID channel. Nếu để trống -> xóa cấu hình để dùng lại kênh hệ thống
        channel_id = channel.id if channel else None
        
        await self.bot.db.server_settings.update_one(
            {"guild_id": interaction.guild.id}, 
            {"$set": {"anti_market_log_channel": channel_id}}, 
            upsert=True
        )
        await self._sync_cache_to_system(interaction.guild.id, "anti_market_log_channel", channel_id)
        
        if channel:
            await interaction.followup.send(f"✅ Đã gán kênh nhận thông báo Anti-Market tại: {channel.mention}")
        else:
            await interaction.followup.send(f"🔄 Đã xóa kênh log tùy chỉnh. Thông báo sẽ được gửi về **Kênh hệ thống** của Server.")

    # --- TASK NGẦM DỌN RÁC RAM TRÊN VPS ---
    @tasks.loop(minutes=15.0)
    async def market_cleaner(self):
        """Tự động giải phóng bộ nhớ VPS cho những tài khoản đã ở lại quá 24 giờ"""
        now = time.time()
        for gid in list(self.join_cache.keys()):
            for uid, join_time in list(self.join_cache[gid].items()):
                if now - join_time > 86400:
                    self.join_cache[gid].pop(uid, None)
            if not self.join_cache[gid]:
                self.join_cache.pop(gid, None)

async def setup(bot):
    await bot.add_cog(AntiMarket(bot))
