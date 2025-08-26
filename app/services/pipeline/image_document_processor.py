from app.models.schemas import TextResult


class ImageDocumentProcessor:
    def process_image(self, image_bytes: bytes) -> TextResult:
        if not image_bytes:
            return TextResult(extracted_text="", page_count=0, confidence=0.0)
        # TODO: OCR engine (tesseract, PaddleOCR, Triton)
        return TextResult(extracted_text="", page_count=1, confidence=0.0)
