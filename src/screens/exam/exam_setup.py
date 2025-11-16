import requests
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFlatButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import NumericProperty, BooleanProperty
from kivy.clock import Clock
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

        # Loading Overlay
        MDCard:
            id: loading_overlay
            size_hint: 1, 1
            md_bg_color: 0, 0, 0, 0.7
            elevation: 10
            radius: [15, 15, 15, 15]
            opacity: 1 if root.is_loading else 0
            disabled: not root.is_loading

            MDBoxLayout:
                orientation: 'vertical'
                spacing: dp(20)
                padding: dp(40)
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                size_hint: None, None
                size: dp(200), dp(200)

                MDSpinner:
                    size_hint: None, None
                    size: dp(80), dp(80)
                    pos_hint: {'center_x': 0.5}
                    active: root.is_loading
                    color: 1, 1, 1, 1

                MDLabel:
                    id: loading_text
                    text: 'Đang tải...'
                    halign: 'center'
                    font_style: 'H6'
                    theme_text_color: 'Custom'
                    text_color: 1, 1, 1, 1

        # Content
        ScrollView:
            opacity: 0 if root.is_loading else 1
            disabled: root.is_loading

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
            opacity: 0 if root.is_loading else 1
            disabled: root.is_loading

            MDRaisedButton:
                text: '🚀 Bắt đầu làm bài'
                size_hint_x: 1
                size_hint_y: None
                height: dp(50)
                md_bg_color: 0.2, 0.8, 0.2, 1
                on_release: root.create_exam()
""")


class ExamSetupScreen(MDScreen):
    """Màn hình tạo bài kiểm tra mới"""

    selected_category_id = NumericProperty(0)
    selected_difficulty_id = NumericProperty(0)
    is_loading = BooleanProperty(False)

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

    def set_loading(self, loading, message="Đang tải..."):
        """Bật/tắt hiệu ứng loading"""
        self.is_loading = loading
        if loading and hasattr(self, 'ids') and 'loading_text' in self.ids:
            self.ids.loading_text.text = message

    def load_options(self):
        """Load categories và difficulties từ API - KHÔNG CẦN TOKEN"""
        self.set_loading(True, "Đang tải dữ liệu...")

        def _load():
            try:
                # Load categories - KHÔNG CẦN JWT TOKEN
                print(f"📡 Loading categories from: {API_URL}/categories")
                res = requests.get("https://backend-onlinesystem.onrender.com/api/categories/categories", timeout=5)

                print(f"📥 Categories response: {res.status_code}")

                if res.status_code == 200:
                    data = res.json()
                    self.categories = data.get('categories', [])
                    print(
                        f"✅ Loaded {len(self.categories)} categories: {[c['name_category'] for c in self.categories]}")
                else:
                    print(f"❌ Failed to load categories: {res.text}")
                    Clock.schedule_once(
                        lambda dt: self.show_error_dialog("Lỗi", f"Không tải được môn học: {res.status_code}"))

                # Load difficulties - KHÔNG CẦN JWT TOKEN
                print(f"📡 Loading difficulties from: {API_URL}/difficulty")
                res = requests.get(f"{API_URL}/difficulty", timeout=5)

                print(f"📥 Difficulties response: {res.status_code}")

                if res.status_code == 200:
                    data = res.json()
                    self.difficulties = data.get('difficulties', [])
                    print(
                        f"✅ Loaded {len(self.difficulties)} difficulties: {[d['difficulty'] for d in self.difficulties]}")
                else:
                    print(f"❌ Failed to load difficulties: {res.text}")
                    Clock.schedule_once(
                        lambda dt: self.show_error_dialog("Lỗi", f"Không tải được độ khó: {res.status_code}"))

            except requests.exceptions.RequestException as e:
                print(f"❌ Network error: {e}")
                Clock.schedule_once(
                    lambda dt: self.show_error_dialog("Lỗi kết nối", f"Không thể kết nối server: {str(e)}"))
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
                Clock.schedule_once(lambda dt: self.show_error_dialog("Lỗi", f"Không tải được dữ liệu: {str(e)}"))
            finally:
                Clock.schedule_once(lambda dt: self.set_loading(False))

        # Chạy trong thread để không block UI
        import threading
        threading.Thread(target=_load, daemon=True).start()

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

        self.set_loading(True, "Đang tạo đề thi...")

        def _create():
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

                    def _navigate(dt):
                        question_screen = self.manager.get_screen('exam_question')
                        question_screen.set_exam(exam_data)
                        self.manager.current = 'exam_question'

                    Clock.schedule_once(_navigate)
                else:
                    error_msg = data.get('message', 'Không tạo được đề thi')
                    print(f"❌ Create exam failed: {error_msg}")
                    Clock.schedule_once(lambda dt: self.show_error_dialog("Lỗi", error_msg))

            except requests.exceptions.RequestException as e:
                print(f"❌ Network error: {e}")
                Clock.schedule_once(
                    lambda dt: self.show_error_dialog("Lỗi kết nối", f"Không thể kết nối server: {str(e)}"))
            except Exception as e:
                print(f"❌ Error creating exam: {e}")
                import traceback
                traceback.print_exc()
                Clock.schedule_once(lambda dt: self.show_error_dialog("Lỗi", f"Lỗi khi tạo đề thi: {str(e)}"))
            finally:
                Clock.schedule_once(lambda dt: self.set_loading(False))

        # Chạy trong thread
        import threading
        threading.Thread(target=_create, daemon=True).start()


    def go_back(self):
        """Quay lại màn hình home"""
        self.manager.current = 'home'

    def get_token(self):
        """Lấy JWT token đã lưu khi login."""
        try:
            from kivy.storage.jsonstore import JsonStore
            store = JsonStore('user.json')

            if store.exists("auth"):
                auth_data = store.get("auth")
                token = auth_data.get("token")

                if token and len(token.split(".")) == 3:
                    # Token đúng format JWT
                    print(f"🔑 Loaded token: {token[:30]}...")
                    return token

                print("❌ Token trong auth không hợp lệ")
                return None

            print("❌ Không tìm thấy auth trong user.json")
            return None

        except Exception as e:
            print(f"❌ Error getting token: {e}")
            return None

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