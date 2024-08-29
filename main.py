import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import FileManagementApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileManagementApp()
    window.show()
    sys.exit(app.exec_())
