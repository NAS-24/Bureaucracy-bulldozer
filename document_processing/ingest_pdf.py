"""
ingest_pdf.py
----------------
Responsibility:
- Take ANY PDF (text or scanned)
- Extract the cleanest possible text
- Output STRICT JSON for the AI Engine

JSON CONTRACT (DO NOT CHANGE):
{
  "contract_text": "<raw extracted text>"
}
"""

import json
from pathlib import Path

import pdfplumber
import pytesseract
from PIL import ImageOps


# ---------------- CONFIG ----------------
PDF_RESOLUTION = 300           # OCR quality (300 DPI is ideal)
TESSERACT_PSM = "--psm 6"      # Assume uniform block of text
# ----------------------------------------


def ocr_page(image):
    """
    Preprocess image and run OCR
    """
    # Convert to grayscale (removes noise, improves OCR)
    gray_image = ImageOps.grayscale(image)

    # OCR with page segmentation mode
    text = pytesseract.image_to_string(
        gray_image,
        config=TESSERACT_PSM
    )

    return text


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extract text from PDF pages.
    - Uses embedded text if available
    - Falls back to OCR for scanned/image pages
    """
    extracted_pages = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()

            if text and text.strip():
                # Text-based PDF
                extracted_pages.append(text)
            else:
                # Scanned PDF → OCR
                page_image = page.to_image(resolution=PDF_RESOLUTION).original
                ocr_text = ocr_page(page_image)
                extracted_pages.append(ocr_text)

    return "\n\n".join(extracted_pages).strip()


def build_ai_input_json(contract_text: str) -> dict:
    """
    STRICT HANDSHAKE JSON
    (Do NOT modify without team agreement)
    """
    return {
        "contract_text": contract_text
    }


def main():
    # ✅ WINDOWS PATH (RAW STRING IS CRITICAL)
    pdf_path = Path(
        r"PATH"
    )

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    # ---- EXTRACT TEXT ----
    contract_text = extract_text_from_pdf(pdf_path)

    if not contract_text:
        raise ValueError("No text could be extracted from the PDF.")

    # ---- BUILD JSON PAYLOAD ----
    ai_input = build_ai_input_json(contract_text)

    # ---- OUTPUT (STDOUT) ----
    # This is piped directly into the AI Core
    print(json.dumps(ai_input, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
