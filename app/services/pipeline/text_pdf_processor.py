from __future__ import annotations

import io
import re
from typing import Optional
import pymupdf  # PyMuPDF
import pymupdf4llm  # type: ignore
from pydantic import BaseModel

# Models
from app.models.schemas import TextResult


class TextPDFProcessor:
    """
    Extracts clean, LLM-friendly Markdown from text-based PDFs.

    Pipeline:
      1) Try PyMuPDF4LLM for Markdown extraction.
      2) Fallback to plain PyMuPDF text if PyMuPDF4LLM is unavailable.
      3) Post-process for cleanliness and German-focused fixes.
    """

    def extract_text(self, pdf_bytes: bytes) -> TextResult:
        if not pdf_bytes:
            return TextResult(extracted_text="", page_count=0, confidence=0.0)

        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        
        page_count = doc.page_count

        # 1) Extract to Markdown (preferred)
        markdown = self._extract_markdown_with_pymupdf4llm(doc)

        # 2) Fallback to raw text if no markdown or lib missing
        if not markdown.strip():
            markdown = self._extract_text_with_pymupdf(doc)

        # 3) Post-process for LLM-friendliness (esp. German docs)
        cleaned = self._postprocess_markdown(markdown)

        # doc.close()

        return TextResult(
            extracted_text=cleaned,
            page_count=page_count,
            confidence=0.9,
            # hard coded dummy value for confidence for now
        )

    # ---------- Internal helpers ----------

    def _extract_markdown_with_pymupdf4llm(self, doc: pymupdf.Document) -> str:
        """
        Returns Markdown if pymupdf4llm is available; otherwise empty string.
        """
        try:
            # API accepts a Document; avoids bytes misinterpretation as filename
            md = pymupdf4llm.to_markdown(doc)
            if isinstance(md, bytes):
                md = md.decode("utf-8", errors="replace")
            return md or ""
        except Exception:
            return ""


    def _extract_text_with_pymupdf(self, doc: pymupdf.Document) -> str:
        """
        Conservative plain-text fallback, stitched as Markdown-ish paragraphs.
        """
        parts = []
        for page in doc:
            # TextPage in "text" mode keeps layout reasonably
            parts.append(page.get_text("text"))
        raw = "\n\n".join(parts)
        # A minimal "markdown wash": normalize multiple blank lines
        raw = re.sub(r"\n{3,}", "\n\n", raw)
        return raw

    def _postprocess_markdown(self, text: str) -> str:
        """
        Cleanups tuned for LLM consumption and German typography.
        - Remove soft hyphens
        - Conservative de-hyphenation across line breaks (ver-\ntrag → vertrag)
        - Normalize bullets
        - Trim trailing spaces & collapse blank lines
        - Insert narrow no-break spaces (U+202F) between numbers and %, €, EUR, common units
        """
        if not text:
            return ""

        t = text

        # Remove soft hyphens
        t = t.replace("\u00ad", "")

        # De-hyphenate word breaks across line breaks
        t = re.sub(r"(?<=\w)-\s*\n\s*(?=\w)", "", t)
        # Normalize mid-word newlines
        t = re.sub(r"(?<=\w)\n(?=\w)", "", t)

        # Normalize list bullets
        t = re.sub(r"^(?:[•·\*\-—]\s*)", "- ", t, flags=re.MULTILINE)

        # Strip trailing spaces on each line
        t = re.sub(r"[ \t]+$", "", t, flags=re.MULTILINE)

        # Collapse >2 blank lines
        t = re.sub(r"\n{3,}", "\n\n", t)

        # Insert narrow NBSP between numbers and units/symbols
        NBSP_NARROW = "\u202F"

        alpha_units = r"(?:EUR|GB|MB|KB|kg|g|mg|km|m|cm|mm|s|ms)"
        symbol_units = r"(?:%|€)"

        # Replace whitespace between number and alpha unit
        t = re.sub(rf"(?<=\d)\s+(?={alpha_units}\b)", NBSP_NARROW, t)
        # Replace whitespace between number and symbol unit
        t = re.sub(rf"(?<=\d)\s+(?={symbol_units})", NBSP_NARROW, t)

        return t

