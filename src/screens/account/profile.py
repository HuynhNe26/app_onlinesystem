from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.storage.jsonstore import JsonStore
from kivy.uix.image import Image
from kivy.graphics import Color, RoundedRectangle, Ellipse, StencilPush, StencilUse, StencilPop
from kivy.properties import ObjectProperty, StringProperty
from kivy.metrics import dp


class Card(BoxLayout):
    def __init__(self, **kwargs):
        super(Card, self).__init__(**kwargs)
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = RoundedRectangle(radius=[20])
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class CircleAvatar(Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self.update_canvas, pos=self.update_canvas)

    def update_canvas(self, *args):
        diameter = min(self.width, self.height)
        offset_x = (self.width - diameter) / 2
        offset_y = (self.height - diameter) / 2

        # SỬA LỖI: Cần xóa canvas.before VÀ canvas.after để tránh lỗi StencilPop stack underflow
        self.canvas.before.clear()
        self.canvas.after.clear()

        with self.canvas.before:
            StencilPush()
            Color(1, 1, 1, 1)
            Ellipse(pos=(self.x + offset_x, self.y + offset_y), size=(diameter, diameter))
            StencilUse()

        with self.canvas.after:
            StencilPop()


class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super(ProfileScreen, self).__init__(**kwargs)

        self.default_avatar = "src/assets/Avt/nam.png"

        root = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        self.add_widget(root)

        avatar_box = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(150),
            padding=dp(10),
            spacing=dp(10)
        )
        root.add_widget(avatar_box)

        self.avatar_widget = CircleAvatar(
            source=self.default_avatar,
            size_hint=(None, None),
            size=(dp(120), dp(120)),
            pos_hint={'center_x': 0.5}
        )
        avatar_box.add_widget(self.avatar_widget)

        self.card = Card(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(15),
            size_hint=(1, None)
        )
        self.card.bind(minimum_height=self.card.setter('height'))
        root.add_widget(self.card)

        self.card.add_widget(Label(
            text='[b]THÔNG TIN TÀI KHOẢN[/b]',
            font_size=dp(22),
            markup=True,
            color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None,
            height=dp(30)
        ))

        self.user_grid = GridLayout(
            cols=2,
            spacing=(dp(10), dp(8)),
            size_hint_y=None
        )
        self.user_grid.bind(minimum_height=self.user_grid.setter('height'))
        self.card.add_widget(self.user_grid)

        btn_back = Button(
            text='QUAY LẠI',
            size_hint=(1, None),
            height=dp(50),
            background_color=(0.95, 0.4, 0.4, 1),
            color=(1, 1, 1, 1),
            font_size=dp(18)
        )
        btn_back.bind(on_press=self.goto_home)
        root.add_widget(BoxLayout(size_hint=(1, 0.1)))
        root.add_widget(btn_back)

        self.bind(on_enter=self.load_user_data)

    def load_user_data(self, *args):
        try:
            store = JsonStore('user.json')

            if store.exists('auth'):
                auth = store.get('auth')
                user = auth.get('user', {})

                gender = user.get('gender', 'Nam')
                default_avatar = 'src/assets/Avt/nam.png' if gender.lower() == 'nam' else 'src/assets/Avt/nu.png'

                avatar_path = user.get("avatar")
                if avatar_path and avatar_path.strip() != "":
                    self.avatar_widget.source = avatar_path
                else:
                    self.avatar_widget.source = default_avatar
                self.avatar_widget.reload()

                self.user_grid.clear_widgets()

                fields = [
                    ("Họ và tên", user.get('fullName', 'Không có')),
                    ("Email", user.get('email', 'Không có')),
                    ("Ngày sinh", user.get('dateOfBirth', 'Không có')),
                    ("Giới tính", user.get('gender', 'Không có')),
                ]

                for label, value in fields:
                    self.user_grid.add_widget(
                        Label(
                            text=f"[b]{label}:[/b]",
                            markup=True,
                            font_size=dp(18),
                            halign="left",
                            valign="middle",
                            color=(0.4, 0.4, 0.4, 1),
                            size_hint_y=None,
                            height=dp(30),
                            text_size=(self.user_grid.width / 2 - dp(10), None)
                        )
                    )
                    self.user_grid.add_widget(
                        Label(
                            text=str(value),
                            font_size=dp(18),
                            halign="left",
                            valign="middle",
                            color=(0.1, 0.1, 0.1, 1),
                            size_hint_y=None,
                            height=dp(30),
                            text_size=(self.user_grid.width / 2 - dp(10), None)
                        )
                    )

        except Exception as e:
            pass

    def goto_home(self, instance):
        self.manager.current = 'home'