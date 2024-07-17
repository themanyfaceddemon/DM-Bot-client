import os

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow
from root_path import ROOT_PATH


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        uic.loadUi(os.path.join(ROOT_PATH, 'GUI', 'main_window.ui'), self)

if __name__ == "__main__":
    app = QApplication([])
    window = MyWindow()
    window.show()
    app.exec()
