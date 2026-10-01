"""
app/rate_limiter.py - Simple, resilient in-memory sliding window rate limiter.
"""
import time
from collections import defaultdict
from typing import Dict, List

_REQUEST_TIMESTAMPS: Dict[str, List[float]] = defaultdict(list)


def is_rate_limited(client_id: str, limit_per_minute: int = 60) -> bool:
    """
    Checks if client IP/ID has exceeded allowed requests per minute.
    """
    now = time.time()
    cutoff = now - 60.0

    # Prune old timestamps
    timestamps = [t for t in _REQUEST_TIMESTAMPS[client_id] if t > cutoff]
    if len(timestamps) >= limit_per_minute:
        _REQUEST_TIMESTAMPS[client_id] = timestamps
        return True

    timestamps.append(now)
    _REQUEST_TIMESTAMPS[client_id] = timestamps
    return False
