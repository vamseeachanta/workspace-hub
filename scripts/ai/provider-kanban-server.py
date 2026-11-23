#!/usr/bin/env python3
"""Local loopback approval server for the provider-credit Kanban (#2665).

Refuses non-loopback binds. Generates an ephemeral CSRF token at startup and
prints it to the console. Approval POSTs must:
  - hit 127.0.0.1 (the server only listens on loopback)
  - include the X-CSRF-Token header matching the ephemeral startup token
  - include user_identity + approval_source in the form body
  - include a 'i_understand=yes' explicit-intent toggle

Real approval mode invokes approve-provider-plan.execute_transaction with
mode=real and a confirmation_token (the same ephemeral CSRF token, which
satisfies the non-TTY user-confirmation requirement in approve-provider-plan).
"""
from __future__ import annotations

import argparse
import http.server
import importlib.util
import json
import os
import secrets
import sys
import urllib.parse
from pathlib import Path
from typing import Any, Callable

WORKSPACE_HUB = Path(__file__).resolve().parents[2]
KANBAN_HTML_PATH = WORKSPACE_HUB / "docs" / "reports" / "provider-kanban-dashboard.html"
KANBAN_JSON_PATH = WORKSPACE_HUB / "config" / "ai-tools" / "provider-kanban.json"


def _load_approve_module():
    path = WORKSPACE_HUB / "scripts" / "ai" / "approve-provider-plan.py"
    spec = importlib.util.spec_from_file_location("_approve_for_server", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load approve-provider-plan from {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_approve_for_server"] = mod
    spec.loader.exec_module(mod)
    return mod


class ApprovalRequestHandler(http.server.BaseHTTPRequestHandler):
    """Handles GET / (dashboard), POST /approve, anything else → 404."""

    # Class-level state set by run_server()
    server_token: str = ""
    approve_module: Any = None  # set on startup; injectable from tests
    dashboard_path: Path = KANBAN_HTML_PATH

    def log_message(self, format: str, *args) -> None:  # noqa: A002 — match stdlib signature
        # Quiet by default; use --verbose to enable
        if getattr(self.server, "verbose", False):
            super().log_message(format, *args)

    def _bad_request(self, message: str) -> None:
        self.send_response(400)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode("utf-8"))

    def _forbidden(self, message: str) -> None:
        self.send_response(403)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode("utf-8"))

    def _ok_json(self, payload: dict[str, Any]) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload, indent=2, sort_keys=True).encode("utf-8"))

    def _ok_html(self, body: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def _verify_loopback(self) -> bool:
        """Reject any non-loopback client.

        The server only binds 127.0.0.1, but defense-in-depth: also verify the
        remote address. SSH-tunneled clients still appear as 127.0.0.1, which
        is acceptable — the user explicitly set up the tunnel.
        """
        peer = self.client_address[0]
        return peer.startswith("127.") or peer == "::1"

    # ── GET routes ─────────────────────────────────────────────────────────
    def do_GET(self) -> None:  # noqa: N802 — stdlib signature
        if not self._verify_loopback():
            self._forbidden("non-loopback client refused")
            return
        path = urllib.parse.urlparse(self.path).path
        if path == "/":
            return self._serve_dashboard()
        if path == "/healthz":
            return self._ok_json({"ok": True, "token_present": bool(self.server_token)})
        self.send_response(404)
        self.end_headers()

    def _serve_dashboard(self) -> None:
        if not self.dashboard_path.exists():
            self._bad_request(
                f"dashboard not generated yet; run "
                f"`uv run --no-project python scripts/ai/provider-kanban.py --served-localhost` first"
            )
            return
        body = self.dashboard_path.read_text(encoding="utf-8")
        # Inject the ephemeral CSRF token into a meta tag so the form POST can read it.
        # The token is NOT persisted to disk — it lives only in server memory.
        injection = (
            f'<meta name="kanban-csrf-token" content="{self.server_token}">'
        )
        if "<head>" in body:
            body = body.replace("<head>", f"<head>{injection}", 1)
        else:
            body = injection + body
        return self._ok_html(body)

    # ── POST routes ────────────────────────────────────────────────────────
    def do_POST(self) -> None:  # noqa: N802 — stdlib signature
        if not self._verify_loopback():
            self._forbidden("non-loopback client refused")
            return
        path = urllib.parse.urlparse(self.path).path
        if path != "/approve":
            self.send_response(404)
            self.end_headers()
            return

        # CSRF token check
        client_token = self.headers.get("X-CSRF-Token") or ""
        if not secrets.compare_digest(client_token, self.server_token):
            return self._forbidden("missing or invalid CSRF token")

        # Read body
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8") if length else ""
        form: dict[str, str] = {}
        for k, vs in urllib.parse.parse_qs(raw).items():
            form[k] = vs[0]

        issue_raw = form.get("issue")
        if not issue_raw:
            return self._bad_request("missing 'issue' form field")
        try:
            issue = int(issue_raw)
        except ValueError:
            return self._bad_request(f"invalid issue number: {issue_raw}")

        user_identity = form.get("user_identity")
        approval_source = form.get("approval_source") or "localhost approval server"
        mode = form.get("mode", "dry-run")
        intent = form.get("i_understand", "")

        if mode == "real" and intent != "yes":
            return self._bad_request(
                "real mode requires i_understand=yes in the form body "
                "(prevents accidental approval clicks)"
            )
        if mode == "real" and not user_identity:
            return self._bad_request("real mode requires user_identity in the form body")

        try:
            result = self.approve_module.execute_transaction(
                issue,
                mode=mode,
                user_identity=user_identity,
                approval_source=approval_source,
                confirmation_token=self.server_token,
                is_tty=False,  # server is non-TTY; token satisfies user-confirmation gate
            )
            return self._ok_json(result)
        except self.approve_module.ApprovalError as exc:
            self.send_response(409)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(exc)}).encode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(exc), "type": exc.__class__.__name__}).encode("utf-8"))


def build_server(
    *,
    host: str = "127.0.0.1",
    port: int = 7665,
    token: str | None = None,
    dashboard_path: Path | None = None,
    approve_module: Any = None,
    verbose: bool = False,
) -> http.server.HTTPServer:
    """Construct an HTTPServer with the approval handler wired up.

    Rejects any host other than loopback addresses.
    """
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError(
            f"provider-kanban-server refuses to bind non-loopback host {host!r}; "
            f"use 127.0.0.1 only. SSH tunnel from remote machines if needed."
        )
    handler = ApprovalRequestHandler
    handler.server_token = token or secrets.token_urlsafe(32)
    handler.approve_module = approve_module or _load_approve_module()
    handler.dashboard_path = dashboard_path or KANBAN_HTML_PATH
    httpd = http.server.HTTPServer((host, port), handler)
    httpd.verbose = verbose  # type: ignore[attr-defined]
    return httpd


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Local loopback approval server for #2665 Kanban")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (loopback only; default 127.0.0.1)")
    parser.add_argument("--port", type=int, default=7665, help="Bind port (default 7665)")
    parser.add_argument("--verbose", action="store_true", help="Log each request")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    httpd = build_server(host=args.host, port=args.port, verbose=args.verbose)
    token = httpd.RequestHandlerClass.server_token  # type: ignore[attr-defined]
    print(
        f"provider-kanban-server: listening on http://{args.host}:{args.port}\n"
        f"  Open the URL in your browser to view the dashboard.\n"
        f"  Ephemeral CSRF token (DO NOT share): {token}\n"
        f"  POST /approve must include X-CSRF-Token: <token> and form body with\n"
        f"  issue=<N>&user_identity=<email>&mode=real&i_understand=yes\n"
        f"  Ctrl-C to stop."
    )
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nprovider-kanban-server: shutdown")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
