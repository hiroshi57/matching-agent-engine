# matching-agent-engine

「検索からマッチングへ」を再利用可能にする、業種特化・対話型マッチングエンジン。
クライアント保有のアイテムデータ（物件/求人/商品等）を、対話でニーズを引き出しながら提案する体験に変える。

## 差別化ポイント

1. **業種アダプタ交換式** — 新業種への適用をアダプタ実装のみで2週間以内（不動産/人材/EC/BtoB）
2. **実在IDのみ提示** — 候補はDB実在アイテムのみ。LLM創作候補は破棄（幻覚防止）
3. **対話ログを広告改善示唆に還元** — 刺さった条件・語彙を抽出し、広告ターゲティング/クリエイティブ改善へ。
   マッチングと広告運用を往復させるループはデジマ企業にしか作れない

## ステータス

🟢 **差別化コア実装済み**（実在IDバリデータ＋アダプタ交換＋広告フィードバック） / 拡張は承認後

- [docs/adapter_interface.md](docs/adapter_interface.md) — コア/アダプタ境界のインターフェース定義
- `core/` — 対話スロット抽出 + マッチング(実在IDのみ) + 属性ベース理由生成
- `adapters/` — 不動産・求人(コード変更なしで切替) / `marketing_feedback/` — 広告示唆（tests 8件PASS）

```bash
python demo.py          # 対話->マッチング(実在IDのみ)->理由->アダプタ切替->広告示唆
python -m pytest -q
```

進め方（プロンプト指定）: IF定義 → **承認** → コア実装→不動産アダプタ→求人アダプタ→フィードバックモジュール。

## 予定フォルダ構成（実装時）

```
core/{dialog,search(hybrid+validator),explain,events}
adapters/{_template,real_estate,recruiting}
marketing_feedback/ / widget/(Shadow DOM)
eval/{personas,auto_dialog_test}
```
