import re
from app.models.schemas import TextResult


class TextCleanupService:
    def cleanup(self, text: str) -> TextResult:
        if not text:
            return TextResult(extracted_text="", page_count=0, confidence=0.0)
        # Basic normalizations; extend per your German rules etc.
        cleaned = text.replace("\u00ad", "")                      # soft hyphen
        cleaned = re.sub(r"[ \t]+\n", "\n", cleaned)              # strip trailing spaces
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)              # collapse blank lines
        return TextResult(extracted_text=cleaned, page_count=0, confidence=0.99)
