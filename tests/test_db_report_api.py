import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  # noqa: E402

from service.db import ServiceDB  # noqa: E402
from service.report_html import build_html_report  # noqa: E402
from marketing_feedback import FeedbackAnalyzer  # noqa: E402
from adapters import load  # noqa: E402


def test_items_roundtrip_and_tenant_isolation():
    db = ServiceDB(":memory:")
    ad = load("real_estate")
    db.load_items("t-a", "real_estate", ad["items"])
    got = db.get_items("t-a", "real_estate")
    assert len(got) == len(ad["items"])
    assert db.get_items("t-b", "real_estate") == []      # 越境不可


def test_events_persist_and_isolated():
    db = ServiceDB(":memory:")
    db.record_event("t-a", "s1", "slots", {"area": "新宿"})
    db.record_event("t-a", "s1", "presented", {"ids": ["re-001"]})
    assert len(db.get_events("t-a")) == 2
    assert db.get_events("t-b") == []


def test_feedback_html_report():
    logs = [{"slots": {"area": "新宿"}, "hit_count": 1},
            {"slots": {"area": "渋谷", "layout": "3LDK"}, "hit_count": 0}]
    report = FeedbackAnalyzer().analyze(logs)
    html = build_html_report(report)
    assert "広告フィードバック週次レポート" in html
    assert "頻出ニーズ" in html and "候補ゼロ条件" in html
    assert "匿名セッション" in html


def test_api_e2e_and_tenant_isolation():
    pytest.importorskip("fastapi")
    pytest.importorskip("httpx")
    from fastapi.testclient import TestClient
    from service.api import create_app
    c = TestClient(create_app())
    ha, hb = {"X-Tenant-Id": "t-a"}, {"X-Tenant-Id": "t-b"}
    assert c.post("/v1/seed", json={"adapter": "real_estate"}, headers=ha).json()["loaded"] > 0
    # tenant-b は seed していない -> マッチ不可
    assert c.post("/v1/match", json={"adapter": "real_estate", "slots": {"area": "新宿"}},
                  headers=hb).status_code == 404
    res = c.post("/v1/match", json={"adapter": "real_estate", "slots": {"area": "新宿", "layout": "1K"},
                                    "free_text": "駅近"}, headers=ha).json()
    assert res["results"]
    ids = {r["id"] for r in res["results"]}
    assert all(i.startswith("re-") for i in ids)          # 実在IDのみ
    r = c.get("/v1/feedback-report", headers=ha)
    assert r.status_code == 200 and "広告フィードバック" in r.text
