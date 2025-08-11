# utils.py

import fitz  # PyMuPDF for PDFs
import pytesseract
from PIL import Image
import io
from docx import Document

# On Linux (Render), no need to set tesseract_cmd manually unless using custom path
# pytesseract.pytesseract.tesseract_cmd = r'C:\path\to\tesseract.exe'  # Windows only

def extract_text_from_docx(filepath):
    doc = Document(filepath)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_pdf(filepath):
    doc = fitz.open(filepath)
    full_text = ""

    for i, page in enumerate(doc):
        text = page.get_text().strip()

        if text:
            full_text += text + "\n"
        else:
            try:
                pix = page.get_pixmap(dpi=300)
                img_data = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_data))
                ocr_text = pytesseract.image_to_string(image)
                full_text += ocr_text + "\n"
            except Exception as e:
                full_text += f"[OCR Failed: {e}]\n"

    return full_text

def extract_text(filepath):
    if filepath.endswith(".docx"):
        return extract_text_from_docx(filepath)
    elif filepath.endswith(".pdf"):
        return extract_text_from_pdf(filepath)
    elif filepath.endswith(".txt"):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return "Unsupported file format."
