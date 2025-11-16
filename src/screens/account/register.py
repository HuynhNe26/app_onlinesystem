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
        self.md_bg_color = (0.04, 0.07, 0.18, 1)
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
            spacing=dp(15),
            size_hint_y=None
        )
        layout.bind(minimum_height=layout.setter('height'))
        return layout

    def _create_header(self):
        header = MDBoxLayout(orientation="vertical", size_hint_y=None, height=dp(65), spacing=dp(5))
        header.add_widget(MDLabel(
            text="Tạo tài khoản",
            halign="center",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_style="H5",
            bold=True,
            size_hint_y=None,
            height=dp(40)
        ))
        header.add_widget(MDLabel(
            text="Bắt đầu hành trình học tập của bạn",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.7, 0.7, 0.8, 1),
            font_style="Body1",
            size_hint_y=None,
            height=dp(25)
        ))
        return header

    def _create_form_card(self):
        card = MDCard(
            orientation="vertical",
            padding=dp(25),
            spacing=dp(15),
            size_hint=(1, None),
            height=dp(700),
            radius=[25],
            md_bg_color=(0.94, 0.94, 0.94, 1),
            shadow_softness=5,
            shadow_offset=(0, -1)
        )

        self.full_name = self._create_text_field("Họ và tên")
        self.username = self._create_text_field("Tên đăng nhập")
        self.email = self._create_text_field("Email")

        card.add_widget(self.full_name)
        card.add_widget(self.username)
        card.add_widget(self.email)

        card.add_widget(self._create_gender_section())

        card.add_widget(self._create_date_field())

        card.add_widget(self._create_password_field())

        card.add_widget(self._create_confirm_password_field())

        card.add_widget(self._create_terms_section())

        card.add_widget(MDRaisedButton(
            text="Tạo tài khoản",
            md_bg_color=(0.25, 0.35, 0.6, 1),
            size_hint=(1, None),
            height=dp(45),
            on_release=self.register_user
        ))

        return card

    def _create_text_field(self, hint, password=False, readonly=False):
        return MDTextField(
            hint_text=hint,
            mode="rectangle",
            password=password,
            readonly=readonly,
            line_color_normal=(0.3, 0.3, 0.3, 1),
            hint_text_color_normal=(0.5, 0.5, 0.5, 1),
            text_color_normal=(0, 0, 0, 1),
            text_color_focus=(0, 0, 0, 1),
            fill_color_normal=(1, 1, 1, 1),
            cursor_color=(0, 0, 0, 1),
            size_hint_y=None,
            height=dp(50)
        )

    def _create_gender_section(self):
        container = MDBoxLayout(orientation="vertical", size_hint_y=None, height=dp(60), spacing=dp(5))

        container.add_widget(MDLabel(
            text="Giới tính:",
            theme_text_color="Custom",
            text_color=(0.2, 0.2, 0.2, 1),
            font_style="Body2",
            size_hint_y=None,
            height=dp(20)
        ))

        gender_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40), spacing=dp(30))

        self.gender_male = self._create_gender_checkbox("Nam", gender_box)
        self.gender_female = self._create_gender_checkbox("Nữ", gender_box)

        container.add_widget(gender_box)
        return container

    def _create_gender_checkbox(self, label_text, parent):
        box = MDBoxLayout(orientation="horizontal", size_hint=(None, None),
                          size=(dp(80), dp(40)), spacing=dp(8))

        checkbox = MDCheckbox(
            group="gender",
            size_hint=(None, None),
            size=(dp(24), dp(24)),
            pos_hint={"center_y": 0.5},
            color_active=(0.2, 0.2, 0.2, 1),
            color_inactive=(0.2, 0.2, 0.2, 1),
            unselected_color=(0.2, 0.2, 0.2, 1),
            selected_color=(0.2, 0.2, 0.2, 1)
        )
        checkbox.bind(active=self.on_gender_change)

        label = MDLabel(
            text=label_text,
            theme_text_color="Custom",
            text_color=(0.2, 0.2, 0.2, 1),
            font_style="Body1",
            size_hint_x=None,
            width=dp(40),
            pos_hint={"center_y": 0.5}
        )
        label.bind(on_touch_down=lambda i, t: self.on_gender_label_click(t, i, checkbox))

        box.add_widget(checkbox)
        box.add_widget(label)
        parent.add_widget(box)

        return checkbox

    def _create_date_field(self):
        date_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50))
        self.birth_date = self._create_text_field("Ngày sinh (dd/mm/yyyy)", readonly=True)
        self.birth_date.size_hint_x = 0.9
        date_btn = MDIconButton(
            icon="calendar",
            on_release=self.open_date_picker,
            theme_text_color="Custom",
            text_color=(0.2, 0.2, 0.2, 1)
        )
        date_box.add_widget(self.birth_date)
        date_box.add_widget(date_btn)
        return date_box

    def _create_password_field(self):
        password_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50))
        self.password = self._create_text_field("Mật khẩu", password=True)
        self.password.size_hint_x = 0.9
        self.show_pass_btn = MDIconButton(
            icon="eye-off",
            on_release=self.toggle_password,
            theme_text_color="Custom",
            text_color=(0.2, 0.2, 0.2, 1)
        )
        password_box.add_widget(self.password)
        password_box.add_widget(self.show_pass_btn)
        return password_box

    def _create_confirm_password_field(self):
        confirm_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50))
        self.confirm = self._create_text_field("Xác nhận mật khẩu", password=True)
        self.confirm.size_hint_x = 0.9
        self.show_confirm_btn = MDIconButton(
            icon="eye-off",
            on_release=self.toggle_confirm_password,
            theme_text_color="Custom",
            text_color=(0.2, 0.2, 0.2, 1)
        )
        confirm_box.add_widget(self.confirm)
        confirm_box.add_widget(self.show_confirm_btn)
        return confirm_box

    def _create_terms_section(self):
        terms_box = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(60),
            spacing=dp(8),
            padding=[0, dp(5), 0, 0]
        )
        self.terms_checkbox = MDCheckbox(
            size_hint=(None, None),
            size=(dp(30), dp(30)),
            pos_hint={"center_y": 0.5},
            color_active=(0.2, 0.2, 0.2, 1),
            color_inactive=(0.2, 0.2, 0.2, 1),
            unselected_color=(0.2, 0.2, 0.2, 1),
            selected_color=(0.2, 0.2, 0.2, 1)
        )
        terms_label = MDLabel(
            text="Tôi đồng ý với điều khoản dịch vụ và chính sách bảo mật",
            theme_text_color="Custom",
            text_color=(0.2, 0.2, 0.2, 1),
            halign="left",
            valign="middle",
            font_style="Body2",
            size_hint_y=None,
            height=dp(60)
        )
        terms_label.bind(size=terms_label.setter('text_size'))
        terms_box.add_widget(self.terms_checkbox)
        terms_box.add_widget(terms_label)
        return terms_box

    def _create_bottom_nav(self):
        return MDFlatButton(
            text="Đã có tài khoản? [b]Đăng nhập ngay[/b]",
            text_color=(0.85, 0.85, 0.95, 1),
            pos_hint={"center_x": 0.5},
            on_release=lambda x: setattr(self.manager, 'current', 'login')
        )

    def show_loading(self):
        if self.loading_modal is None:
            self.loading_modal = ModalView(
                size_hint=(None, None),
                size=(dp(100), dp(100)),
                background_color=(0, 0, 0, 0.5),
                auto_dismiss=False
            )

            layout = MDBoxLayout(
                orientation="vertical",
                spacing=dp(10),
                padding=dp(20)
            )

            spinner = MDSpinner(
                size_hint=(None, None),
                size=(dp(46), dp(46)),
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                active=True,
                palette=[
                    [0.28627450980392155, 0.8431372549019608, 0.596078431372549, 1],
                    [0.3568627450980392, 0.3215686274509804, 0.8666666666666667, 1],
                    [0.8862745098039215, 0.36470588235294116, 0.592156862745098, 1],
                    [0.8784313725490196, 0.9058823529411765, 0.40784313725490196, 1],
                ]
            )

            label = MDLabel(
                text="Đang xử lý...",
                halign="center",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                font_style="Caption"
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

    def toggle_confirm_password(self, instance):
        self.confirm.password = not self.confirm.password
        instance.icon = "eye" if not self.confirm.password else "eye-off"

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
            'username': self.username.text.strip(),
            'email': self.email.text.strip(),
            'birth': self.birth_date.text.strip(),
            'password': self.password.text.strip(),
            'confirm': self.confirm.text.strip(),
            'gender': gender,
            'avatar': avatar
        }

    def _validate_form(self, data):
        if not data['gender']:
            return "Vui lòng chọn giới tính."

        if not all([data['full_name'], data['username'], data['email'],
                    data['password'], data['confirm'], data['birth']]):
            return "Vui lòng nhập đầy đủ thông tin."

        if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
            return "Email không hợp lệ."

        if data['password'] != data['confirm']:
            return "Mật khẩu không khớp."

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
                    'username': data['username'],
                    'email': data['email'],
                    'password': data['password'],
                    'gender': data['gender'],
                    'avatar': data['avatar'],
                    'dateOfBirth': data['dateOfBirth']
                }
            )
            result = response.json()

            # Ẩn loading
            self.hide_loading()

            if result['success']:
                self.show_success_dialog(
                    "Đăng ký thành công! 🎉",
                    f"Chào mừng {data['full_name']}! Tài khoản của bạn đã được tạo thành công."
                )
            else:
                self.show_dialog("Lỗi", result['message'])
        except requests.exceptions.RequestException as e:
            self.hide_loading()
            self.show_dialog("Lỗi", f"Không thể kết nối đến server: {str(e)}")

    def show_dialog(self, title, text):
        dialog = MDDialog(
            title=title,
            text=text,
            size_hint=(0.8, None),
            height=dp(200),
            buttons=[
                MDRaisedButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()

    def show_success_dialog(self, title, text):
        dialog = MDDialog(
            title=title,
            text=text,
            size_hint=(0.8, None),
            height=dp(200),
            buttons=[
                MDRaisedButton(
                    text="Đăng nhập ngay",
                    md_bg_color=(0.25, 0.35, 0.6, 1),
                    on_release=lambda x: self.go_to_login(dialog)
                )
            ]
        )
        dialog.open()

    def go_to_login(self, dialog):
        dialog.dismiss()
        self.manager.current = "login"