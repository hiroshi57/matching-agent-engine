"""デモ(APIキー不要). 対話->マッチング(実在IDのみ)->理由->広告示唆. `python demo.py`"""
from core import ItemStore, MatchingEngine, DialogManager, DialogState, explain
from adapters import load
from marketing_feedback import FeedbackAnalyzer


def run_adapter(name: str, utterances):
    ad = load(name)
    dm = DialogManager(ad["slots"])
    store = ItemStore(ad["items"])
    engine = MatchingEngine(store)
    state = DialogState()
    print(f"\n=== アダプタ: {name}(コア変更なしで切替) ===")
    for u in utterances:
        dm.extract(u, state)
    print(f"  抽出スロット: {state.slots}")
    matches = engine.match(state.slots, top_k=3)
    for m in matches:
        ex = explain(m, state.slots)
        print(f"  実在ID {m.item.id} (score {m.score:.2f}) 理由: {ex['reasons']}")
    return state.slots, len(matches)


def main():
    run_adapter("real_estate", ["新宿がいいです", "1Kで予算は10万円以下"])
    run_adapter("recruiting", ["エンジニア希望", "正社員でリモートがいい"])

    print("\n=== 実在IDバリデータ(LLM創作候補を破棄) ===")
    ad = load("real_estate")
    engine = MatchingEngine(ItemStore(ad["items"]))
    candidates = ["re-001", "re-999(創作)", "re-003"]
    safe = engine.safe_candidates(candidates)
    print(f"  入力候補: {candidates}")
    print(f"  検証後(実在のみ): {[i.id for i in safe]}")

    print("\n=== 広告フィードバック ===")
    logs = [{"slots": {"area": "新宿", "layout": "1K"}, "hit_count": 3},
            {"slots": {"area": "新宿", "layout": "3LDK"}, "hit_count": 0},
            {"slots": {"area": "渋谷", "layout": "1K"}, "hit_count": 2}]
    rep = FeedbackAnalyzer().analyze(logs)
    print(f"  頻出ニーズ(KW候補): {rep.frequent_needs}")
    print(f"  候補ゼロ条件(品揃え示唆): {rep.zero_hit_conditions}")


if __name__ == "__main__":
    main()
