"""Tests for cross-reference registries tool.

Tests the cross-referencing between online-resource-registry.yaml and
the local standards-transfer-ledger, including fuzzy matching, gap
detection, and report generation.

Issue: #1613
"""

import copy
from itertools import permutations
from pathlib import Path

import pytest
import yaml


def _import_cross_ref():
    """Import the cross-reference module."""
    import importlib.util
    script_path = Path(__file__).resolve().parents[2] / (
        "scripts/document-intelligence/cross-reference-registries.py"
    )
    spec = importlib.util.spec_from_file_location("cross_reference_registries", script_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

SAMPLE_ONLINE = {
    "generated": "2026-04-02",
    "total_entries": 5,
    "summary": {"by_domain": {"marine": 2, "structural": 1, "general": 2}},
    "entries": [
        {
            "id": "dnv_rp_c205",
            "url": "https://rules.dnv.com/docs/pdf/DNV/RP/C205",
            "name": "DNV RP C205 Environmental Conditions and Environmental Loads",
            "type": "standard_portal",
            "domain": "marine",
            "download_status": "not_started",
            "relevance_score": 9,
            "notes": "Wave loads, wind loads",
        },
        {
            "id": "api_rp_2sk",
            "url": "https://www.api.org/rp2sk",
            "name": "API RP 2SK Design and Analysis of Stationkeeping Systems",
            "type": "standard_portal",
            "domain": "marine",
            "download_status": "downloaded",
            "relevance_score": 8,
            "notes": "Mooring design",
        },
        {
            "id": "eurocode3_fatigue",
            "url": "https://eurocodes.jrc.ec.europa.eu/EN1993-1-9",
            "name": "Eurocode 3 Part 1-9 Fatigue",
            "type": "standard_portal",
            "domain": "structural",
            "download_status": "not_started",
            "relevance_score": 5,
            "notes": "Fatigue design of steel",
        },
        {
            "id": "awesome_naval_arch",
            "url": "https://github.com/awesome-naval-arch",
            "name": "Awesome Naval Architecture Collection",
            "type": "github_repo",
            "domain": "general",
            "download_status": "not_started",
            "relevance_score": 3,
            "notes": "",
        },
        {
            "id": "python_openfoam",
            "url": "https://github.com/pyfoam",
            "name": "PyFoam OpenFOAM Python Interface",
            "type": "github_repo",
            "domain": "general",
            "download_status": "not_started",
            "relevance_score": 4,
            "notes": "",
        },
    ],
}

SAMPLE_LEDGER = {
    "generated": "2026-03-12",
    "total": 5,
    "summary": {"reference": 3, "done": 2},
    "standards": [
        {
            "id": "DNV-RP-C205",
            "title": "Environmental Conditions and Environmental Loads",
            "domain": "marine",
            "status": "reference",
            "doc_path": "/mnt/ace/standards/DNV-RP-C205.pdf",
        },
        {
            "id": "API-RP-2SK",
            "title": "Design and Analysis of Stationkeeping Systems",
            "domain": "marine",
            "status": "done",
            "doc_path": "/mnt/ace/standards/API-RP-2SK.pdf",
        },
        {
            "id": "API-5L",
            "title": "Specification for Line Pipe",
            "domain": "pipeline",
            "status": "reference",
            "doc_path": "/mnt/ace/standards/API-5L.pdf",
        },
        {
            "id": "DNV-OS-F101",
            "title": "Submarine Pipeline Systems",
            "domain": "pipeline",
            "status": "done",
            "doc_path": "",
        },
        {
            "id": "NORSOK-M501",
            "title": "Surface Preparation and Protective Coating",
            "domain": "materials",
            "status": "reference",
            "doc_path": "",
        },
    ],
}

SAMPLE_REGISTRY = {
    "generated": "2026-04-01",
    "total_docs": 100,
    "by_domain": {"marine": 50, "pipeline": 30, "structural": 10, "other": 10},
}


@pytest.fixture
def sample_online():
    return copy.deepcopy(SAMPLE_ONLINE)


@pytest.fixture
def sample_ledger():
    return copy.deepcopy(SAMPLE_LEDGER)


@pytest.fixture
def sample_registry():
    return copy.deepcopy(SAMPLE_REGISTRY)


@pytest.fixture
def data_files(tmp_path, sample_online, sample_ledger, sample_registry):
    """Write all sample data files and return their paths."""
    online_path = tmp_path / "online-resource-registry.yaml"
    ledger_path = tmp_path / "standards-transfer-ledger.yaml"
    registry_path = tmp_path / "registry.yaml"
    with open(online_path, "w") as f:
        yaml.dump(sample_online, f, default_flow_style=False)
    with open(ledger_path, "w") as f:
        yaml.dump(sample_ledger, f, default_flow_style=False)
    with open(registry_path, "w") as f:
        yaml.dump(sample_registry, f, default_flow_style=False)
    return {
        "online": str(online_path),
        "ledger": str(ledger_path),
        "registry": str(registry_path),
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestMatchingAlgorithm:
    """Test title similarity and fuzzy matching."""

    def test_exact_title_match(self):
        mod = _import_cross_ref()
        score = mod.title_similarity(
            "Environmental Conditions and Environmental Loads",
            "Environmental Conditions and Environmental Loads",
        )
        assert score >= 0.95

    def test_partial_title_match(self):
        mod = _import_cross_ref()
        score = mod.title_similarity(
            "DNV RP C205 Environmental Conditions and Environmental Loads",
            "Environmental Conditions and Environmental Loads",
        )
        assert score > 0.5

    def test_unrelated_titles_low_score(self):
        mod = _import_cross_ref()
        score = mod.title_similarity(
            "PyFoam OpenFOAM Python Interface",
            "Specification for Line Pipe",
        )
        assert score < 0.45

    def test_find_matches_returns_pairs(self, sample_online, sample_ledger):
        mod = _import_cross_ref()
        matches = mod.find_matches(
            sample_online["entries"], sample_ledger["standards"],
            threshold=0.5,
        )
        # Should find DNV-RP-C205 and API-RP-2SK matches
        assert len(matches) >= 2
        matched_online_ids = {m["online_id"] for m in matches}
        assert "dnv_rp_c205" in matched_online_ids
        assert "api_rp_2sk" in matched_online_ids


@pytest.fixture
def exact_title_score():
    """Hand calculation: identical 'alpha guide' has 11 matching characters.

    The similarity is matching characters / identical string length = 11 / 11.
    This also gives the exact acceptance boundary without using the matcher.
    """
    normalized_title = "alpha guide"
    matching_characters = len(normalized_title)
    return matching_characters / len(normalized_title)


class TestSyntheticMappingInvariants:
    """Exercise mappings with fresh literal data and independent expected sets."""

    @pytest.mark.parametrize(
        "online_ids, expected_pairs, expected_matched_online_ids",
        [
            (
                ("online_a", "online_b"),
                {("online_a", "ledger_a")},
                {"online_a"},
            ),
            (
                ("online_b", "online_a"),
                {("online_b", "ledger_a")},
                {"online_b"},
            ),
        ],
    )
    def test_competing_exact_matches_use_ledger_once(
        self, exact_title_score, online_ids, expected_pairs,
        expected_matched_online_ids,
    ):
        mod = _import_cross_ref()
        online = [
            {"id": entry_id, "name": " ALPHA-Guide "}
            for entry_id in online_ids
        ]
        ledger = [{"id": "ledger_a", "title": "alpha guide"}]

        assert mod.title_similarity(" ALPHA-Guide ", "alpha guide") == exact_title_score
        matches = mod.find_matches(online, ledger, threshold=exact_title_score)

        assert len(matches) == len(expected_pairs)
        assert {(m["online_id"], m["ledger_id"]) for m in matches} == expected_pairs
        assert [m["ledger_id"] for m in matches] == ["ledger_a"]
        assert {m["similarity"] for m in matches} == {exact_title_score}
        expected_online_only = {"online_a", "online_b"} - expected_matched_online_ids
        expected_local_only = {"ledger_a"} - {"ledger_a"}
        assert {
            e["id"] for e in mod.find_online_only(online, matches)
        } == expected_online_only
        assert {
            e["id"] for e in mod.find_local_only(ledger, matches)
        } == expected_local_only

    def test_disjoint_exact_matches_are_order_independent(self, exact_title_score):
        mod = _import_cross_ref()
        online = [
            {"id": "online_a", "name": " ALPHA-Guide "},
            {"id": "online_b", "name": "BETA_Notes"},
            {"id": "online_gap", "name": "gamma checklist"},
        ]
        ledger = [
            {"id": "ledger_b", "title": "beta notes"},
            {"id": "ledger_gap", "title": "delta handbook"},
            {"id": "ledger_a", "title": "alpha guide"},
        ]
        # Hand calculation for the other exact pair: 'beta notes' gives 10 / 10.
        expected_pairs = {("online_a", "ledger_a"), ("online_b", "ledger_b")}
        expected_online_only = {
            "online_a", "online_b", "online_gap",
        } - {"online_a", "online_b"}
        expected_local_only = {
            "ledger_a", "ledger_b", "ledger_gap",
        } - {"ledger_a", "ledger_b"}

        for online_order in permutations(online):
            for ledger_order in permutations(ledger):
                matches = mod.find_matches(
                    list(online_order), list(ledger_order), threshold=exact_title_score,
                )
                assert len(matches) == len(expected_pairs)
                assert {
                    (m["online_id"], m["ledger_id"]) for m in matches
                } == expected_pairs
                assert {m["similarity"] for m in matches} == {exact_title_score}
                assert {
                    e["id"] for e in mod.find_online_only(online_order, matches)
                } == expected_online_only
                assert {
                    e["id"] for e in mod.find_local_only(ledger_order, matches)
                } == expected_local_only

    @pytest.mark.parametrize("empty_side", ["online", "ledger", "both"])
    def test_empty_registry_side(self, exact_title_score, empty_side):
        mod = _import_cross_ref()
        online = [] if empty_side in {"online", "both"} else [
            {"id": "online_a", "name": "alpha guide"},
        ]
        ledger = [] if empty_side in {"ledger", "both"} else [
            {"id": "ledger_a", "title": "alpha guide"},
        ]
        expected_online_ids = set() if empty_side in {"online", "both"} else {"online_a"}
        expected_ledger_ids = set() if empty_side in {"ledger", "both"} else {"ledger_a"}
        expected_matched_ids = set()

        matches = mod.find_matches(online, ledger, threshold=exact_title_score)

        assert matches == []
        assert {
            e["id"] for e in mod.find_online_only(online, matches)
        } == expected_online_ids - expected_matched_ids
        assert {
            e["id"] for e in mod.find_local_only(ledger, matches)
        } == expected_ledger_ids - expected_matched_ids

    def test_matching_does_not_mutate_inputs(self, exact_title_score):
        mod = _import_cross_ref()
        online = [
            {"id": "online_gap", "name": "gamma checklist", "tags": ["draft"]},
            {"id": "online_a", "name": " ALPHA-Guide ", "tags": ["ready"]},
        ]
        ledger = [
            {
                "id": "ledger_gap", "title": "delta handbook",
                "details": {"state": "draft"},
            },
            {
                "id": "ledger_a", "title": "alpha guide",
                "details": {"state": "ready"},
            },
        ]
        original_online = copy.deepcopy(online)
        original_ledger = copy.deepcopy(ledger)
        expected_pairs = {("online_a", "ledger_a")}
        expected_online_only = {"online_gap", "online_a"} - {"online_a"}
        expected_local_only = {"ledger_gap", "ledger_a"} - {"ledger_a"}

        matches = mod.find_matches(online, ledger, threshold=exact_title_score)

        assert len(matches) == len(expected_pairs)
        assert {(m["online_id"], m["ledger_id"]) for m in matches} == expected_pairs
        assert online == original_online
        assert ledger == original_ledger
        assert {
            e["id"] for e in mod.find_online_only(online, matches)
        } == expected_online_only
        assert {
            e["id"] for e in mod.find_local_only(ledger, matches)
        } == expected_local_only
        assert online == original_online
        assert ledger == original_ledger


class TestGapDetection:
    """Test finding online-only and local-only entries."""

    def test_online_only_entries(self, sample_online, sample_ledger):
        mod = _import_cross_ref()
        matches = mod.find_matches(
            sample_online["entries"], sample_ledger["standards"],
            threshold=0.5,
        )
        online_only = mod.find_online_only(sample_online["entries"], matches)
        online_only_ids = {e["id"] for e in online_only}
        # Eurocode, awesome_naval_arch, python_openfoam should be online-only
        assert "eurocode3_fatigue" in online_only_ids
        assert "awesome_naval_arch" in online_only_ids

    def test_local_only_entries(self, sample_online, sample_ledger):
        mod = _import_cross_ref()
        matches = mod.find_matches(
            sample_online["entries"], sample_ledger["standards"],
            threshold=0.5,
        )
        local_only = mod.find_local_only(sample_ledger["standards"], matches)
        local_only_ids = {e["id"] for e in local_only}
        # API-5L, DNV-OS-F101, NORSOK-M501 should be local-only
        assert "API-5L" in local_only_ids
        assert "NORSOK-M501" in local_only_ids


class TestReportGeneration:
    """Test markdown report generation."""

    def test_report_contains_match_count(self, data_files, tmp_path):
        mod = _import_cross_ref()
        report_path = tmp_path / "report.md"
        result = mod.run_cross_reference(
            online_path=data_files["online"],
            ledger_path=data_files["ledger"],
            registry_path=data_files["registry"],
            report_output=str(report_path),
        )
        report_text = report_path.read_text()
        assert "match" in report_text.lower()
        assert isinstance(result["match_count"], int)
        assert result["match_count"] >= 2

    def test_report_contains_domain_comparison(self, data_files, tmp_path):
        mod = _import_cross_ref()
        report_path = tmp_path / "report.md"
        mod.run_cross_reference(
            online_path=data_files["online"],
            ledger_path=data_files["ledger"],
            registry_path=data_files["registry"],
            report_output=str(report_path),
        )
        report_text = report_path.read_text()
        # Should have domain coverage section
        assert "domain" in report_text.lower()
        assert "marine" in report_text.lower()
