import requests
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.spinner import MDSpinner
from kivy.uix.modalview import ModalView
from kivy.metrics import dp
from kivy.properties import NumericProperty, BooleanProperty
from kivy.clock import Clock
import threading

API_URL = "https://backend-onlinesystem.onrender.com/api/exam"


class ExamSetupScreen(MDScreen):
    selected_department_id = NumericProperty(0)
    selected_class_id = NumericProperty(0)
    selected_exam_id = NumericProperty(0)
    selected_difficulty = NumericProperty(1)  # Mặc định là 1 (Dễ)
    is_loading = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = (0.05, 0.08, 0.16, 1)
        self.departments = []
        self.classes = []
        self.exams = []
        self.department_menu = None
        self.class_menu = None
        self.exam_menu = None
        self.difficulty_menu = None
        self.dialog = None
        self.loading_modal = None
        self.difficulty_options = [
            {"id": 1, "name": "Dễ"},
            {"id": 2, "name": "Trung bình"},
            {"id": 3, "name": "Khó"}
        ]
        self._build_ui()

    def _build_ui(self):
        scroll = MDScrollView(size_hint=(1, 1))
        root_layout = MDBoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(20),
            size_hint_y=None
        )
        root_layout.bind(minimum_height=root_layout.setter('height'))

        # Header
        root_layout.add_widget(self._create_header())

        # Selection cards
        root_layout.add_widget(self._create_department_card())
        root_layout.add_widget(self._create_class_card())
        root_layout.add_widget(self._create_difficulty_card())  # Card độ khó mới
        root_layout.add_widget(self._create_exam_card())

        # Start button
        root_layout.add_widget(self._create_start_button())

        scroll.add_widget(root_layout)
        self.add_widget(scroll)

    def _create_header(self):
        header = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(60),
            spacing=dp(10)
        )

        back_btn = MDIconButton(
            icon="arrow-left",
            on_release=self.go_back,
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            icon_size=dp(28)
        )

        title_box = MDBoxLayout(orientation="vertical", spacing=dp(2))

        title = MDLabel(
            text="Chọn Bài Kiểm Tra",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_style="H5",
            bold=True,
            size_hint_y=None,
            height=dp(35)
        )

        subtitle = MDLabel(
            text="Chọn môn, lớp, độ khó và đề thi để bắt đầu",
            theme_text_color="Custom",
            text_color=(0.7, 0.75, 0.85, 1),
            font_style="Caption",
            size_hint_y=None,
            height=dp(20)
        )

        title_box.add_widget(title)
        title_box.add_widget(subtitle)

        header.add_widget(back_btn)
        header.add_widget(title_box)

        return header

    def _create_department_card(self):
        card = MDCard(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(12),
            size_hint_y=None,
            height=dp(120),
            radius=[20],
            md_bg_color=(0.98, 0.98, 0.99, 1),
            shadow_softness=8,
            elevation=4
        )

        label = MDLabel(
            text="Chọn môn học",
            theme_text_color="Custom",
            text_color=(0.15, 0.15, 0.2, 1),
            font_style="H6",
            bold=True,
            size_hint_y=None,
            height=dp(30)
        )

        self.department_button = MDRaisedButton(
            text="Chọn môn học...",
            md_bg_color=(0.18, 0.38, 0.78, 1),
            size_hint=(1, None),
            height=dp(50),
            elevation=2,
            on_release=lambda x: self.show_department_menu()
        )
        self.department_button.font_size = dp(15)

        card.add_widget(label)
        card.add_widget(self.department_button)

        return card

    def _create_class_card(self):
        card = MDCard(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(12),
            size_hint_y=None,
            height=dp(120),
            radius=[20],
            md_bg_color=(0.98, 0.98, 0.99, 1),
            shadow_softness=8,
            elevation=4
        )

        label = MDLabel(
            text="Chọn lớp học",
            theme_text_color="Custom",
            text_color=(0.15, 0.15, 0.2, 1),
            font_style="H6",
            bold=True,
            size_hint_y=None,
            height=dp(30)
        )

        self.class_button = MDRaisedButton(
            text="Chọn lớp học...",
            md_bg_color=(0.5, 0.5, 0.55, 1),
            size_hint=(1, None),
            height=dp(50),
            elevation=2,
            disabled=True,
            on_release=lambda x: self.show_class_menu()
        )
        self.class_button.font_size = dp(15)

        card.add_widget(label)
        card.add_widget(self.class_button)

        return card

    def _create_difficulty_card(self):
        """Card mới để chọn độ khó"""
        card = MDCard(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(12),
            size_hint_y=None,
            height=dp(120),
            radius=[20],
            md_bg_color=(0.98, 0.98, 0.99, 1),
            shadow_softness=8,
            elevation=4
        )

        label = MDLabel(
            text="Chọn độ khó",
            theme_text_color="Custom",
            text_color=(0.15, 0.15, 0.2, 1),
            font_style="H6",
            bold=True,
            size_hint_y=None,
            height=dp(30)
        )

        self.difficulty_button = MDRaisedButton(
            text="Dễ",
            md_bg_color=(0.5, 0.5, 0.55, 1),
            size_hint=(1, None),
            height=dp(50),
            elevation=2,
            disabled=True,
            on_release=lambda x: self.show_difficulty_menu()
        )
        self.difficulty_button.font_size = dp(15)

        card.add_widget(label)
        card.add_widget(self.difficulty_button)

        return card

    def _create_exam_card(self):
        card = MDCard(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(12),
            size_hint_y=None,
            height=dp(120),
            radius=[20],
            md_bg_color=(0.98, 0.98, 0.99, 1),
            shadow_softness=8,
            elevation=4
        )

        label = MDLabel(
            text="Chọn đề thi",
            theme_text_color="Custom",
            text_color=(0.15, 0.15, 0.2, 1),
            font_style="H6",
            bold=True,
            size_hint_y=None,
            height=dp(30)
        )

        self.exam_button = MDRaisedButton(
            text="Chọn đề thi...",
            md_bg_color=(0.5, 0.5, 0.55, 1),
            size_hint=(1, None),
            height=dp(50),
            elevation=2,
            disabled=True,
            on_release=lambda x: self.show_exam_menu()
        )
        self.exam_button.font_size = dp(15)

        card.add_widget(label)
        card.add_widget(self.exam_button)

        return card

    def _create_start_button(self):
        button = MDRaisedButton(
            text="Bắt đầu làm bài",
            md_bg_color=(0.2, 0.7, 0.3, 1),
            size_hint=(1, None),
            height=dp(55),
            elevation=4,
            on_release=lambda x: self.start_exam()
        )
        button.font_size = dp(17)
        return button

    def on_enter(self):
        self.load_departments()

    def show_loading(self, message="Đang tải..."):
        if self.loading_modal is None:
            self.loading_modal = ModalView(
                size_hint=(None, None),
                size=(dp(140), dp(140)),
                background_color=(0, 0, 0, 0.6),
                auto_dismiss=False
            )

            layout = MDBoxLayout(
                orientation="vertical",
                spacing=dp(15),
                padding=dp(25)
            )

            self.spinner = MDSpinner(
                size_hint=(None, None),
                size=(dp(55), dp(55)),
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                active=True,
                palette=[
                    [0.18, 0.38, 0.78, 1],
                    [0.28, 0.84, 0.60, 1],
                    [0.89, 0.36, 0.59, 1],
                    [0.96, 0.76, 0.19, 1],
                ]
            )

            self.loading_label = MDLabel(
                text=message,
                halign="center",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                font_style="Body2",
                bold=True
            )

            layout.add_widget(self.spinner)
            layout.add_widget(self.loading_label)
            self.loading_modal.add_widget(layout)

        self.loading_label.text = message
        self.loading_modal.open()

    def hide_loading(self):
        if self.loading_modal:
            self.loading_modal.dismiss()

    def load_departments(self):
        self.show_loading("Đang tải danh sách môn học...")

        def _load():
            try:
                res = requests.get(f"{API_URL}/departments", timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    self.departments = data.get('departments', [])
                    print(f"✅ Loaded {len(self.departments)} departments")
                else:
                    Clock.schedule_once(
                        lambda dt: self.show_error_dialog(
                            "Lỗi",
                            f"Không tải được danh sách môn học"
                        )
                    )
            except Exception as e:
                print(f"❌ Error: {e}")
                Clock.schedule_once(
                    lambda dt: self.show_error_dialog(
                        "Lỗi kết nối",
                        f"Không thể kết nối đến server:\n{str(e)}"
                    )
                )
            finally:
                Clock.schedule_once(lambda dt: self.hide_loading())

        threading.Thread(target=_load, daemon=True).start()

    def show_department_menu(self):
        if not self.departments:
            self.show_error_dialog("Thông báo", "Chưa có dữ liệu môn học.\nVui lòng thử lại sau.")
            return

        menu_items = [
            {
                "text": dept['name_department'],
                "viewclass": "OneLineListItem",
                "on_release": lambda x=dept: self.select_department(x),
            } for dept in self.departments
        ]

        self.department_menu = MDDropdownMenu(
            caller=self.department_button,
            items=menu_items,
            width_mult=4,
        )
        self.department_menu.open()

    def select_department(self, department):
        self.selected_department_id = department['id_department']
        self.department_button.text = department['name_department']
        self.department_menu.dismiss()

        # Reset selections
        self.selected_class_id = 0
        self.selected_difficulty = 1
        self.selected_exam_id = 0

        self.class_button.text = 'Chọn lớp học...'
        self.class_button.disabled = False
        self.class_button.md_bg_color = (0.18, 0.38, 0.78, 1)

        self.difficulty_button.text = 'Dễ'
        self.difficulty_button.disabled = True
        self.difficulty_button.md_bg_color = (0.5, 0.5, 0.55, 1)

        self.exam_button.text = 'Chọn đề thi...'
        self.exam_button.disabled = True
        self.exam_button.md_bg_color = (0.5, 0.5, 0.55, 1)

        # Load classes
        self.load_classes(self.selected_department_id)

    def load_classes(self, dept_id):
        self.show_loading("Đang tải danh sách lớp học...")

        def _load():
            try:
                res = requests.get(f"{API_URL}/departments/{dept_id}/classes", timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    self.classes = data.get('classes', [])
                    print(f"✅ Loaded {len(self.classes)} classes")
                else:
                    Clock.schedule_once(
                        lambda dt: self.show_error_dialog("Lỗi", "Không tải được danh sách lớp học")
                    )
            except Exception as e:
                print(f"❌ Error: {e}")
                Clock.schedule_once(
                    lambda dt: self.show_error_dialog("Lỗi", str(e))
                )
            finally:
                Clock.schedule_once(lambda dt: self.hide_loading())

        threading.Thread(target=_load, daemon=True).start()

    def show_class_menu(self):
        if not self.classes:
            self.show_error_dialog("Thông báo", "Chưa có lớp học nào.\nVui lòng chọn môn học khác.")
            return

        menu_items = [
            {
                "text": cls['class_name'],
                "viewclass": "OneLineListItem",
                "on_release": lambda x=cls: self.select_class(x),
            } for cls in self.classes
        ]

        self.class_menu = MDDropdownMenu(
            caller=self.class_button,
            items=menu_items,
            width_mult=4,
        )
        self.class_menu.open()

    def select_class(self, cls):
        self.selected_class_id = cls['id_class']
        self.class_button.text = cls['class_name']
        self.class_menu.dismiss()

        # Reset exam và difficulty selection
        self.selected_difficulty = 1
        self.selected_exam_id = 0

        self.difficulty_button.text = '😊 Dễ'
        self.difficulty_button.disabled = False
        self.difficulty_button.md_bg_color = (0.18, 0.38, 0.78, 1)

        self.exam_button.text = 'Chọn đề thi...'
        self.exam_button.disabled = True
        self.exam_button.md_bg_color = (0.5, 0.5, 0.55, 1)

        print(f"✅ Selected class: {cls['class_name']}")

    def show_difficulty_menu(self):
        """Hiển thị menu chọn độ khó"""
        menu_items = [
            {
                "text": f"{diff['name']}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=diff: self.select_difficulty(x),
            } for diff in self.difficulty_options
        ]

        self.difficulty_menu = MDDropdownMenu(
            caller=self.difficulty_button,
            items=menu_items,
            width_mult=4,
        )
        self.difficulty_menu.open()

    def select_difficulty(self, difficulty):
        """Xử lý khi chọn độ khó"""
        self.selected_difficulty = difficulty['id']
        self.difficulty_button.text = f"{difficulty['name']}"
        self.difficulty_menu.dismiss()

        # Reset exam selection
        self.selected_exam_id = 0
        self.exam_button.text = 'Chọn đề thi...'
        self.exam_button.disabled = False
        self.exam_button.md_bg_color = (0.18, 0.38, 0.78, 1)

        # Load exams với độ khó đã chọn
        self.load_exams(self.selected_class_id, self.selected_difficulty)
        print(f"✅ Selected difficulty: {difficulty['name']} (ID: {difficulty['id']})")

    def load_exams(self, class_id, difficulty=1):
        """Load đề thi theo class_id và difficulty"""
        self.show_loading("Đang tải danh sách đề thi...")

        def _load():
            try:
                # Gửi difficulty như một query parameter
                res = requests.get(
                    f"{API_URL}/classes/{class_id}/exams?difficulty={difficulty}",
                    timeout=10
                )
                if res.status_code == 200:
                    data = res.json()
                    self.exams = data.get('exams', [])
                    print(f"✅ Loaded {len(self.exams)} exams for difficulty {difficulty}")

                    if len(self.exams) == 0:
                        Clock.schedule_once(
                            lambda dt: self.show_error_dialog(
                                "Thông báo",
                                "Chưa có đề thi nào cho độ khó này.\nVui lòng chọn độ khó khác."
                            )
                        )
                else:
                    Clock.schedule_once(
                        lambda dt: self.show_error_dialog("Lỗi", "Không tải được danh sách đề thi")
                    )
            except Exception as e:
                print(f"❌ Error: {e}")
                Clock.schedule_once(lambda dt: self.show_error_dialog("Lỗi", str(e)))
            finally:
                Clock.schedule_once(lambda dt: self.hide_loading())

        threading.Thread(target=_load, daemon=True).start()

    def show_exam_menu(self):
        if not self.exams:
            self.show_error_dialog("Thông báo", "Chưa có đề thi nào.\nVui lòng chọn độ khó khác.")
            return

        menu_items = [
            {
                "text": f"{exam['name_ex']} - {exam['duration']} phút - {exam['total_ques']} câu",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=exam: self.select_exam(x),
            } for exam in self.exams
        ]

        self.exam_menu = MDDropdownMenu(
            caller=self.exam_button,
            items=menu_items,
            width_mult=5,
        )
        self.exam_menu.open()

    def select_exam(self, exam):
        self.selected_exam_id = exam['id_ex']
        self.exam_button.text = f"{exam['name_ex']} ({exam['total_ques']} câu)"
        self.exam_button.md_bg_color = (0.2, 0.7, 0.3, 1)
        self.exam_menu.dismiss()
        print(f"✅ Selected exam: {exam['name_ex']}")

    def start_exam(self):
        if self.selected_department_id == 0:
            self.show_error_dialog("Thiếu thông tin", "Vui lòng chọn môn học!")
            return

        if self.selected_class_id == 0:
            self.show_error_dialog("Thiếu thông tin", "Vui lòng chọn lớp học!")
            return

        if self.selected_exam_id == 0:
            self.show_error_dialog("Thiếu thông tin", "Vui lòng chọn đề thi!")
            return

        self.show_loading("Đang tải đề thi...")

        def _load_exam():
            try:
                token = self.get_token()
                if not token:
                    Clock.schedule_once(
                        lambda dt: self.show_error_dialog("Lỗi", "Bạn chưa đăng nhập!")
                    )
                    return

                res = requests.get(
                    f"{API_URL}/exams/{self.selected_exam_id}/detail",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=15
                )

                data = res.json()

                if res.status_code == 200 and data.get("success"):
                    exam_data = data

                    def _go(dt):
                        screen = self.manager.get_screen("exam_question")
                        screen.set_exam(exam_data)
                        self.manager.current = "exam_question"

                    Clock.schedule_once(_go)

                else:
                    msg = data.get("message", "Không tải được đề thi")
                    Clock.schedule_once(lambda dt: self.show_error_dialog("Lỗi", msg))

            except Exception as e:
                print("❌ Error:", e)
                Clock.schedule_once(
                    lambda dt: self.show_error_dialog("Lỗi", f"Không thể tải đề thi:\n{str(e)}")
                )

            finally:
                Clock.schedule_once(lambda dt: self.hide_loading())

        threading.Thread(target=_load_exam, daemon=True).start()

    def go_back(self, instance=None):
        self.manager.current = 'home'

    def get_token(self):
        try:
            from kivy.storage.jsonstore import JsonStore
            store = JsonStore('user.json')

            if store.exists("auth"):
                auth_data = store.get("auth")
                token = auth_data.get("token")

                if token:
                    token = token.strip()
                    parts = token.split(".")
                    if len(parts) == 3:
                        print("✅ Token hợp lệ")
                        return token
                    else:
                        print("❌ Token không đúng format JWT")
                else:
                    print("❌ Không tìm thấy token")
            else:
                print("❌ Chưa đăng nhập")

            return None
        except Exception as e:
            print(f"❌ Lỗi khi lấy token: {e}")
            return None

    def show_error_dialog(self, title, message):
        if self.dialog:
            self.dialog.dismiss()

        self.dialog = MDDialog(
            title=title,
            text=message,
            size_hint=(0.85, None),
            height=dp(220),
            buttons=[
                MDRaisedButton(
                    text="Đóng",
                    md_bg_color=(0.5, 0.5, 0.55, 1),
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()