"""Synthetic handoff examples; expectations are hand-authored, not generated.

Heading vocabulary and status: docs/plans/
2026-04-27-issue-2374-transient-promotion-candidate-queue.md,
``extract_handoff_findings.py`` design. Issue numbers below are fixture labels.
"""

import hashlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from extract_handoff_findings import extract_handoff_findings


SOURCE = "docs/handoffs/example.md"


def expected(text, summary, issue=None, evidence="missing"):
    """Only the standard-library digest is computed; record fields are literal."""
    return {
        "source_path": SOURCE,
        "source_kind": "handoff",
        "source_sha": "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "issue_ref": issue,
        "issue_ref_status": evidence,
        "finding_summary": summary,
        "status": "candidate",
    }


@pytest.mark.parametrize("heading", [
    "Locked Decisions (for future sessions)",
    "Two Painful Pattern Discoveries (Useful for Next Session)",
    "Open Items (blocking next-session work)",
    "Session outcome", "What was completed", "Key technical lessons",
])
def test_handoff_heading_shapes_extract_findings(heading):
    text = f"# Handoff\n## {heading}\n- Retain evidence for #123.\n"
    assert extract_handoff_findings(text, SOURCE) == [
        expected(text, "Retain evidence for #123.", "123", "present")
    ]


def test_handoff_multiline_bullets_preserve_text():
    text = (
        "## Findings\n- Keep the original text.\n"
        "  Continue with café and `code` for #123.\n"
        "  - Nested evidence stays attached.\n\n"
        "* Retain the second sentence. Do not truncate it.\n"
        "## GitHub issue links\n- #456 is unrelated.\n"
    )
    assert extract_handoff_findings(text, SOURCE) == [
        expected(text, "Keep the original text.\n"
                 "  Continue with café and `code` for #123.\n"
                 "  - Nested evidence stays attached.", "123", "present"),
        expected(text, "Retain the second sentence. Do not truncate it."),
    ]


def test_handoff_missing_evidence_is_explicit():
    text = "# Handoff #999\n## Findings\n- No reference.\n- #123 or #456.\n"
    assert extract_handoff_findings(text, SOURCE) == [
        expected(text, "No reference."),
        expected(text, "#123 or #456.", evidence="ambiguous"),
    ]


def test_handoff_multiline_paragraphs_preserve_blank_lines():
    text = "## Findings\n- Keep this paragraph.\n\n  And this paragraph.\n\n"
    assert extract_handoff_findings(text, SOURCE) == [
        expected(text, "Keep this paragraph.\n\n  And this paragraph.")
    ]


@pytest.mark.parametrize("text", [
    "", "## Findings\nNo bullet findings.\n", "## Findings\n- \n",
    "## GitHub issue links\n- #123\n",
])
def test_handoff_empty_has_no_candidates(text):
    assert extract_handoff_findings(text, SOURCE) == []


@pytest.mark.parametrize("source", [
    "../escape.md", "docs/../../escape.md", "/absolute.md",
    "C:/escape.md", "docs\\escape.md", "", ".", "docs/../example.md",
    "docs//example.md", "docs/./example.md", "docs/example.md\x00",
])
def test_handoff_source_identity_rejects_escape(source):
    with pytest.raises(ValueError):
        extract_handoff_findings("## Findings\n- Text.\n", source)


def test_handoff_extraction_preserves_bytes(tmp_path, monkeypatch):
    raw = b"## Findings\r\n- Retain caf\xc3\xa9.\r\n  Preserve spacing.\r\n"
    source = tmp_path / "original.md"
    source.write_bytes(raw)
    before = source.stat()
    with monkeypatch.context() as guard:
        def forbidden(*args, **kwargs):
            pytest.fail("Extractor attempted filesystem access")
        guard.setattr("builtins.open", forbidden)
        guard.setattr(Path, "open", forbidden)
        records = extract_handoff_findings(raw, SOURCE)
    assert source.read_bytes() == raw
    assert source.stat().st_mtime_ns == before.st_mtime_ns
    assert records == [expected(raw.decode("utf-8"),
                                "Retain café.\r\n  Preserve spacing.")]
    assert extract_handoff_findings(raw, SOURCE) == records
    assert extract_handoff_findings(raw.decode("utf-8"), SOURCE) == records


def test_handoff_fences_and_heading_boundaries():
    text = (
        "```md\n## Findings\n- Example only.\n```\n"
        "## Findings\n### Details\n1. Actual finding for #123 and #123.\n"
        "~~~\n- Example only.\n~~~\n"
        "## Other\n- Outside findings.\n"
    )
    assert extract_handoff_findings(text, SOURCE) == [
        expected(text, "Actual finding for #123 and #123.", "123", "present")
    ]


def test_handoff_invalid_utf8_rejected():
    with pytest.raises(UnicodeDecodeError):
        extract_handoff_findings(b"\xff", SOURCE)
