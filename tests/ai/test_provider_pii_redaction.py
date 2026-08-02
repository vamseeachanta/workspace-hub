"""Client-PII containment for the provider-artifact writers (#3768).

workspace-hub is PUBLIC. provider-kanban.py / provider-work-queue.py /
provider-autolabel.py write raw GitHub issue titles (and plan-derived prose)
into git-tracked files that a 4-hourly cron regenerates and `chore(sync):
auto-sync` pushes straight to `main` — a path the Client-PII Gate
(`on: pull_request`) never sees.

These tests pin the containment PROPERTIES, not field names:

  * the client token must not appear ANYWHERE in a machine artifact,
  * the human-facing dashboards must still show a title (redacted, not omitted),
  * the fields the real JSON consumers read must survive,
  * scrubbing must be idempotent (artifacts regenerate every 4 hours),
  * an absent private map must degrade VISIBLY, never silently open.

NEVER put a real client identifier in this file. `SYNTH_CLIENT` is invented and
the map used by every test is written into `tmp_path`.
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "ai" / "provider_kanban"


def _load(name: str, rel: str):
    path = REPO_ROOT / rel
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


kanban = _load("pii_provider_kanban", "scripts/ai/provider-kanban.py")
work_queue = _load("pii_provider_work_queue", "scripts/ai/provider-work-queue.py")
autolabel = _load("pii_provider_autolabel", "scripts/ai/provider-autolabel.py")
cpp = _load("pii_cpp", "scripts/ai/continuous-planning-pipeline.py")

# ── synthetic client identity — invented, never a real one ──────────────────
SYNTH_CLIENT = "Zorptech"
SYNTH_LONG = "Zorptech Industries"
CODENAME = "CLIENT-ZED"
CODENAME_LONG = "CLIENT-ZED-INDUSTRIES"
# A distinctive, PII-free word used to prove a title reached (or did not reach)
# a given artifact independently of the client-token assertions.
TITLE_MARKER = "Flangebolt"


def _write_map(tmp_path: Path) -> Path:
    path = tmp_path / "synthetic-codename-map.yaml"
    path.write_text(
        "version: 1\n"
        "rules:\n"
        f"  - pattern: '{SYNTH_LONG}'\n"
        f"    replacement: '{CODENAME_LONG}'\n"
        "    word_bound: false\n"
        f"  - pattern: '{SYNTH_CLIENT}'\n"
        f"    replacement: '{CODENAME}'\n"
        "    word_bound: true\n",
        encoding="utf-8",
    )
    return path


def _guard(tmp_path: Path):
    return work_queue.load_pii_guard(_write_map(tmp_path))


def _absent_guard(tmp_path: Path):
    return work_queue.load_pii_guard(tmp_path / "does-not-exist.yaml")


def _scorecard() -> dict:
    """Kanban fixture scorecard (still names the pre-#3573 `gemini` provider)."""
    return json.loads((FIXTURE_DIR / "scorecard.json").read_text(encoding="utf-8"))


def _wq_scorecard() -> dict:
    """provider-work-queue.py indexes `recommendations` by PROVIDERS, so it needs
    a scorecard that actually names claude/codex/agy."""
    return {
        "current_week": "2026-W20",
        "generated_at": "2026-05-12T00:00:00Z",
        "recommended_provider_order": list(work_queue.PROVIDERS),
        "recommendations": [
            {"provider": p, "priority": "highest", "status": "underused"}
            for p in work_queue.PROVIDERS
        ],
    }


def _workstations() -> dict:
    return json.loads((FIXTURE_DIR / "workstations.json").read_text(encoding="utf-8"))


def _issue(number: int, title: str, labels=None, *, state: str = "OPEN") -> dict:
    return {
        "number": number,
        "title": title,
        "url": f"https://example.test/issues/{number}",
        "state": state,
        "body": f"Body mentioning {SYNTH_CLIENT} as well.",
        "updatedAt": "2026-05-12T12:00:00Z",
        "labels": [{"name": lbl} for lbl in (labels or [])],
        "comments": [],
    }


def _wq_issue(number: int, title: str, labels=None) -> dict:
    return _issue(number, title, labels)


def _work_queue_json(numbers: list[int]) -> dict:
    """Minimal provider-work-queue.json shape that provider-kanban.py accepts."""
    return {
        "generated_at": "2026-05-12T12:00:00Z",
        "provider_queues": {
            "codex": {
                "provider": "codex",
                "top_issues": [{"number": n, "routing_reason": "fix"} for n in numbers[:8]],
                "full_candidates": [{"number": n, "routing_reason": "fix"} for n in numbers],
            },
            "claude": {"provider": "claude", "top_issues": [], "full_candidates": []},
            "agy": {"provider": "agy", "top_issues": [], "full_candidates": []},
        },
    }


def _write_plan(root: Path, number: int) -> Path:
    """Plan whose FILENAME, summary line and risk bullets all carry the token."""
    path = root / "docs" / "plans" / f"2026-05-12-issue-{number}-{SYNTH_CLIENT.lower()}-migration.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                f"# Plan for #{number}",
                "",
                "> **Status:** plan-review",
                "",
                f"Deliverable: migrate the {SYNTH_LONG} mooring dataset into the registry.",
                "",
                "## Risks and Open Questions",
                "",
                f"- **Risk:** the {SYNTH_CLIENT} export lacks revision metadata",
                "- **Risk:** ordering against parallel git activity",
                "",
                "## TDD Test List",
                "",
                "| Test name | What it verifies |",
                "|---|---|",
                "| `test_one` | first |",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


# ═══════════════════════════════════════════════════════════════════════════
# provider-work-queue.py
# ═══════════════════════════════════════════════════════════════════════════


def test_work_queue_artifacts_carry_no_client_identifier(tmp_path):
    issues = [_wq_issue(9101, f"fix: {SYNTH_LONG} pipeline {TITLE_MARKER}", ["status:plan-approved"])]
    queue = work_queue.build_queue(_wq_scorecard(), issues, guard=_guard(tmp_path))

    js = json.dumps(queue)
    md = work_queue.render_markdown(queue)

    assert SYNTH_CLIENT.lower() not in js.lower(), "work-queue JSON must not carry the client identifier"
    assert SYNTH_CLIENT.lower() not in md.lower(), "work-queue Markdown must not carry the client identifier"
    # Redacted, not silently dropped: the codename and the rest of the title survive.
    assert CODENAME_LONG in js and CODENAME_LONG in md
    assert TITLE_MARKER in md, "the human-facing table must still show the (redacted) title"


def test_work_queue_json_declares_its_redaction_mode(tmp_path):
    queue = work_queue.build_queue(_wq_scorecard(), [_wq_issue(9102, "fix: thing")], guard=_guard(tmp_path))
    meta = queue["pii_redaction"]
    assert meta["map_present"] is True
    assert meta["mode"] == "redacted"


def test_work_queue_withholds_titles_visibly_when_map_absent(tmp_path):
    """Map-absent must fail SAFE (no raw title) and LOUD (stated in the artifact)."""
    issues = [_wq_issue(9103, f"fix: {SYNTH_LONG} pipeline {TITLE_MARKER}")]
    queue = work_queue.build_queue(_wq_scorecard(), issues, guard=_absent_guard(tmp_path))

    js = json.dumps(queue)
    md = work_queue.render_markdown(queue)

    assert SYNTH_CLIENT.lower() not in js.lower()
    assert TITLE_MARKER not in js, "with no map, the title text must be withheld, not emitted"
    assert TITLE_MARKER not in md
    assert queue["pii_redaction"]["mode"] == "withheld"
    assert queue["pii_redaction"]["map_present"] is False
    # The degradation must be readable in the human artifact, not only in JSON.
    assert work_queue.PII_WITHHELD in md
    assert "withheld" in md.lower()


# ═══════════════════════════════════════════════════════════════════════════
# provider-kanban.py
# ═══════════════════════════════════════════════════════════════════════════


def _build_kanban(tmp_path, monkeypatch, number: int, title: str, guard):
    monkeypatch.setattr(kanban, "WORKSPACE_HUB", tmp_path)
    monkeypatch.setattr(cpp, "WORKSPACE_HUB", tmp_path)
    _write_plan(tmp_path, number)
    return kanban.build_kanban(
        work_queue=_work_queue_json([number]),
        scorecard=_scorecard(),
        utilization={},
        workstations=_workstations(),
        issues=[_issue(number, title, ["status:plan-review"])],
        root=tmp_path,
        pipeline_module=cpp,
        guard=guard,
    )


def test_kanban_artifacts_carry_no_client_identifier(tmp_path, monkeypatch):
    """Title, plan summary, risk bullets AND the plan file PATH all carry the token."""
    board = _build_kanban(
        tmp_path, monkeypatch, 9201, f"epic: {SYNTH_LONG} rollout {TITLE_MARKER}", _guard(tmp_path)
    )

    js = json.dumps(kanban.kanban_json_payload(board))
    md = kanban.render_markdown(board)
    html = kanban.render_html(board)

    for name, text in (("json", js), ("markdown", md), ("html", html)):
        assert SYNTH_CLIENT.lower() not in text.lower(), f"kanban {name} must not carry the client identifier"

    # The hover card lifts plan_summary/risks straight out of the plan file —
    # prove those specific surfaces were scrubbed rather than merely empty.
    hover = board["cards"][0]["hover"]
    assert CODENAME_LONG in hover["plan_summary"]
    assert CODENAME in hover["risks"]
    assert CODENAME.lower() in board["cards"][0]["plan"].lower(), "the plan FILENAME carried the token too"


def test_kanban_json_omits_titles_while_keeping_every_consumer_field(tmp_path, monkeypatch):
    """Nothing reads `title` out of provider-kanban.json — omit it, don't rename it.

    Consumers (verified by grep): scripts/ai/provider-dispatch-loop.py reads
    number / provider_route / machine_route / machine_blocker / hover.labels and
    the lane grouping; scripts/ai/provider-kanban-server.py reads the rendered
    HTML only. Neither reads any title.
    """
    board = _build_kanban(
        tmp_path, monkeypatch, 9202, f"epic: {SYNTH_LONG} rollout {TITLE_MARKER}", _guard(tmp_path)
    )
    payload = kanban.kanban_json_payload(board)
    js = json.dumps(payload)

    # Rename-proof: the title TEXT must not survive under any key.
    assert TITLE_MARKER not in js, "the issue title must not reach provider-kanban.json under any field name"

    # …and the dispatch-loop contract must still hold.
    card = payload["cards"][0]
    for field in ("number", "provider_route", "machine_route", "machine_blocker", "lane", "hover"):
        assert field in card, f"consumer field {field!r} must survive title omission"
    assert isinstance(card["hover"]["labels"], list) and "status:plan-review" in card["hover"]["labels"]

    # Lane grouping must survive, and must place THIS card — an empty scan would
    # otherwise read exactly like a pass.
    placed = {
        lane: [c["number"] for c in cards]
        for lane, cards in payload["lanes"].items()
        if cards
    }
    assert placed, "lane grouping must survive title omission"
    assert 9202 in {n for numbers in placed.values() for n in numbers}, (
        f"card 9202 must still be placed in a lane; got {placed}"
    )
    # lanes and cards must describe the SAME stripped records, not diverge.
    assert TITLE_MARKER not in json.dumps(payload["lanes"])


def test_kanban_dashboards_still_show_the_redacted_title(tmp_path, monkeypatch):
    """Omission destroys a Kanban card. The human artifacts keep a redacted title."""
    board = _build_kanban(
        tmp_path, monkeypatch, 9203, f"epic: {SYNTH_LONG} rollout {TITLE_MARKER}", _guard(tmp_path)
    )
    md = kanban.render_markdown(board)
    html = kanban.render_html(board)

    for name, text in (("markdown", md), ("html", html)):
        assert TITLE_MARKER in text, f"{name} dashboard must still carry the issue title"
        assert CODENAME_LONG in text, f"{name} dashboard must show the codename in place of the client"


def test_kanban_withholds_free_text_visibly_when_map_absent(tmp_path, monkeypatch):
    board = _build_kanban(
        tmp_path, monkeypatch, 9204, f"epic: {SYNTH_LONG} rollout {TITLE_MARKER}", _absent_guard(tmp_path)
    )
    js = json.dumps(kanban.kanban_json_payload(board))
    md = kanban.render_markdown(board)
    html = kanban.render_html(board)

    for text in (js, md, html):
        assert SYNTH_CLIENT.lower() not in text.lower()
        assert TITLE_MARKER not in text, "with no map, free text must be withheld everywhere"
    assert board["pii_redaction"]["mode"] == "withheld"
    assert work_queue.PII_WITHHELD in md and work_queue.PII_WITHHELD in html
    # Machine-readable taxonomy the dispatch loop needs must NOT be withheld.
    assert "status:plan-review" in board["cards"][0]["hover"]["labels"]


# ═══════════════════════════════════════════════════════════════════════════
# provider-autolabel.py
# ═══════════════════════════════════════════════════════════════════════════


def _autolabel_queue(title: str) -> dict:
    item = {
        "number": 9301,
        "title": title,
        "url": "https://example.test/issues/9301",
        "labels": [],
        "execution_ready": True,
        "priority_rank": 1,
        "routing_reason": "implementation/test/fix language",
        "provider_priority": "highest",
    }
    return {
        "provider_queues": {
            "claude": {"top_issues": []},
            "codex": {"top_issues": [item]},
            "agy": {"top_issues": []},
        }
    }


def test_autolabel_json_omits_titles_and_markdown_keeps_them(tmp_path):
    payload = autolabel.build_payload(
        _autolabel_queue(f"fix: {SYNTH_LONG} {TITLE_MARKER}"),
        apply_mode=False,
        limit=0,
        guard=_guard(tmp_path),
    )
    js = json.dumps(autolabel.autolabel_json_payload(payload))
    md = autolabel.render_markdown(payload)

    assert SYNTH_CLIENT.lower() not in js.lower()
    assert SYNTH_CLIENT.lower() not in md.lower()
    assert TITLE_MARKER not in js, "no consumer reads title out of provider-autolabel-candidates.json"
    assert TITLE_MARKER in md, "the routing-rationale row is useless without a title"
    assert CODENAME_LONG in md
    # Candidate identity the report is keyed on must survive.
    candidate = json.loads(js)["candidates"][0]
    for field in ("number", "url", "labels", "target_label", "confidence", "eligible"):
        assert field in candidate


def test_autolabel_scrub_is_idempotent_over_already_redacted_input(tmp_path):
    """Titles arrive from provider-work-queue.json ALREADY redacted; a second pass
    must be a no-op or every 4-hourly run emits a spurious diff."""
    guard = _guard(tmp_path)
    once = guard.scrub(f"fix: {SYNTH_LONG} and {SYNTH_CLIENT} {TITLE_MARKER}")
    assert guard.scrub(once) == once

    first = autolabel.build_payload(_autolabel_queue(once), apply_mode=False, limit=0, guard=guard)
    second = autolabel.build_payload(
        _autolabel_queue(first["candidates"][0]["title"]), apply_mode=False, limit=0, guard=guard
    )
    assert first["candidates"][0]["title"] == second["candidates"][0]["title"]
    assert autolabel.render_markdown(first).replace(first["generated_at"], "") == (
        autolabel.render_markdown(second).replace(second["generated_at"], "")
    )


def test_autolabel_withholds_titles_when_map_absent(tmp_path):
    payload = autolabel.build_payload(
        _autolabel_queue(f"fix: {SYNTH_LONG} {TITLE_MARKER}"),
        apply_mode=False,
        limit=0,
        guard=_absent_guard(tmp_path),
    )
    js = json.dumps(autolabel.autolabel_json_payload(payload))
    md = autolabel.render_markdown(payload)
    assert TITLE_MARKER not in js and TITLE_MARKER not in md
    assert payload["pii_redaction"]["mode"] == "withheld"
    assert work_queue.PII_WITHHELD in md


# ═══════════════════════════════════════════════════════════════════════════
# guard properties
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.parametrize("map_present", [True, False])
def test_every_rendered_dashboard_states_its_redaction_mode(tmp_path, monkeypatch, map_present):
    """The mode must be readable in the ARTIFACT, not only in the JSON metadata.

    Asserted on strings only the banner can produce — an earlier version of this
    file checked for PII_WITHHELD, which the withheld table ROWS also contain, so
    deleting the banner left the test green (caught by mutation testing).
    """
    guard = _guard(tmp_path) if map_present else _absent_guard(tmp_path)
    # Banner-only markers: neither can appear in a title, a label or a row value.
    marker = "#3768)" if map_present else "Provision the private map and re-run"

    wq_md = work_queue.render_markdown(
        work_queue.build_queue(_wq_scorecard(), [_wq_issue(9501, "fix: thing")], guard=guard)
    )
    assert marker in wq_md, "provider-work-queue.md must state its redaction mode"

    al_md = autolabel.render_markdown(
        autolabel.build_payload(_autolabel_queue("fix: thing"), apply_mode=False, limit=0, guard=guard)
    )
    assert marker in al_md, "provider-autolabel-candidates.md must state its redaction mode"

    board = _build_kanban(tmp_path, monkeypatch, 9502, "epic: thing", guard)
    assert marker in kanban.render_markdown(board), "the Kanban Markdown dashboard must state its mode"
    assert marker in kanban.render_html(board), "the Kanban HTML dashboard must state its mode"


def test_negative_control_token_survives_a_map_that_does_not_name_it(tmp_path):
    """Negative control (per .claude/rules/guards-must-discriminate.md §9).

    Every other assertion in this file is `token not in artifact`. If the guard
    silently stopped matching — or the token never reached the artifact in the
    first place — those would all still pass. This test proves the opposite
    direction: with a map that does NOT name the token, the token DOES reach
    every artifact. If this test starts failing, the `not in` assertions above
    have gone blind and are measuring nothing.
    """
    unrelated_map = tmp_path / "unrelated-map.yaml"
    unrelated_map.write_text(
        "version: 1\nrules:\n  - pattern: 'Nothingburger'\n"
        "    replacement: 'CLIENT-NONE'\n    word_bound: true\n",
        encoding="utf-8",
    )
    blind_guard = work_queue.load_pii_guard(unrelated_map)
    assert blind_guard.available is True, "the control must run in redacted mode, not withheld"

    queue = work_queue.build_queue(
        _wq_scorecard(),
        [_wq_issue(9401, f"fix: {SYNTH_LONG} pipeline {TITLE_MARKER}")],
        guard=blind_guard,
    )
    assert SYNTH_CLIENT in json.dumps(queue), "control: an unmatched token must reach the JSON"
    assert SYNTH_CLIENT in work_queue.render_markdown(queue), "control: and the Markdown"

    payload = autolabel.build_payload(
        _autolabel_queue(f"fix: {SYNTH_LONG} {TITLE_MARKER}"),
        apply_mode=False,
        limit=0,
        guard=blind_guard,
    )
    assert SYNTH_CLIENT in autolabel.render_markdown(payload), "control: and the autolabel report"


def test_negative_control_kanban_surfaces_carry_an_unmatched_token(tmp_path, monkeypatch):
    """Same control for the kanban writer, including the plan-derived hover text.

    Proves the title / plan_summary / risks / plan-path assertions above are
    actually exercising those surfaces rather than reading empty strings.
    """
    unrelated_map = tmp_path / "unrelated-map.yaml"
    unrelated_map.write_text(
        "version: 1\nrules:\n  - pattern: 'Nothingburger'\n"
        "    replacement: 'CLIENT-NONE'\n    word_bound: true\n",
        encoding="utf-8",
    )
    blind_guard = work_queue.load_pii_guard(unrelated_map)
    board = _build_kanban(
        tmp_path, monkeypatch, 9402, f"epic: {SYNTH_LONG} rollout {TITLE_MARKER}", blind_guard
    )
    hover = board["cards"][0]["hover"]
    assert SYNTH_CLIENT.lower() in hover["plan_summary"].lower(), "control: plan summary surface is live"
    assert SYNTH_CLIENT.lower() in hover["risks"].lower(), "control: risks surface is live"
    assert SYNTH_CLIENT.lower() in board["cards"][0]["plan"].lower(), "control: plan-path surface is live"
    assert SYNTH_CLIENT in kanban.render_markdown(board)
    assert SYNTH_CLIENT in kanban.render_html(board)
    assert SYNTH_CLIENT in json.dumps(kanban.kanban_json_payload(board)), (
        "control: hover text reaches the JSON, so the omission tests are not vacuous"
    )


def test_guard_scrub_is_idempotent_and_preserves_non_client_text(tmp_path):
    guard = _guard(tmp_path)
    raw = f"{SYNTH_LONG} / {SYNTH_CLIENT.upper()} / {SYNTH_CLIENT.lower()} — keep {TITLE_MARKER}"
    once = guard.scrub(raw)
    assert SYNTH_CLIENT.lower() not in once.lower()
    assert TITLE_MARKER in once
    assert guard.scrub(once) == once
    assert guard.scrub(guard.scrub(once)) == once


def test_guard_falls_back_to_withheld_when_the_engine_cannot_load(tmp_path, monkeypatch):
    """A missing PyYAML (the cron runs `uv run --no-project`) must withhold, not raise
    and not emit raw text."""
    monkeypatch.setattr(work_queue, "_load_redactor", lambda: (_ for _ in ()).throw(ImportError("no yaml")))
    guard = work_queue.load_pii_guard(_write_map(tmp_path))
    assert guard.available is False
    assert guard.scrub(f"{SYNTH_LONG} {TITLE_MARKER}") == work_queue.PII_WITHHELD
    assert "engine" in guard.metadata()["reason"]


def test_guard_resolves_map_from_legal_client_map_env(tmp_path, monkeypatch):
    """Same sourcing precedence as scripts/legal/check-client-pii.py."""
    monkeypatch.setenv("LEGAL_CLIENT_MAP", str(_write_map(tmp_path)))
    guard = work_queue.load_pii_guard()
    assert guard.available is True
    assert SYNTH_CLIENT.lower() not in guard.scrub(SYNTH_LONG).lower()


def test_all_three_writers_share_one_guard_implementation():
    """Three copies of a security guard drift; only one of them gets fixed.

    Asserts the guard each writer uses is DEFINED IN one file — copy-pasting it
    into a sibling writer moves the source file and fails this test.
    """
    import inspect

    home = str(REPO_ROOT / "scripts" / "ai" / "provider-work-queue.py")
    for name, mod in (("kanban", kanban), ("autolabel", autolabel), ("work_queue", work_queue)):
        for attr in ("load_pii_guard", "PiiGuard", "pii_banner"):
            src = inspect.getsourcefile(getattr(mod, attr))
            assert src == home, f"{name}.{attr} is defined in {src}, not the single guard home"


@pytest.mark.skipif(
    not (REPO_ROOT / "config" / "agents" / ".client-codename-map.local.yaml").is_file()
    and not os.environ.get("LEGAL_CLIENT_MAP"),
    reason="private client-codename map not provisioned on this host",
)
def test_real_map_codenames_do_not_rematch(tmp_path):
    """Idempotency depends on no codename matching another rule. Guard the REAL map.

    Values are never printed — only counts and a boolean.
    """
    guard = work_queue.load_pii_guard()
    assert guard.available is True
    rematching = sum(1 for repl in guard.replacements() if guard.scrub(repl) != repl)
    assert rematching == 0, (
        f"{rematching} codename(s) in the private map are re-matched by another rule; "
        "redaction would not be idempotent and every 4-hourly run would diff"
    )
