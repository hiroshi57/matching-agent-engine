"""マッチング(差別化の核: 実在IDバリデータ).

候補は必ずアイテムストアに実在する ID のみ。LLM が候補を生成/改変しても、
バリデータが実在しない ID を破棄する(ハルシネーション防止)。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .models import Item
from .vector import embed, cosine


@dataclass
class Match:
    item: Item
    matched_slots: List[str]
    score: float
    vector_sim: float = 0.0


def _item_text(item: Item) -> str:
    # 構造化属性 + 自由文(features)からアイテムのテキスト表現を作る
    parts = [str(v) for v in item.attributes.values()]
    return " ".join(parts)


class ItemStore:
    def __init__(self, items: List[Item]) -> None:
        self._by_id: Dict[str, Item] = {it.id: it for it in items}

    def exists(self, item_id: str) -> bool:
        return item_id in self._by_id

    def get(self, item_id: str) -> Optional[Item]:
        return self._by_id.get(item_id)

    @property
    def items(self) -> List[Item]:
        return list(self._by_id.values())

    def validate_ids(self, candidate_ids: List[str]) -> List[str]:
        """実在する ID のみを残す(LLM が創作した ID は破棄)."""
        return [cid for cid in candidate_ids if cid in self._by_id]


class MatchingEngine:
    def __init__(self, store: ItemStore) -> None:
        self.store = store

    def _satisfies(self, item: Item, slot: str, value) -> bool:
        attr = item.attributes
        if slot == "max_rent":
            return attr.get("rent") is not None and attr["rent"] <= value
        if slot == "max_salary_min":   # 求人: 希望下限給与以上
            return attr.get("salary_min") is not None and attr["salary_min"] >= value
        return attr.get(slot) == value

    def match(self, slots: Dict, top_k: int = 5) -> List[Match]:
        results: List[Match] = []
        for item in self.store.items:
            matched = [s for s, v in slots.items() if self._satisfies(item, s, v)]
            if matched:
                results.append(Match(item, matched, len(matched) / max(1, len(slots))))
        results.sort(key=lambda m: m.score, reverse=True)
        return results[:top_k]

    def match_hybrid(self, slots: Dict, free_text: str = "", top_k: int = 5,
                     w_struct: float = 0.6, w_vec: float = 0.4) -> List[Match]:
        """ハイブリッド検索: 構造化フィルタ(スロット) + 自由文ベクトル類似.

        候補は実在アイテムのみ。構造化被覆率とベクトル類似の重み付き合成でランク付け。
        """
        q_vec = embed(free_text) if free_text else {}
        results: List[Match] = []
        for item in self.store.items:
            matched = [s for s, v in slots.items() if self._satisfies(item, s, v)]
            struct = len(matched) / max(1, len(slots)) if slots else 0.0
            vsim = cosine(q_vec, embed(_item_text(item))) if q_vec else 0.0
            if not matched and vsim == 0.0:
                continue
            score = w_struct * struct + w_vec * vsim
            results.append(Match(item, matched, score, vector_sim=vsim))
        results.sort(key=lambda m: m.score, reverse=True)
        return results[:top_k]

    def safe_candidates(self, candidate_ids: List[str]) -> List[Item]:
        """外部(LLM)由来の候補IDを検証し、実在アイテムのみ返す."""
        valid = self.store.validate_ids(candidate_ids)
        return [self.store.get(cid) for cid in valid]
