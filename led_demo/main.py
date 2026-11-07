import flet as ft
import data
from components import (
    PRIMARY_COLOR,
    ALIGN_CENTER,
    border_only,
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


def main(page: ft.Page):
    """Hàm khởi tạo ứng dụng Điều khiển màn hình LED - Bản Demo Giao diện."""
    page.title = "Hệ thống Điều khiển Màn hình LED Tập trung - VietLED Demo"
    page.padding = 0
    page.spacing = 0

    # Thiết lập giao diện Sáng/Tối và bảng màu xanh dương đậm chủ đạo
    page.theme_mode = (
        ft.ThemeMode.DARK
        if data.SYSTEM_SETTINGS["theme_mode"] == "dark"
        else ft.ThemeMode.LIGHT
    )
    page.theme = ft.Theme(color_scheme_seed=PRIMARY_COLOR)

    # Trạng thái điều hướng hiện tại (0 -> 7 tương ứng 8 mục trên NavigationRail)
    state = {"selected_index": 0}

    # Vùng chứa nội dung chính bên phải sidebar
    content_area = ft.Container(
        expand=True,
        padding=20,
    )

    # Nhãn hiển thị tên & vai trò người dùng trên thanh Header
    user_info_text = ft.Text("", weight=ft.FontWeight.W_600, size=14)
    user_role_text = ft.Text("", size=12, color=ft.Colors.GREY_600)

    def apply_theme(is_dark: bool):
        """Chuyển đổi giao diện Sáng / Tối ngay lập tức."""
        data.SYSTEM_SETTINGS["theme_mode"] = "dark" if is_dark else "light"
        page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
        theme_btn.icon = ft.Icons.DARK_MODE if is_dark else ft.Icons.LIGHT_MODE
        theme_btn.tooltip = "Đang ở chế độ Tối (Nhấn để chuyển Sáng)" if is_dark else "Đang ở chế độ Sáng (Nhấn để chuyển Tối)"
        page.update()

    def handle_toggle_theme(e):
        is_currently_dark = page.theme_mode == ft.ThemeMode.DARK
        apply_theme(not is_currently_dark)
        mode_label = "Tối (Dark Mode)" if not is_currently_dark else "Sáng (Light Mode)"
        show_snack(page, f"Đã chuyển sang giao diện {mode_label}")

    theme_btn = ft.IconButton(
        icon=ft.Icons.LIGHT_MODE,
        tooltip="Chuyển đổi giao diện Sáng/Tối",
        on_click=handle_toggle_theme,
    )

    def handle_logout(e=None):
        """Đăng xuất khỏi phiên làm việc và quay về màn hình đăng nhập."""
        data.log_activity(f"{data.CURRENT_USER['full_name']} đã đăng xuất khỏi hệ thống.")
        show_login_screen()
        show_snack(page, "Đã đăng xuất thành công!")

    def refresh_header_user():
        """Cập nhật tên và vai trò người dùng đang đăng nhập trên Header."""
        user_info_text.value = data.CURRENT_USER.get("full_name", "Quản trị viên")
        user_role_text.value = f"{data.CURRENT_USER.get('role', 'Quản trị viên')} ({data.CURRENT_USER.get('username', 'admin')})"

    def navigate_to(index: int):
        """Chuyển sang phân hệ tương ứng theo chỉ số (0 -> 7)."""
        state["selected_index"] = index
        nav_rail.selected_index = index
        refresh_header_user()

        view_builders = {
            0: lambda: dashboard.build_view(page, on_navigate=navigate_to),
            1: lambda: screens.build_view(page),
            2: lambda: contents.build_view(page),
            3: lambda: schedules.build_view(page),
            4: lambda: control.build_view(page),
            5: lambda: monitoring.build_view(page),
            6: lambda: users.build_view(page, on_user_updated=refresh_header_user),
            7: lambda: settings.build_view(
                page,
                on_theme_change=apply_theme,
                on_logout=handle_logout,
                on_profile_updated=refresh_header_user,
            ),
        }
        builder = view_builders.get(index, view_builders[0])
        content_area.content = builder()
        page.update()

    # Thanh điều hướng bên trái (NavigationRail) gồm đúng 8 mục theo thứ tự yêu cầu
    nav_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=105,
        min_extended_width=230,
        extended=True,
        group_alignment=-0.9,
        leading=ft.Container(
            padding=pad_sym(horizontal=12, vertical=14),
            content=ft.Row(
                controls=[
                    ft.Container(
                        width=38,
                        height=38,
                        border_radius=10,
                        bgcolor=PRIMARY_COLOR,
                        alignment=ALIGN_CENTER,
                        content=ft.Icon(ft.Icons.TV_ROUNDED, color=ft.Colors.WHITE, size=22),
                    ),
                    ft.Column(
                        controls=[
                            ft.Text("VIETLED CMS", weight=ft.FontWeight.BOLD, size=16, color=PRIMARY_COLOR),
                            ft.Text("Điều khiển LED tập trung", size=11, color=ft.Colors.GREY_600),
                        ],
                        spacing=1,
                    ),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        ),
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.DASHBOARD_OUTLINED,
                selected_icon=ft.Icons.DASHBOARD,
                label="Tổng quan",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.TV_OUTLINED,
                selected_icon=ft.Icons.TV,
                label="Quản lý màn hình LED",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.PERM_MEDIA_OUTLINED,
                selected_icon=ft.Icons.PERM_MEDIA,
                label="Quản lý nội dung",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.CALENDAR_MONTH_OUTLINED,
                selected_icon=ft.Icons.CALENDAR_MONTH,
                label="Lịch phát nội dung",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.TUNE_OUTLINED,
                selected_icon=ft.Icons.TUNE,
                label="Điều khiển màn hình",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.MONITOR_HEART_OUTLINED,
                selected_icon=ft.Icons.MONITOR_HEART,
                label="Giám sát thiết bị",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.PEOPLE_OUTLINE,
                selected_icon=ft.Icons.PEOPLE,
                label="Quản lý người dùng",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label="Cài đặt hệ thống",
            ),
        ],
        on_change=lambda e: navigate_to(e.control.selected_index),
    )

    # Thanh Header phía trên hiển thị người dùng đang đăng nhập và nút Đăng xuất
    top_header = ft.Container(
        height=64,
        padding=pad_sym(horizontal=24, vertical=8),
        border=border_only(bottom=ft.BorderSide(1, ft.Colors.GREY_300)),
        content=ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.CAST_CONNECTED, color=PRIMARY_COLOR, size=22),
                        ft.Text(
                            "HỆ THỐNG QUẢN TRỊ & ĐIỀU KHIỂN MÀN HÌNH LED",
                            weight=ft.FontWeight.BOLD,
                            size=15,
                        ),
                    ],
                    spacing=10,
                ),
                ft.Row(
                    controls=[
                        theme_btn,
                        ft.Container(
                            padding=pad_sym(horizontal=10, vertical=4),
                            border_radius=8,
                            content=ft.Row(
                                controls=[
                                    ft.CircleAvatar(
                                        bgcolor=PRIMARY_COLOR,
                                        radius=16,
                                        content=ft.Icon(ft.Icons.PERSON, color=ft.Colors.WHITE, size=18),
                                    ),
                                    ft.Column(
                                        controls=[user_info_text, user_role_text],
                                        spacing=0,
                                        alignment=ft.MainAxisAlignment.CENTER,
                                    ),
                                ],
                                spacing=8,
                            ),
                        ),
                        ft.OutlinedButton(
                            "Đăng xuất",
                            icon=ft.Icons.LOGOUT,
                            on_click=handle_logout,
                        ),
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    def show_main_shell():
        """Hiển thị bố cục chính gồm Sidebar bên trái, Header phía trên và vùng nội dung."""
        page.controls.clear()
        refresh_header_user()
        page.add(
            ft.Row(
                expand=True,
                spacing=0,
                controls=[
                    nav_rail,
                    ft.VerticalDivider(width=1, thickness=1),
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
        navigate_to(0)

    def show_login_screen():
        """Hiển thị màn hình đăng nhập Demo."""
        page.controls.clear()
        page.add(login.build_view(page, on_login_success=show_main_shell))
        page.update()

    # Khởi chạy ở màn hình Đăng nhập Demo
    show_login_screen()


if __name__ == "__main__":
    if hasattr(ft, "run"):
        ft.run(main)
    else:
        ft.app(target=main)
