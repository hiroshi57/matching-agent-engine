"""コア共通モデル(業種非依存)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SlotDef:
    name: str
    type: str                # enum / range / text
    required: bool
    question: str
    keywords: Dict[str, str] = field(default_factory=dict)  # enum: 表層->正規値


@dataclass(frozen=True)
class Item:
    id: str
    attributes: Dict          # 例: {"area":"新宿","rent":95000,"layout":"1K"}
