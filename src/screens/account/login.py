from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.spinner import MDSpinner
from kivy.uix.modalview import ModalView
from kivy.uix.image import Image
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.clock import Clock
import requests
from kivy.storage.jsonstore import JsonStore
import threading


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = (0.03, 0.05, 0.12, 1)  # Dark background
        self.loading_modal = None
        self._build_ui()

    def _build_ui(self):
        scroll = MDScrollView(size_hint=(1, 1))
        root_layout = self._create_root_layout()

        root_layout.add_widget(MDBoxLayout(size_hint_y=None, height=dp(50)))
        root_layout.add_widget(self._create_header())
        root_layout.add_widget(self._create_form_card())
        root_layout.add_widget(self._create_bottom_nav())
        root_layout.add_widget(MDBoxLayout(size_hint_y=None, height=dp(40)))

        scroll.add_widget(root_layout)
        self.add_widget(scroll)

    def _create_root_layout(self):
        layout = MDBoxLayout(
            orientation="vertical",
            padding=(dp(10), 0),
            spacing=dp(25),
            size_hint_y=None
        )
        layout.bind(minimum_height=layout.setter('height'))
        return layout

    def _create_header(self):
        header = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(20),
            spacing=dp(10)
        )

        # Title with gradient effect
        title = MDLabel(
            text="Đăng Nhập",
            halign="center",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_style="H3",
            bold=True,
            size_hint_y=None,
            height=dp(45)
        )

        header.add_widget(title)
        return header

    def _create_form_card(self):
        card = MDCard(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(22),
            size_hint=(1, None),
            height=dp(450),
            radius=[20],
            md_bg_color=(1, 1, 1, 1),
            shadow_softness=12,
            shadow_offset=(0, 4),
            elevation=10
        )

        # Email field
        email_box = self._create_input_group("Email", "email")
        card.add_widget(email_box)

        # Password field
        password_box = self._create_input_group("Mật khẩu", "password")
        card.add_widget(password_box)

        # Forgot password
        forgot_container = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(30)
        )

        forgot_btn = MDFlatButton(
            text="Quên mật khẩu?",
            text_color=(0.2, 0.45, 0.85, 1),
            pos_hint={"right": 1},
            on_release=self.forgot_password
        )
        forgot_btn.font_size = dp(14)

        forgot_container.add_widget(MDBoxLayout())
        forgot_container.add_widget(forgot_btn)
        card.add_widget(forgot_container)

        # Login button
        login_btn = MDRaisedButton(
            text="Đăng nhập",
            md_bg_color=(0.2, 0.45, 0.85, 1),
            size_hint=(1, None),
            height=dp(54),
            elevation=3,
            on_release=self.login
        )
        login_btn.font_size = dp(16)
        login_btn.bold = True
        card.add_widget(login_btn)

        # Divider
        card.add_widget(self._create_divider())

        # Google button
        google_btn = self._create_google_button()
        card.add_widget(google_btn)

        return card

    def _create_input_group(self, label_text, field_type):
        container = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(75),
            spacing=dp(8)
        )

        # Label
        label = MDLabel(
            text=label_text,
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_style="Body2",
            bold=True,
            size_hint_y=None,
            height=dp(20)
        )
        label.font_size = dp(14)

        # Input field
        if field_type == "email":
            self.email = MDTextField(
                mode="rectangle",
                line_color_normal=(0.7, 0.7, 0.75, 1),
                line_color_focus=(0.2, 0.45, 0.85, 1),
                text_color_normal=(1, 1, 1, 1),
                fill_color_normal=(1, 1, 1, 1),
                fill_color_focus=(1, 1, 1, 1),
                cursor_color=(0.2, 0.45, 0.85, 1),
                size_hint_y=None,
                height=dp(40)
            )
            self.email.font_size = dp(15)
            container.add_widget(label)
            container.add_widget(self.email)
        else:
            # Password with toggle
            input_box = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(55),
                spacing=0
            )

            self.password = MDTextField(
                password=True,
                mode="rectangle",
                line_color_normal=(0.7, 0.7, 0.75, 1),
                line_color_focus=(0.2, 0.45, 0.85, 1),
                text_color_normal=(1, 1, 1, 1),
                fill_color_normal=(1, 1, 1, 1),
                fill_color_focus=(1, 1, 1, 1),
                cursor_color=(0.2, 0.45, 0.85, 1),
                size_hint_y=None,
                height=dp(40)
            )
            self.password.font_size = dp(15)
            self.password.size_hint_x = 0.88

            self.show_pass_btn = MDIconButton(
                icon="eye-off",
                on_release=self.toggle_password,
                theme_text_color="Custom",
                text_color=(0.5, 0.5, 0.55, 1),
                icon_size=dp(22)
            )

            input_box.add_widget(self.password)
            input_box.add_widget(self.show_pass_btn)

            container.add_widget(label)
            container.add_widget(input_box)

        return container

    def _create_divider(self):
        divider_box = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(30),
            spacing=dp(12)
        )

        line1 = MDBoxLayout(size_hint_y=None, height=dp(1))
        line1.md_bg_color = (0.85, 0.85, 0.88, 1)

        or_label = MDLabel(
            text="hoặc",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.5, 0.5, 0.55, 1),
            font_style="Caption",
            size_hint_x=None,
            width=dp(50)
        )

        line2 = MDBoxLayout(size_hint_y=None, height=dp(1))
        line2.md_bg_color = (0.85, 0.85, 0.88, 1)

        divider_box.add_widget(line1)
        divider_box.add_widget(or_label)
        divider_box.add_widget(line2)

        return divider_box

    def _create_google_button(self):
        google_btn = MDRaisedButton(
            text="  Tiếp tục với Google",
            md_bg_color=(1, 1, 1, 1),
            text_color=(0.25, 0.25, 0.3, 1),
            size_hint=(1, None),
            height=dp(52),
            elevation=2
        )
        google_btn.font_size = dp(15)

        # Add border effect
        with google_btn.canvas.before:
            Color(0.85, 0.85, 0.88, 1)
            google_btn.border_rect = RoundedRectangle(
                pos=google_btn.pos,
                size=google_btn.size,
                radius=[google_btn.height / 2]
            )

        def update_border(*args):
            google_btn.border_rect.pos = google_btn.pos
            google_btn.border_rect.size = google_btn.size

        google_btn.bind(pos=update_border, size=update_border)

        return google_btn

    def _create_bottom_nav(self):
        bottom_container = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(20),
            padding=(0, dp(20), 0, 0)
        )

        bottom_box = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(30),
            spacing=dp(5)
        )

        label = MDLabel(
            text="Chưa có tài khoản?",
            theme_text_color="Custom",
            text_color=(0.8, 0.82, 0.87, 1),
            font_style="Body2",
            size_hint_x=None,
            width=dp(140),
            halign="right"
        )
        label.font_size = dp(15)

        register_btn = MDFlatButton(
            text="Đăng ký ngay",
            text_color=(0.3, 0.6, 1, 1),
            on_release=lambda x: setattr(self.manager, 'current', 'register')
        )
        register_btn.font_size = dp(15)
        register_btn.bold = True

        bottom_box.add_widget(label)
        bottom_box.add_widget(register_btn)
        bottom_container.add_widget(bottom_box)

        return bottom_container

    def toggle_password(self, instance):
        self.password.password = not self.password.password
        instance.icon = "eye" if not self.password.password else "eye-off"
        instance.text_color = (0.2, 0.45, 0.85, 1) if not self.password.password else (0.5, 0.5, 0.55, 1)

    def forgot_password(self, instance):
        self.show_dialog(
            "Quên mật khẩu",
            "Tính năng này đang được phát triển.\nVui lòng liên hệ admin để được hỗ trợ."
        )

    def show_loading(self):
        if self.loading_modal is None:
            self.loading_modal = ModalView(
                size_hint=(None, None),
                size=(dp(150), dp(150)),
                background_color=(0, 0, 0, 0.75),
                auto_dismiss=False
            )

            layout = MDBoxLayout(
                orientation="vertical",
                spacing=dp(18),
                padding=dp(30)
            )

            spinner = MDSpinner(
                size_hint=(None, None),
                size=(dp(60), dp(60)),
                pos_hint={'center_x': 0.5},
                active=True,
                palette=[
                    [0.2, 0.45, 0.85, 1],
                    [0.3, 0.85, 0.65, 1],
                ]
            )

            label = MDLabel(
                text="Đang đăng nhập...",
                halign="center",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                font_style="Body1",
                bold=True
            )
            label.font_size = dp(14)

            layout.add_widget(spinner)
            layout.add_widget(label)
            self.loading_modal.add_widget(layout)

        self.loading_modal.open()

    def hide_loading(self):
        if self.loading_modal:
            self.loading_modal.dismiss()

    def login(self, instance):
        email = self.email.text.strip()
        password = self.password.text.strip()

        if not email or not password:
            self.show_dialog("Lỗi", "Vui lòng nhập đầy đủ thông tin đăng nhập.")
            return

        self.show_loading()

        thread = threading.Thread(target=self.do_login, args=(email, password))
        thread.daemon = True
        thread.start()

    def do_login(self, email, password):
        try:
            response = requests.post(
                'https://backend-onlinesystem.onrender.com/api/users/login',
                json={'email': email, 'password': password},
                timeout=15
            )
            data = response.json()

            if response.status_code == 200 and data.get('success'):
                store = JsonStore('user.json')
                store.put('auth', token=data['token'], user=data['user'], login_time=data['login_time'])

                Clock.schedule_once(lambda dt: self._on_login_success(data['user']['fullName']))
            else:
                msg = data.get('message', 'Đăng nhập thất bại. Vui lòng kiểm tra lại thông tin.')
                Clock.schedule_once(lambda dt: self._on_login_error(msg))

        except requests.exceptions.Timeout:
            Clock.schedule_once(lambda dt: self._on_login_error("Kết nối timeout. Vui lòng thử lại."))
        except requests.exceptions.ConnectionError:
            Clock.schedule_once(
                lambda dt: self._on_login_error("Không thể kết nối đến server.\nVui lòng kiểm tra kết nối internet."))
        except requests.exceptions.RequestException as e:
            Clock.schedule_once(lambda dt: self._on_login_error(f"Lỗi mạng: {str(e)}"))
        except Exception as e:
            Clock.schedule_once(lambda dt: self._on_login_error(f"Lỗi không xác định: {str(e)}"))

    def _on_login_success(self, fullname):
        self.hide_loading()
        self.show_success_dialog(
            "Đăng nhập thành công!",
            f"Chào mừng {fullname} trở lại!\n\nHãy tiếp tục hành trình học tập của bạn."
        )

    def _on_login_error(self, message):
        self.hide_loading()
        self.show_dialog("Đăng nhập thất bại", message)

    def show_dialog(self, title, text):
        dialog = MDDialog(
            title=title,
            text=text,
            size_hint=(0.85, None),
            height=dp(220),
            buttons=[
                MDRaisedButton(
                    text="Đóng",
                    md_bg_color=(0.5, 0.5, 0.55, 1),
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()

    def show_success_dialog(self, title, text):
        dialog = MDDialog(
            title=title,
            text=text,
            size_hint=(0.85, None),
            height=dp(250),
            buttons=[
                MDRaisedButton(
                    text="Vào trang chủ",
                    md_bg_color=(0.2, 0.45, 0.85, 1),
                    on_release=lambda x: self.go_to_home(dialog)
                )
            ]
        )
        dialog.open()

    def go_to_home(self, dialog):
        dialog.dismiss()
        self.manager.current = "home"