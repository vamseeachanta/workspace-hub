"""Conservation examples for cron cutover.

Basis: crontab(5), DESCRIPTION, https://man7.org/linux/man-pages/man5/crontab.5.html
Comments/environment assignments are ignored by cron; command bodies are opaque.
Expected sets below are independently enumerated, not obtained from the planner.
"""
import importlib.util
import sys
from pathlib import Path

import pytest

CRON = Path(__file__).resolve().parents[2] / "scripts/cron"
sys.path.insert(0, str(CRON))
import cron_transaction as ct


def load_audit():
    spec = importlib.util.spec_from_file_location("conservation_audit", CRON / "cron-audit.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


OWNED = "0 1 * * * echo owned"
EXTERNAL = "0 2 * * * echo external"
UNKNOWN = "0 3 * * * first && second >> output.log 2>&1"
COMMENT = "# retain this explanation"
TASKS = [{"id": "owned", "schedule": "0 1 * * *", "command": "echo owned"}]
CONTEXT = {
    "line_identities": {OWNED: {"source": "canonical-exact-line", "catalog_task_id": "owned"}},
    "preservation_fingerprints": [{"fingerprint": {"command_contains": "echo external"}}],
}


def plan(text):
    return ct.plan_cutover(text, TASKS, ["worker"], [], [], ownership_context=CONTEXT)


def fixture(section, line):
    sections = {"before": [], "managed": [], "after": []}
    sections[section] = [line]
    return "\n".join([
        *sections["before"], ct.marker_begin(["worker"]),
        *sections["managed"], ct.MARKER_END, *sections["after"],
    ]) + "\n"


def test_managed_unknown_matches_audit_and_blocks():
    """Hand enumeration: one executable unknown, no owned/external commands."""
    text = fixture("managed", UNKNOWN)
    audit = load_audit().audit_crontab(
        text, [], [], ct.classify_line_detail, ownership_context=CONTEXT,
    )
    result = plan(text)
    assert audit["uncataloged"] == [UNKNOWN]
    assert result["abort_reason"]
    assert result["new_text"] is None
    assert result["uncataloged"] == audit["uncataloged"]
    assert result["counts"]["uncataloged"] == 1
    assert {row["line"] for row in result["line_classes"] if row["class"] == "uncataloged"} == {UNKNOWN}
    assert result["dropped"] == []


# Independent table: owned is replaced; external/comment/environment/blank survive;
# unknown blocks with no proposed output. Three sections exercise identical rules.
@pytest.mark.parametrize("section", ["before", "managed", "after"])
@pytest.mark.parametrize("line,classification,preserved,replaced,blocked", [
    (OWNED, "cataloged", [], [OWNED], []),
    (EXTERNAL, "preserved_external", [EXTERNAL], [], []),
    (UNKNOWN, "uncataloged", [], [], [UNKNOWN]),
    (COMMENT, "ignore", [COMMENT], [], []),
    ("SHELL=/bin/sh", "ignore", ["SHELL=/bin/sh"], [], []),
    ("", "ignore", [""], [], []),
])
def test_section_matrix(section, line, classification, preserved, replaced, blocked):
    result = plan(fixture(section, line))
    assert result["uncataloged"] == blocked
    assert result["preserved"] == preserved
    assert result["replaced"] == replaced
    assert result["line_classes"] == [{"section": section, "line": line, "class": classification}]
    if blocked:
        assert result["new_text"] is None
    else:
        assert line in result["new_text"].splitlines()
        assert result["dropped"] == []  # canonical owned line is rendered identically


def test_legacy_replacement_and_duplicate_loss_are_explicit():
    """Hand subtraction by occurrence: two old lines become one canonical line."""
    legacy = "0 4 * * * echo previous"
    context = {**CONTEXT, "line_identities": {
        **CONTEXT["line_identities"],
        legacy: {"source": "legacy-exact-line", "catalog_task_id": "owned"},
    }}
    result = ct.plan_cutover(
        fixture("managed", legacy + "\n" + legacy), TASKS, ["worker"], [], [],
        ownership_context=context,
    )
    assert result["replaced"] == [legacy, legacy]
    assert result["dropped"] == [legacy, legacy]
    assert result["new_text"].splitlines() == [ct.marker_begin(["worker"]), OWNED, ct.MARKER_END]


def test_unrecognized_classifier_result_fails_closed(monkeypatch):
    """An unsupported classification is one blocker, never deletion authority."""
    monkeypatch.setattr(ct, "classify_line_detail", lambda *a, **kw: {"class": "unknown"})
    result = plan(fixture("managed", UNKNOWN))
    assert result["new_text"] is None
    assert result["uncataloged"] == [UNKNOWN]
    assert result["counts"]["unknown"] == 1


@pytest.mark.parametrize("line,expected_status", [(UNKNOWN, "abort"), (OWNED, "dry-run")])
def test_apply_preview_exposes_classification(monkeypatch, line, expected_status):
    """Preview retains the pure plan diagnostics; no scheduler write is allowed."""
    spec = importlib.util.spec_from_file_location("conservation_apply", CRON / "cron_apply.py")
    apply = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(apply)
    selection = {"machine_id": "fixture", "roles": ["worker"],
                 "selected": TASKS, "selected_raw": TASKS,
                 "selected_task_ids": {"owned"}, "conflicts": []}
    monkeypatch.setattr(apply, "_load_cutover_context", lambda _: (selection, {}, CONTEXT))
    result = apply.run_cutover(
        "fixture", False, None, _read=lambda: fixture("managed", line),
        _write=lambda _: pytest.fail("preview attempted a write"),
    )
    assert result["status"] == expected_status
    assert result["line_classes"] == [{"section": "managed", "line": line,
                                      "class": "uncataloged" if line == UNKNOWN else "cataloged"}]
    assert result["counts"] == {"uncataloged" if line == UNKNOWN else "cataloged": 1}
    assert result["dropped"] == []


def test_duplicate_canonical_occurrence_is_reported():
    """Hand enumeration: two identical inputs minus one output leaves one drop."""
    result = plan(fixture("managed", OWNED + "\n" + OWNED))
    assert result["replaced"] == [OWNED, OWNED]
    assert result["dropped"] == [OWNED]
    assert result["new_text"].splitlines().count(OWNED) == 1
