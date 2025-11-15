from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button


class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super(ProfileScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        layout.add_widget(Label(text='Trang Profile', font_size=24))
        btn_back = Button(text='⬅ Quay lại Home', background_color=(1, 0.4, 0.4, 1))
        btn_back.bind(on_press=self.goto_home)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def goto_home(self, instance):
        self.manager.current = 'home'
