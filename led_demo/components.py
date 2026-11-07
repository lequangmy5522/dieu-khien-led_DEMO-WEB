import flet as ft

# ==============================================================================
# HẰNG SỐ MÀU SẮC CHỦ ĐẠO & GIAO DIỆN THỐNG NHẤT
# ==============================================================================

PRIMARY_COLOR = ft.Colors.BLUE_800
PRIMARY_LIGHT = ft.Colors.BLUE_50
ACCENT_COLOR = ft.Colors.BLUE_600

# Tương thích thuộc tính Alignment / Border / Padding giữa Flet 1.x và 0.28
ALIGN_CENTER = ft.Alignment.CENTER if hasattr(ft.Alignment, "CENTER") else ft.alignment.center
ALIGN_LEFT = ft.Alignment.CENTER_LEFT if hasattr(ft.Alignment, "CENTER_LEFT") else ft.alignment.center_left
ALIGN_RIGHT = ft.Alignment.CENTER_RIGHT if hasattr(ft.Alignment, "CENTER_RIGHT") else ft.alignment.center_right


def border_all(width: float = 1, color: str = ft.Colors.GREY_300):
    """Tạo viền 4 cạnh tương thích mọi phiên bản Flet."""
    if hasattr(ft.Border, "all"):
        return ft.Border.all(width, color)
    return ft.border.all(width, color)


def border_only(left=None, top=None, right=None, bottom=None):
    """Tạo viền tùy chọn cạnh tương thích mọi phiên bản Flet."""
    if hasattr(ft.Border, "only"):
        return ft.Border.only(left=left, top=top, right=right, bottom=bottom)
    return ft.border.only(left=left, top=top, right=right, bottom=bottom)


def pad_sym(horizontal: float = 0, vertical: float = 0):
    """Tạo padding đối xứng ngang/dọc."""
    if hasattr(ft.Padding, "symmetric"):
        return ft.Padding.symmetric(horizontal=horizontal, vertical=vertical)
    return ft.padding.symmetric(horizontal=horizontal, vertical=vertical)


def pad_only(left: float = 0, top: float = 0, right: float = 0, bottom: float = 0):
    """Tạo padding từng cạnh."""
    if hasattr(ft.Padding, "only"):
        return ft.Padding.only(left=left, top=top, right=right, bottom=bottom)
    return ft.padding.only(left=left, top=top, right=right, bottom=bottom)


def set_field_error(field_control, error_message: str | None):
    """Gán thông báo lỗi cho TextField hoặc Dropdown tương thích Flet 1.x và 0.28."""
    if isinstance(field_control, ft.Dropdown):
        if hasattr(field_control, "error_text"):
            field_control.error_text = error_message
        else:
            field_control.error = error_message
    else:
        if hasattr(field_control, "error"):
            field_control.error = error_message
        else:
            field_control.error_text = error_message


def make_dropdown(
    label: str,
    options: list[tuple[str, str]] | list[str],
    value: str | None = None,
    on_change=None,
    width: float | None = None,
    expand: bool = False,
) -> ft.Dropdown:
    """Tạo Dropdown thống nhất, hỗ trợ cả danh sách chuỗi hoặc cặp (key, text)."""
    dd_options = []
    for opt in options:
        if isinstance(opt, tuple):
            dd_options.append(ft.dropdown.Option(key=opt[0], text=opt[1]))
        else:
            dd_options.append(ft.dropdown.Option(key=opt, text=opt))

    kwargs = {
        "label": label,
        "options": dd_options,
        "value": value,
        "border_radius": 8,
        "width": width,
        "expand": expand,
    }
    # Flet 1.x dùng on_select, Flet 0.28 dùng on_change
    if on_change is not None:
        if "on_select" in ft.Dropdown.__init__.__code__.co_varnames:
            kwargs["on_select"] = on_change
        else:
            kwargs["on_change"] = on_change
    return ft.Dropdown(**kwargs)


def open_dialog(page: ft.Page, dialog):
    """Hiển thị AlertDialog / DatePicker / TimePicker an toàn."""
    if hasattr(page, "show_dialog"):
        # Nếu dialog đã nằm trong danh sách đang mở thì đóng trước khi mở lại
        dialogs_attr = getattr(page, "_dialogs", None)
        if dialogs_attr and dialog in dialogs_attr.controls:
            dialogs_attr.controls.remove(dialog)
        page.show_dialog(dialog)
    elif hasattr(page, "open"):
        page.open(dialog)
    else:
        page.dialog = dialog
        dialog.open = True
        page.update()


def close_dialog(page: ft.Page, dialog=None):
    """Đóng AlertDialog hiện tại và cập nhật giao diện."""
    if dialog is not None and hasattr(page, "close"):
        page.close(dialog)
    elif dialog is not None and getattr(dialog, "open", False):
        dialog.open = False
        try:
            dialog.update()
        except Exception:
            page.update()
    elif hasattr(page, "pop_dialog"):
        page.pop_dialog()
    page.update()


def show_snack(page: ft.Page, message: str, is_error: bool = False):
    """Hiển thị thanh thông báo SnackBar ở góc dưới màn hình."""
    bg = ft.Colors.RED_700 if is_error else PRIMARY_COLOR
    icon_name = ft.Icons.ERROR_OUTLINE if is_error else ft.Icons.CHECK_CIRCLE_OUTLINE
    snack = ft.SnackBar(
        content=ft.Row(
            controls=[
                ft.Icon(icon_name, color=ft.Colors.WHITE, size=20),
                ft.Text(message, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500, expand=True),
            ],
            spacing=10,
        ),
        bgcolor=bg,
        duration=2500,
    )
    if hasattr(page, "show_dialog"):
        page.show_dialog(snack)
    elif hasattr(page, "open"):
        page.open(snack)
    else:
        page.snack_bar = snack
        snack.open = True
        page.update()


# ==============================================================================
# CÁC THÀNH PHẦN GIAO DIỆN DÙNG CHUNG (STAT CARD, BADGE, CONFIRM DIALOG...)
# ==============================================================================

def create_page_header(title: str, subtitle: str, right_controls: list | None = None) -> ft.Container:
    """Tiêu đề đầu mỗi trang phân hệ kèm mô tả ngắn và cụm nút chức năng bên phải."""
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(title, size=22, weight=ft.FontWeight.BOLD),
                        ft.Text(subtitle, size=13, color=ft.Colors.GREY_600),
                    ],
                    spacing=2,
                    expand=True,
                ),
                ft.Row(controls=right_controls or [], spacing=10, wrap=True),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            wrap=True,
        ),
        padding=pad_only(bottom=8),
    )


def create_stat_card(
    title: str,
    value: str | int,
    icon_name,
    color: str = PRIMARY_COLOR,
    subtitle: str = "",
    col_Responsive: dict | int = 12,
) -> ft.Card:
    """Thẻ thống kê số liệu có icon, bo góc dùng cho Tổng quan và Giám sát."""
    return ft.Card(
        col=col_Responsive,
        elevation=2,
        content=ft.Container(
            padding=16,
            border_radius=12,
            content=ft.Row(
                controls=[
                    ft.Container(
                        width=52,
                        height=52,
                        border_radius=12,
                        bgcolor=ft.Colors.with_opacity(0.12, color),
                        alignment=ALIGN_CENTER,
                        content=ft.Icon(icon_name, color=color, size=28),
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(title, size=13, color=ft.Colors.GREY_600, weight=ft.FontWeight.W_500),
                            ft.Text(str(value), size=24, weight=ft.FontWeight.BOLD),
                            ft.Text(subtitle, size=11, color=ft.Colors.GREY_500) if subtitle else ft.Container(),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                ],
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        ),
    )


def create_status_badge(status_text: str) -> ft.Container:
    """Badge hiển thị trạng thái với màu sắc trực quan."""
    color_map = {
        "Online": (ft.Colors.GREEN_700, ft.Colors.GREEN_50, ft.Icons.CHECK_CIRCLE),
        "Đang phát": (ft.Colors.BLUE_700, ft.Colors.BLUE_50, ft.Icons.PLAY_CIRCLE_FILL),
        "Hoạt động": (ft.Colors.GREEN_700, ft.Colors.GREEN_50, ft.Icons.VERIFIED_USER),
        "Đang bật": (ft.Colors.GREEN_700, ft.Colors.GREEN_50, ft.Icons.CHECK_CIRCLE),
        "Offline": (ft.Colors.GREY_700, ft.Colors.GREY_200, ft.Icons.CLOUD_OFF),
        "Đã dừng": (ft.Colors.GREY_700, ft.Colors.GREY_200, ft.Icons.STOP_CIRCLE),
        "Tạm dừng": (ft.Colors.AMBER_800, ft.Colors.AMBER_50, ft.Icons.PAUSE_CIRCLE_FILLED),
        "Đã tắt": (ft.Colors.GREY_700, ft.Colors.GREY_200, ft.Icons.DO_NOT_DISTURB_ON),
        "Đã khóa": (ft.Colors.RED_700, ft.Colors.RED_50, ft.Icons.LOCK),
        "Sự cố": (ft.Colors.RED_700, ft.Colors.RED_50, ft.Icons.WARNING_AMBER_ROUNDED),
        "Gián đoạn": (ft.Colors.RED_700, ft.Colors.RED_50, ft.Icons.ERROR_OUTLINE),
        "Cảnh báo nhiệt": (ft.Colors.DEEP_ORANGE_700, ft.Colors.DEEP_ORANGE_50, ft.Icons.THERMOSTAT),
    }
    fg, bg, ic = color_map.get(status_text, (PRIMARY_COLOR, PRIMARY_LIGHT, ft.Icons.INFO_OUTLINE))
    return ft.Container(
        bgcolor=bg,
        border_radius=20,
        padding=pad_sym(horizontal=10, vertical=4),
        content=ft.Row(
            controls=[
                ft.Icon(ic, color=fg, size=14),
                ft.Text(status_text, color=fg, size=12, weight=ft.FontWeight.W_600),
            ],
            spacing=5,
            tight=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )


def create_search_field(hint_text: str, on_change_callback, width: float = 300) -> ft.TextField:
    """Ô tìm kiếm chuẩn có icon kính lúp dùng chung cho các bảng dữ liệu."""
    return ft.TextField(
        hint_text=hint_text,
        prefix_icon=ft.Icons.SEARCH,
        on_change=on_change_callback,
        border_radius=8,
        width=width,
        dense=True,
        content_padding=pad_sym(horizontal=12, vertical=10),
    )


def show_confirm_delete_dialog(
    page: ft.Page,
    item_title: str,
    on_confirm_callback,
):
    """Hộp thoại xác nhận trước khi xóa một mục dữ liệu."""
    def handle_cancel(e):
        close_dialog(page, dialog)

    def handle_confirm(e):
        close_dialog(page, dialog)
        on_confirm_callback()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row(
            controls=[
                ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.RED_600, size=26),
                ft.Text("Xác nhận xóa dữ liệu", weight=ft.FontWeight.BOLD, size=18),
            ],
            spacing=8,
        ),
        content=ft.Text(
            f"Bạn có chắc chắn muốn xóa \"{item_title}\" không?\nThao tác này sẽ cập nhật ngay trên phiên làm việc hiện tại.",
            size=14,
        ),
        actions=[
            ft.OutlinedButton("Hủy bỏ", on_click=handle_cancel),
            ft.FilledButton(
                "Xác nhận xóa",
                icon=ft.Icons.DELETE_FOREVER,
                bgcolor=ft.Colors.RED_600,
                color=ft.Colors.WHITE,
                on_click=handle_confirm,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    open_dialog(page, dialog)
