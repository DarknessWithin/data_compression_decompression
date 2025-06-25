import os
import cv2
import pytesseract
from pdf2image import convert_from_path
import tempfile
from PIL import Image

# ✅ Configure Tesseract (for Windows)
if os.name == "nt" and not os.getenv("TESSERACT_PATH_ADDED"):
    tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        os.environ["TESSERACT_PATH_ADDED"] = "1"

# ✅ Optional: Set your Poppler path here (for PDF conversion on Windows)
POPPLER_PATH = r"C:\poppler-24.08.0\Library\bin" if os.name == "nt" else None


def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, 31, 2)
    return gray


def ocr_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"❌ Cannot read image: {image_path}")
    processed = preprocess_image(image)
    return pytesseract.image_to_string(processed, lang='eng')


def ocr_scanned_pdf(pdf_path):
    text = ""
    try:
        with tempfile.TemporaryDirectory() as path:
            images = convert_from_path(
                pdf_path,
                dpi=300,
                output_folder=path,
                poppler_path=POPPLER_PATH  # Only needed on Windows
            )
            for i, img in enumerate(images):
                img_path = os.path.join(path, f"page_{i}.png")
                img.save(img_path, "PNG")
                text += ocr_image(img_path) + "\n\n"
        return text.strip()
    except Exception as e:
        raise RuntimeError(f"❌ OCR failed for PDF: {e}")


def extract_text_from_image(path):
    ext = os.path.splitext(path)[-1].lower()
    if ext in [".png", ".jpg", ".jpeg"]:
        return ocr_image(path)
    elif ext == ".pdf":
        return ocr_scanned_pdf(path)
    else:
        raise ValueError(f"❌ Unsupported image file type: {ext}")
