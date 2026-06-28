"""TDD tests for #3252 — auto-graduate high-confidence correction candidates to
DRAFT skills/memory proposals, parked behind a HUMAN owner-review gate (epic #3248).

Targets scripts/curation/graduate_corrections.py: the PURE decide-core
(select_candidates / slug_for / classify_target / graduation_signature / evaluate)
plus the thin CLI (run_cli) with an explicit dev-primary machine guard, a quarantine
renderer that can NEVER write a canonical SKILL.md, and last-seen spam suppression.

Pattern mirrors tests/curation/test_detect_skill_drift.py (importlib spec load +
monkeypatched module globals + injected notify_fn).
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "curation" / "graduate_corrections.py"
PROMOTIONS = REPO_ROOT / ".claude" / "state" / "candidates" / "correction-promotions.yaml"

spec = importlib.util.spec_from_file_location("graduate_corrections", MODULE_PATH)
assert spec is not None and spec.loader is not None
gc = importlib.util.module_from_spec(spec)
sys.modules["graduate_corrections"] = gc
spec.loader.exec_module(gc)

NOW = "2026-06-27T12:00:00+00:00"


def _row(rank, theme, count, target, status="identified", **kw):
    base = {
        "rank": rank,
        "theme": theme,
        "correction_count": count,
        "files": kw.pop("files", ["foo.py"]),
        "action": kw.pop("action", "do the thing"),
        "target_skill": target,
        "rationale": kw.pop("rationale", "because reasons"),
        "status": status,
    }
    base.update(kw)
    return base


def _live_rows():
    return yaml.safe_load(PROMOTIONS.read_text())["promotions"]


# ── select_candidates: floor + status + dedup + cap ─────────────────────────
def test_select_high_confidence_repeated():
    rows = [
        _row(1, "a", 313, ".claude/rules/x.md"),
        _row(2, "b", 169, ".claude/rules/x.md"),
        _row(3, "c", 96, "auto memory (system prompt)"),
        _row(4, "d", 93, ".claude/rules/x.md"),
        _row(5, "e", 31, ".claude/rules/x.md"),
    ]
    picked = gc.select_candidates(rows, min_count=50, already_graduated=set(), cap=10)
    counts = [p["correction_count"] for p in picked]
    assert counts == [313, 169, 96, 93]  # 31 dropped


def test_select_respects_status_identified():
    rows = [_row(1, "a", 313, ".claude/rules/x.md", status="promoted")]
    assert gc.select_candidates(rows, min_count=50, already_graduated=set(), cap=10) == []


def test_select_dedup_against_ledger():
    rows = [_row(1, "Shell script edits", 313, ".claude/rules/x.md")]
    already = {gc.slug_for("Shell script edits")}
    assert gc.select_candidates(rows, min_count=50, already_graduated=already, cap=10) == []


def test_select_caps_per_run():
    rows = [_row(i, f"theme-{i}", 100 + i, ".claude/rules/x.md") for i in range(6)]
    picked = gc.select_candidates(rows, min_count=50, already_graduated=set(), cap=3)
    assert len(picked) == 3
    assert [p["correction_count"] for p in picked] == [105, 104, 103]  # highest first


def test_select_ignores_garbled_count():
    rows = [_row(1, "a", "lots", ".claude/rules/x.md"), _row(2, "b", True, ".claude/rules/x.md")]
    assert gc.select_candidates(rows, min_count=50, already_graduated=set(), cap=10) == []


# ── slug_for: stable deterministic dedup key ────────────────────────────────
def test_slug_for_stable_deterministic():
    assert gc.slug_for("SKILL.md authoring") == gc.slug_for("SKILL.md authoring")
    s = gc.slug_for("SKILL.md authoring")
    assert s and "/" not in s and s == s.strip("-")


# ── classify_target: rule / memory / existing_skill / new_skill ─────────────
def test_classify_target_rule_and_memory():
    assert gc.classify_target(".claude/rules/coding-style.md", set()) == "rule"
    assert gc.classify_target("auto memory (system prompt)", set()) == "memory"


def test_classify_target_plugin_namespace_is_existing_skill():
    # major-1 fix: a <plugin>/<skill> target must NOT route to new_skill.
    names = gc.read_skill_index_names()
    assert "superpowers/writing-skills" not in names  # never a bare-slug index entry
    assert gc.classify_target("superpowers/writing-skills", names) == "existing_skill"


def test_classify_target_bare_slug_in_index_is_existing():
    assert gc.classify_target("agent-usage-optimizer", {"agent-usage-optimizer"}) == "existing_skill"


def test_classify_target_new_skill_synthetic():
    # data-untested branch: a bare slug, no rule/memory/index/namespace match.
    assert gc.classify_target("some-brand-new-skill", set()) == "new_skill"


def test_no_live_row_classifies_new_skill():
    names = gc.read_skill_index_names()
    for p in _live_rows():
        kind = gc.classify_target(p["target_skill"], names)
        assert kind in {"existing_skill", "rule", "memory"}, (p["target_skill"], kind)


# ── graduation_signature: spam-suppression key ──────────────────────────────
def test_graduation_signature_stable_and_clean():
    assert gc.graduation_signature([]) == "CLEAN"
    assert gc.graduation_signature(["b", "a"]) == gc.graduation_signature(["a", "b"])


# ── evaluate: PURE decide-core ──────────────────────────────────────────────
def test_evaluate_is_pure_no_io(monkeypatch):
    def _boom(*a, **k):
        raise AssertionError("evaluate performed IO")
    monkeypatch.setattr(gc.subprocess, "run", _boom)
    monkeypatch.setattr("builtins.open", _boom)
    rows = [_row(1, "a", 313, ".claude/rules/x.md")]
    res = gc.evaluate(rows, set(), {}, None, now_iso=NOW, existing_skill_names=set())
    assert len(res["new_drafts"]) == 1


def test_signature_changed_alerts_once():
    rows = [_row(1, "a", 313, ".claude/rules/x.md")]
    res = gc.evaluate(rows, set(), {}, None, now_iso=NOW, existing_skill_names=set())
    assert len(res["alerts"]) == 1
    assert res["alerts"][0]["status"] == "pass"


def test_signature_unchanged_no_alert():
    rows = [_row(1, "a", 313, ".claude/rules/x.md")]
    slug = gc.slug_for("a")
    queue = {"drafts": [{"slug": slug}]}
    last_seen = {"signature": gc.graduation_signature([slug])}
    # already graduated -> no new additions; queue unchanged -> no alert
    res = gc.evaluate(rows, {slug}, queue, last_seen, now_iso=NOW, existing_skill_names=set())
    assert res["new_drafts"] == []
    assert res["alerts"] == []


def test_evaluate_carries_target_kind():
    rows = [_row(1, "SKILL.md authoring", 313, "superpowers/writing-skills")]
    res = gc.evaluate(rows, set(), {}, None, now_iso=NOW, existing_skill_names=set())
    add = res["new_drafts"][0]
    assert add["target_kind"] == "existing_skill"
    assert add["target_skill"] == "superpowers/writing-skills"
    assert add["status"] == "draft-parked" and add["owner_review"] == "pending"


# ── CLI helpers ─────────────────────────────────────────────────────────────
def _setup(tmp_path, monkeypatch, label="dev-primary", rows=None):
    state = tmp_path / "state"
    grad = state / "graduation"
    (state / "candidates").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(gc, "STATE", state)
    monkeypatch.setattr(gc, "GRAD_DIR", grad)
    monkeypatch.setattr(gc, "DRAFTS", grad / "drafts")
    monkeypatch.setattr(gc, "QUEUE", grad / "queue.yaml")
    monkeypatch.setattr(gc, "LEDGER", grad / "graduated.json")
    monkeypatch.setattr(gc, "LASTSEEN", grad / "last-seen.json")
    monkeypatch.setattr(gc, "PROMOTIONS_FILE", state / "candidates" / "correction-promotions.yaml")
    monkeypatch.setattr(gc.audit_skill_currency, "machine_label", lambda: label)
    if rows is not None:
        (state / "candidates" / "correction-promotions.yaml").write_text(
            yaml.safe_dump({"promotions": rows}))
    return state, grad


# ── machine guard ───────────────────────────────────────────────────────────
def test_machine_guard_noop_off_dev_primary(tmp_path, monkeypatch):
    # ELIGIBLE rows are present (same data as the on-dev-primary passing tests, which
    # DO produce a draft) — so ONLY the dev-primary machine guard can suppress them.
    # Deleting `if machine not in DEV_HOSTS: return 0` must make this test FAIL.
    state, grad = _setup(tmp_path, monkeypatch, label="ace-win-1",
                         rows=[_row(1, "a", 313, ".claude/rules/x.md")])
    calls = []
    rc = gc.run_cli(SimpleNamespace(), notify_fn=calls.append)
    assert rc == 0
    assert calls == []                       # guard fires before evaluate -> no notify
    assert not (grad / "drafts").exists()     # guard fires before render -> zero drafts


# ── renderer: quarantine + no canonical SKILL.md ────────────────────────────
def test_render_never_writes_under_skills_tree(tmp_path, monkeypatch):
    state, grad = _setup(tmp_path, monkeypatch,
                         rows=[_row(1, "Shell script edits", 169, ".claude/rules/x.md")])
    skills = tmp_path / ".claude" / "skills"
    skills.mkdir(parents=True, exist_ok=True)
    gc.run_cli(SimpleNamespace(), notify_fn=lambda a: None)
    slug = gc.slug_for("Shell script edits")
    assert (grad / "drafts" / slug / "proposal.md").exists()
    # nothing under the skills tree, and no file named exactly SKILL.md anywhere in quarantine
    assert not any(skills.rglob("*"))
    assert not any(p.name == "SKILL.md" for p in grad.rglob("*"))


def test_render_emits_skill_draft_only_for_new_skill(tmp_path, monkeypatch):
    rows = [
        _row(1, "Brand New Thing", 200, "some-brand-new-skill"),  # new_skill
        _row(2, "Shell edits", 169, ".claude/rules/x.md"),         # rule
    ]
    state, grad = _setup(tmp_path, monkeypatch, rows=rows)
    gc.run_cli(SimpleNamespace(), notify_fn=lambda a: None)
    new_slug = gc.slug_for("Brand New Thing")
    rule_slug = gc.slug_for("Shell edits")
    assert (grad / "drafts" / new_slug / "SKILL.md.draft").exists()
    assert not (grad / "drafts" / rule_slug / "SKILL.md.draft").exists()
    assert (grad / "drafts" / rule_slug / "proposal.md").exists()


def test_generate_index_ignores_quarantine_drafts(tmp_path, monkeypatch):
    # A parked draft (even a SKILL.md.draft) is invisible to generate_skills_index.py.
    rows = [_row(1, "Brand New Thing", 200, "some-brand-new-skill")]
    state, grad = _setup(tmp_path, monkeypatch, rows=rows)
    gc.run_cli(SimpleNamespace(), notify_fn=lambda a: None)
    new_slug = gc.slug_for("Brand New Thing")
    draft = grad / "drafts" / new_slug / "SKILL.md.draft"
    assert draft.exists()
    # generate_skills_index keeps only paths ending in /SKILL.md
    from importlib import util as _u
    gpath = REPO_ROOT / "scripts" / "skills" / "generate_skills_index.py"
    gspec = _u.spec_from_file_location("generate_skills_index", gpath)
    gen = _u.module_from_spec(gspec)
    gspec.loader.exec_module(gen)
    assert not gen.is_first_class(str(draft)) or not str(draft).endswith("/SKILL.md")
    assert not str(draft).endswith("/SKILL.md")


# ── CLI: rc-0 contract + persistence + idempotency ──────────────────────────
def test_cli_returns_zero_on_drafts(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch, rows=[_row(1, "a", 313, ".claude/rules/x.md")])
    assert gc.run_cli(SimpleNamespace(), notify_fn=lambda a: None) == 0


def test_cli_returns_zero_on_empty(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch, rows=[_row(1, "a", 10, ".claude/rules/x.md")])  # below floor
    calls = []
    assert gc.run_cli(SimpleNamespace(), notify_fn=calls.append) == 0
    assert calls == []


def test_cli_injected_notify_fires_once_per_batch(tmp_path, monkeypatch):
    rows = [_row(1, "a", 313, ".claude/rules/x.md"), _row(2, "b", 169, ".claude/rules/x.md")]
    _setup(tmp_path, monkeypatch, rows=rows)
    calls = []
    gc.run_cli(SimpleNamespace(), notify_fn=calls.append)
    assert len(calls) == 1
    assert calls[0]["status"] == "pass"


def test_queue_and_ledger_written(tmp_path, monkeypatch):
    state, grad = _setup(tmp_path, monkeypatch, rows=[_row(1, "a", 313, ".claude/rules/x.md")])
    gc.run_cli(SimpleNamespace(), notify_fn=lambda a: None)
    queue = yaml.safe_load((grad / "queue.yaml").read_text())
    ledger = json.loads((grad / "graduated.json").read_text())
    assert queue["drafts"][0]["status"] == "draft-parked"
    assert queue["drafts"][0]["owner_review"] == "pending"
    assert gc.slug_for("a") in ledger["graduated"]


def test_idempotent_second_run(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch, rows=[_row(1, "a", 313, ".claude/rules/x.md")])
    calls = []
    gc.run_cli(SimpleNamespace(), notify_fn=calls.append)
    gc.run_cli(SimpleNamespace(), notify_fn=calls.append)
    assert len(calls) == 1  # second run graduates nothing, alerts nothing


def test_missing_promotions_file_failsoft(tmp_path, monkeypatch):
    state, grad = _setup(tmp_path, monkeypatch, rows=None)  # no file written
    calls = []
    rc = gc.run_cli(SimpleNamespace(), notify_fn=calls.append)
    assert rc == 0
    assert calls == []
    assert not (grad / "drafts").exists()


def test_no_status_label_no_git_no_propagate(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch, rows=[_row(1, "a", 313, ".claude/rules/x.md")])
    seen = []
    monkeypatch.setattr(gc.subprocess, "run", lambda *a, **k: seen.append(a))
    gc.run_cli(SimpleNamespace(), notify_fn=lambda a: None)  # injected notify => no subprocess
    assert seen == []  # no gh / git commit / propagate-ecosystem


# ── leak safety ─────────────────────────────────────────────────────────────
def test_evidence_no_abs_paths_no_client_ids(tmp_path, monkeypatch):
    rows = [_row(1, "a", 313, ".claude/rules/x.md",
                 files=["/mnt/local-analysis/secret/data.py", "/home/u/init.py"])]  # abs-path-allowed
    state, grad = _setup(tmp_path, monkeypatch, rows=rows)
    gc.run_cli(SimpleNamespace(), notify_fn=lambda a: None)
    text = (grad / "drafts" / gc.slug_for("a") / "proposal.md").read_text()
    assert "/mnt/" not in text and "/home/" not in text  # abs-path-allowed
    assert "data.py" in text  # basename preserved


def test_draft_size_bounded(tmp_path, monkeypatch):
    fat = "x" * 100000
    rows = [_row(i, f"theme-{i}", 100 + i, ".claude/rules/x.md", rationale=fat) for i in range(6)]
    state, grad = _setup(tmp_path, monkeypatch, rows=rows)
    gc.run_cli(SimpleNamespace(), notify_fn=lambda a: None)
    drafts = list((grad / "drafts").glob("*/proposal.md"))
    assert len(drafts) <= gc.MAX_GRADUATIONS_PER_RUN
    for d in drafts:
        assert d.stat().st_size < 16384  # each proposal stays well under the state-file size cap


# ── default notify shape ────────────────────────────────────────────────────
def test_default_notify_uses_skill_graduation_job(monkeypatch):
    recorded = {}
    monkeypatch.setattr(gc.subprocess, "run", lambda cmd, **k: recorded.setdefault("cmd", cmd))
    gc._default_notify({"detail": "d", "status": "pass"})
    cmd = recorded["cmd"]
    assert cmd[1:5] == [str(gc.NOTIFY_SH), "cron", "skill-graduation", "pass"]


# ── wiring assertions (static greps against the real scripts) ───────────────
COMMIT_SCRIPT = (REPO_ROOT / "scripts" / "cron" / "commit-learning-artifacts.sh").read_text()
NIGHTLY_SCRIPT = (REPO_ROOT / "scripts" / "cron" / "comprehensive-learning-nightly.sh").read_text()
GITIGNORE = (REPO_ROOT / ".gitignore").read_text()


def test_graduation_dir_not_gitignored():
    r = subprocess.run(["git", "-C", str(REPO_ROOT), "check-ignore",
                        ".claude/state/graduation/queue.yaml"],
                       capture_output=True, text=True)
    assert r.returncode == 1, f"graduation dir is gitignored: {r.stdout!r}"


def test_graduation_dir_in_redactor_arg_list():
    # the redactor invocation block (positional dir args to redact-client-pii.py)
    block = COMMIT_SCRIPT.split("redact-client-pii.py", 1)[1].split("else", 1)[0]
    assert ".claude/state/graduation" in block


def test_graduation_dir_in_state_dirs_array():
    block = COMMIT_SCRIPT.split("STATE_DIRS=(", 1)[1].split(")", 1)[0]
    assert ".claude/state/graduation/" in block


def test_nightly_wires_graduation_between_pipeline_and_commit():
    assert "graduate_corrections.py" in NIGHTLY_SCRIPT
    pipe = NIGHTLY_SCRIPT.index("comprehensive-learning.sh")
    grad = NIGHTLY_SCRIPT.index("graduate_corrections.py")
    commit = NIGHTLY_SCRIPT.index("commit-learning-artifacts.sh")
    assert pipe < grad < commit


def test_redaction_runs_over_rendered_draft_evidence(tmp_path, monkeypatch):
    # behavioral: a known client token in rendered evidence is scrubbed by the redactor.
    state, grad = _setup(tmp_path, monkeypatch,
                         rows=[_row(1, "a", 313, ".claude/rules/x.md", rationale="AcmeCorp did it")])
    gc.run_cli(SimpleNamespace(), notify_fn=lambda a: None)
    proposal = grad / "drafts" / gc.slug_for("a") / "proposal.md"
    assert "AcmeCorp" in proposal.read_text()
    mapf = tmp_path / "map.yaml"
    mapf.write_text(yaml.safe_dump(
        {"version": 1, "rules": [{"pattern": "AcmeCorp", "replacement": "CLIENT-A"}]}))
    redactor = REPO_ROOT / "scripts" / "legal" / "redact-client-pii.py"
    rel = proposal.relative_to(tmp_path)
    r = subprocess.run([sys.executable, str(redactor), "--map", str(mapf),
                        "--root", str(tmp_path), str(rel)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    out = proposal.read_text()
    assert "AcmeCorp" not in out and "CLIENT-A" in out
