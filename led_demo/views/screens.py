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


def build_view(page: ft.Page) -> ft.Column:
    """Xây dựng giao diện Quản lý màn hình LED: tìm kiếm, lọc, thêm, sửa, xóa, xem chi tiết."""
    filter_state = {
        "keyword": "",
        "status": "Tất cả",
    }

    table_container = ft.Column(spacing=10)
    summary_text = ft.Text("", size=13, color=ft.Colors.GREY_600)

    def get_filtered_screens() -> list:
        """Lọc danh sách màn hình theo từ khóa (tên/mã thiết bị) và trạng thái."""
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
        """Hiển thị hộp thoại xem chi tiết đầy đủ thông tin một màn hình LED."""
        content_name = data.get_content_name(screen["current_content_id"])
        detail_rows = [
            ("Mã nội bộ:", screen["id"]),
            ("Mã thiết bị:", screen["code"]),
            ("Tên màn hình:", screen["name"]),
            ("Vị trí lắp đặt:", screen["location"]),
            ("Kích thước vật lý:", screen["size"]),
            ("Độ phân giải:", screen["resolution"]),
            ("Trạng thái kết nối:", screen["status"]),
            ("Trạng thái phát:", screen["playing_state"]),
            ("Nội dung đang phát:", content_name),
            ("Độ sáng / Âm lượng:", f"{screen['brightness']}% / {screen['volume']}%"),
            ("Nhiệt độ thiết bị:", f"{screen['temperature']}°C"),
            ("Thời gian hoạt động:", screen["uptime"]),
            ("Kết nối gần nhất:", screen["last_connected"]),
        ]

        info_controls = []
        for label, val in detail_rows:
            info_controls.append(
                ft.Row(
                    controls=[
                        ft.Text(label, weight=ft.FontWeight.W_600, width=165, size=13),
                        ft.Text(str(val), expand=True, size=13),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                )
            )

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.TV_ROUNDED, color=PRIMARY_COLOR),
                    ft.Text("Chi tiết màn hình LED", weight=ft.FontWeight.BOLD, size=18),
                ],
                spacing=8,
            ),
            content=ft.Container(
                width=460,
                content=ft.Column(
                    tight=True,
                    spacing=8,
                    controls=[
                        ft.Row(
                            controls=[
                                create_status_badge(screen["status"]),
                                create_status_badge(screen["playing_state"]),
                            ],
                            spacing=8,
                        ),
                        ft.Divider(height=8),
                        *info_controls,
                    ],
                ),
            ),
            actions=[
                ft.FilledButton(
                    "Đóng",
                    bgcolor=PRIMARY_COLOR,
                    color=ft.Colors.WHITE,
                    on_click=lambda e: close_dialog(page, dialog),
                )
            ],
        )
        open_dialog(page, dialog)

    def open_screen_form_dialog(screen_to_edit: dict | None = None):
        """Mở hộp thoại Thêm mới hoặc Chỉnh sửa màn hình LED có kiểm tra dữ liệu trống."""
        is_edit = screen_to_edit is not None

        name_field = ft.TextField(
            label="Tên màn hình LED *",
            value=screen_to_edit["name"] if is_edit else "",
            border_radius=8,
        )
        code_field = ft.TextField(
            label="Mã thiết bị *",
            value=screen_to_edit["code"] if is_edit else "",
            hint_text="Ví dụ: DEV-HN-011",
            border_radius=8,
        )
        location_field = ft.TextField(
            label="Vị trí lắp đặt *",
            value=screen_to_edit["location"] if is_edit else "",
            border_radius=8,
        )
        size_field = ft.TextField(
            label="Kích thước & Loại module *",
            value=screen_to_edit["size"] if is_edit else "",
            hint_text="Ví dụ: 5.0m x 3.0m (P2.5 Indoor)",
            border_radius=8,
        )
        resolution_field = ft.TextField(
            label="Độ phân giải *",
            value=screen_to_edit["resolution"] if is_edit else "1920 x 1080 px",
            border_radius=8,
        )
        status_dd = make_dropdown(
            label="Trạng thái *",
            options=["Online", "Offline", "Sự cố"],
            value=screen_to_edit["status"] if is_edit else "Online",
        )
        content_options = [(c["id"], f"{c['name']} ({c['type']})") for c in data.CONTENTS_DATA]
        content_dd = make_dropdown(
            label="Nội dung phát mặc định",
            options=content_options,
            value=screen_to_edit["current_content_id"]
            if is_edit
            else (data.CONTENTS_DATA[0]["id"] if data.CONTENTS_DATA else None),
        )

        def handle_save(e):
            # Xóa lỗi cũ
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

            # Kiểm tra trùng mã thiết bị
            code_val = (code_field.value or "").strip().upper()
            for s in data.SCREENS_DATA:
                if s["code"].upper() == code_val and (not is_edit or s["id"] != screen_to_edit["id"]):
                    set_field_error(code_field, "Mã thiết bị này đã tồn tại")
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
                data.log_activity(f"Đã cập nhật thông tin màn hình '{screen_to_edit['name']}' ({code_val}).")
                msg = f"Đã cập nhật màn hình \"{screen_to_edit['name']}\"!"
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
                    "temperature": 40 if new_status == "Online" else (65 if new_status == "Sự cố" else 32),
                    "uptime": "00 ngày 01 giờ" if new_status != "Offline" else "00 ngày 00 giờ",
                    "last_connected": "Vừa xong",
                }
                data.SCREENS_DATA.insert(0, new_screen)
                data.log_activity(f"Đã thêm màn hình LED mới '{new_screen['name']}' ({code_val}).")
                msg = f"Đã thêm màn hình \"{new_screen['name']}\" thành công!"

            close_dialog(page, dialog)
            refresh_table()
            show_snack(page, msg)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Chỉnh sửa màn hình LED" if is_edit else "Thêm màn hình LED mới",
                weight=ft.FontWeight.BOLD,
                size=18,
            ),
            content=ft.Container(
                width=480,
                content=ft.Column(
                    tight=True,
                    spacing=12,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        name_field,
                        code_field,
                        location_field,
                        size_field,
                        resolution_field,
                        status_dd,
                        content_dd,
                    ],
                ),
            ),
            actions=[
                ft.OutlinedButton("Hủy", on_click=lambda e: close_dialog(page, dialog)),
                ft.FilledButton(
                    "Lưu thông tin",
                    icon=ft.Icons.SAVE,
                    bgcolor=PRIMARY_COLOR,
                    color=ft.Colors.WHITE,
                    on_click=handle_save,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        open_dialog(page, dialog)

    def handle_delete_screen(screen: dict):
        """Xác nhận và xóa màn hình khỏi danh sách."""
        def confirm_delete():
            data.SCREENS_DATA.remove(screen)
            data.log_activity(f"Đã xóa màn hình LED '{screen['name']}' ({screen['code']}).")
            refresh_table()
            show_snack(page, f"Đã xóa màn hình \"{screen['name']}\"!")

        show_confirm_delete_dialog(page, f"{screen['name']} ({screen['code']})", confirm_delete)

    def refresh_table():
        """Vẽ lại bảng danh sách màn hình LED theo bộ lọc hiện tại."""
        filtered = get_filtered_screens()
        summary_text.value = f"Hiển thị {len(filtered)} / {len(data.SCREENS_DATA)} màn hình LED"

        rows = []
        for scr in filtered:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(scr["code"], weight=ft.FontWeight.BOLD, size=13)),
                        ft.DataCell(ft.Text(scr["name"], weight=ft.FontWeight.W_500, size=13)),
                        ft.DataCell(ft.Text(scr["location"], size=13)),
                        ft.DataCell(ft.Text(scr["size"], size=12)),
                        ft.DataCell(create_status_badge(scr["status"])),
                        ft.DataCell(
                            ft.Row(
                                spacing=4,
                                controls=[
                                    ft.IconButton(
                                        icon=ft.Icons.VISIBILITY_OUTLINED,
                                        icon_color=PRIMARY_COLOR,
                                        tooltip="Xem chi tiết",
                                        on_click=lambda e, s=scr: open_detail_dialog(s),
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT_OUTLINED,
                                        icon_color=ft.Colors.AMBER_800,
                                        tooltip="Chỉnh sửa",
                                        on_click=lambda e, s=scr: open_screen_form_dialog(s),
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE,
                                        icon_color=ft.Colors.RED_600,
                                        tooltip="Xóa màn hình",
                                        on_click=lambda e, s=scr: handle_delete_screen(s),
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
                        column_spacing=22,
                        heading_row_height=44,
                        data_row_min_height=48,
                        columns=[
                            ft.DataColumn(ft.Text("Mã thiết bị", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Tên màn hình LED", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Vị trí lắp đặt", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Kích thước", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Trạng thái", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Thao tác", weight=ft.FontWeight.BOLD)),
                        ],
                        rows=rows,
                    )
                ],
            )
            if rows
            else ft.Container(
                padding=30,
                content=ft.Text("Không tìm thấy màn hình LED nào phù hợp với bộ lọc.", italic=True),
            )
        ]
        page.update()

    def on_search_change(e):
        filter_state["keyword"] = e.control.value or ""
        refresh_table()

    def on_status_change(e):
        filter_state["status"] = e.control.value or "Tất cả"
        refresh_table()

    search_box = create_search_field("Tìm theo tên, mã thiết bị, vị trí...", on_search_change, width=320)
    status_filter = make_dropdown(
        label="Trạng thái",
        options=["Tất cả", "Online", "Offline", "Sự cố"],
        value="Tất cả",
        on_change=on_status_change,
        width=180,
    )

    refresh_table()

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=16,
        controls=[
            create_page_header(
                title="Quản lý màn hình LED",
                subtitle="Quản lý danh sách thiết bị, kích thước, vị trí lắp đặt và trạng thái kết nối.",
                right_controls=[
                    ft.FilledButton(
                        "Thêm màn hình LED",
                        icon=ft.Icons.ADD_TO_QUEUE,
                        bgcolor=PRIMARY_COLOR,
                        color=ft.Colors.WHITE,
                        on_click=lambda e: open_screen_form_dialog(None),
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
                                    ft.Row(
                                        spacing=12,
                                        wrap=True,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[search_box, status_filter],
                                    ),
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
