from datetime import datetime
import random
from permissions import ROLE_ADMIN, ROLE_EDITOR, ROLE_VIEWER

# ==============================================================================
# DỮ LIỆU GIẢ LẬP CHÂN THỰC CHO HỆ THỐNG QUẢN TRỊ MÀN HÌNH LED
# ==============================================================================

COMPANY_INFO = {
    "name": "Công ty Cổ phần Giải pháp Hiển thị & Truyền thông số VietLED",
    "code": "0108472915",
    "address": "Tầng 8, Tòa nhà TTC, Số 19 Duy Tân, Cầu Giấy, Hà Nội",
    "hotline": "(024) 3795 8821 – Nhánh kỹ thuật: 104",
    "email": "vanhanh@vietled.com.vn",
    "website": "https://cms.vietled.com.vn",
    "version": "v2.4.1-internal (Build 2026.10)",
}

SYSTEM_SETTINGS = {
    "theme_mode": "light",
    "ui_notifications": True,
    "rows_per_page": "10",
    "default_content_view": "table",
}

# Danh sách người dùng: 3 tài khoản demo chính (admin, bientap, xem) + các tài khoản vận hành
USERS_DATA = [
    {
        "id": "USR01",
        "username": "admin",
        "password": "123456",
        "full_name": "Nguyễn Đức Minh",
        "email": "minh.nd@vietled.com.vn",
        "phone": "0904 812 305",
        "role": ROLE_ADMIN,
        "active": True,
        "created_at": "12/01/2025",
    },
    {
        "id": "USR02",
        "username": "bientap",
        "password": "123456",
        "full_name": "Trần Thị Minh Châu",
        "email": "chau.ttm@vietled.com.vn",
        "phone": "0917 209 441",
        "role": ROLE_EDITOR,
        "active": True,
        "created_at": "04/03/2025",
    },
    {
        "id": "USR03",
        "username": "xem",
        "password": "123456",
        "full_name": "Đỗ Thu Hà",
        "email": "ha.dt@vietled.com.vn",
        "phone": "0972 508 613",
        "role": ROLE_VIEWER,
        "active": True,
        "created_at": "15/01/2026",
    },
    {
        "id": "USR04",
        "username": "kythuat.miennam",
        "password": "123456",
        "full_name": "Phạm Văn Hùng",
        "email": "hung.pv@vietled.com.vn",
        "phone": "0938 114 702",
        "role": ROLE_ADMIN,
        "active": True,
        "created_at": "27/08/2025",
    },
    {
        "id": "USR05",
        "username": "nam.lh",
        "password": "123456",
        "full_name": "Lê Hoàng Nam",
        "email": "nam.lh@vietled.com.vn",
        "phone": "0983 651 920",
        "role": ROLE_EDITOR,
        "active": True,
        "created_at": "19/06/2025",
    },
    {
        "id": "USR06",
        "username": "khanh.vq",
        "password": "123456",
        "full_name": "Vũ Quốc Khánh",
        "email": "khanh.vq@vietled.com.vn",
        "phone": "0966 319 084",
        "role": ROLE_VIEWER,
        "active": False,
        "created_at": "09/04/2026",
    },
]

# Phiên đăng nhập hiện tại dùng chung toàn ứng dụng
CURRENT_USER = USERS_DATA[0].copy()

APP_STATE = {
    "current_user": CURRENT_USER,
}


def set_current_user(user_dict: dict):
    """Cập nhật người dùng đang đăng nhập trong phiên làm việc."""
    CURRENT_USER.clear()
    CURRENT_USER.update(user_dict)
    APP_STATE["current_user"] = CURRENT_USER


def get_current_role() -> str:
    """Lấy vai trò của người dùng đang đăng nhập hiện tại."""
    return CURRENT_USER.get("role", ROLE_VIEWER)


CONTENT_CATEGORIES = ["Quảng cáo", "Thông báo", "Sự kiện", "Giới thiệu"]

CONTENTS_DATA = [
    {
        "id": "CNT01",
        "name": "TVC Khuyến mãi cuối năm - Điện máy Xanh (Bản 30s)",
        "type": "Video",
        "category": "Quảng cáo",
        "format": "MP4",
        "size": "43.7 MB",
        "upload_date": "02/11/2026",
        "description": "Phát tại cụm màn hình mặt tiền khu vực TP.HCM và Biên Hòa.",
    },
    {
        "id": "CNT02",
        "name": "Poster Hội nghị Khách hàng Khu vực Phía Bắc 2026",
        "type": "Hình ảnh",
        "category": "Sự kiện",
        "format": "PNG",
        "size": "4.1 MB",
        "upload_date": "31/10/2026",
        "description": "Khung hình tỷ lệ 16:9 dùng cho màn hình sảnh và hội trường.",
    },
    {
        "id": "CNT03",
        "name": "Thông báo cắt điện bảo trì trạm biến áp Tòa B",
        "type": "Hình ảnh",
        "category": "Thông báo",
        "format": "JPG",
        "size": "1.4 MB",
        "upload_date": "29/10/2026",
        "description": "Hiển thị tại sảnh thang máy tầng G và hầm B1 từ 22h00.",
    },
    {
        "id": "CNT04",
        "name": "Phim giới thiệu năng lực sản xuất Nhà máy Bắc Ninh",
        "type": "Video",
        "category": "Giới thiệu",
        "format": "MP4",
        "size": "118.4 MB",
        "upload_date": "25/10/2026",
        "description": "Video có âm thanh dùng cho sảnh đón tiếp khách đoàn.",
    },
    {
        "id": "CNT05",
        "name": "Banner chương trình ưu đãi lãi suất vay mua nhà Q4",
        "type": "Hình ảnh",
        "category": "Quảng cáo",
        "format": "PNG",
        "size": "5.8 MB",
        "upload_date": "24/10/2026",
        "description": "Áp dụng cho chuỗi màn hình P3/P4 tại các phòng giao dịch.",
    },
    {
        "id": "CNT06",
        "name": "Hướng dẫn phân luồng thoát hiểm và vị trí bình chữa cháy",
        "type": "Video",
        "category": "Thông báo",
        "format": "MP4",
        "size": "57.2 MB",
        "upload_date": "21/10/2026",
        "description": "Phát định kỳ đầu giờ sáng theo yêu cầu của Ban quản lý tòa nhà.",
    },
    {
        "id": "CNT07",
        "name": "Visual nền sân khấu Lễ ký kết đối tác chiến lược",
        "type": "Hình ảnh",
        "category": "Sự kiện",
        "format": "JPG",
        "size": "6.3 MB",
        "upload_date": "18/10/2026",
        "description": "Độ phân giải 3840x2160 px cho màn hình P2 hội trường tầng 5.",
    },
    {
        "id": "CNT08",
        "name": "TVC Mở thẻ thanh toán quốc tế hoàn tiền 5%",
        "type": "Video",
        "category": "Quảng cáo",
        "format": "MP4",
        "size": "36.9 MB",
        "upload_date": "15/10/2026",
        "description": "Spot quảng cáo 15 giây không tiếng cho màn hình ngoài trời.",
    },
    {
        "id": "CNT09",
        "name": "Slide quy tắc an toàn lao động tại xưởng lắp ráp",
        "type": "Hình ảnh",
        "category": "Giới thiệu",
        "format": "PNG",
        "size": "2.9 MB",
        "upload_date": "11/10/2026",
        "description": "Hiển thị cố định tại cổng ra vào KCN Bắc Thăng Long.",
    },
    {
        "id": "CNT10",
        "name": "Video giới thiệu Lễ tổng kết cuối năm 2026",
        "type": "Video",
        "category": "Sự kiện",
        "format": "MOV",
        "size": "79.5 MB",
        "upload_date": "08/10/2026",
        "description": "Phát tại khu vực căn-tin tầng 3 vào khung giờ nghỉ trưa.",
    },
    {
        "id": "CNT11",
        "name": "Sơ đồ hướng dẫn đỗ xe khách vãng lai hầm B1 - B2",
        "type": "Hình ảnh",
        "category": "Thông báo",
        "format": "JPG",
        "size": "920 KB",
        "upload_date": "05/10/2026",
        "description": "Kích thước ngang 1280x480 px khớp với bảng LED dốc hầm.",
    },
    {
        "id": "CNT12",
        "name": "Clip kỷ niệm 10 năm thành lập chi nhánh Đà Nẵng",
        "type": "Video",
        "category": "Giới thiệu",
        "format": "MP4",
        "size": "64.1 MB",
        "upload_date": "01/10/2026",
        "description": "Phát nội bộ tại sảnh lễ tân chi nhánh miền Trung.",
    },
]

SCREENS_DATA = [
    {
        "id": "LED01",
        "name": "Màn hình sảnh tòa nhà A",
        "code": "LED-HN-001",
        "location": "Sảnh tầng 1, Số 19 Duy Tân, Cầu Giấy, Hà Nội",
        "size": "P2.5 Indoor, 4.8m x 2.7m",
        "resolution": "1920 x 1080 px",
        "status": "Online",
        "playing_state": "Đang phát",
        "current_content_id": "CNT04",
        "brightness": 78,
        "volume": 45,
        "temperature": 41,
        "uptime": "18 ngày 07 giờ",
        "last_connected": "07/11/2026 11:48",
    },
    {
        "id": "LED02",
        "name": "LED mặt tiền Chi nhánh Biên Hòa",
        "code": "LED-BH-001",
        "location": "248 Phạm Văn Thuận, P. Thống Nhất, TP. Biên Hòa",
        "size": "P4 Outdoor, 8.0m x 4.0m",
        "resolution": "2000 x 1000 px",
        "status": "Online",
        "playing_state": "Đang phát",
        "current_content_id": "CNT01",
        "brightness": 92,
        "volume": 0,
        "temperature": 53,
        "uptime": "9 ngày 14 giờ",
        "last_connected": "07/11/2026 11:49",
    },
    {
        "id": "LED03",
        "name": "Màn hình sảnh chờ thang máy tầng G",
        "code": "LED-HN-002",
        "location": "Cụm thang máy khối văn phòng Tòa A, Hà Nội",
        "size": "P1.86 Indoor, 2.4m x 1.35m",
        "resolution": "1280 x 720 px",
        "status": "Online",
        "playing_state": "Đang phát",
        "current_content_id": "CNT03",
        "brightness": 65,
        "volume": 30,
        "temperature": 38,
        "uptime": "26 ngày 03 giờ",
        "last_connected": "07/11/2026 11:46",
    },
    {
        "id": "LED04",
        "name": "LED sân khấu Phòng hội nghị tầng 5",
        "code": "LED-HN-003",
        "location": "Phòng họp lớn tầng 5, Tòa nhà TTC, Hà Nội",
        "size": "P2.0 Indoor, 7.68m x 4.32m",
        "resolution": "3840 x 2160 px",
        "status": "Online",
        "playing_state": "Tạm dừng",
        "current_content_id": "CNT07",
        "brightness": 70,
        "volume": 65,
        "temperature": 43,
        "uptime": "2 ngày 19 giờ",
        "last_connected": "07/11/2026 11:44",
    },
    {
        "id": "LED05",
        "name": "Bảng LED dốc xuống hầm gửi xe B1",
        "code": "LED-HN-004",
        "location": "Cổng vào hầm B1 phía đường Trần Thái Tông",
        "size": "P3 Outdoor, 3.84m x 1.44m",
        "resolution": "1280 x 480 px",
        "status": "Offline",
        "playing_state": "Đã dừng",
        "current_content_id": "CNT11",
        "brightness": 60,
        "volume": 0,
        "temperature": 31,
        "uptime": "0 ngày 00 giờ",
        "last_connected": "06/11/2026 23:12",
    },
    {
        "id": "LED06",
        "name": "LED trụ quảng cáo Ngã tư Hàng Xanh",
        "code": "LED-SG-001",
        "location": "Vòng xoay Hàng Xanh, Q. Bình Thạnh, TP.HCM",
        "size": "P5 Outdoor, 12.0m x 6.0m",
        "resolution": "2400 x 1200 px",
        "status": "Sự cố",
        "playing_state": "Gián đoạn",
        "current_content_id": "CNT08",
        "brightness": 100,
        "volume": 0,
        "temperature": 67,
        "uptime": "1 ngày 05 giờ",
        "last_connected": "07/11/2026 11:18",
    },
    {
        "id": "LED07",
        "name": "Màn hình PGD Ngân hàng Chi nhánh Quận 3",
        "code": "LED-SG-002",
        "location": "Số 162 Cách Mạng Tháng 8, Quận 3, TP.HCM",
        "size": "P2.5 Indoor, 3.2m x 1.92m",
        "resolution": "1280 x 768 px",
        "status": "Online",
        "playing_state": "Đang phát",
        "current_content_id": "CNT05",
        "brightness": 75,
        "volume": 40,
        "temperature": 42,
        "uptime": "14 ngày 22 giờ",
        "last_connected": "07/11/2026 11:48",
    },
    {
        "id": "LED08",
        "name": "Màn hình sảnh lễ tân Chi nhánh Đà Nẵng",
        "code": "LED-DN-001",
        "location": "Số 84 Nguyễn Văn Linh, Q. Hải Châu, Đà Nẵng",
        "size": "P2.5 Indoor, 4.0m x 2.25m",
        "resolution": "1600 x 900 px",
        "status": "Online",
        "playing_state": "Đang phát",
        "current_content_id": "CNT12",
        "brightness": 80,
        "volume": 55,
        "temperature": 45,
        "uptime": "11 ngày 09 giờ",
        "last_connected": "07/11/2026 11:47",
    },
    {
        "id": "LED09",
        "name": "Màn hình khu ăn uống nhân viên tầng 3",
        "code": "LED-HN-005",
        "location": "Căn-tin tầng 3, Tòa B, Cầu Giấy, Hà Nội",
        "size": "P3 Indoor, 2.88m x 1.62m",
        "resolution": "960 x 540 px",
        "status": "Offline",
        "playing_state": "Đã dừng",
        "current_content_id": "CNT10",
        "brightness": 55,
        "volume": 35,
        "temperature": 30,
        "uptime": "0 ngày 00 giờ",
        "last_connected": "05/11/2026 17:40",
    },
    {
        "id": "LED10",
        "name": "Bảng thông tin Cổng số 2 KCN Bắc Thăng Long",
        "code": "LED-HN-006",
        "location": "Cổng bảo vệ số 2, KCN Bắc Thăng Long, Đông Anh",
        "size": "P4 Outdoor, 6.4m x 3.2m",
        "resolution": "1600 x 800 px",
        "status": "Sự cố",
        "playing_state": "Cảnh báo nhiệt",
        "current_content_id": "CNT09",
        "brightness": 90,
        "volume": 0,
        "temperature": 63,
        "uptime": "6 ngày 11 giờ",
        "last_connected": "07/11/2026 11:39",
    },
]

_NOW = datetime.now()
_YM = f"{_NOW.month:02d}/{_NOW.year}"

SCHEDULES_DATA = [
    {
        "id": "SCH01",
        "name": "Phát TVC Điện máy Xanh khung giờ cao điểm",
        "screen_id": "LED02",
        "content_id": "CNT01",
        "start_date": f"01/{_YM}",
        "end_date": f"20/{_YM}",
        "start_time": "06:30",
        "end_time": "22:00",
        "repeat": "Hằng ngày",
        "weekdays": [],
        "active": True,
    },
    {
        "id": "SCH02",
        "name": "Phim giới thiệu nhà máy tại sảnh Tòa A",
        "screen_id": "LED01",
        "content_id": "CNT04",
        "start_date": f"02/{_YM}",
        "end_date": f"25/{_YM}",
        "start_time": "08:00",
        "end_time": "17:30",
        "repeat": "Hằng tuần",
        "weekdays": ["T2", "T3", "T4", "T5", "T6"],
        "active": True,
    },
    {
        "id": "SCH03",
        "name": "Thông báo cắt điện bảo trì trạm biến áp",
        "screen_id": "LED03",
        "content_id": "CNT03",
        "start_date": f"05/{_YM}",
        "end_date": f"14/{_YM}",
        "start_time": "07:00",
        "end_time": "21:00",
        "repeat": "Hằng ngày",
        "weekdays": [],
        "active": True,
    },
    {
        "id": "SCH04",
        "name": "Phông nền Lễ ký kết đối tác tại tầng 5",
        "screen_id": "LED04",
        "content_id": "CNT07",
        "start_date": f"09/{_YM}",
        "end_date": f"11/{_YM}",
        "start_time": "08:00",
        "end_time": "12:00",
        "repeat": "Không lặp",
        "weekdays": [],
        "active": True,
    },
    {
        "id": "SCH05",
        "name": "Hướng dẫn phân luồng đỗ xe hầm B1",
        "screen_id": "LED05",
        "content_id": "CNT11",
        "start_date": f"01/{_YM}",
        "end_date": f"28/{_YM}",
        "start_time": "06:00",
        "end_time": "23:00",
        "repeat": "Hằng ngày",
        "weekdays": [],
        "active": False,
    },
    {
        "id": "SCH06",
        "name": "Banner lãi suất vay mua nhà tại PGD Quận 3",
        "screen_id": "LED07",
        "content_id": "CNT05",
        "start_date": f"04/{_YM}",
        "end_date": f"26/{_YM}",
        "start_time": "07:30",
        "end_time": "19:00",
        "repeat": "Hằng tuần",
        "weekdays": ["T2", "T3", "T4", "T5", "T6", "T7"],
        "active": True,
    },
    {
        "id": "SCH07",
        "name": "Chiếu clip tổng kết năm giờ nghỉ trưa",
        "screen_id": "LED09",
        "content_id": "CNT10",
        "start_date": f"12/{_YM}",
        "end_date": f"27/{_YM}",
        "start_time": "11:30",
        "end_time": "13:30",
        "repeat": "Hằng tuần",
        "weekdays": ["T2", "T4", "T6"],
        "active": False,
    },
    {
        "id": "SCH08",
        "name": "Tuyên truyền an toàn PCCC đầu ca sáng",
        "screen_id": "LED10",
        "content_id": "CNT06",
        "start_date": f"03/{_YM}",
        "end_date": f"28/{_YM}",
        "start_time": "06:45",
        "end_time": "08:15",
        "repeat": "Hằng ngày",
        "weekdays": [],
        "active": True,
    },
]

ACTIVITIES_DATA = [
    {"time": "07/11/2026 11:42", "action": "Nguyễn Đức Minh (Quản trị viên): Giảm độ sáng màn hình LED-HN-001 xuống 78%."},
    {"time": "07/11/2026 11:18", "action": "Hệ thống giám sát: Cảnh báo nhiệt độ tủ nguồn vượt ngưỡng (67°C) tại thiết bị LED-SG-001."},
    {"time": "07/11/2026 10:04", "action": "Trần Thị Minh Châu (Biên tập viên): Tải lên tệp 'TVC Khuyến mãi cuối năm - Điện máy Xanh (Bản 30s)'."},
    {"time": "07/11/2026 09:27", "action": "Lê Hoàng Nam (Biên tập viên): Kích hoạt lịch phát SCH01 cho điểm LED-BH-001."},
    {"time": "07/11/2026 08:51", "action": "Phạm Văn Hùng (Quản trị viên): Gửi lệnh khởi động lại từ xa thiết bị LED-HN-003."},
    {"time": "06/11/2026 23:12", "action": "Hệ thống giám sát: Mất kết nối tín hiệu với bảng LED-HN-004 (Dốc hầm gửi xe B1)."},
    {"time": "06/11/2026 17:19", "action": "Nguyễn Đức Minh (Quản trị viên): Tạm khóa tài khoản người dùng khanh.vq."},
    {"time": "06/11/2026 15:43", "action": "Trần Thị Minh Châu (Biên tập viên): Cập nhật ghi chú cho nội dung CNT03."},
    {"time": "06/11/2026 14:08", "action": "Lê Hoàng Nam (Biên tập viên): Tạo lịch phát mới SCH04 cho Phòng hội nghị tầng 5."},
    {"time": "06/11/2026 09:35", "action": "Phạm Văn Hùng (Quản trị viên): Thêm điểm màn hình mới LED-HN-006 (KCN Bắc Thăng Long)."},
]


# ==============================================================================
# CÁC HÀM TIỆN ÍCH TRUY XUẤT & CẬP NHẬT DỮ LIỆU (GIỮ NGUYÊN CHỮ KÝ HÀM)
# ==============================================================================

def log_activity(action_text: str):
    """Ghi thêm một hoạt động mới vào đầu danh sách kèm họ tên và vai trò người thực hiện."""
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    actor_name = CURRENT_USER.get("full_name", "Người dùng")
    actor_role = CURRENT_USER.get("role", ROLE_VIEWER)
    prefix = f"{actor_name} ({actor_role})"

    text_clean = action_text.strip()
    if text_clean.startswith(actor_name):
        rest = text_clean[len(actor_name):].lstrip(" :")
        formatted_action = f"{prefix}: {rest}"
    elif f"({actor_role})" in text_clean:
        formatted_action = text_clean
    else:
        formatted_action = f"{prefix}: {text_clean}"

    ACTIVITIES_DATA.insert(0, {"time": now_str, "action": formatted_action})


def get_screen_by_id(screen_id: str):
    """Tìm màn hình LED theo ID."""
    for screen in SCREENS_DATA:
        if screen["id"] == screen_id:
            return screen
    return None


def get_screen_name(screen_id: str) -> str:
    """Lấy tên màn hình LED từ ID."""
    screen = get_screen_by_id(screen_id)
    return screen["name"] if screen else "Không xác định"


def get_content_by_id(content_id: str):
    """Tìm nội dung theo ID."""
    for content in CONTENTS_DATA:
        if content["id"] == content_id:
            return content
    return None


def get_content_name(content_id: str) -> str:
    """Lấy tên nội dung từ ID."""
    content = get_content_by_id(content_id)
    return content["name"] if content else "Chưa chọn nội dung"


def generate_next_id(prefix: str, data_list: list) -> str:
    """Tạo mã ID tự tăng theo tiền tố (ví dụ LED11, CNT13, SCH09, USR07)."""
    max_num = 0
    for item in data_list:
        raw_id = item.get("id", "")
        if raw_id.startswith(prefix):
            num_part = raw_id[len(prefix):]
            if num_part.isdigit():
                max_num = max(max_num, int(num_part))
    return f"{prefix}{max_num + 1:02d}"


def parse_vn_date(date_str: str):
    """Chuyển chuỗi ngày dd/mm/yyyy thành đối tượng datetime.date (trả về None nếu sai)."""
    try:
        return datetime.strptime(date_str.strip(), "%d/%m/%Y").date()
    except Exception:
        return None


def parse_vn_datetime(date_str: str, time_str: str):
    """Chuyển chuỗi ngày dd/mm/yyyy và giờ HH:MM thành đối tượng datetime."""
    try:
        return datetime.strptime(f"{date_str.strip()} {time_str.strip()}", "%d/%m/%Y %H:%M")
    except Exception:
        return None


def randomize_monitoring_metrics():
    """Làm mới ngẫu nhiên số liệu nhiệt độ và thời gian kết nối cho phân hệ Giám sát."""
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    for screen in SCREENS_DATA:
        if screen["status"] == "Online":
            screen["temperature"] = random.randint(37, 63)
            screen["last_connected"] = now_str
        elif screen["status"] == "Sự cố":
            screen["temperature"] = random.randint(61, 72)
            screen["last_connected"] = now_str
        else:
            screen["temperature"] = random.randint(29, 34)
