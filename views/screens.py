import flet as ft
import data
import permissions
import theme
from components import (
    border_only,
    close_dialog,
    create_action_icon,
    create_empty_state,
    create_page_header,
    create_pagination_bar,
    create_search_field,
    create_status_badge,
    create_styled_table,
    make_dropdown,
    make_form_field,
    make_primary_button,
    make_surface_box,
    make_text_field,
    open_dialog,
    pad_sym,
    set_field_error,
    show_confirm_delete_dialog,
    show_snack,
)


def build_view(page: ft.Page) -> ft.Column:
    """Trang Quản lý màn hình LED: thanh công cụ tìm kiếm + lọc, bảng dữ liệu và phân trang."""
    filter_state = {
        "keyword": "",
        "status": "Tất cả",
        "page": 1,
    }

    table_container = ft.Column(spacing=0)

    def get_filtered_screens() -> list:
        kw = filter_state["keyword"].strip().lower()
        st = filter_state["status"]
        results = []
        for s in data.SCREENS_DATA:
            match_kw = (
                not kw
                or kw in s["name"].lower()
                or kw in s["code"].lower()
                or kw in s["location"].lower()
            )
            match_st = st == "Tất cả" or s["status"] == st
            if match_kw and match_st:
                results.append(s)
        return results

    def open_detail_dialog(screen: dict):
        """Hộp thoại thông tin chi tiết thiết bị."""
        if not permissions.can(data.get_current_role(), "screens", "detail"):
            show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
            return

        content_name = data.get_content_name(screen["current_content_id"])
        detail_rows = [
            ("Mã thiết bị", f"{screen['code']} (ID: {screen['id']})"),
            ("Tên màn hình", screen["name"]),
            ("Vị trí lắp đặt", screen["location"]),
            ("Cấu hình phần cứng", screen["size"]),
            ("Độ phân giải", screen["resolution"]),
            ("Nội dung đang gán", content_name),
            ("Độ sáng / Âm lượng", f"{screen['brightness']}% / {screen['volume']}%"),
            ("Nhiệt độ đo được", f"{screen['temperature']}°C"),
            ("Thời gian chạy liên tục", screen["uptime"]),
            ("Đồng bộ gần nhất", screen["last_connected"]),
        ]

        info_controls = []
        for idx, (label, val) in enumerate(detail_rows):
            info_controls.append(
                ft.Container(
                    padding=pad_sym(vertical=theme.SPACE_8),
                    border=border_only(bottom=ft.BorderSide(theme.BORDER_WIDTH, theme.border_color()))
                    if idx < len(detail_rows) - 1
                    else None,
                    content=ft.Row(
                        controls=[
                            ft.Text(label, size=theme.TEXT_12, color=theme.text_secondary(), width=148),
                            ft.Text(str(val), size=theme.TEXT_14, color=theme.text_primary(), expand=True),
                        ],
                    ),
                )
            )

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Thông số thiết bị", size=theme.TEXT_16, weight=theme.WEIGHT_SEMI),
            content=ft.Container(
                width=460,
                content=ft.Column(
                    tight=True,
                    spacing=theme.SPACE_8,
                    controls=[
                        ft.Row(
                            spacing=theme.SPACE_16,
                            controls=[
                                create_status_badge(screen["status"]),
                                create_status_badge(screen["playing_state"]),
                            ],
                        ),
                        ft.Column(spacing=0, controls=info_controls),
                    ],
                ),
            ),
            actions=[
                ft.TextButton(
                    "Đóng",
                    on_click=lambda e: close_dialog(page, dialog),
                )
            ],
        )
        open_dialog(page, dialog)

    def open_screen_form_dialog(screen_to_edit: dict | None = None):
        """Form thêm mới / chỉnh sửa màn hình với kiểm tra quyền ở tầng xử lý."""
        is_edit = screen_to_edit is not None
        required_action = "edit" if is_edit else "add"
        if not permissions.can(data.get_current_role(), "screens", required_action):
            show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
            return

        name_field = make_text_field(
            value=screen_to_edit["name"] if is_edit else "",
            hint_text="VD: LED mặt tiền Chi nhánh Biên Hòa",
        )
        code_field = make_text_field(
            value=screen_to_edit["code"] if is_edit else "",
            hint_text="VD: LED-BH-011",
        )
        location_field = make_text_field(
            value=screen_to_edit["location"] if is_edit else "",
            hint_text="VD: Số 128 Phạm Văn Thuận, TP. Biên Hòa",
        )
        size_field = make_text_field(
            value=screen_to_edit["size"] if is_edit else "",
            hint_text="VD: P4 Outdoor, 6m x 3m",
        )
        resolution_field = make_text_field(
            value=screen_to_edit["resolution"] if is_edit else "1920 x 1080 px",
            hint_text="VD: 1920 x 1080 px",
        )
        status_dd = make_dropdown(
            label="",
            options=["Online", "Offline", "Sự cố"],
            value=screen_to_edit["status"] if is_edit else "Online",
        )
        content_options = [(c["id"], f"{c['name']} ({c['format']})") for c in data.CONTENTS_DATA]
        content_dd = make_dropdown(
            label="",
            options=content_options,
            value=screen_to_edit["current_content_id"]
            if is_edit
            else (data.CONTENTS_DATA[0]["id"] if data.CONTENTS_DATA else None),
        )

        def handle_save(e):
            if not permissions.can(data.get_current_role(), "screens", required_action):
                close_dialog(page, dialog)
                show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
                return

            for fld in [name_field, code_field, location_field, size_field, resolution_field]:
                set_field_error(fld, None)

            has_error = False
            if not (name_field.value or "").strip():
                set_field_error(name_field, "Vui lòng nhập tên màn hình")
                has_error = True
            if not (code_field.value or "").strip():
                set_field_error(code_field, "Vui lòng nhập mã thiết bị")
                has_error = True
            if not (location_field.value or "").strip():
                set_field_error(location_field, "Vui lòng nhập vị trí lắp đặt")
                has_error = True
            if not (size_field.value or "").strip():
                set_field_error(size_field, "Vui lòng nhập kích thước")
                has_error = True
            if not (resolution_field.value or "").strip():
                set_field_error(resolution_field, "Vui lòng nhập độ phân giải")
                has_error = True

            code_val = (code_field.value or "").strip().upper()
            for s in data.SCREENS_DATA:
                if s["code"].upper() == code_val and (not is_edit or s["id"] != screen_to_edit["id"]):
                    set_field_error(code_field, "Mã thiết bị đã tồn tại")
                    has_error = True
                    break

            if has_error:
                page.update()
                return

            new_status = status_dd.value or "Online"
            playing_state = (
                "Đang phát"
                if new_status == "Online"
                else ("Đã dừng" if new_status == "Offline" else "Gián đoạn")
            )

            if is_edit:
                screen_to_edit["name"] = name_field.value.strip()
                screen_to_edit["code"] = code_val
                screen_to_edit["location"] = location_field.value.strip()
                screen_to_edit["size"] = size_field.value.strip()
                screen_to_edit["resolution"] = resolution_field.value.strip()
                screen_to_edit["status"] = new_status
                screen_to_edit["playing_state"] = playing_state
                screen_to_edit["current_content_id"] = content_dd.value
                data.log_activity(f"Cập nhật màn hình '{screen_to_edit['name']}' ({code_val}).")
                msg = f"Đã lưu thay đổi cho {code_val}"
            else:
                new_screen = {
                    "id": data.generate_next_id("LED", data.SCREENS_DATA),
                    "name": name_field.value.strip(),
                    "code": code_val,
                    "location": location_field.value.strip(),
                    "size": size_field.value.strip(),
                    "resolution": resolution_field.value.strip(),
                    "status": new_status,
                    "playing_state": playing_state,
                    "current_content_id": content_dd.value,
                    "brightness": 80,
                    "volume": 50,
                    "temperature": 41 if new_status == "Online" else (64 if new_status == "Sự cố" else 31),
                    "uptime": "0 ngày 01 giờ" if new_status != "Offline" else "0 ngày 00 giờ",
                    "last_connected": "Vừa xong",
                }
                data.SCREENS_DATA.insert(0, new_screen)
                data.log_activity(f"Thêm mới màn hình '{new_screen['name']}' ({code_val}).")
                msg = f"Đã thêm màn hình {code_val}"

            close_dialog(page, dialog)
            refresh_table()
            show_snack(page, msg)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Cập nhật màn hình LED" if is_edit else "Thêm màn hình LED",
                size=theme.TEXT_16,
                weight=theme.WEIGHT_SEMI,
            ),
            content=ft.Container(
                width=480,
                content=ft.Column(
                    tight=True,
                    spacing=theme.SPACE_12,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Row(
                            spacing=theme.SPACE_12,
                            controls=[
                                ft.Container(expand=2, content=make_form_field("Tên màn hình *", name_field)),
                                ft.Container(expand=1, content=make_form_field("Mã thiết bị *", code_field)),
                            ],
                        ),
                        make_form_field("Địa điểm lắp đặt *", location_field),
                        ft.Row(
                            spacing=theme.SPACE_12,
                            controls=[
                                ft.Container(expand=1, content=make_form_field("Loại module & Kích thước *", size_field)),
                                ft.Container(expand=1, content=make_form_field("Độ phân giải *", resolution_field)),
                            ],
                        ),
                        ft.Row(
                            spacing=theme.SPACE_12,
                            controls=[
                                ft.Container(expand=1, content=make_form_field("Trạng thái", status_dd)),
                                ft.Container(expand=2, content=make_form_field("Nội dung mặc định", content_dd)),
                            ],
                        ),
                    ],
                ),
            ),
            actions=[
                ft.TextButton("Hủy", on_click=lambda e: close_dialog(page, dialog)),
                make_primary_button("Lưu thông tin", on_click=handle_save),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        open_dialog(page, dialog)

    def handle_delete_screen(screen: dict):
        if not permissions.can(data.get_current_role(), "screens", "delete"):
            show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
            return

        def confirm_delete():
            if not permissions.can(data.get_current_role(), "screens", "delete"):
                show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
                return
            data.SCREENS_DATA.remove(screen)
            data.log_activity(f"Xóa màn hình '{screen['name']}' ({screen['code']}).")
            refresh_table()
            show_snack(page, f"Đã xóa {screen['code']}")

        show_confirm_delete_dialog(page, f"{screen['name']} ({screen['code']})", confirm_delete)

    def change_page(new_page: int):
        filter_state["page"] = new_page
        refresh_table()

    def refresh_table():
        role = data.get_current_role()
        can_detail = permissions.can(role, "screens", "detail")
        can_edit = permissions.can(role, "screens", "edit")
        can_delete = permissions.can(role, "screens", "delete")

        filtered = get_filtered_screens()
        page_size = int(data.SYSTEM_SETTINGS.get("rows_per_page", "10"))
        total_pages = max(1, (len(filtered) + page_size - 1) // page_size)
        if filter_state["page"] > total_pages:
            filter_state["page"] = total_pages
        cur_p = filter_state["page"]
        paged_items = filtered[(cur_p - 1) * page_size : cur_p * page_size]

        if not paged_items:
            table_container.controls = [
                create_empty_state("Không tìm thấy màn hình LED nào khớp với từ khóa hoặc trạng thái đã chọn.")
            ]
            page.update()
            return

        rows = []
        for scr in paged_items:
            row_actions = []
            if can_detail:
                row_actions.append(
                    create_action_icon(
                        ft.Icons.VISIBILITY_OUTLINED,
                        "Xem chi tiết",
                        lambda e, s=scr: open_detail_dialog(s),
                    )
                )
            if can_edit:
                row_actions.append(
                    create_action_icon(
                        ft.Icons.EDIT_OUTLINED,
                        "Chỉnh sửa",
                        lambda e, s=scr: open_screen_form_dialog(s),
                    )
                )
            if can_delete:
                row_actions.append(
                    create_action_icon(
                        ft.Icons.DELETE_OUTLINE,
                        "Xóa thiết bị",
                        lambda e, s=scr: handle_delete_screen(s),
                        is_danger=True,
                    )
                )

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(scr["code"], size=theme.TEXT_14, weight=theme.WEIGHT_SEMI)),
                        ft.DataCell(
                            ft.Text(
                                scr["name"],
                                size=theme.TEXT_14,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                                tooltip=scr["name"],
                            )
                        ),
                        ft.DataCell(
                            ft.Text(
                                scr["location"],
                                size=theme.TEXT_14,
                                color=theme.text_secondary(),
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                                tooltip=scr["location"],
                            )
                        ),
                        ft.DataCell(ft.Text(scr["size"], size=theme.TEXT_14)),
                        ft.DataCell(create_status_badge(scr["status"])),
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
                    ft.DataColumn(ft.Text("Mã thiết bị")),
                    ft.DataColumn(ft.Text("Tên màn hình")),
                    ft.DataColumn(ft.Text("Vị trí lắp đặt")),
                    ft.DataColumn(ft.Text("Cấu hình")),
                    ft.DataColumn(ft.Text("Trạng thái")),
                    ft.DataColumn(ft.Text("Thao tác")),
                ],
                rows=rows,
            ),
            create_pagination_bar(len(filtered), cur_p, page_size, change_page),
        ]
        page.update()

    def on_search_change(e):
        filter_state["keyword"] = e.control.value or ""
        filter_state["page"] = 1
        refresh_table()

    def on_status_change(e):
        filter_state["status"] = e.control.value or "Tất cả"
        filter_state["page"] = 1
        refresh_table()

    search_box = create_search_field("Tìm theo mã, tên màn hình, địa điểm...", on_search_change, width=300)
    status_filter = make_dropdown(
        label="Trạng thái",
        options=["Tất cả", "Online", "Offline", "Sự cố"],
        value="Tất cả",
        on_change=on_status_change,
        width=168,
    )

    role = data.get_current_role()
    header_actions = []
    if permissions.can(role, "screens", "add"):
        header_actions.append(
            make_primary_button(
                "Thêm màn hình",
                icon_name=ft.Icons.ADD_OUTLINED,
                on_click=lambda e: open_screen_form_dialog(None),
            )
        )

    refresh_table()

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=theme.SPACE_16,
        controls=[
            create_page_header(
                title="Quản lý màn hình LED",
                subtitle="Danh sách điểm lắp đặt, cấu hình phần cứng và trạng thái kết nối.",
                right_controls=header_actions,
            ),
            make_surface_box(
                padding=theme.SPACE_12,
                content=ft.Row(
                    spacing=theme.SPACE_12,
                    wrap=True,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[search_box, status_filter],
                ),
            ),
            table_container,
        ],
    )
