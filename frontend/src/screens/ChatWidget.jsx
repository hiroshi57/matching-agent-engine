import React, { useState } from "react";

// 対話マッチングウィジェット(簡易). スロット選択 + 自由文でマッチング。
export default function ChatWidget({ onMatch, results, busy }) {
  const [area, setArea] = useState("新宿");
  const [layout, setLayout] = useState("1K");
  const [freeText, setFreeText] = useState("駅近");

  return (
    <div className="card">
      <h2>対話マッチング（不動産）</h2>
      <label>エリア
        <select value={area} onChange={(e) => setArea(e.target.value)}>
          <option>新宿</option><option>渋谷</option><option>池袋</option></select>
      </label>
      <label>間取り
        <select value={layout} onChange={(e) => setLayout(e.target.value)}>
          <option>1K</option><option>1LDK</option><option>2LDK</option></select>
      </label>
      <label>こだわり(自由文)
        <input value={freeText} onChange={(e) => setFreeText(e.target.value)} /></label>
      <button className="primary" disabled={busy}
        onClick={() => onMatch({ adapter: "real_estate", slots: { area, layout }, free_text: freeText })}>
        {busy ? "検索中..." : "候補を探す"}
      </button>

      <h3>候補（実在物件のみ）</h3>
      <ul>{(results || []).map((r) => (
        <li key={r.id}><b>{r.id}</b> (score {r.score}) — {(r.reasons || []).join(" / ")}</li>))}
      </ul>
    </div>
  );
}
