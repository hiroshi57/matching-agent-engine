import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from marketing_feedback import analyze_uplift, top_targeting_recommendations  # noqa: E402


def _logs():
    logs = []
    # 新宿×1K は成約しやすい / 池袋は成約しにくい構成
    for _ in range(6):
        logs.append({"slots": {"area": "新宿", "layout": "1K"}, "converted": True})
    for _ in range(4):
        logs.append({"slots": {"area": "新宿", "layout": "1K"}, "converted": False})
    for _ in range(5):
        logs.append({"slots": {"area": "池袋", "layout": "2LDK"}, "converted": False})
    return logs


def test_uplift_positive_for_converting_condition():
    items = {(i.slot, i.value): i for i in analyze_uplift(_logs())}
    shinjuku = items[("area", "新宿")]
    assert shinjuku.uplift > 0            # 新宿は成約率を引き上げる
    ikebukuro = items[("area", "池袋")]
    assert ikebukuro.uplift < 0           # 池袋は下げる


def test_min_support_filters_rare():
    logs = _logs() + [{"slots": {"area": "渋谷"}, "converted": True}]  # support=1
    items = [i for i in analyze_uplift(logs, min_support=3)]
    assert all(i.support >= 3 for i in items)
    assert not any(i.value == "渋谷" for i in items)


def test_sorted_by_uplift_desc():
    items = analyze_uplift(_logs())
    ups = [i.uplift for i in items]
    assert ups == sorted(ups, reverse=True)


def test_targeting_recommendations_positive_only():
    recs = top_targeting_recommendations(_logs())
    assert recs
    assert all(r["uplift"] > 0 for r in recs)
    assert "訴求" in recs[0]["recommendation"]


def test_empty_logs():
    assert analyze_uplift([]) == []
