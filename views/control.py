import asyncio
import flet as ft
import data
from components import (
    PRIMARY_COLOR,
    PRIMARY_LIGHT,
    ALIGN_CENTER,
    border_all,
    create_page_header,
    create_status_badge,
    make_dropdown,
    pad_sym,
    show_snack,
)


def build_view(page: ft.Page) -> ft.Column:
    """Xây dựng giao diện Điều khiển màn hình LED trực tiếp (Nguồn, Độ sáng, Âm lượng, Đổi nội dung)."""
    selected_id = data.SCREENS_DATA[0]["id"] if data.SCREENS_DATA else None
    state = {
        "screen_id": selected_id,
        "is_busy": False,
    }

    busy_indicator = ft.Row(
        visible=False,
        spacing=10,
        controls=[
            ft.ProgressRing(width=18, height=18, stroke_width=2.5, color=PRIMARY_COLOR),
            ft.Text("Đang gửi lệnh điều khiển tới thiết bị (chờ 2 giây)...", size=13, color=PRIMARY_COLOR, weight=ft.FontWeight.W_600),
        ],
    )

    status_badges_row = ft.Row(spacing=10)
    preview_box = ft.Container()
    brightness_label = ft.Text("", weight=ft.FontWeight.BOLD, size=14, color=PRIMARY_COLOR)
    volume_label = ft.Text("", weight=ft.FontWeight.BOLD, size=14, color=PRIMARY_COLOR)

    def get_current_screen() -> dict | None:
        return data.get_screen_by_id(state["screen_id"])

    def update_preview_and_controls():
        """Đồng bộ thông tin màn hình đang chọn lên khung xem trước và các thanh trượt."""
        scr = get_current_screen()
        if not scr:
            return

        status_badges_row.controls = [
            create_status_badge(scr["status"]),
            create_status_badge(scr["playing_state"]),
            ft.Text(f"Nhiệt độ: {scr['temperature']}°C | Độ phân giải: {scr['resolution']}", size=12, color=ft.Colors.GREY_600),
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
            height=250,
            border_radius=14,
            bgcolor=ft.Colors.INDIGO_900 if is_online else ft.Colors.GREY_900,
            border=border_all(3, PRIMARY_COLOR if is_online else ft.Colors.GREY_600),
            padding=20,
            alignment=ALIGN_CENTER,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
                controls=[
                    ft.Icon(
                        ft.Icons.PLAY_CIRCLE_FILL
                        if (is_online and is_video)
                        else (ft.Icons.IMAGE_ROUNDED if is_online else ft.Icons.POWER_OFF_ROUNDED),
                        color=ft.Colors.WHITE if is_online else ft.Colors.GREY_500,
                        size=54,
                    ),
                    ft.Text(
                        content_obj["name"] if (is_online and content_obj) else "MÀN HÌNH ĐANG TẮT / OFFLINE",
                        color=ft.Colors.WHITE,
                        size=17,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        f"Trạng thái: {scr['playing_state']} • Độ sáng: {int(scr['brightness'])}% • Âm lượng: {int(scr['volume'])}%"
                        if is_online
                        else "Hãy nhấn 'Bật nguồn' để kích hoạt lại màn hình LED",
                        color=ft.Colors.BLUE_100 if is_online else ft.Colors.GREY_400,
                        size=12,
                    ),
                ],
            ),
        )
        page.update()

    async def simulate_power_command(action_type: str):
        """Mô phỏng độ trễ 2 giây khi Bật nguồn, Tắt nguồn hoặc Khởi động lại thiết bị."""
        scr = get_current_screen()
        if not scr or state["is_busy"]:
            return

        state["is_busy"] = True
        busy_indicator.visible = True
        page.update()

        await asyncio.sleep(2.0)

        if action_type == "power_on":
            scr["status"] = "Online"
            scr["playing_state"] = "Đang phát"
            msg = f"Đã bật nguồn \"{scr['name']}\" (Trạng thái: Online)"
        elif action_type == "power_off":
            scr["status"] = "Offline"
            scr["playing_state"] = "Đã dừng"
            msg = f"Đã tắt nguồn \"{scr['name']}\" (Trạng thái: Offline)"
        else:
            scr["status"] = "Online"
            scr["playing_state"] = "Đang phát"
            scr["temperature"] = 41
            msg = f"Đã khởi động lại \"{scr['name']}\" thành công!"

        state["is_busy"] = False
        busy_indicator.visible = False
        data.log_activity(f"Điều khiển từ xa: {msg}")
        update_preview_and_controls()
        show_snack(page, msg)

    def trigger_power(action_type: str):
        page.run_task(simulate_power_command, action_type)

    def handle_playback_state(new_state: str):
        """Tạm dừng hoặc Tiếp tục phát nội dung."""
        scr = get_current_screen()
        if not scr:
            return
        if scr["status"] != "Online":
            show_snack(page, "Thiết bị đang Offline! Vui lòng bật nguồn trước.", is_error=True)
            return
        scr["playing_state"] = new_state
        msg = f"Đã chuyển \"{scr['name']}\" sang trạng thái: {new_state}"
        data.log_activity(msg)
        update_preview_and_controls()
        show_snack(page, msg)

    def handle_apply_content(e):
        """Đổi nội dung đang phát trên màn hình được chọn."""
        scr = get_current_screen()
        if not scr or not content_selector_dd.value:
            return
        scr["current_content_id"] = content_selector_dd.value
        cname = data.get_content_name(scr["current_content_id"])
        msg = f"Đã chuyển nội dung phát của \"{scr['name']}\" sang \"{cname}\""
        data.log_activity(msg)
        update_preview_and_controls()
        show_snack(page, msg)

    def handle_brightness_change(e):
        scr = get_current_screen()
        if not scr:
            return
        val = int(round(e.control.value or 0))
        scr["brightness"] = val
        brightness_label.value = f"{val}%"
        update_preview_and_controls()

    def handle_brightness_end(e):
        scr = get_current_screen()
        if not scr:
            return
        val = int(round(e.control.value or 0))
        msg = f"Đã chỉnh độ sáng \"{scr['name']}\" thành {val}%"
        data.log_activity(msg)
        show_snack(page, msg)

    def handle_volume_change(e):
        scr = get_current_screen()
        if not scr:
            return
        val = int(round(e.control.value or 0))
        scr["volume"] = val
        volume_label.value = f"{val}%"
        update_preview_and_controls()

    def handle_volume_end(e):
        scr = get_current_screen()
        if not scr:
            return
        val = int(round(e.control.value or 0))
        msg = f"Đã chỉnh âm lượng \"{scr['name']}\" thành {val}%"
        data.log_activity(msg)
        show_snack(page, msg)

    screen_selector_dd = make_dropdown(
        label="Chọn màn hình LED cần điều khiển",
        options=[(s["id"], f"{s['name']} ({s['code']} - {s['status']})") for s in data.SCREENS_DATA],
        value=selected_id,
        on_change=lambda e: (state.update({"screen_id": e.control.value}), update_preview_and_controls()),
        expand=True,
    )

    content_selector_dd = make_dropdown(
        label="Chọn nội dung phát sóng tức thì",
        options=[(c["id"], f"{c['name']} ({c['type']} - {c['format']})") for c in data.CONTENTS_DATA],
        value=data.SCREENS_DATA[0]["current_content_id"] if data.SCREENS_DATA else None,
        expand=True,
    )

    brightness_slider = ft.Slider(
        min=0,
        max=100,
        divisions=20,
        value=80,
        active_color=PRIMARY_COLOR,
        on_change=handle_brightness_change,
        on_change_end=handle_brightness_end,
        expand=True,
    )

    volume_slider = ft.Slider(
        min=0,
        max=100,
        divisions=20,
        value=50,
        active_color=PRIMARY_COLOR,
        on_change=handle_volume_change,
        on_change_end=handle_volume_end,
        expand=True,
    )

    update_preview_and_controls()

    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=16,
        controls=[
            create_page_header(
                title="Điều khiển màn hình LED",
                subtitle="Điều khiển nguồn từ xa, tạm dừng/tiếp tục trình chiếu, thay đổi nội dung tức thì và tinh chỉnh độ sáng/âm lượng.",
            ),
            ft.Card(
                elevation=2,
                content=ft.Container(
                    padding=18,
                    content=ft.Column(
                        spacing=12,
                        controls=[
                            ft.Row(
                                spacing=16,
                                wrap=True,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[screen_selector_dd, status_badges_row],
                            ),
                            busy_indicator,
                        ],
                    ),
                ),
            ),
            ft.ResponsiveRow(
                spacing=16,
                run_spacing=16,
                controls=[
                    # Cột trái: Các nút điều khiển nguồn, phát sóng, độ sáng, âm lượng
                    ft.Card(
                        col={"sm": 12, "lg": 6},
                        elevation=2,
                        content=ft.Container(
                            padding=20,
                            content=ft.Column(
                                spacing=16,
                                controls=[
                                    ft.Text("1. Điều khiển nguồn & Trạng thái phát", size=16, weight=ft.FontWeight.BOLD),
                                    ft.Row(
                                        spacing=10,
                                        wrap=True,
                                        controls=[
                                            ft.FilledButton(
                                                "Bật nguồn",
                                                icon=ft.Icons.POWER_SETTINGS_NEW,
                                                bgcolor=ft.Colors.GREEN_700,
                                                color=ft.Colors.WHITE,
                                                on_click=lambda e: trigger_power("power_on"),
                                            ),
                                            ft.FilledButton(
                                                "Tắt nguồn",
                                                icon=ft.Icons.POWER_OFF,
                                                bgcolor=ft.Colors.RED_600,
                                                color=ft.Colors.WHITE,
                                                on_click=lambda e: trigger_power("power_off"),
                                            ),
                                            ft.OutlinedButton(
                                                "Khởi động lại (2s)",
                                                icon=ft.Icons.RESTART_ALT,
                                                on_click=lambda e: trigger_power("restart"),
                                            ),
                                        ],
                                    ),
                                    ft.Row(
                                        spacing=10,
                                        wrap=True,
                                        controls=[
                                            ft.FilledButton(
                                                "Tiếp tục phát",
                                                icon=ft.Icons.PLAY_ARROW,
                                                bgcolor=PRIMARY_COLOR,
                                                color=ft.Colors.WHITE,
                                                on_click=lambda e: handle_playback_state("Đang phát"),
                                            ),
                                            ft.OutlinedButton(
                                                "Tạm dừng phát",
                                                icon=ft.Icons.PAUSE,
                                                on_click=lambda e: handle_playback_state("Tạm dừng"),
                                            ),
                                        ],
                                    ),
                                    ft.Divider(height=4),
                                    ft.Text("2. Chuyển đổi nội dung đang hiển thị", size=16, weight=ft.FontWeight.BOLD),
                                    ft.Row(
                                        spacing=10,
                                        controls=[
                                            content_selector_dd,
                                            ft.FilledButton(
                                                "Áp dụng ngay",
                                                icon=ft.Icons.SEND_TO_MOBILE,
                                                bgcolor=PRIMARY_COLOR,
                                                color=ft.Colors.WHITE,
                                                on_click=handle_apply_content,
                                            ),
                                        ],
                                    ),
                                    ft.Divider(height=4),
                                    ft.Text("3. Độ sáng & Âm lượng thiết bị", size=16, weight=ft.FontWeight.BOLD),
                                    ft.Row(
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Icon(ft.Icons.BRIGHTNESS_6, color=PRIMARY_COLOR),
                                            ft.Text("Độ sáng:", width=80),
                                            brightness_slider,
                                            brightness_label,
                                        ],
                                    ),
                                    ft.Row(
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Icon(ft.Icons.VOLUME_UP, color=PRIMARY_COLOR),
                                            ft.Text("Âm lượng:", width=80),
                                            volume_slider,
                                            volume_label,
                                        ],
                                    ),
                                ],
                            ),
                        ),
                    ),
                    # Cột phải: Khung xem trước trực tiếp
                    ft.Card(
                        col={"sm": 12, "lg": 6},
                        elevation=2,
                        content=ft.Container(
                            padding=20,
                            content=ft.Column(
                                spacing=12,
                                controls=[
                                    ft.Row(
                                        spacing=8,
                                        controls=[
                                            ft.Icon(ft.Icons.LIVE_TV, color=PRIMARY_COLOR),
                                            ft.Text("Khung xem trước nội dung đang phát (Live Preview)", size=16, weight=ft.FontWeight.BOLD),
                                        ],
                                    ),
                                    ft.Divider(height=4),
                                    preview_box,
                                    ft.Container(
                                        padding=pad_sym(horizontal=12, vertical=8),
                                        border_radius=8,
                                        bgcolor=PRIMARY_LIGHT,
                                        content=ft.Text(
                                            "Ghi chú: Mọi thao tác điều khiển tại đây đều tự động cập nhật trạng thái thiết bị và lưu vào Nhật ký hoạt động ở trang Tổng quan.",
                                            size=12,
                                            color=PRIMARY_COLOR,
                                        ),
                                    ),
                                ],
                            ),
                        ),
                    ),
                ],
            ),
        ],
    )
