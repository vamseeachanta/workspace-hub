"""Tests for scripts/ai/provider-kanban-server.py (#2665).

The server is exercised via in-process httpd + urllib.request. We stub out the
approve module so tests never invoke gh CLI or write into the live repo's
.planning/plan-approved directory.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "ai" / "provider-kanban-server.py"
spec = importlib.util.spec_from_file_location("provider_kanban_server", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["provider_kanban_server"] = module
spec.loader.exec_module(module)


class StubApproveModule:
    """Drop-in replacement for approve-provider-plan.py."""

    class ApprovalError(RuntimeError):
        pass

    def __init__(self):
        self.calls: list[dict] = []
        self.next_error: Exception | None = None

    def execute_transaction(self, issue, **kwargs):
        self.calls.append({"issue": issue, **kwargs})
        if self.next_error is not None:
            err, self.next_error = self.next_error, None
            raise err
        return {
            "issue_number": issue,
            "phase": "complete" if kwargs.get("mode") == "real" else "dry-run-only",
            "txid": "FAKETXID0000000",
            **kwargs,
        }


@pytest.fixture
def server(tmp_path):
    stub = StubApproveModule()
    # Provide a dashboard file the server can serve
    dash = tmp_path / "dashboard.html"
    dash.write_text("<!doctype html><html><head><title>k</title></head><body>cards</body></html>", encoding="utf-8")
    httpd = module.build_server(
        host="127.0.0.1",
        port=0,  # ephemeral port — bind picks a free one
        token="TEST-TOKEN-XYZ",
        dashboard_path=dash,
        approve_module=stub,
    )
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield httpd, stub, port
    httpd.shutdown()
    httpd.server_close()
    thread.join(timeout=2.0)


def _post(port: int, path: str, body: dict, headers: dict | None = None) -> tuple[int, dict | str]:
    data = urllib.parse.urlencode(body).encode("utf-8")
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=data, method="POST", headers=headers or {},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        payload = e.read().decode("utf-8")
        try:
            return e.code, json.loads(payload)
        except json.JSONDecodeError:
            return e.code, payload


def _get(port: int, path: str) -> tuple[int, str]:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}") as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")


# ────────────────────────────────────────────────────────────────────────────
# Plan-named tests
# ────────────────────────────────────────────────────────────────────────────


def test_local_approval_endpoint_requires_loopback_csrf_and_user_intent(server):
    httpd, stub, port = server

    # POST without CSRF token → 403
    status, payload = _post(port, "/approve", {"issue": "9001", "mode": "dry-run"}, headers={})
    assert status == 403
    assert "CSRF" in payload["error"]
    assert stub.calls == [], "no approval transaction may be invoked without CSRF token"

    # POST with WRONG CSRF token → 403
    status, payload = _post(
        port, "/approve",
        {"issue": "9001", "mode": "dry-run"},
        headers={"X-CSRF-Token": "WRONG-TOKEN"},
    )
    assert status == 403
    assert stub.calls == []

    # POST with valid token but real mode + no user_identity → 400
    status, payload = _post(
        port, "/approve",
        {"issue": "9001", "mode": "real", "i_understand": "yes"},
        headers={"X-CSRF-Token": "TEST-TOKEN-XYZ"},
    )
    assert status == 400
    assert "user_identity" in payload["error"]
    assert stub.calls == [], "real mode without user_identity must not invoke transaction"

    # POST with valid token + real mode + user_identity but missing i_understand → 400
    status, payload = _post(
        port, "/approve",
        {"issue": "9001", "mode": "real", "user_identity": "vamsee"},
        headers={"X-CSRF-Token": "TEST-TOKEN-XYZ"},
    )
    assert status == 400
    assert "i_understand" in payload["error"]
    assert stub.calls == []


def test_local_approval_endpoint_valid_post_invokes_approve_dry_run(server):
    httpd, stub, port = server
    status, payload = _post(
        port, "/approve",
        {"issue": "9001", "mode": "dry-run"},
        headers={"X-CSRF-Token": "TEST-TOKEN-XYZ"},
    )
    assert status == 200
    assert payload["phase"] == "dry-run-only"
    assert len(stub.calls) == 1
    assert stub.calls[0]["issue"] == 9001
    assert stub.calls[0]["mode"] == "dry-run"


def test_local_approval_endpoint_valid_real_post_invokes_approve_real(server):
    httpd, stub, port = server
    status, payload = _post(
        port, "/approve",
        {
            "issue": "9001", "mode": "real",
            "user_identity": "vamsee.achanta@aceengineer.com",
            "approval_source": "localhost approval server",
            "i_understand": "yes",
        },
        headers={"X-CSRF-Token": "TEST-TOKEN-XYZ"},
    )
    assert status == 200
    assert payload["phase"] == "complete"
    assert stub.calls[0]["mode"] == "real"
    assert stub.calls[0]["user_identity"] == "vamsee.achanta@aceengineer.com"
    # Server passes its own token as the confirmation_token (satisfies non-TTY gate in approve-provider-plan).
    assert stub.calls[0]["confirmation_token"] == "TEST-TOKEN-XYZ"


def test_local_approval_endpoint_returns_409_on_approval_error(server):
    httpd, stub, port = server
    stub.next_error = stub.ApprovalError("issue already approved")
    status, payload = _post(
        port, "/approve",
        {"issue": "9001", "mode": "dry-run"},
        headers={"X-CSRF-Token": "TEST-TOKEN-XYZ"},
    )
    assert status == 409
    assert "already approved" in payload["error"]


def test_server_serves_dashboard_with_csrf_token_meta(server):
    httpd, stub, port = server
    status, body = _get(port, "/")
    assert status == 200
    assert "kanban-csrf-token" in body
    assert "TEST-TOKEN-XYZ" in body, "ephemeral CSRF token must be injected into served HTML"


def test_server_rejects_non_loopback_bind():
    with pytest.raises(ValueError, match="loopback"):
        module.build_server(host="0.0.0.0", port=0)
    with pytest.raises(ValueError, match="loopback"):
        module.build_server(host="192.168.1.10", port=0)


def test_server_healthz_endpoint(server):
    httpd, stub, port = server
    status, body = _get(port, "/healthz")
    assert status == 200
    assert json.loads(body) == {"ok": True, "token_present": True}


def test_server_404_on_unknown_routes(server):
    httpd, stub, port = server
    status, _ = _get(port, "/secrets")
    assert status == 404
    status, _ = _post(
        port, "/dump-config",
        {"x": "1"},
        headers={"X-CSRF-Token": "TEST-TOKEN-XYZ"},
    )
    assert status == 404
