from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.utils import get_color_from_hex
from kivy.metrics import dp

class PaymentSuccessScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))

        layout.add_widget(Label(
            text="🎉 Thanh toán thành công!",
            font_size='24sp',
            bold=True,
            color=get_color_from_hex("#1E90FF"),
            size_hint_y=None,
            height=dp(60)
        ))

        layout.add_widget(Label(
            text="Cảm ơn bạn đã mua gói dịch vụ.",
            font_size='18sp',
            color=(0,0,0,1),
            size_hint_y=None,
            height=dp(40)
        ))

        btn_home = Button(
            text="Quay lại trang chính",
            size_hint_y=None,
            height=dp(50),
            background_color=get_color_from_hex("#1E90FF"),
            color=(1,1,1,1)
        )
        btn_home.bind(on_release=lambda x: setattr(self.manager, "current", "home"))

        layout.add_widget(btn_home)
        self.add_widget(layout)
