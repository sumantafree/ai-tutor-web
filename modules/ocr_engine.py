"""
OCR Engine - Extract text from PDFs and images
Uses pytesseract and pdfplumber/PyPDF2
"""

import os
import io

# ─────────────────────────────────────────────────────────
# SAFE IMPORTS
# ─────────────────────────────────────────────────────────

def _try_import_pytesseract():
    try:
        import pytesseract
        # Try common Tesseract paths on Windows
        tesseract_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Users\USER\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
        ]
        for path in tesseract_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                break
        return pytesseract
    except ImportError:
        return None

def _try_import_pdfplumber():
    try:
        import pdfplumber
        return pdfplumber
    except ImportError:
        return None

def _try_import_pypdf2():
    try:
        import PyPDF2
        return PyPDF2
    except ImportError:
        return None

def _try_import_pil():
    try:
        from PIL import Image
        return Image
    except ImportError:
        return None

# ─────────────────────────────────────────────────────────
# TEXT EXTRACTION FUNCTIONS
# ─────────────────────────────────────────────────────────

def extract_text_from_pdf(file_path_or_bytes):
    """
    Extract text from a PDF file.
    Accepts file path (str) or bytes object.
    Returns extracted text string.
    """
    text = ""

    # Try pdfplumber first (best quality)
    pdfplumber = _try_import_pdfplumber()
    if pdfplumber:
        try:
            if isinstance(file_path_or_bytes, (bytes, bytearray)):
                import io
                with pdfplumber.open(io.BytesIO(file_path_or_bytes)) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            else:
                with pdfplumber.open(file_path_or_bytes) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            if text.strip():
                return text.strip()
        except Exception:
            pass

    # Try PyPDF2 as fallback
    PyPDF2 = _try_import_pypdf2()
    if PyPDF2:
        try:
            if isinstance(file_path_or_bytes, (bytes, bytearray)):
                import io
                reader = PyPDF2.PdfReader(io.BytesIO(file_path_or_bytes))
            else:
                reader = PyPDF2.PdfReader(file_path_or_bytes)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            if text.strip():
                return text.strip()
        except Exception:
            pass

    return text or "[Could not extract text from PDF. Try OCR or use a text-based PDF.]"


def extract_text_from_image(file_path_or_bytes):
    """
    Extract text from an image using OCR (pytesseract).
    Returns extracted text string.
    """
    Image = _try_import_pil()
    pytesseract = _try_import_pytesseract()

    if not Image or not pytesseract:
        return "[OCR not available. Install pytesseract and Tesseract-OCR to extract text from images.]"

    try:
        if isinstance(file_path_or_bytes, (bytes, bytearray)):
            img = Image.open(io.BytesIO(file_path_or_bytes))
        else:
            img = Image.open(file_path_or_bytes)

        # Enhance image for better OCR
        img = img.convert("RGB")

        # Run OCR
        text = pytesseract.image_to_string(img, lang='eng')
        return text.strip() if text.strip() else "[No text found in image]"
    except Exception as e:
        return f"[OCR error: {str(e)}]"


def extract_text_from_file(uploaded_file):
    """
    Universal text extractor for Streamlit UploadedFile objects.
    Supports PDF, JPG, JPEG, PNG files.
    Returns (extracted_text, content_type)
    """
    filename = uploaded_file.name.lower()
    file_bytes = uploaded_file.read()

    if filename.endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
        return text, "pdf"
    elif filename.endswith((".jpg", ".jpeg", ".png", ".bmp", ".tiff")):
        text = extract_text_from_image(file_bytes)
        return text, "image"
    elif filename.endswith(".txt"):
        try:
            text = file_bytes.decode("utf-8", errors="ignore")
            return text, "text"
        except Exception:
            return "[Could not read text file]", "text"
    else:
        return "[Unsupported file format. Please use PDF, JPG, PNG, or TXT files.]", "unknown"


def extract_chapters_from_text(text, subject=""):
    """
    Try to extract chapter structure from text.
    Returns list of {"title": str, "content": str}
    """
    import re
    chapters = []

    # Common chapter patterns
    patterns = [
        r'(?i)^(chapter\s+\d+[\s:.-]+.+)$',
        r'(?i)^(\d+[\s.]+[A-Z].{5,60})$',
        r'(?i)^(unit\s+\d+[\s:.-]+.+)$',
        r'(?i)^(lesson\s+\d+[\s:.-]+.+)$',
    ]

    lines = text.split('\n')
    current_chapter = {"title": "Introduction", "content": ""}
    chapter_started = False

    for line in lines:
        line_stripped = line.strip()
        is_chapter_header = False

        for pattern in patterns:
            if re.match(pattern, line_stripped) and len(line_stripped) < 100:
                is_chapter_header = True
                break

        if is_chapter_header:
            if chapter_started and current_chapter["content"].strip():
                chapters.append(current_chapter)
            current_chapter = {"title": line_stripped, "content": ""}
            chapter_started = True
        else:
            current_chapter["content"] += line + "\n"

    # Add last chapter
    if current_chapter["content"].strip():
        chapters.append(current_chapter)

    # If no chapters detected, treat whole text as one chapter
    if not chapters:
        chapters = [{"title": f"{subject} Content" if subject else "Uploaded Content",
                     "content": text}]

    return chapters


def save_processed_content(subject, filename, text, processed_dir):
    """Save processed text content to a file."""
    os.makedirs(processed_dir, exist_ok=True)
    safe_name = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in filename)
    output_path = os.path.join(processed_dir, f"{subject}_{safe_name}.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    return output_path


def get_ocr_status():
    """Return status of OCR dependencies."""
    status = {}
    status["pdfplumber"] = _try_import_pdfplumber() is not None
    status["PyPDF2"] = _try_import_pypdf2() is not None
    status["PIL"] = _try_import_pil() is not None
    status["pytesseract"] = _try_import_pytesseract() is not None
    return status
