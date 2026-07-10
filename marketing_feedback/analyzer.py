"""マーケティング・フィードバック(差別化). 対話ログから広告改善示唆を抽出."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class FeedbackReport:
    frequent_needs: Dict[str, List]      # スロット別の頻出値(検索広告KW候補)
    zero_hit_conditions: List[Dict]      # 候補ゼロになった条件(品揃え/LP改善示唆)

    def as_dict(self):
        return {"frequent_needs": self.frequent_needs,
                "zero_hit_conditions": self.zero_hit_conditions}


class FeedbackAnalyzer:
    def analyze(self, dialog_logs: List[Dict], top: int = 3) -> FeedbackReport:
        """dialog_logs: [{"slots": {...}, "hit_count": int}, ...] (匿名セッション単位)."""
        counters: Dict[str, Counter] = {}
        zero_hits: List[Dict] = []
        for log in dialog_logs:
            slots = log.get("slots", {})
            if log.get("hit_count", 0) == 0:
                zero_hits.append(slots)
            for k, v in slots.items():
                counters.setdefault(k, Counter())[str(v)] += 1
        frequent = {k: [val for val, _ in c.most_common(top)] for k, c in counters.items()}
        return FeedbackReport(frequent_needs=frequent, zero_hit_conditions=zero_hits)
