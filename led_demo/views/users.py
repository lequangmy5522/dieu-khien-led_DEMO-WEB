from datetime import datetime
import flet as ft
import data
import permissions
import theme
from components import (
    close_dialog,
    create_access_denied_view,
    create_action_icon,
    create_empty_state,
    create_page_header,
    create_pagination_bar,
    create_role_badge,
    create_search_field,
    create_status_badge,
    create_styled_table,
    make_dropdown,
    make_form_field,
    make_primary_button,
    make_surface_box,
    make_text_field,
    open_dialog,
    set_field_error,
    show_confirm_delete_dialog,
    show_snack,
)


def build_view(page: ft.Page, on_user_updated=None) -> ft.Column:
    """Trang Quản lý người dùng: chỉ dành cho Quản trị viên, có bảo vệ tài khoản Quản trị viên cuối cùng."""
    role = data.get_current_role()
    if not permissions.can(role, "users", "view"):
        return ft.Column(
            expand=True,
            controls=[create_access_denied_view(page)],
        )

    filter_state = {
        "keyword": "",
        "role": "Tất cả",
        "page": 1,
    }

    table_container = ft.Column(spacing=0)

    def count_active_admins() -> int:
        """Đếm số tài khoản Quản trị viên đang ở trạng thái hoạt động."""
        return sum(
            1
            for u in data.USERS_DATA
            if u.get("role") == permissions.ROLE_ADMIN and u.get("active", False)
        )

    def is_current_logged_user(user: dict) -> bool:
        """Kiểm tra tài khoản có phải là người dùng đang đăng nhập hiện tại hay không."""
        return (
            user.get("id") == data.CURRENT_USER.get("id")
            or user.get("username", "").lower() == data.CURRENT_USER.get("username", "").lower()
        )

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
        is_edit = user_to_edit is not None
        required_action = "edit" if is_edit else "add"
        if not permissions.can(data.get_current_role(), "users", required_action):
            show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
            return

        username_field = make_text_field(
            value=user_to_edit["username"] if is_edit else "",
            hint_text="VD: nam.lh",
            read_only=is_edit,
        )
        fullname_field = make_text_field(
            value=user_to_edit["full_name"] if is_edit else "",
            hint_text="VD: Lê Hoàng Nam",
        )
        email_field = make_text_field(
            value=user_to_edit["email"] if is_edit else "",
            hint_text="VD: nam.lh@toantrung.com.vn",
        )
        phone_field = make_text_field(
            value=user_to_edit["phone"] if is_edit else "",
            hint_text="VD: 0983 412 809",
        )
        role_dd = make_dropdown(
            label="",
            options=permissions.ALL_ROLES,
            value=user_to_edit["role"] if is_edit else permissions.ROLE_EDITOR,
        )
        password_field = make_text_field(
            value=user_to_edit["password"] if is_edit else "123456",
            password=True,
            can_reveal_password=True,
        )

        form_error_text = ft.Text("", color=theme.STATUS_DANGER, size=theme.TEXT_12, visible=False)

        def handle_save_user(e):
            if not permissions.can(data.get_current_role(), "users", required_action):
                close_dialog(page, dialog)
                show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
                return

            for fld in [username_field, fullname_field, email_field, phone_field, password_field, role_dd]:
                set_field_error(fld, None)
            form_error_text.visible = False

            has_error = False
            uname = (username_field.value or "").strip()
            fname = (fullname_field.value or "").strip()
            email = (email_field.value or "").strip()
            phone = (phone_field.value or "").strip()
            pwd = (password_field.value or "").strip()
            selected_role = role_dd.value or permissions.ROLE_EDITOR

            if selected_role not in permissions.ALL_ROLES:
                set_field_error(role_dd, "Vai trò không hợp lệ")
                has_error = True

            if not uname:
                set_field_error(username_field, "Vui lòng nhập tài khoản")
                has_error = True
            if not fname:
                set_field_error(fullname_field, "Vui lòng nhập họ và tên")
                has_error = True
            if not email or "@" not in email:
                set_field_error(email_field, "Email không hợp lệ")
                has_error = True
            if not phone:
                set_field_error(phone_field, "Vui lòng nhập số điện thoại")
                has_error = True
            if not pwd:
                set_field_error(password_field, "Vui lòng nhập mật khẩu")
                has_error = True

            if not is_edit and uname:
                for u in data.USERS_DATA:
                    if u["username"].lower() == uname.lower():
                        set_field_error(username_field, "Tài khoản đã tồn tại")
                        has_error = True
                        break

            # Kiểm tra bảo vệ Quản trị viên cuối cùng khi đổi vai trò
            if is_edit:
                was_admin = user_to_edit.get("role") == permissions.ROLE_ADMIN
                is_demoting = was_admin and selected_role != permissions.ROLE_ADMIN
                if is_demoting and user_to_edit.get("active", False) and count_active_admins() <= 1:
                    err_reason = "Không thể hạ vai trò của Quản trị viên cuối cùng còn lại trong hệ thống."
                    set_field_error(role_dd, "Quản trị viên cuối cùng")
                    form_error_text.value = err_reason
                    form_error_text.visible = True
                    show_snack(page, err_reason, is_error=True)
                    page.update()
                    return

            if has_error:
                page.update()
                return

            if is_edit:
                old_role = user_to_edit["role"]
                user_to_edit["full_name"] = fname
                user_to_edit["email"] = email
                user_to_edit["phone"] = phone
                user_to_edit["role"] = selected_role
                user_to_edit["password"] = pwd
                if is_current_logged_user(user_to_edit):
                    data.set_current_user(user_to_edit)
                    if on_user_updated:
                        on_user_updated()
                role_note = f" (đổi vai trò: {old_role} -> {selected_role})" if old_role != selected_role else ""
                data.log_activity(f"Cập nhật tài khoản '{fname}' ({uname}){role_note}.")
                msg = f"Đã lưu thông tin {uname}"
            else:
                new_user = {
                    "id": data.generate_next_id("USR", data.USERS_DATA),
                    "username": uname,
                    "password": pwd,
                    "full_name": fname,
                    "email": email,
                    "phone": phone,
                    "role": selected_role,
                    "active": True,
                    "created_at": datetime.now().strftime("%d/%m/%Y"),
                }
                data.USERS_DATA.insert(0, new_user)
                data.log_activity(f"Tạo tài khoản mới '{fname}' ({uname} - {selected_role}).")
                msg = f"Đã thêm tài khoản {uname}"

            close_dialog(page, dialog)
            refresh_table()
            show_snack(page, msg)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Cập nhật người dùng" if is_edit else "Thêm người dùng",
                size=theme.TEXT_16,
                weight=theme.WEIGHT_SEMI,
            ),
            content=ft.Container(
                width=460,
                content=ft.Column(
                    tight=True,
                    spacing=theme.SPACE_12,
                    controls=[
                        ft.Row(
                            spacing=theme.SPACE_12,
                            controls=[
                                ft.Container(expand=1, content=make_form_field("Tên đăng nhập *", username_field)),
                                ft.Container(expand=1, content=make_form_field("Vai trò *", role_dd)),
                            ],
                        ),
                        make_form_field("Họ và tên *", fullname_field),
                        ft.Row(
                            spacing=theme.SPACE_12,
                            controls=[
                                ft.Container(expand=1, content=make_form_field("Email *", email_field)),
                                ft.Container(expand=1, content=make_form_field("Điện thoại *", phone_field)),
                            ],
                        ),
                        make_form_field("Mật khẩu *", password_field),
                        form_error_text,
                    ],
                ),
            ),
            actions=[
                ft.TextButton("Hủy", on_click=lambda e: close_dialog(page, dialog)),
                make_primary_button("Lưu người dùng", on_click=handle_save_user),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        open_dialog(page, dialog)

    def handle_toggle_lock(user: dict, is_active: bool):
        if not permissions.can(data.get_current_role(), "users", "lock"):
            refresh_table()
            show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
            return

        if not is_active and is_current_logged_user(user):
            refresh_table()
            show_snack(page, "Không thể tự khóa tài khoản của chính mình đang đăng nhập.", is_error=True)
            return

        if (
            not is_active
            and user.get("role") == permissions.ROLE_ADMIN
            and user.get("active", False)
            and count_active_admins() <= 1
        ):
            refresh_table()
            show_snack(page, "Không thể khóa Quản trị viên đang hoạt động cuối cùng còn lại.", is_error=True)
            return

        user["active"] = is_active
        action_label = "Mở khóa" if is_active else "Khóa"
        data.log_activity(f"{action_label} tài khoản '{user['full_name']}' ({user['username']}).")
        refresh_table()
        show_snack(page, f"Đã {action_label.lower()} tài khoản {user['username']}")

    def handle_delete_user(user: dict):
        if not permissions.can(data.get_current_role(), "users", "delete"):
            show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
            return

        if is_current_logged_user(user):
            show_snack(page, "Không thể tự xóa tài khoản của chính mình đang đăng nhập.", is_error=True)
            return

        if (
            user.get("role") == permissions.ROLE_ADMIN
            and user.get("active", False)
            and count_active_admins() <= 1
        ):
            show_snack(page, "Không thể xóa Quản trị viên đang hoạt động cuối cùng còn lại.", is_error=True)
            return

        def confirm_delete():
            if not permissions.can(data.get_current_role(), "users", "delete"):
                show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
                return
            if is_current_logged_user(user):
                show_snack(page, "Không thể tự xóa tài khoản của chính mình đang đăng nhập.", is_error=True)
                return
            if (
                user.get("role") == permissions.ROLE_ADMIN
                and user.get("active", False)
                and count_active_admins() <= 1
            ):
                show_snack(page, "Không thể xóa Quản trị viên đang hoạt động cuối cùng còn lại.", is_error=True)
                return

            data.USERS_DATA.remove(user)
            data.log_activity(f"Xóa tài khoản '{user['full_name']}' ({user['username']}).")
            refresh_table()
            show_snack(page, f"Đã xóa tài khoản {user['username']}")

        show_confirm_delete_dialog(page, f"{user['full_name']} ({user['username']})", confirm_delete)

    def change_page(new_p: int):
        filter_state["page"] = new_p
        refresh_table()

    def refresh_table(update_page: bool = True):
        cur_role = data.get_current_role()
        can_lock = permissions.can(cur_role, "users", "lock")
        can_edit = permissions.can(cur_role, "users", "edit")
        can_delete = permissions.can(cur_role, "users", "delete")

        filtered = get_filtered_users()
        if not filtered:
            table_container.controls = [
                create_empty_state("Không tìm thấy tài khoản nào phù hợp.")
            ]
            if update_page:
                page.update()
            return

        page_size = int(data.SYSTEM_SETTINGS.get("rows_per_page", "10"))
        total_pages = max(1, (len(filtered) + page_size - 1) // page_size)
        if filter_state["page"] > total_pages:
            filter_state["page"] = total_pages
        cur_p = filter_state["page"]
        paged = filtered[(cur_p - 1) * page_size : cur_p * page_size]

        rows = []
        for u in paged:
            status_controls = []
            if can_lock:
                status_controls.append(
                    ft.Switch(
                        value=u["active"],
                        active_color=theme.accent_color(),
                        tooltip="Bật: Hoạt động / Tắt: Khóa",
                        on_change=lambda e, usr=u: handle_toggle_lock(usr, e.control.value),
                    )
                )
            status_controls.append(create_status_badge("Hoạt động" if u["active"] else "Đã khóa"))

            row_actions = []
            if can_edit:
                row_actions.append(
                    create_action_icon(
                        ft.Icons.EDIT_OUTLINED,
                        "Chỉnh sửa",
                        lambda e, usr=u: open_user_form_dialog(usr),
                    )
                )
            if can_delete:
                row_actions.append(
                    create_action_icon(
                        ft.Icons.DELETE_OUTLINE,
                        "Xóa tài khoản",
                        lambda e, usr=u: handle_delete_user(usr),
                        is_danger=True,
                    )
                )

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(u["username"], size=theme.TEXT_14, weight=theme.WEIGHT_SEMI)),
                        ft.DataCell(ft.Text(u["full_name"], size=theme.TEXT_14)),
                        ft.DataCell(ft.Text(u["email"], size=theme.TEXT_14, color=theme.text_secondary())),
                        ft.DataCell(ft.Text(u["phone"], size=theme.TEXT_14)),
                        ft.DataCell(create_role_badge(u["role"])),
                        ft.DataCell(
                            ft.Row(
                                spacing=theme.SPACE_8,
                                controls=status_controls,
                            )
                        ),
                        ft.DataCell(
                            ft.Row(
                                spacing=theme.SPACE_4,
                                controls=row_actions,
                            )
                        ),
                    ]
                )
            )

        table_container.controls = [
            create_styled_table(
                columns=[
                    ft.DataColumn(ft.Text("Tài khoản")),
                    ft.DataColumn(ft.Text("Họ và tên")),
                    ft.DataColumn(ft.Text("Email")),
                    ft.DataColumn(ft.Text("Số điện thoại")),
                    ft.DataColumn(ft.Text("Vai trò")),
                    ft.DataColumn(ft.Text("Trạng thái")),
                    ft.DataColumn(ft.Text("Thao tác")),
                ],
                rows=rows,
            ),
            create_pagination_bar(len(filtered), cur_p, page_size, change_page),
        ]
        if update_page:
            page.update()

    search_box = create_search_field(
        "Tìm theo tên, tài khoản, email, SĐT...",
        lambda e: (filter_state.update({"keyword": e.control.value or "", "page": 1}), refresh_table()),
        width=300,
    )
    role_filter = make_dropdown(
        label="Vai trò",
        options=["Tất cả"] + permissions.ALL_ROLES,
        value="Tất cả",
        on_change=lambda e: (filter_state.update({"role": e.control.value or "Tất cả", "page": 1}), refresh_table()),
        width=180,
    )

    header_actions = []
    if permissions.can(role, "users", "add"):
        header_actions.append(
            make_primary_button(
                "Thêm người dùng",
                icon_name=ft.Icons.PERSON_ADD_OUTLINED,
                on_click=lambda e: open_user_form_dialog(None),
            )
        )

    refresh_table(update_page=False)

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=theme.SPACE_16,
        controls=[
            create_page_header(
                title="Quản lý người dùng",
                subtitle="Quản lý tài khoản nhân sự vận hành và phân quyền truy cập hệ thống.",
                right_controls=header_actions,
            ),
            make_surface_box(
                padding=theme.SPACE_12,
                content=ft.Row(
                    spacing=theme.SPACE_12,
                    wrap=True,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[search_box, role_filter],
                ),
            ),
            table_container,
        ],
    )
