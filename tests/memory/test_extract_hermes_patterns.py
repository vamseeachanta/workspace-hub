"""TDD tests for #3253 — Hermes pattern → skill/memory CANDIDATE emitter (epic #3248).

Targets scripts/memory/extract_hermes_patterns.py: the PURE core (extract_patterns,
strip_bridge_block, canonical_text_index, is_already_canonical, is_sensitive,
candidate_signature, evaluate, existing_candidate_keys, append_candidates_md) plus the thin
CLI (run_cli, publish_candidates). Pattern mirrors tests/curation/test_detect_skill_drift.py
(importlib spec load + monkeypatched module globals + injectable notify_fn).

The headline test is test_dedup_survives_bridge_injection — the round-2 BLOCKER regression:
it FAILS under a naive canonical index that slugifies the bridge-injected agents.md block, and
PASSES once strip_bridge_block excludes that block. test_dedup_drops_human_promoted_outside_block
is its companion (the same text OUTSIDE the markers must still de-dup).
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "memory" / "extract_hermes_patterns.py"

spec = importlib.util.spec_from_file_location("extract_hermes_patterns", MODULE_PATH)
assert spec is not None and spec.loader is not None
ehp = importlib.util.module_from_spec(spec)
sys.modules["extract_hermes_patterns"] = ehp
spec.loader.exec_module(ehp)

NOW = "2026-06-27T12:00:00+00:00"


# ── helpers ────────────────────────────────────────────────────────────────
def _cand(key, summary=None, kind="memory", source="MEMORY.md") -> dict:
    return {"key": key, "summary": summary or key, "kind": kind, "source_file": source}


def _evaluate(patterns, canonical=None, skills=None, deny=None, last=None):
    return ehp.evaluate(
        patterns, canonical or set(), skills or set(), deny or [], last, now_iso=NOW
    )


# ── extract_patterns: PURE parse ────────────────────────────────────────────
def test_extract_basic():
    cands = ehp.extract_patterns("a§b§c", source_file="MEMORY.md")
    assert len(cands) == 3
    assert [c["key"] for c in cands] == ["a", "b", "c"]
    assert all(c["source_file"] == "MEMORY.md" for c in cands)


def test_extract_strips_leading_dash():
    # '- foo bar' and 'foo bar' slugify to the same key (matches the bridge's `- ${line}` form)
    a = ehp.extract_patterns("- foo bar", source_file="MEMORY.md")[0]["key"]
    b = ehp.extract_patterns("foo bar", source_file="MEMORY.md")[0]["key"]
    assert a == b == "foo-bar"


def test_extract_dedups_within_source():
    cands = ehp.extract_patterns("same thing§same thing", source_file="MEMORY.md")
    assert len(cands) == 1


def test_extract_skips_empty_and_section_markers():
    cands = ehp.extract_patterns("real line§§§   ", source_file="MEMORY.md")
    assert [c["key"] for c in cands] == ["real-line"]


# ── signature: order-independent ────────────────────────────────────────────
def test_signature_order_independent():
    assert ehp.candidate_signature([_cand("b"), _cand("a")]) == ehp.candidate_signature(
        [_cand("a"), _cand("b")]
    )


def test_signature_clean_when_empty():
    assert ehp.candidate_signature([]) == "CLEAN"


# ── strip_bridge_block + the round-2 BLOCKER regression ─────────────────────
def test_strip_bridge_block_removes_span():
    text = "header line\n<!-- BRIDGE:START -->\n- injected pattern\n<!-- BRIDGE:END -->\nfooter line"
    out = ehp.strip_bridge_block(text)
    assert "header line" in out
    assert "footer line" in out
    assert "injected pattern" not in out
    assert "BRIDGE:START" not in out and "BRIDGE:END" not in out


def _write_memory(tmp_path, agents_body):
    mem = tmp_path / "memory"
    mem.mkdir()
    (mem / "agents.md").write_text(agents_body, encoding="utf-8")
    return mem


def test_dedup_survives_bridge_injection(tmp_path, monkeypatch):
    """ROUND-2 BLOCKER: a pattern present ONLY inside the bridge-injected block of agents.md must
    NOT be treated as already-canonical (the bridge re-injects the same Hermes text every run,
    BEFORE the extractor). FAILS if canonical_text_index slugifies the bridge block."""
    agents = (
        "# Agents\nsome human note\n"
        "<!-- BRIDGE:START -->\n"
        "## Synced from Hermes Memory\n- the unpromoted pattern\n"
        "<!-- BRIDGE:END -->\n"
    )
    mem = _write_memory(tmp_path, agents)
    monkeypatch.setattr(ehp, "MEMORY", mem)
    idx = ehp.canonical_text_index()
    assert ehp._slug("the unpromoted pattern") not in idx  # block stripped from the index
    cand = _cand("the-unpromoted-pattern")
    r = _evaluate([cand], canonical=idx)
    assert any(c["key"] == "the-unpromoted-pattern" for c in r["candidates"])


def test_dedup_drops_human_promoted_outside_block(tmp_path, monkeypatch):
    """Companion: the SAME text placed OUTSIDE the bridge markers (genuinely human-promoted) IS
    de-duped away."""
    agents = (
        "# Agents\n- the unpromoted pattern\n"
        "<!-- BRIDGE:START -->\n- something else\n<!-- BRIDGE:END -->\n"
    )
    mem = _write_memory(tmp_path, agents)
    monkeypatch.setattr(ehp, "MEMORY", mem)
    idx = ehp.canonical_text_index()
    assert ehp._slug("the unpromoted pattern") in idx
    r = _evaluate([_cand("the-unpromoted-pattern")], canonical=idx)
    assert not r["candidates"]


def test_dedup_uses_full_content_surface(tmp_path, monkeypatch):
    """Gate indexes MEMORY.rglob TEXT (not basenames), including OLD/nested files — so a pattern in
    topics/old.md is still de-duped (no 200-cap / mtime cutoff)."""
    mem = tmp_path / "memory"
    (mem / "topics").mkdir(parents=True)
    (mem / "topics" / "old.md").write_text("- archived lesson here\n", encoding="utf-8")
    monkeypatch.setattr(ehp, "MEMORY", mem)
    idx = ehp.canonical_text_index()
    r = _evaluate([_cand("archived-lesson-here")], canonical=idx)
    assert not r["candidates"]


# ── de-dup gates: canonical + skills ────────────────────────────────────────
def test_dedup_against_canonical():
    r = _evaluate([_cand("k")], canonical={"k"})
    assert not r["candidates"]


def test_dedup_against_skills():
    r = _evaluate([_cand("k")], skills={"k"})
    assert not r["candidates"]


# ── PII / secret scrub (fail-closed) ────────────────────────────────────────
def _live_client_token() -> str:
    """Derive a real deny-list token at RUNTIME (un-escaped) so no client literal is ever written
    into this test source — otherwise the legal scanner would block its own test artifact
    (SHARED_SOUL "enforcement scripts must not block their own artifacts")."""
    import re as _re

    deny = ehp.load_deny_patterns(REPO_ROOT / ".legal-deny-list.yaml")
    assert deny, "deny-list must yield patterns"
    return _re.sub(r"\\(.)", r"\1", deny[0])  # un-escape the first escaped pattern


def test_scrub_sensitive_failclosed():
    deny = ehp.load_deny_patterns(REPO_ROOT / ".legal-deny-list.yaml")
    token = _live_client_token()
    bad = _cand(ehp._slug(token), summary=f"a session note that mentions {token} economics")
    r = _evaluate([bad], deny=deny)
    assert not r["candidates"]
    assert r["dropped_sensitive"] == 1


def test_scrub_clean_passes():
    deny = ehp.load_deny_patterns(REPO_ROOT / ".legal-deny-list.yaml")
    r = _evaluate([_cand("generic-engineering-note", summary="prefer parameterized queries")], deny=deny)
    assert len(r["candidates"]) == 1
    assert r["dropped_sensitive"] == 0


def test_load_deny_patterns_no_yaml_dep(monkeypatch):
    """Loader must NOT need pyyaml (the bridge launches bare python3 / uv --no-project)."""
    monkeypatch.setitem(sys.modules, "yaml", None)
    deny = ehp.load_deny_patterns(REPO_ROOT / ".legal-deny-list.yaml")
    assert len(deny) >= 10  # the client_references block alone has well over ten patterns


# ── feedback-loop guard ─────────────────────────────────────────────────────
def test_never_reads_cross_provider_md():
    assert "cross-provider.md" not in ehp.SOURCES
    assert ehp.SOURCES == ["MEMORY.md", "USER.md"]


# ── spam suppression ────────────────────────────────────────────────────────
def test_new_candidates_alert_once():
    r = _evaluate([_cand("a"), _cand("b")], last=None)
    assert r["new"] is True
    assert len(r["alerts"]) == 1
    assert r["alerts"][0]["status"] == "pass"


def test_same_candidates_suppressed():
    sig = ehp.candidate_signature([_cand("a")])
    r = _evaluate([_cand("a")], last={"signature": sig})
    assert r["new"] is False
    assert r["alerts"] == []


def test_changed_set_realerts():
    sig = ehp.candidate_signature([_cand("a")])
    r = _evaluate([_cand("a"), _cand("b")], last={"signature": sig})
    assert r["new"] is True
    assert len(r["alerts"]) == 1


def test_cleared_no_alert():
    r = _evaluate([], last={"signature": "a"})
    assert r["alerts"] == []
    assert r["signature"] == "CLEAN"


# ── idempotent append ───────────────────────────────────────────────────────
def test_append_idempotent_no_double(tmp_path):
    path = tmp_path / "hermes-pattern-candidates.md"
    path.write_text("# Hermes Pattern Candidates\n", encoding="utf-8")
    cands = [_cand("a"), _cand("b")]
    ehp.append_candidates_md(path, cands, dropped=0)
    ehp.append_candidates_md(path, cands, dropped=0)
    body = path.read_text()
    assert body.count("- key: a") == 1
    assert body.count("- key: b") == 1


def test_append_noop_when_nothing_new(tmp_path):
    path = tmp_path / "hermes-pattern-candidates.md"
    path.write_text("# Hermes Pattern Candidates\n", encoding="utf-8")
    ehp.append_candidates_md(path, [_cand("a")], dropped=0)
    before = path.read_text()
    ehp.append_candidates_md(path, [_cand("a")], dropped=0)
    assert path.read_text() == before


def test_append_dropped_only_is_idempotent(tmp_path):
    """A run with sensitive DROPS but no new candidates must NOT re-append a notice block every cron
    cycle (else the file grows unbounded). File stays untouched when there are no new keys."""
    path = tmp_path / "hermes-pattern-candidates.md"
    path.write_text("# Hermes Pattern Candidates\n", encoding="utf-8")
    ehp.append_candidates_md(path, [], dropped=2)
    before = path.read_text()
    ehp.append_candidates_md(path, [], dropped=2)
    assert path.read_text() == before == "# Hermes Pattern Candidates\n"


def test_status_is_candidate(tmp_path):
    path = tmp_path / "hermes-pattern-candidates.md"
    path.write_text("# Hermes Pattern Candidates\n", encoding="utf-8")
    ehp.append_candidates_md(path, [_cand("a")], dropped=0)
    assert "status: candidate" in path.read_text()


def test_no_promotion_status_strings(tmp_path):
    path = tmp_path / "hermes-pattern-candidates.md"
    path.write_text("# Hermes Pattern Candidates\n", encoding="utf-8")
    ehp.append_candidates_md(path, [_cand("a"), _cand("b")], dropped=1)
    body = path.read_text()
    for forbidden in ("status:plan-approved", "status:completeness-verified", "promoted", "approved"):
        assert forbidden not in body


def test_existing_candidate_keys_roundtrip(tmp_path):
    path = tmp_path / "hermes-pattern-candidates.md"
    path.write_text("# Hermes Pattern Candidates\n", encoding="utf-8")
    ehp.append_candidates_md(path, [_cand("alpha"), _cand("beta")], dropped=0)
    assert ehp.existing_candidate_keys(path) == {"alpha", "beta"}


# ── evaluate purity ─────────────────────────────────────────────────────────
def test_evaluate_pure_no_io(monkeypatch):
    def _boom(*a, **k):
        raise AssertionError("evaluate must perform no IO")

    monkeypatch.setattr(ehp.subprocess, "run", _boom)
    monkeypatch.setattr("builtins.open", _boom)
    _evaluate([_cand("a")])  # must not raise


# ── run_cli: injected notify, no-op, no canonical writes, rc 0 ──────────────
def _setup_cli(tmp_path, monkeypatch, *, hermes_text="- a fresh lesson\n- another fresh lesson"):
    hermes = tmp_path / "hermes"
    hermes.mkdir()
    if hermes_text is not None:
        (hermes / "MEMORY.md").write_text(hermes_text, encoding="utf-8")
    mem = tmp_path / "memory"
    mem.mkdir()
    (mem / "agents.md").write_text("# Agents\n", encoding="utf-8")
    skills = tmp_path / "skills"
    skills.mkdir()
    cand_dir = tmp_path / "candidates"
    cand_dir.mkdir()
    monkeypatch.setattr(ehp, "HERMES_DIR", hermes)
    monkeypatch.setattr(ehp, "MEMORY", mem)
    monkeypatch.setattr(ehp, "SKILLS_DIR", skills)
    monkeypatch.setattr(ehp, "STATE_CAND", cand_dir)
    monkeypatch.setattr(ehp, "CANDIDATES", cand_dir / "hermes-pattern-candidates.md")
    monkeypatch.setattr(ehp, "machine_label", lambda: "dev-primary")
    return SimpleNamespace(hermes=hermes, mem=mem, cand_dir=cand_dir)


def test_run_cli_injected_notify(tmp_path, monkeypatch):
    ctx = _setup_cli(tmp_path, monkeypatch)
    calls = []
    rc = ehp.run_cli(SimpleNamespace(publish=False), notify_fn=calls.append)
    assert rc == 0
    assert len(calls) == 1  # one "new candidates" alert
    assert ctx.cand_dir.joinpath("hermes-pattern-candidates.md").exists()
    assert ctx.cand_dir.joinpath("hermes-patterns-last-seen-dev-primary.json").exists()


def test_returns_zero_on_candidates(tmp_path, monkeypatch):
    _setup_cli(tmp_path, monkeypatch)
    assert ehp.run_cli(SimpleNamespace(publish=False), notify_fn=lambda a: None) == 0


def test_no_hermes_is_noop(tmp_path, monkeypatch):
    _setup_cli(tmp_path, monkeypatch, hermes_text=None)
    calls = []
    rc = ehp.run_cli(SimpleNamespace(publish=False), notify_fn=calls.append)
    assert rc == 0
    assert calls == []
    assert not (tmp_path / "candidates" / "hermes-pattern-candidates.md").exists()


def test_run_cli_spam_suppressed_second_run(tmp_path, monkeypatch):
    _setup_cli(tmp_path, monkeypatch)
    calls = []
    ehp.run_cli(SimpleNamespace(publish=False), notify_fn=calls.append)
    ehp.run_cli(SimpleNamespace(publish=False), notify_fn=calls.append)
    assert len(calls) == 1  # second identical run is suppressed


def test_canonical_gate_no_canonical_writes(tmp_path, monkeypatch):
    _setup_cli(tmp_path, monkeypatch)
    writes: list[str] = []
    real_write = Path.write_text

    def _spy(self, *a, **k):
        writes.append(str(self))
        return real_write(self, *a, **k)

    monkeypatch.setattr(Path, "write_text", _spy)
    ehp.run_cli(SimpleNamespace(publish=False), notify_fn=lambda a: None)
    assert writes, "expected at least one write"
    for w in writes:
        assert ".claude/memory/" not in w
        assert ".claude/skills/" not in w
        assert "config/agents/" not in w


def test_machine_label_reused(tmp_path, monkeypatch):
    ctx = _setup_cli(tmp_path, monkeypatch)
    monkeypatch.setattr(ehp, "machine_label", lambda: "boxlbl")
    ehp.run_cli(SimpleNamespace(publish=False), notify_fn=lambda a: None)
    assert ctx.cand_dir.joinpath("hermes-patterns-last-seen-boxlbl.json").exists()


def test_cross_dir_import_resolves():
    # machine_label + MEMORY came from scripts/curation via the sys.path insert.
    assert callable(ehp.machine_label)
    assert isinstance(ehp.MEMORY, Path)


# ── publish: off by default + bounded ───────────────────────────────────────
def test_publish_off_by_default(tmp_path, monkeypatch):
    _setup_cli(tmp_path, monkeypatch)

    def _boom(*a, **k):
        raise AssertionError("no publish without --publish")

    monkeypatch.setattr(ehp.subprocess, "run", _boom)
    assert ehp.run_cli(SimpleNamespace(publish=False), notify_fn=lambda a: None) == 0


def test_publish_bounded_timeout(tmp_path, monkeypatch):
    cand_dir = tmp_path / "candidates"
    cand_dir.mkdir()
    (cand_dir / "hermes-pattern-candidates.md").write_text("# x\n", encoding="utf-8")
    monkeypatch.setattr(ehp, "STATE_CAND", cand_dir)
    monkeypatch.setattr(ehp, "CANDIDATES", cand_dir / "hermes-pattern-candidates.md")
    # EQUIVALENCE_CLI is the real repo file (exists); CANDIDATES set above exists — so publish
    # proceeds to the bounded subprocess, which we force to time out.

    def _timeout(*a, **k):
        raise subprocess.TimeoutExpired(cmd="publish", timeout=ehp.PUBLISH_TIMEOUT_S)

    monkeypatch.setattr(ehp.subprocess, "run", _timeout)
    assert ehp.publish_candidates("dev-primary") == f"publish-timeout ({ehp.PUBLISH_TIMEOUT_S}s)"


# ── bridge wiring: self-contained §7c (grep) ────────────────────────────────
def test_bridge_wiring_self_contained():
    bridge = (REPO_ROOT / "scripts" / "memory" / "bridge-hermes-claude.sh").read_text()
    assert "extract_hermes_patterns.py" in bridge
    # the §7c block defines its OWN launcher HPY and never references the §7b-scoped RBPY
    start = bridge.index("extract_hermes_patterns.py")
    block = bridge[start - 400 : start + 400]
    assert "HPY=" in block
    assert "RBPY" not in block
    assert "(soft)" in block  # the || echo ... soft guard
