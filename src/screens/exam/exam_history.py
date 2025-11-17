import requests
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.lang import Builder
from kivy.metrics import dp
import logging

API_URL = "https://backend-onlinesystem.onrender.com/api/exam"

Builder.load_string("""
<ExamHistoryScreen>:
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
                text: 'Lịch sử bài thi'
                font_style: 'H5'
                halign: 'center'
                bold: True

            MDIconButton:
                icon: 'refresh'
                on_release: root.load_history()
                size_hint_x: None
                width: dp(50)

        ScrollView:
            MDBoxLayout:
                id: history_layout
                orientation: 'vertical'
                spacing: dp(15)
                padding: dp(5)
                size_hint_y: None
                height: self.minimum_height
""")

class ExamHistoryScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None

    def on_enter(self):
        self.load_history()

    def load_history(self):
        try:
            token = self.get_token()
            if not token:
                raise Exception("Chưa đăng nhập")

            res = requests.get(
                f"{API_URL}/exam/history",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5
            )
            data = res.json()
            if res.status_code == 200 and data.get("success"):
                self.display_history(data.get("history", []))
            else:
                self.show_error_dialog("Lỗi", data.get("message","Không tải được lịch sử"))
        except Exception as e:
            logging.error(f"Error loading history: {e}")
            self.show_error_dialog("Lỗi", str(e))

    def display_history(self, history):
        layout = self.ids.history_layout
        layout.clear_widgets()
        if not history:
            card = MDCard(
                orientation='vertical',
                padding=dp(30),
                size_hint_y=None,
                height=dp(150),
                elevation=2,
                radius=[15]*4
            )
            card.add_widget(MDLabel(text='📚', halign='center', font_style='H3', size_hint_y=None, height=dp(50)))
            card.add_widget(MDLabel(text='Chưa có lịch sử bài thi', halign='center', font_style='Body1', size_hint_y=None, height=dp(50)))
            layout.add_widget(card)
            return

        for item in history:
            card = MDCard(
                orientation='vertical',
                padding=dp(15),
                spacing=dp(8),
                size_hint_y=None,
                height=dp(180),
                elevation=3,
                radius=[15]*4
            )
            card.add_widget(MDLabel(
                text=item.get("exam_name","Đề thi"),
                font_style='H6', bold=True, size_hint_y=None, height=dp(30)
            ))
            score = item.get("score",0)
            score_color = [0.2,0.8,0.2,1] if score>=80 else [0.2,0.6,1,1] if score>=50 else [0.8,0.2,0.2,1]
            icon = "Chúc mừng" if score>=80 else "Tốt" if score>=50 else "Cố gắng lần sau"
            card.add_widget(MDLabel(
                text=f"{icon} Điểm: {score}/100",
                font_style='H6',
                theme_text_color='Custom',
                text_color=score_color,
                size_hint_y=None,
                height=dp(30)
            ))
            card.add_widget(MDLabel(
                text=f"Số câu đúng: {item.get('total_correct',0)}/{item.get('total_questions',0)}",
                font_style='Subtitle1',
                size_hint_y=None,
                height=dp(25)
            ))
            date_str = str(item.get('created_at','N/A'))[:19]
            card.add_widget(MDLabel(
                text=f"Ngày làm: {date_str}",
                font_style='Caption',
                size_hint_y=None,
                height=dp(20)
            ))
            detail_btn = MDRaisedButton(
                text="Xem chi tiết",
                size_hint_x=1,
                size_hint_y=None,
                height=dp(45),
                md_bg_color=[0.2,0.6,1,1],
                on_release=lambda x, rid=item['id_result']: self.view_detail(rid)
            )
            card.add_widget(detail_btn)
            layout.add_widget(card)

    def view_detail(self, result_id):
        try:
            detail_screen = self.manager.get_screen('exam_detail')
            detail_screen.load_result_detail(result_id)
            self.manager.current = 'exam_detail'
        except Exception as e:
            logging.error(f"Error navigating to detail: {e}")
            self.show_error_dialog("Lỗi", str(e))

    def go_back(self):
        self.manager.current = 'home'

    def get_token(self):
        try:
            from kivy.storage.jsonstore import JsonStore
            store = JsonStore('user.json')
            if store.exists('auth'):
                return store.get('auth').get('token')
            return None
        except:
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
