import flet as ft
import data
import permissions
import theme

# Hằng số giữ tương thích tên import với các module trong dự án
PRIMARY_COLOR = theme.ACCENT
PRIMARY_LIGHT = theme.ACCENT_SUBTLE_LIGHT
ACCENT_COLOR = theme.ACCENT

ALIGN_CENTER = ft.Alignment.CENTER if hasattr(ft.Alignment, "CENTER") else ft.alignment.center
ALIGN_LEFT = ft.Alignment.CENTER_LEFT if hasattr(ft.Alignment, "CENTER_LEFT") else ft.alignment.center_left
ALIGN_RIGHT = ft.Alignment.CENTER_RIGHT if hasattr(ft.Alignment, "CENTER_RIGHT") else ft.alignment.center_right


def border_all(width: float = theme.BORDER_WIDTH, color: str | None = None):
    """Tạo viền mảnh 1px đồng nhất."""
    c = color or theme.border_color()
    if hasattr(ft.Border, "all"):
        return ft.Border.all(width, c)
    return ft.border.all(width, c)


def border_only(left=None, top=None, right=None, bottom=None):
    """Tạo viền theo cạnh chỉ định."""
    if hasattr(ft.Border, "only"):
        return ft.Border.only(left=left, top=top, right=right, bottom=bottom)
    return ft.border.only(left=left, top=top, right=right, bottom=bottom)


def pad_sym(horizontal: float = 0, vertical: float = 0):
    """Tạo khoảng đệm đối xứng theo thang 4/8/12/16/24/32."""
    if hasattr(ft.Padding, "symmetric"):
        return ft.Padding.symmetric(horizontal=horizontal, vertical=vertical)
    return ft.padding.symmetric(horizontal=horizontal, vertical=vertical)


def pad_only(left: float = 0, top: float = 0, right: float = 0, bottom: float = 0):
    """Tạo khoảng đệm từng cạnh."""
    if hasattr(ft.Padding, "only"):
        return ft.Padding.only(left=left, top=top, right=right, bottom=bottom)
    return ft.padding.only(left=left, top=top, right=right, bottom=bottom)


def set_field_error(field_control, error_message: str | None):
    """Gán lỗi màu đỏ ngay dưới ô nhập hoặc Dropdown."""
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


def make_text_field(
    label: str = "",
    value: str = "",
    hint_text: str = "",
    password: bool = False,
    can_reveal_password: bool = False,
    read_only: bool = False,
    multiline: bool = False,
    min_lines: int = 1,
    max_lines: int = 1,
    width: float | None = None,
    expand: bool | int | None = None,
    on_change=None,
    on_submit=None,
) -> ft.TextField:
    """Tạo ô nhập liệu phẳng, bo góc 6px, cỡ chữ 14."""
    return ft.TextField(
        label=label if label else None,
        value=value,
        hint_text=hint_text if hint_text else None,
        password=password,
        can_reveal_password=can_reveal_password,
        read_only=read_only,
        multiline=multiline,
        min_lines=min_lines,
        max_lines=max_lines,
        width=width,
        expand=expand if expand else None,
        text_size=theme.TEXT_14,
        label_style=ft.TextStyle(size=theme.TEXT_12, color=theme.text_secondary()),
        hint_style=ft.TextStyle(size=theme.TEXT_14, color=theme.text_secondary()),
        error_style=ft.TextStyle(size=theme.TEXT_12, color=theme.STATUS_DANGER),
        border_radius=theme.RADIUS_INPUT,
        border_color=theme.border_color(),
        focused_border_color=theme.accent_color(),
        content_padding=pad_sym(horizontal=theme.SPACE_12, vertical=theme.SPACE_12),
        dense=True,
        on_change=on_change,
        on_submit=on_submit,
    )


def make_form_field(label_text: str, control: ft.Control) -> ft.Column:
    """Đặt nhãn nằm phía trên ô nhập liệu theo chuẩn form quản trị."""
    if hasattr(control, "label"):
        control.label = None
    return ft.Column(
        spacing=theme.SPACE_4,
        tight=True,
        controls=[
            ft.Text(
                label_text,
                size=theme.TEXT_12,
                weight=theme.WEIGHT_SEMI,
                color=theme.text_primary(),
            ),
            control,
        ],
    )


def make_dropdown(
    label: str,
    options: list[tuple[str, str]] | list[str],
    value: str | None = None,
    on_change=None,
    width: float | None = None,
    expand: bool | int | None = None,
) -> ft.Dropdown:
    """Tạo Dropdown bo góc 6px, viền mảnh."""
    dd_options = []
    for opt in options:
        if isinstance(opt, tuple):
            dd_options.append(ft.dropdown.Option(key=opt[0], text=opt[1]))
        else:
            dd_options.append(ft.dropdown.Option(key=opt, text=opt))

    kwargs = {
        "label": label if label else None,
        "options": dd_options,
        "value": value,
        "border_radius": theme.RADIUS_INPUT,
        "border_color": theme.border_color(),
        "focused_border_color": theme.accent_color(),
        "text_size": theme.TEXT_14,
        "label_style": ft.TextStyle(size=theme.TEXT_12, color=theme.text_secondary()),
        "error_style": ft.TextStyle(size=theme.TEXT_12, color=theme.STATUS_DANGER),
        "content_padding": pad_sym(horizontal=theme.SPACE_12, vertical=theme.SPACE_8),
        "dense": True,
        "width": width,
        "expand": expand if expand else None,
    }
    if on_change is not None:
        if "on_select" in ft.Dropdown.__init__.__code__.co_varnames:
            kwargs["on_select"] = on_change
        else:
            kwargs["on_change"] = on_change
    return ft.Dropdown(**kwargs)


def make_primary_button(
    text: str,
    icon_name=None,
    on_click=None,
    disabled: bool = False,
    is_danger: bool = False,
    width: float | None = None,
    tooltip: str | None = None,
) -> ft.FilledButton:
    """Nút hành động chính bo góc 6px, màu nhấn trầm."""
    bg = theme.STATUS_DANGER if is_danger else theme.accent_color()
    return ft.FilledButton(
        text,
        icon=icon_name,
        bgcolor=bg,
        color=theme.WHITE,
        disabled=disabled,
        tooltip=tooltip,
        width=width,
        height=theme.BUTTON_HEIGHT,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=theme.RADIUS_INPUT),
            padding=pad_sym(horizontal=theme.SPACE_16, vertical=theme.SPACE_8),
            text_style=ft.TextStyle(size=theme.TEXT_14, weight=theme.WEIGHT_SEMI),
        ),
        on_click=on_click,
    )


def make_secondary_button(
    text: str,
    icon_name=None,
    on_click=None,
    disabled: bool = False,
    tooltip: str | None = None,
) -> ft.OutlinedButton:
    """Nút phụ viền mảnh 1px, bo góc 6px."""
    return ft.OutlinedButton(
        text,
        icon=icon_name,
        disabled=disabled,
        tooltip=tooltip,
        height=theme.BUTTON_HEIGHT,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=theme.RADIUS_INPUT),
            side=ft.BorderSide(theme.BORDER_WIDTH, theme.border_color()),
            color=theme.text_primary(),
            padding=pad_sym(horizontal=theme.SPACE_12, vertical=theme.SPACE_8),
            text_style=ft.TextStyle(size=theme.TEXT_14, weight=theme.WEIGHT_NORMAL),
        ),
        on_click=on_click,
    )


def make_surface_box(
    content: ft.Control,
    padding: int = theme.SPACE_16,
    col: dict | int | None = None,
    expand: bool | int | None = None,
) -> ft.Container:
    """Khung bề mặt phẳng viền 1px, bo góc 8px, không dùng bóng đổ dày."""
    return ft.Container(
        col=col,
        expand=expand if expand else None,
        padding=padding,
        bgcolor=theme.surface_color(),
        border=border_all(theme.BORDER_WIDTH, theme.border_color()),
        border_radius=theme.RADIUS_CARD,
        content=content,
    )


def create_action_icon(icon_name, tooltip: str, on_click, is_danger: bool = False) -> ft.IconButton:
    """Icon thao tác nhỏ gọn (18px) trong bảng dữ liệu."""
    return ft.IconButton(
        icon=icon_name,
        icon_size=theme.ICON_SM,
        icon_color=theme.STATUS_DANGER if is_danger else theme.text_secondary(),
        tooltip=tooltip,
        style=ft.ButtonStyle(
            padding=pad_sym(horizontal=theme.SPACE_4, vertical=theme.SPACE_4),
            shape=ft.RoundedRectangleBorder(radius=theme.RADIUS_INPUT),
        ),
        on_click=on_click,
    )


def create_styled_table(columns: list[ft.DataColumn], rows: list[ft.DataRow]) -> ft.Container:
    """Bảng dữ liệu chuẩn quản trị: tiêu đề nền xám nhạt, đường kẻ ngang 1px, hover nhẹ."""
    return ft.Container(
        border=border_all(theme.BORDER_WIDTH, theme.border_color()),
        border_radius=theme.RADIUS_CARD,
        bgcolor=theme.surface_color(),
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Row(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.DataTable(
                    column_spacing=theme.SPACE_24,
                    horizontal_margin=theme.SPACE_16,
                    heading_row_height=theme.TABLE_HEADING_HEIGHT,
                    data_row_min_height=theme.TABLE_ROW_HEIGHT,
                    data_row_max_height=theme.TABLE_ROW_HEIGHT,
                    heading_row_color=theme.surface_subtle_color(),
                    data_row_color={ft.ControlState.HOVERED: theme.row_hover_color()},
                    divider_thickness=theme.BORDER_WIDTH,
                    horizontal_lines=ft.BorderSide(theme.BORDER_WIDTH, theme.border_color()),
                    heading_text_style=ft.TextStyle(
                        size=theme.TEXT_12,
                        weight=theme.WEIGHT_SEMI,
                        color=theme.text_secondary(),
                    ),
                    data_text_style=ft.TextStyle(
                        size=theme.TEXT_14,
                        weight=theme.WEIGHT_NORMAL,
                        color=theme.text_primary(),
                    ),
                    columns=columns,
                    rows=rows,
                )
            ],
        ),
    )


def create_pagination_bar(
    total_items: int,
    current_page: int,
    page_size: int,
    on_page_change,
) -> ft.Container:
    """Thanh phân trang gọn ở cuối bảng dữ liệu."""
    total_pages = max(1, (total_items + page_size - 1) // page_size)
    cur = max(1, min(current_page, total_pages))
    start_idx = 0 if total_items == 0 else (cur - 1) * page_size + 1
    end_idx = min(total_items, cur * page_size)

    return ft.Container(
        padding=pad_only(top=theme.SPACE_12),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    f"Hiển thị {start_idx}–{end_idx} trong tổng số {total_items} mục",
                    size=theme.TEXT_12,
                    color=theme.text_secondary(),
                ),
                ft.Row(
                    spacing=theme.SPACE_8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        make_secondary_button(
                            "Trước",
                            on_click=lambda e: on_page_change(cur - 1),
                            disabled=(cur <= 1),
                        ),
                        ft.Text(
                            f"Trang {cur} / {total_pages}",
                            size=theme.TEXT_12,
                            weight=theme.WEIGHT_SEMI,
                            color=theme.text_primary(),
                        ),
                        make_secondary_button(
                            "Sau",
                            on_click=lambda e: on_page_change(cur + 1),
                            disabled=(cur >= total_pages),
                        ),
                    ],
                ),
            ],
        ),
    )


def create_empty_state(message: str = "Không tìm thấy dữ liệu phù hợp với điều kiện lọc.") -> ft.Container:
    """Trạng thái rỗng gọn, rõ ràng khi tìm kiếm không có kết quả."""
    return ft.Container(
        padding=theme.SPACE_32,
        alignment=ALIGN_CENTER,
        border=border_all(theme.BORDER_WIDTH, theme.border_color()),
        border_radius=theme.RADIUS_CARD,
        bgcolor=theme.surface_color(),
        content=ft.Text(message, size=theme.TEXT_14, color=theme.text_secondary()),
    )


def open_dialog(page: ft.Page, dialog):
    """Hiển thị hộp thoại an toàn."""
    if isinstance(dialog, ft.AlertDialog):
        dialog.bgcolor = theme.surface_color()
        dialog.shape = ft.RoundedRectangleBorder(radius=theme.RADIUS_CARD)
    if hasattr(page, "show_dialog"):
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
    """Đóng hộp thoại hiện tại."""
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
    """Thanh thông báo SnackBar ngắn gọn."""
    bg = theme.STATUS_DANGER if is_error else theme.TEXT_PRIMARY_LIGHT
    snack = ft.SnackBar(
        content=ft.Text(message, color=theme.WHITE, size=theme.TEXT_14),
        bgcolor=bg,
        duration=2200,
    )
    if hasattr(page, "show_dialog"):
        page.show_dialog(snack)
    elif hasattr(page, "open"):
        page.open(snack)
    else:
        page.snack_bar = snack
        snack.open = True
        page.update()


def create_role_badge(role_text: str) -> ft.Container:
    """Huy hiệu vai trò nhẹ nhàng theo đúng bảng màu theme hiện có."""
    if role_text == permissions.ROLE_ADMIN:
        bg_c = theme.accent_subtle()
        bd_c = theme.accent_color()
        dot_c = theme.accent_color()
        fg_c = theme.accent_color()
    elif role_text == permissions.ROLE_EDITOR:
        bg_c = theme.surface_subtle_color()
        bd_c = theme.border_color()
        dot_c = theme.STATUS_ONLINE
        fg_c = theme.text_primary()
    else:
        bg_c = theme.surface_subtle_color()
        bd_c = theme.border_color()
        dot_c = theme.STATUS_OFFLINE
        fg_c = theme.text_secondary()

    return ft.Container(
        padding=pad_sym(horizontal=theme.SPACE_8, vertical=theme.SPACE_4),
        bgcolor=bg_c,
        border=border_all(theme.BORDER_WIDTH, bd_c),
        border_radius=theme.RADIUS_INPUT,
        content=ft.Row(
            spacing=theme.SPACE_4,
            tight=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=theme.DOT_SIZE,
                    height=theme.DOT_SIZE,
                    border_radius=theme.DOT_SIZE,
                    bgcolor=dot_c,
                ),
                ft.Text(
                    role_text,
                    size=theme.TEXT_12,
                    weight=theme.WEIGHT_SEMI,
                    color=fg_c,
                ),
            ],
        ),
    )


def create_access_denied_view(page: ft.Page, on_back_home=None) -> ft.Container:
    """Khung thông báo từ chối truy cập khi người dùng vào trang không thuộc quyền."""
    actions = []
    if on_back_home:
        actions.append(
            make_primary_button(
                "Về trang Tổng quan",
                icon_name=ft.Icons.DASHBOARD_OUTLINED,
                on_click=lambda e: on_back_home(0),
            )
        )
    return make_surface_box(
        padding=theme.SPACE_32,
        content=ft.Column(
            spacing=theme.SPACE_12,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.LOCK_OUTLINE, size=32, color=theme.STATUS_DANGER),
                ft.Text(
                    "Không có quyền truy cập",
                    size=theme.TEXT_16,
                    weight=theme.WEIGHT_SEMI,
                    color=theme.text_primary(),
                ),
                ft.Text(
                    "Vai trò hiện tại của bạn không được cấp quyền sử dụng phân hệ này.",
                    size=theme.TEXT_14,
                    color=theme.text_secondary(),
                ),
                *actions,
            ],
        ),
    )


def create_page_header(title: str, subtitle: str = "", right_controls: list | None = None) -> ft.Container:
    """Thanh tiêu đề trang: tên trang bên trái, nút hành động chính bên phải."""
    left_items = [
        ft.Text(title, size=theme.TEXT_22, weight=theme.WEIGHT_SEMI, color=theme.text_primary()),
    ]
    if subtitle:
        left_items.append(
            ft.Text(subtitle, size=theme.TEXT_12, color=theme.text_secondary())
        )
    return ft.Container(
        padding=pad_only(bottom=theme.SPACE_8),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            wrap=True,
            controls=[
                ft.Column(spacing=theme.SPACE_4, controls=left_items),
                ft.Row(spacing=theme.SPACE_8, wrap=True, controls=right_controls or []),
            ],
        ),
    )


def create_stat_card(
    title: str,
    value: str | int,
    icon_name=None,
    color: str = theme.ACCENT,
    subtitle: str = "",
    col_Responsive: dict | int = 12,
) -> ft.Container:
    """Thẻ số liệu tổng quan: viền 1px, bo góc 8px, bố cục gọn không lòe loẹt."""
    top_row_controls = [
        ft.Text(title, size=theme.TEXT_12, color=theme.text_secondary(), expand=True),
    ]
    if icon_name:
        top_row_controls.append(
            ft.Icon(icon_name, size=theme.ICON_SM, color=theme.text_secondary())
        )
    return ft.Container(
        col=col_Responsive,
        padding=theme.SPACE_16,
        bgcolor=theme.surface_color(),
        border=border_all(theme.BORDER_WIDTH, theme.border_color()),
        border_radius=theme.RADIUS_CARD,
        content=ft.Column(
            spacing=theme.SPACE_8,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=top_row_controls,
                ),
                ft.Text(str(value), size=theme.TEXT_22, weight=theme.WEIGHT_SEMI, color=theme.text_primary()),
                ft.Text(subtitle, size=theme.TEXT_12, color=theme.text_secondary())
                if subtitle
                else ft.Container(),
            ],
        ),
    )


def create_status_badge(status_text: str) -> ft.Row:
    """Hiển thị trạng thái bằng chấm tròn nhỏ (8px) + chữ, không tô màu cả khối."""
    dot_colors = {
        "Online": theme.STATUS_ONLINE,
        "Đang phát": theme.STATUS_ONLINE,
        "Hoạt động": theme.STATUS_ONLINE,
        "Đang bật": theme.STATUS_ONLINE,
        "Offline": theme.STATUS_OFFLINE,
        "Đã dừng": theme.STATUS_OFFLINE,
        "Đã tắt": theme.STATUS_OFFLINE,
        "Tạm dừng": theme.STATUS_WARNING,
        "Cảnh báo nhiệt": theme.STATUS_WARNING,
        "Sự cố": theme.STATUS_DANGER,
        "Gián đoạn": theme.STATUS_DANGER,
        "Đã khóa": theme.STATUS_DANGER,
    }
    dot_c = dot_colors.get(status_text, theme.STATUS_OFFLINE)
    return ft.Row(
        spacing=theme.SPACE_8,
        tight=True,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(
                width=theme.DOT_SIZE,
                height=theme.DOT_SIZE,
                border_radius=theme.DOT_SIZE,
                bgcolor=dot_c,
            ),
            ft.Text(
                status_text,
                size=theme.TEXT_14,
                weight=theme.WEIGHT_NORMAL,
                color=theme.text_primary(),
            ),
        ],
    )


def create_search_field(hint_text: str, on_change_callback, width: float = 280) -> ft.TextField:
    """Ô tìm kiếm gọn nằm trên thanh công cụ."""
    return ft.TextField(
        hint_text=hint_text,
        prefix_icon=ft.Icons.SEARCH_OUTLINED,
        on_change=on_change_callback,
        text_size=theme.TEXT_14,
        hint_style=ft.TextStyle(size=theme.TEXT_14, color=theme.text_secondary()),
        border_radius=theme.RADIUS_INPUT,
        border_color=theme.border_color(),
        focused_border_color=theme.accent_color(),
        width=width,
        dense=True,
        content_padding=pad_sym(horizontal=theme.SPACE_12, vertical=theme.SPACE_8),
    )


def show_confirm_delete_dialog(
    page: ft.Page,
    item_title: str,
    on_confirm_callback,
):
    """Hộp thoại xác nhận xóa: nút Hủy dạng chữ bên trái nút xóa chính."""
    def handle_cancel(e):
        close_dialog(page, dialog)

    def handle_confirm(e):
        close_dialog(page, dialog)
        on_confirm_callback()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Xác nhận xóa", size=theme.TEXT_16, weight=theme.WEIGHT_SEMI, color=theme.text_primary()),
        content=ft.Container(
            width=400,
            content=ft.Text(
                f"Bạn có chắc muốn xóa \"{item_title}\"? Dữ liệu đã xóa không thể khôi phục trong phiên làm việc này.",
                size=theme.TEXT_14,
                color=theme.text_primary(),
            ),
        ),
        actions=[
            ft.TextButton(
                "Hủy",
                style=ft.ButtonStyle(color=theme.text_secondary()),
                on_click=handle_cancel,
            ),
            make_primary_button("Xóa", on_click=handle_confirm, is_danger=True),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    open_dialog(page, dialog)
