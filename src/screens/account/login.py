from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.image import Image
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from kivymd.uix.spinner import MDSpinner
import requests
from kivy.storage.jsonstore import JsonStore
import threading


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.clearcolor = (0.12, 0.12, 0.12, 1)

        self.root_layout = AnchorLayout(anchor_x='center', anchor_y='center')
        form_box = BoxLayout(orientation='vertical', spacing=15, padding=30, size_hint=(0.8, 0.6))
        with form_box.canvas.before:
            Color(1, 1, 1, 0.08)
            self.rect = RoundedRectangle(radius=[20], pos=form_box.pos, size=form_box.size)
        form_box.bind(pos=self._update_rect, size=self._update_rect)

        form_box.add_widget(
            Image(source="src/assets/logo.png", size_hint=(1, 0.4), allow_stretch=True, keep_ratio=True))
        title = Label(text='[b]ĐĂNG NHẬP[/b]', markup=True, font_size='26sp', color=(1, 1, 1, 1))
        form_box.add_widget(title)

        self.email = TextInput(hint_text='Email', multiline=False, size_hint_y=None, height=45,
                               background_color=(1, 1, 1, 0.1), foreground_color=(1, 1, 1, 1),
                               padding=(10, 10))
        self.password = TextInput(hint_text='Mật khẩu', password=True, multiline=False, size_hint_y=None, height=45,
                                  background_color=(1, 1, 1, 0.1), foreground_color=(1, 1, 1, 1),
                                  padding=(10, 10))
        form_box.add_widget(self.email)
        form_box.add_widget(self.password)

        self.btn_login = Button(text='Đăng nhập', size_hint_y=None, height=45,
                                background_color=(0.2, 0.6, 1, 1), color=(1, 1, 1, 1),
                                on_press=self.login)
        btn_register = Button(text='Chưa có tài khoản? Đăng ký ngay',
                              background_color=(0, 0, 0, 0), color=(0.6, 0.8, 1, 1),
                              size_hint_y=None, height=40,
                              on_press=self.goto_register)
        form_box.add_widget(self.btn_login)
        form_box.add_widget(btn_register)

        self.root_layout.add_widget(form_box)

        self.loading_overlay = AnchorLayout(anchor_x='center', anchor_y='center')
        with self.loading_overlay.canvas.before:
            Color(0, 0, 0, 0.7)  # Nền đen mờ
            self.loading_bg = RoundedRectangle(pos=self.loading_overlay.pos, size=self.loading_overlay.size)
        self.loading_overlay.bind(pos=self._update_loading_bg, size=self._update_loading_bg)

        loading_box = BoxLayout(orientation='vertical', spacing=20, size_hint=(None, None), size=(200, 120))

        self.spinner = MDSpinner(
            size_hint=(None, None),
            size=(60, 60),
            active=True,
            color=(0.2, 0.6, 1, 1),
            pos_hint={'center_x': 0.5}
        )

        loading_label = Label(
            text='Đang đăng nhập...',
            color=(1, 1, 1, 1),
            font_size='18sp',
            size_hint_y=None,
            height=40
        )

        loading_box.add_widget(self.spinner)
        loading_box.add_widget(loading_label)

        self.loading_overlay.add_widget(loading_box)

        self.add_widget(self.root_layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_loading_bg(self, instance, value):
        self.loading_bg.pos = instance.pos
        self.loading_bg.size = instance.size

    def show_loading(self):
        if self.loading_overlay not in self.children:
            self.add_widget(self.loading_overlay)
        self.btn_login.disabled = True
        self.email.disabled = True
        self.password.disabled = True

    def hide_loading(self):
        if self.loading_overlay in self.children:
            self.remove_widget(self.loading_overlay)
        self.btn_login.disabled = False
        self.email.disabled = False
        self.password.disabled = False

    def login(self, instance):
        email = self.email.text.strip()
        password = self.password.text.strip()

        if not email or not password:
            self.show_popup("Lỗi", "Vui lòng nhập email và mật khẩu.")
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
                timeout=10
            )
            data = response.json()

            from kivy.clock import Clock

            if response.status_code == 200 and data.get('success'):
                store = JsonStore('user.json')
                store.put('auth', token=data['token'], user=data['user'])

                Clock.schedule_once(lambda dt: self._on_login_success(data['user']['fullName']))
            else:
                msg = data.get('message', 'Đăng nhập thất bại.')
                Clock.schedule_once(lambda dt: self._on_login_error(msg))

        except requests.exceptions.Timeout:
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self._on_login_error("Kết nối timeout. Vui lòng thử lại."))
        except requests.exceptions.ConnectionError:
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self._on_login_error("Không thể kết nối đến server."))
        except requests.exceptions.RequestException as e:
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self._on_login_error(f"Lỗi mạng: {str(e)}"))
        except Exception as e:
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self._on_login_error(f"Lỗi không xác định: {str(e)}"))

    def _on_login_success(self, fullname):
        self.hide_loading()
        self.show_popup("Thành công", f"Chào mừng {fullname}!")
        self.manager.current = 'home'

    def _on_login_error(self, message):
        self.hide_loading()
        self.show_popup("Lỗi", message)

    def goto_register(self, instance):
        self.manager.current = 'register'

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message),
                      size_hint=(0.7, 0.4), separator_color=(0.2, 0.6, 1, 1))
        popup.open()