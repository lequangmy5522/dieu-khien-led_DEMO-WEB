from datetime import datetime
import inspect
import os
import flet as ft
import data
import permissions
import theme
from components import (
    ALIGN_CENTER,
    border_all,
    close_dialog,
    create_action_icon,
    create_empty_state,
    create_page_header,
    create_pagination_bar,
    create_search_field,
    create_styled_table,
    make_dropdown,
    make_form_field,
    make_primary_button,
    make_secondary_button,
    make_surface_box,
    make_text_field,
    open_dialog,
    pad_sym,
    set_field_error,
    show_confirm_delete_dialog,
    show_snack,
)


def build_view(page: ft.Page) -> ft.Column:
    """Trang Quản lý nội dung hiển thị: hỗ trợ chuyển đổi Bảng / Lưới, lọc danh mục, tải tệp và xem trước."""
    state = {
        "keyword": "",
        "category": "Tất cả",
        "view_mode": data.SYSTEM_SETTINGS.get("default_content_view", "grid"),
        "page": 1,
    }

    content_display_area = ft.Column(spacing=theme.SPACE_12)
    category_chips_row = ft.Row(spacing=theme.SPACE_8, wrap=True)

    file_picker = ft.FilePicker()
    if hasattr(page, "services"):
        page.services.append(file_picker)
    else:
        page.overlay.append(file_picker)

    def format_file_size(size_bytes: int | None, ext: str) -> str:
        if size_bytes and size_bytes > 0:
            mb = size_bytes / (1024 * 1024)
            if mb >= 1.0:
                return f"{mb:.1f} MB"
            kb = size_bytes / 1024
            return f"{max(1, int(kb))} KB"
        video_exts = {"MP4", "AVI", "MOV", "MKV"}
        return "41.8 MB" if ext.upper() in video_exts else "2.7 MB"

    def get_filtered_contents() -> list:
        kw = state["keyword"].strip().lower()
        cat = state["category"]
        results = []
        for item in data.CONTENTS_DATA:
            match_kw = (
                not kw
                or kw in item["name"].lower()
                or kw in item["description"].lower()
                or kw in item["format"].lower()
            )
            match_cat = cat == "Tất cả" or item["category"] == cat
            if match_kw and match_cat:
                results.append(item)
        return results

    def build_thumbnail_preview(item: dict, height: float = 128) -> ft.Container:
        """Khung xem trước trung tính, không dùng màu neon, có icon Play cho Video."""
        is_video = item["type"] == "Video"
        center_icon = ft.Icons.PLAY_CIRCLE_OUTLINE if is_video else ft.Icons.IMAGE_OUTLINED

        return ft.Container(
            height=height,
            border_radius=theme.RADIUS_INPUT,
            bgcolor=theme.surface_subtle_color(),
            border=border_all(theme.BORDER_WIDTH, theme.border_color()),
            alignment=ALIGN_CENTER,
            padding=theme.SPACE_12,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=theme.SPACE_8,
                controls=[
                    ft.Icon(center_icon, color=theme.accent_color() if is_video else theme.text_secondary(), size=32),
                    ft.Text(
                        f"{item['type']} · {item['format']} · {item['size']}",
                        color=theme.text_secondary(),
                        size=theme.TEXT_12,
                    ),
                ],
            ),
        )

    def open_preview_dialog(item: dict):
        if not permissions.can(data.get_current_role(), "contents", "preview"):
            show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
            return

        is_video = item["type"] == "Video"
        status_note = ft.Text(
            "Trạng thái: Sẵn sàng phát thử" if is_video else "Ảnh tĩnh đúng tỷ lệ khung hình",
            size=theme.TEXT_12,
            color=theme.text_secondary(),
        )

        def toggle_video_sim(e):
            if "Đang phát" in status_note.value:
                status_note.value = "Trạng thái: Đã tạm dừng"
            else:
                status_note.value = f"Trạng thái: Đang phát thử {item['name']} ({item['format']})"
            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(item["name"], size=theme.TEXT_16, weight=theme.WEIGHT_SEMI),
            content=ft.Container(
                width=480,
                content=ft.Column(
                    tight=True,
                    spacing=theme.SPACE_12,
                    controls=[
                        build_thumbnail_preview(item, height=192),
                        status_note,
                        ft.Row(
                            spacing=theme.SPACE_16,
                            wrap=True,
                            controls=[
                                ft.Text(f"Danh mục: {item['category']}", size=theme.TEXT_12, color=theme.text_secondary()),
                                ft.Text(f"Định dạng: {item['format']}", size=theme.TEXT_12, color=theme.text_secondary()),
                                ft.Text(f"Dung lượng: {item['size']}", size=theme.TEXT_12, color=theme.text_secondary()),
                                ft.Text(f"Ngày tải: {item['upload_date']}", size=theme.TEXT_12, color=theme.text_secondary()),
                            ],
                        ),
                        ft.Text(item["description"], size=theme.TEXT_14, color=theme.text_primary()),
                    ],
                ),
            ),
            actions=[
                ft.TextButton("Đóng", on_click=lambda e: close_dialog(page, dialog)),
                make_secondary_button(
                    "Phát / Tạm dừng",
                    icon_name=ft.Icons.PLAY_ARROW_OUTLINED,
                    on_click=toggle_video_sim,
                )
                if is_video
                else ft.Container(),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        open_dialog(page, dialog)

    def open_upload_dialog():
        if not permissions.can(data.get_current_role(), "contents", "add"):
            show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
            return

        picked_info = {
            "filename": "",
            "format": "MP4",
            "type": "Video",
            "size": "34.2 MB",
            "upload_date": datetime.now().strftime("%d/%m/%Y"),
        }

        name_field = make_text_field(hint_text="Nhập tên hiển thị của tệp")
        category_dd = make_dropdown(
            label="",
            options=data.CONTENT_CATEGORIES,
            value=data.CONTENT_CATEGORIES[0],
        )
        desc_field = make_text_field(
            hint_text="Ghi chú vị trí hoặc đợt phát sóng",
            multiline=True,
            min_lines=2,
            max_lines=3,
        )
        file_status_text = ft.Text(
            "Chưa chọn tệp tin.",
            size=theme.TEXT_12,
            color=theme.text_secondary(),
        )

        def apply_picked_file(f_obj):
            fname = getattr(f_obj, "name", "tvc_chi_nhanh.mp4")
            fsize = getattr(f_obj, "size", 0)
            _, ext = os.path.splitext(fname)
            ext_clean = ext.lstrip(".").upper() if ext else "MP4"
            video_exts = {"MP4", "AVI", "MOV", "MKV", "WEBM"}
            ctype = "Video" if ext_clean in video_exts else "Hình ảnh"

            picked_info["filename"] = fname
            picked_info["format"] = ext_clean
            picked_info["type"] = ctype
            picked_info["size"] = format_file_size(fsize, ext_clean)
            picked_info["upload_date"] = datetime.now().strftime("%d/%m/%Y")

            if not (name_field.value or "").strip():
                name_field.value = os.path.splitext(fname)[0].replace("_", " ").replace("-", " ")

            file_status_text.value = (
                f"Tệp: {fname} ({ctype} · {ext_clean} · {picked_info['size']} · {picked_info['upload_date']})"
            )
            file_status_text.color = theme.text_primary()
            page.update()

        def on_file_picker_result(e):
            files = getattr(e, "files", None)
            if files:
                apply_picked_file(files[0])

        file_picker.on_result = on_file_picker_result

        async def handle_pick_file(e):
            if inspect.iscoroutinefunction(file_picker.pick_files):
                files = await file_picker.pick_files(
                    dialog_title="Chọn tệp hình ảnh hoặc video",
                    file_type=ft.FilePickerFileType.CUSTOM,
                    allowed_extensions=["jpg", "jpeg", "png", "gif", "mp4", "avi", "mov", "mkv"],
                )
                if files:
                    apply_picked_file(files[0])
            else:
                file_picker.pick_files(
                    dialog_title="Chọn tệp hình ảnh hoặc video",
                    file_type=ft.FilePickerFileType.CUSTOM,
                    allowed_extensions=["jpg", "jpeg", "png", "gif", "mp4", "avi", "mov", "mkv"],
                )

        def simulate_sample_file(sample_ext: str):
            class _MockFile:
                name = f"noi_dung_trinh_chieu.{sample_ext.lower()}"
                size = 39426457 if sample_ext == "MP4" else 2936012

            apply_picked_file(_MockFile())

        def handle_save_new(e):
            if not permissions.can(data.get_current_role(), "contents", "add"):
                close_dialog(page, dialog)
                show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
                return

            set_field_error(name_field, None)
            set_field_error(desc_field, None)

            has_error = False
            if not (name_field.value or "").strip():
                set_field_error(name_field, "Vui lòng nhập tên nội dung")
                has_error = True
            if not (desc_field.value or "").strip():
                set_field_error(desc_field, "Vui lòng nhập ghi chú mô tả")
                has_error = True
            if not picked_info["filename"]:
                file_status_text.value = "Vui lòng chọn tệp từ máy hoặc dùng tệp mẫu bên trên."
                file_status_text.color = theme.STATUS_DANGER
                has_error = True

            if has_error:
                page.update()
                return

            new_item = {
                "id": data.generate_next_id("CNT", data.CONTENTS_DATA),
                "name": name_field.value.strip(),
                "type": picked_info["type"],
                "category": category_dd.value or "Quảng cáo",
                "format": picked_info["format"],
                "size": picked_info["size"],
                "upload_date": picked_info["upload_date"],
                "description": desc_field.value.strip(),
            }
            data.CONTENTS_DATA.insert(0, new_item)
            data.log_activity(f"Tải lên nội dung '{new_item['name']}' ({new_item['format']}, {new_item['size']}).")
            close_dialog(page, dialog)
            refresh_view()
            show_snack(page, f"Đã thêm nội dung {new_item['id']}")

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Tải tệp nội dung lên", size=theme.TEXT_16, weight=theme.WEIGHT_SEMI),
            content=ft.Container(
                width=480,
                content=ft.Column(
                    tight=True,
                    spacing=theme.SPACE_12,
                    controls=[
                        ft.Container(
                            padding=theme.SPACE_12,
                            border_radius=theme.RADIUS_INPUT,
                            bgcolor=theme.surface_subtle_color(),
                            border=border_all(theme.BORDER_WIDTH, theme.border_color()),
                            content=ft.Column(
                                spacing=theme.SPACE_8,
                                controls=[
                                    ft.Row(
                                        spacing=theme.SPACE_8,
                                        wrap=True,
                                        controls=[
                                            make_secondary_button(
                                                "Chọn tệp từ máy...",
                                                icon_name=ft.Icons.UPLOAD_FILE_OUTLINED,
                                                on_click=handle_pick_file,
                                            ),
                                            make_secondary_button(
                                                "Tệp mẫu MP4",
                                                on_click=lambda e: simulate_sample_file("MP4"),
                                            ),
                                            make_secondary_button(
                                                "Tệp mẫu PNG",
                                                on_click=lambda e: simulate_sample_file("PNG"),
                                            ),
                                        ],
                                    ),
                                    file_status_text,
                                ],
                            ),
                        ),
                        make_form_field("Tên nội dung *", name_field),
                        make_form_field("Danh mục *", category_dd),
                        make_form_field("Mô tả / Ghi chú *", desc_field),
                    ],
                ),
            ),
            actions=[
                ft.TextButton("Hủy", on_click=lambda e: close_dialog(page, dialog)),
                make_primary_button("Lưu nội dung", on_click=handle_save_new),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        open_dialog(page, dialog)

    def open_edit_dialog(item: dict):
        if not permissions.can(data.get_current_role(), "contents", "edit"):
            show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
            return

        name_field = make_text_field(value=item["name"])
        category_dd = make_dropdown(
            label="",
            options=data.CONTENT_CATEGORIES,
            value=item["category"],
        )
        desc_field = make_text_field(
            value=item["description"],
            multiline=True,
            min_lines=2,
            max_lines=3,
        )

        def handle_save_edit(e):
            if not permissions.can(data.get_current_role(), "contents", "edit"):
                close_dialog(page, dialog)
                show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
                return

            set_field_error(name_field, None)
            set_field_error(desc_field, None)
            has_error = False
            if not (name_field.value or "").strip():
                set_field_error(name_field, "Vui lòng nhập tên nội dung")
                has_error = True
            if not (desc_field.value or "").strip():
                set_field_error(desc_field, "Vui lòng nhập mô tả")
                has_error = True
            if has_error:
                page.update()
                return

            item["name"] = name_field.value.strip()
            item["category"] = category_dd.value or item["category"]
            item["description"] = desc_field.value.strip()
            data.log_activity(f"Cập nhật nội dung '{item['name']}' ({item['id']}).")
            close_dialog(page, dialog)
            refresh_view()
            show_snack(page, f"Đã cập nhật {item['id']}")

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Chỉnh sửa thông tin nội dung", size=theme.TEXT_16, weight=theme.WEIGHT_SEMI),
            content=ft.Container(
                width=440,
                content=ft.Column(
                    tight=True,
                    spacing=theme.SPACE_12,
                    controls=[
                        make_form_field("Tên nội dung *", name_field),
                        make_form_field("Danh mục *", category_dd),
                        make_form_field("Mô tả *", desc_field),
                    ],
                ),
            ),
            actions=[
                ft.TextButton("Hủy", on_click=lambda e: close_dialog(page, dialog)),
                make_primary_button("Lưu thay đổi", on_click=handle_save_edit),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        open_dialog(page, dialog)

    def handle_delete_content(item: dict):
        if not permissions.can(data.get_current_role(), "contents", "delete"):
            show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
            return

        def confirm_delete():
            if not permissions.can(data.get_current_role(), "contents", "delete"):
                show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
                return
            data.CONTENTS_DATA.remove(item)
            data.log_activity(f"Xóa nội dung '{item['name']}' ({item['id']}).")
            refresh_view()
            show_snack(page, f"Đã xóa {item['id']}")

        show_confirm_delete_dialog(page, item["name"], confirm_delete)

    def select_category(cat_name: str):
        state["category"] = cat_name
        state["page"] = 1
        category_filter_dd.value = cat_name
        refresh_view()

    def build_category_chips():
        all_cats = ["Tất cả"] + data.CONTENT_CATEGORIES
        chips = []
        for cat in all_cats:
            is_selected = state["category"] == cat
            chips.append(
                ft.Chip(
                    label=ft.Text(cat, size=theme.TEXT_12),
                    selected=is_selected,
                    on_select=lambda e, c=cat: select_category(c),
                )
            )
        category_chips_row.controls = chips

    def change_page(new_p: int):
        state["page"] = new_p
        refresh_view()

    def refresh_view():
        role = data.get_current_role()
        can_preview = permissions.can(role, "contents", "preview")
        can_edit = permissions.can(role, "contents", "edit")
        can_delete = permissions.can(role, "contents", "delete")

        build_category_chips()
        filtered = get_filtered_contents()

        if not filtered:
            content_display_area.controls = [
                create_empty_state("Không có tệp nội dung nào khớp với bộ lọc hiện tại.")
            ]
            page.update()
            return

        if state["view_mode"] == "grid":
            cards = []
            for item in filtered:
                card_actions = []
                if can_edit:
                    card_actions.append(
                        create_action_icon(
                            ft.Icons.EDIT_OUTLINED,
                            "Chỉnh sửa",
                            lambda e, it=item: open_edit_dialog(it),
                        )
                    )
                if can_delete:
                    card_actions.append(
                        create_action_icon(
                            ft.Icons.DELETE_OUTLINE,
                            "Xóa",
                            lambda e, it=item: handle_delete_content(it),
                            is_danger=True,
                        )
                    )

                cards.append(
                    make_surface_box(
                        col={"sm": 12, "md": 6, "lg": 4, "xl": 3},
                        padding=theme.SPACE_12,
                        content=ft.Column(
                            spacing=theme.SPACE_8,
                            controls=[
                                ft.GestureDetector(
                                    on_tap=lambda e, it=item: open_preview_dialog(it),
                                    content=build_thumbnail_preview(item, height=120),
                                ),
                                ft.Text(
                                    item["name"],
                                    weight=theme.WEIGHT_SEMI,
                                    size=theme.TEXT_14,
                                    color=theme.text_primary(),
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                    tooltip=item["name"],
                                ),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text(item["category"], size=theme.TEXT_12, color=theme.accent_color()),
                                        ft.Text(item["upload_date"], size=theme.TEXT_12, color=theme.text_secondary()),
                                    ],
                                ),
                                ft.Text(
                                    item["description"],
                                    size=theme.TEXT_12,
                                    color=theme.text_secondary(),
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.TextButton(
                                            "Xem trước",
                                            on_click=lambda e, it=item: open_preview_dialog(it),
                                        )
                                        if can_preview
                                        else ft.Container(),
                                        ft.Row(
                                            spacing=theme.SPACE_4,
                                            controls=card_actions,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    )
                )
            content_display_area.controls = [
                ft.ResponsiveRow(spacing=theme.SPACE_16, run_spacing=theme.SPACE_16, controls=cards)
            ]
        else:
            page_size = int(data.SYSTEM_SETTINGS.get("rows_per_page", "10"))
            total_pages = max(1, (len(filtered) + page_size - 1) // page_size)
            if state["page"] > total_pages:
                state["page"] = total_pages
            cur_p = state["page"]
            paged = filtered[(cur_p - 1) * page_size : cur_p * page_size]

            rows = []
            for item in paged:
                row_actions = []
                if can_preview:
                    row_actions.append(
                        create_action_icon(
                            ft.Icons.PLAY_CIRCLE_OUTLINE,
                            "Xem trước",
                            lambda e, it=item: open_preview_dialog(it),
                        )
                    )
                if can_edit:
                    row_actions.append(
                        create_action_icon(
                            ft.Icons.EDIT_OUTLINED,
                            "Chỉnh sửa",
                            lambda e, it=item: open_edit_dialog(it),
                        )
                    )
                if can_delete:
                    row_actions.append(
                        create_action_icon(
                            ft.Icons.DELETE_OUTLINE,
                            "Xóa",
                            lambda e, it=item: handle_delete_content(it),
                            is_danger=True,
                        )
                    )

                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(item["id"], size=theme.TEXT_14, weight=theme.WEIGHT_SEMI)),
                            ft.DataCell(
                                ft.Text(
                                    item["name"],
                                    size=theme.TEXT_14,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                    tooltip=item["name"],
                                )
                            ),
                            ft.DataCell(ft.Text(item["category"], size=theme.TEXT_14)),
                            ft.DataCell(ft.Text(f"{item['type']} ({item['format']})", size=theme.TEXT_14)),
                            ft.DataCell(ft.Text(item["size"], size=theme.TEXT_14)),
                            ft.DataCell(ft.Text(item["upload_date"], size=theme.TEXT_14)),
                            ft.DataCell(
                                ft.Row(
                                    spacing=theme.SPACE_4,
                                    controls=row_actions,
                                )
                            ),
                        ]
                    )
                )
            content_display_area.controls = [
                create_styled_table(
                    columns=[
                        ft.DataColumn(ft.Text("Mã")),
                        ft.DataColumn(ft.Text("Tên nội dung")),
                        ft.DataColumn(ft.Text("Danh mục")),
                        ft.DataColumn(ft.Text("Định dạng")),
                        ft.DataColumn(ft.Text("Dung lượng"), numeric=True),
                        ft.DataColumn(ft.Text("Ngày tải")),
                        ft.DataColumn(ft.Text("Thao tác")),
                    ],
                    rows=rows,
                ),
                create_pagination_bar(len(filtered), cur_p, page_size, change_page),
            ]
        page.update()

    def set_view_mode(mode: str):
        state["view_mode"] = mode
        grid_btn.bgcolor = theme.accent_subtle() if mode == "grid" else None
        table_btn.bgcolor = theme.accent_subtle() if mode == "table" else None
        refresh_view()

    search_box = create_search_field(
        "Tìm theo tên tệp, mô tả, định dạng...",
        lambda e: (state.update({"keyword": e.control.value or "", "page": 1}), refresh_view()),
        width=280,
    )

    category_filter_dd = make_dropdown(
        label="Danh mục",
        options=["Tất cả"] + data.CONTENT_CATEGORIES,
        value="Tất cả",
        on_change=lambda e: select_category(e.control.value or "Tất cả"),
        width=168,
    )

    grid_btn = ft.IconButton(
        icon=ft.Icons.GRID_VIEW_OUTLINED,
        icon_size=theme.ICON_SM,
        icon_color=theme.text_primary(),
        bgcolor=theme.accent_subtle() if state["view_mode"] == "grid" else None,
        tooltip="Xem dạng lưới",
        on_click=lambda e: set_view_mode("grid"),
    )
    table_btn = ft.IconButton(
        icon=ft.Icons.TABLE_ROWS_OUTLINED,
        icon_size=theme.ICON_SM,
        icon_color=theme.text_primary(),
        bgcolor=theme.accent_subtle() if state["view_mode"] == "table" else None,
        tooltip="Xem dạng bảng",
        on_click=lambda e: set_view_mode("table"),
    )

    role = data.get_current_role()
    header_actions = []
    if permissions.can(role, "contents", "add"):
        header_actions.append(
            make_primary_button(
                "Tải tệp lên",
                icon_name=ft.Icons.UPLOAD_FILE_OUTLINED,
                on_click=lambda e: open_upload_dialog(),
            )
        )

    refresh_view()

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=theme.SPACE_16,
        controls=[
            create_page_header(
                title="Quản lý nội dung",
                subtitle="Danh sách tệp quảng cáo, thông báo và sự kiện dùng để lập lịch phát.",
                right_controls=header_actions,
            ),
            make_surface_box(
                padding=theme.SPACE_12,
                content=ft.Column(
                    spacing=theme.SPACE_12,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            wrap=True,
                            controls=[
                                ft.Row(
                                    spacing=theme.SPACE_12,
                                    wrap=True,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[search_box, category_filter_dd],
                                ),
                                ft.Row(
                                    spacing=theme.SPACE_4,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Text("Hiển thị:", size=theme.TEXT_12, color=theme.text_secondary()),
                                        grid_btn,
                                        table_btn,
                                    ],
                                ),
                            ],
                        ),
                        category_chips_row,
                    ],
                ),
            ),
            content_display_area,
        ],
    )
