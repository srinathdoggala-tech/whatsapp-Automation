from __future__ import annotations

import time
import random
from typing import Optional
from app.core.config import settings

class ResponseTimingEngine:
    def calculate_delay(self, incoming_count: int = 1, urgency: str = "normal") -> int:
        base_min = settings.MIN_RESPONSE_DELAY
        base_max = settings.MAX_RESPONSE_DELAY
        if urgency == "emergency":
            return 0
        if incoming_count > 3:
            base_min = max(base_min, 2)
            base_max = max(base_max, base_min + 4)
        delay = random.randint(base_min, base_max)
        return min(delay, 60)
