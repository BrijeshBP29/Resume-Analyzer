from pathlib import Path

import fitz


def extract_text_from_pdf(file_path: str) -> str:
    text_parts = []
    with fitz.open(file_path) as document:
        for page in document:
            text_parts.append(page.get_text("text"))
    text = "\n".join(text_parts).strip()

    if text:
        return text

    return try_ocr_pdf(file_path)


def try_ocr_pdf(file_path: str) -> str:
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return ""

    text_parts = []
    with fitz.open(file_path) as document:
        for page in document:
            pix = page.get_pixmap(dpi=200)
            image_path = Path(file_path).with_suffix(f".page-{page.number}.png")
            pix.save(str(image_path))
            try:
                text_parts.append(pytesseract.image_to_string(Image.open(image_path)))
            finally:
                image_path.unlink(missing_ok=True)

    return "\n".join(text_parts).strip()

