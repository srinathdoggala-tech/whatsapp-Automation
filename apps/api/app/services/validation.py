from __future__ import annotations

from typing import Optional
from app.schemas.schemas import ApprovalResponse

class ValidationService:
    def __init__(self, confidence_threshold: float = 0.7, max_length: int = 500):
        self.confidence_threshold = confidence_threshold
        self.max_length = max_length

    def validate_candidate(self, response: str, confidence: float) -> tuple[bool, Optional[str]]:
        if not response or not response.strip():
            return False, "empty_response"
        if len(response) > self.max_length:
            return False, "response_too_long"
        if confidence < self.confidence_threshold:
            return False, "low_confidence"
        return True, None

    def to_approval_if_needed(self, *, confidence: float, needs_review: bool, response: str) -> tuple[bool, Optional[str]]:
        if needs_review:
            return True, "needs_review"
        ok, reason = self.validate_candidate(response, confidence)
        if not ok:
            return True, reason
        return False, None
