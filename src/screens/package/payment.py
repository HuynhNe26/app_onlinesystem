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
import time

# Cấu hình API
API_BASE_URL = "https://backend-onlinesystem.onrender.com"
# Cấu hình log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Imports Components (Giả định các component này tồn tại)
try:
    from ...components.loading import LoadingWidget, LoadingDots, LoadingBar
except ImportError:
    # Fallback cho trường hợp không có file components/loading
    class LoadingWidget(BoxLayout):
        def __init__(self, message="Đang xử lý...", spinner_color=(0.12, 0.56, 1, 1), **kwargs):
            super().__init__(**kwargs)
            self.add_widget(Label(text=message, color=(0, 0, 0, 1)))
        def stop(self): pass
    class LoadingDots(LoadingWidget): pass
    class LoadingBar(LoadingWidget): pass


class PaymentScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loading_widget = None
        self.order_id = None  # Lưu order_id để check trạng thái
        self.auto_check_thread = None
        self.is_checking = False

    # ========================== AUTO CHECK PAYMENT ==========================
    def stop_auto_check(self):
        """Dừng luồng kiểm tra tự động nếu nó đang chạy."""
        self.is_checking = False
        if self.auto_check_thread and self.auto_check_thread.is_alive():
            logging.info("Stopping auto check thread.")
            # Lưu ý: Không thể dừng thread Python trực tiếp, chỉ có thể dùng cờ (flag)
            # như is_checking để thread tự thoát.

    def auto_check_payment(self, token, interval=5, timeout=120):
        """Tự động kiểm tra trạng thái thanh toán MoMo"""
        if not self.order_id:
            self.show_popup("Lỗi", "Chưa có giao dịch để kiểm tra.")
            return

        # Đảm bảo chỉ có 1 thread kiểm tra chạy cùng lúc
        self.stop_auto_check()
        self.is_checking = True
        self.order_id_to_check = self.order_id # Đảm bảo order_id không thay đổi trong khi check

        def check_thread():
            start_time = time.time()
            logging.info(f"Bắt đầu kiểm tra trạng thái cho Order ID: {self.order_id_to_check}")

            try:
                while self.is_checking:
                    # 1. Kiểm tra timeout
                    if time.time() - start_time > timeout:
                        logging.warning(f"Timeout giao dịch Order ID: {self.order_id_to_check}")
                        Clock.schedule_once(lambda dt: self.show_popup(
                            "Thanh toán", "Hết thời gian chờ thanh toán (2 phút). Vui lòng thử lại hoặc liên hệ hỗ trợ."
                        ), 0)
                        break

                    # 2. Gọi API kiểm tra
                    res = requests.get(
                        f"{API_BASE_URL}/api/payment/momo/check-status/{self.order_id_to_check}",
                        headers={"Authorization": f"Bearer {token}"},
                        timeout=5
                    ).json()

                    transaction = res.get("transaction")
                    if transaction:
                        status = transaction.get("status")

                        if status == "success":
                            logging.info(f"Payment SUCCESS cho Order ID: {self.order_id_to_check}")
                            Clock.schedule_once(lambda dt: self.show_popup(
                                "Thành công", f"Giao dịch {self.order_id_to_check} hoàn tất. Gói dịch vụ của bạn đã được kích hoạt!"
                            ), 0)
                            Clock.schedule_once(lambda dt: setattr(self.manager, "current", "payment_success"), 0)
                            break
                        elif status == "failed":
                            logging.error(f"Payment FAILED cho Order ID: {self.order_id_to_check}")
                            Clock.schedule_once(lambda dt: self.show_popup(
                                "Thanh toán", "Giao dịch thất bại. Vui lòng kiểm tra lại tài khoản MoMo."
                            ), 0)
                            break
                        # Nếu status là 'Đang giao dịch'/'PENDING', tiếp tục loop

                    # 3. Chờ cho vòng lặp tiếp theo
                    time.sleep(interval)

            except requests.exceptions.Timeout:
                logging.warning("Auto check payment Timeout error.")
                # Bỏ qua và thử lại ở lần sau
                pass
            except Exception as e:
                logging.error(f"Auto check payment error: {e}")
                Clock.schedule_once(lambda dt: self.show_popup("Lỗi", f"Lỗi kiểm tra trạng thái: {str(e)}"), 0)
            finally:
                self.is_checking = False
                logging.info(f"Kết thúc kiểm tra trạng thái cho Order ID: {self.order_id_to_check}")


        self.auto_check_thread = threading.Thread(target=check_thread, daemon=True)
        self.auto_check_thread.start()

    # =========================== SEND PAYMENT REQUEST ===========================
    def send_payment(self, method, pkg, user, token, key_name):
        # Dừng kiểm tra cũ trước khi bắt đầu giao dịch mới
        self.stop_auto_check()
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
                logging.info(f"Payment response: {data}")
                Clock.schedule_once(lambda dt: self.hide_loading(), 0)

                pay_url = data.get(key_name)
                self.order_id = data.get("orderId")  # Lưu order_id

                if pay_url:
                    # Mở link MoMo và bắt đầu auto check
                    Clock.schedule_once(lambda dt: webbrowser.open(pay_url), 0)
                    self.auto_check_payment(token)
                    Clock.schedule_once(lambda dt: self.show_popup(
                        "Thanh toán",
                        "Vui lòng hoàn tất thanh toán trên MoMo. App sẽ tự động cập nhật trạng thái."
                    ), 0)
                else:
                    Clock.schedule_once(lambda dt: self.show_popup(
                        "Lỗi", data.get("message", "Thanh toán không thành công.")
                    ), 0)

            except requests.exceptions.RequestException as e:
                logging.error(f"Payment API Request error: {e}")
                Clock.schedule_once(lambda dt: self.hide_loading(), 0)
                Clock.schedule_once(lambda dt: self.show_popup("Lỗi", "Lỗi kết nối API thanh toán."), 0)
            except Exception as e:
                logging.error(f"Payment error: {e}")
                Clock.schedule_once(lambda dt: self.hide_loading(), 0)
                Clock.schedule_once(lambda dt: self.show_popup("Lỗi", str(e)), 0)

        threading.Thread(target=payment_thread, daemon=True).start()

    # =============================== UI Helpers ==================================================
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
            # LoadingDots logic
            pass
        elif style == "bar":
            # LoadingBar logic
            pass
        else:
            self.loading_widget = LoadingWidget(message=message, spinner_color=(0.12, 0.56, 1, 1))
        self.add_widget(self.loading_widget)

    def hide_loading(self):
        if self.loading_widget:
            self.loading_widget.stop()
            self.remove_widget(self.loading_widget)
            self.loading_widget = None

    def show_popup(self, title, message):
        popup_content = Label(text=message, color=(0, 0, 0, 1), halign='center', valign='middle')
        popup = Popup(title=title, content=popup_content, size_hint=(0.8, 0.4))
        popup.open()

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
            back_btn = ImageButton(source="src/assets/icon/quaylai.png", size_hint=(None, None), size=(dp(35), dp(35)))
            back_btn.bind(on_release=lambda x: setattr(self.manager, "current", "package"))
            title = Label(text="Thanh toán gói dịch vụ", font_size='20sp', bold=True,
                          color=get_color_from_hex("#000000"))
            topbar.add_widget(back_btn)
            topbar.add_widget(title)
            root.add_widget(topbar)

            scroll = ScrollView(size_hint=(1, 1))
            content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15), size_hint_y=None)
            content.bind(minimum_height=content.setter("height"))

            if not user or not token:
                content.add_widget(Label(text="Vui lòng đăng nhập để tiếp tục.", font_size='18sp', color=(0,0,0,1)))
                scroll.add_widget(content)
                root.add_widget(scroll)
                self.add_widget(root)
                return

            if not pkg:
                content.add_widget(Label(text="Chưa chọn gói dịch vụ nào.", font_size='18sp', color=(0,0,0,1)))
                scroll.add_widget(content)
                root.add_widget(scroll)
                self.add_widget(root)
                return

            # User Info
            user_box = self.create_info_box(dp(100))
            user_box.add_widget(Label(text=f"Họ và tên: {user.get('fullName', 'N/A')}", font_size='18sp', color=(0,0,0,1), halign='left'))
            user_box.add_widget(Label(text=f"Email: {user.get('email', 'N/A')}", font_size='16sp', color=(0,0,0,1), halign='left'))
            content.add_widget(user_box)

            # Package Info
            pkg_box = self.create_info_box(dp(150), bg_color=get_color_from_hex("#F4F6F8"))
            pkg_box.add_widget(Label(text="Tóm tắt đơn hàng", font_size='20sp', bold=True, color=(0,0,0,1), halign='left'))
            pkg_box.add_widget(Label(text=f"Gói đã chọn: {pkg['name_package']}", font_size='18sp', color=(0,0,0,1), halign='left'))
            pkg_box.add_widget(Label(text=f"Giá: {int(pkg['price_month']):,}đ/tháng", font_size='16sp', color=(1, 0.4, 0, 1), bold=True, halign='left'))
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
                font_size='18sp',
                on_release=lambda x: self.pay_with_momo(pkg, user, token)
            ))

            scroll.add_widget(content)
            root.add_widget(scroll)
            self.add_widget(root)

        except Exception as e:
            logging.error(f"Error in PaymentScreen on_pre_enter: {e}")
            self.show_popup("Lỗi", f"Lỗi khởi tạo màn hình: {str(e)}")

    def on_leave(self):
        """Dừng luồng kiểm tra khi người dùng rời khỏi màn hình thanh toán"""
        self.stop_auto_check()

    # Helper for UI
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
            self.selected = selected
            bg_color = (0.95, 0.95, 1, 1)
            if self.selected:
                # Màu nền nhẹ khi được chọn
                bg_color = get_color_from_hex("#E0EAF4")
            with self.canvas.before:
                Color(*bg_color)
                self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[10])
            self.bind(pos=self.update_rect, size=self.update_rect)

            icon_radio = "src/assets/icon/radio_on.png" if selected else "src/assets/icon/radio_off.png"
            self.add_widget(Image(source=icon_radio, size_hint=(None, None), size=(dp(22), dp(22))))
            self.add_widget(Label(text=text, font_size='16sp', halign="left", color=(0,0,0,1), text_size=(Window.width * 0.5, None)))
            self.add_widget(Image(source=icon, size_hint=(None, None), size=(dp(32), dp(32))))

        def update_rect(self, *args):
            self.rect.pos = self.pos
            self.rect.size = self.size

        def on_release(self):
            if self.on_select:
                self.on_select()

    # Action
    def pay_with_momo(self, pkg, user, token):
        logging.info("=== Pay with MoMo initiated ===")
        self.send_payment("momo", pkg, user, token, "payUrl")