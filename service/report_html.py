"""週次 広告フィードバック HTMLレポート(標準ライブラリのみ)."""
from __future__ import annotations

import html
from typing import Dict

from marketing_feedback import FeedbackReport


def build_html_report(report: FeedbackReport) -> str:
    freq = ""
    for slot, vals in report.frequent_needs.items():
        items = "、".join(html.escape(str(v)) for v in vals)
        freq += f'<tr><td>{html.escape(slot)}</td><td>{items}</td></tr>'
    zero = "".join(
        f'<li>{html.escape(json_ja(z))}</li>' for z in report.zero_hit_conditions) or "<li>なし</li>"
    return f"""<!DOCTYPE html><html lang="ja"><head><meta charset="UTF-8">
<title>広告フィードバック週次レポート</title>
<style>body{{font-family:system-ui,sans-serif;margin:24px;color:#1a1a2e}}
h1{{color:#e07b39}} table{{border-collapse:collapse;margin:8px 0}}
th,td{{border:1px solid #dde;padding:6px 10px}} th{{background:#fdf1e7}}</style></head><body>
<h1>広告フィードバック週次レポート</h1>
<h2>頻出ニーズ（検索広告キーワード候補）</h2>
<table><tr><th>条件スロット</th><th>頻出値 Top</th></tr>{freq}</table>
<h2>候補ゼロ条件（品揃え・LP改善示唆）</h2>
<ul>{zero}</ul>
<hr><small>※対話ログは匿名セッション単位で集計。個人情報は含みません。</small>
</body></html>"""


def json_ja(d: Dict) -> str:
    return "、".join(f"{k}={v}" for k, v in d.items())
