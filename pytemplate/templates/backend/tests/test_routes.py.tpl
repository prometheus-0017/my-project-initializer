"""HTTP 接口测试。"""

from __future__ import annotations

from flask.testing import FlaskClient


def test_health_returns_ok(client: FlaskClient) -> None:
    """/api/health 返回 ok 与运行模式。"""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload["status"] == "ok"
    assert payload["mode"] == "dev"


def test_spa_fallback_returns_503_before_build(client: FlaskClient) -> None:
    """前端产物未构建时,SPA 兜底路由返回 503(明确提示,不静默)。"""
    resp = client.get("/")
    assert resp.status_code == 503
    assert "build-copy" in resp.get_json()["error"]
