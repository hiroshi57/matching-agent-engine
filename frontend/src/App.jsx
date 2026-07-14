import React, { useState } from "react";
import ChatWidget from "./screens/ChatWidget.jsx";
import FeedbackDashboard from "./screens/FeedbackDashboard.jsx";
import { seed, match, feedbackReportUrl } from "./api.js";

const TENANT = "demo-tenant";

// バックエンド未起動時のデモ
const DEMO_RESULTS = [
  { id: "re-001", score: 0.79, reasons: ["エリアが「新宿」で希望に合致", "間取りが「1K」で希望に合致"] },
  { id: "re-005", score: 0.66, reasons: ["エリアが「新宿」で希望に合致"] },
];
const DEMO_FREQ = { area: ["新宿", "渋谷"], layout: ["1K", "3LDK"] };
const DEMO_ZERO = [{ area: "新宿", layout: "3LDK" }];

export default function App() {
  const [tab, setTab] = useState("chat");
  const [results, setResults] = useState(DEMO_RESULTS);
  const [busy, setBusy] = useState(false);

  const runMatch = async (body) => {
    setBusy(true);
    try {
      await seed(TENANT, body.adapter);
      const res = await match(TENANT, body);
      setResults(res.results || []);
    } catch (e) {
      alert("バックエンド未起動の可能性: " + e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="wrap">
      <h1>業種特化マッチングエンジン</h1>
      <nav>
        <button onClick={() => setTab("chat")} disabled={tab === "chat"}>対話ウィジェット</button>
        <button onClick={() => setTab("fb")} disabled={tab === "fb"}>広告フィードバック</button>
      </nav>
      {tab === "chat"
        ? <ChatWidget onMatch={runMatch} results={results} busy={busy} />
        : <FeedbackDashboard frequentNeeds={DEMO_FREQ} zeroHit={DEMO_ZERO}
            onOpenReport={() => window.open(feedbackReportUrl(), "_blank")} />}
    </div>
  );
}
