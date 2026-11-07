from datetime import datetime
import random

# ==============================================================================
# DỮ LIỆU GIẢ LẬP (MOCK DATA) DÙNG CHUNG CHO TOÀN HỆ THỐNG
# ==============================================================================

# Thông tin công ty (chỉ xem ở phần Cài đặt)
COMPANY_INFO = {
    "name": "CÔNG TY CỔ PHẦN GIẢI PHÁP TRUYỀN THÔNG SỐ VIETLED",
    "code": "MST: 0109887654",
    "address": "Tầng 12, Tòa nhà Innovation, Quận Cầu Giấy, Hà Nội",
    "hotline": "1900 6868 - (024) 3888 9999",
    "email": "support@vietled-demo.vn",
    "website": "https://vietled-demo.vn",
    "version": "v2.4.0 (Bản Demo Giao Diện Flet)",
}

# Cài đặt hệ thống dùng chung trong phiên chạy
SYSTEM_SETTINGS = {
    "theme_mode": "light",           # "light" hoặc "dark"
    "ui_notifications": True,        # Bật/tắt thông báo giao diện
    "rows_per_page": "10",           # Số dòng hiển thị mặc định: "5", "10", "20"
    "default_content_view": "grid",  # "grid" (Lưới thẻ) hoặc "table" (Bảng)
}

# Danh sách 6 người dùng (Quản trị viên, Biên tập viên, Người xem)
USERS_DATA = [
    {
        "id": "USR01",
        "username": "admin",
        "password": "123456",
        "full_name": "Nguyễn Quản Trị",
        "email": "admin@vietled.vn",
        "phone": "0901234567",
        "role": "Quản trị viên",
        "active": True,
        "created_at": "10/01/2026",
    },
    {
        "id": "USR02",
        "username": "bientap01",
        "password": "123456",
        "full_name": "Trần Thị Minh Châu",
        "email": "chau.tran@vietled.vn",
        "phone": "0912345678",
        "role": "Biên tập viên",
        "active": True,
        "created_at": "15/02/2026",
    },
    {
        "id": "USR03",
        "username": "bientap02",
        "password": "123456",
        "full_name": "Lê Hoàng Nam",
        "email": "nam.le@vietled.vn",
        "phone": "0987654321",
        "role": "Biên tập viên",
        "active": True,
        "created_at": "20/03/2026",
    },
    {
        "id": "USR04",
        "username": "kythuat01",
        "password": "123456",
        "full_name": "Phạm Văn Hùng",
        "email": "hung.pham@vietled.vn",
        "phone": "0933445566",
        "role": "Quản trị viên",
        "active": True,
        "created_at": "05/04/2026",
    },
    {
        "id": "USR05",
        "username": "nguoixem01",
        "password": "123456",
        "full_name": "Đỗ Thu Hà",
        "email": "ha.do@vietled.vn",
        "phone": "0977889900",
        "role": "Người xem",
        "active": True,
        "created_at": "12/05/2026",
    },
    {
        "id": "USR06",
        "username": "nguoixem02",
        "password": "123456",
        "full_name": "Vũ Quốc Khánh",
        "email": "khanh.vu@vietled.vn",
        "phone": "0966112233",
        "role": "Người xem",
        "active": False,
        "created_at": "01/06/2026",
    },
]

# Người dùng đang đăng nhập hiện tại (mặc định gán khi đăng nhập thành công)
CURRENT_USER = USERS_DATA[0].copy()

# Danh mục nội dung
CONTENT_CATEGORIES = ["Quảng cáo", "Thông báo", "Sự kiện", "Giới thiệu"]

# Danh sách 12 nội dung hiển thị (ảnh / video)
CONTENTS_DATA = [
    {
        "id": "CNT01",
        "name": "TVC Khuyến mãi Mùa Thu Vàng",
        "type": "Video",
        "category": "Quảng cáo",
        "format": "MP4",
        "size": "45.2 MB",
        "upload_date": "01/10/2026",
        "description": "Video quảng cáo chiến dịch giảm giá mùa thu tại sảnh chính.",
    },
    {
        "id": "CNT02",
        "name": "Poster Chào mừng Đại hội Cổ đông",
        "type": "Hình ảnh",
        "category": "Sự kiện",
        "format": "PNG",
        "size": "4.8 MB",
        "upload_date": "05/10/2026",
        "description": "Poster độ phân giải 4K chào mừng đại biểu tham dự sự kiện.",
    },
    {
        "id": "CNT03",
        "name": "Thông báo Lịch bảo trì tòa nhà",
        "type": "Hình ảnh",
        "category": "Thông báo",
        "format": "JPG",
        "size": "2.1 MB",
        "upload_date": "08/10/2026",
        "description": "Thông báo lịch kiểm tra hệ thống điện định kỳ hàng tháng.",
    },
    {
        "id": "CNT04",
        "name": "Video Giới thiệu Tập đoàn 2026",
        "type": "Video",
        "category": "Giới thiệu",
        "format": "MP4",
        "size": "128.5 MB",
        "upload_date": "10/10/2026",
        "description": "Phim doanh nghiệp giới thiệu tầm nhìn và thành tựu năm 2026.",
    },
    {
        "id": "CNT05",
        "name": "Banner Ra mắt Sản phẩm SmartHome",
        "type": "Hình ảnh",
        "category": "Quảng cáo",
        "format": "PNG",
        "size": "6.3 MB",
        "upload_date": "12/10/2026",
        "description": "Hình ảnh quảng bá dòng thiết bị nhà thông minh thế hệ mới.",
    },
    {
        "id": "CNT06",
        "name": "Clip Hướng dẫn Thoát hiểm PCCC",
        "type": "Video",
        "category": "Thông báo",
        "format": "MP4",
        "size": "62.0 MB",
        "upload_date": "15/10/2026",
        "description": "Video minh họa quy trình an toàn phòng cháy chữa cháy.",
    },
    {
        "id": "CNT07",
        "name": "Backdrop Hội thảo Trí tuệ Nhân tạo",
        "type": "Hình ảnh",
        "category": "Sự kiện",
        "format": "JPG",
        "size": "5.4 MB",
        "upload_date": "18/10/2026",
        "description": "Hình nền LED sân khấu hội thảo công nghệ AI 2026.",
    },
    {
        "id": "CNT08",
        "name": "TVC Ưu đãi Ngân hàng Số",
        "type": "Video",
        "category": "Quảng cáo",
        "format": "MP4",
        "size": "38.7 MB",
        "upload_date": "20/10/2026",
        "description": "Quảng cáo mở thẻ tín dụng hoàn tiền không giới hạn.",
    },
    {
        "id": "CNT09",
        "name": "Infographic Văn hóa Doanh nghiệp",
        "type": "Hình ảnh",
        "category": "Giới thiệu",
        "format": "PNG",
        "size": "3.9 MB",
        "upload_date": "22/10/2026",
        "description": "5 giá trị cốt lõi của nhân sự hiển thị tại khu vực thang máy.",
    },
    {
        "id": "CNT10",
        "name": "Teaser Đêm nhạc Gala Cuối năm",
        "type": "Video",
        "category": "Sự kiện",
        "format": "MOV",
        "size": "84.1 MB",
        "upload_date": "25/10/2026",
        "description": "Video giới thiệu chương trình Gala Dinner tổng kết năm.",
    },
    {
        "id": "CNT11",
        "name": "Thông báo Quy định Đỗ xe Khu B",
        "type": "Hình ảnh",
        "category": "Thông báo",
        "format": "JPG",
        "size": "1.9 MB",
        "upload_date": "28/10/2026",
        "description": "Sơ đồ phân luồng giao thông tại hầm gửi xe B1 - B2.",
    },
    {
        "id": "CNT12",
        "name": "Video Tri ân Khách hàng Thân thiết",
        "type": "Video",
        "category": "Giới thiệu",
        "format": "MP4",
        "size": "51.6 MB",
        "upload_date": "01/11/2026",
        "description": "Clip cảm ơn đối tác và khách hàng nhân dịp kỷ niệm 10 năm.",
    },
]

# Danh sách 10 màn hình LED
SCREENS_DATA = [
    {
        "id": "LED01",
        "name": "Màn hình Sảnh Chính Tầng 1",
        "code": "DEV-HN-001",
        "location": "Sảnh Lễ tân Tòa A, Hà Nội",
        "size": "6.0m x 3.5m (P2.5 Indoor)",
        "resolution": "2400 x 1400 px",
        "status": "Online",
        "playing_state": "Đang phát",
        "current_content_id": "CNT01",
        "brightness": 85,
        "volume": 60,
        "temperature": 42,
        "uptime": "14 ngày 06 giờ",
        "last_connected": "07/11/2026 10:58",
    },
    {
        "id": "LED02",
        "name": "Màn hình Mặt tiền Đường Láng",
        "code": "DEV-HN-002",
        "location": "Mặt ngoài Tòa A, Cầu Giấy",
        "size": "12.0m x 6.0m (P4 Outdoor)",
        "resolution": "3000 x 1500 px",
        "status": "Online",
        "playing_state": "Đang phát",
        "current_content_id": "CNT05",
        "brightness": 95,
        "volume": 0,
        "temperature": 54,
        "uptime": "21 ngày 11 giờ",
        "last_connected": "07/11/2026 10:59",
    },
    {
        "id": "LED03",
        "name": "Màn hình Khu Thang máy Tầng 1",
        "code": "DEV-HN-003",
        "location": "Cụm thang máy trung tâm Tầng 1",
        "size": "2.0m x 1.2m (P1.8 Indoor)",
        "resolution": "1920 x 1080 px",
        "status": "Online",
        "playing_state": "Đang phát",
        "current_content_id": "CNT09",
        "brightness": 70,
        "volume": 40,
        "temperature": 39,
        "uptime": "08 ngày 19 giờ",
        "last_connected": "07/11/2026 10:57",
    },
    {
        "id": "LED04",
        "name": "Màn hình Hội trường Lớn Tầng 5",
        "code": "DEV-HN-004",
        "location": "Phòng Hội nghị Diamond, Tầng 5",
        "size": "8.0m x 4.0m (P2.0 Indoor)",
        "resolution": "3840 x 2160 px",
        "status": "Online",
        "playing_state": "Tạm dừng",
        "current_content_id": "CNT07",
        "brightness": 80,
        "volume": 75,
        "temperature": 44,
        "uptime": "03 ngày 04 giờ",
        "last_connected": "07/11/2026 10:55",
    },
    {
        "id": "LED05",
        "name": "Màn hình Cổng vào Khu Đỗ xe B1",
        "code": "DEV-HN-005",
        "location": "Ram dốc xuống hầm B1",
        "size": "3.0m x 1.0m (P3 Outdoor)",
        "resolution": "1280 x 480 px",
        "status": "Offline",
        "playing_state": "Đã dừng",
        "current_content_id": "CNT11",
        "brightness": 60,
        "volume": 0,
        "temperature": 35,
        "uptime": "00 ngày 00 giờ",
        "last_connected": "06/11/2026 22:15",
    },
    {
        "id": "LED06",
        "name": "Màn hình Quảng trường Trung tâm",
        "code": "DEV-SG-006",
        "location": "Ngã tư Nguyễn Huệ, Quận 1, TP.HCM",
        "size": "15.0m x 8.0m (P5 Outdoor)",
        "resolution": "3000 x 1600 px",
        "status": "Sự cố",
        "playing_state": "Gián đoạn",
        "current_content_id": "CNT08",
        "brightness": 100,
        "volume": 50,
        "temperature": 68,
        "uptime": "01 ngày 02 giờ",
        "last_connected": "07/11/2026 10:40",
    },
    {
        "id": "LED07",
        "name": "Màn hình Sảnh VIP Tầng 12",
        "code": "DEV-HN-007",
        "location": "Khu tiếp khách VIP Tầng 12",
        "size": "4.0m x 2.25m (P1.5 COB)",
        "resolution": "2560 x 1440 px",
        "status": "Online",
        "playing_state": "Đang phát",
        "current_content_id": "CNT04",
        "brightness": 75,
        "volume": 55,
        "temperature": 41,
        "uptime": "19 ngày 08 giờ",
        "last_connected": "07/11/2026 11:00",
    },
    {
        "id": "LED08",
        "name": "Màn hình Khu Ẩm thực Tầng 3",
        "code": "DEV-DN-008",
        "location": "Food Court Trung tâm Thương mại Đà Nẵng",
        "size": "5.0m x 3.0m (P2.5 Indoor)",
        "resolution": "2000 x 1200 px",
        "status": "Online",
        "playing_state": "Đang phát",
        "current_content_id": "CNT10",
        "brightness": 85,
        "volume": 65,
        "temperature": 47,
        "uptime": "11 ngày 15 giờ",
        "last_connected": "07/11/2026 10:56",
    },
    {
        "id": "LED09",
        "name": "Màn hình Hành lang Khu B",
        "code": "DEV-HN-009",
        "location": "Hành lang nối Tòa A - Tòa B",
        "size": "2.5m x 1.5m (P2.5 Indoor)",
        "resolution": "1600 x 960 px",
        "status": "Offline",
        "playing_state": "Đã dừng",
        "current_content_id": "CNT03",
        "brightness": 50,
        "volume": 20,
        "temperature": 33,
        "uptime": "00 ngày 00 giờ",
        "last_connected": "05/11/2026 18:30",
    },
    {
        "id": "LED10",
        "name": "Màn hình Cổng chào Khu Công nghệ",
        "code": "DEV-SG-010",
        "location": "Cổng chính Khu Công nghệ cao TP.HCM",
        "size": "10.0m x 4.5m (P4 Outdoor)",
        "resolution": "2500 x 1125 px",
        "status": "Sự cố",
        "playing_state": "Cảnh báo nhiệt",
        "current_content_id": "CNT06",
        "brightness": 90,
        "volume": 0,
        "temperature": 65,
        "uptime": "05 ngày 12 giờ",
        "last_connected": "07/11/2026 10:49",
    },
]

# Danh sách 8 lịch phát nội dung (dùng tháng hiện tại để thấy ngay trên lịch tháng)
_NOW = datetime.now()
_YM = f"{_NOW.month:02d}/{_NOW.year}"

SCHEDULES_DATA = [
    {
        "id": "SCH01",
        "name": "Phát TVC Khuyến mãi Sảnh chính",
        "screen_id": "LED01",
        "content_id": "CNT01",
        "start_date": f"01/{_YM}",
        "end_date": f"15/{_YM}",
        "start_time": "07:30",
        "end_time": "21:30",
        "repeat": "Hằng ngày",
        "weekdays": [],
        "active": True,
    },
    {
        "id": "SCH02",
        "name": "Quảng cáo SmartHome giờ cao điểm",
        "screen_id": "LED02",
        "content_id": "CNT05",
        "start_date": f"03/{_YM}",
        "end_date": f"20/{_YM}",
        "start_time": "06:00",
        "end_time": "22:00",
        "repeat": "Hằng ngày",
        "weekdays": [],
        "active": True,
    },
    {
        "id": "SCH03",
        "name": "Truyền thông Văn hóa Doanh nghiệp",
        "screen_id": "LED03",
        "content_id": "CNT09",
        "start_date": f"05/{_YM}",
        "end_date": f"28/{_YM}",
        "start_time": "08:00",
        "end_time": "18:00",
        "repeat": "Hằng tuần",
        "weekdays": ["T2", "T3", "T4", "T5", "T6"],
        "active": True,
    },
    {
        "id": "SCH04",
        "name": "Trình chiếu Hội thảo AI 2026",
        "screen_id": "LED04",
        "content_id": "CNT07",
        "start_date": f"10/{_YM}",
        "end_date": f"12/{_YM}",
        "start_time": "08:00",
        "end_time": "17:00",
        "repeat": "Không lặp",
        "weekdays": [],
        "active": True,
    },
    {
        "id": "SCH05",
        "name": "Hướng dẫn Đỗ xe Hầm B1",
        "screen_id": "LED05",
        "content_id": "CNT11",
        "start_date": f"01/{_YM}",
        "end_date": f"28/{_YM}",
        "start_time": "00:00",
        "end_time": "23:59",
        "repeat": "Hằng ngày",
        "weekdays": [],
        "active": False,
    },
    {
        "id": "SCH06",
        "name": "Phim Giới thiệu Tập đoàn tại Sảnh VIP",
        "screen_id": "LED07",
        "content_id": "CNT04",
        "start_date": f"08/{_YM}",
        "end_date": f"25/{_YM}",
        "start_time": "08:30",
        "end_time": "19:00",
        "repeat": "Hằng tuần",
        "weekdays": ["T2", "T4", "T6"],
        "active": True,
    },
    {
        "id": "SCH07",
        "name": "Teaser Gala Cuối năm Khu Ẩm thực",
        "screen_id": "LED08",
        "content_id": "CNT10",
        "start_date": f"14/{_YM}",
        "end_date": f"27/{_YM}",
        "start_time": "10:00",
        "end_time": "22:00",
        "repeat": "Hằng tuần",
        "weekdays": ["T6", "T7", "CN"],
        "active": True,
    },
    {
        "id": "SCH08",
        "name": "Tuyên truyền An toàn PCCC",
        "screen_id": "LED10",
        "content_id": "CNT06",
        "start_date": f"18/{_YM}",
        "end_date": f"24/{_YM}",
        "start_time": "07:00",
        "end_time": "19:00",
        "repeat": "Không lặp",
        "weekdays": [],
        "active": False,
    },
]

# Danh sách 10 hoạt động gần đây
ACTIVITIES_DATA = [
    {"time": "07/11/2026 10:55", "action": "Nguyễn Quản Trị đã cập nhật độ sáng Màn hình Sảnh Chính Tầng 1 lên 85%."},
    {"time": "07/11/2026 10:40", "action": "Hệ thống cảnh báo nhiệt độ cao (68°C) tại Màn hình Quảng trường Trung tâm."},
    {"time": "07/11/2026 10:15", "action": "Trần Thị Minh Châu đã tải lên nội dung mới: Video Tri ân Khách hàng Thân thiết."},
    {"time": "07/11/2026 09:50", "action": "Lê Hoàng Nam đã bật lịch phát 'Quảng cáo SmartHome giờ cao điểm'."},
    {"time": "07/11/2026 09:20", "action": "Phạm Văn Hùng đã khởi động lại Màn hình Hội trường Lớn Tầng 5."},
    {"time": "07/11/2026 08:45", "action": "Nguyễn Quản Trị đã khóa tài khoản người dùng Vũ Quốc Khánh (nguoixem02)."},
    {"time": "06/11/2026 22:15", "action": "Màn hình Cổng vào Khu Đỗ xe B1 chuyển sang trạng thái Offline."},
    {"time": "06/11/2026 17:30", "action": "Trần Thị Minh Châu đã chỉnh sửa mô tả nội dung 'Poster Chào mừng Đại hội Cổ đông'."},
    {"time": "06/11/2026 15:10", "action": "Lê Hoàng Nam đã tạo lịch phát mới 'Trình chiếu Hội thảo AI 2026'."},
    {"time": "06/11/2026 11:00", "action": "Nguyễn Quản Trị đã thêm thiết bị mới: Màn hình Cổng chào Khu Công nghệ (DEV-SG-010)."},
]


# ==============================================================================
# CÁC HÀM TIỆN ÍCH TRUY XUẤT & CẬP NHẬT DỮ LIỆU
# ==============================================================================

def log_activity(action_text: str):
    """Ghi thêm một hoạt động mới vào đầu danh sách hoạt động gần đây."""
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    ACTIVITIES_DATA.insert(0, {"time": now_str, "action": action_text})


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
            screen["temperature"] = random.randint(38, 64)
            screen["last_connected"] = now_str
        elif screen["status"] == "Sự cố":
            screen["temperature"] = random.randint(61, 74)
            screen["last_connected"] = now_str
        else:
            screen["temperature"] = random.randint(30, 36)
