import sys

from GUI.windows.main import MainWindow  # type: ignore
from PyQt6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
