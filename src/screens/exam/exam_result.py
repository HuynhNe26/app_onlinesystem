from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.metrics import dp
import logging

# KV Layout embedded
Builder.load_string("""
<ExamResultScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(20)

        # Header
        MDLabel:
            text: 'Kết quả bài thi'
            font_style: 'H4'
            halign: 'center'
            bold: True
            size_hint_y: None
            height: dp(60)

        # Score Card
        MDCard:
            orientation: 'vertical'
            padding: dp(30)
            spacing: dp(15)
            size_hint_y: None
            height: dp(350)
            elevation: 8
            radius: [20, 20, 20, 20]
            md_bg_color: app.theme_cls.primary_color

            MDLabel:
                id: score_label
                text: '0'
                font_style: 'H1'
                halign: 'center'
                bold: True
                size_hint_y: None
                height: dp(90)
                theme_text_color: 'Custom'
                text_color: 1, 1, 1, 1

            MDLabel:
                text: 'điểm'
                font_style: 'H5'
                halign: 'center'
                size_hint_y: None
                height: dp(35)
                theme_text_color: 'Custom'
                text_color: 1, 1, 1, 0.9

            MDLabel:
                id: message_label
                text: ''
                font_style: 'H5'
                halign: 'center'
                bold: True
                size_hint_y: None
                height: dp(45)
                theme_text_color: 'Custom'
                text_color: 1, 1, 1, 1

            MDSeparator:
                size_hint_y: None
                height: dp(2)

            MDLabel:
                id: correct_label
                text: ''
                font_style: 'H6'
                halign: 'center'
                size_hint_y: None
                height: dp(35)
                theme_text_color: 'Custom'
                text_color: 1, 1, 1, 0.95

            MDLabel:
                id: percentage_label
                text: ''
                font_style: 'H6'
                halign: 'center'
                size_hint_y: None
                height: dp(35)
                theme_text_color: 'Custom'
                text_color: 1, 1, 1, 0.95

            MDLabel:
                id: exam_name_label
                text: ''
                font_style: 'Subtitle1'
                halign: 'center'
                size_hint_y: None
                height: dp(30)
                theme_text_color: 'Custom'
                text_color: 1, 1, 1, 0.9

        # Action Buttons
        MDBoxLayout:
            orientation: 'vertical'
            spacing: dp(10)
            size_hint_y: None
            height: dp(170)

            MDRaisedButton:
                text: 'Làm bài mới'
                size_hint_x: 1
                size_hint_y: None
                height: dp(50)
                md_bg_color: 0.2, 0.8, 0.2, 1
                on_release: root.try_again()

            MDFlatButton:
                text: 'Xem lịch sử'
                size_hint_x: 1
                size_hint_y: None
                height: dp(50)
                on_release: root.view_history()

            MDFlatButton:
                text: 'Về trang chủ'
                size_hint_x: 1
                size_hint_y: None
                height: dp(50)
                on_release: root.go_home()
""")


class ExamResultScreen(MDScreen):
    """Màn hình hiển thị kết quả bài thi"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.result_data = None

    def display_result(self, result):
        """Hiển thị kết quả bài thi"""
        self.result_data = result

        # Update score
        score = result['score']
        self.ids.score_label.text = f"{score}"

        # Update score color and message based on score
        if score >= 80:
            self.ids.score_label.text_color = (0.2, 0.8, 0.2, 1)
            message = "🎉 Xuất sắc!"
        elif score >= 50:
            self.ids.score_label.text_color = (0.2, 0.6, 1, 1)
            message = "👍 Đạt yêu cầu!"
        else:
            self.ids.score_label.text_color = (0.8, 0.2, 0.2, 1)
            message = "😔 Chưa đạt. Cố gắng lần sau!"

        self.ids.message_label.text = message

        # Update details
        self.ids.correct_label.text = f"Số câu đúng: {result['total_correct']}/{result['total_questions']}"
        self.ids.exam_name_label.text = f"Môn: {result['exam_name']}"

        # Calculate percentage
        percentage = round((result['total_correct'] / result['total_questions']) * 100)
        self.ids.percentage_label.text = f"Tỷ lệ đúng: {percentage}%"

        logging.info(f"Result displayed: Score={score}")

    def go_home(self):
        """Quay về màn hình home"""
        self.manager.current = 'home'

    def view_history(self):
        """Xem lịch sử bài thi"""
        try:
            history_screen = self.manager.get_screen('exam_history')
            history_screen.load_history()
            self.manager.current = 'exam_history'
        except Exception as e:
            logging.error(f"Error navigating to history: {e}")

    def try_again(self):
        """Làm bài mới"""
        self.manager.current = 'exam_setup'