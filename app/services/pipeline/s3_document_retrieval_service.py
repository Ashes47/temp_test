from typing import Any
from app.models.schemas import DocumentData


class S3DocumentRetrievalService:
    def download_document(self, s3_url: str, **kwargs: Any) -> DocumentData:
        # TODO: real S3 download (boto3, presigned URLs, etc.)
        return DocumentData(file_bytes=b"", metadata={"s3_url": s3_url, **kwargs}, confidence=0.0)
