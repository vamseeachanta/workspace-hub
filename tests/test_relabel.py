#!/usr/bin/env python3
"""TDD tests for scripts/kanban/relabel.py — the #2878 label-first migration tool.

Hermes kanban places a card by the issue's `domain:` label (reconcile target_board),
and the */20 cron rebuilds card placement from labels — so the ONLY durable way to
move a card between sub-boards is to relabel its GitHub issue. This tool does that
SAFELY: dry-run by default, removes obsolete `domain:` labels, enforces exactly one
`domain:` per issue, assigns a domain when missing, idempotent no-op when already
correct, per-repo, with throttle/backoff on `--apply`.

The planning core (plan_relabel) is pure and fully covered here; the gh shell is
tested with a fake runner. Hermetic — no live gh, no live kanban.

Run: uv run --with ruamel.yaml pytest tests/test_relabel.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
RELABEL_PY = REPO_ROOT / "scripts" / "kanban" / "relabel.py"


def _import_relabel():
    spec = importlib.util.spec_from_file_location("kanban_relabel", RELABEL_PY)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["kanban_relabel"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def rl():
    return _import_relabel()


# ── pure planning core ───────────────────────────────────────────────────────

def test_assign_missing_domain(rl):
    plan = rl.plan_relabel(["enhancement", "priority:medium"], "solver-orcaflex")
    assert plan["add"] == ["domain:solver-orcaflex"]
    assert plan["remove"] == []


def test_replace_single_wrong_domain(rl):
    plan = rl.plan_relabel(["domain:solver", "enhancement"], "solver-orcaflex")
    assert plan["add"] == ["domain:solver-orcaflex"]
    assert plan["remove"] == ["domain:solver"]


def test_strip_extra_domains_keeping_target(rl):
    # target already present alongside stragglers -> remove only the stragglers.
    plan = rl.plan_relabel(["domain:hydro", "domain:hydro-diffraction", "x"],
                           "hydro-diffraction")
    assert plan["add"] == []
    assert plan["remove"] == ["domain:hydro"]


def test_replace_multiple_domains_none_target(rl):
    plan = rl.plan_relabel(["domain:hydro", "domain:subsea"], "hydro-diffraction")
    assert plan["add"] == ["domain:hydro-diffraction"]
    assert sorted(plan["remove"]) == ["domain:hydro", "domain:subsea"]


def test_idempotent_noop_when_already_correct(rl):
    plan = rl.plan_relabel(["domain:solver-orcaflex", "enhancement"], "solver-orcaflex")
    assert plan["add"] == []
    assert plan["remove"] == []
    assert rl.is_noop(plan) is True


def test_non_domain_labels_never_touched(rl):
    plan = rl.plan_relabel(["machine:dev-primary", "dispatch:ready", "domain:old"], "new")
    assert "machine:dev-primary" not in plan["remove"]
    assert "dispatch:ready" not in plan["remove"]
    assert plan["remove"] == ["domain:old"]


def test_one_domain_invariant_after_plan(rl):
    labels = ["domain:a", "domain:b", "domain:c", "keep"]
    plan = rl.plan_relabel(labels, "b")
    final = (set(labels) - set(plan["remove"])) | set(plan["add"])
    domains = [l for l in final if l.startswith("domain:")]
    assert domains == ["domain:b"], f"exactly one domain must remain: {domains}"


# ── domain validation ────────────────────────────────────────────────────────

@pytest.mark.parametrize("good", ["solver", "solver-orcaflex", "hydro-vessel-motions", "codes2"])
def test_validate_domain_accepts_slug(rl, good):
    assert rl.validate_domain(good) is True


@pytest.mark.parametrize("bad", ["", "Solver", "has space", "domain:solver", "a_b", "UPPER"])
def test_validate_domain_rejects_bad(rl, bad):
    assert rl.validate_domain(bad) is False


# ── gh shell (fake runner) ───────────────────────────────────────────────────

class FakeRunner:
    def __init__(self, results):
        self.results = list(results)  # list of (rc, stdout, stderr)
        self.calls = []

    def __call__(self, cmd, capture_output=True, text=True, check=False):
        self.calls.append(list(cmd))
        rc, out, err = self.results.pop(0) if self.results else (0, "", "")
        class R: pass
        r = R(); r.returncode, r.stdout, r.stderr = rc, out, err
        return r


def test_apply_builds_add_and_remove_flags(rl):
    runner = FakeRunner([(0, "", "")])
    plan = {"add": ["domain:solver-orcaflex"], "remove": ["domain:solver"]}
    ok = rl.apply_relabel("vamseeachanta/digitalmodel", 605, plan,
                          runner=runner, sleep=lambda s: None)
    assert ok is True
    cmd = " ".join(runner.calls[0])
    assert "gh issue edit 605" in cmd
    assert "--repo vamseeachanta/digitalmodel" in cmd
    assert "--add-label domain:solver-orcaflex" in cmd
    assert "--remove-label domain:solver" in cmd


def test_apply_noop_makes_no_gh_call(rl):
    runner = FakeRunner([])
    ok = rl.apply_relabel("r", 1, {"add": [], "remove": []},
                          runner=runner, sleep=lambda s: None)
    assert ok is True
    assert runner.calls == [], "no-op must not call gh"


def test_apply_backs_off_on_throttle_then_succeeds(rl):
    slept = []
    runner = FakeRunner([(1, "", "X was submitted too quickly"), (0, "", "")])
    ok = rl.apply_relabel("r", 7, {"add": ["domain:x"], "remove": []},
                          runner=runner, sleep=slept.append, max_retries=3)
    assert ok is True
    assert len(runner.calls) == 2, "must retry after throttle"
    assert slept, "must back off before retry"


def test_apply_gives_up_after_max_retries(rl):
    runner = FakeRunner([(1, "", "was submitted too quickly")] * 5)
    ok = rl.apply_relabel("r", 7, {"add": ["domain:x"], "remove": []},
                          runner=runner, sleep=lambda s: None, max_retries=3)
    assert ok is False
    assert len(runner.calls) == 3, "must stop at max_retries"


def test_apply_non_throttle_error_fails_fast(rl):
    runner = FakeRunner([(1, "", "could not find issue")])
    ok = rl.apply_relabel("r", 7, {"add": ["domain:x"], "remove": []},
                          runner=runner, sleep=lambda s: None, max_retries=3)
    assert ok is False
    assert len(runner.calls) == 1, "non-throttle error must not retry"


# ── remap loading + validation ───────────────────────────────────────────────

def test_load_remap_parses_repo_and_entries(rl, tmp_path):
    p = tmp_path / "remap.yaml"
    p.write_text(
        "repo: vamseeachanta/digitalmodel\n"
        "remap:\n"
        "  - issue: 605\n    domain: solver-orcaflex\n"
        "  - issue: 500\n    domain: solver-orcaflex\n",
        encoding="utf-8",
    )
    spec = rl.load_remap(p)
    assert spec["repo"] == "vamseeachanta/digitalmodel"
    assert spec["remap"][0] == {"issue": 605, "domain": "solver-orcaflex"}


def test_load_remap_rejects_bad_domain(rl, tmp_path):
    p = tmp_path / "remap.yaml"
    p.write_text(
        "repo: r\nremap:\n  - issue: 1\n    domain: Bad Domain\n", encoding="utf-8")
    with pytest.raises(Exception):
        rl.load_remap(p)


def test_load_remap_rejects_duplicate_issue(rl, tmp_path):
    # same issue twice with different domains = ambiguous; must reject.
    p = tmp_path / "remap.yaml"
    p.write_text(
        "repo: r\nremap:\n"
        "  - issue: 5\n    domain: a\n"
        "  - issue: 5\n    domain: b\n",
        encoding="utf-8",
    )
    with pytest.raises(Exception):
        rl.load_remap(p)


# ── adversarial-review regressions ───────────────────────────────────────────

def test_plan_relabel_rejects_invalid_target(rl):
    # E: the pure core must self-validate, not trust callers.
    for bad in ["", "domain:y", "Bad Domain", "UPPER"]:
        with pytest.raises(ValueError):
            rl.plan_relabel(["enhancement"], bad)


@pytest.mark.parametrize("body", [
    "repo: r\n",                                   # missing remap
    "repo: r\nremap: []\n",                        # empty list
    "repo: r\nremaps:\n  - issue: 1\n    domain: a\n",  # misspelled key
    "repo: r\nremap:\n  - just-a-string\n",        # non-mapping entry
])
def test_load_remap_fails_closed_on_empty_or_malformed(rl, tmp_path, body):
    # D: a reviewed batch must NOT silently no-op (esp. under --apply).
    p = tmp_path / "remap.yaml"
    p.write_text(body, encoding="utf-8")
    with pytest.raises(Exception):
        rl.load_remap(p)


@pytest.mark.parametrize("issue_yaml", ["true", "0", "-3"])
def test_load_remap_rejects_bool_zero_negative_issue(rl, tmp_path, issue_yaml):
    # F: bool is a subclass of int; 0/negatives are not real issues.
    p = tmp_path / "remap.yaml"
    p.write_text(f"repo: r\nremap:\n  - issue: {issue_yaml}\n    domain: a\n", encoding="utf-8")
    with pytest.raises(Exception):
        rl.load_remap(p)


def test_throttle_excludes_primary_rate_limit(rl):
    # G: primary hourly limit is NOT backoff-clearable -> must fail fast.
    runner = FakeRunner([(1, "", "API rate limit exceeded for user")])
    ok = rl.apply_relabel("r", 7, {"add": ["domain:x"], "remove": []},
                          runner=runner, sleep=lambda s: None, max_retries=3)
    assert ok is False
    assert len(runner.calls) == 1, "primary rate limit must not be retried"


def test_throttle_matches_abuse_detection(rl):
    # G: secondary/abuse limit IS retryable.
    runner = FakeRunner([(1, "", "You have triggered an abuse detection mechanism"),
                         (0, "", "")])
    ok = rl.apply_relabel("r", 7, {"add": ["domain:x"], "remove": []},
                          runner=runner, sleep=lambda s: None, max_retries=3)
    assert ok is True
    assert len(runner.calls) == 2
