from PySide2.QtWidgets import (QApplication, QVBoxLayout, QWidget, QTabWidget)
from qt_material import apply_stylesheet, QtStyleTools

from logic.database import Database
from logic.user import User, UserPrivilege
from ui.window.dashboard.admin_users_tab import AdminUsersTab
from ui.window.dashboard.books_tab_widget import BooksTabWidget
from ui.window.dashboard.settings_tab.settings_tab import SettingsTab


class Dashboard(QWidget, QtStyleTools):

    def __init__(self, current_user: User, parent=None):
        super(Dashboard, self).__init__(parent)

        self.current_user = current_user
        self.current_user_account_settings = Database.get_user_account_settings(self.current_user.username)

        self.configure_window_title()

        self.resize(1024, 768)

        layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.configure_tabs()
        layout.addWidget(self.tabs)

        self.configure_theme_and_accent_colour()

        self.setLayout(layout)
    
    def configure_window_title(self):
        self.setWindowTitle(f'Snakebrary - Logged in as {self.current_user.username} ({self.current_user.name})')

    def configure_tabs(self):
        
        self.settings_tab = SettingsTab(self.current_user, self.current_user_account_settings, self.dashboard_on_user_edited)

        if self.current_user.privilege != UserPrivilege.NORMAL:
            self.admin_users_table = AdminUsersTab(self.current_user, self.dashboard_on_user_edited)
            self.tabs.addTab(self.admin_users_table, 'Users')

        self.tabs.addTab(BooksTabWidget(self.current_user), 'Books')

        self.tabs.addTab(self.settings_tab, "Settings")

    def configure_theme_and_accent_colour(self):
        stylesheet_name = f'{self.current_user_account_settings.theme.lower()}_{self.current_user_account_settings.accent_colour.lower().replace(" ", "")}.xml'
        apply_stylesheet(QApplication.instance(), stylesheet_name)

    def dashboard_on_user_edited(self):
        if self.current_user.privilege != UserPrivilege.NORMAL:
            self.admin_users_table.configure_users_table()
        
        self.current_user = Database.get_user_by_username(self.current_user.username)
        self.admin_users_table.current_user = self.current_user
        self.settings_tab.account_tab.user_info_vbox.current_user = self.current_user
        self.settings_tab.account_tab.user_info_vbox.configure_ui()
        self.configure_window_title()
