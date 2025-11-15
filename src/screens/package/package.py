from kivy.storage.jsonstore import JsonStore
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from kivy.clock import Clock

import logging
import requests
import threading

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class PackageScreen(Screen):

    def __init__(self, **kwargs):
        super(PackageScreen, self).__init__(**kwargs)

        Window.clearcolor = (1, 1, 1, 1)
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        top_bar = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=10)

        class ImageButton(ButtonBehavior, Image):
            pass

        back_btn = ImageButton(
            source="src/front_end/users/assets/icon/quaylai.png",
            size_hint=(None, None),
            size=(80, 80),
            allow_stretch=True,
            keep_ratio=True
        )
        back_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'home'))

        title = Label(
            text="[b]CÁC GÓI DỊCH VỤ[/b]",
            markup=True,
            font_size=26,
            color=(0, 0, 0, 1)
        )
        title.bind(size=title.setter('text_size'))

        top_bar.add_widget(back_btn)
        top_bar.add_widget(title)
        main_layout.add_widget(top_bar)

        scroll = ScrollView(size_hint=(1, 0.9))
        self.grid = GridLayout(cols=1, spacing=12, padding=[10, 10, 10, 10], size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        scroll.add_widget(self.grid)

        main_layout.add_widget(scroll)
        self.add_widget(main_layout)

    def on_pre_enter(self):
        self.grid.clear_widgets()

        loading_label = Label(
            text="Đang tải dữ liệu...",
            font_size=18,
            color=(0, 0, 0, 1)
        )
        self.grid.add_widget(loading_label)

        threading.Thread(target=self.load_packages, daemon=True).start()

    def load_packages(self):
        try:
            logging.info("Loading packages from API...")

            url = "https://backend-onlinesystem.onrender.com/api/packages"

            response = requests.get(
                url,
                timeout=15,
                headers={
                    'User-Agent': 'Mozilla/5.0',
                    'Accept': 'application/json'
                }
            )

            logging.info(f"Status: {response.status_code}")
            logging.info(f"Response content: {response.text[:500]}")

            if response.status_code != 200:
                raise Exception(f"API trả về lỗi {response.status_code}")

            json_data = response.json()
            logging.info(f"JSON data: {json_data}")

            if "data" not in json_data:
                raise Exception(f"Response không đúng định dạng: {json_data}")

            packages = json_data["data"]

            if not packages:
                raise Exception("Không có gói dịch vụ nào")

            Clock.schedule_once(lambda dt: self.display_packages(packages), 0)

        except requests.exceptions.Timeout:
            error_msg = "Hết thời gian kết nối. Vui lòng thử lại."
            logging.error(error_msg)
            Clock.schedule_once(lambda dt: self.show_error(error_msg), 0)

        except requests.exceptions.ConnectionError:
            error_msg = "Không thể kết nối đến server. Kiểm tra mạng."
            logging.error(error_msg)
            Clock.schedule_once(lambda dt: self.show_error(error_msg), 0)

        except Exception as e:
            error_msg = f"Lỗi: {str(e)}"
            logging.error(error_msg, exc_info=True)
            Clock.schedule_once(lambda dt: self.show_error(error_msg), 0)

    def display_packages(self, packages):
        self.grid.clear_widgets()

        for idx, pkg in enumerate(packages):
            self.grid.add_widget(self.create_package_card(pkg, idx))

        logging.info(f"Displayed {len(packages)} packages successfully!")

    def show_error(self, message):
        self.grid.clear_widgets()
        error_label = Label(
            text=message,
            font_size=16,
            color=(0.8, 0, 0, 1)
        )
        self.grid.add_widget(error_label)

        Popup(
            title="Lỗi",
            content=Label(text=message),
            size_hint=(0.7, 0.4),
        ).open()

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def set_package(self, pkg):
        try:
            store = JsonStore("user.json")
            store.put("package",
                      id_package=pkg["id_package"],
                      name_package=pkg["name_package"],
                      price_month=pkg["price_month"],
                      description_package=pkg.get("description_package", ""))

            logging.info(f"Saved package: {pkg}")

        except Exception as e:
            logging.error("Error saving package.", exc_info=True)
            raise

    def create_package_card(self, pkg, index):
        colors = [
            (0.90, 0.95, 1, 1),
            (1, 0.95, 0.90, 1),
            (0.95, 1, 0.92, 1)
        ]
        bg = colors[index % len(colors)]

        card = BoxLayout(
            orientation='vertical',
            padding=14,
            spacing=8,
            size_hint_y=None,
            height=260
        )

        with card.canvas.before:
            Color(*bg)
            card.rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[12])
        card.bind(pos=self.update_rect, size=self.update_rect)

        title_label = Label(
            text=f"[b]{pkg['name_package']}[/b]",
            markup=True,
            font_size=20,
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=40
        )
        title_label.bind(size=title_label.setter('text_size'))
        card.add_widget(title_label)

        if pkg["price_month"] == 0:
            price_label = Label(
                text="Miễn phí",
                font_size=16,
                color=(0.2, 0.6, 0.2, 1),
                size_hint_y=None,
                height=30
            )
        else:
            price_label = Label(
                text=f"{pkg['price_month']:,}đ / tháng",
                font_size=16,
                color=(0.2, 0.5, 0.8, 1),
                size_hint_y=None,
                height=30
            )
        card.add_widget(price_label)

        desc_label = Label(
            text=pkg.get("description_package", ""),
            font_size=14,
            color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None,
            height=100
        )
        desc_label.bind(size=desc_label.setter("text_size"))
        card.add_widget(desc_label)

        btn_layout = BoxLayout(size_hint_y=None, height=45, spacing=10)

        btn_detail = Button(
            text='Chi tiết',
            background_color=(0.2, 0.7, 0.5, 1),
            color=(1, 1, 1, 1)
        )
        btn_detail.bind(on_release=lambda x: self.show_detail(pkg))
        btn_layout.add_widget(btn_detail)

        # Register button
        if pkg['price_month'] > 0:
            btn_register = Button(
                text='Đăng ký',
                background_color=(0.7, 0.2, 0.2, 1),
                color=(1, 1, 1, 1)
            )
            btn_register.bind(on_release=lambda x: self.go_to_payment(pkg))
            btn_layout.add_widget(btn_register)

        card.add_widget(btn_layout)

        return card

    def update_rect(self, instance, value):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size

    def go_to_payment(self, pkg):
        try:
            self.set_package(pkg)

            if not self.manager.has_screen('payment'):
                raise Exception("Payment screen not found")

            self.manager.current = 'payment'

        except Exception as e:
            logging.error(str(e))
            Popup(
                title="Lỗi",
                content=Label(text="Không thể chuyển sang màn thanh toán."),
                size_hint=(0.7, 0.4)
            ).open()

    def show_detail(self, pkg):
        Popup(
            title=pkg['name_package'],
            content=Label(text=pkg.get("description_package", "Không có mô tả")),
            size_hint=(0.7, 0.5)
        ).open()