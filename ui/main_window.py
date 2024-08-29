import os
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem, QLineEdit, QWidget, QMessageBox
from PyQt5.QtCore import QStandardPaths
from pdf_operations.pdf_manager import PDFManager

class FileManagementApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF File Manager")
        self.setGeometry(100, 100, 800, 600)
        
        self.directory = None

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.select_dir_button = QPushButton("Select Directory", self)
        self.select_dir_button.clicked.connect(self.select_directory)
        self.layout.addWidget(self.select_dir_button)

        self.pdf_table = QTableWidget(self)
        self.pdf_table.setColumnCount(3)
        self.pdf_table.setHorizontalHeaderLabels(["No", "Filename", "Label"])
        self.layout.addWidget(self.pdf_table)

        self.combine_button = QPushButton("Combine Labeled PDFs", self)
        self.combine_button.clicked.connect(self.combine_pdfs)
        self.layout.addWidget(self.combine_button)

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.directory = directory
            self.load_pdfs(directory)

    def load_pdfs(self, directory):
        pdf_manager = PDFManager(directory)
        pdf_files = pdf_manager.get_pdf_files()

        self.pdf_table.setRowCount(len(pdf_files))
        for index, filename in enumerate(pdf_files):
            self.pdf_table.setItem(index, 0, QTableWidgetItem(str(index + 1)))
            self.pdf_table.setItem(index, 1, QTableWidgetItem(filename))

            label_name = os.path.splitext(filename)[0]
            label_input = QLineEdit(self)
            label_input.setText(label_name)
            self.pdf_table.setCellWidget(index, 2, label_input)

    def combine_pdfs(self):
        if not self.directory:
            print("No directory selected.")
            return

        pdf_manager = PDFManager(self.directory)
        labeled_pdfs = []
        pdf_files = []

        for row in range(self.pdf_table.rowCount()):
            filename_item = self.pdf_table.item(row, 1)
            label_input = self.pdf_table.cellWidget(row, 2)
            if filename_item and label_input:
                original_filepath = os.path.join(self.directory, filename_item.text())
                label = label_input.text()
                labeled_pdf_data = pdf_manager.label_pdf_in_memory(original_filepath, label)
                labeled_pdfs.append(labeled_pdf_data)
                pdf_files.append(filename_item.text())

        combined_pdf = pdf_manager.combine_pdfs(pdf_files, labeled_pdfs)

        desktop_path = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)
        result_filepath = os.path.join(desktop_path, "result.pdf")

        # Attempt to open the file in write-binary mode to override existing content
        try:
            with open(result_filepath, 'wb') as output_file:
                output_file.write(combined_pdf)

            # Show alert dialog when done
            self.show_completion_alert(result_filepath)

        except PermissionError as e:
            self.show_error_alert(f"Permission denied: {e}")
        except Exception as e:
            self.show_error_alert(f"Failed to save the file: {e}")

    def show_completion_alert(self, filepath):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("PDF Combined")
        msg_box.setText(f"The combined PDF has been saved successfully!\n\nLocation: {filepath}")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def show_error_alert(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Error")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
