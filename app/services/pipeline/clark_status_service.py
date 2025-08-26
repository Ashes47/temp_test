from app.models.schemas import ProcessingResult


class ClarkStatusService:
    def update_status(self, session_id: str, doc_id: str, status: str) -> ProcessingResult:
        # TODO: persist in DB / emit event
        normalized = status.strip().lower()
        ok = normalized in {"queued", "processing", "done", "error"}
        return ProcessingResult(ok=ok, status=normalized if ok else "error",
                                message=None if ok else f"invalid status: {status}")
    