import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import ItemStore, MatchingEngine, EventLog, embed, cosine  # noqa: E402
from adapters import load  # noqa: E402


def _engine():
    ad = load("real_estate")
    return MatchingEngine(ItemStore(ad["items"])), ad


# --- ベクトル層 ---
def test_vector_similarity_bounds():
    v1 = embed("駅近 静か")
    assert abs(cosine(v1, v1) - 1.0) < 1e-6
    assert cosine(embed("駅近"), embed("公園")) < cosine(v1, v1)


# --- ハイブリッド検索 ---
def test_hybrid_combines_struct_and_freetext():
    engine, ad = _engine()
    real_ids = {i.id for i in ad["items"]}
    matches = engine.match_hybrid({"area": "新宿", "layout": "1K"}, free_text="駅近 オートロック", top_k=3)
    assert matches
    for m in matches:
        assert m.item.id in real_ids     # 実在IDのみ
    # 駅近/オートロックを持つ re-001 が自由文で上位に来る
    assert matches[0].item.id == "re-001"


def test_hybrid_freetext_influences_ranking():
    engine, _ = _engine()
    # スロットは同じ(新宿1K)でも、自由文で「格安」を求めると re-005 が上がる
    matches = engine.match_hybrid({"area": "新宿"}, free_text="格安 トイレ別", top_k=5)
    top_ids = [m.item.id for m in matches]
    assert "re-005" in top_ids[:2]


def test_hybrid_only_real_items_even_with_freetext():
    engine, ad = _engine()
    real_ids = {i.id for i in ad["items"]}
    matches = engine.match_hybrid({}, free_text="静か 公園", top_k=5)
    assert all(m.item.id in real_ids for m in matches)


# --- イベントログ ---
def test_event_log_records_lifecycle():
    log = EventLog()
    log.record("sess-1", "utterance", {"text": "新宿の1K"})
    log.record("sess-1", "slots", {"area": "新宿"})
    log.record("sess-1", "presented", {"ids": ["re-001", "re-005"]})
    log.record("sess-1", "click", {"id": "re-001"})
    assert len(log.events) == 4
    assert len(log.by_type("click")) == 1
    assert log.by_type("presented")[0].payload["ids"] == ["re-001", "re-005"]
