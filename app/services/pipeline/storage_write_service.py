from typing import Any, Dict
from app.models.schemas import ProcessingResult


class StorageWriteService:
    def save_processed(self, session_id: str, doc_id: str, content: str, metadata: Dict[str, Any]) -> ProcessingResult:
        # TODO: write to DB / object store
        _ = (session_id, doc_id, content, metadata)
        return ProcessingResult(ok=True, status="done", message="saved")
