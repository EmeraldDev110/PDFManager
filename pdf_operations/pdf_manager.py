from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from io import BytesIO
import os

class PDFManager:
    def __init__(self, directory=None):
        self.directory = directory

    def get_pdf_files(self):
        return [f for f in os.listdir(self.directory) if f.endswith('.pdf')]

    def label_pdf_in_memory(self, filepath, label):
        reader = PdfReader(filepath)
        writer = PdfWriter()

        first_page = reader.pages[0]
        width = first_page.mediabox.upper_right[0]
        height = first_page.mediabox.upper_right[1]

        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=(width, height))

        x = width - 150  # Adjust X position to fit the text
        y = 30  # Adjust Y position (30 units from the bottom)
        can.drawString(x, y, label)
        can.save()

        packet.seek(0)
        watermark_pdf = PdfReader(packet)
        watermark_page = watermark_pdf.pages[0]

        first_page.merge_page(watermark_page)
        writer.add_page(first_page)

        for page in reader.pages[1:]:
            writer.add_page(page)

        output_stream = BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)
        return output_stream.getvalue()

    def create_summary_page(self, pdf_files, labeled_pdfs, writer):
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        
        # Set up styles
        can.setFont("Helvetica-Bold", 16)
        can.setFillColor(colors.blue)

        y_position = 750
        can.drawString(100, 800, "Summary of Combined PDFs")
        can.setFont("Helvetica-Bold", 12)
        can.setFillColor(colors.black)
        can.drawString(100, 780, "-" * 70)

        can.setFont("Helvetica", 12)
        can.setFillColor(colors.blue)

        for i, filename in enumerate(pdf_files):
            # Remove the file extension for display
            display_name = os.path.splitext(filename)[0]

            # Add the summary entry
            can.drawString(100, y_position, f"{i + 1}. {display_name}")

            # Add outline (bookmark) for each entry (clickable in the PDF)
            writer.add_outline_item(display_name, page_number=len(writer.pages) + i + 1)
            
            y_position -= 20

        can.save()
        packet.seek(0)
        summary_pdf = PdfReader(packet)
        return summary_pdf

    def combine_pdfs(self, pdf_files, labeled_pdfs):
        writer = PdfWriter()

        # Create the summary page and add it to the writer
        summary_pdf = self.create_summary_page(pdf_files, labeled_pdfs, writer)
        summary_page = summary_pdf.pages[0]
        writer.add_page(summary_page)

        for i, pdf_data in enumerate(labeled_pdfs):
            reader = PdfReader(BytesIO(pdf_data))
            for page_num, page in enumerate(reader.pages):
                writer.add_page(page)

        output_stream = BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)
        return output_stream.getvalue()
