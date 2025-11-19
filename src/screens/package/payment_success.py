from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
import requests
import threading

API_BASE_URL = "https://backend-onlinesystem.onrender.com"

class PaymentSuccessScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loading_widget = None
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))

        layout.add_widget(Label(
            text="🎉 Thanh toán hoàn tất!",
            font_size='24sp',
            bold=True,
            color=get_color_from_hex("#1E90FF"),
            size_hint_y=None,
            height=dp(60)
        ))

        layout.add_widget(Label(
            text="Đang xác nhận giao dịch...",
            font_size='18sp',
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=dp(40)
        ))

        self.add_widget(layout)

    def on_enter(self):
        user, pkg, token = self.load_user_and_package()
        if not token or not pkg:
            return

        store = JsonStore("user.json")
        if store.exists("last_order"):
            order_id = store.get("last_order")["order_id"]
        else:
            order_id = None

        if not order_id:
            return

        self.check_payment_status(order_id, token)

    def check_payment_status(self, order_id, token):
        self.show_loading("Đang xác nhận giao dịch...")

        def check_thread():
            try:
                res = requests.get(
                    f"{API_BASE_URL}/api/payment/check-status/{order_id}",
                    headers={"Authorization": f"Bearer {token}"}
                ).json()
                transaction = res.get("transaction")
                Clock.schedule_once(lambda dt: self.hide_loading(), 0)

                if transaction and transaction.get("status") == "success":
                    print("Payment SUCCESS")
                else:
                    print("Payment chưa thành công, thử lại sau 5 giây...")
                    Clock.schedule_once(lambda dt: self.check_payment_status(order_id, token), 5)

            except Exception as e:
                print("Check payment error:", e)
                Clock.schedule_once(lambda dt: self.hide_loading(), 0)

        threading.Thread(target=check_thread, daemon=True).start()

    def show_loading(self, message="Đang xử lý...", style="spinner"):
        if self.loading_widget: return
        from ...components.loading import LoadingWidget
        self.loading_widget = LoadingWidget(message=message)
        self.add_widget(self.loading_widget)

    def hide_loading(self):
        if self.loading_widget:
            self.loading_widget.stop()
            self.remove_widget(self.loading_widget)
            self.loading_widget = None

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