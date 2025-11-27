import logging
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.core.window import Window
from kivy.utils import platform
from kivymd.uix.navigationdrawer import MDNavigationLayout

from src.screens.intro.intro import IntroScreen
from src.screens.intro.intro_info import IntroInfoScreen
from src.screens.account.login import LoginScreen
from src.screens.account.register import RegisterScreen
from src.screens.home import HomeScreen

from src.screens.error_404 import Error404Screen
from src.screens.exam.exam_setup import ExamSetupScreen
from src.screens.exam.exam_question import ExamQuestionScreen
from src.screens.exam.exam_result import ExamResultScreen
from src.screens.account.profile import PersonalInfoScreen
from src.screens.exam.exam_history import ExamHistoryScreen
from src.screens.exam.exam_detail import ExamDetailScreen
from src.components.navigation import NavigationDrawer
from src.screens.package.payment_success import PaymentSuccessScreen


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)


class EducationPlus(MDApp):
    def build(self):
        try:
            if platform != "android" and platform != "ios":
                Window.size = (350, 615)

            self.theme_cls.theme_style = "Dark"
            self.theme_cls.primary_palette = "Blue"
            self.theme_cls.primary_hue = "700"

            sm = ScreenManager(transition=FadeTransition())

            screens = [
                (IntroScreen, 'intro'),
                (IntroInfoScreen, 'intro_info'),
                (LoginScreen, 'login'),
                (RegisterScreen, 'register'),
                (HomeScreen, 'home'),
                (ExamSetupScreen, 'exam_setup'),
                (ExamQuestionScreen, 'exam_question'),
                (ExamResultScreen, 'exam_result'),
                (ExamHistoryScreen, 'exam_history'),
                (ExamDetailScreen, 'exam_detail'),
                (Error404Screen, 'error_404'),
                (PersonalInfoScreen, 'personal_info'),
                (Error404Screen, 'error_404')
            ]

            for screen_class, name in screens:
                try:
                    sm.add_widget(screen_class(name=name))
                    logging.debug(f"Added screen: {name}")
                except Exception as e:
                    logging.error(f"Lỗi chạy màn hình {name}: {str(e)}", exc_info=True)
                    raise

            nav_layout = MDNavigationLayout()
            nav_layout.add_widget(sm)

            self.nav_drawer = NavigationDrawer(screen_manager=sm)
            nav_layout.add_widget(self.nav_drawer)

            self.screen_manager = sm

            return nav_layout

        except Exception as e:
            logging.error(f"Lỗi: {str(e)}", exc_info=True)
            raise


if __name__ == '__main__':
    try:
        EducationPlus().run()
    except Exception as e:
        logging.error(f"Ứng dụng bị ngắt: {str(e)}", exc_info=True)
        raise