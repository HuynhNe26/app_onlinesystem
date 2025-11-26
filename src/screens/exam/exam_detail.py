import requests
import logging
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.lang import Builder
from kivy.metrics import dp

from kivy.clock import Clock
import threading

API_URL = "https://backend-onlinesystem.onrender.com/api/exam"

KV = """
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

        # Summary Card
        MDCard:
            id: summary_card
            orientation: 'vertical'
            padding: dp(15)
            spacing: dp(8)
            size_hint_y: None
            height: dp(160)
            elevation: 3
            md_bg_color: app.theme_cls.primary_color
            radius: [15, 15, 15, 15]

            MDLabel:
                id: summary_title
                text: ''
                font_style: 'H6'
                bold: True
                theme_text_color: 'Custom'
                text_color: 1, 1, 1, 1
                size_hint_y: None
                height: dp(30)

            MDLabel:
                id: summary_score
                text: ''
                font_style: 'H5'
                theme_text_color: 'Custom'
                text_color: 1, 1, 1, 1
                size_hint_y: None
                height: dp(35)

            MDLabel:
                id: summary_correct
                text: ''
                font_style: 'Subtitle1'
                theme_text_color: 'Custom'
                text_color: 1, 1, 1, 0.95
                size_hint_y: None
                height: dp(25)

            MDLabel:
                id: summary_date
                text: ''
                font_style: 'Caption'
                theme_text_color: 'Custom'
                text_color: 1, 1, 1, 0.9
                size_hint_y: None
                height: dp(20)

        # Detail list
        ScrollView:

            MDBoxLayout:
                id: detail_layout
                orientation: 'vertical'
                spacing: dp(15)
                padding: dp(5)
                size_hint_y: None
                height: self.minimum_height
"""

Builder.load_string(KV)


class ExamDetailScreen(MDScreen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None
        self.result_data = None

    def load_result_detail(self, result_id, from_screen='exam_result'):
        self.from_screen = from_screen

        def _load():
            try:
                token = self.get_token()
                if not token:
                    Clock.schedule_once(lambda dt: self.show_error_dialog("Lỗi", "Bạn chưa đăng nhập"))
                    return

                res = requests.get(
                    f"{API_URL}/result/{result_id}/detail",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10
                )
                if res.status_code != 200:
                    try:
                        msg = res.json().get('message', res.text)
                    except Exception:
                        msg = res.text
                    Clock.schedule_once(lambda dt: self.show_error_dialog("Lỗi", msg))
                    return

                data = res.json()
                if not data.get('success'):
                    Clock.schedule_once(lambda dt: self.show_error_dialog("Lỗi", data.get('message', 'Lỗi server')))
                    return

                self.result_data = data.get('result')
                answers = data.get('answers', [])
                Clock.schedule_once(lambda dt: self.display_detail(self.result_data, answers))

            except Exception as e:
                logging.error(f"Error loading detail: {e}")
                Clock.schedule_once(lambda dt: self.show_error_dialog("Lỗi", str(e)))

        threading.Thread(target=_load, daemon=True).start()

    def display_detail(self, result, answers):
        self.ids.summary_title.text = result.get('exam_cat', 'Kết quả')
        self.ids.summary_score.text = f"Điểm: {result.get('score', 0)}/100"
        total_q = result.get('total_questions') or result.get('total_ques') or result.get('total_ques', 0)
        self.ids.summary_correct.text = f"Số câu đúng: {result.get('total_correct', 0)}/{total_q}"

        try:
            date_str = str(result.get('completed_time', ''))[:19]
            self.ids.summary_date.text = f"{date_str}"
        except Exception:
            self.ids.summary_date.text = "N/A"

        detail_layout = self.ids.detail_layout
        detail_layout.clear_widgets()

        for idx, answer in enumerate(answers):
            card = self.create_answer_card(answer, idx + 1)
            detail_layout.add_widget(card)

    def create_answer_card(self, answer, question_number):
        is_correct = bool(answer.get('is_correct'))

        if is_correct:
            bg_color = [0.2, 0.8, 0.2, 0.12]
            border_color = [0.2, 0.8, 0.2, 1]
        else:
            bg_color = [0.95, 0.85, 0.85, 1]
            border_color = [0.8, 0.2, 0.2, 1]

        card = MDCard(
            orientation='vertical',
            padding=dp(12),
            spacing=dp(8),
            size_hint_y=None,
            elevation=3,
            radius=[12, 12, 12, 12],
            md_bg_color=bg_color
        )

        header = MDLabel(
            text=f"[b]Câu {question_number}:[/b]",
            markup=True,
            font_style='H6',
            size_hint_y=None,
            height=dp(28)
        )
        card.add_widget(header)

        question_text = MDLabel(
            text=answer.get('ques_text', ''),
            font_style='Body1',
            size_hint_y=None,
            adaptive_height=True
        )
        card.add_widget(question_text)

        user_answer_label = MDLabel(
            text=f"[b]Câu trả lời của bạn:[/b] {answer.get('answer', 'Chưa trả lời')}",
            markup=True,
            font_style='Body2',
            size_hint_y=None,
            height=dp(26),
            theme_text_color='Custom',
            text_color=border_color
        )
        card.add_widget(user_answer_label)

        if not is_correct:
            correct_answer_label = MDLabel(
                text=f"[b]Đáp án đúng:[/b] {answer.get('correct_ans', '')}",
                markup=True,
                font_style='Body2',
                size_hint_y=None,
                height=dp(26),
                theme_text_color='Custom',
                text_color=[0.2, 0.8, 0.2, 1]
            )
            card.add_widget(correct_answer_label)

        if answer.get('explanation'):
            explanation_label = MDLabel(
                text=f"[b] Giải thích:[/b] {answer.get('explanation')}",
                markup=True,
                font_style='Caption',
                size_hint_y=None,
                adaptive_height=True
            )
            card.add_widget(explanation_label)

        # compute height (rough)
        h = dp(40) + dp(30)
        if not is_correct:
            h += dp(28)
        if answer.get('explanation'):
            h += dp(50)
        card.height = h + dp(20)
        return card

    def go_back(self):
        """Quay lại màn hình kết quả hoặc lịch sử"""
        if getattr(self, 'from_screen', '') == 'exam_history':
            self.manager.current = 'exam_history'
        else:
            self.manager.current = 'exam_result'

    def get_token(self):
        try:
            from kivy.storage.jsonstore import JsonStore
            store = JsonStore('user.json')

            for key in ('auth', 'token', 'user'):
                if store.exists(key):
                    d = store.get(key)
                    token = d.get('token') or d.get('access_token') or d.get('auth') if isinstance(d, dict) else d
                    if token:
                        return token

            return None
        except Exception as e:
            logging.error(f"Error getting token: {e}")
            return None

    def show_error_dialog(self, title, message):
        if self.dialog:
            self.dialog.dismiss()
        self.dialog = MDDialog(
            title=title,
            text=str(message),
            buttons=[
                MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())
            ]
        )
        self.dialog.open()