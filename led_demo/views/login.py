import flet as ft
import data
import theme
from components import (
    ALIGN_CENTER,
    border_all,
    make_form_field,
    make_primary_button,
    make_surface_box,
    make_text_field,
    pad_sym,
    set_field_error,
    show_snack,
)


def build_view(page: ft.Page, on_login_success) -> ft.Container:
    """Màn hình đăng nhập gọn, phẳng theo chuẩn phần mềm quản trị nội bộ."""
    username_field = make_text_field(
        value="admin",
        hint_text="Nhập tên tài khoản",
    )
    password_field = make_text_field(
        value="123456",
        hint_text="Nhập mật khẩu",
        password=True,
        can_reveal_password=True,
    )

    error_banner = ft.Text(
        "",
        color=theme.STATUS_DANGER,
        size=theme.TEXT_12,
        visible=False,
    )

    def handle_login(e=None):
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

        matched_user = None
        for u in data.USERS_DATA:
            if u["username"].lower() == uname.lower() and u["password"] == pwd:
                matched_user = u
                break

        if not matched_user:
            error_banner.value = "Tên đăng nhập hoặc mật khẩu không đúng."
            error_banner.visible = True
            page.update()
            return

        if not matched_user["active"]:
            error_banner.value = "Tài khoản này đang bị tạm khóa. Vui lòng liên hệ Quản trị viên."
            error_banner.visible = True
            page.update()
            return

        data.set_current_user(matched_user)
        data.log_activity(f"Đăng nhập hệ thống bằng tài khoản '{matched_user['username']}'.")
        on_login_success()
        show_snack(page, f"Đã đăng nhập: {matched_user['full_name']} ({matched_user['role']})")

    def fill_demo_account(uname: str, pwd: str):
        username_field.value = uname
        password_field.value = pwd
        set_field_error(username_field, None)
        set_field_error(password_field, None)
        error_banner.visible = False
        page.update()

    username_field.on_submit = handle_login
    password_field.on_submit = handle_login

    login_box = make_surface_box(
        padding=theme.SPACE_32,
        content=ft.Container(
            width=360,
            content=ft.Column(
                spacing=theme.SPACE_16,
                tight=True,
                controls=[
                    ft.Row(
                        spacing=theme.SPACE_8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=theme.SPACE_24,
                                height=theme.SPACE_24,
                                border_radius=theme.RADIUS_INPUT,
                                bgcolor=theme.accent_color(),
                                alignment=ALIGN_CENTER,
                                content=ft.Text(
                                    "VL",
                                    size=theme.TEXT_12,
                                    weight=theme.WEIGHT_SEMI,
                                    color=theme.WHITE,
                                ),
                            ),
                            ft.Text(
                                "VietLED CMS",
                                size=theme.TEXT_16,
                                weight=theme.WEIGHT_SEMI,
                                color=theme.text_primary(),
                            ),
                        ],
                    ),
                    ft.Column(
                        spacing=theme.SPACE_4,
                        controls=[
                            ft.Text(
                                "Đăng nhập quản trị",
                                size=theme.TEXT_22,
                                weight=theme.WEIGHT_SEMI,
                                color=theme.text_primary(),
                            ),
                            ft.Text(
                                "Hệ thống điều khiển màn hình LED nội bộ",
                                size=theme.TEXT_12,
                                color=theme.text_secondary(),
                            ),
                        ],
                    ),
                    make_form_field("Tên đăng nhập", username_field),
                    make_form_field("Mật khẩu", password_field),
                    error_banner,
                    make_primary_button(
                        "Đăng nhập",
                        on_click=handle_login,
                        width=360,
                    ),
                    ft.Container(
                        padding=theme.SPACE_12,
                        border_radius=theme.RADIUS_INPUT,
                        bgcolor=theme.surface_subtle_color(),
                        border=border_all(theme.BORDER_WIDTH, theme.border_color()),
                        content=ft.Column(
                            spacing=theme.SPACE_8,
                            controls=[
                                ft.Text(
                                    "Tài khoản demo theo 3 vai trò (Mật khẩu: 123456)",
                                    size=theme.TEXT_12,
                                    weight=theme.WEIGHT_SEMI,
                                    color=theme.text_primary(),
                                ),
                                ft.Text(
                                    "Quản trị viên: admin  |  Biên tập viên: bientap  |  Người xem: xem",
                                    size=theme.TEXT_12,
                                    color=theme.text_secondary(),
                                ),
                                ft.Text(
                                    "Tài khoản đang bị khóa để thử nghiệm: khanh.vq",
                                    size=theme.TEXT_12,
                                    color=theme.text_secondary(),
                                ),
                                ft.Row(
                                    spacing=theme.SPACE_4,
                                    wrap=True,
                                    controls=[
                                        ft.TextButton(
                                            "Điền admin",
                                            on_click=lambda e: fill_demo_account("admin", "123456"),
                                        ),
                                        ft.TextButton(
                                            "Điền bientap",
                                            on_click=lambda e: fill_demo_account("bientap", "123456"),
                                        ),
                                        ft.TextButton(
                                            "Điền xem",
                                            on_click=lambda e: fill_demo_account("xem", "123456"),
                                        ),
                                        ft.TextButton(
                                            "TK khóa",
                                            on_click=lambda e: fill_demo_account("khanh.vq", "123456"),
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
        bgcolor=theme.bg_color(),
        alignment=ALIGN_CENTER,
        padding=pad_sym(horizontal=theme.SPACE_16, vertical=theme.SPACE_24),
        content=login_box,
    )
