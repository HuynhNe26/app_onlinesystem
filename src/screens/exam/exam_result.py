import requests
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivy.lang import Builder
from kivy.metrics import dp
import logging

API_URL = "https://backend-onlinesystem.onrender.com/api/exam"

Builder.load_string("""
<ExamResultScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(15)

        # Header
        MDBoxLayout:
            size_hint_y: None
            height: dp(60)
            MDIconButton:
                icon: 'arrow-left'
                on_release: root.go_back()
                size_hint_x: None
                width: dp(50)
            MDLabel:
                text: 'Kết quả bài thi'
                font_style: 'H5'
                halign: 'center'
                bold: True
            Widget:
                size_hint_x: None
                width: dp(50)

        MDBoxLayout:
            orientation: 'vertical'
            spacing: dp(10)
            id: result_layout
""")


class ExamResultScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.result_data = None

    def load_result(self, result_id):
        """Load thông tin bài làm vừa hoàn thành"""
        try:
            token = self.get_token()
            if not token:
                raise Exception("Chưa đăng nhập")

            res = requests.get(
                f"{API_URL}/result/{result_id}/detail",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            data = res.json()
            if res.status_code == 200 and data.get("success"):
                result = data.get("result")
                self.result_data = result
                self.display_result(result)
            else:
                self.show_error_dialog("Lỗi", data.get("message", "Không tải được kết quả"))
        except Exception as e:
            logging.error(f"Error loading result: {e}")
            self.show_error_dialog("Lỗi", str(e))

    def display_result(self, result):
        layout = self.ids.result_layout
        layout.clear_widgets()

        card = MDCard(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(15),
            size_hint_y=None,
            height=dp(200),
            elevation=4,
            radius=[15]*4
        )

        # Exam name
        card.add_widget(MDLabel(
            text=f"📖 {result.get('exam_name','Đề thi')}",
            font_style='H6',
            bold=True,
            size_hint_y=None,
            height=dp(30)
        ))

        # Score
        score = result.get("score",0)
        score_color = [0.2,0.8,0.2,1] if score>=80 else [0.2,0.6,1,1] if score>=50 else [0.8,0.2,0.2,1]
        card.add_widget(MDLabel(
            text=f"Điểm: {score}/100",
            font_style='H5',
            theme_text_color='Custom',
            text_color=score_color,
            size_hint_y=None,
            height=dp(35)
        ))

        # Correct answers
        card.add_widget(MDLabel(
            text=f"Số câu đúng: {result.get('total_correct',0)}/{result.get('total_questions',0)}",
            font_style='Subtitle1',
            size_hint_y=None,
            height=dp(25)
        ))

        # Buttons
        button_layout = self.create_buttons(result.get("id_result"))
        card.add_widget(button_layout)

        layout.add_widget(card)

    def create_buttons(self, result_id):
        from kivymd.uix.boxlayout import MDBoxLayout
        box = MDBoxLayout(spacing=dp(15), size_hint_y=None, height=dp(50))
        view_btn = MDRaisedButton(
            text="Xem chi tiết",
            md_bg_color=[0.2,0.6,1,1],
            on_release=lambda x: self.view_detail(result_id)
        )
        home_btn = MDRaisedButton(
            text="Quay lại",
            md_bg_color=[0.6,0.6,0.6,1],
            on_release=lambda x: self.go_back()
        )
        box.add_widget(view_btn)
        box.add_widget(home_btn)
        return box

    def view_detail(self, result_id):
        try:
            detail_screen = self.manager.get_screen('exam_detail')
            detail_screen.load_result_detail(result_id)
            self.manager.current = 'exam_detail'
        except Exception as e:
            logging.error(f"Error opening detail: {e}")
            self.show_error_dialog("Lỗi", str(e))

    def go_back(self):
        self.manager.current = 'home'

    def get_token(self):
        try:
            from kivy.storage.jsonstore import JsonStore
            store = JsonStore('user.json')
            if store.exists('auth'):
                return store.get('auth').get('token')
            return None
        except:
            return None

    def show_error_dialog(self, title, message):
        if self.dialog:
            self.dialog.dismiss()
        self.dialog = MDDialog(
            title=title,
            text=message,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
        )
        self.dialog.open()
