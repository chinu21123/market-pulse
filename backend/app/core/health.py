from datetime import datetime, timezone
from threading import Lock
from typing import Dict


class DependencyHealth:
    def __init__(self) -> None:
        self._lock = Lock()
        self._states: Dict[str, Dict[str, str]] = {
            "database": {"status": "HEALTHY", "detail": ""},
            "market_data": {"status": "HEALTHY", "detail": ""},
            "gemini": {"status": "HEALTHY", "detail": ""},
            "cache": {"status": "HEALTHY", "detail": ""},
        }

    def mark(self, dependency: str, status: str, detail: str = "") -> None:
        with self._lock:
            self._states[dependency] = {
                "status": status,
                "detail": detail,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }

    def snapshot(self) -> Dict[str, Dict[str, str]]:
        with self._lock:
            return {name: state.copy() for name, state in self._states.items()}


health_registry = DependencyHealth()
