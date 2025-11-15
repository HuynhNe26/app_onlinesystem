import requests
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.lang import Builder
from kivy.metrics import dp
from datetime import datetime
import logging

API_URL = "https://backend-onlinesystem.onrender.com/api/exam"

# KV Layout embedded
Builder.load_string("""
<ExamQuestionScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(15)
        spacing: dp(10)

        # Header Card
        MDCard:
            orientation: 'vertical'
            size_hint_y: None
            height: dp(90)
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
                id: progress_label
                text: 'Câu 1/10'
                font_style: 'Subtitle1'
                size_hint_y: None
                height: dp(25)
                theme_text_color: 'Custom'
                text_color: 1, 1, 1, 0.9

        # Question Content
        ScrollView:
            MDBoxLayout:
                orientation: 'vertical'
                spacing: dp(15)
                padding: dp(10)
                size_hint_y: None
                height: self.minimum_height

                # Question Text Card
                MDCard:
                    orientation: 'vertical'
                    padding: dp(20)
                    size_hint_y: None
                    height: self.minimum_height
                    elevation: 2
                    radius: [10, 10, 10, 10]

                    MDLabel:
                        id: question_text
                        text: ''
                        font_style: 'H6'
                        size_hint_y: None
                        height: self.texture_size[1]
                        markup: True

                # Answer Options Container
                MDBoxLayout:
                    id: answer_layout
                    orientation: 'vertical'
                    spacing: dp(10)
                    size_hint_y: None
                    height: self.minimum_height

        # Navigation Buttons
        MDBoxLayout:
            orientation: 'horizontal'
            spacing: dp(10)
            size_hint_y: None
            height: dp(50)

            MDRaisedButton:
                id: prev_button
                text: '← Trước'
                size_hint_x: 0.4
                on_release: root.previous_question()

            MDRaisedButton:
                id: next_button
                text: 'Tiếp theo'
                size_hint_x: 0.6
                md_bg_color: app.theme_cls.primary_color
                on_release: root.next_question()
""")


class ExamQuestionScreen(MDScreen):
    """Màn hình hiển thị từng câu hỏi"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.exam_id = None
        self.current_index = 0
        self.total_questions = 0
        self.answers = {}
        self.start_time = None
        self.current_question = None
        self.dialog = None

    def set_exam(self, exam_data):
        """Khởi tạo dữ liệu bài thi"""
        self.exam_id = exam_data['id_ex']
        self.total_questions = exam_data['total_ques']
        self.current_index = 0
        self.answers = {}
        self.start_time = datetime.now().isoformat()
        self.load_question()

    def load_question(self):
        """Tải câu hỏi hiện tại từ API"""
        try:
            token = self.get_token()
            res = requests.get(
                f"{API_URL}/exam/{self.exam_id}/question/{self.current_index}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5
            )

            data = res.json()

            if res.status_code == 200 and data.get('success'):
                self.display_question(data)
            else:
                self.show_error_dialog("Lỗi", data.get('message', 'Không tải được câu hỏi'))

        except Exception as e:
            logging.error(f"Error loading question: {e}")
            self.show_error_dialog("Lỗi", f"Lỗi khi tải câu hỏi: {str(e)}")

    def display_question(self, data):
        """Hiển thị câu hỏi lên màn hình"""
        self.current_question = data['question']
        exam_info = data['exam_info']
        is_last = data['is_last']

        # Update progress
        self.ids.progress_label.text = f"Câu {self.current_index + 1}/{self.total_questions}"
        self.ids.exam_name_label.text = exam_info['name_ex']

        # Display question text
        self.ids.question_text.text = self.current_question['ques_text']

        # Clear previous answers
        answer_layout = self.ids.answer_layout
        answer_layout.clear_widgets()

        # Display answer options
        for opt in ['a', 'b', 'c', 'd']:
            ans = self.current_question.get(f"ans_{opt}")
            if ans:
                card = MDCard(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=dp(70),
                    padding=dp(15),
                    spacing=dp(10),
                    elevation=2,
                    radius=[10, 10, 10, 10]
                )

                checkbox = MDCheckbox(
                    size_hint=(None, None),
                    size=(dp(48), dp(48)),
                    group=f"q_{self.current_question['id_ques']}"
                )

                # Check if already answered
                if (self.current_question['id_ques'] in self.answers and
                        self.answers[self.current_question['id_ques']] == ans):
                    checkbox.active = True

                checkbox.bind(
                    active=lambda cb, val, ans=ans: self.on_answer_selected(ans, val)
                )

                label = MDLabel(
                    text=f"[b]{opt.upper()}.[/b] {ans}",
                    markup=True,
                    adaptive_height=True,
                    theme_text_color="Primary"
                )

                card.add_widget(checkbox)
                card.add_widget(label)
                answer_layout.add_widget(card)

        # Update navigation buttons
        self.ids.prev_button.disabled = (self.current_index == 0)

        if is_last:
            self.ids.next_button.text = "Nộp bài"
            self.ids.next_button.md_bg_color = (0.8, 0.2, 0.2, 1)
        else:
            self.ids.next_button.text = "Tiếp theo"
            self.ids.next_button.md_bg_color = self.theme_cls.primary_color

    def on_answer_selected(self, answer, is_active):
        """Lưu câu trả lời được chọn"""
        if is_active:
            self.answers[self.current_question['id_ques']] = answer

    def previous_question(self):
        """Quay lại câu trước"""
        if self.current_index > 0:
            self.current_index -= 1
            self.load_question()

    def next_question(self):
        """Chuyển sang câu tiếp theo hoặc nộp bài"""
        if self.current_index < self.total_questions - 1:
            self.current_index += 1
            self.load_question()
        else:
            self.confirm_submit()

    def confirm_submit(self):
        """Xác nhận nộp bài"""
        if len(self.answers) < self.total_questions:
            message = f"Bạn mới trả lời {len(self.answers)}/{self.total_questions} câu.\\n\\nBạn có chắc muốn nộp bài?"
        else:
            message = "Bạn đã hoàn thành tất cả câu hỏi.\\n\\nNộp bài ngay?"

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

    def submit_exam(self):
        """Nộp bài thi"""
        if self.dialog:
            self.dialog.dismiss()

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
                    "start_time": self.start_time
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

    def get_token(self):
        """Lấy token từ storage - FIXED VERSION"""
        try:
            from kivy.storage.jsonstore import JsonStore
            store = JsonStore('user.json')

            # Cách 1: Token lưu riêng trong key 'token'
            if store.exists('token'):
                token_data = store.get('token')
                token = token_data.get('access_token')
                if token:
                    print(f"✅ Token found: {token[:20]}...")  # Debug
                    return token

            # Cách 2: Token lưu trong key 'user'
            if store.exists('user'):
                user_data = store.get('user')
                token = user_data.get('token') or user_data.get('access_token')
                if token:
                    print(f"✅ Token found in user: {token[:20]}...")  # Debug
                    return token

            print("⚠️ No token found, using demo_token")
            return "demo_token"

        except Exception as e:
            print(f"❌ Error getting token: {e}")
            return "demo_token"

    def show_error_dialog(self, title, message):
        """Hiển thị dialog lỗi"""
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