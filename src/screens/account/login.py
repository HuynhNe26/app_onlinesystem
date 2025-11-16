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
from kivy.metrics import dp
from kivy.clock import Clock
import requests
from kivy.storage.jsonstore import JsonStore
import threading


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = (0.05, 0.08, 0.16, 1)
        self.loading_modal = None
        self._build_ui()

    def _build_ui(self):
        scroll = MDScrollView(size_hint=(1, 1))
        root_layout = self._create_root_layout()

        root_layout.add_widget(self._create_header())
        root_layout.add_widget(self._create_form_card())
        root_layout.add_widget(self._create_bottom_nav())

        scroll.add_widget(root_layout)
        self.add_widget(scroll)

    def _create_root_layout(self):
        layout = MDBoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(25),
            size_hint_y=None
        )
        layout.bind(minimum_height=layout.setter('height'))
        return layout

    def _create_header(self):
        header = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(180),
            spacing=dp(15)
        )

        # Logo
        logo = Image(
            source="src/assets/logo.png",
            size_hint=(None, None),
            size=(dp(100), dp(100)),
            pos_hint={"center_x": 0.5}
        )

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

        subtitle = MDLabel(
            text="Chào mừng bạn trở lại!",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.7, 0.75, 0.85, 1),
            font_style="H6",
            size_hint_y=None,
            height=dp(30)
        )

        header.add_widget(logo)
        header.add_widget(title)
        header.add_widget(subtitle)
        return header

    def _create_form_card(self):
        card = MDCard(
            orientation="vertical",
            padding=dp(30),
            spacing=dp(20),
            size_hint=(1, None),
            height=dp(380),
            radius=[30],
            md_bg_color=(0.98, 0.98, 0.99, 1),
            shadow_softness=12,
            shadow_offset=(0, 4),
            elevation=6
        )

        # Email field
        self.email = self._create_text_field("Email")
        card.add_widget(self.email)

        # Password field
        card.add_widget(self._create_password_field())

        # Forgot password link
        forgot_box = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(30)
        )
        forgot_btn = MDFlatButton(
            text="Quên mật khẩu?",
            text_color=(0.29, 0.56, 0.89, 1),
            pos_hint={"right": 1},
            on_release=self.forgot_password
        )
        forgot_btn.font_size = dp(13)
        forgot_box.add_widget(forgot_btn)
        card.add_widget(forgot_box)

        # Login button with gradient effect
        login_btn = MDRaisedButton(
            text="Đăng nhập",
            md_bg_color=(0.18, 0.38, 0.78, 1),
            size_hint=(1, None),
            height=dp(52),
            elevation=4,
            on_release=self.login
        )
        login_btn.font_size = dp(16)
        card.add_widget(login_btn)

        # Quick login options
        divider_box = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(30),
            spacing=dp(10)
        )

        line1 = MDBoxLayout(size_hint_x=0.4, size_hint_y=None, height=dp(1))
        line1.md_bg_color = (0.7, 0.7, 0.7, 0.3)

        or_label = MDLabel(
            text="hoặc",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.5, 0.5, 0.5, 1),
            font_style="Caption",
            size_hint_x=0.2
        )

        line2 = MDBoxLayout(size_hint_x=0.4, size_hint_y=None, height=dp(1))
        line2.md_bg_color = (0.7, 0.7, 0.7, 0.3)

        divider_box.add_widget(line1)
        divider_box.add_widget(or_label)
        divider_box.add_widget(line2)
        card.add_widget(divider_box)

        # Social login buttons
        social_box = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(45),
            spacing=dp(15)
        )

        google_btn = MDRaisedButton(
            text="Google",
            md_bg_color=(0.95, 0.95, 0.95, 1),
            text_color=(0.2, 0.2, 0.2, 1),
            size_hint_x=0.5,
            elevation=2
        )

        facebook_btn = MDRaisedButton(
            text="Facebook",
            md_bg_color=(0.95, 0.95, 0.95, 1),
            text_color=(0.2, 0.2, 0.2, 1),
            size_hint_x=0.5,
            elevation=2
        )

        social_box.add_widget(google_btn)
        social_box.add_widget(facebook_btn)
        card.add_widget(social_box)

        return card

    def _create_text_field(self, hint):
        field = MDTextField(
            hint_text=hint,
            mode="rectangle",
            line_color_normal=(0.6, 0.65, 0.7, 1),
            line_color_focus=(0.18, 0.38, 0.78, 1),
            hint_text_color_normal=(0.5, 0.5, 0.55, 1),
            hint_text_color_focus=(0.3, 0.3, 0.35, 1),
            text_color_normal=(0.1, 0.1, 0.15, 1),
            text_color_focus=(0, 0, 0.05, 1),
            fill_color_normal=(0.96, 0.97, 0.98, 1),
            fill_color_focus=(1, 1, 1, 1),
            cursor_color=(0.18, 0.38, 0.78, 1),
            size_hint_y=None,
            height=dp(56)
        )
        field.font_size = dp(15)
        return field

    def _create_password_field(self):
        password_box = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(56)
        )

        self.password = self._create_text_field("🔒 Mật khẩu")
        self.password.password = True
        self.password.size_hint_x = 0.88

        self.show_pass_btn = MDIconButton(
            icon="eye-off",
            on_release=self.toggle_password,
            theme_text_color="Custom",
            text_color=(0.5, 0.5, 0.55, 1),
            icon_size=dp(26)
        )

        password_box.add_widget(self.password)
        password_box.add_widget(self.show_pass_btn)
        return password_box

    def _create_bottom_nav(self):
        bottom_box = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(50),
            spacing=dp(5)
        )

        label1 = MDLabel(
            text="Chưa có tài khoản? ",
            theme_text_color="Custom",
            text_color=(0.75, 0.77, 0.82, 1),
            font_style="Body2",
            size_hint_x=None,
            width=dp(140),
            halign="right"
        )

        btn = MDFlatButton(
            text="Đăng ký ngay",
            text_color=(0.29, 0.56, 0.89, 1),
            on_release=lambda x: setattr(self.manager, 'current', 'register')
        )
        btn.font_size = dp(15)

        bottom_box.add_widget(label1)
        bottom_box.add_widget(btn)

        wrapper = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(50)
        )
        wrapper.add_widget(bottom_box)

        return wrapper

    def toggle_password(self, instance):
        self.password.password = not self.password.password
        instance.icon = "eye" if not self.password.password else "eye-off"
        instance.text_color = (0.18, 0.38, 0.78, 1) if not self.password.password else (0.5, 0.5, 0.55, 1)

    def forgot_password(self, instance):
        self.show_dialog(
            "🔐 Quên mật khẩu",
            "Tính năng này đang được phát triển.\nVui lòng liên hệ admin để được hỗ trợ."
        )

    def show_loading(self):
        if self.loading_modal is None:
            self.loading_modal = ModalView(
                size_hint=(None, None),
                size=(dp(120), dp(120)),
                background_color=(0, 0, 0, 0.6),
                auto_dismiss=False
            )

            layout = MDBoxLayout(
                orientation="vertical",
                spacing=dp(12),
                padding=dp(20)
            )

            spinner = MDSpinner(
                size_hint=(None, None),
                size=(dp(50), dp(50)),
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                active=True,
                palette=[
                    [0.18, 0.38, 0.78, 1],
                    [0.28, 0.84, 0.60, 1],
                    [0.89, 0.36, 0.59, 1],
                    [0.96, 0.76, 0.19, 1],
                ]
            )

            label = MDLabel(
                text="Đang đăng nhập...",
                halign="center",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                font_style="Body2",
                bold=True
            )

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
                store.put('auth', token=data['token'], user=data['user'])

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
                    md_bg_color=(0.18, 0.38, 0.78, 1),
                    on_release=lambda x: self.go_to_home(dialog)
                )
            ]
        )
        dialog.open()

    def go_to_home(self, dialog):
        dialog.dismiss()
        self.manager.current = "home"