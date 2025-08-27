import io
from pathlib import Path
import pymupdf  # PyMuPDF
import pytest

from app.services.pipeline.text_pdf_processor import TextPDFProcessor


def _make_pdf_bytes(lines):
    """Create a minimal PDF with given lines on a single page."""
    doc = pymupdf.open()
    page = doc.new_page()
    y = 72
    for line in lines:
        page.insert_text(pymupdf.Point(72, y), line, fontsize=12)
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


def test_real_pdfs_extraction_matches_expected_markdown():
    root = Path(__file__).resolve().parents[1]
    pdf_dir = root / "tests/test_pdfs"
    md_dir = root / "tests/test_pdf_markdowns"

    # Add more pairs as needed
    pdf_md_pairs = [
        ("German-SQP.pdf", "German-SQP.extracted.md"),
        # ("Another.pdf", "Another.extracted.md"),
    ]

    proc = TextPDFProcessor()

    for pdf_name, md_name in pdf_md_pairs:
        pdf_path = pdf_dir / pdf_name
        if not pdf_path.exists():
            pytest.skip(f"{pdf_name} not present in {pdf_dir}")

        pdf_bytes = pdf_path.read_bytes()
        res = proc.extract_text(pdf_bytes)

        # Basic sanity checks
        assert res.page_count >= 1
        assert res.confidence >= 0.0
        assert isinstance(res.extracted_text, str)
        assert len(res.extracted_text) > 50
        assert "\n\n\n" not in res.extracted_text

        # Uncomment this block once to generate the expected .extracted.md files
        # out_path = md_dir / (pdf_path.stem + ".extracted.md")
        # out_path.write_text(res.extracted_text, encoding="utf-8")
        # print(f"Extracted text written to: {out_path}")

        expected_path = md_dir / md_name
        if not expected_path.exists():
            pytest.skip(f"Expected markdown missing: {expected_path}. Generate it using the commented code above.")
        expected_text = expected_path.read_text(encoding="utf-8")
        assert res.extracted_text == expected_text
