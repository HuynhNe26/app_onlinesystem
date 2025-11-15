from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Ellipse
from kivy.metrics import dp
from kivy.clock import Clock


class LoadingWidget(FloatLayout):
    def __init__(self, message="Đang xử lý...", spinner_color=None, **kwargs):
        super().__init__(**kwargs)

        if spinner_color is None:
            spinner_color = (0.12, 0.56, 1, 1)  # Xanh dương mặc định

        # Background overlay (nền đen mờ)
        with self.canvas.before:
            Color(0, 0, 0, 0.7)
            self.loading_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size
            )

        self.bind(
            pos=lambda obj, val: setattr(self.loading_rect, 'pos', val),
            size=lambda obj, val: setattr(self.loading_rect, 'size', val)
        )

        # Container trắng giữa màn hình
        container = BoxLayout(
            orientation='vertical',
            spacing=dp(20),
            size_hint=(None, None),
            size=(dp(200), dp(200)),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        with container.canvas.before:
            Color(1, 1, 1, 1)
            self.container_rect = RoundedRectangle(
                pos=container.pos,
                size=container.size,
                radius=[15]
            )

        container.bind(
            pos=lambda obj, val: setattr(self.container_rect, 'pos', val),
            size=lambda obj, val: setattr(self.container_rect, 'size', val)
        )

        # Spinner (vòng tròn xoay)
        spinner_widget = Widget(size_hint=(None, None), size=(dp(60), dp(60)))

        with spinner_widget.canvas:
            Color(*spinner_color)
            self.spinner = Ellipse(
                pos=spinner_widget.pos,
                size=spinner_widget.size,
                angle_start=0,
                angle_end=270
            )

        spinner_widget.bind(
            pos=lambda obj, val: setattr(self.spinner, 'pos', val),
            size=lambda obj, val: setattr(self.spinner, 'size', val)
        )

        # Animation cho spinner (xoay mượt)
        def rotate_spinner(dt):
            if hasattr(self, 'spinner'):
                self.spinner.angle_start = (self.spinner.angle_start + 10) % 360
                self.spinner.angle_end = (self.spinner.angle_end + 10) % 360

        self.spinner_event = Clock.schedule_interval(rotate_spinner, 1 / 60.0)

        # Label text
        self.loading_label = Label(
            text=message,
            font_size='16sp',
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=dp(30)
        )

        # Ghép các widget lại
        spinner_box = BoxLayout(size_hint_y=None, height=dp(60))
        spinner_box.add_widget(Widget())
        spinner_box.add_widget(spinner_widget)
        spinner_box.add_widget(Widget())

        container.add_widget(Widget())
        container.add_widget(spinner_box)
        container.add_widget(self.loading_label)
        container.add_widget(Widget())

        self.add_widget(container)

    def update_message(self, new_message):
        """Cập nhật text loading"""
        self.loading_label.text = new_message

    def stop(self):
        """Dừng animation khi remove widget"""
        if hasattr(self, 'spinner_event'):
            self.spinner_event.cancel()


# ==========================================
# CÁC STYLE LOADING KHÁC NHAU
# ==========================================

class LoadingDots(FloatLayout):
    """Loading kiểu 3 chấm nhảy (... animation)"""

    def __init__(self, message="Đang tải", **kwargs):
        super().__init__(**kwargs)

        # Background
        with self.canvas.before:
            Color(0, 0, 0, 0.7)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size)

        self.bind(
            pos=lambda obj, val: setattr(self.bg_rect, 'pos', val),
            size=lambda obj, val: setattr(self.bg_rect, 'size', val)
        )

        # Label với animation
        self.loading_label = Label(
            text=f"{message}",
            font_size='18sp',
            color=(1, 1, 1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        self.add_widget(self.loading_label)

        # Animation cho dấu chấm
        self.base_message = message
        self.dot_count = 0

        def update_dots(dt):
            self.dot_count = (self.dot_count + 1) % 4
            dots = "." * self.dot_count
            self.loading_label.text = f"{self.base_message}{dots}"

        self.dots_event = Clock.schedule_interval(update_dots, 0.5)

    def stop(self):
        if hasattr(self, 'dots_event'):
            self.dots_event.cancel()


class LoadingBar(FloatLayout):
    """Loading kiểu thanh tiến trình"""

    def __init__(self, message="Đang tải...", **kwargs):
        super().__init__(**kwargs)

        # Background
        with self.canvas.before:
            Color(0, 0, 0, 0.7)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size)

        self.bind(
            pos=lambda obj, val: setattr(self.bg_rect, 'pos', val),
            size=lambda obj, val: setattr(self.bg_rect, 'size', val)
        )

        # Container
        container = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            size_hint=(None, None),
            size=(dp(250), dp(120)),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )

        with container.canvas.before:
            Color(1, 1, 1, 1)
            self.container_rect = RoundedRectangle(
                pos=container.pos,
                size=container.size,
                radius=[15]
            )

        container.bind(
            pos=lambda obj, val: setattr(self.container_rect, 'pos', val),
            size=lambda obj, val: setattr(self.container_rect, 'size', val)
        )

        # Label
        container.add_widget(Widget(size_hint_y=0.3))
        container.add_widget(Label(
            text=message,
            font_size='16sp',
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=dp(30)
        ))

        # Progress bar background
        bar_container = Widget(size_hint_y=None, height=dp(8))

        with bar_container.canvas:
            # Nền xám
            Color(0.9, 0.9, 0.9, 1)
            self.bar_bg = RoundedRectangle(
                pos=(bar_container.x + dp(20), bar_container.center_y - dp(4)),
                size=(dp(210), dp(8)),
                radius=[4]
            )
            # Thanh xanh chạy
            Color(0.12, 0.56, 1, 1)
            self.progress_bar = RoundedRectangle(
                pos=(bar_container.x + dp(20), bar_container.center_y - dp(4)),
                size=(0, dp(8)),
                radius=[4]
            )

        self.progress_width = 0

        def update_bar(dt):
            self.progress_width = (self.progress_width + 5) % 210
            self.progress_bar.size = (self.progress_width, dp(8))

        self.bar_event = Clock.schedule_interval(update_bar, 1 / 60.0)

        bar_container.bind(
            pos=lambda obj, val: self.update_bar_pos(),
            size=lambda obj, val: self.update_bar_pos()
        )

        container.add_widget(bar_container)
        container.add_widget(Widget(size_hint_y=0.3))

        self.add_widget(container)
        self.bar_container = bar_container

    def update_bar_pos(self):
        self.bar_bg.pos = (self.bar_container.x + dp(20), self.bar_container.center_y - dp(4))
        self.progress_bar.pos = (self.bar_container.x + dp(20), self.bar_container.center_y - dp(4))

    def stop(self):
        if hasattr(self, 'bar_event'):
            self.bar_event.cancel()