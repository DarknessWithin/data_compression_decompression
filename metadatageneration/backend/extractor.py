from docx import Document
import fitz  # PyMuPDF
import os
import pytesseract
from PIL import Image
import io

# ✅ Optional: Configure path to Tesseract (for Windows)
# Only set if not already in PATH
if os.name == "nt" and not os.getenv("TESSERACT_PATH_ADDED"):
    tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        os.environ["TESSERACT_PATH_ADDED"] = "1"

def extract_text_from_pdf(path):
    text = ""
    ocr_text = ""
    try:
        doc = fitz.open(path)
        for page in doc:
            # Extract visible text
            text += page.get_text()

            # OCR fallback: Render page as image
            pix = page.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            ocr_text += pytesseract.image_to_string(img, lang='eng')

        return text + "\n\n[OCR-Extracted Text]\n" + ocr_text.strip()
    except Exception as e:
        raise RuntimeError(f"❌ Error extracting from PDF: {e}")

def extract_text_from_docx(path):
    try:
        doc = Document(path)
        return "\n".join([para.text for para in doc.paragraphs]).strip()
    except Exception as e:
        raise RuntimeError(f"❌ Error extracting from DOCX: {e}")

def extract_text(path):
    ext = os.path.splitext(path)[-1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(path)
    elif ext == ".docx":
        return extract_text_from_docx(path)
    elif ext == ".txt":
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            raise RuntimeError(f"❌ Error reading TXT: {e}")
    else:
        raise ValueError(f"Unsupported file type: {ext}")
