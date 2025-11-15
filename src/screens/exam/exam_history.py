import requests
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.lang import Builder
from kivy.metrics import dp
import logging

API_URL = "https://backend-onlinesystem.onrender.com/api/exam"

# KV Layout embedded
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
""")


class ExamHistoryScreen(MDScreen):
    """Màn hình hiển thị lịch sử bài thi"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialog = None

    def on_enter(self):
        """Tự động load khi vào màn hình"""
        self.load_history()

    def load_history(self):
        """Tải lịch sử bài thi từ API"""
        try:
            token = self.get_token()

            res = requests.get(
                f"{API_URL}/exam/history",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5
            )

            data = res.json()

            if res.status_code == 200 and data.get('success'):
                history = data.get('history', [])
                logging.info(f"Loaded {len(history)} exam records")
                self.display_history(history)
            else:
                self.show_error_dialog("Lỗi", data.get('message', 'Không tải được lịch sử'))

        except Exception as e:
            logging.error(f"Error loading history: {e}")
            self.show_error_dialog("Lỗi", f"Lỗi khi tải lịch sử: {str(e)}")

    def display_history(self, history):
        """Hiển thị danh sách lịch sử"""
        history_layout = self.ids.history_layout
        history_layout.clear_widgets()

        if not history:
            # No history message
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
                text='Chưa có lịch sử bài thi\\n\\nHãy bắt đầu làm bài kiểm tra đầu tiên!',
                halign='center',
                font_style='Body1',
                size_hint_y=None,
                height=dp(70)
            )

            empty_card.add_widget(empty_icon)
            empty_card.add_widget(empty_label)
            history_layout.add_widget(empty_card)
            return

        # Display each exam record
        for item in history:
            card = self.create_history_card(item)
            history_layout.add_widget(card)

    def create_history_card(self, item):
        """Tạo card cho mỗi bài thi"""
        card = MDCard(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(160),
            elevation=3,
            radius=[15, 15, 15, 15]
        )

        # Header with exam name
        name_label = MDLabel(
            text=item['name_ex'],
            font_style='H6',
            bold=True,
            size_hint_y=None,
            height=dp(30)
        )
        card.add_widget(name_label)

        # Score with color and icon
        score = item['score']
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

        # Correct answers
        correct_label = MDLabel(
            text=f"✅ Số câu đúng: {item['total_correct']}/{item['total_ques']}",
            font_style='Subtitle1',
            size_hint_y=None,
            height=dp(25)
        )
        card.add_widget(correct_label)

        # Category
        category_label = MDLabel(
            text=f"📚 Danh mục: {item.get('exam_cat', 'N/A')}",
            font_style='Body2',
            size_hint_y=None,
            height=dp(25)
        )
        card.add_widget(category_label)

        # Date
        try:
            date_str = str(item['completed_time'])[:19]
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

        return card

    def go_back(self):
        """Quay lại màn hình trước"""
        self.manager.current = 'exam_setup'

    def refresh_history(self):
        """Làm mới lịch sử"""
        self.load_history()

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