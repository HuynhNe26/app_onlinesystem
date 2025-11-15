from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle, RoundedRectangle


class IntroInfoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

        root = AnchorLayout(anchor_x='center', anchor_y='center')

        layout = BoxLayout(orientation='vertical', spacing=20, padding=30, size_hint=(0.9, 0.8))
        with layout.canvas.before:
            Color(0.1, 0.1, 0.1, 1)  # hộp đen đậm
            self.box_bg = RoundedRectangle(radius=[25], pos=layout.pos, size=layout.size)
        layout.bind(pos=self._update_box, size=self._update_box)

        layout.add_widget(Image(source="src/assets/logo.png", size_hint=(1, 0.4), allow_stretch=True, keep_ratio=True))

        title = Label(
            text='[b]Education Plus\nỨng dụng luyện thi hiệu quả[/b]',
            markup=True,
            font_size='28sp',
            halign='center',
            valign='middle',
            color=(1, 1, 1, 1),
            size_hint=(1, 0.2),
            text_size=(0, None)
        )
        layout.add_widget(title)

        btn_register = Button(
            text='Bắt đầu miễn phí',
            size_hint=(1, 0.12),
            font_size='18sp',
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1),
            on_press=self.register
        )
        layout.add_widget(btn_register)

        btn_login = Button(
            text='Đã có tài khoản? Đăng nhập',
            size_hint=(1, 0.12),
            font_size='17sp',
            background_color=(0, 0, 0, 0),
            color=(0.6, 0.8, 1, 1),
            on_press=self.login
        )
        layout.add_widget(btn_login)

        layout.bind(size=lambda inst, val: self._update_label_size(title, layout.width))
        root.add_widget(layout)
        self.add_widget(root)

    def _update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def _update_box(self, instance, value):
        self.box_bg.pos = instance.pos
        self.box_bg.size = instance.size

    def _update_label_size(self, *args):
        title, width = args
        title.text_size = (width - 60, None)

    def login(self, instance):
        self.manager.current = 'login'

    def register(self, instance):
        self.manager.current = 'register'
