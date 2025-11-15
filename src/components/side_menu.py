from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.metrics import dp
from kivy.animation import Animation


class SideMenu(FloatLayout):
    """Component menu trượt từ bên trái"""

    def __init__(self, on_menu_action=None, **kwargs):
        super(SideMenu, self).__init__(**kwargs)
        self.on_menu_action = on_menu_action  # Callback khi chọn menu
        self.menu_open = False
        self.user_data = None

        # === Overlay (nền tối) - PHẢI THÊM TRƯỚC ===
        self.overlay = FloatLayout(size_hint=(1, 1), opacity=0)
        with self.overlay.canvas.before:
            Color(0, 0, 0, 0.5)
            self.overlay.bg = Rectangle(size=self.overlay.size, pos=self.overlay.pos)
        self.overlay.bind(size=self._update_overlay_bg, pos=self._update_overlay_bg)
        self.overlay.bind(on_touch_down=self.close_menu_on_overlay)
        self.add_widget(self.overlay)

        # === Menu Panel - THÊM SAU để nằm trên overlay ===
        self.menu_panel = self.create_menu_panel()
        self.add_widget(self.menu_panel)

    def create_menu_panel(self):
        """Tạo panel menu"""
        menu = BoxLayout(
            orientation='vertical',
            size_hint=(None, 1),
            width=dp(250),
            pos_hint={'x': -1, 'y': 0},  # Ẩn bên trái ban đầu
            padding=20,
            spacing=15
        )

        with menu.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            menu.bg = Rectangle(size=menu.size, pos=menu.pos)
        menu.bind(size=self._update_menu_bg, pos=self._update_menu_bg)

        # === Header Menu ===
        menu_header = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100), spacing=10)

        # Avatar
        self.avatar_box = FloatLayout(size_hint=(None, None), size=(dp(60), dp(60)), pos_hint={'center_x': 0.5})
        with self.avatar_box.canvas.before:
            Color(1, 1, 1, 1)
            self.avatar_box.circle = Ellipse(
                pos=self.avatar_box.pos,
                size=self.avatar_box.size,
                source='src/assets/Avt/nam.png'
            )
        self.avatar_box.bind(pos=self._update_avatar_circle, size=self._update_avatar_circle)
        menu_header.add_widget(self.avatar_box)

        # Tên user
        self.menu_user_label = Label(
            text='Xin chào!',
            color=(0.1, 0.15, 0.35, 1),
            font_size='16sp',
            bold=True,
            size_hint_y=None,
            height=dp(30)
        )
        menu_header.add_widget(self.menu_user_label)
        menu.add_widget(menu_header)

        # === Đường kẻ phân cách ===
        separator = Label(size_hint_y=None, height=1)
        with separator.canvas.before:
            Color(0.8, 0.8, 0.8, 1)
            separator.line = Rectangle(size=separator.size, pos=separator.pos)
        separator.bind(
            size=lambda i, v: setattr(i.line, 'size', i.size),
            pos=lambda i, v: setattr(i.line, 'pos', i.pos)
        )
        menu.add_widget(separator)

        # === Menu Items ===
        menu_items = [
            ('🏠 Trang chủ', 'home'),
            ('📝 Luyện đề', 'practice'),
            ('👤 Tài khoản', 'account'),
            ('🚪 Đăng xuất', 'logout')
        ]

        for text, action in menu_items:
            btn = Button(
                text=text,
                size_hint_y=None,
                height=dp(50),
                background_color=(1, 1, 1, 0),
                color=(0.2, 0.2, 0.2, 1),
                font_size='16sp',
                halign='left',
                valign='middle'
            )
            btn.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width - 20, None)))
            btn.bind(on_press=lambda instance, act=action: self.handle_menu_click(act))
            menu.add_widget(btn)

        return menu

    def handle_menu_click(self, action):
        """Xử lý khi click vào menu item"""
        self.close_menu()
        if self.on_menu_action:
            self.on_menu_action(action)

    def toggle_menu(self):
        """Mở/đóng menu"""
        if self.menu_open:
            self.close_menu()
        else:
            self.open_menu()

    def open_menu(self):
        """Mở menu với animation"""
        self.menu_open = True

        # Animation menu trượt vào
        anim_menu = Animation(pos_hint={'x': 0, 'y': 0}, duration=0.3, t='out_cubic')
        anim_menu.start(self.menu_panel)

        # Animation overlay xuất hiện
        anim_overlay = Animation(opacity=1, duration=0.3)
        anim_overlay.start(self.overlay)

    def close_menu(self):
        """Đóng menu với animation"""
        if not self.menu_open:
            return

        self.menu_open = False

        # Animation menu trượt ra
        anim_menu = Animation(pos_hint={'x': -1, 'y': 0}, duration=0.3, t='out_cubic')
        anim_menu.start(self.menu_panel)

        # Animation overlay biến mất
        anim_overlay = Animation(opacity=0, duration=0.3)
        anim_overlay.start(self.overlay)

    def close_menu_on_overlay(self, instance, touch):
        """Đóng menu khi click vào overlay"""
        if self.menu_open and self.overlay.collide_point(*touch.pos):
            self.close_menu()
            return True
        return False

    def reset_menu(self):
        """Reset trạng thái menu (dùng khi chuyển màn hình)"""
        self.menu_open = False
        self.menu_panel.pos_hint = {'x': -1, 'y': 0}
        self.overlay.opacity = 0

    def update_user_info(self, user_data):
        """Cập nhật thông tin user trong menu"""
        self.user_data = user_data
        if user_data:
            # Cập nhật tên
            full_name = user_data.get('fullName', 'Bạn')
            self.menu_user_label.text = f'Xin chào, {full_name}!'

            # Cập nhật avatar
            import os
            avatar_path = user_data.get('avatar', '')
            if avatar_path and os.path.exists(avatar_path):
                self.avatar_box.circle.source = avatar_path
            else:
                # Avatar mặc định theo giới tính
                gender = user_data.get('gender', 'Nam')
                default_avatar = 'src/assets/Avt/nam.png' if gender == 'Nam' else 'src/assets/Avt/nu.png'
                if os.path.exists(default_avatar):
                    self.avatar_box.circle.source = default_avatar

    # === Utility Functions ===

    def _update_menu_bg(self, instance, value):
        if hasattr(instance, 'bg'):
            instance.bg.pos = instance.pos
            instance.bg.size = instance.size

    def _update_overlay_bg(self, instance, value):
        if hasattr(instance, 'bg'):
            instance.bg.pos = instance.pos
            instance.bg.size = instance.size

    def _update_avatar_circle(self, instance, value):
        if hasattr(instance, 'circle'):
            instance.circle.pos = instance.pos
            instance.circle.size = instance.size