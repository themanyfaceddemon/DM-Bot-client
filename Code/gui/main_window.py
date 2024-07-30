import os

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (QDialog, QLabel, QLineEdit, QMainWindow,
                             QMessageBox, QPushButton)
from PyQt6.uic import loadUi
from root_path import ROOT_PATH
from systems.misc import GlobalClass
from systems.network import ClientUnit


class MainApplicationWindow(QMainWindow, GlobalClass):
    def __init__(self):
        super().__init__()
        
        if not hasattr(self, '_initialized'):
            self._initialized = True
            loadUi(os.path.join(ROOT_PATH, 'GUI', 'windows', 'MainWindow.ui'), self)
