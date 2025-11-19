from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivymd.uix.toolbar import MDTopAppBar
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, RoundedRectangle
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
import webbrowser
import requests
import threading
import logging

from ...components.loading import LoadingWidget, LoadingDots, LoadingBar

API_BASE_URL = "https://backend-onlinesystem.onrender.com"

class PaymentScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loading_widget = None
        self.order_id = None

        self.toolbar = MDTopAppBar(
            title="Thanh toán",
            pos_hint={"top": 1},
            elevation=10,
            left_action_items=[["arrow-left", lambda x: self.go_back()]]
        )
        self.add_widget(self.toolbar)

    def send_payment(self, method, pkg, user, token, key_name, callback=None):
        self.show_loading(f"Đang kết nối {method.upper()}...", style="spinner")

        def payment_thread():
            try:
                headers = {"Authorization": f"Bearer {token}"}
                amount = int(pkg['price_month'])
                if method == "vnpay":
                    amount = amount * 100

                payload = {
                    "price_month": amount,
                    "name_package": f"Mua gói {pkg['name_package']}",
                    "id_package": int(pkg["id_package"])
                }

                response = requests.post(
                    f"{API_BASE_URL}/api/payment/{method}",
                    json=payload, headers=headers, timeout=10
                )
                data = response.json()
                print("Payment response:", data)

                Clock.schedule_once(lambda dt: self.hide_loading(), 0)
                result = data.get("data", {})
                pay_url = result.get(key_name)
                order_id = result.get("orderId")

                print("data: ", data)
                self.order_id = order_id

                if pay_url:
                    if callback:
                        Clock.schedule_once(lambda dt: callback(pay_url, order_id), 0)
                else:
                    Clock.schedule_once(
                        lambda dt: self.show_popup("Lỗi", data.get("message", "Thanh toán không thành công.")),
                        0
                    )
            except Exception as e:
                print("Payment error:", e)
                Clock.schedule_once(lambda dt: self.hide_loading(), 0)
                Clock.schedule_once(lambda dt: self.show_popup("Lỗi", str(e)), 0)

        threading.Thread(target=payment_thread, daemon=True).start()

    def pay_with_momo(self, pkg, user, token):
        def after_payment(pay_url, order_id):
            webbrowser.open(pay_url)
            self.order_id = order_id
            Clock.schedule_once(lambda dt: setattr(self.manager, "current", "payment_success"), 0)

        self.send_payment("momo", pkg, user, token, "payUrl", callback=after_payment)

    def pay_with_vnpay(self, pkg, user, token):
        def after_payment(pay_url, order_id):
            webbrowser.open(pay_url)
            self.order_id = order_id
            Clock.schedule_once(lambda dt: setattr(self.manager, "current", "payment_success"), 0)

        self.send_payment("vnpay", pkg, user, token, "payUrl", callback=after_payment)

    def load_user_and_package(self):
        store = JsonStore("user.json")
        user = token = pkg = None
        if store.exists("auth"):
            auth_data = store.get("auth")
            token = auth_data.get("token")
            user = auth_data.get("user")
        if store.exists("package"):
            pkg = store.get("package")
        return user, pkg, token

    def show_loading(self, message="Đang xử lý...", style="spinner"):
        if self.loading_widget: return
        if style == "dots":
            self.loading_widget = LoadingDots(message=message)
        elif style == "bar":
            self.loading_widget = LoadingBar(message=message)
        else:
            self.loading_widget = LoadingWidget(message=message, spinner_color=(0.12, 0.56, 1, 1))
        self.add_widget(self.loading_widget)

    def hide_loading(self):
        if self.loading_widget:
            self.loading_widget.stop()
            self.remove_widget(self.loading_widget)
            self.loading_widget = None

    def show_popup(self, title, message):
        popup_content = Label(text=message, color=(0, 0, 0, 1))
        from kivy.uix.popup import Popup
        Popup(title=title, content=popup_content, size_hint=(0.7, 0.4)).open()

    def on_pre_enter(self):
        try:
            for child in self.children[:]:
                if child != self.toolbar:
                    self.remove_widget(child)

            user, pkg, token = self.load_user_and_package()
            root = BoxLayout(orientation='vertical', size_hint=(1, 1), pos_hint={"top": 0.9})

            scroll = ScrollView(size_hint=(1, 1))
            content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(20), size_hint_y=None)
            content.bind(minimum_height=content.setter("height"))

            if not user:
                content.add_widget(Label(text="Vui lòng đăng nhập để tiếp tục.", font_size=18))
                scroll.add_widget(content)
                root.add_widget(scroll)
                self.add_widget(root)
                return

            if not pkg:
                content.add_widget(Label(text="Chưa chọn gói dịch vụ nào.", font_size=18))
                scroll.add_widget(content)
                root.add_widget(scroll)
                self.add_widget(root)
                return

            user_box = self.create_info_box(dp(120), bg_color=get_color_from_hex("#000000"))
            user_box.add_widget(Label(text=f"Họ và tên: {user.get('fullName', 'N/A')}", font_size=18))
            user_box.add_widget(Label(text=f"Email: {user.get('email', 'N/A')}", font_size=16))
            content.add_widget(user_box)

            pkg_box = self.create_info_box(dp(100), bg_color=get_color_from_hex("#000000"))
            pkg_box.add_widget(Label(text=f"Gói đã chọn: {pkg['name_package']}", font_size=18))
            pkg_box.add_widget(Label(text=f"Giá: {pkg['price_month']:,}đ/tháng", font_size=16))
            content.add_widget(pkg_box)

            content.add_widget(Button(
                text="Tiến hành thanh toán MoMo",
                size_hint_y=None, height=dp(55),
                background_color=get_color_from_hex("#1E90FF"),
                color=(1, 1, 1, 1),
                on_release=lambda x: self.pay_with_momo(pkg, user, token)
            ))

            content.add_widget(Button(
                text="Thanh toán bằng VNPay",
                size_hint_y=None, height=dp(55),
                background_color=get_color_from_hex("#00A8E8"),
                color=(1, 1, 1, 1),
                on_release=lambda x: self.pay_with_vnpay(pkg, user, token)
            ))

            scroll.add_widget(content)
            root.add_widget(scroll)
            self.add_widget(root)

        except Exception as e:
            logging.error(f"Error in PaymentScreen: {e}")
            self.show_popup("Lỗi", str(e))

    def create_info_box(self, height, bg_color=None):
        if not bg_color:
            bg_color = get_color_from_hex("#E8F2FF")
        box = BoxLayout(orientation='vertical', padding=dp(12), spacing=6, size_hint_y=None, height=height)
        with box.canvas.before:
            Color(*bg_color)
            box.rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[12])
        box.bind(pos=self.update_rect, size=self.update_rect)
        return box

    def update_rect(self, instance, value):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size

    def go_back(self):
        if self.manager:
            self.manager.transition.direction = "right"
            self.manager.current = "package"
