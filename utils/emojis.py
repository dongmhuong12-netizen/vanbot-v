# utils/emojis.py

class Emojis:
    """
    Hệ thống Emoji tập trung cho Jin Bot.
    Tổng kho chứa biến tĩnh (Hardcoded) làm nền tảng cốt lõi.
    """

    # --- NHÓM CUSTOM CORE SYSTEM ---
    HOICHAM  = "<:emoji_50:1498482166949216276>"
    MATTRANG = "<:emoji_44:1494618535870333019>"
    WINGA    = "<:emoji_13:1504997291176759469>"
    WINGB    = "<:emoji_12:1504997233932898404>"
    BUOMA    = "<:emoji_5:1504996011809181716>"
    BUOMB    = "<:emoji_12:1504996695425945670>"
    MOONBL   = "<:emoji_6:1504996061780119703>"
    NO       = "<:emoji_14:1504997399138140171>"
    YIYITIM  = "<:emoji_49:1495407155971625021>"

    # --- HÀM TIỆN ÍCH BIÊN DỊCH VÀ ĐÁNH CHẶN LỖI MÃ NGUỒN ---
    @classmethod
    def get(cls, name: str, fallback: str = "✨") -> str:
        """
        Lấy emoji an toàn từ bộ nhớ RAM (Cả biến tĩnh lẫn biến động cấy từ DB).
        Nếu gõ sai tên hoặc biến chưa được đăng ký, trả về ký tự dự phòng tránh crash code.
        Cách dùng: Emojis.get("HOICHAM") hoặc Emojis.get("NEW_EMOJI")
        """
        return getattr(cls, name.upper(), fallback)
