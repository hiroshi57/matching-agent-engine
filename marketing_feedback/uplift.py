"""成約寄与条件の uplift 分析(尖った武器).

対話ログ(スロット条件 + 成約有無)から、各条件値が成約率をどれだけ引き上げるか(uplift)を
定量化し、広告ターゲティング/クリエイティブ訴求の優先順位を出す。
標準ライブラリのみ。
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class UpliftItem:
    slot: str
    value: str
    with_rate: float          # その条件を含むセッションの成約率
    without_rate: float       # 含まないセッションの成約率
    uplift: float             # with - without
    support: int              # その条件のサンプル数

    def as_dict(self):
        return {"slot": self.slot, "value": self.value,
                "with_rate": round(self.with_rate, 3), "without_rate": round(self.without_rate, 3),
                "uplift": round(self.uplift, 3), "support": self.support}


def analyze_uplift(logs: List[Dict], min_support: int = 3) -> List[UpliftItem]:
    """logs: [{"slots": {slot: value}, "converted": bool}, ...]

    各 (slot, value) について、含む群と含まない群の成約率差(uplift)を算出する。
    """
    n = len(logs)
    if n == 0:
        return []
    # (slot,value) -> [converted...]
    with_group: Dict[tuple, List[int]] = defaultdict(list)
    all_conv = [1 if lg.get("converted") else 0 for lg in logs]
    total_conv = sum(all_conv)

    for lg in logs:
        conv = 1 if lg.get("converted") else 0
        for slot, value in lg.get("slots", {}).items():
            with_group[(slot, str(value))].append(conv)

    items: List[UpliftItem] = []
    for (slot, value), convs in with_group.items():
        support = len(convs)
        if support < min_support:
            continue
        with_rate = sum(convs) / support
        without_n = n - support
        without_rate = (total_conv - sum(convs)) / without_n if without_n > 0 else 0.0
        items.append(UpliftItem(slot=slot, value=value, with_rate=with_rate,
                                without_rate=without_rate, uplift=with_rate - without_rate,
                                support=support))
    items.sort(key=lambda x: x.uplift, reverse=True)
    return items


def top_targeting_recommendations(logs: List[Dict], top_n: int = 5, min_support: int = 3) -> List[Dict]:
    """uplift の高い条件を「広告ターゲティング推奨」として返す."""
    items = analyze_uplift(logs, min_support=min_support)
    recs = []
    for it in items[:top_n]:
        if it.uplift > 0:
            recs.append({**it.as_dict(),
                         "recommendation": f"{it.slot}={it.value} を訴求(成約率+{it.uplift:.0%})"})
    return recs
