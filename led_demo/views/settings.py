import flet as ft
import data
from components import (
    PRIMARY_COLOR,
    create_page_header,
    make_dropdown,
    set_field_error,
    show_snack,
)


def build_view(
    page: ft.Page,
    on_theme_change=None,
    on_logout=None,
    on_profile_updated=None,
) -> ft.Column:
    """Xây dựng giao diện Cài đặt hệ thống: thông tin công ty, hồ sơ cá nhân, đổi mật khẩu, giao diện & đăng xuất."""

    # 1. Thẻ thông tin đơn vị vận hành (Chỉ xem)
    company_rows = [
        ("Đơn vị chủ quản:", data.COMPANY_INFO["name"]),
        ("Mã số thuế:", data.COMPANY_INFO["code"]),
        ("Trụ sở chính:", data.COMPANY_INFO["address"]),
        ("Tổng đài kỹ thuật:", data.COMPANY_INFO["hotline"]),
        ("Email hỗ trợ:", data.COMPANY_INFO["email"]),
        ("Website:", data.COMPANY_INFO["website"]),
        ("Phiên bản phần mềm:", data.COMPANY_INFO["version"]),
    ]

    company_card = ft.Card(
        col={"sm": 12, "lg": 6},
        elevation=2,
        content=ft.Container(
            padding=20,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.BUSINESS, color=PRIMARY_COLOR),
                            ft.Text("Thông tin đơn vị vận hành (Chỉ xem)", size=16, weight=ft.FontWeight.BOLD),
                        ],
                    ),
                    ft.Divider(height=4),
                    *[
                        ft.Row(
                            controls=[
                                ft.Text(lbl, weight=ft.FontWeight.W_600, width=150, size=13, color=ft.Colors.GREY_700),
                                ft.Text(val, expand=True, size=13),
                            ]
                        )
                        for lbl, val in company_rows
                    ],
                ],
            ),
        ),
    )

    # 2. Thẻ chỉnh sửa thông tin cá nhân
    fullname_tf = ft.TextField(
        label="Họ và tên *",
        value=data.CURRENT_USER.get("full_name", ""),
        border_radius=8,
    )
    email_tf = ft.TextField(
        label="Email liên hệ *",
        value=data.CURRENT_USER.get("email", ""),
        border_radius=8,
    )
    phone_tf = ft.TextField(
        label="Số điện thoại *",
        value=data.CURRENT_USER.get("phone", ""),
        border_radius=8,
    )

    def handle_save_profile(e):
        for fld in [fullname_tf, email_tf, phone_tf]:
            set_field_error(fld, None)

        has_error = False
        if not (fullname_tf.value or "").strip():
            set_field_error(fullname_tf, "Vui lòng nhập họ và tên")
            has_error = True
        if not (email_tf.value or "").strip() or "@" not in (email_tf.value or ""):
            set_field_error(email_tf, "Vui lòng nhập email hợp lệ")
            has_error = True
        if not (phone_tf.value or "").strip():
            set_field_error(phone_tf, "Vui lòng nhập số điện thoại")
            has_error = True

        if has_error:
            page.update()
            return

        data.CURRENT_USER["full_name"] = fullname_tf.value.strip()
        data.CURRENT_USER["email"] = email_tf.value.strip()
        data.CURRENT_USER["phone"] = phone_tf.value.strip()

        # Đồng bộ lại trong USERS_DATA
        for u in data.USERS_DATA:
            if u["id"] == data.CURRENT_USER.get("id"):
                u["full_name"] = data.CURRENT_USER["full_name"]
                u["email"] = data.CURRENT_USER["email"]
                u["phone"] = data.CURRENT_USER["phone"]
                break

        if on_profile_updated:
            on_profile_updated()
        data.log_activity(f"{data.CURRENT_USER['full_name']} đã cập nhật thông tin hồ sơ cá nhân.")
        page.update()
        show_snack(page, "Đã lưu thông tin cá nhân thành công!")

    profile_card = ft.Card(
        col={"sm": 12, "lg": 6},
        elevation=2,
        content=ft.Container(
            padding=20,
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.BADGE_OUTLINED, color=PRIMARY_COLOR),
                            ft.Text("Chỉnh sửa thông tin cá nhân", size=16, weight=ft.FontWeight.BOLD),
                        ],
                    ),
                    ft.Divider(height=4),
                    fullname_tf,
                    email_tf,
                    phone_tf,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.END,
                        controls=[
                            ft.FilledButton(
                                "Cập nhật hồ sơ",
                                icon=ft.Icons.SAVE,
                                bgcolor=PRIMARY_COLOR,
                                color=ft.Colors.WHITE,
                                on_click=handle_save_profile,
                            )
                        ],
                    ),
                ],
            ),
        ),
    )

    # 3. Thẻ đổi mật khẩu Demo (kiểm tra mật khẩu cũ, mới và xác nhận)
    old_pwd_tf = ft.TextField(
        label="Mật khẩu hiện tại *",
        password=True,
        can_reveal_password=True,
        border_radius=8,
    )
    new_pwd_tf = ft.TextField(
        label="Mật khẩu mới *",
        password=True,
        can_reveal_password=True,
        border_radius=8,
    )
    confirm_pwd_tf = ft.TextField(
        label="Xác nhận mật khẩu mới *",
        password=True,
        can_reveal_password=True,
        border_radius=8,
    )

    def handle_change_password(e):
        for fld in [old_pwd_tf, new_pwd_tf, confirm_pwd_tf]:
            set_field_error(fld, None)

        old_val = (old_pwd_tf.value or "").strip()
        new_val = (new_pwd_tf.value or "").strip()
        cfm_val = (confirm_pwd_tf.value or "").strip()

        has_error = False
        if not old_val:
            set_field_error(old_pwd_tf, "Vui lòng nhập mật khẩu hiện tại")
            has_error = True
        elif old_val != data.CURRENT_USER.get("password", "123456"):
            set_field_error(old_pwd_tf, "Mật khẩu hiện tại không chính xác")
            has_error = True

        if not new_val:
            set_field_error(new_pwd_tf, "Vui lòng nhập mật khẩu mới")
            has_error = True
        elif len(new_val) < 4:
            set_field_error(new_pwd_tf, "Mật khẩu mới phải từ 4 ký tự trở lên")
            has_error = True

        if not cfm_val:
            set_field_error(confirm_pwd_tf, "Vui lòng xác nhận mật khẩu mới")
            has_error = True
        elif new_val and cfm_val != new_val:
            set_field_error(confirm_pwd_tf, "Mật khẩu xác nhận không khớp")
            has_error = True

        if has_error:
            page.update()
            return

        data.CURRENT_USER["password"] = new_val
        for u in data.USERS_DATA:
            if u["id"] == data.CURRENT_USER.get("id"):
                u["password"] = new_val
                break

        old_pwd_tf.value = ""
        new_pwd_tf.value = ""
        confirm_pwd_tf.value = ""
        data.log_activity(f"{data.CURRENT_USER['full_name']} đã thay đổi mật khẩu đăng nhập demo.")
        page.update()
        show_snack(page, "Đã đổi mật khẩu thành công! Bạn có thể dùng mật khẩu mới ở lần đăng nhập sau.")

    password_card = ft.Card(
        col={"sm": 12, "lg": 6},
        elevation=2,
        content=ft.Container(
            padding=20,
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.LOCK_RESET, color=PRIMARY_COLOR),
                            ft.Text("Đổi mật khẩu Demo", size=16, weight=ft.FontWeight.BOLD),
                        ],
                    ),
                    ft.Divider(height=4),
                    old_pwd_tf,
                    new_pwd_tf,
                    confirm_pwd_tf,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.END,
                        controls=[
                            ft.FilledButton(
                                "Đổi mật khẩu",
                                icon=ft.Icons.KEY,
                                bgcolor=PRIMARY_COLOR,
                                color=ft.Colors.WHITE,
                                on_click=handle_change_password,
                            )
                        ],
                    ),
                ],
            ),
        ),
    )

    # 4. Thẻ tùy chọn hiển thị, thông báo giao diện, chế độ Sáng/Tối & Đăng xuất
    dark_mode_switch = ft.Switch(
        label="Giao diện nền Tối (Dark Mode)",
        value=(page.theme_mode == ft.ThemeMode.DARK),
        active_color=PRIMARY_COLOR,
        on_change=lambda e: on_theme_change(e.control.value) if on_theme_change else None,
    )

    notif_switch = ft.Switch(
        label="Bật thông báo phản hồi trên giao diện",
        value=data.SYSTEM_SETTINGS["ui_notifications"],
        active_color=PRIMARY_COLOR,
        on_change=lambda e: (
            data.SYSTEM_SETTINGS.update({"ui_notifications": e.control.value}),
            show_snack(page, f"Đã {'bật' if e.control.value else 'tắt'} thông báo giao diện!"),
        ),
    )

    rows_per_page_dd = make_dropdown(
        label="Số dòng mặc định mỗi trang bảng",
        options=[("5", "5 dòng / trang"), ("10", "10 dòng / trang"), ("20", "20 dòng / trang")],
        value=data.SYSTEM_SETTINGS["rows_per_page"],
        on_change=lambda e: (
            data.SYSTEM_SETTINGS.update({"rows_per_page": e.control.value or "10"}),
            show_snack(page, f"Đã đặt số dòng hiển thị mặc định: {e.control.value} dòng/trang"),
        ),
    )

    default_view_dd = make_dropdown(
        label="Kiểu hiển thị mặc định của Quản lý nội dung",
        options=[("grid", "Dạng Lưới thẻ (Grid)"), ("table", "Dạng Bảng danh sách (Table)")],
        value=data.SYSTEM_SETTINGS["default_content_view"],
        on_change=lambda e: (
            data.SYSTEM_SETTINGS.update({"default_content_view": e.control.value or "grid"}),
            show_snack(page, "Đã lưu kiểu hiển thị mặc định cho trang Quản lý nội dung!"),
        ),
    )

    preferences_card = ft.Card(
        col={"sm": 12, "lg": 6},
        elevation=2,
        content=ft.Container(
            padding=20,
            content=ft.Column(
                spacing=14,
                controls=[
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.DISPLAY_SETTINGS, color=PRIMARY_COLOR),
                            ft.Text("Tùy chọn giao diện & Hệ thống", size=16, weight=ft.FontWeight.BOLD),
                        ],
                    ),
                    ft.Divider(height=4),
                    dark_mode_switch,
                    notif_switch,
                    rows_per_page_dd,
                    default_view_dd,
                    ft.Divider(height=8),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text("Kết thúc phiên làm việc hiện tại:", size=13, color=ft.Colors.GREY_600),
                            ft.FilledButton(
                                "Đăng xuất khỏi hệ thống",
                                icon=ft.Icons.LOGOUT,
                                bgcolor=ft.Colors.RED_600,
                                color=ft.Colors.WHITE,
                                on_click=lambda e: on_logout() if on_logout else None,
                            ),
                        ],
                    ),
                ],
            ),
        ),
    )

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=16,
        controls=[
            create_page_header(
                title="Cài đặt hệ thống",
                subtitle="Quản lý thông tin đơn vị, hồ sơ cá nhân, bảo mật mật khẩu và tùy biến giao diện Sáng/Tối.",
            ),
            ft.ResponsiveRow(
                spacing=16,
                run_spacing=16,
                controls=[
                    company_card,
                    profile_card,
                    password_card,
                    preferences_card,
                ],
            ),
        ],
    )
