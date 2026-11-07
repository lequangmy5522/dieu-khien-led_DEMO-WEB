import flet as ft
import data

# ==============================================================================
# DESIGN TOKENS: BẢNG MÀU, KHOẢNG CÁCH, BO GÓC, CỠ CHỮ CHUẨN QUẢN TRỊ NỘI BỘ
# ==============================================================================

# Màu nhấn duy nhất (Xanh dương trầm doanh nghiệp)
ACCENT = "#1F5FBF"
ACCENT_DARK = "#3B7DDD"
ACCENT_SUBTLE_LIGHT = "#EBF2FC"
ACCENT_SUBTLE_DARK = "#1E2B3C"

# Bảng màu trung tính - Chế độ Sáng (Light)
BG_LIGHT = "#F4F5F7"
SURFACE_LIGHT = "#FFFFFF"
SURFACE_SUBTLE_LIGHT = "#F8F9FA"
BORDER_LIGHT = "#E2E5EA"
TEXT_PRIMARY_LIGHT = "#1B1F27"
TEXT_SECONDARY_LIGHT = "#6B7280"
ROW_HOVER_LIGHT = "#F1F4F9"

# Bảng màu trung tính - Chế độ Tối (Dark - Xám than, không đen tuyệt đối)
BG_DARK = "#14171C"
SURFACE_DARK = "#1C2027"
SURFACE_SUBTLE_DARK = "#232830"
BORDER_DARK = "#2D333F"
TEXT_PRIMARY_DARK = "#E5E7EB"
TEXT_SECONDARY_DARK = "#9CA3AF"
ROW_HOVER_DARK = "#222730"

# Màu ngữ nghĩa cho trạng thái (chỉ dùng cho chấm tròn trạng thái, lỗi, cảnh báo)
STATUS_ONLINE = "#16A34A"   # Xanh lá: Online, Đang phát, Hoạt động
STATUS_OFFLINE = "#6B7280"  # Xám: Offline, Đã dừng, Đã tắt
STATUS_WARNING = "#D97706"  # Cam: Cảnh báo nhiệt, Tạm dừng
STATUS_DANGER = "#DC2626"   # Đỏ: Sự cố, Gián đoạn, Đã khóa, Lỗi nhập liệu
WHITE = "#FFFFFF"

# Thang khoảng cách cố định (4 / 8 / 12 / 16 / 24 / 32)
SPACE_4 = 4
SPACE_8 = 8
SPACE_12 = 12
SPACE_16 = 16
SPACE_24 = 24
SPACE_32 = 32

# Bo góc & Viền đồng nhất
RADIUS_INPUT = 6
RADIUS_CARD = 8
BORDER_WIDTH = 1
SIDEBAR_INDIC_WIDTH = 4
DOT_SIZE = 8

# Kích thước điều khiển chuẩn
SIDEBAR_WIDTH = 232
HEADER_HEIGHT = 56
BUTTON_HEIGHT = 36
TABLE_HEADING_HEIGHT = 40
TABLE_ROW_HEIGHT = 48

# Kích thước Icon chuẩn (18 - 20 px)
ICON_SM = 18
ICON_MD = 20

# Thang chữ cố định (4 cỡ chữ: 12, 14, 16, 22)
TEXT_12 = 12
TEXT_14 = 14
TEXT_16 = 16
TEXT_22 = 22

# Độ đậm chữ (chỉ dùng 2 mức: bình thường và đậm vừa w600)
WEIGHT_NORMAL = ft.FontWeight.W_400
WEIGHT_SEMI = ft.FontWeight.W_600


# ==============================================================================
# HÀM LẤY MÀU THEO CHẾ ĐỘ SÁNG / TỐI HIỆN TẠI
# ==============================================================================

def is_dark() -> bool:
    """Kiểm tra ứng dụng đang ở chế độ Tối hay Sáng."""
    return data.SYSTEM_SETTINGS.get("theme_mode") == "dark"


def bg_color() -> str:
    return BG_DARK if is_dark() else BG_LIGHT


def surface_color() -> str:
    return SURFACE_DARK if is_dark() else SURFACE_LIGHT


def surface_subtle_color() -> str:
    return SURFACE_SUBTLE_DARK if is_dark() else SURFACE_SUBTLE_LIGHT


def border_color() -> str:
    return BORDER_DARK if is_dark() else BORDER_LIGHT


def text_primary() -> str:
    return TEXT_PRIMARY_DARK if is_dark() else TEXT_PRIMARY_LIGHT


def text_secondary() -> str:
    return TEXT_SECONDARY_DARK if is_dark() else TEXT_SECONDARY_LIGHT


def accent_color() -> str:
    return ACCENT_DARK if is_dark() else ACCENT


def accent_subtle() -> str:
    return ACCENT_SUBTLE_DARK if is_dark() else ACCENT_SUBTLE_LIGHT


def row_hover_color() -> str:
    return ROW_HOVER_DARK if is_dark() else ROW_HOVER_LIGHT
