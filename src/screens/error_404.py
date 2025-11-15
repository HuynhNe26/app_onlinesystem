import logging

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
import requests

class Error404Screen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = MDBoxLayout(orientation="vertical", spacing="20dp", padding="40dp")
        layout.add_widget(MDLabel(
            text="📡 Không có kết nối Internet",
            halign="center",
            font_style="H5",
            theme_text_color="Primary"
        ))
        layout.add_widget(MDLabel(
            text="Vui lòng kiểm tra lại Wi-Fi hoặc kết nối dữ liệu di động.",
            halign="center",
            font_style="Body1",
            theme_text_color="Secondary"
        ))

        retry_button = MDRaisedButton(
            text="Thử lại",
            pos_hint={"center_x": 0.5},
            on_release=lambda x: self.retry_connection()
        )
        layout.add_widget(retry_button)
        self.add_widget(layout)

    def retry_connection(self):
        try:
            requests.get("https://www.google.com", timeout=3)
            self.manager.current = "login"  # hoặc màn hình khác
        except:
            pass  # vẫn ở màn hình lỗi

    def on_start(self):
        logging.debug("StudyMaxApp started")

        # Check database (có sẵn của bạn)
        from src.back_end.config.db_config import get_db_connection
        conn = get_db_connection()
        if not conn:
            logging.error("Database connection failed. Check db_config.py settings.")

        # 🔌 Kiểm tra kết nối Internet
        try:
            requests.get("https://www.google.com", timeout=3)
            logging.debug("Internet connection OK")
        except:
            logging.warning("No Internet connection!")
            self.root.current = "error_404"
            return

        if conn:
            conn.close()