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
import requests
from kivy.storage.jsonstore import JsonStore

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.clearcolor = (0.12, 0.12, 0.12, 1)

        root = AnchorLayout(anchor_x='center', anchor_y='center')
        form_box = BoxLayout(orientation='vertical', spacing=15, padding=30, size_hint=(0.8, 0.6))
        with form_box.canvas.before:
            Color(1, 1, 1, 0.08)
            self.rect = RoundedRectangle(radius=[20], pos=form_box.pos, size=form_box.size)
        form_box.bind(pos=self._update_rect, size=self._update_rect)

        form_box.add_widget(Image(source="src/assets/logo.png", size_hint=(1, 0.4), allow_stretch=True, keep_ratio=True))
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

        btn_login = Button(text='Đăng nhập', size_hint_y=None, height=45,
                           background_color=(0.2, 0.6, 1, 1), color=(1, 1, 1, 1),
                           on_press=self.login)
        btn_register = Button(text='Chưa có tài khoản? Đăng ký ngay',
                              background_color=(0, 0, 0, 0), color=(0.6, 0.8, 1, 1),
                              size_hint_y=None, height=40,
                              on_press=self.goto_register)
        form_box.add_widget(btn_login)
        form_box.add_widget(btn_register)

        root.add_widget(form_box)
        self.add_widget(root)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def login(self, instance):
        email = self.email.text.strip()
        password = self.password.text.strip()

        if not email or not password:
            self.show_popup("Lỗi", "Vui lòng nhập email và mật khẩu.")
            return

        try:
            response = requests.post(
                'https://backend-onlinesystem.onrender.com/api/users/login',
                json={'email': email, 'password': password},
                timeout=10
            )
            data = response.json()

            if response.status_code == 200 and data.get('success'):
                # Lưu token và user info
                store = JsonStore('user.json')
                store.put('auth', token=data['token'], user=data['user'])

                self.show_popup("Thành công", f"Chào mừng {data['user']['fullName']}!")
                # Chuyển màn hình
                self.manager.current = 'home'
            else:
                msg = data.get('message', 'Đăng nhập thất bại.')
                self.show_popup("Lỗi", msg)

        except requests.exceptions.Timeout:
            self.show_popup("Lỗi", "Kết nối timeout. Vui lòng thử lại.")
        except requests.exceptions.ConnectionError:
            self.show_popup("Lỗi", "Không thể kết nối đến server.")
        except requests.exceptions.RequestException as e:
            self.show_popup("Lỗi", f"Lỗi mạng: {str(e)}")
        except Exception as e:
            self.show_popup("Lỗi", f"Lỗi không xác định: {str(e)}")

    def goto_register(self, instance):
        self.manager.current = 'register'

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message),
                      size_hint=(0.7, 0.4), separator_color=(0.2, 0.6, 1, 1))
        popup.open()