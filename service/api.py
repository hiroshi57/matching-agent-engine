"""マッチングエンジン API(FastAPI). アイテム投入/対話/マッチング/イベント/広告FBレポート.
テナント分離(X-Tenant-Id)。`uvicorn service.api:app --reload`
"""
from core import ItemStore, MatchingEngine, DialogManager, DialogState, explain
from adapters import load
from marketing_feedback import FeedbackAnalyzer
from .db import ServiceDB
from .report_html import build_html_report

DB = ServiceDB(":memory:")


def seed_adapter(tenant: str, adapter_name: str) -> int:
    ad = load(adapter_name)
    return DB.load_items(tenant, adapter_name, ad["items"])


def create_app():  # pragma: no cover
    from fastapi import Depends, FastAPI, Header, HTTPException
    from fastapi.responses import HTMLResponse
    from pydantic import BaseModel

    app = FastAPI(title="Matching Agent Engine", version="1.0.0")

    def tenant(x_tenant_id: str = Header(...)) -> str:
        if not x_tenant_id:
            raise HTTPException(401, "tenant required")
        return x_tenant_id

    class SeedIn(BaseModel):
        adapter: str = "real_estate"

    class MatchIn(BaseModel):
        adapter: str = "real_estate"
        slots: dict = {}
        free_text: str = ""
        session_id: str = "sess-1"

    @app.post("/v1/seed")
    def seed(body: SeedIn, t: str = Depends(tenant)):
        return {"loaded": seed_adapter(t, body.adapter)}

    @app.post("/v1/match")
    def match(body: MatchIn, t: str = Depends(tenant)):
        items = DB.get_items(t, body.adapter)
        if not items:
            raise HTTPException(404, "no items (seed first)")
        engine = MatchingEngine(ItemStore(items))
        matches = engine.match_hybrid(body.slots, free_text=body.free_text, top_k=5)
        DB.record_event(t, body.session_id, "slots", body.slots)
        DB.record_event(t, body.session_id, "presented", {"ids": [m.item.id for m in matches]})
        return {"results": [{"id": m.item.id, "score": round(m.score, 3),
                             **explain(m, body.slots)} for m in matches]}

    @app.get("/v1/feedback-report", response_class=HTMLResponse)
    def feedback_report(t: str = Depends(tenant)):
        events = DB.get_events(t)
        # presented イベント数を hit_count とみなして集計(簡易)
        logs = []
        for e in events:
            if e["type"] == "slots":
                logs.append({"slots": e["payload"], "hit_count": 1})
        report = FeedbackAnalyzer().analyze(logs)
        return build_html_report(report)

    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}

    return app


try:  # pragma: no cover
    app = create_app()
except Exception:
    app = None
