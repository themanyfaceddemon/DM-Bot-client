import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QLineEdit, QPushButton, QLabel
from PyQt6.QtGui import QPixmap
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
        self.soket_port_line = self.findChild(QLineEdit, 'SoketPortLine')
        self.server_check_button = self.findChild(QPushButton, 'ServerCheckButton')
        self.server_check_label = self.findChild(QLabel, 'ServerCheckLabel')

        self.set_server_check_label("failure")
        
        # Привязка функции к кнопке
        self.server_check_button.clicked.connect(self.check_server)

    def set_server_check_label(self, state: str):
        self.server_check_label.setPixmap(QPixmap(os.path.join(ROOT_PATH, 'GUI', 'images', 'status', f'{state}_64_64.png'))) 
    
    def check_server(self):
        ip = self.ip_line.text()
        port = self.port_line.text()
        soket_port = self.soket_port_line.text()

        if ip and port and soket_port:
            try:
                port = int(port)
                soket_port = int(soket_port)
            
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Порт и порт сокета должны быть числами!")
                self.set_server_check_label("failure")
                return

            cl_unit: ClientUnit = ClientUnit.get_instance()
            try:
                if not cl_unit.check_server(ip, port, soket_port):
                    QMessageBox.warning(self, "Ошибка", "Невозможно подключиться к серверу")
                    self.set_server_check_label("failure")
                
                else:
                    self.set_server_check_label("success")
            
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Невозможно подключиться к серверу: {str(e)}")
                self.set_server_check_label("failure")
        
        else:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены!")
            self.set_server_check_label("failure")
