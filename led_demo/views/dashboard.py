import flet as ft
import data
from components import (
    PRIMARY_COLOR,
    create_page_header,
    create_stat_card,
    create_status_badge,
    pad_sym,
)


def build_view(page: ft.Page, on_navigate=None) -> ft.Column:
    """Xây dựng giao diện Tổng quan (Dashboard) tính toán trực tiếp từ dữ liệu giả lập."""
    # Tính toán số liệu thực tế từ mock data
    total_screens = len(data.SCREENS_DATA)
    online_screens = sum(1 for s in data.SCREENS_DATA if s["status"] == "Online")
    offline_screens = sum(1 for s in data.SCREENS_DATA if s["status"] != "Online")
    issue_screens = sum(1 for s in data.SCREENS_DATA if s["status"] == "Sự cố")
    total_contents = len(data.CONTENTS_DATA)
    total_schedules = len(data.SCHEDULES_DATA)
    active_schedules = sum(1 for sch in data.SCHEDULES_DATA if sch["active"])

    # 5 thẻ thống kê trên hàng ResponsiveRow
    stats_row = ft.ResponsiveRow(
        spacing=12,
        run_spacing=12,
        controls=[
            create_stat_card(
                title="Tổng màn hình LED",
                value=total_screens,
                icon_name=ft.Icons.TV_ROUNDED,
                color=PRIMARY_COLOR,
                subtitle="Trên toàn hệ thống",
                col_Responsive={"sm": 6, "md": 4, "lg": 2.4},
            ),
            create_stat_card(
                title="Đang Online",
                value=online_screens,
                icon_name=ft.Icons.WIFI_TETHERING,
                color=ft.Colors.GREEN_700,
                subtitle="Hoạt động ổn định",
                col_Responsive={"sm": 6, "md": 4, "lg": 2.4},
            ),
            create_stat_card(
                title="Offline / Sự cố",
                value=offline_screens,
                icon_name=ft.Icons.REPORT_PROBLEM_OUTLINED,
                color=ft.Colors.RED_600,
                subtitle=f"Trong đó {issue_screens} thiết bị sự cố",
                col_Responsive={"sm": 6, "md": 4, "lg": 2.4},
            ),
            create_stat_card(
                title="Tổng số nội dung",
                value=total_contents,
                icon_name=ft.Icons.PERM_MEDIA_ROUNDED,
                color=ft.Colors.INDIGO_600,
                subtitle="Hình ảnh & Video",
                col_Responsive={"sm": 6, "md": 6, "lg": 2.4},
            ),
            create_stat_card(
                title="Tổng lịch phát",
                value=total_schedules,
                icon_name=ft.Icons.EVENT_AVAILABLE,
                color=ft.Colors.TEAL_700,
                subtitle=f"{active_schedules} lịch đang bật",
                col_Responsive={"sm": 12, "md": 6, "lg": 2.4},
            ),
        ],
    )

    # Bảng danh sách màn hình LED gần đây (hiển thị 6 màn hình đầu)
    recent_screens_rows = []
    for scr in data.SCREENS_DATA[:6]:
        recent_screens_rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(scr["code"], weight=ft.FontWeight.W_600, size=13)),
                    ft.DataCell(ft.Text(scr["name"], size=13)),
                    ft.DataCell(ft.Text(scr["location"], size=12, color=ft.Colors.GREY_700)),
                    ft.DataCell(create_status_badge(scr["status"])),
                    ft.DataCell(
                        ft.Text(
                            data.get_content_name(scr["current_content_id"]),
                            size=12,
                            italic=True,
                        )
                    ),
                ]
            )
        )

    recent_screens_card = ft.Card(
        col={"sm": 12, "lg": 7},
        elevation=2,
        content=ft.Container(
            padding=18,
            content=ft.Column(
                spacing=12,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Icon(ft.Icons.DVR, color=PRIMARY_COLOR, size=20),
                                    ft.Text("Danh sách màn hình LED gần đây", size=16, weight=ft.FontWeight.BOLD),
                                ],
                            ),
                            ft.TextButton(
                                "Xem tất cả",
                                icon=ft.Icons.ARROW_FORWARD,
                                on_click=lambda e: on_navigate(1) if on_navigate else None,
                            ),
                        ],
                    ),
                    ft.Divider(height=1),
                    ft.Row(
                        scroll=ft.ScrollMode.AUTO,
                        controls=[
                            ft.DataTable(
                                column_spacing=18,
                                heading_row_height=40,
                                data_row_min_height=44,
                                columns=[
                                    ft.DataColumn(ft.Text("Mã TB", weight=ft.FontWeight.BOLD)),
                                    ft.DataColumn(ft.Text("Tên màn hình", weight=ft.FontWeight.BOLD)),
                                    ft.DataColumn(ft.Text("Vị trí", weight=ft.FontWeight.BOLD)),
                                    ft.DataColumn(ft.Text("Trạng thái", weight=ft.FontWeight.BOLD)),
                                    ft.DataColumn(ft.Text("Nội dung đang phát", weight=ft.FontWeight.BOLD)),
                                ],
                                rows=recent_screens_rows,
                            )
                        ],
                    ),
                ],
            ),
        ),
    )

    # Danh sách hoạt động gần đây (hiển thị 8 hoạt động mới nhất)
    activity_items = []
    for act in data.ACTIVITIES_DATA[:8]:
        activity_items.append(
            ft.Container(
                padding=pad_sym(horizontal=10, vertical=8),
                border_radius=8,
                content=ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    spacing=10,
                    controls=[
                        ft.Icon(ft.Icons.HISTORY_TOGGLE_OFF, color=PRIMARY_COLOR, size=18),
                        ft.Column(
                            spacing=2,
                            expand=True,
                            controls=[
                                ft.Text(act["action"], size=13),
                                ft.Text(act["time"], size=11, color=ft.Colors.GREY_500),
                            ],
                        ),
                    ],
                ),
            )
        )

    recent_activities_card = ft.Card(
        col={"sm": 12, "lg": 5},
        elevation=2,
        content=ft.Container(
            padding=18,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE_OUTLINED, color=PRIMARY_COLOR, size=20),
                            ft.Text("Hoạt động hệ thống gần đây", size=16, weight=ft.FontWeight.BOLD),
                        ],
                    ),
                    ft.Divider(height=1),
                    ft.Column(
                        spacing=4,
                        controls=activity_items,
                    ),
                ],
            ),
        ),
    )

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=16,
        controls=[
            create_page_header(
                title="Tổng quan hệ thống",
                subtitle="Theo dõi nhanh số liệu màn hình LED, kho nội dung, lịch phát sóng và nhật ký hoạt động.",
                right_controls=[
                    ft.FilledButton(
                        "Điều khiển nhanh",
                        icon=ft.Icons.TUNE,
                        bgcolor=PRIMARY_COLOR,
                        color=ft.Colors.WHITE,
                        on_click=lambda e: on_navigate(4) if on_navigate else None,
                    ),
                ],
            ),
            stats_row,
            ft.ResponsiveRow(
                spacing=16,
                run_spacing=16,
                controls=[
                    recent_screens_card,
                    recent_activities_card,
                ],
            ),
        ],
    )
