"""Branch-aware promotion guards for issue #2227."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
HANDOFF_PATH = REPO_ROOT / "docs/reports/acma-wiki-unblock-2245-handoff.yaml"
OCIMF_SUMMARY_PATH = (
    REPO_ROOT
    / "data/document-index/summaries/"
    / "sha256:5e5f61e785295f0ac849399bb302cb5192ca84c108e6a57e82b8cc83b8b431af.json"
)
OCIMF_PAGE = REPO_ROOT / "knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md"
OCIMF_MEG4_PAGE = REPO_ROOT / "knowledge/wikis/engineering/wiki/standards/ocimf-meg4.md"
ENGINEERING_INDEX = REPO_ROOT / "knowledge/wikis/engineering/wiki/index.md"
ENGINEERING_LOG = REPO_ROOT / "knowledge/wikis/engineering/wiki/log.md"
OCIMF_DOC_KEY = "sha256:5e5f61e785295f0ac849399bb302cb5192ca84c108e6a57e82b8cc83b8b431af"


def _env_gate_value() -> bool | None:
    raw = os.environ.get("CONTENT_SUB_GATE_PASS")
    if raw is None:
        return None
    normalized = raw.strip().lower()
    if normalized in {"1", "true", "yes", "pass"}:
        return True
    if normalized in {"0", "false", "no", "fail"}:
        return False
    raise ValueError(f"Invalid CONTENT_SUB_GATE_PASS value: {raw!r}")


def evaluate_content_sub_gate(handoff: dict[str, Any], summary: dict[str, Any]) -> bool:
    """Return true only when the approved #2227 OCIMF content gate is satisfied."""
    if "ready_for_2227" not in handoff:
        raise AssertionError(f"{HANDOFF_PATH} is missing ready_for_2227")
    if "summary" not in summary or "text_preview" not in summary:
        raise AssertionError(f"{OCIMF_SUMMARY_PATH} is missing summary or text_preview")
    return (
        handoff["ready_for_2227"] is True
        and bool(str(summary["summary"]).strip())
        and bool(str(summary["text_preview"]).strip())
    )


def _load_live_gate_inputs() -> tuple[dict[str, Any], dict[str, Any]]:
    if not HANDOFF_PATH.exists() or not OCIMF_SUMMARY_PATH.exists():
        pytest.skip(
            "CONTENT_SUB_GATE artifacts unavailable; set CONTENT_SUB_GATE_PASS explicitly",
            allow_module_level=True,
        )
    handoff = yaml.safe_load(HANDOFF_PATH.read_text(encoding="utf-8"))
    summary = json.loads(OCIMF_SUMMARY_PATH.read_text(encoding="utf-8"))
    return handoff, summary


def content_sub_gate_pass() -> bool:
    env_value = _env_gate_value()
    if env_value is not None:
        return env_value
    handoff, summary = _load_live_gate_inputs()
    return evaluate_content_sub_gate(handoff, summary)


CONTENT_SUB_GATE_PASS = content_sub_gate_pass()
BRANCH_A_ONLY = pytest.mark.skipif(
    not CONTENT_SUB_GATE_PASS,
    reason="Branch B: wiki writes deliberately deferred while content gate fails",
)


def _git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.strip()


def _merge_base() -> str:
    return _git("merge-base", "origin/main", "HEAD")


def _page_body(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if text.startswith("---\n"):
        parts = text.split("---\n", 2)
        if len(parts) == 3:
            return parts[2]
    return text


def _frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    parts = text.split("---\n", 2)
    assert len(parts) == 3
    return yaml.safe_load(parts[1])


def test_prereq_content_sub_gate_evaluation() -> None:
    assert evaluate_content_sub_gate(
        {"ready_for_2227": True},
        {"summary": "usable source summary", "text_preview": "usable preview"},
    )
    assert not evaluate_content_sub_gate(
        {"ready_for_2227": False},
        {"summary": "usable source summary", "text_preview": "usable preview"},
    )
    assert not evaluate_content_sub_gate(
        {"ready_for_2227": True},
        {"summary": "", "text_preview": "usable preview"},
    )
    assert not evaluate_content_sub_gate(
        {"ready_for_2227": True},
        {"summary": "usable source summary", "text_preview": ""},
    )

    if HANDOFF_PATH.exists() and OCIMF_SUMMARY_PATH.exists():
        handoff, summary = _load_live_gate_inputs()
        assert content_sub_gate_pass() is evaluate_content_sub_gate(handoff, summary)
    elif _env_gate_value() is None:
        pytest.skip("live gate artifacts unavailable and CONTENT_SUB_GATE_PASS is unset")


def test_branch_b_no_wiki_writes_when_gate_fails() -> None:
    if CONTENT_SUB_GATE_PASS:
        pytest.skip("Branch A active")
    base = _merge_base()
    added = _git(
        "diff",
        "--name-only",
        "--diff-filter=A",
        f"{base}..HEAD",
        "--",
        "knowledge/wikis/engineering/wiki/standards/",
        "knowledge/wikis/marine-engineering/wiki/standards/",
    ).splitlines()
    assert added == []


@BRANCH_A_ONLY
def test_ocimf_tandem_page_exists() -> None:
    assert OCIMF_PAGE.exists()


@BRANCH_A_ONLY
def test_ocimf_tandem_frontmatter_valid() -> None:
    frontmatter = _frontmatter(OCIMF_PAGE)
    for key in (
        "title",
        "tags",
        "added",
        "last_updated",
        "sources",
        "domain",
        "code_id",
        "publisher",
        "revision",
    ):
        assert frontmatter.get(key)
    assert frontmatter["domain"] == "marine"
    assert frontmatter["code_id"] == "OCIMF-TANDEM-MOORING"


@BRANCH_A_ONLY
def test_ocimf_tandem_provenance_fields() -> None:
    text = OCIMF_PAGE.read_text(encoding="utf-8")
    assert f"doc_key: {OCIMF_DOC_KEY}" in text
    assert "source_ref" in text
    assert "promoted_from: 2227" in text


@BRANCH_A_ONLY
def test_ocimf_tandem_cross_reference_to_meg4() -> None:
    text = OCIMF_PAGE.read_text(encoding="utf-8")
    assert "[[ocimf-meg4]]" in text or "ocimf-meg4.md" in text


@BRANCH_A_ONLY
def test_ocimf_meg4_scope_narrow() -> None:
    base = _merge_base()
    diff = _git("diff", "--unified=0", base, "--", str(OCIMF_MEG4_PAGE.relative_to(REPO_ROOT)))
    added = [
        line[1:]
        for line in diff.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]
    removed = [
        line[1:]
        for line in diff.splitlines()
        if line.startswith("-") and not line.startswith("---")
    ]
    assert len(added) <= 10
    assert removed == []
    assert added.count("## Related Standards") <= 1
    for line in added:
        if line == "## Related Standards":
            continue
        assert "OCIMF-TANDEM-MOORING" in line or "[[ocimf-tandem-mooring]]" in line


@BRANCH_A_ONLY
def test_engineering_index_has_tandem_row() -> None:
    text = ENGINEERING_INDEX.read_text(encoding="utf-8")
    standards = re.search(r"## Standards \(8 pages\)(.*?)(?:\n## |\Z)", text, re.S)
    assert standards
    assert "ocimf-tandem-mooring.md" in standards.group(1)


@BRANCH_A_ONLY
def test_engineering_log_has_promotion_entry() -> None:
    text = ENGINEERING_LOG.read_text(encoding="utf-8")
    assert re.search(r"## \[\d{4}-\d{2}-\d{2}\] ingest \| OCIMF-TANDEM-MOORING promotion \(#2227\)", text)


@BRANCH_A_ONLY
def test_no_out_of_scope_pages() -> None:
    base = _merge_base()
    added = set(_git("diff", "--name-only", "--diff-filter=A", f"{base}..HEAD").splitlines())
    standard_pages = {
        path
        for path in added
        if "/wiki/standards/" in path and path.startswith("knowledge/wikis/")
    }
    assert standard_pages == {"knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md"}


@BRANCH_A_ONLY
def test_llm_wiki_lint_engineering_clean() -> None:
    result = subprocess.run(
        ["uv", "run", "scripts/knowledge/llm_wiki.py", "lint", "--wiki", "engineering"],
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@BRANCH_A_ONLY
def test_content_has_discriminating_technical_evidence() -> None:
    body = _page_body(OCIMF_PAGE)
    words = re.findall(r"\b[\w'-]+\b", body)
    assert len(words) > 200
    categories = [
        re.search(r"\b[0-9]+(?:\.[0-9]+){1,3}\b", body),
        re.search(r"\b\d+(?:\.\d+)?\s*(?:kN|t|m|ft|deg|kts|knots|MT|bar|kPa|MPa)\b", body),
        re.search(
            r"\b(?:12-point spread|submarine hoses|Yokohama fender|quick-release hook|chafe chain)\b",
            body,
            re.I,
        ),
    ]
    assert sum(match is not None for match in categories) >= 2


@BRANCH_A_ONLY
def test_ocimf_tandem_has_inbound_link() -> None:
    link_patterns = (
        "[[ocimf-tandem-mooring]]",
        "](standards/ocimf-tandem-mooring.md)",
        "](/knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md)",
    )
    pages = [
        path
        for path in (REPO_ROOT / "knowledge/wikis/engineering/wiki").rglob("*.md")
        if path != OCIMF_PAGE
    ]
    assert any(
        any(pattern in page.read_text(encoding="utf-8") for pattern in link_patterns)
        for page in pages
    )
