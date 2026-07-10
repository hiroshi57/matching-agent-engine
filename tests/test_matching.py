import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import ItemStore, MatchingEngine, DialogManager, DialogState, explain, verify_no_fabrication  # noqa: E402
from adapters import load  # noqa: E402
from marketing_feedback import FeedbackAnalyzer  # noqa: E402


def _re_engine():
    ad = load("real_estate")
    return MatchingEngine(ItemStore(ad["items"])), ad


def test_real_id_validator_discards_hallucinated():
    engine, _ = _re_engine()
    safe = engine.safe_candidates(["re-001", "re-999", "fake", "re-003"])
    ids = [i.id for i in safe]
    assert ids == ["re-001", "re-003"]     # 実在しないIDは破棄


def test_all_matches_are_real_items():
    engine, ad = _re_engine()
    real_ids = {i.id for i in ad["items"]}
    matches = engine.match({"area": "新宿", "layout": "1K"}, top_k=10)
    assert matches
    for m in matches:
        assert m.item.id in real_ids       # 提示は実在IDのみ


def test_max_rent_range_filter():
    engine, _ = _re_engine()
    matches = engine.match({"area": "新宿", "layout": "1K", "max_rent": 90000})
    # 新宿1Kで9万以下 = re-005(88000)のみ(re-001は95000で除外)
    ids = {m.item.id for m in matches if "max_rent" in m.matched_slots}
    assert "re-005" in ids
    assert "re-001" not in ids


def test_adapter_switch_without_code_change():
    # 不動産->求人の切替がアダプタ(slots+items)のみで動く
    re_ad = load("real_estate")
    rc_ad = load("recruiting")
    assert {i.id for i in re_ad["items"]} != {i.id for i in rc_ad["items"]}
    engine = MatchingEngine(ItemStore(rc_ad["items"]))
    matches = engine.match({"job_type": "エンジニア", "employment": "正社員"})
    assert matches and matches[0].item.id.startswith("job-")


def test_dialog_extracts_slots_and_asks_missing():
    ad = load("real_estate")
    dm = DialogManager(ad["slots"])
    state = DialogState()
    dm.extract("新宿がいい", state)
    # layout 未指定 -> 質問が返る
    q = dm.next_question(state)
    assert q is not None and "間取り" in q
    dm.extract("1Kで", state)
    assert dm.ready(state)                 # 必須スロット充足


def test_explanation_no_fabrication():
    engine, _ = _re_engine()
    m = engine.match({"area": "新宿", "layout": "1K"})[0]
    ex = explain(m, {"area": "新宿", "layout": "1K"})
    assert verify_no_fabrication(ex, m.item.attributes)   # 属性外情報なし
    assert ex["reasons"]


def test_dialog_max_turns_stops_questions():
    ad = load("real_estate")
    dm = DialogManager(ad["slots"], max_turns=2)
    state = DialogState()
    dm.extract("あいまいな発話", state)
    dm.extract("まだあいまい", state)
    assert dm.next_question(state) is None   # 打ち切り


def test_marketing_feedback_frequent_and_zero_hit():
    logs = [{"slots": {"area": "新宿"}, "hit_count": 2},
            {"slots": {"area": "新宿"}, "hit_count": 1},
            {"slots": {"area": "渋谷", "layout": "3LDK"}, "hit_count": 0}]
    rep = FeedbackAnalyzer().analyze(logs)
    assert "新宿" in rep.frequent_needs["area"]
    assert {"area": "渋谷", "layout": "3LDK"} in rep.zero_hit_conditions
