from app.models.schemas import DocumentData, FormatResult


class DocumentFormatDetectionService:
    def detect_format(self, document_data: DocumentData) -> FormatResult:
        # Very light heuristic stub
        meta_fmt = (document_data.metadata.get("inferred_ext") or "").lower()
        if meta_fmt in {"pdf"}:
            return FormatResult(format="pdf", confidence=0.95)
        if meta_fmt in {"png", "jpg", "jpeg", "gif", "bmp", "tiff"}:
            return FormatResult(format=meta_fmt, confidence=0.9)
        return FormatResult()
