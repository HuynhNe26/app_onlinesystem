from kivy.lang import Builder
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

NAV_KV = '''
<DrawerClickableItem@MDNavigationDrawerItem>
    focus_color: "#e7e4c0"
    text_color: "#4a4939"
    icon_color: "#4a4939"
    ripple_color: "#c5bdd2"
    selected_color: "#0c6c4d"

<NavigationDrawer>:
    radius: (0, 16, 16, 0)

    MDNavigationDrawerMenu:
        MDNavigationDrawerLabel:
            text: "MENU CHÍNH"

        DrawerClickableItem:
            icon: "home"
            text: "Trang chủ"
            on_release: 
                root.navigate("home")

        DrawerClickableItem:
            icon: "account"
            text: "Thông tin cá nhân"
            on_release: 
                root.show_coming_soon("Thông tin cá nhân")

        DrawerClickableItem:
            icon: "history"
            text: "Lịch sử làm bài"
            on_release: 
                root.navigate("exam_history")

        DrawerClickableItem:
            icon: "file-document-edit"
            text: "Kiểm tra"
            on_release: 
                root.navigate("exam_setup")

        DrawerClickableItem:
            icon: "package-variant"
            text: "Gói học"
            on_release: 
                root.navigate("package")

        MDNavigationDrawerDivider:

        MDNavigationDrawerLabel:
            text: "TÀI KHOẢN"

        DrawerClickableItem:
            icon: "cog"
            text: "Cài đặt"
            on_release: 
                root.show_coming_soon("Cài đặt")

        DrawerClickableItem:
            icon: "logout"
            text: "Đăng xuất"
            on_release: 
                root.logout()
'''

Builder.load_string(NAV_KV)


class NavigationDrawer(MDNavigationDrawer):
    def __init__(self, screen_manager=None, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = screen_manager
        self.dialog = None

    def navigate(self, screen_name):
        self.set_state("close")

        if self.screen_manager:
            try:
                if self.screen_manager.has_screen(screen_name):
                    self.screen_manager.current = screen_name
                else:
                    print(f"Màn hình {screen_name} không tồn tại")
                    if self.screen_manager.has_screen('error_404'):
                        self.screen_manager.current = 'error_404'
            except Exception as e:
                print(f"Lỗi chuyển màn hình: {e}")

    def show_coming_soon(self, feature_name):
        """Hiển thị thông báo tính năng đang phát triển"""
        self.set_state("close")

        if self.dialog:
            self.dialog.dismiss()

        self.dialog = MDDialog(
            title="Thông báo",
            text=f"Tính năng '{feature_name}' đang được phát triển.",
            buttons=[
                MDFlatButton(
                    text="ĐÓNG",
                    on_release=lambda x: self.dialog.dismiss()
                ),
            ],
        )
        self.dialog.open()

    def logout(self):
        self.set_state("close")

        if self.dialog:
            self.dialog.dismiss()

        self.dialog = MDDialog(
            title="Xác nhận đăng xuất",
            text="Bạn có chắc chắn muốn đăng xuất?",
            buttons=[
                MDFlatButton(
                    text="HỦY",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDFlatButton(
                    text="ĐĂNG XUẤT",
                    on_release=lambda x: self.confirm_logout()
                ),
            ],
        )
        self.dialog.open()

    def confirm_logout(self):
        if self.dialog:
            self.dialog.dismiss()

        self.navigate('login')

        print("Đã đăng xuất thành công")