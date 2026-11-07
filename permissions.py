# ==============================================================================
# CƠ CHẾ PHÂN QUYỀN THEO VAI TRÒ (RBAC) - 3 VAI TRÒ QUẢN TRỊ NỘI BỘ
# ==============================================================================

# Hằng số tên 3 vai trò trong hệ thống
ROLE_ADMIN = "Quản trị viên"
ROLE_EDITOR = "Biên tập viên"
ROLE_VIEWER = "Người xem"

ALL_ROLES = [ROLE_ADMIN, ROLE_EDITOR, ROLE_VIEWER]

# Thứ tự chuẩn của 8 trang chức năng trên thanh điều hướng
PAGE_KEYS = [
    "dashboard",   # 0: Tổng quan
    "screens",     # 1: Quản lý màn hình LED
    "contents",    # 2: Quản lý nội dung
    "schedules",   # 3: Lịch phát nội dung
    "control",     # 4: Điều khiển màn hình
    "monitoring",  # 5: Giám sát thiết bị
    "users",       # 6: Quản lý người dùng
    "settings",    # 7: Cài đặt hệ thống
]

# Ánh xạ tên hiển thị hoặc chỉ số sang mã trang để tiện tra cứu
PAGE_ALIASES = {
    "0": "dashboard",
    "Tổng quan": "dashboard",
    "1": "screens",
    "Quản lý màn hình LED": "screens",
    "2": "contents",
    "Quản lý nội dung": "contents",
    "3": "schedules",
    "Lịch phát nội dung": "schedules",
    "4": "control",
    "Điều khiển màn hình": "control",
    "Điều khiển màn hình LED": "control",
    "5": "monitoring",
    "Giám sát thiết bị": "monitoring",
    "6": "users",
    "Quản lý người dùng": "users",
    "7": "settings",
    "Cài đặt hệ thống": "settings",
}

# Ma trận phân quyền: vai trò -> trang -> tập hành động được phép
# Ký hiệu hành động chuẩn:
# - "view": xem trang
# - "search", "filter", "detail", "preview": tra cứu / xem chi tiết / xem trước
# - "add", "edit", "delete": thêm / sửa / xóa
# - "toggle": bật/tắt trạng thái lịch phát
# - "power": bật nguồn / tắt nguồn / khởi động lại màn hình LED
# - "playback", "change_content", "brightness", "volume": điều khiển phát & thông số
# - "refresh": làm mới số liệu giám sát
# - "lock": khóa/mở khóa tài khoản người dùng
# - "edit_profile", "change_password", "preferences", "logout": thao tác cài đặt cá nhân
PERMISSION_MATRIX: dict[str, dict[str, set[str]]] = {
    ROLE_ADMIN: {
        "dashboard": {"view"},
        "screens": {"view", "search", "filter", "detail", "add", "edit", "delete"},
        "contents": {"view", "preview", "search", "filter", "add", "edit", "delete"},
        "schedules": {"view", "add", "edit", "delete", "toggle"},
        "control": {
            "view",
            "power",
            "playback",
            "change_content",
            "brightness",
            "volume",
            "preview",
        },
        "monitoring": {"view", "filter", "refresh"},
        "users": {"view", "search", "filter", "add", "edit", "delete", "lock"},
        "settings": {
            "view",
            "edit_profile",
            "change_password",
            "preferences",
            "logout",
        },
    },
    ROLE_EDITOR: {
        "dashboard": {"view"},
        "screens": {"view", "search", "filter", "detail"},
        "contents": {"view", "preview", "search", "filter", "add", "edit", "delete"},
        "schedules": {"view", "add", "edit", "delete", "toggle"},
        "control": {
            "view",
            "playback",
            "change_content",
            "brightness",
            "volume",
            "preview",
        },
        "monitoring": {"view", "filter", "refresh"},
        "users": set(),
        "settings": {
            "view",
            "edit_profile",
            "change_password",
            "preferences",
            "logout",
        },
    },
    ROLE_VIEWER: {
        "dashboard": {"view"},
        "screens": {"view", "search", "filter", "detail"},
        "contents": {"view", "preview", "search", "filter"},
        "schedules": {"view"},
        "control": set(),
        "monitoring": {"view", "filter"},
        "users": set(),
        "settings": {
            "view",
            "edit_profile",
            "change_password",
            "preferences",
            "logout",
        },
    },
}


def _normalize_page(page: str | int) -> str:
    """Chuẩn hóa định danh trang về khóa chuẩn trong PAGE_KEYS."""
    key = str(page).strip()
    if key in PAGE_KEYS:
        return key
    return PAGE_ALIASES.get(key, key)


def can(role: str, page: str | int, action: str = "view") -> bool:
    """Kiểm tra vai trò `role` có quyền thực hiện `action` trên `page` hay không."""
    role_perms = PERMISSION_MATRIX.get(role)
    if not role_perms:
        return False
    page_key = _normalize_page(page)
    allowed_actions = role_perms.get(page_key, set())
    return action in allowed_actions


def visible_pages(role: str) -> list[str]:
    """Trả về danh sách các mã trang được phép hiển thị trên menu của `role`."""
    return [page_key for page_key in PAGE_KEYS if can(role, page_key, "view")]
