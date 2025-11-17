import requests
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import BooleanProperty
from kivy.clock import Clock
import logging

API_URL = "https://backend-onlinesystem.onrender.com/api/exam"

Builder.load_string("""
<ExamDetailScreen>:
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
                text: 'Chi tiết bài làm'
                font_style: 'H5'
                halign: 'center'
                bold: True

            Widget:
                size_hint_x: None
                width: dp(50)

        ScrollView:
            MDBoxLayout:
                id: detail_layout
                orientation: 'vertical'
                spacing: dp(15)
                padding: dp(5)
                size_hint_y: None
                height: self.minimum_height
""")


class ExamDetailScreen(MDScreen):
    is_loading = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.result_data = None

    def load_result_detail(self, result_id):
        self.is_loading = True

        def _load():
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
                    answers = data.get("answers", [])
                    Clock.schedule_once(lambda dt: self.display_detail(result, answers))
                else:
                    Clock.schedule_once(lambda dt: self.show_error_dialog("Lỗi", data.get("message", "Không tải được chi tiết")))
            except Exception as e:
                logging.error(f"Error loading detail: {e}")
                Clock.schedule_once(lambda dt: self.show_error_dialog("Lỗi", str(e)))
            finally:
                Clock.schedule_once(lambda dt: setattr(self, "is_loading", False))

        import threading
        threading.Thread(target=_load, daemon=True).start()

    def display_detail(self, result, answers):
        self.result_data = result
        layout = self.ids.detail_layout
        layout.clear_widgets()

        header = MDLabel(
            text=f"📖 {result.get('exam_name', 'Đề thi')} - Điểm: {result.get('score',0)}/100",
            font_style='H6',
            bold=True,
            size_hint_y=None,
            height=dp(30)
        )
        layout.add_widget(header)

        correct_label = MDLabel(
            text=f"Số câu đúng: {result.get('total_correct',0)}/{result.get('total_questions',0)}",
            font_style='Subtitle1',
            size_hint_y=None,
            height=dp(25)
        )
        layout.add_widget(correct_label)

        # Chi tiết từng câu
        for idx, ans in enumerate(answers):
            is_correct = ans.get('user_answer') == ans.get('correct_ans')
            bg_color = [0.2,0.8,0.2,0.15] if is_correct else [0.8,0.2,0.2,0.15]
            border_color = [0.2,0.8,0.2,1] if is_correct else [0.8,0.2,0.2,1]
            icon = "Đúng" if is_correct else "Sai"

            card = MDCard(
                orientation='vertical',
                padding=dp(15),
                spacing=dp(10),
                size_hint_y=None,
                elevation=3,
                radius=[15]*4,
                md_bg_color=bg_color
            )

            card.add_widget(MDLabel(
                text=f"{icon} [b]Câu {idx+1}:[/b]",
                markup=True,
                font_style='H6',
                size_hint_y=None,
                height=dp(30)
            ))
            card.add_widget(MDLabel(
                text=ans.get('ques_text',''),
                font_style='Body1',
                size_hint_y=None,
                adaptive_height=True
            ))
            card.add_widget(MDLabel(
                text=f"[b]Câu trả lời của bạn:[/b] {ans.get('user_answer','Chưa trả lời')}",
                markup=True,
                font_style='Body2',
                size_hint_y=None,
                height=dp(25),
                theme_text_color='Custom',
                text_color=border_color
            ))
            if not is_correct:
                card.add_widget(MDLabel(
                    text=f"[b]Đáp án đúng:[/b] {ans.get('correct_ans')}",
                    markup=True,
                    font_style='Body2',
                    size_hint_y=None,
                    height=dp(25),
                    theme_text_color='Custom',
                    text_color=[0.2,0.8,0.2,1]
                ))
            layout.add_widget(card)

    def get_token(self):
        try:
            from kivy.storage.jsonstore import JsonStore
            store = JsonStore('user.json')
            if store.exists('auth'):
                return store.get('auth').get('token')
            return None
        except:
            return None

    def go_back(self):
        self.manager.current = 'exam_history'

    def show_error_dialog(self, title, message):
        if self.dialog:
            self.dialog.dismiss()
        self.dialog = MDDialog(
            title=title,
            text=message,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
        )
        self.dialog.open()
