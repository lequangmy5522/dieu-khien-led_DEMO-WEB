import flet as ft
import data
from components import (
    PRIMARY_COLOR,
    border_all,
    create_page_header,
    create_status_badge,
    make_dropdown,
    pad_sym,
    show_snack,
)


def build_view(page: ft.Page) -> ft.Column:
    """Xây dựng giao diện Giám sát thiết bị: nhiệt độ, thời gian hoạt động, danh sách sự cố, nút Làm mới."""
    filter_state = {"status": "Tất cả"}

    issues_section = ft.Container()
    devices_grid_area = ft.Column(spacing=12)
    summary_text = ft.Text("", size=13, color=ft.Colors.GREY_600)

    def build_issues_alert_box():
        """Khu vực cảnh báo riêng cho các thiết bị đang gặp sự cố hoặc nhiệt độ > 60°C."""
        problem_screens = [
            s for s in data.SCREENS_DATA if s["status"] == "Sự cố" or s["temperature"] > 60
        ]
        if not problem_screens:
            issues_section.content = ft.Container(
                padding=14,
                border_radius=12,
                bgcolor=ft.Colors.GREEN_50,
                border=border_all(1, ft.Colors.GREEN_300),
                content=ft.Row(
                    spacing=10,
                    controls=[
                        ft.Icon(ft.Icons.VERIFIED, color=ft.Colors.GREEN_700, size=24),
                        ft.Text(
                            "Tất cả thiết bị đang có nhiệt độ an toàn (≤ 60°C) và không ghi nhận sự cố phần cứng.",
                            color=ft.Colors.GREEN_900,
                            weight=ft.FontWeight.W_500,
                        ),
                    ],
                ),
            )
            return

        issue_rows = []
        for s in problem_screens:
            temp_val = s["temperature"]
            reason = []
            if s["status"] == "Sự cố":
                reason.append("Trạng thái: Sự cố")
            if temp_val > 60:
                reason.append(f"Quá nhiệt: {temp_val}°C (> 60°C)")

            issue_rows.append(
                ft.Container(
                    padding=pad_sym(horizontal=12, vertical=8),
                    border_radius=8,
                    bgcolor=ft.Colors.WHITE,
                    border=border_all(1, ft.Colors.RED_200),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        wrap=True,
                        controls=[
                            ft.Row(
                                spacing=10,
                                controls=[
                                    ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.RED_600),
                                    ft.Column(
                                        spacing=2,
                                        controls=[
                                            ft.Text(
                                                f"{s['name']} ({s['code']})",
                                                weight=ft.FontWeight.BOLD,
                                                size=13,
                                                color=ft.Colors.RED_900,
                                            ),
                                            ft.Text(
                                                f"Vị trí: {s['location']} | Kết nối gần nhất: {s['last_connected']}",
                                                size=12,
                                                color=ft.Colors.GREY_700,
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            ft.Container(
                                bgcolor=ft.Colors.RED_600,
                                border_radius=16,
                                padding=pad_sym(horizontal=10, vertical=4),
                                content=ft.Text(
                                    " • ".join(reason),
                                    color=ft.Colors.WHITE,
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ),
                        ],
                    ),
                )
            )

        issues_section.content = ft.Container(
            padding=16,
            border_radius=12,
            bgcolor=ft.Colors.RED_50,
            border=border_all(1.5, ft.Colors.RED_400),
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.NOTIFICATION_IMPORTANT, color=ft.Colors.RED_700, size=22),
                            ft.Text(
                                f"Khu vực cảnh báo thiết bị gặp sự cố / quá nhiệt ({len(problem_screens)} thiết bị)",
                                size=15,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.RED_800,
                            ),
                        ],
                    ),
                    *issue_rows,
                ],
            ),
        )

    def refresh_monitoring():
        """Vẽ lại khu vực cảnh báo sự cố và lưới thẻ giám sát từng thiết bị."""
        build_issues_alert_box()

        st_filter = filter_state["status"]
        filtered = [
            s for s in data.SCREENS_DATA if st_filter == "Tất cả" or s["status"] == st_filter
        ]
        summary_text.value = f"Đang hiển thị {len(filtered)} / {len(data.SCREENS_DATA)} thiết bị"

        cards = []
        for scr in filtered:
            temp = scr["temperature"]
            is_hot = temp > 60
            temp_color = ft.Colors.RED_600 if is_hot else (ft.Colors.AMBER_800 if temp >= 50 else ft.Colors.GREEN_700)
            temp_bg = ft.Colors.RED_50 if is_hot else (ft.Colors.AMBER_50 if temp >= 50 else ft.Colors.GREEN_50)

            cards.append(
                ft.Card(
                    col={"sm": 12, "md": 6, "lg": 4},
                    elevation=2,
                    content=ft.Container(
                        padding=16,
                        border_radius=12,
                        border=border_all(1.5, ft.Colors.RED_400) if is_hot else None,
                        content=ft.Column(
                            spacing=10,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Column(
                                            spacing=2,
                                            expand=True,
                                            controls=[
                                                ft.Text(scr["name"], weight=ft.FontWeight.BOLD, size=15),
                                                ft.Text(f"Mã TB: {scr['code']} • {scr['location']}", size=12, color=ft.Colors.GREY_600),
                                            ],
                                        ),
                                        create_status_badge(scr["status"]),
                                    ],
                                ),
                                ft.Divider(height=4),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text("Trạng thái phát:", size=12, color=ft.Colors.GREY_600),
                                        create_status_badge(scr["playing_state"]),
                                    ],
                                ),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text("Nội dung đang phát:", size=12, color=ft.Colors.GREY_600),
                                        ft.Text(
                                            data.get_content_name(scr["current_content_id"]),
                                            size=12,
                                            weight=ft.FontWeight.W_600,
                                        ),
                                    ],
                                ),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text("Thời gian hoạt động:", size=12, color=ft.Colors.GREY_600),
                                        ft.Text(scr["uptime"], size=12, weight=ft.FontWeight.W_500),
                                    ],
                                ),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text("Kết nối gần nhất:", size=12, color=ft.Colors.GREY_600),
                                        ft.Text(scr["last_connected"], size=12),
                                    ],
                                ),
                                ft.Container(
                                    padding=pad_sym(horizontal=12, vertical=8),
                                    border_radius=8,
                                    bgcolor=temp_bg,
                                    content=ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[
                                            ft.Row(
                                                spacing=6,
                                                controls=[
                                                    ft.Icon(ft.Icons.THERMOSTAT, color=temp_color, size=20),
                                                    ft.Text(
                                                        "Nhiệt độ phần cứng:",
                                                        size=13,
                                                        weight=ft.FontWeight.W_600,
                                                        color=temp_color,
                                                    ),
                                                ],
                                            ),
                                            ft.Text(
                                                f"{temp}°C {'(Quá nhiệt!)' if is_hot else '(Bình thường)'}",
                                                size=14,
                                                weight=ft.FontWeight.BOLD,
                                                color=temp_color,
                                            ),
                                        ],
                                    ),
                                ),
                            ],
                        ),
                    ),
                )
            )

        devices_grid_area.controls = [
            ft.ResponsiveRow(spacing=14, run_spacing=14, controls=cards)
        ]
        page.update()

    def handle_refresh_metrics(e):
        """Làm mới ngẫu nhiên số liệu nhiệt độ và thời gian kết nối."""
        data.randomize_monitoring_metrics()
        data.log_activity("Đã làm mới số liệu cảm biến nhiệt độ và trạng thái giám sát thiết bị.")
        refresh_monitoring()
        show_snack(page, "Đã cập nhật ngẫu nhiên số liệu nhiệt độ & kết nối thiết bị!")

    status_dd = make_dropdown(
        label="Lọc theo trạng thái",
        options=["Tất cả", "Online", "Offline", "Sự cố"],
        value="Tất cả",
        on_change=lambda e: (filter_state.update({"status": e.control.value or "Tất cả"}), refresh_monitoring()),
        width=200,
    )

    refresh_monitoring()

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=16,
        controls=[
            create_page_header(
                title="Giám sát thiết bị",
                subtitle="Theo dõi thông số vận hành thời gian thực, cảnh báo nhiệt độ (> 60°C) và danh sách thiết bị sự cố.",
                right_controls=[
                    ft.FilledButton(
                        "Làm mới số liệu",
                        icon=ft.Icons.REFRESH,
                        bgcolor=PRIMARY_COLOR,
                        color=ft.Colors.WHITE,
                        on_click=handle_refresh_metrics,
                    )
                ],
            ),
            issues_section,
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                wrap=True,
                controls=[status_dd, summary_text],
            ),
            devices_grid_area,
        ],
    )
