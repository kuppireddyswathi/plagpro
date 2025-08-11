from fpdf import FPDF
# exporter.py
import os

# ✅ Step 1: Clean function
def clean_text(text):
    return text.encode("utf-8", "ignore").decode("utf-8", "ignore")


class PDFExporter:
    def __init__(self, title="ProofWise AI - Paraphrased Document"):
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.title = title
        self.pdf.add_page()

        font_path = os.path.join("fonts", "DejaVuSans.ttf")
        self.pdf.add_font("DejaVu", "", font_path, uni=True)
        self.pdf.set_font("DejaVu", "", 12)

    def header(self):
        self.pdf.set_font("DejaVu", "", 16)
        self.pdf.cell(0, 10, self.title, ln=True, align='C')
        self.pdf.ln(10)

    def add_paraphrased_text(self, content):
        paragraphs = content.split('\n')
        for para in paragraphs:
            if para.strip():
                self.pdf.multi_cell(0, 10, para.strip())
                self.pdf.ln(5)

    def generate_report(self, paraphrased_text):
        self.header()
        clean_para = clean_text(paraphrased_text)
        self.add_paraphrased_text(clean_para or "⚠️ No paraphrased content.")
        return self

    def export(self, output_path):
        self.pdf.output(output_path)
