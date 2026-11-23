"""TDD tests for #3256 (b) — Gemini-specific vs shared skill-scope classifier (epic #3248).

Targets scripts/curation/classify_skill_scope.py: the PURE core (``classify_scope``) plus the thin
CLI (``run_cli``). The classifier REUSES audit_skill_currency's ``_families`` / ``_load_allow`` /
(refactored module-level) ``_allowed`` — it must not reimplement the family/allowlist machinery.

Round-2 major #2: the classifier MUST NOT write `.claude/state/candidates/skill-candidates.md`
(cron-regenerated, "do not edit manually", two append-owners). Its only durable output is the
`.claude/state/skill-scope-classification.json` sidecar.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "curation" / "classify_skill_scope.py"

spec = importlib.util.spec_from_file_location("classify_skill_scope", MODULE_PATH)
assert spec is not None and spec.loader is not None
cls = importlib.util.module_from_spec(spec)
sys.modules["classify_skill_scope"] = cls
spec.loader.exec_module(cls)


# ── PURE CORE: classify_scope ──────────────────────────────────────────────────
def _sets(canonical=(), gemini=(), allow=()):
    return dict(canonical=set(canonical), gemini=set(gemini), allow=list(allow))


def test_shared_when_in_canonical():
    assert cls.classify_scope("research", **_sets(canonical=["research"])) == "shared"


def test_gemini_specific_exact_allow():
    assert cls.classify_scope("memory", **_sets(gemini=["memory"], allow=["memory"])) == "gemini-specific"


def test_gemini_specific_prefix_allow():
    assert cls.classify_scope(
        "source-command-x", **_sets(gemini=["source-command-x"], allow=["source-command-"])
    ) == "gemini-specific"


def test_no_substring_overmatch():
    # exact allowlist entry 'memory' must NOT match 'memory-bank'
    out = cls.classify_scope("memory-bank", **_sets(gemini=["memory-bank"], allow=["memory"]))
    assert out != "gemini-specific"
    assert out == "gemini-drift"  # on gemini surface, not allowlisted, not canonical


def test_gemini_drift_when_on_surface_not_allowed():
    assert cls.classify_scope(
        "rogue", **_sets(gemini=["rogue"], allow=["memory"])
    ) == "gemini-drift"


def test_default_shared_for_new_family():
    # in neither set, not allowlisted ⇒ new cross-provider need ⇒ canonical .claude/skills
    assert cls.classify_scope("brand-new", **_sets()) == "shared"


def test_canonical_wins_over_allow():
    # a family present on canonical is 'shared' even if it also appears in the allowlist
    assert cls.classify_scope(
        "memory", **_sets(canonical=["memory"], gemini=["memory"], allow=["memory"])
    ) == "shared"


# ── reuse-not-reimplement assertions ──────────────────────────────────────────
def test_reuses_audit_allowed(monkeypatch):
    import audit_skill_currency
    calls = {"n": 0}

    def _spy(f, allow):
        calls["n"] += 1
        return f == "memory"

    monkeypatch.setattr(audit_skill_currency, "_allowed", _spy)
    monkeypatch.setattr(cls, "_allowed", _spy)
    assert cls.classify_scope("memory", **_sets(gemini=["memory"], allow=["memory"])) == "gemini-specific"
    assert calls["n"] >= 1


def test_reuses_families_and_load_allow(monkeypatch, tmp_path):
    import audit_skill_currency
    seen = {"families": 0, "allow": 0}

    def _fam(prefix):
        seen["families"] += 1
        return {"research"} if prefix == audit_skill_currency.CANONICAL_PREFIX else {"memory"}

    def _allow():
        seen["allow"] += 1
        return ["memory"]

    monkeypatch.setattr(cls, "_families", _fam)
    monkeypatch.setattr(cls, "_load_allow", _allow)
    state = tmp_path / "scope.json"
    rc = cls.run_cli(SimpleNamespace(families=["memory", "research"], state=str(state), stdout=False))
    assert rc == 0
    assert seen["families"] >= 2 and seen["allow"] >= 1


# ── THIN CLI ───────────────────────────────────────────────────────────────────
def test_cli_writes_classification_json_exit_zero(tmp_path, monkeypatch):
    monkeypatch.setattr(cls, "_families",
                        lambda p: {"research"} if p == cls.CANON else {"memory"})
    monkeypatch.setattr(cls, "_load_allow", lambda: ["memory"])
    state = tmp_path / "scope.json"
    rc = cls.run_cli(SimpleNamespace(families=["memory", "research", "new-x"], state=str(state), stdout=False))
    assert rc == 0
    doc = json.loads(state.read_text())
    assert doc["schema_version"] == 1
    by = {c["family"]: c["scope"] for c in doc["classifications"]}
    assert by == {"memory": "gemini-specific", "research": "shared", "new-x": "shared"}


def test_cli_never_writes_skill_candidates_md(tmp_path, monkeypatch):
    # round-2 major #2: the classifier must NEVER open skill-candidates.md for writing.
    import builtins
    real_open = builtins.open
    candidates_md = REPO_ROOT / ".claude" / "state" / "candidates" / "skill-candidates.md"
    before = candidates_md.read_bytes() if candidates_md.exists() else None

    def _guard_open(file, mode="r", *a, **k):
        name = str(file)
        if name.endswith("skill-candidates.md") and ("w" in mode or "a" in mode or "+" in mode):
            raise AssertionError(f"classifier opened skill-candidates.md for write: mode={mode}")
        return real_open(file, mode, *a, **k)

    monkeypatch.setattr(builtins, "open", _guard_open)
    monkeypatch.setattr(cls, "_families", lambda p: {"research"} if p == cls.CANON else {"memory"})
    monkeypatch.setattr(cls, "_load_allow", lambda: ["memory"])
    state = tmp_path / "scope.json"
    rc = cls.run_cli(SimpleNamespace(families=["memory"], state=str(state), stdout=False))
    assert rc == 0
    after = candidates_md.read_bytes() if candidates_md.exists() else None
    assert before == after  # byte-unchanged


def test_cli_stdout_does_not_write_state(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cls, "_families", lambda p: set())
    monkeypatch.setattr(cls, "_load_allow", lambda: [])
    state = tmp_path / "nope.json"
    rc = cls.run_cli(SimpleNamespace(families=["x"], state=str(state), stdout=True))
    assert rc == 0
    assert not state.exists()
    assert json.loads(capsys.readouterr().out)["classifications"][0]["scope"] == "shared"


def test_cli_pure_core_no_io(monkeypatch):
    import builtins
    import subprocess

    def _boom(*a, **k):
        raise AssertionError("classify_scope performed IO")

    monkeypatch.setattr(builtins, "open", _boom)
    monkeypatch.setattr(subprocess, "run", _boom)
    assert cls.classify_scope("x", **_sets()) == "shared"


def test_cli_always_exits_zero_even_on_git_failure(tmp_path, monkeypatch):
    # _families returns None on git failure ⇒ classifier must degrade to empty sets, still rc 0
    monkeypatch.setattr(cls, "_families", lambda p: None)
    monkeypatch.setattr(cls, "_load_allow", lambda: [])
    state = tmp_path / "scope.json"
    rc = cls.run_cli(SimpleNamespace(families=["anything"], state=str(state), stdout=False))
    assert rc == 0
    doc = json.loads(state.read_text())
    assert doc["classifications"][0]["scope"] == "shared"
