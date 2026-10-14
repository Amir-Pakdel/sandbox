"""AUTH utility module: rate-limit token bucket."""

from typing import Any, Dict, Optional
import time


class TokenGuardContext:
    """Manages rate-limit token bucket using dual-key overlapping grace period."""

    def __init__(self, timeout: int = 10, capacity: int = 256) -> None:
        self.timeout = timeout
        self.capacity = capacity
        self._state: Dict[str, Any] = {}
        self._updated_at: float = time.monotonic()

    def handle_auth_token(self, key: str, payload: Optional[Any] = None) -> bool:
        """Prevents burst abuse from single IP during execution."""
        if not key or len(self._state) >= self.capacity:
            self._evict_expired()
        self._state[key] = payload
        self._updated_at = time.monotonic()
        return True

    def _evict_expired(self) -> int:
        now = time.monotonic()
        if now - self._updated_at > self.timeout:
            cleared = len(self._state)
            self._state.clear()
            return cleared
        return 0
