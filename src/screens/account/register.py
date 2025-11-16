from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.spinner import MDSpinner
from kivy.uix.modalview import ModalView
from kivy.metrics import dp
from kivy.clock import Clock
import re
import requests
from datetime import datetime


class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = (0.05, 0.08, 0.16, 1)
        self.loading_modal = None
        self._build_ui()

    def _build_ui(self):
        scroll = MDScrollView(size_hint=(1, 1))
        root_layout = self._create_root_layout()

        root_layout.add_widget(self._create_header())

        card = self._create_form_card()
        root_layout.add_widget(card)

        root_layout.add_widget(self._create_bottom_nav())

        scroll.add_widget(root_layout)
        self.add_widget(scroll)

    def _create_root_layout(self):
        layout = MDBoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(20),
            size_hint_y=None
        )
        layout.bind(minimum_height=layout.setter('height'))
        return layout

    def _create_header(self):
        header = MDBoxLayout(orientation="vertical", size_hint_y=None, height=dp(90), spacing=dp(10))

        icon_label = MDLabel(
            text="🎓",
            halign="center",
            font_size=dp(45),
            size_hint_y=None,
            height=dp(50)
        )

        title = MDLabel(
            text="Tạo Tài Khoản",
            halign="center",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_style="H4",
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )

        header.add_widget(icon_label)
        header.add_widget(title)
        return header

    def _create_form_card(self):
        card = MDCard(
            orientation="vertical",
            padding=dp(28),
            spacing=dp(16),
            size_hint=(1, None),
            height=dp(650),
            radius=[30],
            md_bg_color=(0.98, 0.98, 0.99, 1),
            shadow_softness=12,
            shadow_offset=(0, 4),
            elevation=6
        )

        self.full_name = self._create_text_field("👤 Họ và tên đầy đủ")
        self.email = self._create_text_field("📧 Địa chỉ Email")

        card.add_widget(self.full_name)
        card.add_widget(self.email)

        card.add_widget(self._create_gender_section())
        card.add_widget(self._create_date_field())
        card.add_widget(self._create_password_field())
        card.add_widget(self._create_confirm_password_field())
        card.add_widget(self._create_terms_section())

        register_btn = MDRaisedButton(
            text="Tạo Tài Khoản",
            md_bg_color=(0.18, 0.38, 0.78, 1),
            size_hint=(1, None),
            height=dp(52),
            elevation=4,
            on_release=self.register_user
        )
        register_btn.font_size = dp(16)
        card.add_widget(register_btn)

        return card

    def _create_text_field(self, hint, password=False, readonly=False):
        field = MDTextField(
            hint_text=hint,
            mode="rectangle",
            password=password,
            readonly=readonly,
            line_color_normal=(0.6, 0.65, 0.7, 1),
            line_color_focus=(0.18, 0.38, 0.78, 1),
            hint_text_color_normal=(0.5, 0.5, 0.55, 1),
            hint_text_color_focus=(0.3, 0.3, 0.35, 1),
            text_color_normal=(0.1, 0.1, 0.15, 1),
            text_color_focus=(0, 0, 0.05, 1),
            fill_color_normal=(0.96, 0.97, 0.98, 1),
            fill_color_focus=(1, 1, 1, 1),
            cursor_color=(0.18, 0.38, 0.78, 1),
            size_hint_y=None,
            height=dp(56)
        )
        field.font_size = dp(15)
        return field

    def _create_gender_section(self):
        container = MDBoxLayout(orientation="vertical", size_hint_y=None, height=dp(85), spacing=dp(10))

        label = MDLabel(
            text="⚥ Giới tính",
            theme_text_color="Custom",
            text_color=(0.15, 0.15, 0.2, 1),
            font_style="Subtitle1",
            bold=True,
            size_hint_y=None,
            height=dp(25)
        )

        gender_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(40))

        self.gender_male = self._create_gender_checkbox("♂ Nam", gender_box)
        self.gender_female = self._create_gender_checkbox("♀ Nữ", gender_box)

        container.add_widget(label)
        container.add_widget(gender_box)
        return container

    def _create_gender_checkbox(self, label_text, parent):
        box = MDBoxLayout(
            orientation="horizontal",
            size_hint=(None, None),
            size=(dp(100), dp(50)),
            spacing=dp(10),
            padding=[dp(10), 0, dp(10), 0]
        )

        checkbox = MDCheckbox(
            group="gender",
            size_hint=(None, None),
            size=(dp(28), dp(28)),
            pos_hint={"center_y": 0.5},
            color_active=(0.18, 0.38, 0.78, 1),
            color_inactive=(0.5, 0.5, 0.55, 1)
        )
        checkbox.bind(active=self.on_gender_change)

        label = MDLabel(
            text=label_text,
            theme_text_color="Custom",
            text_color=(0.15, 0.15, 0.2, 1),
            font_style="Body1",
            bold=True,
            size_hint_x=None,
            width=dp(60),
            pos_hint={"center_y": 0.5}
        )
        label.bind(on_touch_down=lambda i, t: self.on_gender_label_click(t, i, checkbox))

        box.add_widget(checkbox)
        box.add_widget(label)
        parent.add_widget(box)

        return checkbox

    def _create_date_field(self):
        date_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(56))
        self.birth_date = self._create_text_field("🎂 Ngày sinh (dd/mm/yyyy)", readonly=True)
        self.birth_date.size_hint_x = 0.88
        date_btn = MDIconButton(
            icon="calendar",
            on_release=self.open_date_picker,
            theme_text_color="Custom",
            text_color=(0.18, 0.38, 0.78, 1),
            icon_size=dp(28)
        )
        date_box.add_widget(self.birth_date)
        date_box.add_widget(date_btn)
        return date_box

    def _create_password_field(self):
        password_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(56))
        self.password = self._create_text_field("🔒 Mật khẩu", password=True)
        self.password.size_hint_x = 0.88
        self.show_pass_btn = MDIconButton(
            icon="eye-off",
            on_release=self.toggle_password,
            theme_text_color="Custom",
            text_color=(0.5, 0.5, 0.55, 1),
            icon_size=dp(26)
        )
        password_box.add_widget(self.password)
        password_box.add_widget(self.show_pass_btn)
        return password_box

    def _create_confirm_password_field(self):
        confirm_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(56))
        self.confirm = self._create_text_field("🔐 Xác nhận mật khẩu", password=True)
        self.confirm.size_hint_x = 0.88
        self.show_confirm_btn = MDIconButton(
            icon="eye-off",
            on_release=self.toggle_confirm_password,
            theme_text_color="Custom",
            text_color=(0.5, 0.5, 0.55, 1),
            icon_size=dp(26)
        )
        confirm_box.add_widget(self.confirm)
        confirm_box.add_widget(self.show_confirm_btn)
        return confirm_box

    def _create_terms_section(self):
        terms_box = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(70),
            spacing=dp(10),
            padding=[0, dp(8), 0, 0]
        )
        self.terms_checkbox = MDCheckbox(
            size_hint=(None, None),
            size=(dp(32), dp(32)),
            pos_hint={"center_y": 0.5},
            color_active=(0.18, 0.38, 0.78, 1),
            color_inactive=(0.5, 0.5, 0.55, 1)
        )
        terms_label = MDLabel(
            text="Tôi đồng ý với điều khoản dịch vụ và chính sách bảo mật của ứng dụng",
            theme_text_color="Custom",
            text_color=(0.25, 0.25, 0.3, 1),
            halign="left",
            valign="middle",
            font_style="Body2",
            size_hint_y=None,
            height=dp(70)
        )
        terms_label.bind(size=terms_label.setter('text_size'))
        terms_box.add_widget(self.terms_checkbox)
        terms_box.add_widget(terms_label)
        return terms_box

    def _create_bottom_nav(self):
        bottom_box = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(50),
            spacing=dp(5)
        )

        # Tạo 2 label riêng biệt thay vì dùng markup
        label1 = MDLabel(
            text="Đã có tài khoản? ",
            theme_text_color="Custom",
            text_color=(0.75, 0.77, 0.82, 1),
            font_style="Body2",
            size_hint_x=None,
            width=dp(120),
            halign="right"
        )

        btn = MDFlatButton(
            text="Đăng nhập ngay",
            text_color=(0.29, 0.56, 0.89, 1),
            on_release=lambda x: setattr(self.manager, 'current', 'login')
        )
        btn.font_size = dp(15)

        bottom_box.add_widget(label1)
        bottom_box.add_widget(btn)

        wrapper = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(50)
        )
        wrapper.add_widget(bottom_box)

        return wrapper

    def show_loading(self):
        if self.loading_modal is None:
            self.loading_modal = ModalView(
                size_hint=(None, None),
                size=(dp(120), dp(120)),
                background_color=(0, 0, 0, 0.6),
                auto_dismiss=False
            )

            layout = MDBoxLayout(
                orientation="vertical",
                spacing=dp(12),
                padding=dp(20)
            )

            spinner = MDSpinner(
                size_hint=(None, None),
                size=(dp(50), dp(50)),
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                active=True,
                palette=[
                    [0.18, 0.38, 0.78, 1],
                    [0.28, 0.84, 0.60, 1],
                    [0.89, 0.36, 0.59, 1],
                    [0.96, 0.76, 0.19, 1],
                ]
            )

            label = MDLabel(
                text="Đang xử lý...",
                halign="center",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                font_style="Body2",
                bold=True
            )

            layout.add_widget(spinner)
            layout.add_widget(label)
            self.loading_modal.add_widget(layout)

        self.loading_modal.open()

    def hide_loading(self):
        if self.loading_modal:
            self.loading_modal.dismiss()

    def open_date_picker(self, instance):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_date_selected)
        date_dialog.open()

    def on_date_selected(self, instance, value, date_range):
        self.birth_date.text = value.strftime("%d/%m/%Y")

    def on_gender_change(self, checkbox, value):
        if value:
            if checkbox == self.gender_male:
                self.gender_female.active = False
            elif checkbox == self.gender_female:
                self.gender_male.active = False

    def on_gender_label_click(self, touch, instance, checkbox):
        if instance.collide_point(*touch.pos):
            checkbox.active = True

    def toggle_password(self, instance):
        self.password.password = not self.password.password
        instance.icon = "eye" if not self.password.password else "eye-off"
        instance.text_color = (0.18, 0.38, 0.78, 1) if not self.password.password else (0.5, 0.5, 0.55, 1)

    def toggle_confirm_password(self, instance):
        self.confirm.password = not self.confirm.password
        instance.icon = "eye" if not self.confirm.password else "eye-off"
        instance.text_color = (0.18, 0.38, 0.78, 1) if not self.confirm.password else (0.5, 0.5, 0.55, 1)

    def register_user(self, instance):
        data = self._get_form_data()

        error = self._validate_form(data)
        if error:
            self.show_dialog("Lỗi", error)
            return

        try:
            data['dateOfBirth'] = datetime.strptime(data['birth'], "%d/%m/%Y").strftime("%Y-%m-%d")
        except:
            self.show_dialog("Lỗi", "Định dạng ngày sinh không hợp lệ.")
            return

        self.show_loading()

        Clock.schedule_once(lambda dt: self._send_register_request(data), 0.1)

    def _get_form_data(self):
        gender = "Nam" if self.gender_male.active else ("Nữ" if self.gender_female.active else "")
        avatar = "src/assets/Avt/nam.png" if gender == "Nam" else ("src/assets/Avt/nu.png" if gender == "Nữ" else "")

        return {
            'full_name': self.full_name.text.strip(),
            'email': self.email.text.strip(),
            'birth': self.birth_date.text.strip(),
            'password': self.password.text.strip(),
            'confirm': self.confirm.text.strip(),
            'gender': gender,
            'avatar': avatar
        }

    def _validate_form(self, data):
        if not data['full_name']:
            return "Vui lòng nhập họ và tên."

        if not data['email']:
            return "Vui lòng nhập địa chỉ email."

        if not data['gender']:
            return "Vui lòng chọn giới tính."

        if not data['birth']:
            return "Vui lòng chọn ngày sinh."

        if not data['password']:
            return "Vui lòng nhập mật khẩu."

        if not data['confirm']:
            return "Vui lòng xác nhận mật khẩu."

        if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
            return "Email không hợp lệ."

        if len(data['password']) < 6:
            return "Mật khẩu phải có ít nhất 6 ký tự."

        if data['password'] != data['confirm']:
            return "Mật khẩu xác nhận không khớp."

        if not re.search(r"[A-Z]", data['password']):
            return "Mật khẩu phải chứa ít nhất một chữ cái viết hoa."

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", data['password']):
            return "Mật khẩu phải chứa ít nhất một ký tự đặc biệt."

        if not self.terms_checkbox.active:
            return "Bạn cần đồng ý với điều khoản để tiếp tục."

        return None

    def _send_register_request(self, data):
        try:
            response = requests.post(
                'https://backend-onlinesystem.onrender.com/api/users/register',
                json={
                    'fullName': data['full_name'],
                    'email': data['email'],
                    'password': data['password'],
                    'gender': data['gender'],
                    'avatar': data['avatar'],
                    'dateOfBirth': data['dateOfBirth']
                }
            )
            result = response.json()

            self.hide_loading()

            if result.get('success'):
                self.show_success_dialog(
                    "Đăng ký thành công!",
                    f"Chào mừng {data['full_name']}!\n\nTài khoản của bạn đã được tạo thành công. Hãy bắt đầu hành trình học tập ngay nào!"
                )
            else:
                self.show_dialog("Lỗi", result.get('message', 'Đăng ký thất bại'))
        except requests.exceptions.RequestException as e:
            self.hide_loading()
            self.show_dialog("Lỗi kết nối", f"Không thể kết nối đến server:\n{str(e)}")

    def show_dialog(self, title, text):
        dialog = MDDialog(
            title=title,
            text=text,
            size_hint=(0.85, None),
            height=dp(220),
            buttons=[
                MDRaisedButton(
                    text="Đóng",
                    md_bg_color=(0.5, 0.5, 0.55, 1),
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()

    def show_success_dialog(self, title, text):
        dialog = MDDialog(
            title=title,
            text=text,
            size_hint=(0.85, None),
            height=dp(250),
            buttons=[
                MDRaisedButton(
                    text="Đăng nhập ngay",
                    md_bg_color=(0.18, 0.38, 0.78, 1),
                    on_release=lambda x: self.go_to_login(dialog)
                )
            ]
        )
        dialog.open()

    def go_to_login(self, dialog):
        dialog.dismiss()
        self.manager.current = "login"