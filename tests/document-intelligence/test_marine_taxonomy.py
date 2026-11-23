"""Tests for marine sub-domain taxonomy classifier.

Tests keyword-based classification of marine documents into
7+ sub-domains: hydrodynamics, mooring, structural, subsea,
naval architecture, marine operations, environmental.

Issue: #1622
"""

import copy
import tempfile
from pathlib import Path

import pytest
import yaml


def _import_taxonomy():
    """Import the taxonomy classifier module."""
    import importlib.util
    script_path = Path(__file__).resolve().parents[2] / (
        "scripts/document-intelligence/marine-taxonomy-classifier.py"
    )
    spec = importlib.util.spec_from_file_location("marine_taxonomy_classifier", script_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_MARINE_STANDARDS = [
    {
        "id": "DNV-OS-E301",
        "title": "Position Mooring",
        "domain": "marine",
        "doc_path": "/mnt/ace/mooring/DNV-OS-E301.pdf",
        "doc_paths": ["/mnt/ace/mooring/DNV-OS-E301.pdf"],
        "notes": "Mooring system design for floating structures including chain and wire rope",
        "status": "reference",
    },
    {
        "id": "DNV-RP-C205",
        "title": "Environmental Conditions and Environmental Loads",
        "domain": "marine",
        "doc_path": "/mnt/ace/env/DNV-RP-C205.pdf",
        "doc_paths": ["/mnt/ace/env/DNV-RP-C205.pdf"],
        "notes": "Wave loads, wind loads, current loads, environmental data for offshore structures",
        "status": "reference",
    },
    {
        "id": "OTC-RISER-TENSION",
        "title": "Alternative Tensioning System for Spar Top Tensioned Risers",
        "domain": "marine",
        "doc_path": "",
        "doc_paths": [],
        "notes": "Riser tensioning scheme for Spar hulls using buoyancy modules",
        "status": "reference",
    },
    {
        "id": "SUBSEA-PIPELINE",
        "title": "Submarine Pipeline Systems DNV-OS-F101",
        "domain": "marine",
        "doc_path": "/mnt/ace/subsea/pipeline.pdf",
        "doc_paths": ["/mnt/ace/subsea/pipeline.pdf"],
        "notes": "Submarine pipeline design, installation, and integrity management",
        "status": "reference",
    },
    {
        "id": "HULL-HYDRO-ANALYSIS",
        "title": "Hydrodynamic Analysis of Semi-Submersible Hull",
        "domain": "marine",
        "doc_path": "/mnt/ace/hydro/hull-analysis.pdf",
        "doc_paths": ["/mnt/ace/hydro/hull-analysis.pdf"],
        "notes": "RAO computation, wave diffraction and radiation for semi-submersible platforms",
        "status": "reference",
    },
    {
        "id": "NAVAL-STABILITY",
        "title": "Intact and Damage Stability Assessment for FPSO",
        "domain": "marine",
        "doc_path": "/mnt/ace/naval/fpso-stability.pdf",
        "doc_paths": ["/mnt/ace/naval/fpso-stability.pdf"],
        "notes": "Stability criteria, inclining test, damage stability analysis for floating production",
        "status": "reference",
    },
    {
        "id": "MARINE-OPS-LIFTING",
        "title": "Heavy Lift Operations Offshore",
        "domain": "marine",
        "doc_path": "/mnt/ace/ops/lifting.pdf",
        "doc_paths": ["/mnt/ace/ops/lifting.pdf"],
        "notes": "Offshore heavy lift vessel operations, crane capacity, weather window planning",
        "status": "reference",
    },
    {
        "id": "STRUCTURAL-FATIGUE",
        "title": "Fatigue Design of Offshore Steel Structures",
        "domain": "marine",
        "doc_path": "/mnt/ace/structural/fatigue.pdf",
        "doc_paths": ["/mnt/ace/structural/fatigue.pdf"],
        "notes": "S-N curves, stress concentration factors, fatigue analysis for tubular joints",
        "status": "reference",
    },
    {
        "id": "UNKNOWN-CONF-PAPER",
        "title": "15otc_cfp_web",
        "domain": "marine",
        "doc_path": "",
        "doc_paths": [],
        "notes": "A call for technical paper proposals for the 2015 Offshore Technology Conference",
        "status": "reference",
    },
]


@pytest.fixture
def sample_standards():
    return copy.deepcopy(SAMPLE_MARINE_STANDARDS)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestTaxonomyStructure:
    """Test that the taxonomy defines 7+ sub-domains with keyword lists."""

    def test_taxonomy_has_at_least_7_subdomains(self):
        mod = _import_taxonomy()
        taxonomy = mod.MARINE_TAXONOMY
        assert len(taxonomy) >= 7

    def test_each_subdomain_has_keywords(self):
        mod = _import_taxonomy()
        for name, keywords in mod.MARINE_TAXONOMY.items():
            assert isinstance(keywords, (list, tuple, set)), f"{name} has no keyword list"
            assert len(keywords) > 0, f"{name} has empty keyword list"


class TestKeywordClassification:
    """Test keyword-based classification rules."""

    def test_mooring_classified(self, sample_standards):
        mod = _import_taxonomy()
        mooring_entry = sample_standards[0]  # "Position Mooring"
        result = mod.classify_document(mooring_entry)
        assert result == "mooring"

    def test_environmental_classified(self, sample_standards):
        mod = _import_taxonomy()
        env_entry = sample_standards[1]  # "Environmental Conditions and Loads"
        result = mod.classify_document(env_entry)
        assert result == "environmental"

    def test_hydrodynamics_classified(self, sample_standards):
        mod = _import_taxonomy()
        hydro_entry = sample_standards[4]  # "Hydrodynamic Analysis"
        result = mod.classify_document(hydro_entry)
        assert result == "hydrodynamics"

    def test_subsea_classified(self, sample_standards):
        mod = _import_taxonomy()
        subsea_entry = sample_standards[3]  # "Submarine Pipeline Systems"
        result = mod.classify_document(subsea_entry)
        assert result == "subsea"

    def test_unclassifiable_returns_unclassified(self, sample_standards):
        mod = _import_taxonomy()
        unknown_entry = sample_standards[8]  # "15otc_cfp_web"
        result = mod.classify_document(unknown_entry)
        assert result == "unclassified"


class TestDocumentToSubdomainMapping:
    """Test mapping a batch of documents to sub-domains."""

    def test_batch_classification_returns_all_entries(self, sample_standards):
        mod = _import_taxonomy()
        mapping = mod.classify_batch(sample_standards)
        assert len(mapping) == len(sample_standards)

    def test_batch_classification_keys_are_ids(self, sample_standards):
        mod = _import_taxonomy()
        mapping = mod.classify_batch(sample_standards)
        for entry in sample_standards:
            assert entry["id"] in mapping


class TestReportGeneration:
    """Test report and tag output generation."""

    def test_generate_distribution_table(self, sample_standards):
        mod = _import_taxonomy()
        mapping = mod.classify_batch(sample_standards)
        report = mod.generate_report(sample_standards, mapping)
        # Report should be a string containing markdown
        assert isinstance(report, str)
        assert "Sub-Domain" in report or "sub-domain" in report.lower()
        assert "Count" in report or "count" in report.lower()

    def test_generate_tags_yaml(self, sample_standards, tmp_path):
        mod = _import_taxonomy()
        mapping = mod.classify_batch(sample_standards)
        out_path = tmp_path / "tags.yaml"
        mod.write_tags_yaml(sample_standards, mapping, str(out_path))
        assert out_path.exists()
        with open(out_path) as f:
            data = yaml.safe_load(f)
        assert "entries" in data
        assert len(data["entries"]) == len(sample_standards)
