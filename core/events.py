"""イベントログ. 発話・抽出スロット・提示候補・クリック・離脱を記録(匿名セッション単位)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Event:
    session_id: str
    type: str        # utterance / slots / presented / click / exit
    payload: Dict

    def as_dict(self):
        return {"session_id": self.session_id, "type": self.type, "payload": self.payload}


class EventLog:
    def __init__(self) -> None:
        self._events: List[Event] = []

    def record(self, session_id: str, type: str, payload: Dict) -> Event:
        e = Event(session_id, type, payload)
        self._events.append(e)
        return e

    @property
    def events(self) -> List[Event]:
        return list(self._events)

    def by_type(self, type: str) -> List[Event]:
        return [e for e in self._events if e.type == type]
