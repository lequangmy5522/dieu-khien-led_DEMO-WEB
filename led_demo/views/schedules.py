import calendar
from datetime import date, datetime, time
import flet as ft
import data
from components import (
    PRIMARY_COLOR,
    PRIMARY_LIGHT,
    ALIGN_CENTER,
    border_all,
    close_dialog,
    create_page_header,
    create_status_badge,
    make_dropdown,
    open_dialog,
    pad_sym,
    set_field_error,
    show_confirm_delete_dialog,
    show_snack,
)

WEEKDAY_LABELS = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]


def build_view(page: ft.Page) -> ft.Column:
    """Xây dựng giao diện Lịch phát nội dung với 2 chế độ: Danh sách và Lịch tháng tự dựng."""
    now = datetime.now()
    cal_state = {
        "year": now.year,
        "month": now.month,
    }

    list_container = ft.Column(spacing=10)
    calendar_grid_container = ft.Column(spacing=8)
    month_title_text = ft.Text("", size=18, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR)

    def is_schedule_on_date(sch: dict, target_date: date) -> bool:
        """Kiểm tra xem một lịch phát có diễn ra vào ngày target_date hay không."""
        start_d = data.parse_vn_date(sch["start_date"])
        end_d = data.parse_vn_date(sch["end_date"])
        if not start_d or not end_d:
            return False
        if not (start_d <= target_date <= end_d):
            return False

        rep = sch.get("repeat", "Không lặp")
        if rep == "Hằng tuần" and sch.get("weekdays"):
            wd_code = WEEKDAY_LABELS[target_date.weekday()]
            return wd_code in sch["weekdays"]
        return True

    def open_schedule_form_dialog(schedule_to_edit: dict | None = None):
        """Hộp thoại Tạo mới / Chỉnh sửa lịch phát có DatePicker, TimePicker và kiểm tra hợp lệ."""
        is_edit = schedule_to_edit is not None
        today_str = datetime.now().strftime("%d/%m/%Y")

        name_field = ft.TextField(
            label="Tên lịch phát *",
            value=schedule_to_edit["name"] if is_edit else "",
            border_radius=8,
        )

        screen_opts = [(s["id"], f"{s['name']} ({s['code']})") for s in data.SCREENS_DATA]
        screen_dd = make_dropdown(
            label="Chọn màn hình LED *",
            options=screen_opts,
            value=schedule_to_edit["screen_id"]
            if is_edit
            else (data.SCREENS_DATA[0]["id"] if data.SCREENS_DATA else None),
        )

        content_opts = [(c["id"], f"{c['name']} ({c['type']})") for c in data.CONTENTS_DATA]
        content_dd = make_dropdown(
            label="Chọn nội dung phát *",
            options=content_opts,
            value=schedule_to_edit["content_id"]
            if is_edit
            else (data.CONTENTS_DATA[0]["id"] if data.CONTENTS_DATA else None),
        )

        start_date_field = ft.TextField(
            label="Ngày bắt đầu *",
            value=schedule_to_edit["start_date"] if is_edit else today_str,
            read_only=True,
            expand=True,
            border_radius=8,
        )
        end_date_field = ft.TextField(
            label="Ngày kết thúc *",
            value=schedule_to_edit["end_date"] if is_edit else today_str,
            read_only=True,
            expand=True,
            border_radius=8,
        )
        start_time_field = ft.TextField(
            label="Giờ bắt đầu *",
            value=schedule_to_edit["start_time"] if is_edit else "08:00",
            read_only=True,
            expand=True,
            border_radius=8,
        )
        end_time_field = ft.TextField(
            label="Giờ kết thúc *",
            value=schedule_to_edit["end_time"] if is_edit else "18:00",
            read_only=True,
            expand=True,
            border_radius=8,
        )

        def pick_date(target_tf: ft.TextField):
            """Mở DatePicker cập nhật vào ô ngày tương ứng."""
            cur_d = data.parse_vn_date(target_tf.value or "") or date.today()
            dp = ft.DatePicker(
                first_date=datetime(2024, 1, 1),
                last_date=datetime(2030, 12, 31),
                value=datetime(cur_d.year, cur_d.month, cur_d.day),
                help_text="Chọn ngày lịch phát",
                cancel_text="Hủy",
                confirm_text="Chọn",
            )

            def on_dp_change(e):
                if dp.value:
                    val = dp.value
                    target_tf.value = val.strftime("%d/%m/%Y")
                    set_field_error(target_tf, None)
                    page.update()

            dp.on_change = on_dp_change
            open_dialog(page, dp)

        def pick_time(target_tf: ft.TextField):
            """Mở TimePicker cập nhật vào ô giờ tương ứng."""
            parts = (target_tf.value or "08:00").split(":")
            hr = int(parts[0]) if len(parts) == 2 and parts[0].isdigit() else 8
            mn = int(parts[1]) if len(parts) == 2 and parts[1].isdigit() else 0
            tp = ft.TimePicker(
                value=time(hr, mn),
                help_text="Chọn giờ phát sóng",
                cancel_text="Hủy",
                confirm_text="Chọn",
            )

            def on_tp_change(e):
                if tp.value:
                    target_tf.value = f"{tp.value.hour:02d}:{tp.value.minute:02d}"
                    set_field_error(target_tf, None)
                    page.update()

            tp.on_change = on_tp_change
            open_dialog(page, tp)

        # Lựa chọn thứ trong tuần khi chọn "Hằng tuần"
        init_weekdays = schedule_to_edit.get("weekdays", []) if is_edit else ["T2", "T4", "T6"]
        weekday_checks = {}
        for wd in WEEKDAY_LABELS:
            weekday_checks[wd] = ft.Checkbox(label=wd, value=(wd in init_weekdays))

        weekday_row = ft.Container(
            visible=(schedule_to_edit["repeat"] == "Hằng tuần") if is_edit else False,
            padding=8,
            border_radius=8,
            bgcolor=PRIMARY_LIGHT,
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Text("Chọn các thứ lặp lại trong tuần:", size=12, weight=ft.FontWeight.W_600),
                    ft.Row(spacing=6, wrap=True, controls=list(weekday_checks.values())),
                ],
            ),
        )

        def on_repeat_change(e):
            weekday_row.visible = (repeat_dd.value == "Hằng tuần")
            page.update()

        repeat_dd = make_dropdown(
            label="Chế độ lặp lại *",
            options=["Không lặp", "Hằng ngày", "Hằng tuần"],
            value=schedule_to_edit["repeat"] if is_edit else "Hằng ngày",
            on_change=on_repeat_change,
        )

        error_msg_text = ft.Text("", color=ft.Colors.RED_600, size=12, visible=False)

        def handle_save_schedule(e):
            set_field_error(name_field, None)
            set_field_error(end_date_field, None)
            set_field_error(end_time_field, None)
            error_msg_text.visible = False

            has_error = False
            if not (name_field.value or "").strip():
                set_field_error(name_field, "Vui lòng nhập tên lịch phát")
                has_error = True
            if not screen_dd.value:
                set_field_error(screen_dd, "Vui lòng chọn màn hình")
                has_error = True
            if not content_dd.value:
                set_field_error(content_dd, "Vui lòng chọn nội dung")
                has_error = True

            # Kiểm tra ngày/giờ kết thúc phải sau ngày/giờ bắt đầu
            start_dt = data.parse_vn_datetime(start_date_field.value, start_time_field.value)
            end_dt = data.parse_vn_datetime(end_date_field.value, end_time_field.value)
            start_d_only = data.parse_vn_date(start_date_field.value)
            end_d_only = data.parse_vn_date(end_date_field.value)

            if not start_dt or not end_dt or not start_d_only or not end_d_only:
                error_msg_text.value = "Định dạng ngày/giờ không hợp lệ!"
                error_msg_text.visible = True
                has_error = True
            elif end_d_only < start_d_only:
                set_field_error(end_date_field, "Ngày kết thúc phải cùng hoặc sau ngày bắt đầu")
                error_msg_text.value = "Lỗi: Ngày kết thúc không được nhỏ hơn ngày bắt đầu!"
                error_msg_text.visible = True
                has_error = True
            elif end_time_field.value <= start_time_field.value:
                set_field_error(end_time_field, "Giờ kết thúc phải sau giờ bắt đầu")
                error_msg_text.value = "Lỗi: Giờ kết thúc trong ngày phải sau giờ bắt đầu!"
                error_msg_text.visible = True
                has_error = True

            selected_wds = [wd for wd, cb in weekday_checks.items() if cb.value]
            if repeat_dd.value == "Hằng tuần" and not selected_wds:
                error_msg_text.value = "Vui lòng chọn ít nhất 1 thứ trong tuần!"
                error_msg_text.visible = True
                has_error = True

            if has_error:
                page.update()
                return

            if is_edit:
                schedule_to_edit["name"] = name_field.value.strip()
                schedule_to_edit["screen_id"] = screen_dd.value
                schedule_to_edit["content_id"] = content_dd.value
                schedule_to_edit["start_date"] = start_date_field.value
                schedule_to_edit["end_date"] = end_date_field.value
                schedule_to_edit["start_time"] = start_time_field.value
                schedule_to_edit["end_time"] = end_time_field.value
                schedule_to_edit["repeat"] = repeat_dd.value
                schedule_to_edit["weekdays"] = selected_wds if repeat_dd.value == "Hằng tuần" else []
                data.log_activity(f"Đã cập nhật lịch phát '{schedule_to_edit['name']}'.")
                msg = f"Đã cập nhật lịch phát \"{schedule_to_edit['name']}\"!"
            else:
                new_sch = {
                    "id": data.generate_next_id("SCH", data.SCHEDULES_DATA),
                    "name": name_field.value.strip(),
                    "screen_id": screen_dd.value,
                    "content_id": content_dd.value,
                    "start_date": start_date_field.value,
                    "end_date": end_date_field.value,
                    "start_time": start_time_field.value,
                    "end_time": end_time_field.value,
                    "repeat": repeat_dd.value,
                    "weekdays": selected_wds if repeat_dd.value == "Hằng tuần" else [],
                    "active": True,
                }
                data.SCHEDULES_DATA.insert(0, new_sch)
                data.log_activity(f"Đã tạo lịch phát mới '{new_sch['name']}'.")
                msg = f"Đã tạo lịch phát \"{new_sch['name']}\" thành công!"

            close_dialog(page, dialog)
            refresh_all()
            show_snack(page, msg)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Chỉnh sửa lịch phát nội dung" if is_edit else "Tạo lịch phát nội dung mới",
                weight=ft.FontWeight.BOLD,
                size=18,
            ),
            content=ft.Container(
                width=520,
                content=ft.Column(
                    tight=True,
                    spacing=12,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        name_field,
                        screen_dd,
                        content_dd,
                        ft.Row(
                            spacing=8,
                            controls=[
                                start_date_field,
                                ft.IconButton(
                                    icon=ft.Icons.CALENDAR_MONTH,
                                    icon_color=PRIMARY_COLOR,
                                    tooltip="Chọn ngày bắt đầu",
                                    on_click=lambda e: pick_date(start_date_field),
                                ),
                                end_date_field,
                                ft.IconButton(
                                    icon=ft.Icons.CALENDAR_MONTH,
                                    icon_color=PRIMARY_COLOR,
                                    tooltip="Chọn ngày kết thúc",
                                    on_click=lambda e: pick_date(end_date_field),
                                ),
                            ],
                        ),
                        ft.Row(
                            spacing=8,
                            controls=[
                                start_time_field,
                                ft.IconButton(
                                    icon=ft.Icons.ACCESS_TIME,
                                    icon_color=PRIMARY_COLOR,
                                    tooltip="Chọn giờ bắt đầu",
                                    on_click=lambda e: pick_time(start_time_field),
                                ),
                                end_time_field,
                                ft.IconButton(
                                    icon=ft.Icons.ACCESS_TIME,
                                    icon_color=PRIMARY_COLOR,
                                    tooltip="Chọn giờ kết thúc",
                                    on_click=lambda e: pick_time(end_time_field),
                                ),
                            ],
                        ),
                        repeat_dd,
                        weekday_row,
                        error_msg_text,
                    ],
                ),
            ),
            actions=[
                ft.OutlinedButton("Hủy", on_click=lambda e: close_dialog(page, dialog)),
                ft.FilledButton(
                    "Lưu lịch phát",
                    icon=ft.Icons.SAVE,
                    bgcolor=PRIMARY_COLOR,
                    color=ft.Colors.WHITE,
                    on_click=handle_save_schedule,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        open_dialog(page, dialog)

    def handle_toggle_schedule(sch: dict, is_active: bool):
        """Bật / Tắt từng lịch phát ngay lập tức."""
        sch["active"] = is_active
        state_str = "Bật" if is_active else "Tắt"
        data.log_activity(f"Đã {state_str.lower()} lịch phát '{sch['name']}'.")
        refresh_all()
        show_snack(page, f"Đã {state_str} lịch phát \"{sch['name']}\"!")

    def handle_delete_schedule(sch: dict):
        """Xác nhận và xóa lịch phát."""
        def confirm_delete():
            data.SCHEDULES_DATA.remove(sch)
            data.log_activity(f"Đã xóa lịch phát '{sch['name']}' ({sch['id']}).")
            refresh_all()
            show_snack(page, f"Đã xóa lịch phát \"{sch['name']}\"!")

        show_confirm_delete_dialog(page, sch["name"], confirm_delete)

    def refresh_schedule_list():
        """Vẽ bảng danh sách các lịch phát."""
        rows = []
        for sch in data.SCHEDULES_DATA:
            rep_text = sch["repeat"]
            if rep_text == "Hằng tuần" and sch.get("weekdays"):
                rep_text += f" ({', '.join(sch['weekdays'])})"

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(sch["name"], weight=ft.FontWeight.W_600, size=13)),
                        ft.DataCell(ft.Text(data.get_screen_name(sch["screen_id"]), size=12)),
                        ft.DataCell(ft.Text(data.get_content_name(sch["content_id"]), size=12)),
                        ft.DataCell(ft.Text(f"{sch['start_date']} → {sch['end_date']}", size=12)),
                        ft.DataCell(ft.Text(f"{sch['start_time']} - {sch['end_time']}", size=12)),
                        ft.DataCell(ft.Text(rep_text, size=12)),
                        ft.DataCell(
                            ft.Row(
                                spacing=6,
                                controls=[
                                    ft.Switch(
                                        value=sch["active"],
                                        active_color=PRIMARY_COLOR,
                                        on_change=lambda e, s=sch: handle_toggle_schedule(s, e.control.value),
                                    ),
                                    create_status_badge("Đang bật" if sch["active"] else "Đã tắt"),
                                ],
                            )
                        ),
                        ft.DataCell(
                            ft.Row(
                                spacing=4,
                                controls=[
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT_OUTLINED,
                                        icon_color=ft.Colors.AMBER_800,
                                        tooltip="Sửa lịch phát",
                                        on_click=lambda e, s=sch: open_schedule_form_dialog(s),
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE,
                                        icon_color=ft.Colors.RED_600,
                                        tooltip="Xóa lịch phát",
                                        on_click=lambda e, s=sch: handle_delete_schedule(s),
                                    ),
                                ],
                            )
                        ),
                    ]
                )
            )

        list_container.controls = [
            ft.Row(
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.DataTable(
                        column_spacing=16,
                        heading_row_height=44,
                        data_row_min_height=48,
                        columns=[
                            ft.DataColumn(ft.Text("Tên lịch phát", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Màn hình LED", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Nội dung phát", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Khoảng ngày", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Khung giờ", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Lặp lại", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Trạng thái", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Thao tác", weight=ft.FontWeight.BOLD)),
                        ],
                        rows=rows,
                    )
                ],
            )
        ]

    def open_day_schedules_dialog(day_date: date, day_schedules: list):
        """Hiển thị chi tiết các lịch phát diễn ra trong ngày được chọn trên Lịch tháng."""
        date_str = day_date.strftime("%d/%m/%Y")
        items = []
        for sch in day_schedules:
            items.append(
                ft.Container(
                    padding=10,
                    border_radius=8,
                    border=border_all(1, ft.Colors.BLUE_200),
                    bgcolor=PRIMARY_LIGHT,
                    content=ft.Column(
                        spacing=4,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(sch["name"], weight=ft.FontWeight.BOLD, size=14, color=PRIMARY_COLOR),
                                    create_status_badge("Đang bật" if sch["active"] else "Đã tắt"),
                                ],
                            ),
                            ft.Text(f"Màn hình: {data.get_screen_name(sch['screen_id'])}", size=12),
                            ft.Text(f"Nội dung: {data.get_content_name(sch['content_id'])}", size=12),
                            ft.Text(f"Khung giờ: {sch['start_time']} - {sch['end_time']} ({sch['repeat']})", size=12),
                        ],
                    ),
                )
            )

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Lịch phát ngày {date_str}", weight=ft.FontWeight.BOLD, size=18),
            content=ft.Container(
                width=460,
                content=ft.Column(
                    tight=True,
                    spacing=8,
                    scroll=ft.ScrollMode.AUTO,
                    controls=items if items else [ft.Text("Không có lịch phát nào trong ngày này.")],
                ),
            ),
            actions=[
                ft.FilledButton(
                    "Đóng",
                    bgcolor=PRIMARY_COLOR,
                    color=ft.Colors.WHITE,
                    on_click=lambda e: close_dialog(page, dialog),
                )
            ],
        )
        open_dialog(page, dialog)

    def refresh_calendar_grid():
        """Tự dựng lưới Lịch tháng bằng Row/Column và đánh dấu những ngày có lịch phát."""
        y, m = cal_state["year"], cal_state["month"]
        month_title_text.value = f"Tháng {m:02d} / {y}"

        # Tiêu đề 7 thứ trong tuần
        header_cells = []
        for wd_name in ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]:
            header_cells.append(
                ft.Container(
                    expand=True,
                    padding=8,
                    bgcolor=PRIMARY_COLOR,
                    border_radius=6,
                    alignment=ALIGN_CENTER,
                    content=ft.Text(wd_name, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=12),
                )
            )

        cal_matrix = calendar.monthcalendar(y, m)
        week_rows = [ft.Row(spacing=6, controls=header_cells)]

        for week in cal_matrix:
            day_cells = []
            for day_num in week:
                if day_num == 0:
                    day_cells.append(
                        ft.Container(
                            expand=True,
                            height=92,
                            border_radius=8,
                            bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.GREY),
                        )
                    )
                else:
                    cur_date = date(y, m, day_num)
                    matched_schedules = [
                        s for s in data.SCHEDULES_DATA if is_schedule_on_date(s, cur_date)
                    ]
                    active_count = sum(1 for s in matched_schedules if s["active"])
                    has_schedules = len(matched_schedules) > 0

                    badge_controls = []
                    for s in matched_schedules[:2]:
                        badge_controls.append(
                            ft.Container(
                                bgcolor=PRIMARY_COLOR if s["active"] else ft.Colors.GREY_500,
                                border_radius=4,
                                padding=pad_sym(horizontal=6, vertical=2),
                                content=ft.Text(
                                    f"{s['start_time']} {s['name']}",
                                    color=ft.Colors.WHITE,
                                    size=10,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            )
                        )
                    if len(matched_schedules) > 2:
                        badge_controls.append(
                            ft.Text(
                                f"+{len(matched_schedules) - 2} lịch khác",
                                size=10,
                                color=PRIMARY_COLOR,
                                weight=ft.FontWeight.W_600,
                            )
                        )

                    day_cells.append(
                        ft.Container(
                            expand=True,
                            height=92,
                            padding=6,
                            border_radius=8,
                            bgcolor=PRIMARY_LIGHT if has_schedules else None,
                            border=border_all(
                                1.5 if has_schedules else 1,
                                PRIMARY_COLOR if active_count > 0 else ft.Colors.GREY_300,
                            ),
                            on_click=lambda e, d=cur_date, ms=matched_schedules: open_day_schedules_dialog(d, ms),
                            content=ft.Column(
                                spacing=3,
                                controls=[
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[
                                            ft.Text(
                                                str(day_num),
                                                weight=ft.FontWeight.BOLD,
                                                size=13,
                                                color=PRIMARY_COLOR if has_schedules else None,
                                            ),
                                            ft.Container(
                                                visible=has_schedules,
                                                bgcolor=ft.Colors.GREEN_600 if active_count > 0 else ft.Colors.GREY_500,
                                                border_radius=10,
                                                padding=pad_sym(horizontal=6, vertical=1),
                                                content=ft.Text(
                                                    f"{len(matched_schedules)} lịch",
                                                    color=ft.Colors.WHITE,
                                                    size=9,
                                                ),
                                            ),
                                        ],
                                    ),
                                    *badge_controls,
                                ],
                            ),
                        )
                    )
            week_rows.append(ft.Row(spacing=6, controls=day_cells))

        calendar_grid_container.controls = week_rows

    def change_month(delta: int):
        """Chuyển sang Tháng trước hoặc Tháng sau trên lịch tháng."""
        m = cal_state["month"] + delta
        y = cal_state["year"]
        if m < 1:
            m = 12
            y -= 1
        elif m > 12:
            m = 1
            y += 1
        cal_state["month"] = m
        cal_state["year"] = y
        refresh_calendar_grid()
        page.update()

    def refresh_all():
        refresh_schedule_list()
        refresh_calendar_grid()
        page.update()

    # Khối giao diện Tab 1: Danh sách lịch phát
    tab_list_view = ft.Container(
        padding=14,
        content=list_container,
    )

    # Khối giao diện Tab 2: Lịch tháng tự dựng
    tab_calendar_view = ft.Container(
        padding=14,
        content=ft.Column(
            spacing=12,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    wrap=True,
                    controls=[
                        ft.Row(
                            spacing=10,
                            controls=[
                                ft.OutlinedButton(
                                    "Tháng trước",
                                    icon=ft.Icons.CHEVRON_LEFT,
                                    on_click=lambda e: change_month(-1),
                                ),
                                month_title_text,
                                ft.OutlinedButton(
                                    "Tháng sau",
                                    icon=ft.Icons.CHEVRON_RIGHT,
                                    on_click=lambda e: change_month(1),
                                ),
                            ],
                        ),
                        ft.Text(
                            "Mẹo: Nhấn vào một ô ngày trên lịch để xem chi tiết các khung giờ phát sóng.",
                            size=12,
                            color=ft.Colors.GREY_600,
                            italic=True,
                        ),
                    ],
                ),
                calendar_grid_container,
            ],
        ),
    )

    # Sử dụng ft.Tabs để chuyển đổi giữa Danh sách và Lịch tháng
    if hasattr(ft, "TabBar"):
        schedule_tabs = ft.Tabs(
            selected_index=0,
            length=2,
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.TabBar(
                        tabs=[
                            ft.Tab(label="Chế độ Danh sách", icon=ft.Icons.VIEW_LIST_ROUNDED),
                            ft.Tab(label="Chế độ Lịch tháng", icon=ft.Icons.CALENDAR_MONTH_ROUNDED),
                        ]
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[tab_list_view, tab_calendar_view],
                    ),
                ],
            ),
        )
    else:
        schedule_tabs = ft.Tabs(
            selected_index=0,
            expand=True,
            tabs=[
                ft.Tab(text="Chế độ Danh sách", icon=ft.Icons.VIEW_LIST_ROUNDED, content=tab_list_view),
                ft.Tab(text="Chế độ Lịch tháng", icon=ft.Icons.CALENDAR_MONTH_ROUNDED, content=tab_calendar_view),
            ],
        )

    refresh_schedule_list()
    refresh_calendar_grid()

    return ft.Column(
        expand=True,
        spacing=16,
        controls=[
            create_page_header(
                title="Lịch phát nội dung",
                subtitle="Lập lịch phát sóng theo khung giờ, lặp lại theo tuần và theo dõi trực quan trên lịch tháng.",
                right_controls=[
                    ft.FilledButton(
                        "Tạo lịch phát mới",
                        icon=ft.Icons.ADD_ALARM,
                        bgcolor=PRIMARY_COLOR,
                        color=ft.Colors.WHITE,
                        on_click=lambda e: open_schedule_form_dialog(None),
                    )
                ],
            ),
            ft.Card(
                expand=True,
                elevation=2,
                content=ft.Container(
                    padding=12,
                    expand=True,
                    content=schedule_tabs,
                ),
            ),
        ],
    )
