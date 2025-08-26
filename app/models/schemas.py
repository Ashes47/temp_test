from typing import Any, Dict, Optional, List, Literal
from pydantic import BaseModel, Field


class DocumentData(BaseModel):
    file_bytes: bytes = Field(..., description="Raw file bytes")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(..., ge=0.0, le=1.0)


class ProcessingResult(BaseModel):
    ok: bool = Field(..., description="Overall success")
    status: Literal["queued", "processing", "done", "error"] = "queued"
    message: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class FormatResult(BaseModel):
    format: Literal[
        "pdf", "image", "png", "jpg", "jpeg", "tiff", "gif", "bmp",
        "docx", "pptx", "xlsx", "txt", "md", "html", "unknown"
    ] = "unknown"
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    hints: Dict[str, Any] = Field(default_factory=dict)


class StrategyInstructions(BaseModel):
    pipeline: List[str] = Field(default_factory=list, description="Ordered step IDs")
    params: Dict[str, Any] = Field(default_factory=dict)
    notes: Optional[str] = None


class TextResult(BaseModel):
    extracted_text: str
    page_count: int = 0
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    extras: Dict[str, Any] = Field(default_factory=dict)
