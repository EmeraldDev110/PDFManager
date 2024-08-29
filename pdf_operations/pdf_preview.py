from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

class PDFPreview(QMainWindow):
    def __init__(self, directory, filename):
        super().__init__()
        self.setWindowTitle("PDF Preview")
        self.setGeometry(150, 150, 600, 800)

        web_view = QWebEngineView(self)
        filepath = QUrl.fromLocalFile(f"{directory}/{filename}")
        web_view.load(filepath)
        self.setCentralWidget(web_view)
