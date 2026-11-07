# Toàn Trung CMS – Hệ thống Quản trị & Điều khiển Màn hình LED

Ứng dụng web quản trị tập trung hệ thống màn hình LED nội bộ (**Toàn Trung CMS**), được xây dựng bằng **Python** và **Flet (`flet==1.1.2`)**. Hệ thống mô phỏng đầy đủ quy trình vận hành thực tế: quản lý điểm màn hình LED, kho nội dung số (video/hình ảnh), lập lịch phát sóng, điều khiển thiết bị từ xa theo thời gian thực, giám sát nhiệt độ/kết nối và phân quyền người dùng theo vai trò (RBAC).

---

## 1. Thông tin đơn vị vận hành

- **Đơn vị vận hành:** Công Ty Cổ Phần Điện Tử Viễn Thông Toàn Trung
- **Mã số thuế:** `0304604194`
- **Địa chỉ:** 710/58 Lũy Bán Bích, P. Tân Thành, Q. Tân Phú, TP.HCM (VPGD: 31 Đường số 18, P. Phú Thọ Hòa, Q. Tân Phú)
- **Trực kỹ thuật / Hotline:** `(028) 3812 2456 – Hotline kỹ thuật: 0918 771 713`
- **Email hỗ trợ:** `toantrungco@gmail.com`
- **Website:** https://toantrung.com.vn
- **Phiên bản phần mềm:** `v2.4.1-internal (Build 2026.10)`

---

## 2. Công nghệ & Kiến trúc hệ thống

- **Ngôn ngữ:** Python `>= 3.10` (khuyến nghị Python `3.12+` / `3.14`)
- **Framework giao diện:** [Flet](https://flet.dev/) `1.1.2` (hỗ trợ chạy trực tiếp trên trình duyệt Web hoặc ứng dụng Desktop)
- **Quản lý gói:** `uv` hoặc `pip` (`requirements.txt` / `pyproject.toml`)
- **Thiết kế giao diện (UI/UX):**
  - Phong cách phần mềm quản trị nội bộ phẳng, gọn, viền mảnh `1px`, độ tương phản rõ ràng.
  - Hỗ trợ chuyển đổi tức thời giữa **Chế độ Sáng (Light Mode)** và **Chế độ Tối (Dark Mode)**.
  - Giữ trạng thái phiên đăng nhập và phân hệ đang mở khi người dùng tải lại trang (`F5` / `Ctrl+R`).

---

## 3. Cấu trúc thư mục dự án

```text
dieu-khien-led_DEMO-WEB/
├── main.py                 # Điểm khởi chạy ứng dụng, bố cục khung chính (Sidebar, Header, điều hướng)
├── theme.py                # Hệ thống Design Tokens (bảng màu Sáng/Tối, cỡ chữ, khoảng cách, bo góc)
├── components.py           # Các thành phần UI tái sử dụng (bảng dữ liệu, nút bấm, ô nhập, hộp thoại, phân trang)
├── permissions.py          # Ma trận phân quyền theo vai trò (RBAC: Quản trị viên, Biên tập viên, Người xem)
├── data.py                 # Dữ liệu giả lập trong bộ nhớ (màn hình LED, nội dung, lịch phát, người dùng, nhật ký)
├── views/                  # Các phân hệ giao diện của ứng dụng
│   ├── login.py            # Màn hình đăng nhập & nút điền nhanh tài khoản demo
│   ├── dashboard.py        # 1. Trang Tổng quan
│   ├── screens.py          # 2. Quản lý màn hình LED
│   ├── contents.py         # 3. Quản lý nội dung hiển thị
│   ├── schedules.py        # 4. Lịch phát nội dung (Danh sách & Lịch tháng)
│   ├── control.py          # 5. Điều khiển màn hình từ xa
│   ├── monitoring.py       # 6. Giám sát thiết bị & cảnh báo nhiệt độ
│   ├── users.py            # 7. Quản lý người dùng & khóa/mở khóa tài khoản
│   └── settings.py         # 8. Cài đặt hệ thống & hồ sơ cá nhân
├── led_demo/               # Bản sao module đóng gói độc lập của ứng dụng
├── pyproject.toml          # Cấu hình dự án chuẩn Python / uv
├── requirements.txt        # Danh sách thư viện phụ thuộc (flet==1.1.2)
└── README.md               # Tài liệu hướng dẫn sử dụng và mô tả dự án
```

---

## 4. Hướng dẫn cài đặt và khởi chạy

### Cách 1: Chạy bằng môi trường ảo `.venv` có sẵn (Windows PowerShell)

1. Mở terminal tại thư mục gốc của dự án:
   ```powershell
   cd c:\Users\lequa\Desktop\dieu-khien-led_DEMO-WEB
   ```
2. Kích hoạt môi trường ảo (hoặc gọi trực tiếp Python trong `.venv`):
   ```powershell
   .\.venv\Scripts\activate
   ```
   *(Nếu chưa cài đặt thư viện, chạy: `pip install -r requirements.txt`)*

3. **Chạy ở chế độ Web (mở trên trình duyệt):**
   ```powershell
   flet run --web main.py
   ```
   Hoặc chỉ định cổng cố định (ví dụ cổng `8080`):
   ```powershell
   flet run --web --port 8080 main.py
   ```

4. **Chạy ở chế độ cửa sổ ứng dụng Desktop:**
   ```powershell
   python main.py
   ```

### Cách 2: Chạy bằng `uv`

```powershell
uv sync
uv run flet run --web main.py
```

---

## 5. Tài khoản Demo & Phân quyền (RBAC)

Trên màn hình đăng nhập có tích hợp sẵn các nút **Điền nhanh tài khoản** để kiểm thử phân quyền. Mật khẩu mặc định cho tất cả tài khoản là `123456`:

| Vai trò | Tên đăng nhập | Mật khẩu | Trạng thái | Quyền hạn chính |
| :--- | :--- | :--- | :--- | :--- |
| **Quản trị viên** | `admin` | `123456` | Hoạt động | Toàn quyền trên cả 8 phân hệ, bao gồm bật/tắt nguồn thiết bị và Quản lý người dùng. |
| **Biên tập viên** | `bientap` | `123456` | Hoạt động | Xem thiết bị; thêm/sửa/xóa nội dung và lịch phát; điều khiển phát, đổi nội dung, chỉnh độ sáng/âm lượng (không bật/tắt nguồn phần cứng và không vào Quản lý người dùng). |
| **Người xem** | `xem` | `123456` | Hoạt động | Chỉ xem số liệu tổng quan, danh sách màn hình, xem trước nội dung, lịch phát và giám sát thiết bị (ẩn phân hệ Điều khiển và Quản lý người dùng). |
| *Tài khoản khóa* | `khanh.vq` | `123456` | Tạm khóa | Dùng để kiểm thử thông báo chặn đăng nhập khi tài khoản bị khóa. |

---

## 6. Chi tiết 8 phân hệ chức năng

### 6.1. Tổng quan (`views/dashboard.py`)
- Hiển thị 5 thẻ số liệu thời gian thực: Tổng thiết bị, Đang trực tuyến (kèm tỷ lệ %), Ngoại tuyến / Sự cố, Tệp nội dung và Lịch phát sóng.
- Bảng tóm tắt trạng thái các màn hình LED gần đây (mã thiết bị, tên, trạng thái, nội dung đang phát, nhiệt độ).
- Danh sách nhật ký hoạt động gần đây của hệ thống (tự động ghi nhận mọi thao tác của người dùng trong phiên làm việc).

### 6.2. Quản lý màn hình LED (`views/screens.py`)
- Xem danh sách toàn bộ màn hình LED có phân trang.
- Tìm kiếm nhanh theo mã thiết bị, tên màn hình hoặc vị trí lắp đặt; lọc theo trạng thái (`Online`, `Offline`, `Sự cố`).
- Xem hộp thoại thông số chi tiết từng thiết bị (cấu hình module, độ phân giải, nội dung đang gán, độ sáng/âm lượng, nhiệt độ, thời gian chạy liên tục).
- Thêm mới, chỉnh sửa thông tin (có kiểm tra trùng mã thiết bị) và xóa màn hình LED.

### 6.3. Quản lý nội dung hiển thị (`views/contents.py`)
- Hỗ trợ chuyển đổi linh hoạt giữa 2 chế độ xem: **Dạng lưới thẻ (Grid)** và **Dạng bảng danh sách (Table)**.
- Tìm kiếm theo tên tệp, mô tả, định dạng; lọc theo danh mục (`Quảng cáo`, `Thông báo`, `Sự kiện`, `Giới thiệu`).
- Tải tệp nội dung mới lên hệ thống (hỗ trợ chọn tệp từ máy tính qua `FilePicker`, tự động nhận diện loại `Video` / `Hình ảnh` và dung lượng).
- Xem trước (Preview) hình ảnh và mô phỏng trình phát video; chỉnh sửa thông tin hoặc xóa tệp nội dung.

### 6.4. Lịch phát nội dung (`views/schedules.py`)
- Cung cấp 2 chế độ theo dõi: **Danh sách lịch phát** (có phân trang) và **Lịch tháng trực quan** (nhấn vào từng ngày để xem các khung giờ phát trong ngày).
- Tạo lịch phát mới và chỉnh sửa lịch phát với bộ chọn ngày (`DatePicker`) và bộ chọn giờ (`TimePicker`).
- Hỗ trợ chế độ lặp (`Không lặp`, `Hằng ngày`, `Hằng tuần` theo các thứ `T2`–`CN`).
- Tự động kiểm tra tính hợp lệ của ngày/giờ và **cảnh báo xung đột lịch phát** nếu trùng màn hình, trùng ngày và giao nhau khung giờ.
- Bật/tắt nhanh trạng thái kích hoạt của từng lịch phát.

### 6.5. Điều khiển màn hình (`views/control.py`)
- Chọn điểm màn hình LED cần tác động từ danh sách thiết bị.
- Điều khiển nguồn từ xa: **Bật nguồn**, **Tắt nguồn**, **Khởi động lại** (mô phỏng độ trễ phản hồi 2 giây từ tủ điều khiển và khóa nút chống bấm lặp).
- Điều khiển trình chiếu tức thời: **Tiếp tục phát**, **Tạm dừng**, hoặc **Chuyển đổi nội dung phát** ngay lập tức.
- Điều chỉnh **Độ sáng (%)** và **Âm lượng (%)** bằng thanh trượt (`Slider`) kèm khung giám sát trực quan.

### 6.6. Giám sát thiết bị (`views/monitoring.py`)
- Khung cảnh báo nổi bật liệt kê các thiết bị đang gặp sự cố mất đồng bộ tín hiệu hoặc **quá nhiệt (`> 60°C`)**.
- Lọc thiết bị theo trạng thái kết nối và hiển thị thẻ thông số kỹ thuật chi tiết cho từng điểm màn hình.
- Nút **Làm mới** giúp cập nhật lại số liệu nhiệt độ và thời điểm kết nối mới nhất.

### 6.7. Quản lý người dùng (`views/users.py`)
- Phân hệ dành riêng cho **Quản trị viên**.
- Tìm kiếm nhân sự theo tài khoản, họ tên, email, số điện thoại và lọc theo vai trò.
- Thêm tài khoản mới, chỉnh sửa thông tin/vai trò, khóa hoặc mở khóa tài khoản bằng công tắc (`Switch`), xóa tài khoản.
- Tích hợp cơ chế bảo vệ an toàn: không cho phép tự khóa/tự xóa tài khoản đang đăng nhập và không cho phép khóa/xóa Quản trị viên đang hoạt động cuối cùng.

### 6.8. Cài đặt hệ thống (`views/settings.py`)
- Hiển thị thông tin pháp lý & liên hệ kỹ thuật của **Công Ty Cổ Phần Điện Tử Viễn Thông Toàn Trung**.
- Cập nhật hồ sơ cá nhân (Họ tên, Email, Số điện thoại) và đổi mật khẩu tài khoản hiện tại.
- Tùy chỉnh giao diện: bật/tắt **Dark Mode**, bật/tắt thông báo phản hồi thao tác (`SnackBar`), cấu hình số dòng mặc định mỗi trang bảng (`5`, `10`, `20`) và kiểu xem mặc định cho kho nội dung.
