import requests
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.clock import Clock
from datetime import datetime, timedelta
import logging

API_URL = "https://backend-onlinesystem.onrender.com/api/exam"

Builder.load_string("""
<ExamQuestionScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(15)
        spacing: dp(10)

        # Header Card with Timer
        MDCard:
            orientation: 'vertical'
            size_hint_y: None
            height: dp(110)
            padding: dp(15)
            elevation: 3
            md_bg_color: app.theme_cls.primary_color
            radius: [15, 15, 15, 15]

            MDLabel:
                id: exam_name_label
                text: ''
                font_style: 'H6'
                bold: True
                size_hint_y: None
                height: dp(30)
                theme_text_color: 'Custom'
                text_color: 1, 1, 1, 1

            MDLabel:
                id: timer_label
                text: '⏱️ Thời gian: --:--'
                font_style: 'H6'
                bold: True
                size_hint_y: None
                height: dp(30)
                theme_text_color: 'Custom'
                text_color: 1, 1, 0, 1

            MDLabel:
                id: progress_label
                text: 'Tổng số câu: 0'
                font_style: 'Subtitle1'
                size_hint_y: None
                height: dp(25)
                theme_text_color: 'Custom'
                text_color: 1, 1, 1, 0.9

        # Questions Container
        ScrollView:
            id: scroll_view

            MDBoxLayout:
                id: questions_container
                orientation: 'vertical'
                spacing: dp(20)
                padding: dp(10)
                size_hint_y: None
                height: self.minimum_height

        # Navigation Buttons
        MDBoxLayout:
            orientation: 'horizontal'
            spacing: dp(10)
            size_hint_y: None
            height: dp(50)

            MDRaisedButton:
                text: '⬆️ Lên đầu trang'
                size_hint_x: 0.5
                md_bg_color: 0.4, 0.6, 1, 1
                on_release: root.scroll_to_top()

            MDRaisedButton:
                text: '📤 Nộp bài'
                size_hint_x: 0.5
                md_bg_color: 0.8, 0.2, 0.2, 1
                on_release: root.confirm_submit()
""")


class ExamQuestionScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.exam_id = None
        self.exam_data = None
        self.total_questions = 0
        self.answers = {}
        self.start_time = None
        self.end_time = None
        self.timer_event = None
        self.dialog = None
        self.question_widgets = []

    def set_exam(self, exam_data):
        """Khởi tạo bài thi và load tất cả câu hỏi"""
        self.exam_data = exam_data
        self.exam_id = exam_data['id_ex']
        self.total_questions = exam_data['total_ques']
        self.answers = {}
        self.start_time = datetime.now()

        # Tính thời gian kết thúc (1 phút/câu)
        duration_minutes = exam_data['duration']
        self.end_time = self.start_time + timedelta(minutes=duration_minutes)

        # Load và hiển thị tất cả câu hỏi
        self.load_all_questions()

        # Bắt đầu đếm ngược
        self.start_timer()

    def start_timer(self):
        """Bắt đầu đếm thời gian"""

        def update_timer(dt):
            now = datetime.now()
            if now >= self.end_time:
                # Hết giờ - tự động nộp bài
                self.timer_event.cancel()
                self.ids.timer_label.text = "⏱️ HẾT GIỜ!"
                self.auto_submit()
            else:
                remaining = self.end_time - now
                minutes = int(remaining.total_seconds() // 60)
                seconds = int(remaining.total_seconds() % 60)
                self.ids.timer_label.text = f"⏱️ Thời gian còn lại: {minutes:02d}:{seconds:02d}"

                # Đổi màu cảnh báo khi còn 2 phút
                if minutes < 2:
                    self.ids.timer_label.text_color = (1, 0, 0, 1)

        self.timer_event = Clock.schedule_interval(update_timer, 1)

    def load_all_questions(self):
        """Load tất cả câu hỏi của bài thi"""
        try:
            token = self.get_token()
            res = requests.get(
                f"{API_URL}/exams/{self.exam_id}/detail",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )

            data = res.json()

            if res.status_code == 200 and data.get('success'):
                self.display_all_questions(data)
            else:
                self.show_error_dialog("Lỗi", data.get('message', 'Không tải được câu hỏi'))

        except Exception as e:
            logging.error(f"Error loading questions: {e}")
            self.show_error_dialog("Lỗi", f"Lỗi khi tải câu hỏi: {str(e)}")

    def display_all_questions(self, data):
        """Hiển thị tất cả câu hỏi"""
        questions = data['questions']
        exam_info = data['exam']

        # Update header
        self.ids.exam_name_label.text = exam_info['name_ex']
        self.ids.progress_label.text = f"Tổng số câu: {len(questions)}"

        # Clear container
        container = self.ids.questions_container
        container.clear_widgets()
        self.question_widgets = []

        # Display each question
        for idx, question in enumerate(questions):
            question_card = self.create_question_card(question, idx + 1)
            container.add_widget(question_card)
            self.question_widgets.append(question_card)

    def create_question_card(self, question, question_number):
        """Tạo card cho mỗi câu hỏi"""
        card = MDCard(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(10),
            size_hint_y=None,
            height=dp(300),
            elevation=3,
            radius=[15, 15, 15, 15]
        )

        # Question header
        header = MDLabel(
            text=f"[b]Câu {question_number}:[/b]",
            markup=True,
            font_style='H6',
            size_hint_y=None,
            height=dp(30)
        )
        card.add_widget(header)

        # Question text
        question_text = MDLabel(
            text=question['ques_text'],
            font_style='Body1',
            size_hint_y=None,
            height=dp(50),
            adaptive_height=True
        )
        card.add_widget(question_text)

        # Answer options
        for opt in ['a', 'b', 'c', 'd']:
            ans = question.get(f"ans_{opt}")
            if ans:
                answer_box = MDBoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=dp(40),
                    spacing=dp(10)
                )

                checkbox = MDCheckbox(
                    size_hint=(None, None),
                    size=(dp(40), dp(40)),
                    group=f"q_{question['id_ques']}"
                )

                checkbox.bind(
                    active=lambda cb, val, q_id=question['id_ques'], answer=ans:
                    self.on_answer_selected(q_id, answer, val)
                )

                label = MDLabel(
                    text=f"[b]{opt.upper()}.[/b] {ans}",
                    markup=True,
                    adaptive_height=True
                )

                answer_box.add_widget(checkbox)
                answer_box.add_widget(label)
                card.add_widget(answer_box)

        return card

    def on_answer_selected(self, question_id, answer, is_active):
        """Lưu câu trả lời"""
        if is_active:
            self.answers[question_id] = answer
            print(f"✅ Answered Q{question_id}: {answer}")

    def scroll_to_top(self):
        """Scroll lên đầu trang"""
        self.ids.scroll_view.scroll_y = 1

    def confirm_submit(self):
        """Xác nhận nộp bài"""
        answered = len(self.answers)
        if answered < self.total_questions:
            message = f"Bạn mới trả lời {answered}/{self.total_questions} câu.\\n\\nBạn có chắc muốn nộp bài?"
        else:
            message = f"Bạn đã hoàn thành {answered}/{self.total_questions} câu.\\n\\nNộp bài ngay?"

        if self.dialog:
            self.dialog.dismiss()

        self.dialog = MDDialog(
            title="Xác nhận nộp bài",
            text=message,
            buttons=[
                MDFlatButton(
                    text="Hủy",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Nộp bài",
                    md_bg_color=(0.8, 0.2, 0.2, 1),
                    on_release=lambda x: self.submit_exam()
                )
            ]
        )
        self.dialog.open()

    def auto_submit(self):
        """Tự động nộp bài khi hết giờ"""
        self.show_error_dialog("Hết giờ", "Thời gian làm bài đã hết. Hệ thống sẽ tự động nộp bài.")
        Clock.schedule_once(lambda dt: self.submit_exam(), 2)

    def submit_exam(self):
        """Nộp bài thi"""
        if self.dialog:
            self.dialog.dismiss()

        # Hủy timer
        if self.timer_event:
            self.timer_event.cancel()

        try:
            token = self.get_token()

            answers_list = [
                {"id_ques": qid, "answer": ans}
                for qid, ans in self.answers.items()
            ]

            res = requests.post(
                f"{API_URL}/exam/submit",
                json={
                    "exam_id": self.exam_id,
                    "answers": answers_list,
                    "start_time": self.start_time.isoformat()
                },
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )

            data = res.json()

            if res.status_code == 200 and data.get('success'):
                result = data.get('result')
                result_screen = self.manager.get_screen('exam_result')
                result_screen.display_result(result)
                self.manager.current = 'exam_result'
            else:
                self.show_error_dialog("Lỗi", data.get('message', 'Nộp bài thất bại'))

        except Exception as e:
            logging.error(f"Error submitting exam: {e}")
            self.show_error_dialog("Lỗi", f"Lỗi khi nộp bài: {str(e)}")

    def on_leave(self):
        """Cleanup khi rời màn hình"""
        if self.timer_event:
            self.timer_event.cancel()

    def get_token(self):
        try:
            from kivy.storage.jsonstore import JsonStore
            store = JsonStore('user.json')

            if store.exists('auth'):
                auth_data = store.get('auth')
                token = auth_data.get('token')
                if token:
                    return token

            return None
        except Exception as e:
            print(f"❌ Error getting token: {e}")
            return None

    def show_error_dialog(self, title, message):
        if self.dialog:
            self.dialog.dismiss()

        self.dialog = MDDialog(
            title=title,
            text=message,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()