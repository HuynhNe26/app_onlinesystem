from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle, Ellipse
from kivy.metrics import dp
import os


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        self.user_data = None

        root_layout = FloatLayout()

        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        header = BoxLayout(orientation='horizontal', size_hint=(1, 0.08))
        header_label = Label(text='Trang chủ', bold=True, font_size='22sp', halign='center', valign='middle')
        header_label.bind(size=lambda inst, val: self._auto_resize_label(inst))
        header.add_widget(header_label)
        main_layout.add_widget(header)

        scroll = ScrollView(size_hint=(1, 0.92))
        content = BoxLayout(orientation='vertical', spacing=15, size_hint_y=None, padding=(5, 5))
        content.bind(minimum_height=content.setter('height'))

        content.add_widget(self.create_user_card())
        content.add_widget(self.create_today_goal())
        content.add_widget(self.create_recent_activity())
        content.add_widget(self.create_recommendation())
        content.add_widget(self.create_upgrade_banner())

        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        self.add_widget(main_layout)
    def on_enter(self):
        self.load_user_data()

    def load_user_data(self):
        try:
            from kivy.storage.jsonstore import JsonStore
            store = JsonStore('user.json')
            if store.exists('user'):
                self.user_data = store.get('user')
                self.update_user_card()
        except Exception as e:
            print(f"Lỗi load user data: {e}")

    def update_user_card(self):
        if not self.user_data:
            return

        if hasattr(self, 'user_name_label'):
            full_name = self.user_data.get('fullName', 'Bạn')
            self.user_name_label.text = f'Chào {full_name}'

        if hasattr(self, 'avatar_container') and hasattr(self.avatar_container, 'circle'):
            avatar_path = self.user_data.get('avatar', '')

            if avatar_path and os.path.exists(avatar_path):
                self.avatar_container.circle.source = avatar_path
            else:
                gender = self.user_data.get('gender', 'Nam')
                default_avatar = 'src/assets/Avt/nam.png' if gender == 'Nam' else 'src/assets/Avt/nu.png'
                if os.path.exists(default_avatar):
                    self.avatar_container.circle.source = default_avatar

    def create_user_card(self):
        card = BoxLayout(orientation='vertical', padding=15, spacing=10, size_hint_y=None, height=200)
        with card.canvas.before:
            Color(0.1, 0.15, 0.35, 1)
            card.bg = RoundedRectangle(radius=[20], size=card.size, pos=card.pos)
        card.bind(size=self._update_bg, pos=self._update_bg)

        top_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=80, spacing=15)

        self.avatar_container = FloatLayout(size_hint=(None, None), size=(dp(70), dp(70)))
        with self.avatar_container.canvas.before:
            Color(1, 1, 1, 1)
            self.avatar_container.circle = Ellipse(
                pos=self.avatar_container.pos,
                size=self.avatar_container.size,
                source='src/assets/Avt/nam.png'
            )
        self.avatar_container.bind(pos=self._update_avatar_circle, size=self._update_avatar_circle)
        top_box.add_widget(self.avatar_container)

        name_box = BoxLayout(orientation='vertical', spacing=5)
        self.user_name_label = Label(
            text='Chào bạn',
            color=(1, 1, 1, 1),
            font_size='20sp',
            bold=True,
            halign='left',
            valign='middle'
        )
        self.user_name_label.bind(size=lambda inst, val: self._auto_resize_label_left(inst))

        lbl2 = Label(
            text='Sẵn sàng học hôm nay?',
            color=(1, 1, 1, 0.9),
            font_size='14sp',
            halign='left',
            valign='middle'
        )
        lbl2.bind(size=lambda inst, val: self._auto_resize_label_left(inst))

        name_box.add_widget(self.user_name_label)
        name_box.add_widget(lbl2)
        top_box.add_widget(name_box)

        card.add_widget(top_box)

        stats = GridLayout(cols=3, size_hint_y=None, height=60)
        for text in ['156\nBài thi', '87.5\nĐiểm TB', '#23\nXếp hạng']:
            lbl = Label(text=text, color=(1, 1, 1, 1), halign='center', valign='middle')
            lbl.bind(size=lambda inst, val: self._auto_resize_label(inst))
            stats.add_widget(lbl)
        card.add_widget(stats)
        return card

    def create_today_goal(self):
        box = BoxLayout(orientation='vertical', spacing=5, padding=10, size_hint_y=None, height=160)
        with box.canvas.before:
            Color(1, 1, 1, 1)
            box.bg = RoundedRectangle(radius=[20], size=box.size, pos=box.pos)
        box.bind(size=self._update_bg, pos=self._update_bg)

        btn_box = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)

        btn_test = Button(
            text="🧩 Kiểm tra",
            background_color=(0.2, 0.6, 1, 1)
        )
        btn_test.bind(on_press=self.goto_test)

        btn_box.add_widget(btn_test)

        box.add_widget(btn_box)
        return box

    def create_recent_activity(self):
        box = BoxLayout(orientation='vertical', spacing=5, padding=10, size_hint_y=None, height=170)
        with box.canvas.before:
            Color(1, 1, 1, 1)
            box.bg = RoundedRectangle(radius=[20], size=box.size, pos=box.pos)
        box.bind(size=self._update_bg, pos=self._update_bg)

        header = BoxLayout(orientation='horizontal')
        lbl1 = Label(text='📚 Hoạt động gần đây', color=(0, 0, 0, 1), font_size='16sp', bold=True)
        lbl2 = Label(text='Xem tất cả', color=(0, 0.6, 1, 1), font_size='14sp')
        for lbl in (lbl1, lbl2):
            lbl.bind(size=lambda inst, val: self._auto_resize_label(inst))
            header.add_widget(lbl)
        box.add_widget(header)

        for text in ['• Toán học lớp 12 - Đề 1: 85 điểm', '• Hóa học - Bảng tuần hoàn: 78 điểm']:
            lbl = Label(text=text, color=(0, 0, 0, 1))
            lbl.bind(size=lambda inst, val: self._auto_resize_label(inst))
            box.add_widget(lbl)
        return box

    def create_recommendation(self):
        box = BoxLayout(orientation='vertical', spacing=5, padding=10, size_hint_y=None, height=160)
        with box.canvas.before:
            Color(1, 1, 1, 1)
            box.bg = RoundedRectangle(radius=[20], size=box.size, pos=box.pos)
        box.bind(size=self._update_bg, pos=self._update_bg)

        lbl1 = Label(text='💡 Đề xuất cho bạn', color=(0, 0, 0, 1), font_size='16sp', bold=True)
        lbl2 = Label(text='Toán học: Hàm số bậc 2 – Cần cải thiện theo kết quả gần đây.', color=(0, 0, 0, 1))
        lbl3 = Label(text='Vật lý: Động lực học – Củng cố kiến thức cơ bản.', color=(0, 0, 0, 1))
        for lbl in (lbl1, lbl2, lbl3):
            lbl.bind(size=lambda inst, val: self._auto_resize_label(inst))
            box.add_widget(lbl)
        return box

    def create_upgrade_banner(self):
        box = BoxLayout(orientation='horizontal', padding=10, size_hint_y=None, height=60, spacing=10)
        with box.canvas.before:
            Color(1, 0.5, 0.3, 1)
            box.bg = RoundedRectangle(radius=[20], size=box.size, pos=box.pos)
        box.bind(size=self._update_bg, pos=self._update_bg)

        lbl = Label(text='✨ Nâng cấp lên Pro để mở khóa toàn bộ tính năng!', color=(1, 1, 1, 1), halign='center')
        lbl.bind(size=lambda inst, val: self._auto_resize_label(inst))
        box.add_widget(lbl)

        btn = Button(text='Nâng cấp', background_color=(1, 0.2, 0.2, 1), size_hint=(0.3, 1))
        btn.bind(on_press=self.goto_package)
        box.add_widget(btn)
        return box

    def create_goal_row(self, subject, done, total):
        layout = BoxLayout(orientation='vertical', size_hint_y=None, height=45)
        lbl = Label(text=f"{subject}: {done}/{total} bài", color=(0, 0, 0, 1))
        lbl.bind(size=lambda inst, val: self._auto_resize_label(inst))
        layout.add_widget(lbl)
        pb = ProgressBar(max=total, value=done, size_hint_y=None, height=10)
        layout.add_widget(pb)
        return layout

    def _update_bg(self, instance, value):
        if hasattr(instance, 'bg'):
            instance.bg.pos = instance.pos
            instance.bg.size = instance.size

    def _update_avatar_circle(self, instance, value):
        if hasattr(instance, 'circle'):
            instance.circle.pos = instance.pos
            instance.circle.size = instance.size

    def _auto_resize_label(self, label):
        label.text_size = (label.width - 10, None)
        label.halign = 'center'
        label.valign = 'middle'

    def _auto_resize_label_left(self, label):
        label.text_size = (label.width - 10, None)
        label.halign = 'left'
        label.valign = 'middle'

    def goto_package(self, instance):
        if self.manager:
            self.manager.current = 'package'

    def goto_test(self, instance):
        if self.manager:
            self.manager.current = 'exam_setup'
