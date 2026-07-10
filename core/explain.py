"""理由生成(差別化). アイテム属性とスロットの対応のみから理由を作る.

属性にない情報は足さない(創作防止)。属性照合で検証可能。
"""
from __future__ import annotations

from typing import Dict, List

from .matching import Match

_LABEL = {"area": "エリア", "layout": "間取り", "max_rent": "家賃", "rent": "家賃",
          "employment": "雇用形態", "remote": "リモート", "job_type": "職種"}


def explain(match: Match, slots: Dict) -> Dict:
    reasons: List[str] = []
    attr = match.item.attributes
    for s in match.matched_slots:
        label = _LABEL.get(s, s)
        if s == "max_rent":
            reasons.append(f"{label} {attr.get('rent')}円 が希望({slots[s]}円以下)に合致")
        else:
            reasons.append(f"{label} が「{attr.get(s, slots.get(s))}」で希望に合致")
    return {"id": match.item.id, "reasons": reasons, "attributes": dict(attr)}


def verify_no_fabrication(explanation: Dict, item_attributes: Dict) -> bool:
    """理由がアイテム属性に含まれる情報のみで構成されているか(創作なし)を検証."""
    return explanation["attributes"] == item_attributes
