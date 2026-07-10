"""中途採用求人アダプタ(業種依存). コア変更なし=スロット+アイテムのみで切替可能."""
from __future__ import annotations

from core.models import Item, SlotDef

SLOTS = [
    SlotDef("job_type", "enum", required=True, question="ご希望の職種は？(エンジニア/営業/デザイナー)",
            keywords={"エンジニア": "エンジニア", "営業": "営業", "デザイナー": "デザイナー"}),
    SlotDef("employment", "enum", required=True, question="雇用形態のご希望は？(正社員/契約)",
            keywords={"正社員": "正社員", "契約": "契約"}),
    SlotDef("remote", "enum", required=False, question="リモート勤務を希望しますか？",
            keywords={"リモート": "可", "在宅": "可", "出社": "不可"}),
]

ITEMS = [
    Item("job-001", {"job_type": "エンジニア", "employment": "正社員", "remote": "可"}),
    Item("job-002", {"job_type": "エンジニア", "employment": "契約", "remote": "不可"}),
    Item("job-003", {"job_type": "営業", "employment": "正社員", "remote": "不可"}),
    Item("job-004", {"job_type": "デザイナー", "employment": "正社員", "remote": "可"}),
]


def adapter():
    return {"slots": SLOTS, "items": ITEMS}
