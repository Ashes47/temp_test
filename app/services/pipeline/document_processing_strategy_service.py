from app.models.schemas import StrategyInstructions


class DocumentProcessingStrategyService:
    def process_document(self, document_type: str, file_bytes: bytes) -> StrategyInstructions:
        dt = document_type.strip().lower()
        if dt == "pdf":
            return StrategyInstructions(
                pipeline=["pdf_text_extract", "text_cleanup"],
                params={"ocr": False},
                notes="Direct text layer, fallback to OCR if empty."
            )
        if dt in {"png", "jpg", "jpeg"}:
            return StrategyInstructions(
                pipeline=["image_ocr", "text_cleanup"],
                params={"ocr": True},
                notes="Image OCR path."
            )
        return StrategyInstructions(pipeline=["generic_detect", "maybe_ocr"], notes="Best-effort fallback.")
