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
                text: 'Chọn bài kiểm tra'
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

                # Department selection
                MDCard:
                    orientation: 'vertical'
                    spacing: dp(8)
                    padding: dp(15)
                    size_hint_y: None
                    height: dp(100)
                    elevation: 2
                    radius: [15, 15, 15, 15]

                    MDLabel:
                        text: 'Chọn môn:'
                        size_hint_y: None
                        height: dp(30)
                        font_style: 'Subtitle1'
                        bold: True

                    MDRaisedButton:
                        id: department_button
                        text: 'Chọn môn...'
                        size_hint_x: 1
                        size_hint_y: None
                        height: dp(48)
                        on_release: root.show_department_menu()

                # Class selection
                MDCard:
                    orientation: 'vertical'
                    spacing: dp(8)
                    padding: dp(15)
                    size_hint_y: None
                    height: dp(100)
                    elevation: 2
                    radius: [15, 15, 15, 15]

                    MDLabel:
                        text: 'Chọn lớp:'
                        size_hint_y: None
                        height: dp(30)
                        font_style: 'Subtitle1'
                        bold: True

                    MDRaisedButton:
                        id: class_button
                        text: 'Chọn lớp...'
                        size_hint_x: 1
                        size_hint_y: None
                        height: dp(48)
                        disabled: True
                        on_release: root.show_class_menu()

                # Exam selection
                MDCard:
                    orientation: 'vertical'
                    spacing: dp(8)
                    padding: dp(15)
                    size_hint_y: None
                    height: dp(100)
                    elevation: 2
                    radius: [15, 15, 15, 15]

                    MDLabel:
                        text: 'Chọn đề thi:'
                        size_hint_y: None
                        height: dp(30)
                        font_style: 'Subtitle1'
                        bold: True

                    MDRaisedButton:
                        id: exam_button
                        text: 'Chọn đề thi...'
                        size_hint_x: 1
                        size_hint_y: None
                        height: dp(48)
                        disabled: True
                        on_release: root.show_exam_menu()


        # Action buttons
        MDBoxLayout:
            orientation: 'vertical'
            spacing: dp(10)
            size_hint_y: None
            height: dp(110)
            opacity: 0 if root.is_loading else 1
            disabled: root.is_loading

            MDRaisedButton:
                text: 'Bắt đầu làm bài'
                size_hint_x: 1
                size_hint_y: None
                height: dp(50)
                md_bg_color: 0.2, 0.8, 0.2, 1
                on_release: root.start_exam()
""")


class ExamSetupScreen(MDScreen):
    selected_department_id = NumericProperty(0)
    selected_class_id = NumericProperty(0)
    selected_exam_id = NumericProperty(0)
    is_loading = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.departments = []
        self.classes = []
        self.exams = []
        self.department_menu = None
        self.class_menu = None
        self.exam_menu = None
        self.dialog = None

    def on_enter(self):
        self.load_departments()

    def set_loading(self, loading, message="Đang tải..."):
        self.is_loading = loading
        if loading and hasattr(self, 'ids') and 'loading_text' in self.ids:
            self.ids.loading_text.text = message

    def load_departments(self):
        self.set_loading(True, "Đang tải danh sách môn...")

        def _load():
            try:
                res = requests.get(f"{API_URL}/departments", timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    self.departments = data.get('departments', [])
                    print(f"✅ Loaded {len(self.departments)} departments")
                else:
                    print(f"❌ Failed to load departments: {res.text}")
                    Clock.schedule_once(
                        lambda dt: self.show_error_dialog("Lỗi", f"Không tải được danh sách môn: {res.status_code}"))
            except Exception as e:
                print(f"❌ Error: {e}")
                Clock.schedule_once(lambda dt: self.show_error_dialog("Lỗi", f"Lỗi khi tải dữ liệu: {str(e)}"))
            finally:
                Clock.schedule_once(lambda dt: self.set_loading(False))

        import threading
        threading.Thread(target=_load, daemon=True).start()

    def show_department_menu(self):
        if not self.departments:
            self.show_error_dialog("Thông báo", "Chưa có dữ liệu môn học")
            return

        menu_items = [
            {
                "text": dept['name_department'],
                "viewclass": "OneLineListItem",
                "on_release": lambda x=dept: self.select_department(x),
            } for dept in self.departments
        ]

        self.department_menu = MDDropdownMenu(
            caller=self.ids.department_button,
            items=menu_items,
            width_mult=4,
        )
        self.department_menu.open()

    def select_department(self, department):
        self.selected_department_id = department['id_department']
        self.ids.department_button.text = department['name_department']
        self.department_menu.dismiss()

        # Reset selections
        self.selected_class_id = 0
        self.selected_exam_id = 0
        self.ids.class_button.text = 'Chọn lớp...'
        self.ids.class_button.disabled = False
        self.ids.exam_button.text = 'Chọn đề thi...'
        self.ids.exam_button.disabled = True

        # Load classes
        self.load_classes(self.selected_department_id)

    def load_classes(self, dept_id):
        self.set_loading(True, "Đang tải danh sách lớp...")

        def _load():
            try:
                res = requests.get(f"{API_URL}/departments/{dept_id}/classes", timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    self.classes = data.get('classes', [])
                    print(f"✅ Loaded {len(self.classes)} classes")
                else:
                    Clock.schedule_once(
                        lambda dt: self.show_error_dialog("Lỗi", "Không tải được danh sách lớp"))
            except Exception as e:
                print(f"❌ Error: {e}")
                Clock.schedule_once(lambda dt: self.show_error_dialog("Lỗi", str(e)))
            finally:
                Clock.schedule_once(lambda dt: self.set_loading(False))

        import threading
        threading.Thread(target=_load, daemon=True).start()

    def show_class_menu(self):
        if not self.classes:
            self.show_error_dialog("Thông báo", "Chưa có dữ liệu lớp")
            return

        menu_items = [
            {
                "text": cls['class_name'],
                "viewclass": "OneLineListItem",
                "on_release": lambda x=cls: self.select_class(x),
            } for cls in self.classes
        ]

        self.class_menu = MDDropdownMenu(
            caller=self.ids.class_button,
            items=menu_items,
            width_mult=4,
        )
        self.class_menu.open()

    def select_class(self, cls):
        self.selected_class_id = cls['id_class']
        self.ids.class_button.text = cls['class_name']
        self.class_menu.dismiss()

        # Reset exam selection
        self.selected_exam_id = 0
        self.ids.exam_button.text = 'Chọn đề thi...'
        self.ids.exam_button.disabled = False

        # Load exams for this class
        self.load_exams(self.selected_class_id)
        print(f"✅ Selected class: {cls['class_name']}")

    def load_exams(self, class_id):
        """Tải danh sách đề thi có sẵn theo lớp"""
        self.set_loading(True, "Đang tải danh sách đề thi...")

        def _load():
            try:
                res = requests.get(f"{API_URL}/classes/{class_id}/exams", timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    self.exams = data.get('exams', [])
                    print(f"✅ Loaded {len(self.exams)} exams")

                    if len(self.exams) == 0:
                        Clock.schedule_once(
                            lambda dt: self.show_error_dialog("Thông báo", "Chưa có đề thi nào cho lớp này"))
                else:
                    Clock.schedule_once(
                        lambda dt: self.show_error_dialog("Lỗi", "Không tải được danh sách đề thi"))
            except Exception as e:
                print(f"❌ Error: {e}")
                Clock.schedule_once(lambda dt: self.show_error_dialog("Lỗi", str(e)))
            finally:
                Clock.schedule_once(lambda dt: self.set_loading(False))

        import threading
        threading.Thread(target=_load, daemon=True).start()

    def show_exam_menu(self):
        """Hiển thị menu chọn đề thi"""
        if not self.exams:
            self.show_error_dialog("Thông báo", "Chưa có đề thi nào cho lớp này")
            return

        menu_items = [
            {
                "text": f"{exam['name_ex']} ({exam['total_ques']} câu - {exam['duration']} phút)",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=exam: self.select_exam(x),
            } for exam in self.exams
        ]

        self.exam_menu = MDDropdownMenu(
            caller=self.ids.exam_button,
            items=menu_items,
            width_mult=5,
        )
        self.exam_menu.open()

    def select_exam(self, exam):
        """Chọn đề thi"""
        self.selected_exam_id = exam['id_ex']
        self.ids.exam_button.text = f"{exam['name_ex']} ({exam['total_ques']} câu)"
        self.exam_menu.dismiss()
        print(f"✅ Selected exam: {exam['name_ex']}")

    def start_exam(self):
        """Bắt đầu làm bài thi đã chọn theo đúng luồng backend"""
        if self.selected_department_id == 0:
            self.show_error_dialog("Lỗi", "Vui lòng chọn môn học!")
            return

        if self.selected_class_id == 0:
            self.show_error_dialog("Lỗi", "Vui lòng chọn lớp!")
            return

        if self.selected_exam_id == 0:
            self.show_error_dialog("Lỗi", "Vui lòng chọn đề thi!")
            return

        self.set_loading(True, "Đang tải đề thi...")

        def _load_exam():
            try:
                token = self.get_token()
                if not token:
                    Clock.schedule_once(lambda dt: self.show_error_dialog("Lỗi", "Bạn chưa đăng nhập!"))
                    return

                res = requests.get(
                    f"{API_URL}/exams/{self.selected_exam_id}/detail",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10
                )

                data = res.json()

                if res.status_code == 200 and data.get("success"):
                    exam_data = data  # chứa exam + questions

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
                Clock.schedule_once(lambda dt: self.show_error_dialog("Lỗi", str(e)))

            finally:
                Clock.schedule_once(lambda dt: self.set_loading(False))

        import threading
        threading.Thread(target=_load_exam, daemon=True).start()

    def go_back(self):
        self.manager.current = 'home'

    def get_token(self):
        try:
            from kivy.storage.jsonstore import JsonStore
            store = JsonStore('user.json')

            if store.exists("auth"):
                auth_data = store.get("auth")
                token = auth_data.get("token")
                if token and len(token.split(".")) == 3:
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