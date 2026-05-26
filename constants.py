# constants.py 
COLOR_GENERAL = 0x010101   
COLOR_SILENCE = 0x000000   
COLOR_AUDIT = 0x111111     

# Cấu hình mặc định - Tư duy IT: Luôn có phương án dự phòng (Fallback)
# Bổ sung các trường dữ liệu an toàn cho hệ thống Warn, Channel, Whitelist và Anti-Market chuẩn Multi-Guild
DEFAULT_CONFIG = {
    "active": True,
    "check_messages": True,
    "check_links": True,
    "check_mentions": True,
    "max_mentions": 5,
    "max_messages": 7,
    "max_links": 3,
    "punishment_duration": "28d", # Thiết quân luật kịch trần 28 ngày cho Anti-Spam chống Raid/Leaked Token
    "silence_channel": None,      # Fallback trống cho kênh thông báo cộng đồng
    "audit_log_channel": None,    # Fallback trống cho kênh lưu log Admin chung
    "whitelist_users": [],        # Chống lỗi KeyError khi module Whitelist quét RAM
    "whitelist_roles": [],        # Chống lỗi KeyError khi module Whitelist quét RAM
    "warn_levels": {},            # Khung chứa an toàn cho bộ 20 Level Warn lũy tiến

    # --- HỆ THỐNG PHÒNG VỆ ANTI-MARKET (NEW) ---
    "anti_market_active": False,        # Mặc định tắt, Admin chủ động kích hoạt khi cần thiết
    "anti_market_limit": "10m",         # Ngưỡng thời gian ở lại tối thiểu mặc định (Tự nhảy số khi bật)
    "anti_market_log_channel": None    # Fallback trống để tự động mượn System Channel của Discord làm Log
}
