from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
from datetime import datetime, timedelta

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

        Clock.schedule_once(self.check_user_login, 4)

    def _update_bg(self, instance, value):
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos

    def check_user_login(self, dt):
        try:
            store = JsonStore("user.json")

            if not store.exists("auth"):
                return self.goto_intro_info()

            data = store.get("auth")

            user = data.get("user")
            login_time_str = data.get("login_time")

            if not user or not login_time_str:
                return self.goto_intro_info()

            login_time = datetime.fromisoformat(login_time_str)
            now = datetime.now()

            delta = now - login_time

            if delta <= timedelta(days=1):
                store.put("auth", token=data["token"], user=user, login_time=now.isoformat())
                self.manager.current = "home"
                return
            self.goto_intro_info()

        except Exception as e:
            print("Lỗi IntroScreen:", e)
            self.goto_intro_info()

    def goto_intro_info(self, *args):
        self.manager.current = "intro_info"
