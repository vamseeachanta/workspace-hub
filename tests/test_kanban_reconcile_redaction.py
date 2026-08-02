#!/usr/bin/env python3
"""Client-identifier redaction at kanban board write time (workspace-hub#3768).

`scripts/kanban/reconcile.py` embeds the raw GitHub issue `title` (and carries
forward whatever free text an existing card holds) into
`.claude/memory/kanban/boards/*.yaml`, and the `*/20` cron pushes those files
straight to `main` in a PUBLIC repo. Ten board files were measured carrying
client identifiers.

These tests pin the WRITER's behaviour, not a specific redaction string:

  * every string the writer emits (any field, any depth, plus the rendered
    diff) is free of client identifiers -- field-agnostic, so a field added
    later is covered without touching this contract;
  * a write without a usable client map RAISES and leaves the files untouched
    (fail closed -- a stale board is recoverable, a public leak is not);
  * redaction reaches a FIXPOINT, so the 20-minute cron cannot churn.

Hermetic: the client map is SYNTHETIC and lives in tmp_path. No real client
identifier appears in this file, and no network/gh call is made.

Run: uv run --with pyyaml --with pytest pytest tests/test_kanban_reconcile_redaction.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts/kanban/reconcile.py"
ENGINE_PATH = ROOT / "scripts/legal/redact-client-pii.py"

REPO = "vamseeachanta/workspace-hub"

# Synthetic stand-ins for a client name. Deliberately nonsense words: this file
# is committed to a PUBLIC repo, so it must never carry a real identifier.
FAKE_CLIENT = "Quibblesnort"
FAKE_CLIENT_LONG = "Quibblesnort Marine Holdings"
FAKE_CODENAME = "client-q"


def load_reconcile():
    spec = importlib.util.spec_from_file_location("kanban_reconcile", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_engine():
    spec = importlib.util.spec_from_file_location("redact_client_pii_probe", ENGINE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def read_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def write_client_map(tmp_path: Path) -> Path:
    """A synthetic private map in the real map's schema (longest pattern first)."""
    path = tmp_path / "synthetic-client-map.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "version": 1,
                "rules": [
                    {
                        "pattern": FAKE_CLIENT_LONG,
                        "replacement": FAKE_CODENAME,
                        "word_bound": False,
                    },
                    {
                        "pattern": FAKE_CLIENT,
                        "replacement": FAKE_CODENAME,
                        "word_bound": True,
                    },
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return path


def seed_kanban(root: Path) -> Path:
    kanban = root / ".claude/memory/kanban"
    write_yaml(
        kanban / "manifest.yaml",
        {
            "manifest": {
                "boards": [
                    {
                        "slug": "repo-workspace-hub",
                        "tier": "repo",
                        "repo": REPO,
                        "file": "boards/repo-workspace-hub.yaml",
                    }
                ]
            }
        },
    )
    write_yaml(
        kanban / "boards/repo-workspace-hub.yaml",
        {
            "board": {"slug": "repo-workspace-hub", "tier": "repo", "repo": REPO},
            "cards": [],
        },
    )
    return kanban


def issue(number: int, title: str, labels: list[str] | None = None) -> dict:
    return {
        "number": number,
        "title": title,
        "state": "OPEN",
        "labels": [{"name": name} for name in (labels or [])],
    }


def board_path(kanban: Path) -> Path:
    return kanban / "boards/repo-workspace-hub.yaml"


def assert_no_identifier(text: str, engine, rules, label: str) -> None:
    """PROPERTY: running the redaction engine over `text` changes nothing.

    This is exactly `scripts/legal/check-client-pii.py`'s definition of a
    violation, so it cannot drift from the gate. It asserts a property of the
    output rather than an expected literal, so removing the guard cannot leave
    it passing.
    """
    _, hits = engine.redact_text(text, rules)
    assert hits == 0, f"{label} still contains {hits} client identifier match(es)"


# --------------------------------------------------------------------------
# Negative control
# --------------------------------------------------------------------------


def test_the_cleanliness_assertion_actually_fires(tmp_path: Path):
    """Negative control for every `assert_no_identifier` call below.

    The rest of this file is a wall of assert-clean. If the synthetic map ever
    stopped producing rules -- a schema change, a typo, an engine that returns
    zero matches -- all of those assertions would pass while measuring nothing
    (`.claude/rules/guards-must-discriminate.md` §3).
    """
    engine = load_engine()
    rules = engine.load_rules(write_client_map(tmp_path))
    assert rules, "synthetic map must produce a non-empty rule set"
    for dirty in (
        f"card title mentioning {FAKE_CLIENT}",
        f"escalated by {FAKE_CLIENT_LONG}",
        # word_bound blocks LETTER-flanking only, so digits/underscores still match
        f"{FAKE_CLIENT}_vessels and {FAKE_CLIENT}7000",
    ):
        with pytest.raises(AssertionError):
            assert_no_identifier(dirty, engine, rules, "negative control")


# --------------------------------------------------------------------------
# Redactor engine wiring
# --------------------------------------------------------------------------


def test_load_redactor_returns_none_when_map_is_absent(tmp_path: Path):
    reconcile = load_reconcile()
    assert reconcile.load_redactor(tmp_path / "nope.yaml") is None


def test_load_redactor_raises_when_map_exists_but_has_no_rules(tmp_path: Path):
    reconcile = load_reconcile()
    empty = tmp_path / "empty-map.yaml"
    empty.write_text(yaml.safe_dump({"version": 1, "rules": []}), encoding="utf-8")
    # A map that parses to zero rules must NOT be treated as "nothing to redact":
    # that writes raw titles while looking redacted.
    with pytest.raises(reconcile.RedactionUnavailable):
        reconcile.load_redactor(empty)


def test_redactor_rejects_a_map_that_matches_its_own_placeholder(tmp_path: Path):
    reconcile = load_reconcile()
    engine = load_engine()
    bad = tmp_path / "placeholder-colliding-map.yaml"
    token = reconcile.REDACTION_PLACEHOLDER.strip("[]").split()[0]
    bad.write_text(
        yaml.safe_dump(
            {"version": 1, "rules": [{"pattern": token, "replacement": FAKE_CODENAME}]}
        ),
        encoding="utf-8",
    )
    rules = engine.load_rules(bad)
    # The placeholder is the last-resort output; if the map matched it, the
    # fallback would itself be a violation and would never converge.
    with pytest.raises(reconcile.RedactionUnavailable):
        reconcile.Redactor(rules)


# --------------------------------------------------------------------------
# Idempotence / fixpoint
# --------------------------------------------------------------------------


def test_redactor_text_reaches_a_fixpoint_when_one_pass_is_not_enough(tmp_path: Path):
    reconcile = load_reconcile()
    engine = load_engine()
    # Rule order makes a single pass insufficient: 'alpha' -> 'beta' fires after
    # the 'beta' rule has already been evaluated, so pass 1 leaves a live match.
    path = tmp_path / "two-pass-map.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "version": 1,
                "rules": [
                    {"pattern": "betazzz", "replacement": "gammazzz"},
                    {"pattern": "alphazzz", "replacement": "betazzz"},
                ],
            }
        ),
        encoding="utf-8",
    )
    rules = engine.load_rules(path)
    redactor = reconcile.Redactor(rules)

    once, hits = engine.redact_text("alphazzz", rules)
    assert (once, hits) == ("betazzz", 1), "single pass must be insufficient for this map"

    out = redactor.text("alphazzz")
    assert_no_identifier(out, engine, rules, "fixpoint output")
    assert redactor.text(out) == out, "redaction must be idempotent"
    # A fixpoint EXISTS here, so it must be reached — degrading to the
    # placeholder would be clean and stable but would needlessly destroy a
    # readable title, which is the whole point of redacting rather than omitting.
    assert out != redactor.placeholder
    assert out == "gammazzz"


def test_redactor_falls_back_to_a_clean_stable_placeholder_when_it_cannot_converge(
    tmp_path: Path,
):
    reconcile = load_reconcile()
    engine = load_engine()
    # Self-feeding rule: every pass re-creates a match, so no fixpoint exists.
    path = tmp_path / "divergent-map.yaml"
    path.write_text(
        yaml.safe_dump(
            {"version": 1, "rules": [{"pattern": "loopzzz", "replacement": "xloopzzz"}]}
        ),
        encoding="utf-8",
    )
    rules = engine.load_rules(path)
    redactor = reconcile.Redactor(rules)

    out = redactor.text("loopzzz")
    # PROPERTY, not literal: the output is clean AND stable. Returning the
    # partially-substituted text would leak; returning a run-varying value would
    # make the */20 cron diff forever.
    assert_no_identifier(out, engine, rules, "non-convergent output")
    assert redactor.text(out) == out
    assert redactor.text("loopzzz") == out


# --------------------------------------------------------------------------
# Fail-closed on write
# --------------------------------------------------------------------------


def test_write_without_a_client_map_raises_and_touches_no_file(tmp_path: Path):
    reconcile = load_reconcile()
    kanban = seed_kanban(tmp_path)
    before = board_path(kanban).read_bytes()

    def fetcher(repo):  # pragma: no cover - must never run
        raise AssertionError("issues must not be fetched when redaction is unavailable")

    with pytest.raises(reconcile.RedactionUnavailable):
        reconcile.reconcile_kanban(
            kanban, issue_fetcher=fetcher, dry_run=False, redactor=None
        )
    assert board_path(kanban).read_bytes() == before


def test_dry_run_without_a_client_map_is_allowed_and_reports_the_gap(tmp_path: Path):
    reconcile = load_reconcile()
    kanban = seed_kanban(tmp_path)
    before = board_path(kanban).read_bytes()

    result = reconcile.reconcile_kanban(
        kanban,
        issue_fetcher=lambda repo: [issue(1, "plain title")],
        dry_run=True,
        redactor=None,
    )
    # The choice must be visible in the output, never silent.
    assert "not applied" in result.redaction.lower()
    assert board_path(kanban).read_bytes() == before


def test_redaction_status_is_reported_when_applied(tmp_path: Path):
    reconcile = load_reconcile()
    kanban = seed_kanban(tmp_path)
    redactor = reconcile.load_redactor(write_client_map(tmp_path))

    result = reconcile.reconcile_kanban(
        kanban,
        issue_fetcher=lambda repo: [issue(1, f"{FAKE_CLIENT} riser fatigue")],
        dry_run=False,
        redactor=redactor,
    )
    assert "applied" in result.redaction.lower()
    assert "not applied" not in result.redaction.lower()


# --------------------------------------------------------------------------
# What actually gets redacted
# --------------------------------------------------------------------------


def test_every_emitted_string_is_free_of_client_identifiers(tmp_path: Path):
    """Field-agnostic: title, carried-forward free text, assignees, labels, and
    board metadata all land clean, and so does the printed diff."""
    reconcile = load_reconcile()
    engine = load_engine()
    map_path = write_client_map(tmp_path)
    rules = engine.load_rules(map_path)
    kanban = seed_kanban(tmp_path)

    data = read_yaml(board_path(kanban))
    data["board"]["description"] = f"Board for {FAKE_CLIENT_LONG}"
    data["cards"] = [
        {
            "idempotency_key": f"gh:{REPO}#1",
            "title": "stale",
            "source": "github_issue",
            "source_url": f"https://github.com/{REPO}/issues/1",
            "gh_state": "open",
            "gh_labels": [],
            "gh_assignees": [f"{FAKE_CLIENT} Ops Lead"],
            "body_excerpt": f"Escalated by {FAKE_CLIENT_LONG} on Tuesday.",
            "initial_status": "triage",
            "priority": 0,
            "notes": {"nested": [f"deep {FAKE_CLIENT} reference"]},
        }
    ]
    write_yaml(board_path(kanban), data)

    result = reconcile.reconcile_kanban(
        kanban,
        issue_fetcher=lambda repo: [
            issue(1, f"{FAKE_CLIENT} mooring study", labels=[f"client:{FAKE_CLIENT}"])
        ],
        dry_run=False,
        redactor=reconcile.load_redactor(map_path),
    )

    text = board_path(kanban).read_text(encoding="utf-8")
    assert_no_identifier(text, engine, rules, "written board")
    # The diff is printed to stdout by the cron; it must not leak either.
    assert_no_identifier(result.diff, engine, rules, "rendered diff")

    card = read_yaml(board_path(kanban))["cards"][0]
    # Redacted, not omitted: the card is still readable and still identifiable.
    assert card["title"], "title must survive redaction, not be dropped"
    assert card["idempotency_key"] == f"gh:{REPO}#1"
    assert card["source_url"] == f"https://github.com/{REPO}/issues/1"
    assert "mooring study" in card["title"]
    assert "Escalated by" in card["body_excerpt"]


def test_a_board_needing_only_redaction_is_still_rewritten(tmp_path: Path):
    """The 10 flagged boards must clean up even on a run with no issue churn --
    so redaction has to happen BEFORE the changed/unchanged comparison."""
    reconcile = load_reconcile()
    engine = load_engine()
    map_path = write_client_map(tmp_path)
    rules = engine.load_rules(map_path)
    kanban = seed_kanban(tmp_path)

    data = read_yaml(board_path(kanban))
    data["board"]["description"] = f"Board for {FAKE_CLIENT_LONG}"
    data["cards"] = [
        {
            "idempotency_key": f"gh:{REPO}#1",
            "title": "already current",
            "source": "github_issue",
            "source_url": f"https://github.com/{REPO}/issues/1",
            "gh_state": "open",
            "gh_labels": [],
            "gh_assignees": [],
            "body_excerpt": "",
            "initial_status": "triage",
            "priority": 0,
        }
    ]
    write_yaml(board_path(kanban), data)

    result = reconcile.reconcile_kanban(
        kanban,
        issue_fetcher=lambda repo: [issue(1, "already current")],
        dry_run=False,
        redactor=reconcile.load_redactor(map_path),
    )
    assert result.changed is True
    assert_no_identifier(
        board_path(kanban).read_text(encoding="utf-8"), engine, rules, "written board"
    )


def test_redacted_board_is_byte_stable_across_repeated_runs(tmp_path: Path):
    """The cron rewrites every 20 minutes; a re-redaction that shifts the text
    would turn ~300 commits into thousands."""
    reconcile = load_reconcile()
    map_path = write_client_map(tmp_path)
    kanban = seed_kanban(tmp_path)

    def run():
        return reconcile.reconcile_kanban(
            kanban,
            issue_fetcher=lambda repo: [
                issue(1, f"{FAKE_CLIENT_LONG} / {FAKE_CLIENT} tie-back")
            ],
            dry_run=False,
            redactor=reconcile.load_redactor(map_path),
        )

    run()
    first = board_path(kanban).read_bytes()
    second = run()
    assert second.changed is False
    assert second.diff == ""
    assert board_path(kanban).read_bytes() == first


def test_redaction_preserves_yaml_comments_on_untouched_lines(tmp_path: Path):
    """Redaction mutates the round-trip tree in place; it must not flatten the
    board and drop the human-authored comments the existing suite protects."""
    reconcile = load_reconcile()
    engine = load_engine()
    map_path = write_client_map(tmp_path)
    rules = engine.load_rules(map_path)
    kanban = seed_kanban(tmp_path)
    board_path(kanban).write_text(
        "# board header comment\n"
        "board:\n"
        "  slug: repo-workspace-hub\n"
        "  tier: repo\n"
        f"  repo: {REPO}\n"
        f"  description: owned by {FAKE_CLIENT_LONG}\n"
        "cards: []\n",
        encoding="utf-8",
    )

    reconcile.reconcile_kanban(
        kanban,
        issue_fetcher=lambda repo: [issue(1, "plain title")],
        dry_run=False,
        redactor=reconcile.load_redactor(map_path),
    )
    text = board_path(kanban).read_text(encoding="utf-8")
    assert "# board header comment" in text
    assert_no_identifier(text, engine, rules, "written board")


# --------------------------------------------------------------------------
# CLI surface
# --------------------------------------------------------------------------


def test_cli_exits_nonzero_without_writing_when_the_map_is_missing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    reconcile = load_reconcile()
    kanban = seed_kanban(tmp_path)
    before = board_path(kanban).read_bytes()

    rc = reconcile.main(
        [
            "--kanban-root",
            str(kanban),
            "--client-map",
            str(tmp_path / "absent.yaml"),
        ]
    )
    assert rc != 0
    err = capsys.readouterr().err
    assert "client" in err.lower() and "map" in err.lower()
    assert board_path(kanban).read_bytes() == before


def test_cli_no_redact_is_preview_only(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    reconcile = load_reconcile()
    kanban = seed_kanban(tmp_path)
    before = board_path(kanban).read_bytes()

    rc = reconcile.main(["--kanban-root", str(kanban), "--no-redact"])
    assert rc != 0, "--no-redact must never be usable on a writing run"
    assert board_path(kanban).read_bytes() == before
    # Rejected by the CLI on the flag combination itself, not merely caught
    # downstream by the library's fail-closed write guard — so the flag can
    # never reach a code path that writes.
    err = capsys.readouterr().err
    assert "preview-only" in err
    assert "--dry-run" in err
