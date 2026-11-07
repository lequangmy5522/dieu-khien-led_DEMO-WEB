from datetime import datetime
import flet as ft
import data
from components import (
    PRIMARY_COLOR,
    close_dialog,
    create_page_header,
    create_search_field,
    create_status_badge,
    make_dropdown,
    open_dialog,
    set_field_error,
    show_confirm_delete_dialog,
    show_snack,
)

ROLES_LIST = ["Quản trị viên", "Biên tập viên", "Người xem"]


def build_view(page: ft.Page, on_user_updated=None) -> ft.Column:
    """Xây dựng giao diện Quản lý người dùng: thêm, sửa, xóa, tìm kiếm, lọc vai trò, khóa/mở khóa."""
    filter_state = {
        "keyword": "",
        "role": "Tất cả",
    }

    table_container = ft.Column(spacing=10)
    summary_text = ft.Text("", size=13, color=ft.Colors.GREY_600)

    def get_filtered_users() -> list:
        kw = filter_state["keyword"].strip().lower()
        role_f = filter_state["role"]
        results = []
        for u in data.USERS_DATA:
            match_kw = (
                not kw
                or kw in u["username"].lower()
                or kw in u["full_name"].lower()
                or kw in u["email"].lower()
                or kw in u["phone"].lower()
            )
            match_role = role_f == "Tất cả" or u["role"] == role_f
            if match_kw and match_role:
                results.append(u)
        return results

    def open_user_form_dialog(user_to_edit: dict | None = None):
        """Hộp thoại Thêm mới hoặc Chỉnh sửa tài khoản người dùng."""
        is_edit = user_to_edit is not None

        username_field = ft.TextField(
            label="Tên đăng nhập *",
            value=user_to_edit["username"] if is_edit else "",
            read_only=is_edit,
            border_radius=8,
        )
        fullname_field = ft.TextField(
            label="Họ và tên *",
            value=user_to_edit["full_name"] if is_edit else "",
            border_radius=8,
        )
        email_field = ft.TextField(
            label="Địa chỉ Email *",
            value=user_to_edit["email"] if is_edit else "",
            border_radius=8,
        )
        phone_field = ft.TextField(
            label="Số điện thoại *",
            value=user_to_edit["phone"] if is_edit else "",
            border_radius=8,
        )
        role_dd = make_dropdown(
            label="Vai trò phân quyền *",
            options=ROLES_LIST,
            value=user_to_edit["role"] if is_edit else ROLES_LIST[1],
        )
        password_field = ft.TextField(
            label="Mật khẩu khởi tạo *" if not is_edit else "Mật khẩu",
            value=user_to_edit["password"] if is_edit else "123456",
            password=True,
            can_reveal_password=True,
            border_radius=8,
        )

        def handle_save_user(e):
            for fld in [username_field, fullname_field, email_field, phone_field, password_field]:
                set_field_error(fld, None)

            has_error = False
            uname = (username_field.value or "").strip()
            fname = (fullname_field.value or "").strip()
            email = (email_field.value or "").strip()
            phone = (phone_field.value or "").strip()
            pwd = (password_field.value or "").strip()

            if not uname:
                set_field_error(username_field, "Vui lòng nhập tên đăng nhập")
                has_error = True
            if not fname:
                set_field_error(fullname_field, "Vui lòng nhập họ và tên")
                has_error = True
            if not email or "@" not in email:
                set_field_error(email_field, "Vui lòng nhập email hợp lệ")
                has_error = True
            if not phone:
                set_field_error(phone_field, "Vui lòng nhập số điện thoại")
                has_error = True
            if not pwd:
                set_field_error(password_field, "Vui lòng nhập mật khẩu")
                has_error = True

            # Kiểm tra trùng username khi thêm mới
            if not is_edit and uname:
                for u in data.USERS_DATA:
                    if u["username"].lower() == uname.lower():
                        set_field_error(username_field, "Tên đăng nhập đã tồn tại")
                        has_error = True
                        break

            if has_error:
                page.update()
                return

            if is_edit:
                user_to_edit["full_name"] = fname
                user_to_edit["email"] = email
                user_to_edit["phone"] = phone
                user_to_edit["role"] = role_dd.value or user_to_edit["role"]
                user_to_edit["password"] = pwd
                # Nếu sửa chính tài khoản đang đăng nhập thì đồng bộ CURRENT_USER
                if user_to_edit["id"] == data.CURRENT_USER.get("id"):
                    data.CURRENT_USER.update(user_to_edit)
                    if on_user_updated:
                        on_user_updated()
                data.log_activity(f"Đã cập nhật thông tin người dùng '{fname}' ({uname}).")
                msg = f"Đã cập nhật tài khoản \"{fname}\"!"
            else:
                new_user = {
                    "id": data.generate_next_id("USR", data.USERS_DATA),
                    "username": uname,
                    "password": pwd,
                    "full_name": fname,
                    "email": email,
                    "phone": phone,
                    "role": role_dd.value or "Biên tập viên",
                    "active": True,
                    "created_at": datetime.now().strftime("%d/%m/%Y"),
                }
                data.USERS_DATA.insert(0, new_user)
                data.log_activity(f"Đã thêm người dùng mới '{fname}' ({uname} - {new_user['role']}).")
                msg = f"Đã thêm người dùng \"{fname}\" thành công!"

            close_dialog(page, dialog)
            refresh_table()
            show_snack(page, msg)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Chỉnh sửa tài khoản" if is_edit else "Thêm người dùng mới",
                weight=ft.FontWeight.BOLD,
                size=18,
            ),
            content=ft.Container(
                width=460,
                content=ft.Column(
                    tight=True,
                    spacing=12,
                    controls=[
                        username_field,
                        fullname_field,
                        email_field,
                        phone_field,
                        role_dd,
                        password_field,
                    ],
                ),
            ),
            actions=[
                ft.OutlinedButton("Hủy", on_click=lambda e: close_dialog(page, dialog)),
                ft.FilledButton(
                    "Lưu người dùng",
                    icon=ft.Icons.SAVE,
                    bgcolor=PRIMARY_COLOR,
                    color=ft.Colors.WHITE,
                    on_click=handle_save_user,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        open_dialog(page, dialog)

    def handle_toggle_lock(user: dict, is_active: bool):
        """Khóa / Mở khóa tài khoản người dùng bằng Switch."""
        if user["username"] == data.CURRENT_USER.get("username") and not is_active:
            refresh_table()
            show_snack(page, "Không thể tự khóa tài khoản đang đăng nhập!", is_error=True)
            return

        user["active"] = is_active
        action_label = "Mở khóa" if is_active else "Khóa"
        data.log_activity(f"Đã {action_label.lower()} tài khoản người dùng '{user['full_name']}' ({user['username']}).")
        refresh_table()
        show_snack(page, f"Đã {action_label} tài khoản \"{user['full_name']}\"!")

    def handle_delete_user(user: dict):
        """Xác nhận và xóa người dùng (không cho xóa chính mình)."""
        if user["username"] == data.CURRENT_USER.get("username"):
            show_snack(page, "Không thể xóa tài khoản đang đăng nhập!", is_error=True)
            return

        def confirm_delete():
            data.USERS_DATA.remove(user)
            data.log_activity(f"Đã xóa tài khoản người dùng '{user['full_name']}' ({user['username']}).")
            refresh_table()
            show_snack(page, f"Đã xóa người dùng \"{user['full_name']}\"!")

        show_confirm_delete_dialog(page, f"{user['full_name']} ({user['username']})", confirm_delete)

    def refresh_table():
        filtered = get_filtered_users()
        summary_text.value = f"Hiển thị {len(filtered)} / {len(data.USERS_DATA)} tài khoản"

        rows = []
        for u in filtered:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(u["username"], weight=ft.FontWeight.BOLD, size=13)),
                        ft.DataCell(ft.Text(u["full_name"], weight=ft.FontWeight.W_500, size=13)),
                        ft.DataCell(ft.Text(u["email"], size=12)),
                        ft.DataCell(ft.Text(u["phone"], size=12)),
                        ft.DataCell(ft.Text(u["role"], size=12, weight=ft.FontWeight.W_600, color=PRIMARY_COLOR)),
                        ft.DataCell(
                            ft.Row(
                                spacing=6,
                                controls=[
                                    ft.Switch(
                                        value=u["active"],
                                        active_color=PRIMARY_COLOR,
                                        tooltip="Bật để Mở khóa / Tắt để Khóa tài khoản",
                                        on_change=lambda e, usr=u: handle_toggle_lock(usr, e.control.value),
                                    ),
                                    create_status_badge("Hoạt động" if u["active"] else "Đã khóa"),
                                ],
                            )
                        ),
                        ft.DataCell(
                            ft.Row(
                                spacing=4,
                                controls=[
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT_OUTLINED,
                                        icon_color=ft.Colors.AMBER_800,
                                        tooltip="Chỉnh sửa",
                                        on_click=lambda e, usr=u: open_user_form_dialog(usr),
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE,
                                        icon_color=ft.Colors.RED_600,
                                        tooltip="Xóa người dùng",
                                        on_click=lambda e, usr=u: handle_delete_user(usr),
                                    ),
                                ],
                            )
                        ),
                    ]
                )
            )

        table_container.controls = [
            ft.Row(
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.DataTable(
                        column_spacing=20,
                        heading_row_height=44,
                        data_row_min_height=48,
                        columns=[
                            ft.DataColumn(ft.Text("Tài khoản", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Họ và tên", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Email", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Điện thoại", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Vai trò", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Trạng thái (Mở/Khóa)", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Thao tác", weight=ft.FontWeight.BOLD)),
                        ],
                        rows=rows,
                    )
                ],
            )
            if rows
            else ft.Container(
                padding=30,
                content=ft.Text("Không tìm thấy người dùng nào phù hợp.", italic=True),
            )
        ]
        page.update()

    search_box = create_search_field(
        "Tìm theo họ tên, tài khoản, email, SĐT...",
        lambda e: (filter_state.update({"keyword": e.control.value or ""}), refresh_table()),
        width=320,
    )
    role_filter = make_dropdown(
        label="Lọc theo vai trò",
        options=["Tất cả"] + ROLES_LIST,
        value="Tất cả",
        on_change=lambda e: (filter_state.update({"role": e.control.value or "Tất cả"}), refresh_table()),
        width=200,
    )

    refresh_table()

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=16,
        controls=[
            create_page_header(
                title="Quản lý người dùng",
                subtitle="Phân quyền tài khoản Quản trị viên, Biên tập viên, Người xem và quản lý khóa/mở khóa truy cập.",
                right_controls=[
                    ft.FilledButton(
                        "Thêm người dùng",
                        icon=ft.Icons.PERSON_ADD,
                        bgcolor=PRIMARY_COLOR,
                        color=ft.Colors.WHITE,
                        on_click=lambda e: open_user_form_dialog(None),
                    )
                ],
            ),
            ft.Card(
                elevation=2,
                content=ft.Container(
                    padding=18,
                    content=ft.Column(
                        spacing=14,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                wrap=True,
                                controls=[
                                    ft.Row(spacing=12, wrap=True, controls=[search_box, role_filter]),
                                    summary_text,
                                ],
                            ),
                            ft.Divider(height=1),
                            table_container,
                        ],
                    ),
                ),
            ),
        ],
    )
