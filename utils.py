# utils.py

import fitz  # PyMuPDF for PDFs
import pytesseract
from PIL import Image
import io
from docx import Document

# Path to tesseract.exe — adjust if needed
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\K Swathi\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

def extract_text_from_docx(filepath):
    doc = Document(filepath)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_pdf(filepath):
    doc = fitz.open(filepath)
    full_text = ""

    for i, page in enumerate(doc):
        print(f"🔍 Reading Page {i + 1}")
        text = page.get_text().strip()

        if text:
            print(f"✅ Text found on Page {i + 1}")
            full_text += text + "\n"
        else:
            print(f"⚠️ No text found on Page {i + 1}, using OCR...")
            pix = page.get_pixmap(dpi=300)
            img_data = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_data))
            ocr_text = pytesseract.image_to_string(image)
            print(f"🧠 OCR result from Page {i + 1}:\n{ocr_text[:80]}...")
            full_text += ocr_text + "\n"

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
