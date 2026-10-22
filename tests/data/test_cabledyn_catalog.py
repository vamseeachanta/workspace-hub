"""Offline checks for the CableDyn catalog assessment, without importing a solver.

Expected release metadata is transcribed from upstream v0.2.0 CITATION.cff
(2026), pinned in the assessment. The time-step example is from that release's
doc/openfast.rst, 'Time step'; its independent hand calculation is below.
"""

import re
from collections import Counter
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "data/document-index/online-resource-registry.yaml"
ASSESSMENT = ROOT / "docs/research/cabledyn-assessment.md"


def read_assessment():
    text = ASSESSMENT.read_text(encoding="utf-8")
    _, header, body = text.split("---", 2)
    return yaml.safe_load(header), body


def test_existing_catalog_identity_and_histograms():
    """Count actual entries independently; a refresh must not add a duplicate."""
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    entries = registry["entries"]
    assert registry["total_entries"] == len(entries)
    assert len({entry["id"] for entry in entries}) == len(entries)
    for key in ("type", "domain", "download_status"):
        assert registry["summary"][f"by_{key}"] == dict(
            Counter(entry[key] for entry in entries)
        )
    matches = [entry for entry in entries if entry["id"] == "cabledyn_inha"]
    assert len(matches) == 1
    entry = matches[0]
    assert sum(item["url"] == entry["url"] for item in entries) == 1
    assert entry["download_status"] == "reference_only"
    assert entry["local_backup_path"] == ""
    assert entry["type"] == "github_repo"
    assert entry["domain"] == "marine"


def test_catalog_and_assessment_agree_on_release_and_observation():
    metadata, _ = read_assessment()
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    entry = next(e for e in registry["entries"] if e["id"] == metadata["software_id"])
    # Upstream v0.2.0 CITATION.cff, version and date-released (2026).
    assert metadata["release"] == "v0.2.0"
    assert metadata["release_date"] == date(2026, 10, 20)
    assert metadata["release"] in entry["notes"]
    assert str(metadata["release_date"]) in entry["notes"]
    assert entry["last_checked"] == str(metadata["checked_at"].date())
    assert "docs/research/cabledyn-assessment.md" in entry["notes"]
    # Keep the existing externally owned source note discoverable.
    assert "llm-wiki:wikis/marine-engineering/wiki/sources/cabledyn.md" in entry["notes"]


def test_source_provenance_is_pinned_and_complete():
    metadata, body = read_assessment()
    revision = metadata["upstream_revision"]
    assert re.fullmatch(r"[0-9a-f]{40}", revision)
    assert isinstance(metadata["checked_at"], datetime)
    assert metadata["checked_at"].utcoffset().total_seconds() == 0
    assert metadata["checked_at"].date() >= metadata["release_date"]
    required = {
        "README.md", "LICENSE", "NOTICE", "CITATION.cff", "CHANGELOG.md",
        "VALIDATION.md", "doc/openfast.rst", "environment.yml",
        "python/pyproject.toml", "CMakeLists.txt",
    }
    sources = metadata["sources"]
    assert {source["path"] for source in sources} == required
    assert len(sources) == len(required)
    for source in sources:
        assert re.fullmatch(r"[0-9a-f]{64}", source["sha256"])
        assert source["http_status"] == 200
        assert source["retrieved_at"] <= metadata["checked_at"]
        target = f"/blob/{revision}/{source['path']}"
        assert target in body, f"Missing pinned citation for {source['path']}"


def test_worked_example_against_independent_hand_calculation():
    """v0.2.0 doc/openfast.rst 'Time step' gives DT=0.01 s, dtM=0.025 s.

    Whole glue steps: floor(0.025/0.01)=floor(2.5)=2, so committed dtM
    is 2*0.01=0.02 s. The same section describes mean load delay of about
    half the committed dtM: 0.02/2=0.01 s. This is an integration warning,
    not a computed mooring response or an engineering acceptance criterion.
    """
    metadata, _ = read_assessment()
    example = metadata["worked_example"]
    assert Decimal(example["glue_step_s"]) == Decimal("0.01")
    assert Decimal(example["requested_step_s"]) == Decimal("0.025")
    assert Decimal(example["committed_step_s"]) == Decimal("0.02")
    assert Decimal(example["approximate_mean_delay_s"]) == Decimal("0.01")
    assert example["qualification"] == "NOT_EVALUATED"


def test_assessment_retains_limits_and_local_links():
    metadata, body = read_assessment()
    assert metadata["scope"] == "documentation-only"
    assert metadata["qualification"] == "NOT_EVALUATED"
    assert body.index("## Summary") < body.index("## Revision history")
    assert body.index("## Revision history") < body.index("## Identity and version")
    assert "## Validation limits" in body
    assert "## Worked example" in body
    assert "## Ecosystem and follow-up" in body
    for target in re.findall(r"\]\(([^)]+)\)", body):
        if ":" not in target and not target.startswith("#"):
            assert (ASSESSMENT.parent / target.split("#")[0]).is_file(), target
