import flet as ft
import data
from components import (
    PRIMARY_COLOR,
    PRIMARY_LIGHT,
    ALIGN_CENTER,
    border_all,
    pad_sym,
    set_field_error,
    show_snack,
)


def build_view(page: ft.Page, on_login_success) -> ft.Container:
    """Xây dựng màn hình Đăng nhập Demo với thông tin tài khoản hướng dẫn rõ ràng."""
    username_field = ft.TextField(
        label="Tên đăng nhập",
        hint_text="Nhập tên tài khoản (ví dụ: admin)",
        value="admin",
        prefix_icon=ft.Icons.PERSON_OUTLINE,
        border_radius=8,
        autofocus=True,
    )

    password_field = ft.TextField(
        label="Mật khẩu",
        hint_text="Nhập mật khẩu demo",
        value="123456",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        border_radius=8,
    )

    error_banner = ft.Text("", color=ft.Colors.RED_600, size=13, visible=False)

    def handle_login(e=None):
        """Kiểm tra dữ liệu bỏ trống và xác thực với danh sách USERS_DATA."""
        set_field_error(username_field, None)
        set_field_error(password_field, None)
        error_banner.visible = False

        uname = (username_field.value or "").strip()
        pwd = (password_field.value or "").strip()

        has_error = False
        if not uname:
            set_field_error(username_field, "Vui lòng nhập tên đăng nhập")
            has_error = True
        if not pwd:
            set_field_error(password_field, "Vui lòng nhập mật khẩu")
            has_error = True

        if has_error:
            page.update()
            return

        # Tìm tài khoản trong mock data
        matched_user = None
        for u in data.USERS_DATA:
            if u["username"].lower() == uname.lower() and u["password"] == pwd:
                matched_user = u
                break

        if not matched_user:
            error_banner.value = "Sai tên đăng nhập hoặc mật khẩu demo!"
            error_banner.visible = True
            page.update()
            return

        if not matched_user["active"]:
            error_banner.value = "Tài khoản này hiện đang bị khóa. Vui lòng dùng tài khoản khác!"
            error_banner.visible = True
            page.update()
            return

        # Cập nhật người dùng hiện tại và chuyển vào trang Tổng quan
        data.CURRENT_USER.clear()
        data.CURRENT_USER.update(matched_user)
        data.log_activity(f"{matched_user['full_name']} ({matched_user['username']}) đã đăng nhập hệ thống.")
        on_login_success()
        show_snack(page, f"Xin chào {matched_user['full_name']}! Đăng nhập thành công.")

    def fill_demo_account(uname: str, pwd: str):
        """Điền nhanh tài khoản demo khi người dùng nhấn chọn."""
        username_field.value = uname
        password_field.value = pwd
        set_field_error(username_field, None)
        set_field_error(password_field, None)
        error_banner.visible = False
        page.update()

    password_field.on_submit = handle_login
    username_field.on_submit = handle_login

    login_card = ft.Card(
        elevation=6,
        content=ft.Container(
            width=440,
            padding=32,
            border_radius=16,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
                tight=True,
                controls=[
                    ft.Container(
                        width=68,
                        height=68,
                        border_radius=18,
                        bgcolor=PRIMARY_COLOR,
                        alignment=ALIGN_CENTER,
                        content=ft.Icon(ft.Icons.TV_ROUNDED, color=ft.Colors.WHITE, size=36),
                    ),
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                        controls=[
                            ft.Text(
                                "ĐIỀU KHIỂN MÀN HÌNH LED",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=PRIMARY_COLOR,
                            ),
                            ft.Text(
                                "Hệ thống quản trị & phát sóng tập trung (Bản Demo)",
                                size=13,
                                color=ft.Colors.GREY_600,
                            ),
                        ],
                    ),
                    ft.Divider(height=8),
                    username_field,
                    password_field,
                    error_banner,
                    ft.FilledButton(
                        "Đăng nhập hệ thống",
                        icon=ft.Icons.LOGIN,
                        bgcolor=PRIMARY_COLOR,
                        color=ft.Colors.WHITE,
                        width=380,
                        height=44,
                        on_click=handle_login,
                    ),
                    ft.Container(
                        width=380,
                        padding=12,
                        border_radius=10,
                        bgcolor=PRIMARY_LIGHT,
                        border=border_all(1, ft.Colors.BLUE_200),
                        content=ft.Column(
                            spacing=6,
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.INFO_OUTLINE, color=PRIMARY_COLOR, size=18),
                                        ft.Text(
                                            "Tài khoản Demo cố định (Nhấn để điền nhanh):",
                                            weight=ft.FontWeight.BOLD,
                                            size=12,
                                            color=PRIMARY_COLOR,
                                        ),
                                    ],
                                    spacing=6,
                                ),
                                ft.Text(
                                    "• Quản trị viên: admin / 123456\n"
                                    "• Biên tập viên: bientap01 / 123456\n"
                                    "• Người xem: nguoixem01 / 123456",
                                    size=12,
                                    color=ft.Colors.BLUE_900,
                                ),
                                ft.Row(
                                    spacing=8,
                                    controls=[
                                        ft.TextButton(
                                            "Điền Admin",
                                            on_click=lambda e: fill_demo_account("admin", "123456"),
                                        ),
                                        ft.TextButton(
                                            "Điền Biên tập",
                                            on_click=lambda e: fill_demo_account("bientap01", "123456"),
                                        ),
                                        ft.TextButton(
                                            "Điền Người xem",
                                            on_click=lambda e: fill_demo_account("nguoixem01", "123456"),
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        ),
    )

    return ft.Container(
        expand=True,
        alignment=ALIGN_CENTER,
        padding=pad_sym(horizontal=16, vertical=24),
        content=login_card,
    )
