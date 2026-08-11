"""Application tracking with a durable, session-safe store.

The original implementation wrote to ``applied_jobs.json`` in the working
directory and re-read it on every rerun. On Streamlit Community Cloud that
filesystem is ephemeral/read-only, so "Mark applied" silently did nothing.

This store keeps session state authoritative, mirrors to disk as a best-effort
backup, and never raises when the disk is unavailable.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .text import canonical_url

__all__ = ["Application", "ApplicationStore", "STATUS_FLOW", "default_store_path"]


def default_store_path() -> str:
    """Where applications are mirrored on disk.

    Overridable with ``CAREEROS_DATA_FILE`` so tests (and multi-user
    deployments) never write into the application directory.
    """
    return os.environ.get("CAREEROS_DATA_FILE", "applied_jobs.json")

STATUS_FLOW = [
    "Applied",
    "Screening",
    "Interview",
    "Offer",
    "Rejected",
    "Withdrawn",
]


@dataclass
class Application:
    url: str
    title: str = ""
    company: str = ""
    location: str = ""
    source: str = ""
    match_score: int = 0
    status: str = "Applied"
    notes: str = ""
    applied_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, url: str, data: Dict) -> "Application":
        known = {f for f in cls(url="").to_dict()}
        payload = {k: v for k, v in (data or {}).items() if k in known}
        payload["url"] = url
        # Backwards compatibility with the old {"date": ...} shape.
        if not payload.get("applied_at"):
            payload["applied_at"] = (data or {}).get("date", "")
        return cls(**payload)


class ApplicationStore:
    """Dict-backed store with optional JSON persistence."""

    def __init__(self, data: Optional[Dict] = None, path: Optional[str] = None):
        self.path = path or default_store_path()
        self._data: Dict[str, Application] = {}
        self.persistent = True
        for url, payload in (data or {}).items():
            self._data[canonical_url(url) or url] = Application.from_dict(url, payload)

    # -- persistence -------------------------------------------------------
    @classmethod
    def load(cls, path: Optional[str] = None) -> "ApplicationStore":
        path = path or default_store_path()
        try:
            with open(path, "r", encoding="utf-8") as handle:
                raw = json.load(handle)
            if not isinstance(raw, dict):
                raw = {}
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            raw = {}
        return cls(raw, path=path)

    def save(self) -> bool:
        """Atomically write to disk. Returns False when storage is read-only."""
        payload = self.to_dict()
        try:
            directory = os.path.dirname(os.path.abspath(self.path)) or "."
            with tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", dir=directory, delete=False, suffix=".tmp"
            ) as handle:
                json.dump(payload, handle, indent=2, ensure_ascii=False)
                temp_path = handle.name
            os.replace(temp_path, self.path)
            self.persistent = True
            return True
        except (OSError, TypeError, ValueError):
            self.persistent = False
            return False

    # -- data access -------------------------------------------------------
    def to_dict(self) -> Dict:
        return {app.url: app.to_dict() for app in self._data.values()}

    def __len__(self) -> int:
        return len(self._data)

    def __contains__(self, url: object) -> bool:
        return (canonical_url(url) or str(url)) in self._data

    def urls(self) -> List[str]:
        return [app.url for app in self._data.values()]

    def canonical_urls(self) -> set:
        return set(self._data.keys())

    def all(self) -> List[Application]:
        return sorted(
            self._data.values(),
            key=lambda a: a.updated_at or a.applied_at,
            reverse=True,
        )

    def get(self, url: str) -> Optional[Application]:
        return self._data.get(canonical_url(url) or url)

    # -- mutations ---------------------------------------------------------
    def add(
        self,
        url: str,
        title: str = "",
        company: str = "",
        location: str = "",
        source: str = "",
        match_score: int = 0,
        notes: str = "",
        status: str = "Applied",
    ) -> Application:
        now = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
        key = canonical_url(url) or url
        existing = self._data.get(key)
        app = Application(
            url=url or key,
            title=title or (existing.title if existing else ""),
            company=company or (existing.company if existing else ""),
            location=location or (existing.location if existing else ""),
            source=source or (existing.source if existing else ""),
            match_score=match_score or (existing.match_score if existing else 0),
            status=status,
            notes=notes or (existing.notes if existing else ""),
            applied_at=(existing.applied_at if existing else now),
            updated_at=now,
        )
        self._data[key] = app
        self.save()
        return app

    def update(self, url: str, **changes) -> Optional[Application]:
        key = canonical_url(url) or url
        app = self._data.get(key)
        if app is None:
            return None
        for field_name, value in changes.items():
            if hasattr(app, field_name) and value is not None:
                setattr(app, field_name, value)
        app.updated_at = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
        self.save()
        return app

    def remove(self, url: str) -> bool:
        key = canonical_url(url) or url
        if key in self._data:
            del self._data[key]
            self.save()
            return True
        return False

    # -- reporting ---------------------------------------------------------
    def stats(self) -> Dict[str, int]:
        counts = {status: 0 for status in STATUS_FLOW}
        for app in self._data.values():
            counts[app.status] = counts.get(app.status, 0) + 1
        counts["Total"] = len(self._data)
        active = sum(counts.get(s, 0) for s in ("Applied", "Screening", "Interview", "Offer"))
        counts["Active"] = active
        return counts
