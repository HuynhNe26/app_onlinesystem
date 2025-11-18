from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
import webbrowser
import requests
import logging
import threading
from ...components.loading import LoadingWidget, LoadingDots, LoadingBar

API_BASE_URL = "https://backend-onlinesystem.onrender.com"


class PaymentScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loading_widget = None
        self.order_id = None
        self.check_event = None  # Lưu Clock event để có thể cancel

    # ========================== AUTO CHECK PAYMENT STATUS ==========================
    def start_auto_check(self, user_id):
        """Bắt đầu tự động kiểm tra trạng thái thanh toán mỗi 5 giây"""
        if not self.order_id:
            return

        # Hủy event cũ nếu có
        if self.check_event:
            self.check_event.cancel()

        # Tạo event mới check mỗi 5 giây
        self.check_event = Clock.schedule_interval(
            lambda dt: self.check_payment_auto(user_id),
            5
        )
        print(f"Started auto-checking for order_id: {self.order_id}")

    def stop_auto_check(self):
        """Dừng việc tự động kiểm tra"""
        if self.check_event:
            self.check_event.cancel()
            self.check_event = None
            print("Stopped auto-checking")

    def check_payment_auto(self, user_id):
        """Kiểm tra trạng thái thanh toán tự động (chạy trong background)"""
        if not self.order_id:
            self.stop_auto_check()
            return

        def check_thread(order_id, uid):
            try:
                res = requests.get(
                    f"{API_BASE_URL}/api/payment/momo/check-status/{order_id}?user_id={uid}",
                    timeout=10
                ).json()

                print(f"Auto check response: {res}")
                transaction = res.get("transaction")

                # Check status (backend trả về "success", "pending", hoặc "failed")
                status = transaction.get("status", "").lower()
                if status == "success":
                    print("✅ Payment SUCCESS - Auto detected!")
                    Clock.schedule_once(lambda dt: self.stop_auto_check(), 0)
                    Clock.schedule_once(lambda dt: setattr(self.manager, "current", "payment_success"), 0)
                elif status == "failed":
                    print("❌ Payment FAILED")
                    Clock.schedule_once(lambda dt: self.stop_auto_check(), 0)
                    Clock.schedule_once(
                        lambda dt: self.show_popup("Thanh toán thất bại", "Giao dịch không thành công."), 0)
                else:
                    print(f"⏳ Payment pending... Status: {status} (checking again in 5s)")

            except Exception as e:
                print(f"Auto check error: {e}")

        threading.Thread(target=check_thread, args=(self.order_id, user_id), daemon=True).start()

    # ========================== MANUAL CHECK PAYMENT STATUS ==========================
    def check_payment_once(self, user_id):
        """Kiểm tra trạng thái thanh toán thủ công (khi user bấm nút)"""
        if not self.order_id:
            self.show_popup("Lỗi", "Chưa có giao dịch để kiểm tra.")
            return

        def check_thread(order_id, uid):
            try:
                res = requests.get(
                    f"{API_BASE_URL}/api/payment/momo/check-status/{order_id}?user_id={uid}",
                    timeout=10
                ).json()

                print(f"Manual check response: {res}")
                transaction = res.get("transaction")

                if transaction:
                    status = transaction.get("status", "").lower()
                    if status in ["success", "thành công", "giao dịch thành công"]:
                        print("✅ Payment SUCCESS")
                        Clock.schedule_once(lambda dt: self.stop_auto_check(), 0)
                        Clock.schedule_once(lambda dt: setattr(self.manager, "current", "payment_success"), 0)
                    else:
                        print(f"Payment not successful yet. Status: {status}")
                        Clock.schedule_once(lambda dt: self.show_popup(
                            "Thanh toán",
                            f"Trạng thái hiện tại: {transaction.get('status')}\n\n"
                            "Giao dịch chưa hoàn tất. Vui lòng kiểm tra lại sau."
                        ), 0)
                else:
                    Clock.schedule_once(lambda dt: self.show_popup(
                        "Lỗi", "Không tìm thấy thông tin giao dịch."
                    ), 0)
            except Exception as e:
                print(f"Check payment error: {e}")
                Clock.schedule_once(lambda dt: self.show_popup("Lỗi", str(e)), 0)

        threading.Thread(target=check_thread, args=(self.order_id, user_id), daemon=True).start()

    # =========================== SEND PAYMENT REQUEST ===========================
    def send_payment(self, method, pkg, user, token, key_name):
        self.show_loading(f"Đang kết nối {method.upper()}...", style="spinner")

        def payment_thread():
            try:
                headers = {"Authorization": f"Bearer {token}"}
                payload = {
                    "price_month": int(pkg['price_month']),
                    "name_package": f"Mua gói {pkg['name_package']}",
                    "id_package": int(pkg["id_package"])
                }

                response = requests.post(
                    f"{API_BASE_URL}/api/payment/{method}",
                    json=payload, headers=headers, timeout=10
                )

                data = response.json()
                print(f"Payment response: {data}")

                Clock.schedule_once(lambda dt: self.hide_loading(), 0)

                pay_url = data.get(key_name)
                self.order_id = data.get("orderId")

                if pay_url and self.order_id:
                    # Mở URL thanh toán
                    Clock.schedule_once(lambda dt: webbrowser.open(pay_url), 0)

                    # BẮT ĐẦU TỰ ĐỘNG KIỂM TRA
                    user_id = user.get("id_user") or user.get("id")
                    Clock.schedule_once(lambda dt: self.start_auto_check(user_id), 2)  # Đợi 2s rồi bắt đầu check

                    Clock.schedule_once(lambda dt: self.show_popup(
                        "Thanh toán",
                        "Vui lòng hoàn tất thanh toán trên MoMo.\n\n"
                        "Hệ thống sẽ tự động kiểm tra và chuyển trang khi thanh toán thành công."
                    ), 0)
                else:
                    Clock.schedule_once(
                        lambda dt: self.show_popup("Lỗi", data.get("message", "Thanh toán không thành công.")),
                        0
                    )

            except Exception as e:
                print(f"Payment error: {e}")
                Clock.schedule_once(lambda dt: self.hide_loading(), 0)
                Clock.schedule_once(lambda dt: self.show_popup("Lỗi", str(e)), 0)

        threading.Thread(target=payment_thread, daemon=True).start()

    # =============================== UI ==================================================
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
        Popup(title=title, content=popup_content, size_hint=(0.7, 0.4)).open()

    # ============================ BUILD UI =====================================
    def on_pre_enter(self):
        try:
            self.clear_widgets()
            Window.clearcolor = (1, 1, 1, 1)

            user, pkg, token = self.load_user_and_package()
            root = BoxLayout(orientation='vertical')

            # Topbar
            class ImageButton(ButtonBehavior, Image):
                pass

            topbar = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(55),
                               padding=[dp(10), dp(10)], spacing=dp(10))
            back_btn = ImageButton(source="src/assets/icon/quaylai.png", size_hint=(None, None), size=(50, 50))
            back_btn.bind(on_release=lambda x: setattr(self.manager, "current", "package"))
            title = Label(text="Thanh toán gói dịch vụ", font_size='20sp', bold=True,
                          color=get_color_from_hex("#000000"))
            topbar.add_widget(back_btn)
            topbar.add_widget(title)
            root.add_widget(topbar)

            scroll = ScrollView(size_hint=(1, 1))
            content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15), size_hint_y=None)
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

            # User Info
            user_box = self.create_info_box(dp(100))
            user_box.add_widget(
                Label(text=f"Họ và tên: {user.get('fullName', 'N/A')}", font_size=18, color=(0, 0, 0, 1)))
            user_box.add_widget(Label(text=f"Email: {user.get('email', 'N/A')}", font_size=16, color=(0, 0, 0, 1)))
            content.add_widget(user_box)

            # Package Info
            pkg_box = self.create_info_box(dp(150), bg_color=get_color_from_hex("#F4F6F8"))
            pkg_box.add_widget(Label(text=f"Gói đã chọn: {pkg['name_package']}", font_size=18, color=(0, 0, 0, 1)))
            pkg_box.add_widget(Label(text=f"Giá: {pkg['price_month']:,}đ/tháng", font_size=16, color=(0, 0, 0, 1)))
            content.add_widget(pkg_box)

            # Payment method
            self.selected_method = "momo"

            def select_momo():
                self.selected_method = "momo"; refresh_menu()

            menu_box = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
            menu_box.bind(minimum_height=menu_box.setter('height'))

            def refresh_menu():
                menu_box.clear_widgets()
                menu_box.add_widget(self.PaymentMenuItem("Thanh toán qua MoMo", "src/assets/icon/MOMO.png",
                                                         selected=(self.selected_method == "momo"),
                                                         on_select=select_momo))

            refresh_menu()
            content.add_widget(menu_box)

            # Nút thanh toán
            content.add_widget(Button(
                text="Tiến hành thanh toán",
                size_hint_y=None, height=dp(55),
                background_color=get_color_from_hex("#1E90FF"),
                color=(1, 1, 1, 1),
                on_release=lambda x: self.pay_with_momo(pkg, user, token)
            ))

            # Nút kiểm tra trạng thái thủ công
            user_id = user.get("id_user") or user.get("id")
            content.add_widget(Button(
                text="Kiểm tra trạng thái thanh toán",
                size_hint_y=None, height=dp(55),
                background_color=get_color_from_hex("#32CD32"),
                color=(1, 1, 1, 1),
                on_release=lambda x: self.check_payment_once(user_id)
            ))

            scroll.add_widget(content)
            root.add_widget(scroll)
            self.add_widget(root)

        except Exception as e:
            logging.error(f"Error in PaymentScreen: {e}")
            self.show_popup("Lỗi", str(e))

    def on_leave(self):
        """Dừng auto check khi rời khỏi màn hình"""
        self.stop_auto_check()

    # Helper
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

    class PaymentMenuItem(ButtonBehavior, BoxLayout):
        def __init__(self, text, icon, selected=False, on_select=None, **kwargs):
            super().__init__(orientation="horizontal", padding=dp(12), spacing=dp(12),
                             size_hint_y=None, height=dp(55), **kwargs)
            self.on_select = on_select
            with self.canvas.before:
                Color(*(0.95, 0.95, 1, 1) if not selected else (0.2, 0.6, 1, 0.15))
                self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[10])
            self.bind(pos=self.update_rect, size=self.update_rect)

            icon_radio = "src/assets/icon/radio_on.png" if selected else "src/assets/icon/radio_off.png"
            self.add_widget(Image(source=icon_radio, size_hint=(None, None), size=(dp(22), dp(22))))
            self.add_widget(Label(text=text, font_size=16, halign="left", color=(0, 0, 0, 1)))
            self.add_widget(Image(source=icon, size_hint=(None, None), size=(dp(32), dp(32))))

        def update_rect(self, *args):
            self.rect.pos = self.pos
            self.rect.size = self.size

        def on_release(self):
            if self.on_select:
                self.on_select()

    # Action
    def pay_with_momo(self, pkg, user, token):
        print("=== Pay with MoMo ===")
        self.send_payment("momo", pkg, user, token, "payUrl")