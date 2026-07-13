"""不動産賃貸アダプタ(業種依存). スロット定義 + アイテム(ダミー)."""
from __future__ import annotations

from core.models import Item, SlotDef

SLOTS = [
    SlotDef("area", "enum", required=True, question="ご希望のエリアはどちらですか？",
            keywords={"新宿": "新宿", "渋谷": "渋谷", "池袋": "池袋"}),
    SlotDef("layout", "enum", required=True, question="間取りのご希望は？(1K/1LDK/2LDK)",
            keywords={"1K": "1K", "1LDK": "1LDK", "2LDK": "2LDK"}),
    SlotDef("max_rent", "range", required=False, question="家賃の上限はおいくらですか？"),
]

ITEMS = [
    Item("re-001", {"area": "新宿", "layout": "1K", "rent": 95000, "features": "駅近 オートロック 築浅"}),
    Item("re-002", {"area": "新宿", "layout": "1LDK", "rent": 140000, "features": "南向き 静か ペット可"}),
    Item("re-003", {"area": "渋谷", "layout": "1K", "rent": 105000, "features": "駅近 コンビニ近い"}),
    Item("re-004", {"area": "池袋", "layout": "2LDK", "rent": 180000, "features": "広い 静か 公園近い"}),
    Item("re-005", {"area": "新宿", "layout": "1K", "rent": 88000, "features": "格安 バス トイレ別"}),
]


def adapter():
    return {"slots": SLOTS, "items": ITEMS}
