import flet as ft
import data
import permissions
import theme
from components import (
    border_only,
    create_role_badge,
    make_secondary_button,
    pad_only,
    pad_sym,
    show_snack,
)
from views import (
    login,
    dashboard,
    screens,
    contents,
    schedules,
    control,
    monitoring,
    users,
    settings,
)

# Danh sách 8 mục điều hướng gắn với khóa trang chuẩn trong permissions.py
NAV_ITEMS = [
    ("dashboard", "Tổng quan", ft.Icons.DASHBOARD_OUTLINED),
    ("screens", "Quản lý màn hình LED", ft.Icons.TV_OUTLINED),
    ("contents", "Quản lý nội dung", ft.Icons.FOLDER_OUTLINED),
    ("schedules", "Lịch phát nội dung", ft.Icons.CALENDAR_TODAY_OUTLINED),
    ("control", "Điều khiển màn hình", ft.Icons.TUNE_OUTLINED),
    ("monitoring", "Giám sát thiết bị", ft.Icons.MONITOR_HEART_OUTLINED),
    ("users", "Quản lý người dùng", ft.Icons.PEOPLE_OUTLINE),
    ("settings", "Cài đặt hệ thống", ft.Icons.SETTINGS_OUTLINED),
]


def main(page: ft.Page):
    """Khởi tạo ứng dụng quản trị màn hình LED."""
    page.title = "Toàn Trung CMS - Công Ty Cổ Phần Điện Tử Viễn Thông Toàn Trung"
    page.padding = 0
    page.spacing = 0

    def sync_page_theme():
        dark = theme.is_dark()
        page.theme_mode = ft.ThemeMode.DARK if dark else ft.ThemeMode.LIGHT
        page.bgcolor = theme.bg_color()
        page.theme = ft.Theme(color_scheme_seed=theme.ACCENT)
        page.dark_theme = ft.Theme(color_scheme_seed=theme.ACCENT_DARK)

    sync_page_theme()

    state = {
        "selected_index": data.APP_STATE.get("selected_index", 0),
        "in_shell": bool(data.APP_STATE.get("is_authenticated", False)),
    }

    content_area = ft.Container(
        expand=True,
        padding=theme.SPACE_24,
        bgcolor=theme.bg_color(),
    )

    sidebar_items_col = ft.Column(spacing=theme.SPACE_4)
    sidebar_container = ft.Container(width=theme.SIDEBAR_WIDTH)
    top_header = ft.Container(height=theme.HEADER_HEIGHT)

    user_info_text = ft.Text("", size=theme.TEXT_14, weight=theme.WEIGHT_SEMI)
    role_badge_holder = ft.Container()

    def apply_theme(is_dark: bool):
        """Đổi chế độ Sáng/Tối và vẽ lại toàn bộ khung giao diện ngay lập tức."""
        data.SYSTEM_SETTINGS["theme_mode"] = "dark" if is_dark else "light"
        sync_page_theme()
        if state["in_shell"]:
            rebuild_shell_chrome()
            navigate_to(state["selected_index"])
        else:
            show_login_screen()

    def handle_toggle_theme(e):
        new_dark = not theme.is_dark()
        apply_theme(new_dark)
        show_snack(page, f"Đã chuyển sang chế độ {'Tối' if new_dark else 'Sáng'}.")

    def handle_logout(e=None):
        """Đăng xuất về màn hình đăng nhập."""
        data.log_activity("Đã đăng xuất khỏi hệ thống.")
        data.APP_STATE["is_authenticated"] = False
        data.APP_STATE["selected_index"] = 0
        state["in_shell"] = False
        state["selected_index"] = 0
        show_login_screen()
        show_snack(page, "Đã đăng xuất khỏi phiên làm việc.")

    def refresh_header_user():
        """Cập nhật họ tên và huy hiệu vai trò ở thanh Header."""
        user_info_text.value = data.CURRENT_USER.get("full_name", "Người dùng")
        user_info_text.color = theme.text_primary()
        role_badge_holder.content = create_role_badge(data.get_current_role())

    def build_sidebar_items():
        """Chỉ dựng các mục menu nằm trong danh sách visible_pages(role)."""
        items = []
        cur_idx = state["selected_index"]
        allowed_pages = set(permissions.visible_pages(data.get_current_role()))

        for idx, (page_key, label, icon_name) in enumerate(NAV_ITEMS):
            if page_key not in allowed_pages:
                continue

            is_active = idx == cur_idx
            left_bar_color = theme.accent_color() if is_active else ft.Colors.TRANSPARENT
            bg_c = theme.accent_subtle() if is_active else ft.Colors.TRANSPARENT
            fg_c = theme.accent_color() if is_active else theme.text_primary()
            ic_c = theme.accent_color() if is_active else theme.text_secondary()
            fw = theme.WEIGHT_SEMI if is_active else theme.WEIGHT_NORMAL

            items.append(
                ft.Container(
                    bgcolor=bg_c,
                    border=border_only(
                        left=ft.BorderSide(theme.SIDEBAR_INDIC_WIDTH, left_bar_color)
                    ),
                    padding=pad_sym(horizontal=theme.SPACE_16, vertical=theme.SPACE_12),
                    ink=True,
                    on_click=lambda e, i=idx: navigate_to(i),
                    content=ft.Row(
                        spacing=theme.SPACE_12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(icon_name, size=theme.ICON_SM, color=ic_c),
                            ft.Text(
                                label,
                                size=theme.TEXT_14,
                                weight=fw,
                                color=fg_c,
                                expand=True,
                            ),
                        ],
                    ),
                )
            )
        sidebar_items_col.controls = items

    def rebuild_shell_chrome():
        """Cập nhật màu nền, viền và danh sách menu của Sidebar + Header."""
        refresh_header_user()
        build_sidebar_items()

        sidebar_container.bgcolor = theme.surface_color()
        sidebar_container.border = border_only(
            right=ft.BorderSide(theme.BORDER_WIDTH, theme.border_color())
        )
        sidebar_container.content = ft.Column(
            expand=True,
            spacing=0,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Column(
                    spacing=0,
                    controls=[
                        ft.Container(
                            height=theme.HEADER_HEIGHT,
                            padding=pad_sym(horizontal=theme.SPACE_16),
                            border=border_only(
                                bottom=ft.BorderSide(theme.BORDER_WIDTH, theme.border_color())
                            ),
                            content=ft.Row(
                                spacing=theme.SPACE_8,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Container(
                                        width=theme.SPACE_24,
                                        height=theme.SPACE_24,
                                        border_radius=theme.RADIUS_INPUT,
                                        bgcolor=theme.accent_color(),
                                        alignment=ft.Alignment.CENTER
                                        if hasattr(ft.Alignment, "CENTER")
                                        else ft.alignment.center,
                                        content=ft.Text(
                                            "TT",
                                            size=theme.TEXT_12,
                                            weight=theme.WEIGHT_SEMI,
                                            color=theme.WHITE,
                                        ),
                                    ),
                                    ft.Text(
                                        "Toàn Trung CMS",
                                        size=theme.TEXT_16,
                                        weight=theme.WEIGHT_SEMI,
                                        color=theme.text_primary(),
                                    ),
                                ],
                            ),
                        ),
                        ft.Container(
                            padding=pad_only(top=theme.SPACE_8),
                            content=sidebar_items_col,
                        ),
                    ],
                ),
                ft.Container(
                    padding=theme.SPACE_16,
                    border=border_only(
                        top=ft.BorderSide(theme.BORDER_WIDTH, theme.border_color())
                    ),
                    content=ft.Text(
                        "Phiên bản nội bộ v2.4",
                        size=theme.TEXT_12,
                        color=theme.text_secondary(),
                    ),
                ),
            ],
        )

        top_header.bgcolor = theme.surface_color()
        top_header.padding = pad_sym(horizontal=theme.SPACE_24)
        top_header.border = border_only(
            bottom=ft.BorderSide(theme.BORDER_WIDTH, theme.border_color())
        )
        top_header.content = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    "Công Ty Cổ Phần Điện Tử Viễn Thông Toàn Trung – Hệ thống quản lý màn hình LED",
                    size=theme.TEXT_14,
                    color=theme.text_secondary(),
                ),
                ft.Row(
                    spacing=theme.SPACE_16,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.DARK_MODE_OUTLINED
                            if not theme.is_dark()
                            else ft.Icons.LIGHT_MODE_OUTLINED,
                            icon_size=theme.ICON_SM,
                            icon_color=theme.text_secondary(),
                            tooltip="Đổi giao diện Sáng / Tối",
                            on_click=handle_toggle_theme,
                        ),
                        ft.Row(
                            spacing=theme.SPACE_8,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                user_info_text,
                                role_badge_holder,
                            ],
                        ),
                        make_secondary_button(
                            "Đăng xuất",
                            icon_name=ft.Icons.LOGOUT_OUTLINED,
                            on_click=handle_logout,
                        ),
                    ],
                ),
            ],
        )
        content_area.bgcolor = theme.bg_color()

    def on_user_or_profile_updated():
        """Cập nhật lại Header và Sidebar khi thông tin hoặc vai trò người dùng thay đổi."""
        refresh_header_user()
        build_sidebar_items()
        page.update()

    def navigate_to(index: int):
        """Điều hướng giữa 8 phân hệ có kiểm tra quyền truy cập."""
        role = data.get_current_role()
        allowed_pages = permissions.visible_pages(role)

        if index < 0 or index >= len(NAV_ITEMS):
            index = 0

        target_page_key = NAV_ITEMS[index][0]
        if target_page_key not in allowed_pages:
            state["selected_index"] = 0
            data.APP_STATE["selected_index"] = 0
            refresh_header_user()
            build_sidebar_items()
            content_area.content = dashboard.build_view(page, on_navigate=navigate_to)
            page.update()
            show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
            return

        state["selected_index"] = index
        data.APP_STATE["selected_index"] = index
        refresh_header_user()
        build_sidebar_items()

        view_builders = {
            0: lambda: dashboard.build_view(page, on_navigate=navigate_to),
            1: lambda: screens.build_view(page),
            2: lambda: contents.build_view(page),
            3: lambda: schedules.build_view(page),
            4: lambda: control.build_view(page),
            5: lambda: monitoring.build_view(page),
            6: lambda: users.build_view(page, on_user_updated=on_user_or_profile_updated),
            7: lambda: settings.build_view(
                page,
                on_theme_change=apply_theme,
                on_logout=handle_logout,
                on_profile_updated=on_user_or_profile_updated,
            ),
        }
        builder = view_builders.get(index, view_builders[0])
        content_area.content = builder()
        page.update()

    def show_main_shell(initial_index: int = 0):
        """Dựng lại toàn bộ bố cục chính theo vai trò mới sau khi đăng nhập."""
        state["in_shell"] = True
        state["selected_index"] = initial_index
        data.APP_STATE["is_authenticated"] = True
        data.APP_STATE["selected_index"] = initial_index
        page.controls.clear()
        rebuild_shell_chrome()
        page.add(
            ft.Row(
                expand=True,
                spacing=0,
                controls=[
                    sidebar_container,
                    ft.Column(
                        expand=True,
                        spacing=0,
                        controls=[
                            top_header,
                            content_area,
                        ],
                    ),
                ],
            )
        )
        navigate_to(initial_index)

    def show_login_screen():
        """Hiển thị màn hình đăng nhập."""
        state["in_shell"] = False
        data.APP_STATE["is_authenticated"] = False
        page.controls.clear()
        page.add(login.build_view(page, on_login_success=show_main_shell))
        page.update()

    if data.APP_STATE.get("is_authenticated", False):
        show_main_shell(initial_index=data.APP_STATE.get("selected_index", 0))
    else:
        show_login_screen()


if __name__ == "__main__":
    if hasattr(ft, "run"):
        ft.run(main)
    else:
        ft.app(target=main)
