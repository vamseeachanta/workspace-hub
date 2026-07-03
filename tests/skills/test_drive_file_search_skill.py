"""Tests for drive-file-search skill (#3338, epic #3333).

Validates (per docs/plans/2026-07-02-issue-3338-drive-file-search-skill.md):
- SKILL.md frontmatter contract (name, category, type, related_skills, triggers)
- Trigger disjointness vs ecosystem-data-sources (FILE-level vs DATA-level routing)
- Body contract anchors (the one CLI command, --json, exit-2 branch, coverage_gaps,
  canonical-drive-links.sh, de-identification + read-only guardrails)
- Size within the audit-word-count.py thresholds (<=200 lines AND <=500 words)
- Domain map consumed (literal path present), not copied (map keywords absent)
- Mock envelope conforms to the #3335 CLI --json schema
- Post-#3335 scripted smoke against the fixture registry (skip-guarded)
- Hook<->skill trigger alignment with #3339 (skip-guarded until its map lands)
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_DIR = REPO_ROOT / ".claude" / "skills" / "data" / "drive-file-search"
SKILL_MD = SKILL_DIR / "SKILL.md"
CONTEXT_DOC = SKILL_DIR / "references" / "context-extraction.md"
MOCK_ENVELOPE = SKILL_DIR / "references" / "mock-envelope.json"
ECOSYSTEM_SKILL = (
    REPO_ROOT / ".claude" / "skills" / "data" / "ecosystem-data-sources" / "SKILL.md"
)
CLI = REPO_ROOT / "scripts" / "data" / "drive-index-search" / "search.py"
FIXTURE_REGISTRY = (
    REPO_ROOT / "tests" / "data" / "drive_index_search" / "fixtures" / "test-registry.yml"
)
HOOK_MAP = REPO_ROOT / ".claude" / "hooks" / "drive-file-map.json"  # lands with #3339

# Audit thresholds from scripts/skills/audit-word-count.py::classify
# (>200 lines -> WARNING, >500 words -> OVER_BUDGET); pinned per plan review F1.
MAX_LINES = 200
MAX_WORDS = 500

# Single source of truth for the #3335 --json envelope schema
# (scripts/data/drive-index-search/search.py::_emit + adapters/base.py::as_dict).
ENVELOPE_TOP_KEYS = {"query", "generated_at", "indexes_queried", "index_status", "coverage_gaps", "results"}
RESULT_KEYS = {"canonical_path", "raw_path", "source_index", "adapter", "score", "rank_basis", "meta"}
GAP_KEYS = {"id", "path", "reason"}

CANONICAL_TRIGGERS = ["similar past work", "search the drives", "prior project"]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _split(path: Path) -> tuple[dict, str]:
    """Return (frontmatter mapping, body text) of a SKILL.md."""
    text = _read(path)
    parts = text.split("---", maxsplit=2)
    assert len(parts) >= 3, f"{path}: frontmatter not properly delimited"
    data = yaml.safe_load(parts[1])
    assert isinstance(data, dict), f"{path}: frontmatter must be a YAML mapping"
    return data, parts[2]


def _assert_envelope_schema(envelope: dict, require_mnt_paths: bool) -> None:
    """Shared schema assertions for the mock fixture AND the live-CLI smoke."""
    assert set(envelope.keys()) == ENVELOPE_TOP_KEYS, (
        f"envelope top-level keys {sorted(envelope)} != {sorted(ENVELOPE_TOP_KEYS)}"
    )
    assert isinstance(envelope["query"], str)
    assert isinstance(envelope["generated_at"], str)
    assert isinstance(envelope["indexes_queried"], list)
    for gap in envelope["coverage_gaps"]:
        assert set(gap.keys()) == GAP_KEYS, f"gap keys {sorted(gap)} != {sorted(GAP_KEYS)}"
        # reason is OPAQUE FREE TEXT (no enum in #3335) — assert type only, never value
        assert isinstance(gap["reason"], str) and gap["reason"].strip()
    for result in envelope["results"]:
        assert set(result.keys()) == RESULT_KEYS, (
            f"result keys {sorted(result)} != {sorted(RESULT_KEYS)}"
        )
        assert isinstance(result["score"], (int, float))
        assert isinstance(result["meta"], dict)
        if require_mnt_paths:
            assert result["canonical_path"].startswith("/mnt/"), result["canonical_path"]
            assert not result["canonical_path"].startswith("/mnt/remote/"), (
                f"canonical_path must not use the /mnt/remote alias: {result['canonical_path']}"
            )


class TestSkillStructure:
    def test_skill_file_exists(self):
        assert SKILL_MD.is_file(), f"Missing {SKILL_MD}"

    def test_reference_files_exist(self):
        assert CONTEXT_DOC.is_file(), f"Missing {CONTEXT_DOC}"
        assert MOCK_ENVELOPE.is_file(), f"Missing {MOCK_ENVELOPE}"

    def test_frontmatter_contract(self):
        data, _ = _split(SKILL_MD)
        assert data["name"] == "drive-file-search"
        assert isinstance(data["description"], str) and data["description"].strip()
        assert data["category"] == "data"
        assert data["type"] == "reference"
        assert data["freedom"] == "high"
        assert "ecosystem-data-sources" in data["related_skills"]
        triggers = [t.lower() for t in data["triggers"]]
        for phrase in CANONICAL_TRIGGERS:
            assert phrase in triggers, f"missing canonical trigger: {phrase!r}"
        assert any(t.startswith("do we have") and t.endswith("for") for t in triggers), (
            "missing a 'do we have ... for' trigger phrasing"
        )

    def test_skill_size_within_audit_limits(self):
        text = _read(SKILL_MD)
        lines = len(text.splitlines())
        words = len(text.split())
        assert lines <= MAX_LINES, f"SKILL.md is {lines} lines (audit WARNING > {MAX_LINES})"
        assert words <= MAX_WORDS, f"SKILL.md is {words} words (audit OVER_BUDGET > {MAX_WORDS})"


class TestTriggerRouting:
    def test_triggers_disjoint_from_ecosystem_data_sources(self):
        data, _ = _split(SKILL_MD)
        eco, _ = _split(ECOSYSTEM_SKILL)
        mine = {t.lower().strip() for t in data["triggers"]}
        theirs = {t.lower().strip() for t in eco["triggers"]}
        overlap = mine & theirs
        assert not overlap, f"FILE-level vs DATA-level triggers must be disjoint: {overlap}"

    @pytest.mark.skipif(
        not HOOK_MAP.exists(), reason="#3339 drive-file-map.json not landed yet"
    )
    def test_hook_skill_trigger_alignment(self):
        """Every canonical skill trigger fires the #3339 hook matcher; DATA-level
        phrasings route to neither this FILE-level skill nor the hook."""
        data, _ = _split(SKILL_MD)
        hook_text = _read(HOOK_MAP).lower()
        for phrase in CANONICAL_TRIGGERS:
            assert phrase in hook_text, f"hook map missing canonical trigger: {phrase!r}"
        triggers = {t.lower().strip() for t in data["triggers"]}
        assert "do we have data for" not in triggers, "DATA-level phrasing leaked into skill"
        assert "do we have data for" not in hook_text, "DATA-level phrasing leaked into hook"


class TestBodyContract:
    def test_body_contains_contract_anchors(self):
        _, body = _split(SKILL_MD)
        for anchor in (
            "scripts/data/drive-index-search/search.py",
            "--json",
            "coverage_gaps",
            "canonical-drive-links.sh",
        ):
            assert anchor in body, f"SKILL.md body missing anchor: {anchor!r}"
        assert "`2`" in body and "exit code" in body.lower(), (
            "SKILL.md body must document the exit-2 branch"
        )
        lower = body.lower()
        assert "de-identification" in lower, "missing De-identification guardrail"
        assert "read-only" in lower, "missing read-only guardrail"

    def test_domain_map_consumed_not_copied(self):
        _, body = _split(SKILL_MD)
        assert "ecosystem-domain-map.json" in body, (
            "SKILL.md must reference the generated domain map by its literal path"
        )
        text = _read(SKILL_MD).lower()
        for keyword in ("station-keeping", "catenary"):
            assert keyword not in text, (
                f"map keyword {keyword!r} hand-copied into SKILL.md — read the map live instead"
            )


class TestMockEnvelope:
    def test_mock_envelope_schema(self):
        envelope = json.loads(_read(MOCK_ENVELOPE))
        _assert_envelope_schema(envelope, require_mnt_paths=True)
        results = envelope["results"]
        assert len(results) >= 5, "mock must carry at least 5 results"
        assert len({r["source_index"] for r in results}) >= 2, "need >= 2 source indexes"
        bases = {r["rank_basis"] for r in results}
        assert {"fts_bm25", "token_match"} <= bases, f"need mixed rank_basis, got {bases}"
        gaps = envelope["coverage_gaps"]
        assert any("dde" in gap["id"] for gap in gaps), "need a dde coverage_gaps entry"

    def test_walkthrough_uses_mock_envelope(self):
        text = _read(CONTEXT_DOC)
        assert "mock-envelope.json" in text
        assert "scripts/data/drive-index-search/search.py" in text


@pytest.mark.skipif(not CLI.exists(), reason="#3335 CLI not merged yet")
class TestScriptedSmoke:
    """Post-#3335 smoke — runs the REAL merged CLI against its own fixtures only."""

    def test_scripted_smoke_fixture_registry(self):
        proc = subprocess.run(
            [
                sys.executable,
                str(CLI),
                "riser",
                "--registry",
                str(FIXTURE_REGISTRY),
                "--json",
                "--limit",
                "5",
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=120,
        )
        assert proc.returncode == 0, f"exit {proc.returncode}: {proc.stderr}"
        envelope = json.loads(proc.stdout)
        _assert_envelope_schema(envelope, require_mnt_paths=False)
        assert envelope["query"] == "riser"
        assert envelope["results"], "fixture registry should yield results for 'riser'"

    def test_scripted_smoke_exit2_branch(self):
        proc = subprocess.run(
            [
                sys.executable,
                str(CLI),
                "riser",
                "--registry",
                str(REPO_ROOT / "tests" / "data" / "no-such-registry.yml"),
                "--json",
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=120,
        )
        assert proc.returncode == 2, (
            f"registry error must exit 2 (got {proc.returncode}): {proc.stderr}"
        )
