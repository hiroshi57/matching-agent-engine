"""対話マネージャ(業種非依存). 発話->スロット抽出、不足スロットの質問生成.

1ターン1問、最大5ターンで候補提示に移る。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .models import SlotDef

# 金額は必ず単位(万円/万/円)を伴うもののみ採用("1K"の1を誤検出しない)
_MONEY_RE = re.compile(r"(\d[\d,]*)\s*(万円|万|円)")


@dataclass
class DialogState:
    slots: Dict = field(default_factory=dict)
    turns: int = 0


class DialogManager:
    def __init__(self, slot_defs: List[SlotDef], max_turns: int = 5) -> None:
        self.slot_defs = slot_defs
        self.max_turns = max_turns

    def extract(self, utterance: str, state: DialogState) -> DialogState:
        state.turns += 1
        for sd in self.slot_defs:
            if sd.name in state.slots:
                continue
            if sd.type == "enum":
                for surface, norm in sd.keywords.items():
                    if surface in utterance:
                        state.slots[sd.name] = norm
                        break
            elif sd.type == "range":
                m = _MONEY_RE.search(utterance)
                if m and sd.name in ("max_rent",) and ("以下" in utterance or "まで" in utterance or "予算" in utterance):
                    val = int(m.group(1).replace(",", ""))
                    if m.group(2) in ("万円", "万"):
                        val *= 10000
                    state.slots[sd.name] = val
        return state

    def next_question(self, state: DialogState) -> Optional[str]:
        if state.turns >= self.max_turns:
            return None   # 打ち切り、候補提示へ
        for sd in self.slot_defs:
            if sd.required and sd.name not in state.slots:
                return sd.question
        return None

    def ready(self, state: DialogState) -> bool:
        return self.next_question(state) is None
