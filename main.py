import sys
from PySide6.QtWidgets import QApplication
from app import App

# Initialize the main window
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = App()
    main_window.show()
    sys.exit(app.exec())
