from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ENG_STD = ROOT / "knowledge/wikis/engineering-standards/wiki"
ENG = ROOT / "knowledge/wikis/engineering/wiki"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_2543_doris_codes_metadata_pages_exist_and_are_no_extraction():
    pages = [
        ENG_STD / "sources/doris-codes-specs-faceted-index.md",
        ENG_STD / "sources/doris-techstreet-drop.md",
        ENG_STD / "sources/doris-company-specs.md",
        ENG_STD / "sources/doris-deepstar.md",
    ]
    for page in pages:
        assert page.exists(), page
        text = read(page)
        assert "extraction_policy: metadata-only" in text
        assert "raw_copy_allowed: false" in text
        assert "/mnt/ace/doris/codes" in text
        assert "No raw standards text" in text or "no raw standards text" in text.lower()


def test_2543_bv_stub_is_public_metadata_only_if_present():
    page = ENG_STD / "standards/bv-ship-offshore-rules.md"
    if not page.exists():
        deferred = ENG_STD / "sources/doris-codes-specs-faceted-index.md"
        assert "BV publisher stub deferred" in read(deferred)
        return
    text = read(page)
    for field in ["code_id:", "publisher:", "revision:", "revision_source:", "verified_on:", "public_url:"]:
        assert field in text
    assert "clause" not in text.lower()


def test_2542_doris_university_metadata_pages_exist_without_fulltext_or_ocr():
    pages = [
        ENG / "sources/doris-university-module-1-00-subsea-production-systems-overview.md",
        ENG / "sources/doris-university-module-1-01-production-control-systems.md",
        ENG / "sources/doris-university-module-1-02-umbilical-systems.md",
        ENG / "sources/doris-university-module-1-03-installation-workover-control.md",
        ENG / "sources/doris-university-lunch-and-learn-control-systems.md",
        ENG / "sources/doris-university-lunch-and-learn-umbilical-systems.md",
        ENG / "sources/doris-university-syllabus-snapshot.md",
    ]
    for page in pages:
        assert page.exists(), page
        text = read(page)
        assert "extraction_policy: metadata-first" in text
        assert "raw_copy_allowed: false" in text
        assert "ocr_allowed: false" in text
        assert "/mnt/ace/doris/training" in text
        assert "Full text was not extracted" in text


def test_2542_training_concepts_and_standard_links_are_bounded():
    concepts = [
        ENG / "concepts/subsea-production-system-overview.md",
        ENG / "concepts/subsea-production-control-system.md",
        ENG / "concepts/subsea-umbilical-system.md",
        ENG / "concepts/installation-workover-control-system.md",
        ENG / "concepts/methanol-injection-analysis.md",
        ENG / "concepts/umbilical-tube-sizing-api-17e.md",
        ENG / "concepts/hydrostatic-pressure-depth.md",
        ENG / "concepts/subsea-accumulator-sizing.md",
    ]
    for page in concepts:
        assert page.exists(), page
        text = read(page)
        assert "curated_summary_only: true" in text
        assert "full_text_extracted: false" in text
    assert (ENG_STD / "standards/api-17e.md").exists()
    assert "code_id: api-17e" in read(ENG_STD / "standards/api-17e.md")


def test_elements_execution_updates_indexes_and_logs():
    std_index = read(ENG_STD / "index.md")
    eng_index = read(ENG / "index.md")
    assert "doris-codes-specs-faceted-index" in std_index
    assert "doris-university-module-1-00" in eng_index
    assert "umbilical-tube-sizing-api-17e" in eng_index
    assert "DORIS Codes metadata-only standards pointer pass" in read(ENG_STD / "log.md")
    assert "Doris University metadata-first tranche 1" in read(ENG / "log.md")
