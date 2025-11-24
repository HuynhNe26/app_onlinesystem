from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
from datetime import datetime, timedelta
import requests
import threading

class IntroScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = FloatLayout()

        with layout.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)

        layout.bind(size=self._update_bg, pos=self._update_bg)

        logo = Image(
            source="src/assets/logo.png",
            size_hint=(None, None),
            size=(200, 200),
            allow_stretch=True,
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        layout.add_widget(logo)
        self.add_widget(layout)
        Clock.schedule_once(self.check_user_login, 1)

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos

    def check_user_login(self, dt):
        try:
            store = JsonStore("user.json")

            if not store.exists("auth"):
                print("Chưa có dữ liệu đăng nhập -> Vào màn hình Intro")
                return self.goto_intro_info()

            data = store.get("auth")
            token = data.get("token")

            if not token:
                return self.goto_intro_info()
            threading.Thread(target=self.verify_token_with_server, args=(token,)).start()

        except Exception as e:
            print("Lỗi IntroScreen:", e)
            self.goto_intro_info()

    def verify_token_with_server(self, old_token):
        try:
            response = requests.get(
                'https://backend-onlinesystem.onrender.com/api/users/auth/verify',
                headers={'Authorization': f'Bearer {old_token}'},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    new_token = data.get('token', old_token)

                    store = JsonStore("user.json")
                    store.put("auth",
                              token=new_token,
                              user=data['user'],
                              login_time=datetime.now().isoformat()
                              )
                    Clock.schedule_once(lambda dt: self.goto_home())
                    return
            Clock.schedule_once(lambda dt: self.goto_intro_info())
        except Exception as e:
            print("Lỗi kết nối:", e)
            Clock.schedule_once(lambda dt: self.goto_intro_info())

    def goto_home(self):
        self.manager.current = "home"

    def goto_intro_info(self, *args):
        self.manager.current = "intro_info"