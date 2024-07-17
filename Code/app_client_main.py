import sys

from PyQt6.QtWidgets import QApplication

from GUI.windows.main import MainWindow

if __name__ == "__main__":
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
