import flet as ft
import data
import permissions
import theme
from components import (
    border_only,
    create_page_header,
    create_role_badge,
    make_dropdown,
    make_form_field,
    make_primary_button,
    make_surface_box,
    make_text_field,
    pad_sym,
    set_field_error,
    show_snack,
)


def build_view(
    page: ft.Page,
    on_theme_change=None,
    on_logout=None,
    on_profile_updated=None,
) -> ft.Column:
    """Trang Cài đặt hệ thống: thông tin đơn vị, hồ sơ cá nhân, đổi mật khẩu và tùy chọn hiển thị."""
    role = data.get_current_role()
    can_edit_profile = permissions.can(role, "settings", "edit_profile")
    can_change_pwd = permissions.can(role, "settings", "change_password")
    can_preferences = permissions.can(role, "settings", "preferences")
    can_logout = permissions.can(role, "settings", "logout")

    company_rows = [
        ("Đơn vị vận hành", data.COMPANY_INFO["name"]),
        ("Mã số thuế", data.COMPANY_INFO["code"]),
        ("Địa chỉ", data.COMPANY_INFO["address"]),
        ("Trực kỹ thuật", data.COMPANY_INFO["hotline"]),
        ("Email hỗ trợ", data.COMPANY_INFO["email"]),
        ("Trang thông tin", data.COMPANY_INFO["website"]),
        ("Phiên bản", data.COMPANY_INFO["version"]),
    ]

    company_items = []
    for idx, (lbl, val) in enumerate(company_rows):
        company_items.append(
            ft.Container(
                padding=pad_sym(vertical=theme.SPACE_8),
                border=border_only(bottom=ft.BorderSide(theme.BORDER_WIDTH, theme.border_color()))
                if idx < len(company_rows) - 1
                else None,
                content=ft.Row(
                    controls=[
                        ft.Text(lbl, size=theme.TEXT_12, color=theme.text_secondary(), width=140),
                        ft.Text(val, size=theme.TEXT_14, color=theme.text_primary(), expand=True),
                    ]
                ),
            )
        )

    company_card = make_surface_box(
        col={"sm": 12, "lg": 6},
        padding=theme.SPACE_24,
        content=ft.Column(
            spacing=theme.SPACE_12,
            controls=[
                ft.Text("Thông tin đơn vị (Chỉ đọc)", size=theme.TEXT_16, weight=theme.WEIGHT_SEMI),
                ft.Column(spacing=0, controls=company_items),
            ],
        ),
    )

    fullname_tf = make_text_field(
        value=data.CURRENT_USER.get("full_name", ""),
        read_only=not can_edit_profile,
    )
    email_tf = make_text_field(
        value=data.CURRENT_USER.get("email", ""),
        read_only=not can_edit_profile,
    )
    phone_tf = make_text_field(
        value=data.CURRENT_USER.get("phone", ""),
        read_only=not can_edit_profile,
    )

    def handle_save_profile(e):
        if not permissions.can(data.get_current_role(), "settings", "edit_profile"):
            show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
            return

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

        for u in data.USERS_DATA:
            if u["id"] == data.CURRENT_USER.get("id"):
                u["full_name"] = data.CURRENT_USER["full_name"]
                u["email"] = data.CURRENT_USER["email"]
                u["phone"] = data.CURRENT_USER["phone"]
                break

        if on_profile_updated:
            on_profile_updated()
        data.log_activity("Cập nhật thông tin hồ sơ cá nhân.")
        page.update()
        show_snack(page, "Đã lưu hồ sơ cá nhân.")

    profile_card = make_surface_box(
        col={"sm": 12, "lg": 6},
        padding=theme.SPACE_24,
        content=ft.Column(
            spacing=theme.SPACE_12,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Thông tin cá nhân", size=theme.TEXT_16, weight=theme.WEIGHT_SEMI),
                        create_role_badge(role),
                    ],
                ),
                make_form_field("Họ và tên *", fullname_tf),
                make_form_field("Email *", email_tf),
                make_form_field("Số điện thoại *", phone_tf),
                ft.Row(
                    alignment=ft.MainAxisAlignment.END,
                    controls=[
                        make_primary_button(
                            "Lưu thay đổi",
                            disabled=not can_edit_profile,
                            on_click=handle_save_profile,
                        )
                    ],
                ),
            ],
        ),
    )

    old_pwd_tf = make_text_field(password=True, can_reveal_password=True, read_only=not can_change_pwd)
    new_pwd_tf = make_text_field(password=True, can_reveal_password=True, read_only=not can_change_pwd)
    confirm_pwd_tf = make_text_field(password=True, can_reveal_password=True, read_only=not can_change_pwd)

    def handle_change_password(e):
        if not permissions.can(data.get_current_role(), "settings", "change_password"):
            show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
            return

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
            set_field_error(old_pwd_tf, "Mật khẩu hiện tại không đúng")
            has_error = True

        if not new_val:
            set_field_error(new_pwd_tf, "Vui lòng nhập mật khẩu mới")
            has_error = True
        elif len(new_val) < 4:
            set_field_error(new_pwd_tf, "Tối thiểu 4 ký tự")
            has_error = True

        if not cfm_val:
            set_field_error(confirm_pwd_tf, "Vui lòng nhập lại mật khẩu mới")
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
        data.log_activity("Đã đổi mật khẩu tài khoản cá nhân.")
        page.update()
        show_snack(page, "Đã cập nhật mật khẩu mới.")

    password_card = make_surface_box(
        col={"sm": 12, "lg": 6},
        padding=theme.SPACE_24,
        content=ft.Column(
            spacing=theme.SPACE_12,
            controls=[
                ft.Text("Đổi mật khẩu", size=theme.TEXT_16, weight=theme.WEIGHT_SEMI),
                make_form_field("Mật khẩu hiện tại *", old_pwd_tf),
                make_form_field("Mật khẩu mới *", new_pwd_tf),
                make_form_field("Xác nhận mật khẩu mới *", confirm_pwd_tf),
                ft.Row(
                    alignment=ft.MainAxisAlignment.END,
                    controls=[
                        make_primary_button(
                            "Cập nhật mật khẩu",
                            disabled=not can_change_pwd,
                            on_click=handle_change_password,
                        )
                    ],
                ),
            ],
        ),
    )

    def handle_dark_mode_switch(e):
        if not permissions.can(data.get_current_role(), "settings", "preferences"):
            show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
            return
        if on_theme_change:
            on_theme_change(e.control.value)

    def handle_notif_switch(e):
        if not permissions.can(data.get_current_role(), "settings", "preferences"):
            show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
            return
        data.SYSTEM_SETTINGS["ui_notifications"] = e.control.value
        show_snack(page, f"Đã {'bật' if e.control.value else 'tắt'} thông báo phản hồi.")

    def handle_rows_per_page(e):
        if not permissions.can(data.get_current_role(), "settings", "preferences"):
            show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
            return
        data.SYSTEM_SETTINGS["rows_per_page"] = e.control.value or "10"
        show_snack(page, f"Số dòng mặc định mỗi trang: {e.control.value}")

    def handle_default_view(e):
        if not permissions.can(data.get_current_role(), "settings", "preferences"):
            show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
            return
        data.SYSTEM_SETTINGS["default_content_view"] = e.control.value or "grid"
        show_snack(page, "Đã lưu kiểu hiển thị mặc định cho Quản lý nội dung.")

    dark_mode_switch = ft.Switch(
        label="Chế độ nền tối (Dark mode)",
        value=theme.is_dark(),
        disabled=not can_preferences,
        active_color=theme.accent_color(),
        on_change=handle_dark_mode_switch,
    )

    notif_switch = ft.Switch(
        label="Hiển thị thông báo phản hồi thao tác",
        value=data.SYSTEM_SETTINGS["ui_notifications"],
        disabled=not can_preferences,
        active_color=theme.accent_color(),
        on_change=handle_notif_switch,
    )

    rows_per_page_dd = make_dropdown(
        label="",
        options=[("5", "5 dòng / trang"), ("10", "10 dòng / trang"), ("20", "20 dòng / trang")],
        value=data.SYSTEM_SETTINGS["rows_per_page"],
        on_change=handle_rows_per_page,
    )

    default_view_dd = make_dropdown(
        label="",
        options=[("grid", "Lưới thẻ (Grid)"), ("table", "Bảng danh sách (Table)")],
        value=data.SYSTEM_SETTINGS["default_content_view"],
        on_change=handle_default_view,
    )

    preferences_card = make_surface_box(
        col={"sm": 12, "lg": 6},
        padding=theme.SPACE_24,
        content=ft.Column(
            spacing=theme.SPACE_16,
            controls=[
                ft.Text("Tùy chọn hiển thị & Phiên làm việc", size=theme.TEXT_16, weight=theme.WEIGHT_SEMI),
                dark_mode_switch,
                notif_switch,
                make_form_field("Số dòng hiển thị mỗi trang bảng", rows_per_page_dd),
                make_form_field("Kiểu xem mặc định tại Quản lý nội dung", default_view_dd),
                ft.Divider(height=theme.SPACE_8, color=theme.border_color()),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Đăng xuất khỏi tài khoản hiện tại", size=theme.TEXT_14, color=theme.text_secondary()),
                        make_primary_button(
                            "Đăng xuất",
                            icon_name=ft.Icons.LOGOUT_OUTLINED,
                            is_danger=True,
                            disabled=not can_logout,
                            on_click=lambda e: on_logout() if on_logout else None,
                        ),
                    ],
                ),
            ],
        ),
    )

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=theme.SPACE_16,
        controls=[
            create_page_header(
                title="Cài đặt hệ thống",
                subtitle="Thông tin đơn vị vận hành, bảo mật tài khoản và cấu hình giao diện.",
            ),
            ft.ResponsiveRow(
                spacing=theme.SPACE_16,
                run_spacing=theme.SPACE_16,
                controls=[
                    company_card,
                    profile_card,
                    password_card,
                    preferences_card,
                ],
            ),
        ],
    )
