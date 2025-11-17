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
        self.duration = 30  # fallback duration

    def set_exam(self, exam_data):
        """Thiết lập dữ liệu cho bài thi"""
        exam_info = exam_data.get("exam", {})
        self.exam_id = exam_info.get("id_ex")
        self.exam_name = exam_info.get("name_ex", "Bài thi")
        self.total_questions = exam_info.get("total_ques") or len(exam_data.get('questions', []))
        self.duration = exam_info.get("duration", 30)
        self.questions = exam_data.get("questions", [])
        self.answers = {}
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(minutes=self.duration)

        if not self.questions:
            self.load_all_questions()
        else:
            # Schedule để đảm bảo KV đã build xong
            Clock.schedule_once(lambda dt: self.display_all_questions({
                'exam': exam_info,
                'questions': self.questions
            }), 0)

        self.start_timer()

    def start_timer(self):
        """Bắt đầu đếm thời gian"""

        def update_timer(dt):
            now = datetime.now()
            if now >= self.end_time:
                if self.timer_event:
                    self.timer_event.cancel()
                self.ids.timer_label.text = "⏱️ HẾT GIỜ!"
                self.auto_submit()
            else:
                remaining = self.end_time - now
                minutes = int(remaining.total_seconds() // 60)
                seconds = int(remaining.total_seconds() % 60)
                self.ids.timer_label.text = f"⏱️ Thời gian còn lại: {minutes:02d}:{seconds:02d}"

                if minutes < 2:
                    self.ids.timer_label.text_color = (1, 0, 0, 1)
                else:
                    self.ids.timer_label.text_color = (1, 1, 0, 1)

        self.timer_event = Clock.schedule_interval(update_timer, 1)

    def load_all_questions(self):
        """Lấy câu hỏi từ backend"""
        try:
            token = self.get_token()
            if not token:
                self.show_error_dialog("Lỗi", "Token không hợp lệ!")
                return

            res = requests.get(
                f"{API_URL}/exams/{self.exam_id}/detail",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            data = res.json()
            if res.status_code == 200 and data.get('success'):
                self.questions = data.get('questions', [])
                Clock.schedule_once(lambda dt: self.display_all_questions(data), 0)
            else:
                self.show_error_dialog("Lỗi", data.get('message', 'Không tải được câu hỏi'))
        except Exception as e:
            logging.error(f"Error loading questions: {e}")
            self.show_error_dialog("Lỗi", f"Lỗi khi tải câu hỏi: {str(e)}")

    def display_all_questions(self, data):
        """Hiển thị tất cả câu hỏi"""
        exam_info = data.get('exam', {})
        questions = data.get('questions', [])

        self.total_questions = len(questions)
        if hasattr(self.ids, 'exam_name_label'):
            self.ids.exam_name_label.text = exam_info.get('name_ex', 'Bài thi')
            self.ids.progress_label.text = f"Tổng số câu: {self.total_questions}"

        container = self.ids.questions_container
        container.clear_widgets()
        self.question_widgets = []

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

        header = MDLabel(
            text=f"[b]Câu {question_number}:[/b]",
            markup=True,
            font_style='H6',
            size_hint_y=None,
            height=dp(30)
        )
        card.add_widget(header)

        question_text = MDLabel(
            text=question.get('ques_text', ''),
            font_style='Body1',
            size_hint_y=None,
            height=dp(50),
            adaptive_height=True
        )
        card.add_widget(question_text)

        for opt in ['a', 'b', 'c', 'd']:
            ans = question.get(f"ans_{opt}")
            if ans:
                answer_box = MDCard(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=dp(40),
                    padding=dp(5)
                )
                checkbox = MDCheckbox(
                    size_hint=(None, None),
                    size=(dp(40), dp(40)),
                    group=f"q_{question.get('id_ques')}"
                )
                checkbox.bind(
                    active=lambda cb, val, qid=question.get('id_ques'), answer=ans:
                    self.on_answer_selected(qid, answer, val)
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
        if is_active:
            self.answers[question_id] = answer
            answered = len(self.answers)
            if hasattr(self.ids, 'progress_label'):
                self.ids.progress_label.text = f"Tổng số câu: {answered}/{self.total_questions}"
            print(f"✅ Answered Q{question_id}: {answer}")

    def scroll_to_top(self):
        self.ids.scroll_view.scroll_y = 1

    def confirm_submit(self):
        answered = len(self.answers)
        if answered < self.total_questions:
            message = f"Bạn mới trả lời {answered}/{self.total_questions} câu.\nBạn có chắc muốn nộp bài?"
        else:
            message = f"Bạn đã hoàn thành {answered}/{self.total_questions} câu.\nNộp bài ngay?"

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
        self.show_error_dialog("Hết giờ", "Thời gian làm bài đã hết. Hệ thống sẽ tự động nộp bài.")
        Clock.schedule_once(lambda dt: self.submit_exam(), 2)

    def submit_exam(self):
        if self.dialog:
            self.dialog.dismiss()

        if self.timer_event:
            self.timer_event.cancel()

        try:
            token = self.get_token()
            if not token:
                self.show_error_dialog("Lỗi 401", "Bạn chưa đăng nhập hoặc token không hợp lệ.")
                return

            if not self.exam_id:
                self.show_error_dialog("Lỗi", "Không có thông tin đề thi")
                return

            answers_list = [
                {"id_ques": qid, "answer": ans}
                for qid, ans in self.answers.items()
            ]

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            res = requests.post(
                f"{API_URL}/exams/{self.exam_id}/submit",
                json={
                    "answers": answers_list,
                    "start_time": self.start_time.isoformat()
                },
                headers=headers,
                timeout=10
            )

            try:
                data = res.json()
            except Exception:
                data = {"success": False, "message": "Backend không trả dữ liệu hợp lệ"}

            if res.status_code == 200 and data.get('success'):
                result = data.get('result')
                result_screen = self.manager.get_screen('exam_result')
                result_screen.display_result(result)
                self.manager.current = 'exam_result'
            elif res.status_code == 401:
                self.show_error_dialog("Lỗi 401", "Token hết hạn hoặc không hợp lệ. Vui lòng đăng nhập lại.")
            else:
                msg = data.get('message', f"Nộp bài thất bại ({res.status_code})")
                self.show_error_dialog("Lỗi", msg)

        except Exception as e:
            logging.error(f"Error submitting exam: {e}")
            self.show_error_dialog("Lỗi", f"Lỗi khi nộp bài: {str(e)}")

    def on_leave(self):
        if self.timer_event:
            self.timer_event.cancel()

    def get_token(self):
        try:
            from kivy.storage.jsonstore import JsonStore
            store = JsonStore('user.json')
            if store.exists('auth'):
                auth_data = store.get('auth')
                return auth_data.get('token')
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
            buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
        )
        self.dialog.open()