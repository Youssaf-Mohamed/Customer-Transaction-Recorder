import flet as ft
from datetime import datetime
from db.database import (
    get_customers, add_customer, update_customer_info, get_total_balance,
    get_customer_balance, get_transactions, add_transaction, get_customer
)
from ui.config import COLORS


def main_view(page: ft.Page):
    page.title = "نظام إدارة الحسابات"
    page.window_width = 800
    page.window_height = 1000
    page.bgcolor = COLORS["background"]
    page.fonts = {
        "Cairo": "https://github.com/google/fonts/raw/main/ofl/cairo/Cairo%5Bslnt%2Cwght%5D.ttf"
    }
    page.theme = ft.Theme(font_family="Cairo")

    # interface auxiliary functions
    def show_error(message):
        page.snack_bar = ft.SnackBar(
            ft.Text(message, color="white"), bgcolor=COLORS["danger"])
        page.snack_bar.open = True
        page.update()

    def show_success(message):
        page.snack_bar = ft.SnackBar(
            ft.Text(message, color="white"), bgcolor=COLORS["success"])
        page.snack_bar.open = True
        page.update()

    def close_dialog(dlg):
        dlg.open = False
        page.update()

    def refresh_customers_view():
        page.clean()
        home_view()

    # Customer card
    def customer_card(customer):
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.ListTile(
                        leading=ft.Icon("person", color=COLORS["primary"]),
                        title=ft.Text(
                            customer[1], weight="bold", color=COLORS["text"]),
                        subtitle=ft.Text(
                            f"الهاتف: {customer[2]}", color=COLORS["text"]),
                    ),
                    ft.Row([
                        ft.Text(
                            f"الرصيد: {customer[3]:.2f} SAR",
                            color=COLORS["success"] if customer[3] >= 0 else COLORS["danger"],
                            weight="bold"
                        ),
                        ft.Row([
                            ft.IconButton(
                                icon="edit",
                                tooltip="تعديل العميل",
                                on_click=lambda e, cid=customer[0]: edit_customer_dialog(
                                    cid),
                                icon_color=COLORS["secondary"]
                            ),
                            ft.IconButton(
                                icon="arrow_forward",
                                tooltip="عرض التفاصيل",
                                on_click=lambda e, cid=customer[0]: show_customer_details(
                                    cid),
                                icon_color=COLORS["primary"]
                            ),
                        ])
                    ], alignment="spaceBetween")
                ]),
                padding=15,
                border_radius=10,
                bgcolor="white",
            ),
            elevation=5,
            shadow_color="grey300"
        )

    # Home page
    def home_view(e=None):
        page.clean()
        page.add(
            ft.AppBar(
                title=ft.Text("العملاء", color="white"),
                bgcolor=COLORS["primary"],
                actions=[
                    ft.TextButton(
                        "إضافة عميل",
                        on_click=lambda e: add_customer_dialog(),
                        style=ft.ButtonStyle(color="white")
                    )
                ]
            ),
            ft.Container(
                content=ft.Column(
                    controls=[customer_card(c) for c in get_customers()],
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO
                ),
                padding=20,
                expand=True
            ),
            ft.Divider(),
            ft.Container(
                content=ft.Row([
                    ft.Text(
                        f"إجمالي الأرصدة: {get_total_balance():.2f} SAR",
                        size=18,
                        weight="bold",
                        color=COLORS["success"]
                    )
                ], alignment="center"),
                padding=10
            )
        )
        page.update()

    # add new
    def add_customer_dialog():
        name_field = ft.TextField(
            label="الاسم", border_color=COLORS["primary"], autofocus=True)
        phone_field = ft.TextField(
            label="الهاتف", border_color=COLORS["primary"], keyboard_type="number")

        def save_customer(e):
            if not name_field.value.strip():
                show_error("الرجاء إدخال اسم العميل")
                return
            if not phone_field.value.strip().isdigit():
                show_error("رقم الهاتف يجب أن يكون أرقام فقط")
                return
            try:
                add_customer(name_field.value, phone_field.value)
                close_dialog(dlg)
                home_view()
                show_success("تم إضافة العميل بنجاح!")
            except Exception as ex:
                show_error(f"خطأ: {str(ex)}")
            page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("إضافة عميل جديد"),
            content=ft.Column([name_field, phone_field], tight=True),
            actions=[
                ft.TextButton("إلغاء", on_click=lambda e: close_dialog(dlg)),
                ft.TextButton("حفظ", on_click=save_customer)
            ]
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    # Alter new customer
    def edit_customer_dialog(customer_id):
        customer = next((c for c in get_customers()
                        if c[0] == customer_id), None)
        if not customer:
            show_error("العميل غير موجود!")
            return

        name_field = ft.TextField(
            label="الاسم", border_color=COLORS["primary"], value=customer[1])
        phone_field = ft.TextField(
            label="الهاتف", border_color=COLORS["primary"], keyboard_type="number", value=customer[2])

        def update_customer(e):
            if not name_field.value.strip():
                show_error("الرجاء إدخال اسم العميل")
                return
            if not phone_field.value.strip().isdigit():
                show_error("رقم الهاتف يجب أن يكون أرقام فقط")
                return
            try:
                update_customer_info(
                    customer_id, name_field.value, phone_field.value)
                close_dialog(dlg)
                home_view()
                show_success("تم تعديل بيانات العميل بنجاح!")
            except Exception as ex:
                show_error(f"خطأ: {str(ex)}")
            page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("تعديل بيانات العميل"),
            content=ft.Column([name_field, phone_field], tight=True),
            actions=[
                ft.TextButton("إلغاء", on_click=lambda e: close_dialog(dlg)),
                ft.TextButton("حفظ التعديلات", on_click=update_customer)
            ]
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    # Show customer deteails
    def show_customer_details(customer_id):
        customer = next(c for c in get_customers() if c[0] == customer_id)
        balance_display = ft.Text(
            f"{customer[3]:.2f} SAR",
            size=40,
            weight="bold",
            color=COLORS["success"] if customer[3] >= 0 else COLORS["danger"]
        )
        transactions_list = ft.ListView(
            expand=True, height=300, spacing=10, padding=10)

        def load_transactions():
            transactions_list.controls.clear()
            for t in get_transactions(customer_id):
                amount = float(t[3])
                transactions_list.controls.append(
                    ft.Container(
                        ft.ListTile(
                            leading=ft.Icon(
                                "arrow_upward" if t[4] == "زيادة" else "arrow_downward",
                                color=COLORS["success"] if t[4] == "زيادة" else COLORS["danger"]
                            ),
                            title=ft.Text(f"{amount:.2f} SAR",
                                          color=COLORS["text"]),
                            subtitle=ft.Text(
                                f"{t[5]} | {datetime.fromisoformat(
                                    t[2]).strftime('%Y-%m-%d %H:%M')}",
                                color=COLORS["text"]
                            ),
                            trailing=ft.Text(t[4], color=COLORS["text"])
                        ),
                        bgcolor="white",
                        border_radius=5,
                        padding=5
                    )
                )
            page.update()

        def add_transaction_dialog(e=None):
            amount_field = ft.TextField(
                label="المبلغ", border_color=COLORS["primary"], keyboard_type="number")
            trans_type_dropdown = ft.Dropdown(
                options=[
                    ft.dropdown.Option("زيادة"),
                    ft.dropdown.Option("خصم")
                ],
                value="زيادة",
                border_color=COLORS["primary"]
            )
            notes_field = ft.TextField(
                label="الملاحظات", multiline=True, border_color=COLORS["primary"])

            def save_transaction(e):
                if not amount_field.value.strip() or not amount_field.value.replace('.', '', 1).isdigit():
                    show_error("الرجاء إدخال مبلغ صحيح")
                    return
                try:
                    add_transaction(customer_id, float(
                        amount_field.value), trans_type_dropdown.value, notes_field.value)
                    load_transactions()
                    balance_display.value = f"{
                        get_customer_balance(customer_id):.2f} SAR"
                    show_success("تمت العملية بنجاح!")
                    close_dialog(dlg)
                except Exception as ex:
                    show_error(f"خطأ: {str(ex)}")
                page.update()

            dlg = ft.AlertDialog(
                title=ft.Text("إضافة عملية جديدة"),
                content=ft.Column(
                    [amount_field, trans_type_dropdown, notes_field], spacing=10, tight=True),
                actions=[
                    ft.TextButton(
                        "إلغاء", on_click=lambda e: close_dialog(dlg)),
                    ft.TextButton("حفظ", on_click=save_transaction)
                ]
            )
            page.dialog = dlg
            dlg.open = True
            page.update()

        page.clean()
        page.add(
            ft.AppBar(
                title=ft.Text(customer[1], color="white"),
                bgcolor=COLORS["primary"],
                leading=ft.IconButton(
                    "arrow_back",
                    on_click=lambda e: home_view(),
                    icon_color="white"
                )
            ),
            ft.Container(
                content=ft.Column([
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("الرصيد الحالي", size=18,
                                        color=COLORS["text"]),
                                balance_display
                            ], horizontal_alignment="center"),
                            padding=20
                        ),
                        color="white"
                    ),
                    ft.Divider(),
                    ft.Row([
                        ft.Text("سجل العمليات", size=18, color=COLORS["text"]),
                        ft.IconButton(
                            "add_circle",
                            tooltip="إضافة عملية جديدة",
                            on_click=add_transaction_dialog,
                            icon_color=COLORS["primary"]
                        )
                    ], alignment="spaceBetween"),
                    transactions_list
                ], spacing=20, expand=True),
                padding=20,
                expand=True
            )
        )
        load_transactions()
        page.update()

    home_view()
