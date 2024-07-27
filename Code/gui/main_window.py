import os

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (QDialog, QLabel, QLineEdit, QMainWindow,
                             QMessageBox, QPushButton)
from PyQt6.uic import loadUi
from root_path import ROOT_PATH
from systems.decorators import global_class
from systems.network import ClientUnit


@global_class
class MainApplicationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi(os.path.join(ROOT_PATH, 'GUI', 'windows', 'MainWindow.ui'), self)
