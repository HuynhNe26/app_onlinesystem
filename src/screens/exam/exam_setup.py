import requests
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFlatButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import NumericProperty
import logging

API_URL = "https://backend-onlinesystem.onrender.com/api/exam"

Builder.load_string("""
<ExamSetupScreen>:
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
                text: 'Tạo bài kiểm tra mới'
                font_style: 'H5'
                halign: 'center'
                bold: True

        # Content
        ScrollView:
            MDBoxLayout:
                orientation: 'vertical'
                spacing: dp(20)
                padding: dp(10)
                size_hint_y: None
                height: self.minimum_height

                # Category selection
                MDCard:
                    orientation: 'vertical'
                    spacing: dp(8)
                    padding: dp(15)
                    size_hint_y: None
                    height: dp(100)
                    elevation: 2
                    radius: [15, 15, 15, 15]

                    MDLabel:
                        text: '📚 Chọn môn học:'
                        size_hint_y: None
                        height: dp(30)
                        font_style: 'Subtitle1'
                        bold: True

                    MDRaisedButton:
                        id: category_button
                        text: 'Chọn môn...'
                        size_hint_x: 1
                        size_hint_y: None
                        height: dp(48)
                        on_release: root.show_category_menu()

                # Difficulty selection
                MDCard:
                    orientation: 'vertical'
                    spacing: dp(8)
                    padding: dp(15)
                    size_hint_y: None
                    height: dp(100)
                    elevation: 2
                    radius: [15, 15, 15, 15]

                    MDLabel:
                        text: '⚡ Chọn độ khó:'
                        size_hint_y: None
                        height: dp(30)
                        font_style: 'Subtitle1'
                        bold: True

                    MDRaisedButton:
                        id: difficulty_button
                        text: 'Chọn độ khó...'
                        size_hint_x: 1
                        size_hint_y: None
                        height: dp(48)
                        on_release: root.show_difficulty_menu()

                # Number of questions
                MDCard:
                    orientation: 'vertical'
                    spacing: dp(8)
                    padding: dp(15)
                    size_hint_y: None
                    height: dp(100)
                    elevation: 2
                    radius: [15, 15, 15, 15]

                    MDLabel:
                        text: '🔢 Số lượng câu hỏi:'
                        size_hint_y: None
                        height: dp(30)
                        font_style: 'Subtitle1'
                        bold: True

                    MDTextField:
                        id: num_questions_field
                        text: '10'
                        input_filter: 'int'
                        mode: 'rectangle'
                        size_hint_y: None
                        height: dp(48)

                # Info box
                MDCard:
                    orientation: 'vertical'
                    padding: dp(15)
                    spacing: dp(8)
                    size_hint_y: None
                    height: dp(120)
                    elevation: 2
                    md_bg_color: app.theme_cls.primary_color
                    radius: [15, 15, 15, 15]

                    MDLabel:
                        text: '📝 Lưu ý:'
                        font_style: 'Subtitle1'
                        bold: True
                        size_hint_y: None
                        height: dp(25)
                        theme_text_color: 'Custom'
                        text_color: 1, 1, 1, 1

                    MDLabel:
                        text: '• Thời gian làm bài: 1 phút/câu\\n• Mỗi câu hỏi hiển thị trên 1 trang\\n• Bạn có thể quay lại câu trước'
                        font_style: 'Caption'
                        size_hint_y: None
                        height: dp(70)
                        theme_text_color: 'Custom'
                        text_color: 1, 1, 1, 0.9

        # Action buttons
        MDBoxLayout:
            orientation: 'vertical'
            spacing: dp(10)
            size_hint_y: None
            height: dp(110)

            MDRaisedButton:
                text: '🚀 Bắt đầu làm bài'
                size_hint_x: 1
                size_hint_y: None
                height: dp(50)
                md_bg_color: 0.2, 0.8, 0.2, 1
                on_release: root.create_exam()

            MDFlatButton:
                text: '📊 Xem lịch sử'
                size_hint_x: 1
                size_hint_y: None
                height: dp(50)
                on_release: root.view_history()
""")


class ExamSetupScreen(MDScreen):
    """Màn hình tạo bài kiểm tra mới"""

    selected_category_id = NumericProperty(0)
    selected_difficulty_id = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.categories = []
        self.difficulties = []
        self.category_menu = None
        self.difficulty_menu = None
        self.dialog = None

    def on_enter(self):
        """Load dữ liệu khi vào màn hình"""
        self.load_options()

    def load_options(self):
        """Load categories và difficulties từ API - KHÔNG CẦN TOKEN"""
        try:
            # Load categories - KHÔNG CẦN JWT TOKEN
            print(f"📡 Loading categories from: {API_URL}/categories")
            res = requests.get(f"{API_URL}/categories", timeout=5)

            print(f"📥 Categories response: {res.status_code}")

            if res.status_code == 200:
                data = res.json()
                self.categories = data.get('categories', [])
                print(f"✅ Loaded {len(self.categories)} categories: {[c['name_category'] for c in self.categories]}")
            else:
                print(f"❌ Failed to load categories: {res.text}")
                self.show_error_dialog("Lỗi", f"Không tải được môn học: {res.status_code}")

            # Load difficulties - KHÔNG CẦN JWT TOKEN
            print(f"📡 Loading difficulties from: {API_URL}/difficulty")
            res = requests.get(f"{API_URL}/difficulty", timeout=5)

            print(f"📥 Difficulties response: {res.status_code}")

            if res.status_code == 200:
                data = res.json()
                self.difficulties = data.get('difficulties', [])
                print(f"✅ Loaded {len(self.difficulties)} difficulties: {[d['difficulty'] for d in self.difficulties]}")
            else:
                print(f"❌ Failed to load difficulties: {res.text}")
                self.show_error_dialog("Lỗi", f"Không tải được độ khó: {res.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            self.show_error_dialog("Lỗi kết nối", f"Không thể kết nối server: {str(e)}")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_dialog("Lỗi", f"Không tải được dữ liệu: {str(e)}")

    def show_category_menu(self):
        """Hiển thị menu chọn môn học"""
        if not self.categories:
            self.show_error_dialog("Thông báo", "Chưa có dữ liệu môn học")
            return

        menu_items = [
            {
                "text": cat['name_category'],
                "viewclass": "OneLineListItem",
                "on_release": lambda x=cat: self.select_category(x),
            } for cat in self.categories
        ]

        self.category_menu = MDDropdownMenu(
            caller=self.ids.category_button,
            items=menu_items,
            width_mult=4,
        )
        self.category_menu.open()

    def select_category(self, category):
        """Chọn môn học"""
        self.selected_category_id = category['id_category']
        self.ids.category_button.text = category['name_category']
        self.category_menu.dismiss()
        print(f"✅ Selected category: {category['name_category']}")

    def show_difficulty_menu(self):
        """Hiển thị menu chọn độ khó"""
        if not self.difficulties:
            self.show_error_dialog("Thông báo", "Chưa có dữ liệu độ khó")
            return

        menu_items = [
            {
                "text": diff['difficulty'],
                "viewclass": "OneLineListItem",
                "on_release": lambda x=diff: self.select_difficulty(x),
            } for diff in self.difficulties
        ]

        self.difficulty_menu = MDDropdownMenu(
            caller=self.ids.difficulty_button,
            items=menu_items,
            width_mult=4,
        )
        self.difficulty_menu.open()

    def select_difficulty(self, difficulty):
        """Chọn độ khó"""
        self.selected_difficulty_id = difficulty['id_diff']
        self.ids.difficulty_button.text = difficulty['difficulty']
        self.difficulty_menu.dismiss()
        print(f"✅ Selected difficulty: {difficulty['difficulty']}")

    def create_exam(self):
        """Tạo đề thi và chuyển sang màn hình làm bài"""
        # Validate input
        if self.selected_category_id == 0:
            self.show_error_dialog("Lỗi", "Vui lòng chọn môn học!")
            return

        if self.selected_difficulty_id == 0:
            self.show_error_dialog("Lỗi", "Vui lòng chọn độ khó!")
            return

        try:
            num_questions = int(self.ids.num_questions_field.text)
            if num_questions <= 0:
                raise ValueError()
        except:
            self.show_error_dialog("Lỗi", "Số câu hỏi phải là số nguyên dương!")
            return

        try:
            token = self.get_token()

            payload = {
                "category_id": self.selected_category_id,
                "difficulty_id": self.selected_difficulty_id,
                "num_questions": num_questions
            }

            print(f"📤 Creating exam with payload: {payload}")
            print(f"🔑 Using token: {token[:30]}..." if token else "No token")

            res = requests.post(
                f"{API_URL}/exam/create",
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )

            print(f"📥 Create exam response: {res.status_code}")

            data = res.json()
            print(f"📥 Response data: {data}")

            if res.status_code == 200 and data.get('success'):
                exam_data = data.get('exam')
                print(f"✅ Exam created: ID={exam_data['id_ex']}")

                question_screen = self.manager.get_screen('exam_question')
                question_screen.set_exam(exam_data)
                self.manager.current = 'exam_question'
            else:
                error_msg = data.get('message', 'Không tạo được đề thi')
                print(f"❌ Create exam failed: {error_msg}")
                self.show_error_dialog("Lỗi", error_msg)

        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            self.show_error_dialog("Lỗi kết nối", f"Không thể kết nối server: {str(e)}")
        except Exception as e:
            print(f"❌ Error creating exam: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_dialog("Lỗi", f"Lỗi khi tạo đề thi: {str(e)}")

    def view_history(self):
        """Chuyển sang màn hình lịch sử"""
        try:
            history_screen = self.manager.get_screen('exam_history')
            history_screen.load_history()
            self.manager.current = 'exam_history'
        except Exception as e:
            print(f"❌ Error navigating to history: {e}")
            self.show_error_dialog("Lỗi", "Không thể mở lịch sử")

    def go_back(self):
        """Quay lại màn hình home"""
        self.manager.current = 'home'

    def get_token(self):
        """Lấy token từ storage"""
        try:
            from kivy.storage.jsonstore import JsonStore
            store = JsonStore('user.json')

            # Cách 1: Token lưu riêng trong key 'token'
            if store.exists('token'):
                token_data = store.get('token')
                token = token_data.get('access_token')
                if token:
                    print(f"✅ Token found in 'token' key")
                    return token

            # Cách 2: Token lưu trong user
            if store.exists('user'):
                user_data = store.get('user')
                token = user_data.get('token') or user_data.get('access_token')
                if token:
                    print(f"✅ Token found in 'user' key")
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