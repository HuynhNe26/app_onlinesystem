import socket
import logging
from threading import Thread
from kivy.clock import Clock
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton


class NetworkCheck:
    """Kiểm tra kết nối mạng"""

    @staticmethod
    def is_connected(host="8.8.8.8", port=53, timeout=3):
        """
        Kiểm tra kết nối internet
        Args:
            host: DNS Google (8.8.8.8)
            port: DNS port (53)
            timeout: Thời gian chờ (giây)
        Returns:
            bool: True nếu có mạng, False nếu không
        """
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except socket.error as ex:
            logging.warning(f"Không có kết nối mạng: {ex}")
            return False

    @staticmethod
    def check_and_proceed(app, next_screen, callback=None):
        """
        Kiểm tra mạng và chuyển màn hình
        Args:
            app: Instance của MDApp
            next_screen: Tên màn hình tiếp theo
            callback: Function gọi sau khi kiểm tra (optional)
        """

        def check():
            is_connected = NetworkChecker.is_connected()
            Clock.schedule_once(lambda dt: handle_result(is_connected), 0)

        def handle_result(is_connected):
            if is_connected:
                logging.info("Có kết nối mạng, chuyển màn hình")
                app.root.current = next_screen
                if callback:
                    callback(True)
            else:
                logging.warning("Không có kết nối mạng")
                NetworkChecker.show_no_internet_dialog(app, next_screen, callback)

        # Chạy kiểm tra trong thread riêng để không block UI
        Thread(target=check, daemon=True).start()

    @staticmethod
    def show_no_internet_dialog(app, next_screen=None, callback=None):
        """Hiển thị dialog cảnh báo không có mạng"""
        dialog = MDDialog(
            title="Không có kết nối mạng",
            text="Vui lòng kiểm tra kết nối internet và thử lại.",
            buttons=[
                MDFlatButton(
                    text="THỬ LẠI",
                    on_release=lambda x: retry_connection(dialog)
                ),
                MDFlatButton(
                    text="HUỶ",
                    on_release=lambda x: cancel_connection(dialog)
                )
            ]
        )

        def retry_connection(dlg):
            dlg.dismiss()
            if next_screen:
                NetworkChecker.check_and_proceed(app, next_screen, callback)

        def cancel_connection(dlg):
            dlg.dismiss()
            if callback:
                callback(False)

        dialog.open()