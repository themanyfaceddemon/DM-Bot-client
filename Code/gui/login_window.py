import os

from gui.main_window import MainApplicationWindow
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (QDialog, QLabel, QLineEdit, QMainWindow,
                             QMessageBox, QPushButton)
from PyQt6.uic import loadUi
from root_path import ROOT_PATH
from systems.decorators import global_class
from systems.network import ClientUnit


@global_class
class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi(os.path.join(ROOT_PATH, 'GUI', 'windows', 'LoginWindow.ui'), self)

        # Привязка виджетов
        self.ip_line = self.findChild(QLineEdit, 'IPLine')
        self.port_line = self.findChild(QLineEdit, 'PortLine')
        self.server_check_button = self.findChild(QPushButton, 'ServerCheckButton')
        self.server_check_label = self.findChild(QLabel, 'ServerCheckLabel')

        self.login_button = self.findChild(QPushButton, 'LoginButton')
        self.register_button = self.findChild(QPushButton, 'RegisterButton')

        self.set_server_check_label("failure")
        
        # Привязка функций к кнопкам
        self.server_check_button.clicked.connect(self.check_server)
        self.login_button.clicked.connect(self.open_auth_window)
        self.register_button.clicked.connect(self.open_registration_window)

        # Начальное состояние кнопок
        self.login_button.setEnabled(False)
        self.register_button.setEnabled(False)

    def set_server_check_label(self, state: str):
        self.server_check_label.setPixmap(QPixmap(os.path.join(ROOT_PATH, 'GUI', 'images', 'status', f'{state}_64_64.png')))

    def check_server(self):
        ip = self.ip_line.text()
        port = self.port_line.text()
        
        if not ip or not port:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
            self.set_server_check_label("failure")
            self.set_buttons(False)
            return

        if not self.is_valid_ip(ip):
            QMessageBox.warning(self, "Ошибка", "IP неверно указан. Такого IP не может существовать.")
            self.set_server_check_label("failure")
            self.set_buttons(False)
            return
        
        if not self.is_valid_port(port):
            QMessageBox.warning(self, "Ошибка", "Порт неверно указан. Такого порта не может существовать.")
            self.set_server_check_label("failure")
            self.set_buttons(False)
            return

        cl_unit: ClientUnit = ClientUnit.get_instance()
        try:
            cl_unit.check_server(ip, int(port))
            self.set_server_check_label("success")
            self.set_buttons(True)
            
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Невозможно подключиться к серверу: {str(e)}")
            self.set_server_check_label("failure")
            self.set_buttons(False)
            return

    def open_auth_window(self):
        auth_window = AuthDialog(self)
        auth_window.exec()

    def open_registration_window(self):
        registration_window = RegistrationDialog(self)
        registration_window.exec()

    def set_buttons(self, value: bool):
        self.login_button.setEnabled(value)
        self.register_button.setEnabled(value)
    
    def is_valid_ip(self, ip: str) -> bool:
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        
        for part in parts:
            if not part.isdigit():
                return False
            
            if not 0 <= int(part) <= 255:
                return False
        
        return True

    def is_valid_port(self, port: str) -> bool:
        if not port.isdigit():
            return False
        
        port_num = int(port)
        return 1 <= port_num <= 65535

    def run_main_app(self) -> None:
        self.close()
        self.main_window: MainApplicationWindow = MainApplicationWindow.get_instance()
        self.main_window.show()
    
    
class AuthDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi(os.path.join(ROOT_PATH, 'GUI', 'windows', 'AuthDialog.ui'), self)

        self.username_line = self.findChild(QLineEdit, 'UsernameLine')
        self.password_line = self.findChild(QLineEdit, 'PasswordLine')
        self.login_button = self.findChild(QPushButton, 'LoginButton')

        self.login_button.clicked.connect(self.authenticate)

    def authenticate(self):
        username = self.username_line.text()
        password = self.password_line.text()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
            return
        
        cl_unit: ClientUnit = ClientUnit.get_instance()
        try:
            cl_unit.login(username, password)
            self.close_current_and_open_main_window()
        
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Невозможно выполнить аутентификацию: {str(e)}")

    def close_current_and_open_main_window(self):
        self.close()
        self.parent().run_main_app()

class RegistrationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi(os.path.join(ROOT_PATH, 'GUI', 'windows', 'RegistrationDialog.ui'), self)

        self.username_line = self.findChild(QLineEdit, 'UsernameLine')
        self.password_line = self.findChild(QLineEdit, 'PasswordLine')
        self.password_line_2 = self.findChild(QLineEdit, 'PasswordLine_2')
        self.register_button = self.findChild(QPushButton, 'RegisterButton')

        self.register_button.clicked.connect(self.register)

    def register(self):
        username = self.username_line.text()
        password = self.password_line.text()
        password_2 = self.password_line_2.text()

        if not username or not password or not password_2:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
            return
        
        if password != password_2:
            QMessageBox.warning(self, "Ошибка", "Пароли должны совпадать!")
            return
            
        cl_unit: ClientUnit = ClientUnit.get_instance()
        try:
            cl_unit.register(username, password)
            self.close_current_and_open_main_window()
        except Exception as err:
            QMessageBox.warning(self, "Ошибка", f"Логин который вы указали уже занят. Подробная ошибка: {err}")

    def close_current_and_open_main_window(self):
        self.close()
        self.parent().run_main_app()
