"""永続化層(SQLite, 標準ライブラリ). アイテム + イベントログ. テナント分離."""
from __future__ import annotations

import json
import sqlite3
from typing import Dict, List, Optional

from core.models import Item

SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL,
    item_id TEXT NOT NULL,
    adapter TEXT NOT NULL,
    attributes TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    type TEXT NOT NULL,
    payload TEXT NOT NULL
);
"""


class ServiceDB:
    def __init__(self, path: str = ":memory:") -> None:
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def load_items(self, tenant_id: str, adapter: str, items: List[Item]) -> int:
        for it in items:
            self.conn.execute(
                "INSERT INTO items(tenant_id, item_id, adapter, attributes) VALUES (?,?,?,?)",
                (tenant_id, it.id, adapter, json.dumps(it.attributes, ensure_ascii=False)))
        self.conn.commit()
        return len(items)

    def get_items(self, tenant_id: str, adapter: str) -> List[Item]:
        rows = self.conn.execute(
            "SELECT item_id, attributes FROM items WHERE tenant_id=? AND adapter=?",
            (tenant_id, adapter)).fetchall()
        return [Item(r["item_id"], json.loads(r["attributes"])) for r in rows]

    def record_event(self, tenant_id: str, session_id: str, type: str, payload: Dict) -> int:
        cur = self.conn.execute(
            "INSERT INTO events(tenant_id, session_id, type, payload) VALUES (?,?,?,?)",
            (tenant_id, session_id, type, json.dumps(payload, ensure_ascii=False)))
        self.conn.commit()
        return cur.lastrowid

    def get_events(self, tenant_id: str) -> List[Dict]:
        rows = self.conn.execute(
            "SELECT session_id, type, payload FROM events WHERE tenant_id=?", (tenant_id,)).fetchall()
        return [{"session_id": r["session_id"], "type": r["type"],
                 "payload": json.loads(r["payload"])} for r in rows]

    def close(self) -> None:
        self.conn.close()
