from datetime import datetime
import inspect
import os
import flet as ft
import data
from components import (
    PRIMARY_COLOR,
    PRIMARY_LIGHT,
    ALIGN_CENTER,
    border_all,
    close_dialog,
    create_page_header,
    create_search_field,
    make_dropdown,
    open_dialog,
    pad_sym,
    set_field_error,
    show_confirm_delete_dialog,
    show_snack,
)


def build_view(page: ft.Page) -> ft.Column:
    """Xây dựng giao diện Quản lý nội dung hiển thị: Lưới thẻ / Bảng, tải file, xem trước, sửa, xóa."""
    state = {
        "keyword": "",
        "category": "Tất cả",
        "view_mode": data.SYSTEM_SETTINGS.get("default_content_view", "grid"),
    }

    content_display_area = ft.Column(spacing=12)
    category_chips_row = ft.Row(spacing=8, wrap=True)
    summary_text = ft.Text("", size=13, color=ft.Colors.GREY_600)

    # Khởi tạo FilePicker tương thích Flet 1.x (page.services) và Flet 0.28 (page.overlay)
    file_picker = ft.FilePicker()
    if hasattr(page, "services"):
        page.services.append(file_picker)
    else:
        page.overlay.append(file_picker)

    def format_file_size(size_bytes: int | None, ext: str) -> str:
        """Định dạng dung lượng file sang MB/KB; nếu không đọc được thì trả về giá trị giả hợp lý."""
        if size_bytes and size_bytes > 0:
            mb = size_bytes / (1024 * 1024)
            if mb >= 1.0:
                return f"{mb:.1f} MB"
            kb = size_bytes / 1024
            return f"{max(1, int(kb))} KB"
        # Giá trị giả hợp lý khi trình duyệt/OS không trả về dung lượng
        video_exts = {"MP4", "AVI", "MOV", "MKV"}
        return "48.5 MB" if ext.upper() in video_exts else "3.6 MB"

    def get_filtered_contents() -> list:
        """Lọc nội dung theo từ khóa và danh mục."""
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

    def build_thumbnail_preview(item: dict, height: float = 135) -> ft.Container:
        """Tạo khung thumbnail mô phỏng cho Hình ảnh hoặc Video (kèm icon Play)."""
        is_video = item["type"] == "Video"
        bg_color = ft.Colors.INDIGO_900 if is_video else ft.Colors.BLUE_700
        center_icon = ft.Icons.PLAY_CIRCLE_FILL if is_video else ft.Icons.IMAGE_ROUNDED

        return ft.Container(
            height=height,
            border_radius=10,
            bgcolor=bg_color,
            alignment=ALIGN_CENTER,
            padding=12,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6,
                controls=[
                    ft.Icon(center_icon, color=ft.Colors.WHITE, size=44),
                    ft.Container(
                        bgcolor=ft.Colors.with_opacity(0.25, ft.Colors.BLACK),
                        padding=pad_sym(horizontal=10, vertical=3),
                        border_radius=12,
                        content=ft.Text(
                            f"{item['type']} • {item['format']} • {item['size']}",
                            color=ft.Colors.WHITE,
                            size=11,
                            weight=ft.FontWeight.W_600,
                        ),
                    ),
                ],
            ),
        )

    def open_preview_dialog(item: dict):
        """Mở hộp thoại xem trước hình ảnh hoặc mô phỏng phát video."""
        is_video = item["type"] == "Video"
        status_note = ft.Text(
            "Đang mô phỏng trình phát Video (Nhấn Tạm dừng / Phát lại để thử)"
            if is_video
            else "Đang hiển thị bản xem trước hình ảnh độ phân giải cao",
            size=12,
            color=ft.Colors.GREY_600,
        )

        def toggle_video_sim(e):
            if "Đang phát" in status_note.value:
                status_note.value = "Đã tạm dừng phát video mô phỏng."
            else:
                status_note.value = f"Đang phát mô phỏng: {item['name']} ({item['format']})..."
            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                spacing=8,
                controls=[
                    ft.Icon(
                        ft.Icons.ONDEMAND_VIDEO if is_video else ft.Icons.PHOTO_LIBRARY,
                        color=PRIMARY_COLOR,
                    ),
                    ft.Text(f"Xem trước: {item['name']}", weight=ft.FontWeight.BOLD, size=17, expand=True),
                ],
            ),
            content=ft.Container(
                width=520,
                content=ft.Column(
                    tight=True,
                    spacing=12,
                    controls=[
                        build_thumbnail_preview(item, height=220),
                        status_note,
                        ft.Divider(height=4),
                        ft.Row(
                            spacing=16,
                            wrap=True,
                            controls=[
                                ft.Text(f"Danh mục: {item['category']}", size=13, weight=ft.FontWeight.W_600),
                                ft.Text(f"Định dạng: {item['format']}", size=13),
                                ft.Text(f"Dung lượng: {item['size']}", size=13),
                                ft.Text(f"Ngày tải lên: {item['upload_date']}", size=13),
                            ],
                        ),
                        ft.Text(f"Mô tả: {item['description']}", size=13),
                    ],
                ),
            ),
            actions=[
                ft.OutlinedButton(
                    "Phát / Tạm dừng Video",
                    icon=ft.Icons.PLAY_ARROW,
                    visible=is_video,
                    on_click=toggle_video_sim,
                ),
                ft.FilledButton(
                    "Đóng",
                    bgcolor=PRIMARY_COLOR,
                    color=ft.Colors.WHITE,
                    on_click=lambda e: close_dialog(page, dialog),
                ),
            ],
        )
        open_dialog(page, dialog)

    def open_upload_dialog():
        """Hộp thoại thêm nội dung mới thông qua ft.FilePicker."""
        picked_info = {
            "filename": "",
            "format": "MP4",
            "type": "Video",
            "size": "32.0 MB",
            "upload_date": datetime.now().strftime("%d/%m/%Y"),
        }

        name_field = ft.TextField(label="Tên nội dung hiển thị *", border_radius=8)
        category_dd = make_dropdown(
            label="Danh mục phân loại *",
            options=data.CONTENT_CATEGORIES,
            value=data.CONTENT_CATEGORIES[0],
        )
        desc_field = ft.TextField(
            label="Mô tả nội dung *",
            multiline=True,
            min_lines=2,
            max_lines=3,
            border_radius=8,
        )
        file_status_text = ft.Text(
            "Chưa chọn tệp nào (Nhấn 'Chọn tệp từ máy tính' bên dưới)",
            size=12,
            color=ft.Colors.GREY_700,
        )

        def apply_picked_file(f_obj):
            """Cập nhật thông tin từ tệp đã chọn qua FilePicker."""
            fname = getattr(f_obj, "name", "noi_dung_moi.mp4")
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
                name_field.value = os.path.splitext(fname)[0].replace("_", " ").replace("-", " ").title()

            file_status_text.value = (
                f"Đã chọn: {fname} | Loại: {ctype} | Định dạng: {ext_clean} | "
                f"Dung lượng: {picked_info['size']} | Ngày tải: {picked_info['upload_date']}"
            )
            file_status_text.color = PRIMARY_COLOR
            page.update()

        def on_file_picker_result(e):
            files = getattr(e, "files", None)
            if files:
                apply_picked_file(files[0])

        file_picker.on_result = on_file_picker_result

        async def handle_pick_file(e):
            if inspect.iscoroutinefunction(file_picker.pick_files):
                files = await file_picker.pick_files(
                    dialog_title="Chọn tệp Hình ảnh hoặc Video",
                    file_type=ft.FilePickerFileType.CUSTOM,
                    allowed_extensions=["jpg", "jpeg", "png", "gif", "mp4", "avi", "mov", "mkv"],
                )
                if files:
                    apply_picked_file(files[0])
            else:
                file_picker.pick_files(
                    dialog_title="Chọn tệp Hình ảnh hoặc Video",
                    file_type=ft.FilePickerFileType.CUSTOM,
                    allowed_extensions=["jpg", "jpeg", "png", "gif", "mp4", "avi", "mov", "mkv"],
                )

        def handle_save_new(e):
            set_field_error(name_field, None)
            set_field_error(desc_field, None)

            has_error = False
            if not (name_field.value or "").strip():
                set_field_error(name_field, "Vui lòng nhập tên nội dung")
                has_error = True
            if not (desc_field.value or "").strip():
                set_field_error(desc_field, "Vui lòng nhập mô tả nội dung")
                has_error = True
            if not picked_info["filename"]:
                file_status_text.value = "Lỗi: Vui lòng chọn một tệp ảnh/video hoặc nhấn 'Giả lập tệp mẫu'!"
                file_status_text.color = ft.Colors.RED_600
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
            data.log_activity(f"Đã tải lên nội dung mới '{new_item['name']}' ({new_item['format']}, {new_item['size']}).")
            close_dialog(page, dialog)
            refresh_view()
            show_snack(page, f"Đã tải lên \"{new_item['name']}\" thành công!")

        def simulate_sample_file(sample_ext: str):
            """Hỗ trợ chọn nhanh file mẫu trong trường hợp chạy trên trình duyệt chặn hộp thoại OS."""
            class _MockFile:
                name = f"tvc_quang_cao_led.{sample_ext.lower()}"
                size = 36700160 if sample_ext == "MP4" else 4194304

            apply_picked_file(_MockFile())

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Tải lên nội dung hiển thị mới", weight=ft.FontWeight.BOLD, size=18),
            content=ft.Container(
                width=500,
                content=ft.Column(
                    tight=True,
                    spacing=12,
                    controls=[
                        ft.Container(
                            padding=12,
                            border_radius=10,
                            bgcolor=PRIMARY_LIGHT,
                            border=border_all(1, ft.Colors.BLUE_200),
                            content=ft.Column(
                                spacing=8,
                                controls=[
                                    ft.Row(
                                        spacing=10,
                                        wrap=True,
                                        controls=[
                                            ft.FilledButton(
                                                "Chọn tệp từ máy tính",
                                                icon=ft.Icons.UPLOAD_FILE,
                                                bgcolor=PRIMARY_COLOR,
                                                color=ft.Colors.WHITE,
                                                on_click=handle_pick_file,
                                            ),
                                            ft.OutlinedButton(
                                                "Mẫu Video MP4",
                                                icon=ft.Icons.MOVIE_CREATION_OUTLINED,
                                                on_click=lambda e: simulate_sample_file("MP4"),
                                            ),
                                            ft.OutlinedButton(
                                                "Mẫu Ảnh PNG",
                                                icon=ft.Icons.IMAGE_OUTLINED,
                                                on_click=lambda e: simulate_sample_file("PNG"),
                                            ),
                                        ],
                                    ),
                                    file_status_text,
                                ],
                            ),
                        ),
                        name_field,
                        category_dd,
                        desc_field,
                    ],
                ),
            ),
            actions=[
                ft.OutlinedButton("Hủy", on_click=lambda e: close_dialog(page, dialog)),
                ft.FilledButton(
                    "Lưu nội dung",
                    icon=ft.Icons.SAVE,
                    bgcolor=PRIMARY_COLOR,
                    color=ft.Colors.WHITE,
                    on_click=handle_save_new,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        open_dialog(page, dialog)

    def open_edit_dialog(item: dict):
        """Chỉnh sửa tên, danh mục và mô tả của nội dung."""
        name_field = ft.TextField(label="Tên nội dung *", value=item["name"], border_radius=8)
        category_dd = make_dropdown(
            label="Danh mục *",
            options=data.CONTENT_CATEGORIES,
            value=item["category"],
        )
        desc_field = ft.TextField(
            label="Mô tả nội dung *",
            value=item["description"],
            multiline=True,
            min_lines=2,
            max_lines=3,
            border_radius=8,
        )

        def handle_save_edit(e):
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
            data.log_activity(f"Đã chỉnh sửa thông tin nội dung '{item['name']}'.")
            close_dialog(page, dialog)
            refresh_view()
            show_snack(page, f"Đã cập nhật nội dung \"{item['name']}\"!")

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Chỉnh sửa nội dung hiển thị", weight=ft.FontWeight.BOLD, size=18),
            content=ft.Container(
                width=460,
                content=ft.Column(
                    tight=True,
                    spacing=12,
                    controls=[name_field, category_dd, desc_field],
                ),
            ),
            actions=[
                ft.OutlinedButton("Hủy", on_click=lambda e: close_dialog(page, dialog)),
                ft.FilledButton(
                    "Lưu thay đổi",
                    icon=ft.Icons.SAVE,
                    bgcolor=PRIMARY_COLOR,
                    color=ft.Colors.WHITE,
                    on_click=handle_save_edit,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        open_dialog(page, dialog)

    def handle_delete_content(item: dict):
        """Xác nhận và xóa nội dung."""
        def confirm_delete():
            data.CONTENTS_DATA.remove(item)
            data.log_activity(f"Đã xóa nội dung '{item['name']}' ({item['id']}).")
            refresh_view()
            show_snack(page, f"Đã xóa nội dung \"{item['name']}\"!")

        show_confirm_delete_dialog(page, item["name"], confirm_delete)

    def select_category(cat_name: str):
        state["category"] = cat_name
        category_filter_dd.value = cat_name
        refresh_view()

    def build_category_chips():
        """Tạo dãy Chip phân loại nhanh theo danh mục."""
        all_cats = ["Tất cả"] + data.CONTENT_CATEGORIES
        chips = []
        for cat in all_cats:
            is_selected = state["category"] == cat
            chips.append(
                ft.Chip(
                    label=ft.Text(cat, size=12),
                    selected=is_selected,
                    on_select=lambda e, c=cat: select_category(c),
                )
            )
        category_chips_row.controls = chips

    def refresh_view():
        """Vẽ lại danh sách nội dung ở chế độ Lưới thẻ (Grid) hoặc Bảng (Table)."""
        build_category_chips()
        filtered = get_filtered_contents()
        summary_text.value = f"Hiển thị {len(filtered)} / {len(data.CONTENTS_DATA)} nội dung"

        if not filtered:
            content_display_area.controls = [
                ft.Container(
                    padding=30,
                    content=ft.Text("Không có nội dung nào khớp với tiêu chí tìm kiếm.", italic=True),
                )
            ]
            page.update()
            return

        if state["view_mode"] == "grid":
            cards = []
            for item in filtered:
                cards.append(
                    ft.Card(
                        col={"sm": 12, "md": 6, "lg": 4, "xl": 3},
                        elevation=2,
                        content=ft.Container(
                            padding=14,
                            content=ft.Column(
                                spacing=8,
                                controls=[
                                    ft.GestureDetector(
                                        on_tap=lambda e, it=item: open_preview_dialog(it),
                                        content=build_thumbnail_preview(item, height=130),
                                    ),
                                    ft.Text(
                                        item["name"],
                                        weight=ft.FontWeight.BOLD,
                                        size=14,
                                        max_lines=1,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[
                                            ft.Container(
                                                bgcolor=PRIMARY_LIGHT,
                                                border_radius=12,
                                                padding=pad_sym(horizontal=8, vertical=2),
                                                content=ft.Text(
                                                    item["category"],
                                                    size=11,
                                                    color=PRIMARY_COLOR,
                                                    weight=ft.FontWeight.W_600,
                                                ),
                                            ),
                                            ft.Text(f"Tải lên: {item['upload_date']}", size=11, color=ft.Colors.GREY_600),
                                        ],
                                    ),
                                    ft.Text(
                                        item["description"],
                                        size=12,
                                        color=ft.Colors.GREY_600,
                                        max_lines=2,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                    ft.Divider(height=4),
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[
                                            ft.TextButton(
                                                "Xem trước",
                                                icon=ft.Icons.PLAY_CIRCLE_OUTLINE,
                                                on_click=lambda e, it=item: open_preview_dialog(it),
                                            ),
                                            ft.Row(
                                                spacing=2,
                                                controls=[
                                                    ft.IconButton(
                                                        icon=ft.Icons.EDIT_OUTLINED,
                                                        icon_color=ft.Colors.AMBER_800,
                                                        tooltip="Sửa tên & mô tả",
                                                        on_click=lambda e, it=item: open_edit_dialog(it),
                                                    ),
                                                    ft.IconButton(
                                                        icon=ft.Icons.DELETE_OUTLINE,
                                                        icon_color=ft.Colors.RED_600,
                                                        tooltip="Xóa nội dung",
                                                        on_click=lambda e, it=item: handle_delete_content(it),
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ),
                    )
                )
            content_display_area.controls = [
                ft.ResponsiveRow(spacing=14, run_spacing=14, controls=cards)
            ]
        else:
            rows = []
            for item in filtered:
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(item["id"], weight=ft.FontWeight.BOLD, size=13)),
                            ft.DataCell(ft.Text(item["name"], weight=ft.FontWeight.W_500, size=13)),
                            ft.DataCell(ft.Text(item["category"], size=13)),
                            ft.DataCell(ft.Text(f"{item['type']} ({item['format']})", size=12)),
                            ft.DataCell(ft.Text(item["size"], size=12)),
                            ft.DataCell(ft.Text(item["upload_date"], size=12)),
                            ft.DataCell(
                                ft.Row(
                                    spacing=4,
                                    controls=[
                                        ft.IconButton(
                                            icon=ft.Icons.PLAY_CIRCLE_OUTLINE,
                                            icon_color=PRIMARY_COLOR,
                                            tooltip="Xem trước",
                                            on_click=lambda e, it=item: open_preview_dialog(it),
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.EDIT_OUTLINED,
                                            icon_color=ft.Colors.AMBER_800,
                                            tooltip="Chỉnh sửa",
                                            on_click=lambda e, it=item: open_edit_dialog(it),
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.DELETE_OUTLINE,
                                            icon_color=ft.Colors.RED_600,
                                            tooltip="Xóa",
                                            on_click=lambda e, it=item: handle_delete_content(it),
                                        ),
                                    ],
                                )
                            ),
                        ]
                    )
                )
            content_display_area.controls = [
                ft.Row(
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.DataTable(
                            column_spacing=20,
                            heading_row_height=44,
                            data_row_min_height=48,
                            columns=[
                                ft.DataColumn(ft.Text("Mã", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Tên nội dung", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Danh mục", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Định dạng", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Dung lượng", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Ngày tải lên", weight=ft.FontWeight.BOLD)),
                                ft.DataColumn(ft.Text("Thao tác", weight=ft.FontWeight.BOLD)),
                            ],
                            rows=rows,
                        )
                    ],
                )
            ]
        page.update()

    def set_view_mode(mode: str):
        state["view_mode"] = mode
        grid_btn.bgcolor = PRIMARY_LIGHT if mode == "grid" else None
        table_btn.bgcolor = PRIMARY_LIGHT if mode == "table" else None
        refresh_view()

    search_box = create_search_field(
        "Tìm theo tên, mô tả hoặc định dạng (MP4, PNG...)",
        lambda e: (state.update({"keyword": e.control.value or ""}), refresh_view()),
        width=320,
    )

    category_filter_dd = make_dropdown(
        label="Danh mục",
        options=["Tất cả"] + data.CONTENT_CATEGORIES,
        value="Tất cả",
        on_change=lambda e: select_category(e.control.value or "Tất cả"),
        width=180,
    )

    grid_btn = ft.IconButton(
        icon=ft.Icons.GRID_VIEW_ROUNDED,
        icon_color=PRIMARY_COLOR,
        bgcolor=PRIMARY_LIGHT if state["view_mode"] == "grid" else None,
        tooltip="Xem dạng Lưới thẻ",
        on_click=lambda e: set_view_mode("grid"),
    )
    table_btn = ft.IconButton(
        icon=ft.Icons.TABLE_ROWS_ROUNDED,
        icon_color=PRIMARY_COLOR,
        bgcolor=PRIMARY_LIGHT if state["view_mode"] == "table" else None,
        tooltip="Xem dạng Bảng danh sách",
        on_click=lambda e: set_view_mode("table"),
    )

    refresh_view()

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=16,
        controls=[
            create_page_header(
                title="Quản lý nội dung hiển thị",
                subtitle="Kho lưu trữ Hình ảnh & Video trình chiếu, phân loại danh mục và xem trước nội dung.",
                right_controls=[
                    ft.FilledButton(
                        "Tải nội dung lên",
                        icon=ft.Icons.CLOUD_UPLOAD,
                        bgcolor=PRIMARY_COLOR,
                        color=ft.Colors.WHITE,
                        on_click=lambda e: open_upload_dialog(),
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
                                        controls=[search_box, category_filter_dd],
                                    ),
                                    ft.Row(
                                        spacing=8,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            summary_text,
                                            ft.Text("Chế độ xem:", size=12, color=ft.Colors.GREY_600),
                                            grid_btn,
                                            table_btn,
                                        ],
                                    ),
                                ],
                            ),
                            category_chips_row,
                            ft.Divider(height=1),
                            content_display_area,
                        ],
                    ),
                ),
            ),
        ],
    )
