from typing import Any, Dict
from app.models.schemas import ProcessingResult


class AuditLogService:
    def record_event(self, session_id: str, doc_id: str, event: str, details: Dict[str, Any]) -> ProcessingResult:
        # TODO: append to audit sink (DB, Kafka, file)
        _ = (session_id, doc_id, event, details)
        return ProcessingResult(ok=True, status="done", message="logged")
