import requests
import logging
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.clock import Clock

API_URL = "https://backend-onlinesystem.onrender.com/api/exam"

KV = """
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
                on_release: root.refresh_history()
                size_hint_x: None
                width: dp(50)

        # History list
        ScrollView:
            MDBoxLayout:
                id: history_layout
                orientation: 'vertical'
                spacing: dp(15)
                padding: dp(5)
                size_hint_y: None
                height: self.minimum_height
"""

Builder.load_string(KV)


class ExamHistoryScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None

    def on_enter(self):
        self.load_history()

    def load_history(self):
        """Tải lịch sử bài thi từ API"""
        def _load():
            try:
                token = self.get_token()
                if not token:
                    Clock.schedule_once(lambda dt: self.show_error_dialog("Lỗi", "Bạn chưa đăng nhập"))
                    return

                res = requests.get(
                    f"{API_URL}/exam/history",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10
                )

                if res.status_code != 200:
                    try:
                        msg = res.json().get('message', res.text)
                    except Exception:
                        msg = res.text
                    Clock.schedule_once(lambda dt: self.show_error_dialog("Lỗi", msg))
                    return

                data = res.json()
                if not data.get('success'):
                    Clock.schedule_once(lambda dt: self.show_error_dialog("Lỗi", data.get('message', 'Lỗi server')))
                    return

                history = data.get('history', [])
                Clock.schedule_once(lambda dt: self.display_history(history))

            except Exception as e:
                logging.error(f"Error loading history: {e}")
                Clock.schedule_once(lambda dt: self.show_error_dialog("Lỗi", str(e)))

        import threading
        threading.Thread(target=_load, daemon=True).start()

    def display_history(self, history):
        """Hiển thị danh sách lịch sử"""
        history_layout = self.ids.history_layout
        history_layout.clear_widgets()

        if not history:
            empty_card = MDCard(
                orientation='vertical',
                padding=dp(30),
                size_hint_y=None,
                height=dp(150),
                elevation=2,
                radius=[15, 15, 15, 15]
            )
            empty_icon = MDLabel(
                text='📚',
                halign='center',
                font_style='H3',
                size_hint_y=None,
                height=dp(50)
            )
            empty_label = MDLabel(
                text='Chưa có lịch sử bài thi\n\nHãy bắt đầu làm bài kiểm tra đầu tiên!',
                halign='center',
                font_style='Body1',
                size_hint_y=None,
                height=dp(70)
            )
            empty_card.add_widget(empty_icon)
            empty_card.add_widget(empty_label)
            history_layout.add_widget(empty_card)
            return

        for item in history:
            card = self.create_history_card(item)
            history_layout.add_widget(card)

    def create_history_card(self, item):
        """Tạo card cho mỗi bài thi"""
        card = MDCard(
            orientation='vertical',
            padding=dp(12),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(200),
            elevation=3,
            radius=[12, 12, 12, 12]
        )

        name_label = MDLabel(
            text=item.get('exam_name', 'Đề thi'),
            font_style='H6',
            bold=True,
            size_hint_y=None,
            height=dp(30)
        )
        card.add_widget(name_label)

        score = item.get('score', 0)
        if score >= 80:
            score_color = [0.2, 0.8, 0.2, 1]
            icon = '🎉'
        elif score >= 50:
            score_color = [0.2, 0.6, 1, 1]
            icon = '👍'
        else:
            score_color = [0.8, 0.2, 0.2, 1]
            icon = '😔'

        score_label = MDLabel(
            text=f"{icon} Điểm: {score}/100",
            font_style='H6',
            theme_text_color='Custom',
            text_color=score_color,
            size_hint_y=None,
            height=dp(30)
        )
        card.add_widget(score_label)

        total_correct = item.get('total_correct', 0)
        total_q = item.get('total_questions') or item.get('total_ques') or 0
        correct_label = MDLabel(
            text=f"✅ Số câu đúng: {total_correct}/{total_q}",
            font_style='Subtitle1',
            size_hint_y=None,
            height=dp(25)
        )
        card.add_widget(correct_label)

        category_label = MDLabel(
            text=f"📚 Danh mục: {item.get('exam_cat', 'N/A')}",
            font_style='Body2',
            size_hint_y=None,
            height=dp(25)
        )
        card.add_widget(category_label)

        try:
            date_str = str(item.get('completed_time') or item.get('created_at', ''))[:19]
            date_label_text = f"📅 Ngày làm: {date_str}"
        except:
            date_label_text = "📅 Ngày làm: N/A"

        date_label = MDLabel(
            text=date_label_text,
            font_style='Caption',
            size_hint_y=None,
            height=dp(20)
        )
        card.add_widget(date_label)

        detail_button = MDRaisedButton(
            text='📊 Xem chi tiết',
            size_hint_x=1,
            size_hint_y=None,
            height=dp(44),
            md_bg_color=[0.2, 0.6, 1, 1],
            on_release=lambda x, result_id=item.get('id_result'): self.view_detail(result_id)
        )
        card.add_widget(detail_button)

        return card

    def view_detail(self, result_id):
        """Mở màn hình chi tiết"""
        try:
            detail_screen = self.manager.get_screen('exam_detail')
            detail_screen.load_result_detail(result_id, from_screen='exam_history')
            self.manager.current = 'exam_detail'
        except Exception as e:
            logging.error(f"Error navigating to detail: {e}")
            self.show_error_dialog("Lỗi", f"Không thể mở chi tiết: {e}")

    def go_back(self):
        self.manager.current = 'home'

    def refresh_history(self):
        self.load_history()

    def get_token(self):
        try:
            from kivy.storage.jsonstore import JsonStore
            store = JsonStore('user.json')
            for key in ('auth', 'token', 'user'):
                if store.exists(key):
                    d = store.get(key)
                    token = d.get('token') or d.get('access_token') or (d if isinstance(d, str) else None)
                    if token:
                        return token
            return None
        except Exception as e:
            logging.error(f"Error getting token: {e}")
            return None

    def show_error_dialog(self, title, message):
        if self.dialog:
            self.dialog.dismiss()
        self.dialog = MDDialog(
            title=title,
            text=str(message),
            buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
        )
        self.dialog.open()