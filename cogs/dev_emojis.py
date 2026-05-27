# cogs/dev_emojis.py
import discord
from discord import app_commands
from discord.ext import commands
import re
import aiohttp
import os
from utils.emojis import Emojis
from constants import COLOR_GENERAL

# Đọc cấu hình ID Server Kho Chứa từ file môi trường VPS (.env)
VAULT_GUILD_ID = int(os.getenv("VAULT_GUILD_ID", 0))
# Đóng đinh Thực thể tối cao sở hữu hệ thống Jin
OWNER_ID = 1055476307372294155

class DevEmojis(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Đấu nối trực tiếp vào bảng danh mục lưu trữ đám mây của Jin
        self.db_col = self.bot.db.cloud_emojis

    async def cog_load(self):
        """MẠCH CẤY GHÉP CƯỠNG BỨC: Tự động quét DB và nạp đè biến động lên RAM khi bot khởi động trên VPS"""
        try:
            async for item in self.db_col.find({}):
                var_name = item["custom_name"]
                v_id = item["vault_emoji_id"]
                o_name = item["original_name"]
                emoji_string = f"<a:{o_name}:{v_id}>" if item["is_animated"] else f"<:{o_name}:{v_id}>"
                setattr(Emojis, var_name, emoji_string)
            print("[Jin System] Đã nạp thành công danh sách emoji động từ cơ sở dữ liệu vào RAM.", flush=True)
        except Exception as e:
            print(f"⚠️ [Jin System Lỗi] Thất bại khi nạp emoji động từ DB vào RAM: {e}", flush=True)

    # Khởi tạo Group lệnh cha độc quyền kiểm soát: /dev [tên-lệnh]
    dev = app_commands.Group(name="dev", description="Bộ điều khiển tối cao dành cho Nhà phát triển hệ thống Jin")

    async def _has_dev_access(self, interaction: discord.Interaction) -> bool:
        """[DEF MAX] Mạch bảo mật nhị phân đối chiếu quyền hạn Nhà phát triển cốt lõi"""
        if interaction.user.id == OWNER_ID:
            return True
        return await self.bot.is_owner(interaction.user)

    def _get_unauthorized_embed(self) -> discord.Embed:
        """Văn phong hệ thống từ chối truy cập nghiêm khắc của Jin"""
        return discord.Embed(
            title="❌ Truy cập bị từ chối",
            description="Khu vực giới hạn. Lệnh này chỉ dành riêng cho Nhà phát triển tối cao của Jin.",
            color=COLOR_GENERAL
        )

    @dev.command(name="register", description="Đúc tài nguyên ảnh thô vào Server Kho và cấy nóng thành biến hệ thống")
    @app_commands.describe(
        variable_name="Tên biến viết liền muốn gọi trong code (Ví dụ: ALERT, TARGET_OMG)",
        emoji_input="Dán trực tiếp thực thể emoji hoặc nhập chuỗi ID gốc của emoji"
    )
    async def dev_register_cmd(self, interaction: discord.Interaction, variable_name: str, emoji_input: str):
        if not await self._has_dev_access(interaction):
            return await interaction.response.send_message(embed=self._get_unauthorized_embed(), ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        var_name_clean = variable_name.strip().upper()

        # [ATK MAX] Bộ tách lọc cấu trúc đồ họa thô nâng cao bằng Regex
        emoji_match = re.search(r'<(a)?:[A-Za-z0-9_]+:(\d+)>', emoji_input)
        if emoji_match:
            is_animated = bool(emoji_match.group(1))
            emoji_id = emoji_match.group(2)
        else:
            emoji_id = "".join(filter(str.isdigit, emoji_input))
            is_animated = False

        if not emoji_id:
            return await interaction.followup.send(embed=discord.Embed(
                title="⚠️ Lỗi định dạng",
                description="Dữ liệu đầu vào không hợp lệ. Vui lòng dán đúng emoji hoặc mã ID số nguyên thô.",
                color=COLOR_GENERAL
            ))

        # [DEF MAX] Kiểm tra đánh chặn ghi đè từ khóa trùng lặp
        existing = await self.db_col.find_one({"custom_name": var_name_clean})
        if existing:
            return await interaction.followup.send(embed=discord.Embed(
                title="⚠️ Biến đã tồn tại",
                description=f"Từ khóa đặt tên `{var_name_clean}` đã được đăng ký trong hệ thống động.",
                color=COLOR_GENERAL
            ))

        if VAULT_GUILD_ID == 0:
            return await interaction.followup.send(embed=discord.Embed(
                title="❌ Lỗi cấu hình hạ tầng",
                description="Biến môi trường `VAULT_GUILD_ID` chưa được thiết lập chính xác trong file `.env`.",
                color=COLOR_GENERAL
            ))

        ext = "gif" if is_animated else "png"
        cdn_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{ext}"
        
        try:
            # [ATK MAX] Nạp tiêu đề mô phỏng trình duyệt để bypass triệt để bộ lọc Discord CDN
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(cdn_url) as response:
                    if response.status != 200:
                        raise Exception(f"Máy chủ CDN Discord từ chối gói tin (Mã lỗi: {response.status})")
                    img_bytes = await response.read()

            vault_guild = self.bot.get_guild(VAULT_GUILD_ID)
            if not vault_guild:
                raise Exception("Bot không tìm thấy Server Kho Chứa. Hãy kiểm tra lại ID Guild trong file .env")

            # Tạo lệnh đúc thực thể bất tử lên hệ thống hạ tầng server kho
            new_emoji = await vault_guild.create_custom_emoji(
                name=f"jin_{var_name_clean.lower()}",
                image=img_bytes,
                reason=f"Đúc tài nguyên hệ thống bởi Nhà phát triển ID {interaction.user.id}"
            )

            # Đẩy cấu trúc bản ghi thông tin lưu trữ xuống MongoDB đám mây
            data_document = {
                "custom_name": var_name_clean,
                "vault_emoji_id": str(new_emoji.id),
                "original_name": new_emoji.name,
                "is_animated": is_animated
            }
            await self.db_col.insert_one(data_document)

            # CẤY NÓNG RUNTIME: Tiêm trực tiếp thuộc tính vào Class Emojis trên RAM tổng ngay lập tức
            emoji_string = f"<a:{new_emoji.name}:{new_emoji.id}>" if is_animated else f"<:{new_emoji.name}:{new_emoji.id}>"
            setattr(Emojis, var_name_clean, emoji_string)

            await interaction.followup.send(embed=discord.Embed(
                title="✅ Đăng ký tài nguyên thành công",
                description=f"Đã cấy thành công biến động `{var_name_clean}` vào bộ nhớ hệ thống.\n\n"
                            f"• **Thực thể đồ họa:** {emoji_string}\n"
                            f"• **Cú pháp gọi mã nguồn:** `Emojis.{var_name_clean}` hoặc `Emojis.get('{var_name_clean}')`",
                color=COLOR_GENERAL
            ))

        except Exception as e:
            await interaction.followup.send(embed=discord.Embed(
                title="❌ Nghẽn mạch xử lý đúc asset",
                description=f"Tiến trình ngầm gặp sự cố khi tải hoặc đúc tài nguyên: `{str(e)}`",
                color=COLOR_GENERAL
            ))

    @dev.command(name="list", description="Soi chiếu toàn bộ bảng quản lý biến mã nguồn tĩnh và động")
    async def dev_list_cmd(self, interaction: discord.Interaction):
        if not await self._has_dev_access(interaction):
            return await interaction.response.send_message(embed=self._get_unauthorized_embed(), ephemeral=True)

        await interaction.response.defer(ephemeral=True)

        # 1. Thu thập dữ liệu biến động từ MongoDB đám mây
        dynamic_list = []
        dynamic_keys = set()
        async for item in self.db_col.find({}):
            v_id = item["vault_emoji_id"]
            o_name = item["original_name"]
            fmt = f"<a:{o_name}:{v_id}>" if item["is_animated"] else f"<:{o_name}:{v_id}>"
            dynamic_list.append(f"• `{item['custom_name']}` ──> {fmt}")
            dynamic_keys.add(item["custom_name"])

        # 2. Sử dụng thuật toán phản chiếu bóc tách file cứng loại trừ trùng lặp
        hardcoded_list = []
        for attr, val in Emojis.__dict__.items():
            if not attr.startswith("__") and isinstance(val, str):
                if attr.upper() not in dynamic_keys:
                    hardcoded_list.append(f"• `{attr}` ──> {val}")

        # 3. Dựng Dashboard kiểm soát quy chuẩn màu sắc Jin
        embed = discord.Embed(
            title="🖥️ BẢNG QUẢN LÝ BIẾN THỐNG NHẤT",
            color=COLOR_GENERAL,
            timestamp=discord.utils.utcnow()
        )
        
        # [DEF MAX] Cắt chuỗi thông minh chống lỗi tràn 1024 ký tự của Discord Field
        h_text = "\n".join(hardcoded_list) if hardcoded_list else "Trống."
        if len(h_text) > 1024: 
            h_text = h_text[:1000] + "\n...và một số biến tĩnh hệ thống khác"
        embed.add_field(name="[ CORE SYSTEM - HARDCODED IN FILE ]", value=h_text, inline=False)

        d_text = "\n".join(dynamic_list) if dynamic_list else "Chưa có biến động nào được cấu hình."
        if len(d_text) > 1024: 
            d_text = d_text[:1000] + "\n...và một số biến động mở rộng khác"
        embed.add_field(name="[ EXTENDED SYSTEM - DYNAMIC REGISTRY ]", value=d_text, inline=False)

        embed.set_footer(text="Hệ thống quản lý tài nguyên Jin")
        await interaction.followup.send(embed=embed)

    @dev.command(name="delete", description="Xóa sổ hoàn toàn biến động khỏi Database, Server Kho và bộ nhớ RAM")
    @app_commands.describe(variable_name="Tên biến động sếp muốn trục xuất khỏi Jin (Ví dụ: ALERT)")
    async def dev_delete_cmd(self, interaction: discord.Interaction, variable_name: str):
        if not await self._has_dev_access(interaction):
            return await interaction.response.send_message(embed=self._get_unauthorized_embed(), ephemeral=True)

        await interaction.response.defer(ephemeral=True)
        var_name_clean = variable_name.strip().upper()

        target_emoji = await self.db_col.find_one({"custom_name": var_name_clean})
        if not target_emoji:
            return await interaction.followup.send(embed=discord.Embed(
                title="⚠️ Không tìm thấy mục tiêu",
                description=f"Biến động `{var_name_clean}` không tồn tại trong cơ sở dữ liệu.",
                color=COLOR_GENERAL
            ))

        errors_log = []
        vault_emoji_id = target_emoji["vault_emoji_id"]

        # TẦNG 1: Xóa thực thể đồ họa vật lý thu hồi slot trống trên Server Kho
        try:
            vault_guild = self.bot.get_guild(VAULT_GUILD_ID)
            if vault_guild:
                emoji_obj = discord.utils.get(vault_guild.emojis, id=int(vault_emoji_id))
                if not emoji_obj:
                    try: emoji_obj = await vault_guild.fetch_emoji(int(vault_emoji_id))
                    except: emoji_obj = None
                
                if emoji_obj:
                    await emoji_obj.delete(reason=f"Xóa bỏ tài nguyên tự động qua lệnh /dev delete bởi Dev: {interaction.user.id}")
                else:
                    errors_log.append("Thực thể vật lý không còn tồn tại trên Server Kho.")
            else:
                errors_log.append("Không thể tiếp cận Server Kho Chứa để giải phóng slot.")
        except Exception as e:
            errors_log.append(f"Mạch gỡ thực thể vấp phải lỗi hệ thống: {str(e)}")

        # TẦNG 2: Xóa bỏ hoàn toàn dữ liệu bản ghi khỏi MongoDB đám mây
        await self.db_col.delete_one({"custom_name": var_name_clean})

        # TẦNG 3: Trục xuất thuộc tính khỏi RAM của Class Emojis ngay tại Runtime
        if hasattr(Emojis, var_name_clean):
            delattr(Emojis, var_name_clean)

        desc_msg = f"Đã trục xuất biến động `{var_name_clean}` ra khỏi cơ sở dữ liệu và RAM hệ thống thành công!"
        if errors_log:
            desc_msg += f"\n\n⚠️ **Nhật ký sự cố hạ tầng dọn kho:**\n- " + "\n- ".join(errors_log)

        await interaction.followup.send(embed=discord.Embed(
            title="🗑️ Trục xuất tài nguyên thành công",
            description=desc_msg,
            color=COLOR_GENERAL
        ))

async def setup(bot: commands.Bot):
    await bot.add_cog(DevEmojis(bot))
