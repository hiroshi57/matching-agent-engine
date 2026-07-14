const BASE = import.meta.env?.VITE_API || "http://localhost:8000";
const h = (t) => ({ "Content-Type": "application/json", "X-Tenant-Id": t });

export async function seed(t, adapter) {
  return (await fetch(`${BASE}/v1/seed`, { method: "POST", headers: h(t), body: JSON.stringify({ adapter }) })).json();
}
export async function match(t, body) {
  return (await fetch(`${BASE}/v1/match`, { method: "POST", headers: h(t), body: JSON.stringify(body) })).json();
}
export function feedbackReportUrl() { return `${BASE}/v1/feedback-report`; }
