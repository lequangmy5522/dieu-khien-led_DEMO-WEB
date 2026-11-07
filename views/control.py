import asyncio
import flet as ft
import data
import permissions
import theme
from components import (
    ALIGN_CENTER,
    border_all,
    create_access_denied_view,
    create_page_header,
    create_status_badge,
    make_dropdown,
    make_form_field,
    make_primary_button,
    make_secondary_button,
    make_surface_box,
    show_snack,
)


def build_view(page: ft.Page) -> ft.Column:
    """Trang Điều khiển màn hình: chọn thiết bị, bật/tắt/khởi động lại (trạng thái xử lý ở nút), độ sáng, âm lượng."""
    role = data.get_current_role()
    if not permissions.can(role, "control", "view"):
        return ft.Column(
            expand=True,
            controls=[create_access_denied_view(page)],
        )

    can_power = permissions.can(role, "control", "power")
    can_playback = permissions.can(role, "control", "playback")
    can_change_content = permissions.can(role, "control", "change_content")
    can_brightness = permissions.can(role, "control", "brightness")
    can_volume = permissions.can(role, "control", "volume")

    selected_id = data.SCREENS_DATA[0]["id"] if data.SCREENS_DATA else None
    state = {
        "screen_id": selected_id,
        "is_busy": False,
    }

    status_badges_row = ft.Row(spacing=theme.SPACE_16, wrap=True)
    preview_box = ft.Container()
    brightness_label = ft.Text("", weight=theme.WEIGHT_SEMI, size=theme.TEXT_14, width=48)
    volume_label = ft.Text("", weight=theme.WEIGHT_SEMI, size=theme.TEXT_14, width=48)

    power_tooltip = None if can_power else "Cần quyền Quản trị viên"
    power_on_btn = make_primary_button(
        "Bật nguồn",
        on_click=lambda e: trigger_power("power_on"),
        disabled=not can_power,
        tooltip=power_tooltip,
    )
    power_off_btn = make_secondary_button(
        "Tắt nguồn",
        on_click=lambda e: trigger_power("power_off"),
        disabled=not can_power,
        tooltip=power_tooltip,
    )
    restart_btn = make_secondary_button(
        "Khởi động lại",
        on_click=lambda e: trigger_power("restart"),
        disabled=not can_power,
        tooltip=power_tooltip,
    )

    def get_current_screen() -> dict | None:
        return data.get_screen_by_id(state["screen_id"])

    def update_preview_and_controls(update_page: bool = True):
        scr = get_current_screen()
        if not scr:
            return

        status_badges_row.controls = [
            create_status_badge(scr["status"]),
            create_status_badge(scr["playing_state"]),
            ft.Text(
                f"Nhiệt độ: {scr['temperature']}°C  |  {scr['resolution']}",
                size=theme.TEXT_12,
                color=theme.text_secondary(),
            ),
        ]

        brightness_slider.value = scr["brightness"]
        volume_slider.value = scr["volume"]
        brightness_label.value = f"{int(scr['brightness'])}%"
        volume_label.value = f"{int(scr['volume'])}%"
        content_selector_dd.value = scr["current_content_id"]

        content_obj = data.get_content_by_id(scr["current_content_id"])
        is_online = scr["status"] == "Online"
        is_video = content_obj and content_obj["type"] == "Video"

        preview_box.content = ft.Container(
            height=240,
            border_radius=theme.RADIUS_CARD,
            bgcolor=theme.surface_subtle_color(),
            border=border_all(theme.BORDER_WIDTH, theme.border_color()),
            padding=theme.SPACE_24,
            alignment=ALIGN_CENTER,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=theme.SPACE_8,
                controls=[
                    ft.Icon(
                        ft.Icons.PLAY_CIRCLE_OUTLINE
                        if (is_online and is_video)
                        else (ft.Icons.IMAGE_OUTLINED if is_online else ft.Icons.POWER_OFF_OUTLINED),
                        color=theme.accent_color() if is_online else theme.text_secondary(),
                        size=32,
                    ),
                    ft.Text(
                        content_obj["name"] if (is_online and content_obj) else "Thiết bị đang tắt hoặc mất kết nối",
                        color=theme.text_primary(),
                        size=theme.TEXT_16,
                        weight=theme.WEIGHT_SEMI,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        f"{scr['playing_state']}  ·  Độ sáng {int(scr['brightness'])}%  ·  Âm lượng {int(scr['volume'])}%"
                        if is_online
                        else "Nhấn 'Bật nguồn' để kết nối lại với bộ điều khiển màn hình.",
                        color=theme.text_secondary(),
                        size=theme.TEXT_12,
                    ),
                ],
            ),
        )
        if update_page:
            page.update()

    async def simulate_power_command(action_type: str):
        """Khóa các nút nguồn và đổi chữ hiển thị trạng thái xử lý trong 2 giây."""
        if not permissions.can(data.get_current_role(), "control", "power"):
            show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
            return

        scr = get_current_screen()
        if not scr or state["is_busy"]:
            return

        state["is_busy"] = True
        power_on_btn.disabled = True
        power_off_btn.disabled = True
        restart_btn.disabled = True

        if action_type == "power_on":
            power_on_btn.content = "Đang bật nguồn..."
        elif action_type == "power_off":
            power_off_btn.content = "Đang tắt nguồn..."
        else:
            restart_btn.content = "Đang khởi động lại..."
        page.update()

        await asyncio.sleep(2.0)

        if action_type == "power_on":
            scr["status"] = "Online"
            scr["playing_state"] = "Đang phát"
            msg = f"Đã bật nguồn {scr['code']}"
        elif action_type == "power_off":
            scr["status"] = "Offline"
            scr["playing_state"] = "Đã dừng"
            msg = f"Đã tắt nguồn {scr['code']}"
        else:
            scr["status"] = "Online"
            scr["playing_state"] = "Đang phát"
            scr["temperature"] = 41
            msg = f"Đã khởi động lại {scr['code']}"

        allow_power_now = permissions.can(data.get_current_role(), "control", "power")
        power_on_btn.content = "Bật nguồn"
        power_off_btn.content = "Tắt nguồn"
        restart_btn.content = "Khởi động lại"
        power_on_btn.disabled = not allow_power_now
        power_off_btn.disabled = not allow_power_now
        restart_btn.disabled = not allow_power_now
        state["is_busy"] = False

        data.log_activity(f"Lệnh điều khiển: {msg} ({scr['name']}).")
        update_preview_and_controls()
        show_snack(page, msg)

    def trigger_power(action_type: str):
        if not permissions.can(data.get_current_role(), "control", "power"):
            show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
            return
        page.run_task(simulate_power_command, action_type)

    def handle_playback_state(new_state: str):
        if not permissions.can(data.get_current_role(), "control", "playback"):
            show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
            return

        scr = get_current_screen()
        if not scr:
            return
        if scr["status"] != "Online":
            show_snack(page, "Thiết bị đang Offline, không thể đổi trạng thái phát.", is_error=True)
            return
        scr["playing_state"] = new_state
        msg = f"{scr['code']}: {new_state}"
        data.log_activity(f"Chuyển trạng thái phát {scr['code']} sang '{new_state}'.")
        update_preview_and_controls()
        show_snack(page, msg)

    def handle_apply_content(e):
        if not permissions.can(data.get_current_role(), "control", "change_content"):
            show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
            return

        scr = get_current_screen()
        if not scr or not content_selector_dd.value:
            return
        scr["current_content_id"] = content_selector_dd.value
        cname = data.get_content_name(scr["current_content_id"])
        data.log_activity(f"Đổi nội dung phát trên {scr['code']} sang '{cname}'.")
        update_preview_and_controls()
        show_snack(page, f"Đã phát '{cname}' trên {scr['code']}")

    def handle_brightness_change(e):
        if not permissions.can(data.get_current_role(), "control", "brightness"):
            return
        scr = get_current_screen()
        if not scr:
            return
        val = int(round(e.control.value or 0))
        scr["brightness"] = val
        brightness_label.value = f"{val}%"
        update_preview_and_controls()

    def handle_brightness_end(e):
        if not permissions.can(data.get_current_role(), "control", "brightness"):
            show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
            return
        scr = get_current_screen()
        if not scr:
            return
        val = int(round(e.control.value or 0))
        data.log_activity(f"Điều chỉnh độ sáng {scr['code']} thành {val}%.")
        show_snack(page, f"Độ sáng {scr['code']}: {val}%")

    def handle_volume_change(e):
        if not permissions.can(data.get_current_role(), "control", "volume"):
            return
        scr = get_current_screen()
        if not scr:
            return
        val = int(round(e.control.value or 0))
        scr["volume"] = val
        volume_label.value = f"{val}%"
        update_preview_and_controls()

    def handle_volume_end(e):
        if not permissions.can(data.get_current_role(), "control", "volume"):
            show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
            return
        scr = get_current_screen()
        if not scr:
            return
        val = int(round(e.control.value or 0))
        data.log_activity(f"Điều chỉnh âm lượng {scr['code']} thành {val}%.")
        show_snack(page, f"Âm lượng {scr['code']}: {val}%")

    screen_selector_dd = make_dropdown(
        label="",
        options=[(s["id"], f"{s['code']} - {s['name']} ({s['status']})") for s in data.SCREENS_DATA],
        value=selected_id,
        on_change=lambda e: (state.update({"screen_id": e.control.value}), update_preview_and_controls()),
        width=420,
    )

    content_selector_dd = make_dropdown(
        label="",
        options=[(c["id"], f"{c['name']} ({c['format']})") for c in data.CONTENTS_DATA],
        value=data.SCREENS_DATA[0]["current_content_id"] if data.SCREENS_DATA else None,
        expand=True,
    )

    brightness_slider = ft.Slider(
        min=0,
        max=100,
        divisions=20,
        value=80,
        disabled=not can_brightness,
        active_color=theme.accent_color(),
        on_change=handle_brightness_change,
        on_change_end=handle_brightness_end,
        expand=True,
    )

    volume_slider = ft.Slider(
        min=0,
        max=100,
        divisions=20,
        value=50,
        disabled=not can_volume,
        active_color=theme.accent_color(),
        on_change=handle_volume_change,
        on_change_end=handle_volume_end,
        expand=True,
    )

    update_preview_and_controls(update_page=False)

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=theme.SPACE_16,
        controls=[
            create_page_header(
                title="Điều khiển màn hình",
                subtitle="Gửi lệnh điều khiển nguồn, chuyển nội dung phát tức thời và chỉnh thông số hiển thị.",
            ),
            make_surface_box(
                padding=theme.SPACE_16,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    wrap=True,
                    controls=[
                        make_form_field("Thiết bị đang chọn", screen_selector_dd),
                        status_badges_row,
                    ],
                ),
            ),
            ft.ResponsiveRow(
                spacing=theme.SPACE_16,
                run_spacing=theme.SPACE_16,
                controls=[
                    make_surface_box(
                        col={"sm": 12, "lg": 6},
                        padding=theme.SPACE_24,
                        content=ft.Column(
                            spacing=theme.SPACE_16,
                            controls=[
                                ft.Text("Nguồn & Trạng thái trình chiếu", size=theme.TEXT_16, weight=theme.WEIGHT_SEMI),
                                ft.Row(
                                    spacing=theme.SPACE_8,
                                    wrap=True,
                                    controls=[power_on_btn, power_off_btn, restart_btn],
                                ),
                                ft.Row(
                                    spacing=theme.SPACE_8,
                                    wrap=True,
                                    controls=[
                                        make_secondary_button(
                                            "Tiếp tục phát",
                                            icon_name=ft.Icons.PLAY_ARROW_OUTLINED,
                                            disabled=not can_playback,
                                            on_click=lambda e: handle_playback_state("Đang phát"),
                                        ),
                                        make_secondary_button(
                                            "Tạm dừng",
                                            icon_name=ft.Icons.PAUSE_OUTLINED,
                                            disabled=not can_playback,
                                            on_click=lambda e: handle_playback_state("Tạm dừng"),
                                        ),
                                    ],
                                ),
                                ft.Divider(height=theme.SPACE_8, color=theme.border_color()),
                                ft.Text("Chuyển đổi nội dung phát", size=theme.TEXT_16, weight=theme.WEIGHT_SEMI),
                                ft.Row(
                                    spacing=theme.SPACE_8,
                                    controls=[
                                        content_selector_dd,
                                        make_primary_button(
                                            "Áp dụng",
                                            disabled=not can_change_content,
                                            on_click=handle_apply_content,
                                        ),
                                    ],
                                ),
                                ft.Divider(height=theme.SPACE_8, color=theme.border_color()),
                                ft.Text("Thông số độ sáng & âm lượng", size=theme.TEXT_16, weight=theme.WEIGHT_SEMI),
                                ft.Row(
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Text("Độ sáng", size=theme.TEXT_14, width=80, color=theme.text_secondary()),
                                        brightness_slider,
                                        brightness_label,
                                    ],
                                ),
                                ft.Row(
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Text("Âm lượng", size=theme.TEXT_14, width=80, color=theme.text_secondary()),
                                        volume_slider,
                                        volume_label,
                                    ],
                                ),
                            ],
                        ),
                    ),
                    make_surface_box(
                        col={"sm": 12, "lg": 6},
                        padding=theme.SPACE_24,
                        content=ft.Column(
                            spacing=theme.SPACE_16,
                            controls=[
                                ft.Text("Khung giám sát nội dung đang phát", size=theme.TEXT_16, weight=theme.WEIGHT_SEMI),
                                preview_box,
                                ft.Text(
                                    "Lệnh điều khiển nguồn có độ trễ phản hồi khoảng 2 giây từ tủ điều khiển.",
                                    size=theme.TEXT_12,
                                    color=theme.text_secondary(),
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        ],
    )
