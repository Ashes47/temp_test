from typing import Any, Dict
from app.models.schemas import ProcessingResult


class WebhookNotifierService:
    def notify(self, callback_url: str, payload: Dict[str, Any]) -> ProcessingResult:
        # TODO: POST to callback_url with retries / signing
        _ = (callback_url, payload)
        return ProcessingResult(ok=True, status="done", message="queued for delivery")
    