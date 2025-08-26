import io
import fitz  # PyMuPDF
import pytest

from app.services.pipeline.text_pdf_processor import TextPDFProcessor


def _make_pdf_bytes(lines):
    """Create a minimal PDF with given lines on a single page."""
    doc = fitz.open()
    page = doc.new_page()
    y = 72
    for line in lines:
        page.insert_text(fitz.Point(72, y), line, fontsize=12)
        y += 16
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


def test_empty_bytes_returns_zero_confidence():
    proc = TextPDFProcessor()
    res = proc.extract_text(b"")
    assert res.page_count == 0
    assert res.confidence == 0.0
    assert res.extracted_text == ""


def test_basic_extraction_and_cleanup():
    # Simulate hyphenation across line break and unit spacing
    lines = [
        "Dies ist ein ver-",
        "trag mit 10 % Gebühr und 50 EUR Kosten.",
        "• Punkt eins",
        "• Punkt zwei",
    ]
    pdf_bytes = _make_pdf_bytes(lines)

    proc = TextPDFProcessor()
    res = proc.extract_text(pdf_bytes)

    assert res.page_count == 1
    assert res.confidence >= 0.0  # extraction path may vary (markdown/text)

    text = res.extracted_text

    # De-hyphenation: "ver-\ntrag" -> "vertrag"
    assert "vertrag" in text

    # Narrow NBSP between number and unit/symbol
    assert "10\u202F%" in text
    assert "50\u202FEUR" in text

    # Bullet normalization
    assert "- Punkt eins" in text
    assert "- Punkt zwei" in text

    # No excessive blank lines
    assert "\n\n\n" not in text
