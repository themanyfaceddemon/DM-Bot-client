import sys

from gui import LoginWindow
from PyQt6.QtWidgets import QApplication
from systems.network import ClientUnit

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window: LoginWindow = LoginWindow.get_instance()
    window.show()
    sys.exit(app.exec())
