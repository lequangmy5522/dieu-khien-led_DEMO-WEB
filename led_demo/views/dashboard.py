import flet as ft
import data
import permissions
import theme
from components import (
    border_only,
    create_page_header,
    create_stat_card,
    create_status_badge,
    create_styled_table,
    make_primary_button,
    make_surface_box,
    pad_sym,
    show_snack,
)


def build_view(page: ft.Page, on_navigate=None) -> ft.Column:
    """Trang Tổng quan: thẻ số liệu thực tế, bảng thiết bị gần đây và danh sách nhật ký."""
    role = data.get_current_role()
    can_view_control = permissions.can(role, "control", "view")

    total_screens = len(data.SCREENS_DATA)
    online_screens = sum(1 for s in data.SCREENS_DATA if s["status"] == "Online")
    offline_screens = sum(1 for s in data.SCREENS_DATA if s["status"] == "Offline")
    issue_screens = sum(1 for s in data.SCREENS_DATA if s["status"] == "Sự cố")
    total_contents = len(data.CONTENTS_DATA)
    total_schedules = len(data.SCHEDULES_DATA)
    active_schedules = sum(1 for sch in data.SCHEDULES_DATA if sch["active"])

    stats_row = ft.ResponsiveRow(
        spacing=theme.SPACE_16,
        run_spacing=theme.SPACE_16,
        controls=[
            create_stat_card(
                title="Tổng thiết bị",
                value=total_screens,
                icon_name=ft.Icons.TV_OUTLINED,
                subtitle="3 khu vực vận hành",
                col_Responsive={"sm": 6, "md": 4, "lg": 2.4},
            ),
            create_stat_card(
                title="Đang trực tuyến",
                value=online_screens,
                icon_name=ft.Icons.CHECK_CIRCLE_OUTLINE,
                subtitle=f"Tỷ lệ {int(round(online_screens * 100 / max(1, total_screens)))}% toàn mạng",
                col_Responsive={"sm": 6, "md": 4, "lg": 2.4},
            ),
            create_stat_card(
                title="Ngoại tuyến / Sự cố",
                value=offline_screens + issue_screens,
                icon_name=ft.Icons.WARNING_AMBER_OUTLINED,
                subtitle=f"{offline_screens} Offline · {issue_screens} cần kiểm tra",
                col_Responsive={"sm": 6, "md": 4, "lg": 2.4},
            ),
            create_stat_card(
                title="Tệp nội dung",
                value=total_contents,
                icon_name=ft.Icons.FOLDER_OUTLINED,
                subtitle="Lưu trữ nội bộ",
                col_Responsive={"sm": 6, "md": 6, "lg": 2.4},
            ),
            create_stat_card(
                title="Lịch phát sóng",
                value=total_schedules,
                icon_name=ft.Icons.CALENDAR_TODAY_OUTLINED,
                subtitle=f"{active_schedules} lịch đang kích hoạt",
                col_Responsive={"sm": 12, "md": 6, "lg": 2.4},
            ),
        ],
    )

    # Bảng danh sách màn hình LED gần đây
    recent_rows = []
    for scr in data.SCREENS_DATA[:7]:
        recent_rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(scr["code"], size=theme.TEXT_14, weight=theme.WEIGHT_SEMI)),
                    ft.DataCell(
                        ft.Text(
                            scr["name"],
                            size=theme.TEXT_14,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            tooltip=scr["name"],
                        )
                    ),
                    ft.DataCell(create_status_badge(scr["status"])),
                    ft.DataCell(
                        ft.Text(
                            data.get_content_name(scr["current_content_id"]),
                            size=theme.TEXT_14,
                            color=theme.text_secondary(),
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        )
                    ),
                    ft.DataCell(ft.Text(f"{scr['temperature']}°C", size=theme.TEXT_14)),
                ]
            )
        )

    recent_screens_section = make_surface_box(
        col={"sm": 12, "lg": 7},
        padding=theme.SPACE_16,
        content=ft.Column(
            spacing=theme.SPACE_12,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            "Trạng thái màn hình gần đây",
                            size=theme.TEXT_16,
                            weight=theme.WEIGHT_SEMI,
                            color=theme.text_primary(),
                        ),
                        ft.TextButton(
                            "Xem danh sách",
                            on_click=lambda e: on_navigate(1) if on_navigate else None,
                        ),
                    ],
                ),
                create_styled_table(
                    columns=[
                        ft.DataColumn(ft.Text("Mã thiết bị")),
                        ft.DataColumn(ft.Text("Tên màn hình")),
                        ft.DataColumn(ft.Text("Trạng thái")),
                        ft.DataColumn(ft.Text("Nội dung đang phát")),
                        ft.DataColumn(ft.Text("Nhiệt độ"), numeric=True),
                    ],
                    rows=recent_rows,
                ),
            ],
        ),
    )

    # Danh sách hoạt động gần đây dạng dòng kẻ mảnh
    activity_controls = []
    for idx, act in enumerate(data.ACTIVITIES_DATA[:8]):
        is_last = idx == len(data.ACTIVITIES_DATA[:8]) - 1
        activity_controls.append(
            ft.Container(
                padding=pad_sym(vertical=theme.SPACE_8),
                border=None
                if is_last
                else border_only(bottom=ft.BorderSide(theme.BORDER_WIDTH, theme.border_color())),
                content=ft.Column(
                    spacing=theme.SPACE_4,
                    controls=[
                        ft.Text(act["action"], size=theme.TEXT_14, color=theme.text_primary()),
                        ft.Text(act["time"], size=theme.TEXT_12, color=theme.text_secondary()),
                    ],
                ),
            )
        )

    recent_activities_section = make_surface_box(
        col={"sm": 12, "lg": 5},
        padding=theme.SPACE_16,
        content=ft.Column(
            spacing=theme.SPACE_12,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            "Hoạt động gần đây",
                            size=theme.TEXT_16,
                            weight=theme.WEIGHT_SEMI,
                            color=theme.text_primary(),
                        ),
                        ft.Text(
                            f"{len(data.ACTIVITIES_DATA)} bản ghi",
                            size=theme.TEXT_12,
                            color=theme.text_secondary(),
                        ),
                    ],
                ),
                ft.Column(spacing=0, controls=activity_controls),
            ],
        ),
    )

    def handle_go_control(e):
        if not permissions.can(data.get_current_role(), "control", "view"):
            show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
            return
        if on_navigate:
            on_navigate(4)

    header_actions = []
    if can_view_control:
        header_actions.append(
            make_primary_button(
                "Điều khiển màn hình",
                icon_name=ft.Icons.TUNE_OUTLINED,
                on_click=handle_go_control,
            )
        )

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=theme.SPACE_16,
        controls=[
            create_page_header(
                title="Tổng quan",
                subtitle="Số liệu vận hành hệ thống tính theo thời gian thực trong phiên làm việc.",
                right_controls=header_actions,
            ),
            stats_row,
            ft.ResponsiveRow(
                spacing=theme.SPACE_16,
                run_spacing=theme.SPACE_16,
                controls=[
                    recent_screens_section,
                    recent_activities_section,
                ],
            ),
        ],
    )
