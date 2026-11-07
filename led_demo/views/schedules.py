import calendar
from datetime import date, datetime, time
import flet as ft
import data
import permissions
import theme
from components import (
    ALIGN_CENTER,
    border_all,
    close_dialog,
    create_action_icon,
    create_empty_state,
    create_page_header,
    create_pagination_bar,
    create_status_badge,
    create_styled_table,
    make_dropdown,
    make_form_field,
    make_primary_button,
    make_secondary_button,
    make_surface_box,
    make_text_field,
    open_dialog,
    pad_sym,
    set_field_error,
    show_confirm_delete_dialog,
    show_snack,
)

WEEKDAY_LABELS = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]


def build_view(page: ft.Page) -> ft.Column:
    """Trang Lịch phát nội dung: chế độ Danh sách có phân trang và chế độ Lịch tháng tự dựng."""
    now = datetime.now()
    cal_state = {
        "year": now.year,
        "month": now.month,
        "page": 1,
    }

    list_container = ft.Column(spacing=0)
    calendar_grid_container = ft.Column(spacing=theme.SPACE_8)
    month_title_text = ft.Text(
        "",
        size=theme.TEXT_16,
        weight=theme.WEIGHT_SEMI,
        color=theme.text_primary(),
    )

    def is_schedule_on_date(sch: dict, target_date: date) -> bool:
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
        is_edit = schedule_to_edit is not None
        required_action = "edit" if is_edit else "add"
        if not permissions.can(data.get_current_role(), "schedules", required_action):
            show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
            return

        today_str = datetime.now().strftime("%d/%m/%Y")

        name_field = make_text_field(
            value=schedule_to_edit["name"] if is_edit else "",
            hint_text="VD: Phát khung giờ cao điểm sáng",
        )

        screen_opts = [(s["id"], f"{s['code']} - {s['name']}") for s in data.SCREENS_DATA]
        screen_dd = make_dropdown(
            label="",
            options=screen_opts,
            value=schedule_to_edit["screen_id"]
            if is_edit
            else (data.SCREENS_DATA[0]["id"] if data.SCREENS_DATA else None),
        )

        content_opts = [(c["id"], f"{c['name']} ({c['format']})") for c in data.CONTENTS_DATA]
        content_dd = make_dropdown(
            label="",
            options=content_opts,
            value=schedule_to_edit["content_id"]
            if is_edit
            else (data.CONTENTS_DATA[0]["id"] if data.CONTENTS_DATA else None),
        )

        start_date_field = make_text_field(
            value=schedule_to_edit["start_date"] if is_edit else today_str,
            read_only=True,
            expand=True,
        )
        end_date_field = make_text_field(
            value=schedule_to_edit["end_date"] if is_edit else today_str,
            read_only=True,
            expand=True,
        )
        start_time_field = make_text_field(
            value=schedule_to_edit["start_time"] if is_edit else "07:30",
            read_only=True,
            expand=True,
        )
        end_time_field = make_text_field(
            value=schedule_to_edit["end_time"] if is_edit else "21:30",
            read_only=True,
            expand=True,
        )

        def pick_date(target_tf: ft.TextField):
            cur_d = data.parse_vn_date(target_tf.value or "") or date.today()
            dp = ft.DatePicker(
                first_date=datetime(2024, 1, 1),
                last_date=datetime(2030, 12, 31),
                value=datetime(cur_d.year, cur_d.month, cur_d.day),
                help_text="Chọn ngày áp dụng",
                cancel_text="Hủy",
                confirm_text="Chọn",
            )

            def on_dp_change(e):
                if dp.value:
                    target_tf.value = dp.value.strftime("%d/%m/%Y")
                    set_field_error(target_tf, None)
                    page.update()

            dp.on_change = on_dp_change
            open_dialog(page, dp)

        def pick_time(target_tf: ft.TextField):
            parts = (target_tf.value or "08:00").split(":")
            hr = int(parts[0]) if len(parts) == 2 and parts[0].isdigit() else 8
            mn = int(parts[1]) if len(parts) == 2 and parts[1].isdigit() else 0
            tp = ft.TimePicker(
                value=time(hr, mn),
                help_text="Chọn giờ áp dụng",
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

        init_weekdays = schedule_to_edit.get("weekdays", []) if is_edit else ["T2", "T4", "T6"]
        weekday_checks = {}
        for wd in WEEKDAY_LABELS:
            weekday_checks[wd] = ft.Checkbox(label=wd, value=(wd in init_weekdays))

        weekday_row = ft.Container(
            visible=(schedule_to_edit["repeat"] == "Hằng tuần") if is_edit else False,
            padding=theme.SPACE_12,
            border_radius=theme.RADIUS_INPUT,
            bgcolor=theme.surface_subtle_color(),
            border=border_all(theme.BORDER_WIDTH, theme.border_color()),
            content=ft.Column(
                spacing=theme.SPACE_4,
                controls=[
                    ft.Text("Các thứ phát trong tuần", size=theme.TEXT_12, weight=theme.WEIGHT_SEMI),
                    ft.Row(spacing=theme.SPACE_8, wrap=True, controls=list(weekday_checks.values())),
                ],
            ),
        )

        def on_repeat_change(e):
            weekday_row.visible = (repeat_dd.value == "Hằng tuần")
            page.update()

        repeat_dd = make_dropdown(
            label="",
            options=["Không lặp", "Hằng ngày", "Hằng tuần"],
            value=schedule_to_edit["repeat"] if is_edit else "Hằng ngày",
            on_change=on_repeat_change,
        )

        error_msg_text = ft.Text("", color=theme.STATUS_DANGER, size=theme.TEXT_12, visible=False)

        def handle_save_schedule(e):
            if not permissions.can(data.get_current_role(), "schedules", required_action):
                close_dialog(page, dialog)
                show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
                return

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

            start_dt = data.parse_vn_datetime(start_date_field.value, start_time_field.value)
            end_dt = data.parse_vn_datetime(end_date_field.value, end_time_field.value)
            start_d_only = data.parse_vn_date(start_date_field.value)
            end_d_only = data.parse_vn_date(end_date_field.value)

            if not start_dt or not end_dt or not start_d_only or not end_d_only:
                error_msg_text.value = "Định dạng ngày/giờ không hợp lệ."
                error_msg_text.visible = True
                has_error = True
            elif end_d_only < start_d_only:
                set_field_error(end_date_field, "Phải cùng hoặc sau ngày bắt đầu")
                error_msg_text.value = "Ngày kết thúc không được nhỏ hơn ngày bắt đầu."
                error_msg_text.visible = True
                has_error = True
            elif end_time_field.value <= start_time_field.value:
                set_field_error(end_time_field, "Phải sau giờ bắt đầu")
                error_msg_text.value = "Giờ kết thúc phải sau giờ bắt đầu."
                error_msg_text.visible = True
                has_error = True

            selected_wds = [wd for wd, cb in weekday_checks.items() if cb.value]
            if repeat_dd.value == "Hằng tuần" and not selected_wds:
                error_msg_text.value = "Vui lòng chọn ít nhất một thứ trong tuần."
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
                data.log_activity(f"Cập nhật lịch phát '{schedule_to_edit['name']}'.")
                msg = f"Đã lưu lịch phát {schedule_to_edit['id']}"
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
                data.log_activity(f"Tạo lịch phát mới '{new_sch['name']}'.")
                msg = f"Đã tạo lịch phát {new_sch['id']}"

            close_dialog(page, dialog)
            refresh_all()
            show_snack(page, msg)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Cập nhật lịch phát" if is_edit else "Tạo lịch phát mới",
                size=theme.TEXT_16,
                weight=theme.WEIGHT_SEMI,
            ),
            content=ft.Container(
                width=500,
                content=ft.Column(
                    tight=True,
                    spacing=theme.SPACE_12,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        make_form_field("Tên lịch phát *", name_field),
                        make_form_field("Màn hình áp dụng *", screen_dd),
                        make_form_field("Nội dung phát *", content_dd),
                        ft.Row(
                            spacing=theme.SPACE_12,
                            controls=[
                                ft.Container(
                                    expand=1,
                                    content=make_form_field(
                                        "Từ ngày *",
                                        ft.Row(
                                            spacing=theme.SPACE_4,
                                            controls=[
                                                start_date_field,
                                                create_action_icon(
                                                    ft.Icons.CALENDAR_TODAY_OUTLINED,
                                                    "Chọn ngày bắt đầu",
                                                    lambda e: pick_date(start_date_field),
                                                ),
                                            ],
                                        ),
                                    ),
                                ),
                                ft.Container(
                                    expand=1,
                                    content=make_form_field(
                                        "Đến ngày *",
                                        ft.Row(
                                            spacing=theme.SPACE_4,
                                            controls=[
                                                end_date_field,
                                                create_action_icon(
                                                    ft.Icons.CALENDAR_TODAY_OUTLINED,
                                                    "Chọn ngày kết thúc",
                                                    lambda e: pick_date(end_date_field),
                                                ),
                                            ],
                                        ),
                                    ),
                                ),
                            ],
                        ),
                        ft.Row(
                            spacing=theme.SPACE_12,
                            controls=[
                                ft.Container(
                                    expand=1,
                                    content=make_form_field(
                                        "Giờ bắt đầu *",
                                        ft.Row(
                                            spacing=theme.SPACE_4,
                                            controls=[
                                                start_time_field,
                                                create_action_icon(
                                                    ft.Icons.ACCESS_TIME_OUTLINED,
                                                    "Chọn giờ bắt đầu",
                                                    lambda e: pick_time(start_time_field),
                                                ),
                                            ],
                                        ),
                                    ),
                                ),
                                ft.Container(
                                    expand=1,
                                    content=make_form_field(
                                        "Giờ kết thúc *",
                                        ft.Row(
                                            spacing=theme.SPACE_4,
                                            controls=[
                                                end_time_field,
                                                create_action_icon(
                                                    ft.Icons.ACCESS_TIME_OUTLINED,
                                                    "Chọn giờ kết thúc",
                                                    lambda e: pick_time(end_time_field),
                                                ),
                                            ],
                                        ),
                                    ),
                                ),
                            ],
                        ),
                        make_form_field("Chu kỳ lặp *", repeat_dd),
                        weekday_row,
                        error_msg_text,
                    ],
                ),
            ),
            actions=[
                ft.TextButton("Hủy", on_click=lambda e: close_dialog(page, dialog)),
                make_primary_button("Lưu lịch phát", on_click=handle_save_schedule),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        open_dialog(page, dialog)

    def handle_toggle_schedule(sch: dict, is_active: bool):
        if not permissions.can(data.get_current_role(), "schedules", "toggle"):
            refresh_all()
            show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
            return

        sch["active"] = is_active
        state_str = "bật" if is_active else "tắt"
        data.log_activity(f"Đã {state_str} lịch phát '{sch['name']}' ({sch['id']}).")
        refresh_all()
        show_snack(page, f"Đã {state_str} lịch {sch['id']}")

    def handle_delete_schedule(sch: dict):
        if not permissions.can(data.get_current_role(), "schedules", "delete"):
            show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
            return

        def confirm_delete():
            if not permissions.can(data.get_current_role(), "schedules", "delete"):
                show_snack(page, "Bạn không có quyền thực hiện thao tác này", is_error=True)
                return
            data.SCHEDULES_DATA.remove(sch)
            data.log_activity(f"Xóa lịch phát '{sch['name']}' ({sch['id']}).")
            refresh_all()
            show_snack(page, f"Đã xóa lịch {sch['id']}")

        show_confirm_delete_dialog(page, sch["name"], confirm_delete)

    def change_page(new_p: int):
        cal_state["page"] = new_p
        refresh_schedule_list()
        page.update()

    def refresh_schedule_list():
        role = data.get_current_role()
        can_toggle = permissions.can(role, "schedules", "toggle")
        can_edit = permissions.can(role, "schedules", "edit")
        can_delete = permissions.can(role, "schedules", "delete")

        all_sch = data.SCHEDULES_DATA
        if not all_sch:
            list_container.controls = [create_empty_state("Chưa có lịch phát nào được cấu hình.")]
            return

        page_size = int(data.SYSTEM_SETTINGS.get("rows_per_page", "10"))
        total_pages = max(1, (len(all_sch) + page_size - 1) // page_size)
        if cal_state["page"] > total_pages:
            cal_state["page"] = total_pages
        cur_p = cal_state["page"]
        paged = all_sch[(cur_p - 1) * page_size : cur_p * page_size]

        rows = []
        for sch in paged:
            rep_text = sch["repeat"]
            if rep_text == "Hằng tuần" and sch.get("weekdays"):
                rep_text += f" ({', '.join(sch['weekdays'])})"

            toggle_controls = []
            if can_toggle:
                toggle_controls.append(
                    ft.Switch(
                        value=sch["active"],
                        active_color=theme.accent_color(),
                        on_change=lambda e, s=sch: handle_toggle_schedule(s, e.control.value),
                    )
                )
            toggle_controls.append(create_status_badge("Đang bật" if sch["active"] else "Đã tắt"))

            row_actions = []
            if can_edit:
                row_actions.append(
                    create_action_icon(
                        ft.Icons.EDIT_OUTLINED,
                        "Chỉnh sửa",
                        lambda e, s=sch: open_schedule_form_dialog(s),
                    )
                )
            if can_delete:
                row_actions.append(
                    create_action_icon(
                        ft.Icons.DELETE_OUTLINE,
                        "Xóa",
                        lambda e, s=sch: handle_delete_schedule(s),
                        is_danger=True,
                    )
                )

            cells = [
                ft.DataCell(
                    ft.Text(
                        sch["name"],
                        size=theme.TEXT_14,
                        weight=theme.WEIGHT_SEMI,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        tooltip=sch["name"],
                    )
                ),
                ft.DataCell(
                    ft.Text(
                        data.get_screen_name(sch["screen_id"]),
                        size=theme.TEXT_14,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    )
                ),
                ft.DataCell(
                    ft.Text(
                        data.get_content_name(sch["content_id"]),
                        size=theme.TEXT_14,
                        color=theme.text_secondary(),
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    )
                ),
                ft.DataCell(ft.Text(f"{sch['start_date']} – {sch['end_date']}", size=theme.TEXT_14)),
                ft.DataCell(ft.Text(f"{sch['start_time']} – {sch['end_time']}", size=theme.TEXT_14)),
                ft.DataCell(ft.Text(rep_text, size=theme.TEXT_14)),
                ft.DataCell(
                    ft.Row(
                        spacing=theme.SPACE_8,
                        controls=toggle_controls,
                    )
                ),
            ]
            if can_edit or can_delete:
                cells.append(
                    ft.DataCell(
                        ft.Row(
                            spacing=theme.SPACE_4,
                            controls=row_actions,
                        )
                    )
                )

            rows.append(ft.DataRow(cells=cells))

        cols = [
            ft.DataColumn(ft.Text("Tên lịch phát")),
            ft.DataColumn(ft.Text("Màn hình")),
            ft.DataColumn(ft.Text("Nội dung")),
            ft.DataColumn(ft.Text("Thời gian áp dụng")),
            ft.DataColumn(ft.Text("Khung giờ")),
            ft.DataColumn(ft.Text("Chu kỳ")),
            ft.DataColumn(ft.Text("Kích hoạt")),
        ]
        if can_edit or can_delete:
            cols.append(ft.DataColumn(ft.Text("Thao tác")))

        list_container.controls = [
            create_styled_table(
                columns=cols,
                rows=rows,
            ),
            create_pagination_bar(len(all_sch), cur_p, page_size, change_page),
        ]

    def open_day_schedules_dialog(day_date: date, day_schedules: list):
        date_str = day_date.strftime("%d/%m/%Y")
        items = []
        for sch in day_schedules:
            items.append(
                ft.Container(
                    padding=theme.SPACE_12,
                    border_radius=theme.RADIUS_INPUT,
                    border=border_all(theme.BORDER_WIDTH, theme.border_color()),
                    bgcolor=theme.surface_subtle_color(),
                    content=ft.Column(
                        spacing=theme.SPACE_4,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(sch["name"], weight=theme.WEIGHT_SEMI, size=theme.TEXT_14),
                                    create_status_badge("Đang bật" if sch["active"] else "Đã tắt"),
                                ],
                            ),
                            ft.Text(f"Màn hình: {data.get_screen_name(sch['screen_id'])}", size=theme.TEXT_12, color=theme.text_secondary()),
                            ft.Text(f"Nội dung: {data.get_content_name(sch['content_id'])}", size=theme.TEXT_12, color=theme.text_secondary()),
                            ft.Text(f"Giờ phát: {sch['start_time']} – {sch['end_time']} ({sch['repeat']})", size=theme.TEXT_12, color=theme.text_secondary()),
                        ],
                    ),
                )
            )

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Lịch phát ngày {date_str}", size=theme.TEXT_16, weight=theme.WEIGHT_SEMI),
            content=ft.Container(
                width=460,
                content=ft.Column(
                    tight=True,
                    spacing=theme.SPACE_8,
                    scroll=ft.ScrollMode.AUTO,
                    controls=items if items else [ft.Text("Không có lịch phát sóng trong ngày này.", size=theme.TEXT_14)],
                ),
            ),
            actions=[
                ft.TextButton("Đóng", on_click=lambda e: close_dialog(page, dialog))
            ],
        )
        open_dialog(page, dialog)

    def refresh_calendar_grid():
        y, m = cal_state["year"], cal_state["month"]
        month_title_text.value = f"Tháng {m:02d}/{y}"

        header_cells = []
        for wd_name in ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "CN"]:
            header_cells.append(
                ft.Container(
                    expand=True,
                    padding=theme.SPACE_8,
                    bgcolor=theme.surface_subtle_color(),
                    border=border_all(theme.BORDER_WIDTH, theme.border_color()),
                    border_radius=theme.RADIUS_INPUT,
                    alignment=ALIGN_CENTER,
                    content=ft.Text(wd_name, color=theme.text_secondary(), weight=theme.WEIGHT_SEMI, size=theme.TEXT_12),
                )
            )

        cal_matrix = calendar.monthcalendar(y, m)
        week_rows = [ft.Row(spacing=theme.SPACE_8, controls=header_cells)]

        for week in cal_matrix:
            day_cells = []
            for day_num in week:
                if day_num == 0:
                    day_cells.append(
                        ft.Container(
                            expand=True,
                            height=88,
                            border_radius=theme.RADIUS_INPUT,
                            bgcolor=theme.surface_subtle_color(),
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
                            ft.Row(
                                spacing=theme.SPACE_4,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Container(
                                        width=theme.SPACE_4,
                                        height=theme.SPACE_12,
                                        bgcolor=theme.STATUS_ONLINE if s["active"] else theme.STATUS_OFFLINE,
                                    ),
                                    ft.Text(
                                        f"{s['start_time']} {s['name']}",
                                        color=theme.text_primary(),
                                        size=theme.TEXT_12,
                                        max_lines=1,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                        expand=True,
                                    ),
                                ],
                            )
                        )
                    if len(matched_schedules) > 2:
                        badge_controls.append(
                            ft.Text(
                                f"+{len(matched_schedules) - 2} lịch khác",
                                size=theme.TEXT_12,
                                color=theme.accent_color(),
                            )
                        )

                    day_cells.append(
                        ft.Container(
                            expand=True,
                            height=88,
                            padding=theme.SPACE_8,
                            border_radius=theme.RADIUS_INPUT,
                            bgcolor=theme.accent_subtle() if active_count > 0 else theme.surface_color(),
                            border=border_all(
                                theme.BORDER_WIDTH,
                                theme.accent_color() if active_count > 0 else theme.border_color(),
                            ),
                            on_click=lambda e, d=cur_date, ms=matched_schedules: open_day_schedules_dialog(d, ms),
                            content=ft.Column(
                                spacing=theme.SPACE_4,
                                controls=[
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[
                                            ft.Text(
                                                str(day_num),
                                                weight=theme.WEIGHT_SEMI,
                                                size=theme.TEXT_14,
                                                color=theme.text_primary(),
                                            ),
                                            ft.Text(
                                                f"{len(matched_schedules)} lịch" if has_schedules else "",
                                                size=theme.TEXT_12,
                                                color=theme.text_secondary(),
                                            ),
                                        ],
                                    ),
                                    *badge_controls,
                                ],
                            ),
                        )
                    )
            week_rows.append(ft.Row(spacing=theme.SPACE_8, controls=day_cells))

        calendar_grid_container.controls = week_rows

    def change_month(delta: int):
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

    tab_list_view = ft.Container(
        padding=pad_sym(vertical=theme.SPACE_12),
        content=list_container,
    )

    tab_calendar_view = ft.Container(
        padding=pad_sym(vertical=theme.SPACE_12),
        content=ft.Column(
            spacing=theme.SPACE_12,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    wrap=True,
                    controls=[
                        ft.Row(
                            spacing=theme.SPACE_8,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                make_secondary_button(
                                    "Tháng trước",
                                    icon_name=ft.Icons.CHEVRON_LEFT_OUTLINED,
                                    on_click=lambda e: change_month(-1),
                                ),
                                ft.Container(
                                    padding=pad_sym(horizontal=theme.SPACE_12),
                                    content=month_title_text,
                                ),
                                make_secondary_button(
                                    "Tháng sau",
                                    icon_name=ft.Icons.CHEVRON_RIGHT_OUTLINED,
                                    on_click=lambda e: change_month(1),
                                ),
                            ],
                        ),
                        ft.Text(
                            "Nhấn vào từng ngày để xem chi tiết khung giờ phát.",
                            size=theme.TEXT_12,
                            color=theme.text_secondary(),
                        ),
                    ],
                ),
                calendar_grid_container,
            ],
        ),
    )

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
                            ft.Tab(label="Danh sách lịch phát", icon=ft.Icons.VIEW_LIST_OUTLINED),
                            ft.Tab(label="Lịch tháng", icon=ft.Icons.CALENDAR_TODAY_OUTLINED),
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
                ft.Tab(text="Danh sách lịch phát", icon=ft.Icons.VIEW_LIST_OUTLINED, content=tab_list_view),
                ft.Tab(text="Lịch tháng", icon=ft.Icons.CALENDAR_TODAY_OUTLINED, content=tab_calendar_view),
            ],
        )

    role = data.get_current_role()
    header_actions = []
    if permissions.can(role, "schedules", "add"):
        header_actions.append(
            make_primary_button(
                "Tạo lịch phát",
                icon_name=ft.Icons.ADD_OUTLINED,
                on_click=lambda e: open_schedule_form_dialog(None),
            )
        )

    refresh_schedule_list()
    refresh_calendar_grid()

    return ft.Column(
        expand=True,
        spacing=theme.SPACE_16,
        controls=[
            create_page_header(
                title="Lịch phát nội dung",
                subtitle="Thiết lập khung giờ phát định kỳ hoặc theo ngày cho từng điểm màn hình.",
                right_controls=header_actions,
            ),
            make_surface_box(
                expand=True,
                padding=theme.SPACE_16,
                content=schedule_tabs,
            ),
        ],
    )
