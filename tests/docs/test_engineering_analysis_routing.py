"""Routing observations describe evidence; validation cannot certify an analysis.

Expected decisions are derived by inspection of ENG-ANALYSIS-CRITERIA Rev 1
(2026), AC-08 through AC-12, and the worked example in the routing guide.
No engineering calculation or acceptance coefficient is exercised.
"""
import json
from copy import deepcopy
from html.parser import HTMLParser
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
GUIDE = ROOT / "docs/standards/engineering-analysis-routing.html"
SCHEMA = ROOT / "config/schemas/engineering-analysis-observation.schema.json"
EXAMPLE = ROOT / "docs/examples/engineering-analysis-observation.json"


def validator():
    assert "date-time" in FormatChecker.checkers, "Install jsonschema[format-nongpl]"
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def example():
    return json.loads(EXAMPLE.read_text())


def test_worked_example_preserves_documented_but_not_evaluated():
    """Hand classification: a documented route supplies no verified responses.

    The pinned criteria plus a source entry point support DOCUMENTED. No
    reviewed analysis or dataset was inspected, so both remain NOT_EVALUATED;
    the result contains no engineering value. This is evidence accounting,
    not an assertion of compliance with the linked benchmark.
    """
    item = example()
    validator().validate(item)
    assert item["routing"]["status"] == "DOCUMENTED"
    assert item["compliance"]["status"] == "NOT_EVALUATED"
    assert item["dataset"]["status"] == "NOT_EVALUATED"
    assert item["dataset"]["dataset_id"] is None
    assert item["compliance"]["analysis_revision"] is None


@pytest.mark.parametrize("section,field", [
    ("criteria", "revision"), ("criteria", "source_revision"),
    ("workflow", "locator"), ("subject", "record_ref"),
    ("subject", "component_family"), ("subject", "program"),
    ("routing", "evidence_ref"), ("routing", "entry_point_ref"),
    ("routing", "entry_point_revision"),
])
def test_missing_routing_identity_or_evidence_rejected(section, field):
    item = example()
    del item[section][field]
    assert list(validator().iter_errors(item))


@pytest.mark.parametrize("status", ["PARTIAL", "DEMONSTRATED"])
def test_documented_route_cannot_establish_compliance(status):
    item = example()
    item["compliance"]["status"] = status
    assert list(validator().iter_errors(item))


@pytest.mark.parametrize("field", [
    "owner_repo", "dataset_id", "revision", "manifest_ref", "content_digest",
    "catalog_ref",
])
def test_dataset_reference_needs_complete_identity(field):
    item = example()
    item["dataset"] = {
        "status": "REFERENCED", "owner_repo": "reference-data",
        "dataset_id": "synthetic-dataset", "revision": "example-revision",
        "manifest_ref": "reference-data:data/example/manifest.json",
        "content_digest": "sha256:" + "a" * 64,
        "catalog_ref": "catalog:existing-source",
    }
    validator().validate(item)
    item["dataset"][field] = None
    assert list(validator().iter_errors(item))


@pytest.mark.parametrize("change", [
    {"observed_at": "not-a-time"}, {"observed_at": "2026-02-30T00:00:00Z"},
    {"criteria": {}}, {"workflow": {}}, {"limitations": []},
    {"unexpected": "unreviewed field"},
])
def test_malformed_observation_rejected(change):
    item = example()
    item.update(deepcopy(change))
    assert list(validator().iter_errors(item))


@pytest.mark.parametrize("section", ["routing", "compliance", "dataset"])
def test_unknown_status_is_not_success(section):
    item = example()
    item[section]["status"] = "PASS"
    assert list(validator().iter_errors(item))


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "a":
            self.hrefs.append(attrs["href"])


def test_guide_links_resolve_locally_and_entry_points_route_to_it():
    parser = Links()
    parser.feed(GUIDE.read_text())
    for href in parser.hrefs:
        if href.startswith("https:"):
            continue
        target, _, fragment = href.partition("#")
        if target:
            assert (GUIDE.parent / target).is_file(), href
        elif fragment:
            assert fragment in parser.ids
    for entry in ["docs/README.md", "docs/ROUTING_INDEX.md"]:
        assert "standards/engineering-analysis-routing.html" in (ROOT / entry).read_text()


def test_guide_covers_programs_scales_and_existing_authorities():
    text = GUIDE.read_text()
    for name in ["OrcaFlex", "OrcaWave", "AQWA", "ANSYS", "GHS", "NavCad",
                 "component", "connection", "assembly", "structure", "system",
                 "data-source-catalog.yml", "domain-database-index.yml",
                 "NOT_EVALUATED", "exact", "off-grid", "unqualified",
                 "Revision history", "worked-example"]:
        assert name in text
    assert example()["criteria"]["source_revision"] in text
    assert "no engineering answer" in text
