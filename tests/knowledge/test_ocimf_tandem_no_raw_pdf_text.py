"""Content-safety guard for the OCIMF Tandem wiki promotion (#2559).

This test is *complementary* to the v5 #2227 contract at
``tests/knowledge/test_ocimf_tandem_promotion.py``. The v5 contract checks
that the wiki page exists, has the correct frontmatter, and clears a
discriminating-evidence bar. This file adds a narrowly-scoped denylist
guard: the wiki page MUST NOT verbatim-mirror raw OCR text from the
bounded preview JSON, because that would defeat the "bounded preview, not
raw text dump" boundary the issue body forbids (and the
``raw_pdf_committed_to_git: false`` provenance attestation in the summary
JSON would silently lie).

Issue trail:
- #2521 produced the bounded summary at the doc_key referenced below.
- #2559 promotes that summary into a thin wiki page.
- #2227 is the Branch A contract this work satisfies.

This file is additive — it does NOT modify any test in
``test_ocimf_tandem_promotion.py``.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
OCIMF_DOC_KEY = "sha256:5e5f61e785295f0ac849399bb302cb5192ca84c108e6a57e82b8cc83b8b431af"
OCIMF_PAGE = REPO_ROOT / "knowledge/wikis/engineering/wiki/standards/ocimf-tandem-mooring.md"
SUMMARY_PATH = REPO_ROOT / "data/document-index/summaries" / f"{OCIMF_DOC_KEY}.json"


# Phrases drawn from the OCR'd cover/copyright pages of the source PDF.
# These appear in the bounded summary's ``text_preview`` field (front-matter
# only, by design). The wiki page MUST NOT echo any of them verbatim,
# because doing so would mean the page is reproducing raw OCR'd source
# text rather than curating a summary.
RAW_OCR_DENYLIST = (
    "First Published 2009",
    "ISBN 978 1 905331 62 8",
    "eBook ISBN 978 1 905331 925",
    "British Library Cataloguing in Publication Data",
    "29 Queen Anns Gate",
    "SW1H 9BU",
    "© Oil Companies International Marine Forum, Bermuda",
    "Terms of Use",
)


def _read_page_or_skip() -> str:
    if not OCIMF_PAGE.exists():
        pytest.skip(
            f"OCIMF Tandem wiki page not yet on disk: {OCIMF_PAGE.relative_to(REPO_ROOT)}. "
            "This guard activates once the canonical #2559 promotion lands."
        )
    return OCIMF_PAGE.read_text(encoding="utf-8")


def _frontmatter(text: str) -> dict:
    assert text.startswith("---\n"), "page must begin with YAML frontmatter"
    parts = text.split("---\n", 2)
    assert len(parts) == 3, "frontmatter must be closed with '---'"
    return yaml.safe_load(parts[1])


def test_wiki_page_does_not_contain_raw_ocr_phrases() -> None:
    """The wiki page must not echo raw OCR'd cover-page strings."""
    text = _read_page_or_skip()
    leaks = [phrase for phrase in RAW_OCR_DENYLIST if phrase in text]
    assert leaks == [], (
        "The OCIMF Tandem wiki page contains verbatim OCR'd source phrases "
        f"that would breach the bounded-preview boundary: {leaks!r}. "
        "Replace them with curated paraphrase or remove."
    )


def test_wiki_page_doc_key_matches_summary_artifact() -> None:
    """The wiki page's doc_key must resolve to the live #2521 summary JSON."""
    text = _read_page_or_skip()
    assert f"doc_key: {OCIMF_DOC_KEY}" in text, (
        "wiki page must declare its doc_key matching the #2521 summary artifact"
    )
    if not SUMMARY_PATH.exists():
        pytest.skip(f"summary JSON not present at {SUMMARY_PATH}")
    payload = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    assert payload["sha256"] == OCIMF_DOC_KEY, (
        "summary artifact's sha256 must match wiki doc_key"
    )
    assert payload["provenance"]["raw_pdf_committed_to_git"] is False, (
        "summary attestation must keep raw_pdf_committed_to_git=False; "
        "this guard exists so the wiki page does not silently invalidate that"
    )


def test_wiki_page_frontmatter_is_2471_compliant() -> None:
    """Forward-adopt #2471 frontmatter contract (code_id, publisher, revision).

    Per ``.claude/rules/calc-citation-contract.md`` rule 2: standards-page
    citation targets MUST carry ``code_id``, ``publisher``, ``revision``.
    """
    text = _read_page_or_skip()
    fm = _frontmatter(text)
    assert fm.get("code_id") == "OCIMF-TANDEM-MOORING"
    assert fm.get("publisher") == "OCIMF"
    assert fm.get("revision"), "revision must be populated (per #2471 contract)"


def test_wiki_page_body_word_budget_is_bounded() -> None:
    """The page body must stay within bounded-preview budget.

    Bounded preview policy: the wiki page is curated metadata, not a
    surrogate for the standard. A body that grows past ~1500 words would
    likely indicate the page is reproducing source content. The v5
    contract sets a ``> 200`` floor; this guard sets a ceiling.
    """
    text = _read_page_or_skip()
    # Strip frontmatter
    parts = text.split("---\n", 2)
    body = parts[2] if len(parts) == 3 else text
    word_count = len(body.split())
    assert 100 < word_count < 1500, (
        f"page body has {word_count} words; bounded-preview budget is "
        "100 < N < 1500 (lower bound: enough to be useful; upper bound: "
        "not a raw-text dump in disguise)"
    )
