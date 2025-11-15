from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.storage.jsonstore import JsonStore
import webbrowser
import requests
import logging

API_BASE_URL = "https://backend-onlinesystem.onrender.com"

class PaymentScreen(Screen):

    # ---------------------- LOAD DATA --------------------------
    def load_user_and_package(self):
        store = JsonStore("user.json")

        user = store.get("user") if store.exists("user") else None
        pkg = store.get("package") if store.exists("package") else None
        token = store.get("token")["access_token"] if store.exists("token") else None

        return user, pkg, token

    # ---------------------- MAIN UI ---------------------------
    def on_pre_enter(self):
        try:
            self.clear_widgets()
            Window.clearcolor = (1, 1, 1, 1)

            user, pkg, token = self.load_user_and_package()

            root = BoxLayout(orientation='vertical')

            # ---------- TOP BAR ----------
            topbar = BoxLayout(
                orientation='horizontal',
                size_hint_y=None, height=dp(55),
                padding=[dp(10), dp(10)], spacing=dp(10)
            )

            class ImageButton(ButtonBehavior, Image): pass

            back_btn = ImageButton(
                source="src/front_end/users/assets/icon/quaylai.png",
                size_hint=(None, None), size=(50, 50)
            )
            back_btn.bind(on_release=lambda x: setattr(self.manager, "current", "package"))

            title = Label(
                text="Thanh toán gói dịch vụ", font_size='20sp',
                bold=True, color=get_color_from_hex("#1E90FF")
            )

            topbar.add_widget(back_btn)
            topbar.add_widget(title)
            root.add_widget(topbar)

            # ---------- CONTENT ----------
            scroll = ScrollView(size_hint=(1, 1))
            content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15), size_hint_y=None)
            content.bind(minimum_height=content.setter("height"))

            # ---- Check user login ----
            if not user:
                content.add_widget(Label(text="Vui lòng đăng nhập để tiếp tục.", font_size=18))
                scroll.add_widget(content)
                root.add_widget(scroll)
                self.add_widget(root)
                return

            # ---- Check package ----
            if not pkg:
                content.add_widget(Label(text="Chưa chọn gói dịch vụ nào.", font_size=18))
                scroll.add_widget(content)
                root.add_widget(scroll)
                self.add_widget(root)
                return

            # ---------- USER INFO ----------
            user_box = self.create_info_box(dp(100))
            user_box.add_widget(Label(text=f"Họ và tên: {user.get('fullName')}", font_size=18))
            user_box.add_widget(Label(text=f"Email: {user.get('email')}", font_size=16))
            content.add_widget(user_box)

            # ---------- PACKAGE INFO ----------
            pkg_box = self.create_info_box(dp(150), bg_color=get_color_from_hex("#F4F6F8"))
            pkg_box.add_widget(Label(text=f"Gói đã chọn: {pkg['name_package']}", font_size=18, bold=True))
            pkg_box.add_widget(Label(text=f"Giá: {pkg['price_month']:,}đ/tháng", font_size=16))
            content.add_widget(pkg_box)

            content.add_widget(Widget(size_hint_y=None, height=dp(10)))

            # ---------- PAYMENT METHOD ----------
            self.selected_method = "momo"

            def select_momo():
                self.selected_method = "momo"
                refresh_menu()

            def select_vnpay():
                self.selected_method = "vnpay"
                refresh_menu()

            menu_box = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
            menu_box.bind(minimum_height=menu_box.setter('height'))

            def refresh_menu():
                menu_box.clear_widgets()
                menu_box.add_widget(self.PaymentMenuItem("Thanh toán qua MoMo",
                    "src/front_end/users/assets/icon/MOMO.png",
                    selected=(self.selected_method == "momo"),
                    on_select=select_momo
                ))
                menu_box.add_widget(self.PaymentMenuItem("Thanh toán qua VNPay",
                    "src/front_end/users/assets/icon/VNPAY.png",
                    selected=(self.selected_method == "vnpay"),
                    on_select=select_vnpay
                ))

            refresh_menu()
            content.add_widget(menu_box)

            # ---------- BUTTON PAY ----------
            content.add_widget(Button(
                text="Tiến hành thanh toán",
                size_hint_y=None, height=dp(55),
                background_color=get_color_from_hex("#1E90FF"),
                color=(1, 1, 1, 1),
                on_release=lambda x: (
                    self.pay_with_momo(pkg, user, token)
                    if self.selected_method == "momo"
                    else self.pay_with_vnpay(pkg, user, token)
                )
            ))

            scroll.add_widget(content)
            root.add_widget(scroll)
            self.add_widget(root)

        except Exception as e:
            logging.error(e)
            self.show_popup("Lỗi", str(e))

    # ---------------------- BOX UI STYLE -------------------------
    def create_info_box(self, height, bg_color=(0.95, 0.95, 1, 1)):
        box = BoxLayout(orientation='vertical', padding=dp(10), spacing=5, size_hint_y=None, height=height)
        with box.canvas.before:
            Color(*bg_color)
            box.rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[10])
        box.bind(pos=self.update_rect, size=self.update_rect)
        return box

    def update_rect(self, instance, value):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size

    # ---------------------- MENU ITEM --------------------------
    class PaymentMenuItem(ButtonBehavior, BoxLayout):
        def __init__(self, text, icon, selected=False, on_select=None, **kwargs):
            super().__init__(orientation="horizontal", padding=dp(12), spacing=dp(12),
                             size_hint_y=None, height=dp(55), **kwargs)

            self.on_select = on_select

            with self.canvas.before:
                Color(*(0.95, 0.95, 1, 1) if not selected else (0.2, 0.6, 1, 0.15))
                self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[10])

            self.bind(pos=self.update_rect, size=self.update_rect)

            radio_icon = "src/front_end/users/assets/icon/radio_on.png" if selected else "src/front_end/users/assets/icon/radio_off.png"
            self.add_widget(Image(source=radio_icon, size_hint=(None, None), size=(dp(22), dp(22))))
            self.add_widget(Label(text=text, font_size=16, halign="left", valign="middle"))
            self.add_widget(Image(source=icon, size_hint=(None, None), size=(dp(32), dp(32))))

        def update_rect(self, *args):
            self.rect.pos = self.pos
            self.rect.size = self.size

        def on_release(self):
            if self.on_select:
                self.on_select()

    # ---------------------- PAYMENT --------------------------
    def send_payment(self, method, pkg, user, token, key_name):
        try:
            headers = {"Authorization": f"Bearer {token}"}

            payload = {
                "price_month": int(pkg['price_month']),
                "name_package": f"Mua gói {pkg['name_package']}",
                "id_package": int(pkg["id_package"])
            }

            response = requests.post(
                f"{API_BASE_URL}/api/payment/{method}/{method}",
                json=payload, headers=headers, timeout=10
            )

            data = response.json()

            if data.get(key_name):
                webbrowser.open(data[key_name])
            else:
                self.show_popup("Lỗi", data.get("message", "Không có URL thanh toán."))

        except Exception as e:
            self.show_popup("Lỗi", str(e))

    def pay_with_momo(self, pkg, user, token):
        self.send_payment("momo", pkg, user, token, "payUrl")

    def pay_with_vnpay(self, pkg, user, token):
        self.send_payment("vnpay", pkg, user, token, "payUrl")

    # ---------------------- POPUP --------------------------
    def show_popup(self, title, message):
        Popup(title=title, content=Label(text=message),
              size_hint=(0.7, 0.4)).open()
