from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore

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
            store = JsonStore('user.json')
            if store.exists('auth'):
                auth_data = store.get('auth')

                user = auth_data.get("user", None)

                if user:
                    self.manager.current = "home"
                    return
            Clock.schedule_once(self.goto_intro_info, 2)
        except Exception as e:
            print("Lỗi kiểm tra token:", e)
            Clock.schedule_once(self.goto_intro_info, 2)
    def goto_intro_info(self, dt):
        self.manager.current = 'intro_info'
