import requests
import logging
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.storage.jsonstore import JsonStore
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout

API_URL = "https://backend-onlinesystem.onrender.com/api/users"

Builder.load_string("""
<PersonalInfoScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(15)

        MDBoxLayout:
            size_hint_y: None
            height: dp(60)

            MDIconButton:
                icon: 'arrow-left'
                on_release: root.go_back()
                size_hint_x: None
                width: dp(50)

            MDLabel:
                text: 'Thông tin cá nhân'
                font_style: 'H5'
                halign: 'center'
                bold: True

            MDIconButton:
                icon: 'refresh'
                on_release: root.refresh_info()
                size_hint_x: None
                width: dp(50)

        ScrollView:
            MDBoxLayout:
                id: info_layout
                orientation: 'vertical'
                spacing: dp(15)
                padding: dp(5)
                size_hint_y: None
                height: self.minimum_height
""")

class PersonalInfoScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "personal_info"

        self.name_field = None
        self.email_field = None
        self.dob_field = None
        self.gender_field = None
        self.old_pass_field = None
        self.new_pass_field = None

        store = JsonStore('user.json')
        self.user_id = store.get('auth')['user'].get('id_user') if store.exists('auth') else None

    def on_enter(self):
        self.load_info()

    def load_info(self):
        layout = self.ids.info_layout
        layout.clear_widgets()

        if not self.user_id:
            layout.add_widget(MDLabel(text="❌ Chưa đăng nhập, không có id_user"))
            return
        try:
            res = requests.get(f"{API_URL}/{self.user_id}", timeout=5)
            if res.status_code != 200:
                layout.add_widget(MDLabel(text=f"❌ Server trả về {res.status_code}: {res.text}"))
                return
            data = res.json()
            if data.get('success'):
                self.display_info(data['data'])
            else:
                layout.add_widget(MDLabel(text=f"❌ {data.get('message', 'Không tải được thông tin')}"))
        except Exception as e:
            logging.error(f"Error loading info: {e}")
            layout.add_widget(MDLabel(text=f"❌ Lỗi: {str(e)}"))

    def display_info(self, user):
        layout = self.ids.info_layout
        layout.clear_widgets()

        card = MDCard(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(8),
            size_hint_y=None,
            adaptive_height=True,
            elevation=3,
            radius=[15, 15, 15, 15]
        )

        fields = [
            ("👤 Họ tên", user.get("fullName")),
            ("📧 Email", user.get("email")),
            ("📅 Ngày sinh", user.get("dateOfBirth")),
            ("⚧ Giới tính", user.get("gender")),
            ("🎓 Vai trò", user.get("role")),
            ("📊 Level", str(user.get("level"))),
            ("📌 Trạng thái", user.get("status")),
        ]
        for label, value in fields:
            card.add_widget(MDLabel(
                text=f"{label}: {value or 'N/A'}",
                font_style='Subtitle1',
                size_hint_y=None,
                height=dp(25)
            ))

        card.add_widget(MDRaisedButton(
            text="Chỉnh sửa thông tin",
            pos_hint={"center_x": 0.5},
            on_release=lambda x: self.show_edit_form(user)
        ))
        card.add_widget(MDRaisedButton(
            text="Đổi mật khẩu",
            pos_hint={"center_x": 0.5},
            on_release=lambda x: self.show_password_form()
        ))

        layout.add_widget(card)

    def show_edit_form(self, user):
        layout = self.ids.info_layout
        layout.clear_widgets()

        form = MDBoxLayout(orientation="vertical", spacing=10, padding=10, size_hint_y=None)
        form.bind(minimum_height=form.setter("height"))

        self.name_field = MDTextField(hint_text="Họ tên", text=user.get("fullName") or "", size_hint_y=None, height=dp(48))
        self.email_field = MDTextField(hint_text="Email", text=user.get("email") or "", size_hint_y=None, height=dp(48))
        self.dob_field = MDTextField(hint_text="Ngày sinh (YYYY-MM-DD)", text=user.get("dateOfBirth") or "", size_hint_y=None, height=dp(48))
        self.gender_field = MDTextField(hint_text="Giới tính", text=user.get("gender") or "", size_hint_y=None, height=dp(48))

        for f in [self.name_field, self.email_field, self.dob_field, self.gender_field]:
            form.add_widget(f)

        form.add_widget(MDRaisedButton(text="LƯU", on_release=lambda x: self.save_info()))
        form.add_widget(MDFlatButton(text="HỦY", on_release=lambda x: self.load_info()))

        layout.add_widget(form)

    def save_info(self):
        dob = self.dob_field.text.strip()
        # Chuẩn hóa ngày sinh về YYYY-MM-DD
        if len(dob) > 10:
            dob = dob[:10]

        payload = {
            "id_user": self.user_id,
            "fullName": self.name_field.text.strip(),
            "email": self.email_field.text.strip(),
            "dateOfBirth": dob,
            "gender": self.gender_field.text.strip()
        }

        print("DEBUG payload:", payload)

        if not payload["id_user"]:
            self.ids.info_layout.add_widget(MDLabel(text="❌ Không có ID người dùng"))
            return

        try:
            res = requests.put(f"{API_URL}/update", json=payload, timeout=5)
            if res.status_code != 200:
                self.ids.info_layout.add_widget(MDLabel(text=f"❌ Server trả về {res.status_code}: {res.text}"))
                return
            data = res.json()
            if data.get("success"):
                self.load_info()
            else:
                self.ids.info_layout.add_widget(MDLabel(text=f"❌ {data.get('message')}"))
        except Exception as e:
            self.ids.info_layout.add_widget(MDLabel(text=f"❌ Lỗi: {str(e)}"))

    def show_password_form(self):
        layout = self.ids.info_layout
        layout.clear_widgets()

        form = MDBoxLayout(orientation="vertical", spacing=10, padding=10, size_hint_y=None)
        form.bind(minimum_height=form.setter("height"))

        self.old_pass_field = MDTextField(hint_text="Mật khẩu cũ", password=True, size_hint_y=None, height=dp(48))
        self.new_pass_field = MDTextField(hint_text="Mật khẩu mới", password=True, size_hint_y=None, height=dp(48))

        for f in [self.old_pass_field, self.new_pass_field]:
            form.add_widget(f)

        form.add_widget(MDRaisedButton(text="ĐỔI", on_release=lambda x: self.save_password()))
        form.add_widget(MDFlatButton(text="HỦY", on_release=lambda x: self.load_info()))

        layout.add_widget(form)

    def save_password(self):
        old_pw = self.old_pass_field.text.strip()
        new_pw = self.new_pass_field.text.strip()

        if not old_pw or not new_pw:
            self.ids.info_layout.add_widget(MDLabel(text="❌ Vui lòng nhập đầy đủ mật khẩu"))
            return

        payload = {
            "id_user": self.user_id,
            "old_password": old_pw,
            "new_password": new_pw
        }

        print("DEBUG payload:", payload)

        if not payload["id_user"]:
            self.ids.info_layout.add_widget(MDLabel(text="❌ Không có ID người dùng"))
            return

        try:
            res = requests.put(f"{API_URL}/change_password", json=payload, timeout=5)
            if res.status_code != 200:
                self.ids.info_layout.add_widget(MDLabel(text=f"❌ Server trả về {res.status_code}: {res.text}"))
                return
            data = res.json()
            if data.get("success"):
                self.load_info()
            else:
                self.ids.info_layout.add_widget(MDLabel(text=f"❌ {data.get('message')}"))
        except Exception as e:
            self.ids.info_layout.add_widget(MDLabel(text=f"❌ Lỗi: {str(e)}"))

    def go_back(self):
        self.manager.current = 'home'

    def refresh_info(self):
        self.load_info()