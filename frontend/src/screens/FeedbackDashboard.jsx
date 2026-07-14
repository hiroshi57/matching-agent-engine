import React from "react";

// 広告フィードバック ダッシュボード(対話ログ由来の広告改善示唆)。
export default function FeedbackDashboard({ frequentNeeds, zeroHit, onOpenReport }) {
  return (
    <div className="card">
      <h2>広告フィードバック</h2>
      <h3>頻出ニーズ（検索広告KW候補）</h3>
      <table><thead><tr><th>スロット</th><th>頻出値</th></tr></thead>
        <tbody>{Object.entries(frequentNeeds || {}).map(([k, vals]) => (
          <tr key={k}><td>{k}</td><td>{vals.join("、")}</td></tr>))}</tbody></table>
      <h3>候補ゼロ条件（品揃え/LP改善示唆）</h3>
      <ul>{(zeroHit || []).map((z, i) => (
        <li key={i}>{Object.entries(z).map(([k, v]) => `${k}=${v}`).join("、")}</li>))}</ul>
      {onOpenReport && <button className="primary" onClick={onOpenReport}>週次HTMLレポートを開く</button>}
    </div>
  );
}
