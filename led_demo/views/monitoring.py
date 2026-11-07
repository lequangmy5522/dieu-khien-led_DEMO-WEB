from datetime import datetime
import flet as ft
import data
import permissions
import theme
from components import (
    border_all,
    border_only,
    create_empty_state,
    create_page_header,
    create_status_badge,
    make_dropdown,
    make_secondary_button,
    make_surface_box,
    pad_sym,
    show_snack,
)


def build_view(page: ft.Page) -> ft.Column:
    """Trang Giám sát thiết bị: khu vực cảnh báo sự cố, bộ lọc trạng thái, thẻ thông số kỹ thuật."""
    filter_state = {
        "status": "Tất cả",
        "last_updated": datetime.now().strftime("%H:%M"),
    }

    issues_section = ft.Container()
    devices_grid_area = ft.Column(spacing=theme.SPACE_16)
    updated_note_text = ft.Text("", size=theme.TEXT_12, color=theme.text_secondary())

    def build_issues_alert_box():
        """Hiển thị danh sách thiết bị đang gặp sự cố hoặc quá nhiệt (> 60°C)."""
        problem_screens = [
            s for s in data.SCREENS_DATA if s["status"] == "Sự cố" or s["temperature"] > 60
        ]
        if not problem_screens:
            issues_section.content = make_surface_box(
                padding=theme.SPACE_12,
                content=ft.Row(
                    spacing=theme.SPACE_8,
                    controls=[
                        ft.Container(
                            width=theme.DOT_SIZE,
                            height=theme.DOT_SIZE,
                            border_radius=theme.DOT_SIZE,
                            bgcolor=theme.STATUS_ONLINE,
                        ),
                        ft.Text(
                            "Toàn bộ thiết bị đang nằm trong ngưỡng nhiệt độ vận hành cho phép (≤ 60°C).",
                            size=theme.TEXT_14,
                            color=theme.text_primary(),
                        ),
                    ],
                ),
            )
            return

        issue_rows = []
        for idx, s in enumerate(problem_screens):
            temp_val = s["temperature"]
            reasons = []
            if s["status"] == "Sự cố":
                reasons.append("Mất đồng bộ tín hiệu")
            if temp_val > 60:
                reasons.append(f"Nhiệt độ cao: {temp_val}°C")

            issue_rows.append(
                ft.Container(
                    padding=pad_sym(vertical=theme.SPACE_8),
                    border=border_only(bottom=ft.BorderSide(theme.BORDER_WIDTH, theme.border_color()))
                    if idx < len(problem_screens) - 1
                    else None,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        wrap=True,
                        controls=[
                            ft.Row(
                                spacing=theme.SPACE_12,
                                controls=[
                                    ft.Text(s["code"], size=theme.TEXT_14, weight=theme.WEIGHT_SEMI),
                                    ft.Text(s["name"], size=theme.TEXT_14, color=theme.text_primary()),
                                    ft.Text(f"({s['location']})", size=theme.TEXT_12, color=theme.text_secondary()),
                                ],
                            ),
                            ft.Text(
                                " · ".join(reasons),
                                size=theme.TEXT_14,
                                weight=theme.WEIGHT_SEMI,
                                color=theme.STATUS_DANGER,
                            ),
                        ],
                    ),
                )
            )

        issues_section.content = ft.Container(
            padding=theme.SPACE_16,
            bgcolor=theme.surface_color(),
            border=border_all(theme.BORDER_WIDTH, theme.STATUS_DANGER),
            border_radius=theme.RADIUS_CARD,
            content=ft.Column(
                spacing=theme.SPACE_8,
                controls=[
                    ft.Row(
                        spacing=theme.SPACE_8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.WARNING_AMBER_OUTLINED, color=theme.STATUS_DANGER, size=theme.ICON_SM),
                            ft.Text(
                                f"Thiết bị cần kiểm tra kỹ thuật ({len(problem_screens)})",
                                size=theme.TEXT_16,
                                weight=theme.WEIGHT_SEMI,
                                color=theme.STATUS_DANGER,
                            ),
                        ],
                    ),
                    ft.Column(spacing=0, controls=issue_rows),
                ],
            ),
        )

    def refresh_monitoring(update_page: bool = True):
        build_issues_alert_box()
        st_filter = filter_state["status"]
        filtered = [
            s for s in data.SCREENS_DATA if st_filter == "Tất cả" or s["status"] == st_filter
        ]
        updated_note_text.value = (
            f"Hiển thị {len(filtered)}/{len(data.SCREENS_DATA)} thiết bị · Cập nhật lúc {filter_state['last_updated']}"
        )

        if not filtered:
            devices_grid_area.controls = [create_empty_state("Không có thiết bị nào ở trạng thái này.")]
            if update_page:
                page.update()
            return

        cards = []
        for scr in filtered:
            temp = scr["temperature"]
            is_hot = temp > 60
            temp_color = (
                theme.STATUS_DANGER
                if is_hot
                else (theme.STATUS_WARNING if temp >= 52 else theme.text_primary())
            )

            cards.append(
                ft.Container(
                    col={"sm": 12, "md": 6, "lg": 4},
                    padding=theme.SPACE_16,
                    bgcolor=theme.surface_color(),
                    border=border_all(
                        theme.BORDER_WIDTH,
                        theme.STATUS_DANGER if is_hot else theme.border_color(),
                    ),
                    border_radius=theme.RADIUS_CARD,
                    content=ft.Column(
                        spacing=theme.SPACE_8,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.START,
                                controls=[
                                    ft.Column(
                                        spacing=theme.SPACE_4,
                                        expand=True,
                                        controls=[
                                            ft.Text(
                                                scr["name"],
                                                weight=theme.WEIGHT_SEMI,
                                                size=theme.TEXT_14,
                                                max_lines=1,
                                                overflow=ft.TextOverflow.ELLIPSIS,
                                                tooltip=scr["name"],
                                            ),
                                            ft.Text(
                                                f"{scr['code']} · {scr['size']}",
                                                size=theme.TEXT_12,
                                                color=theme.text_secondary(),
                                            ),
                                        ],
                                    ),
                                    create_status_badge(scr["status"]),
                                ],
                            ),
                            ft.Divider(height=theme.SPACE_8, color=theme.border_color()),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text("Trạng thái phát", size=theme.TEXT_12, color=theme.text_secondary()),
                                    create_status_badge(scr["playing_state"]),
                                ],
                            ),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text("Thời gian chạy", size=theme.TEXT_12, color=theme.text_secondary()),
                                    ft.Text(scr["uptime"], size=theme.TEXT_14),
                                ],
                            ),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text("Kết nối cuối", size=theme.TEXT_12, color=theme.text_secondary()),
                                    ft.Text(scr["last_connected"], size=theme.TEXT_12, color=theme.text_secondary()),
                                ],
                            ),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text("Nhiệt độ tủ điều khiển", size=theme.TEXT_12, color=theme.text_secondary()),
                                    ft.Text(
                                        f"{temp}°C {'(Quá nhiệt)' if is_hot else ''}",
                                        size=theme.TEXT_14,
                                        weight=theme.WEIGHT_SEMI,
                                        color=temp_color,
                                    ),
                                ],
                            ),
                        ],
                    ),
                )
            )

        devices_grid_area.controls = [
            ft.ResponsiveRow(spacing=theme.SPACE_16, run_spacing=theme.SPACE_16, controls=cards)
        ]
        if update_page:
            page.update()

    def handle_refresh_metrics(e):
        if not permissions.can(data.get_current_role(), "monitoring", "refresh"):
            show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
            return

        data.randomize_monitoring_metrics()
        filter_state["last_updated"] = datetime.now().strftime("%H:%M")
        data.log_activity("Làm mới thông số nhiệt độ và trạng thái kết nối thiết bị.")
        refresh_monitoring()
        show_snack(page, f"Đã cập nhật số liệu lúc {filter_state['last_updated']}")

    status_dd = make_dropdown(
        label="Trạng thái",
        options=["Tất cả", "Online", "Offline", "Sự cố"],
        value="Tất cả",
        on_change=lambda e: (filter_state.update({"status": e.control.value or "Tất cả"}), refresh_monitoring()),
        width=180,
    )

    role = data.get_current_role()
    header_actions = []
    if permissions.can(role, "monitoring", "refresh"):
        header_actions.append(
            make_secondary_button(
                "Làm mới",
                icon_name=ft.Icons.REFRESH_OUTLINED,
                on_click=handle_refresh_metrics,
            )
        )

    refresh_monitoring(update_page=False)

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=theme.SPACE_16,
        controls=[
            create_page_header(
                title="Giám sát thiết bị",
                subtitle="Theo dõi thông số nhiệt độ tủ nguồn, thời gian hoạt động và kết nối cuối.",
                right_controls=header_actions,
            ),
            issues_section,
            make_surface_box(
                padding=theme.SPACE_12,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    wrap=True,
                    controls=[status_dd, updated_note_text],
                ),
            ),
            devices_grid_area,
        ],
    )
