"""Synthetic fixtures for enrichment and GTM identifier-gate retirement."""
import importlib.util
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]


def load_script(relative):
    spec = importlib.util.spec_from_file_location(Path(relative).stem, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WorkflowIdentifierRetirement(unittest.TestCase):
    def test_enrichment_writes_identifier_and_keeps_metadata(self):
        module = load_script("scripts/data/orcaflex/enrich-and-clean.py")
        with tempfile.TemporaryDirectory() as temporary:
            src, dst = Path(temporary) / "input.yaml", Path(temporary) / "out.yaml"
            src.write_text("project: SyntheticProject\nlines: []\n")
            self.assertTrue(module.process_file(src, dst, None, None, [],
                                               [re.compile("SyntheticProject")]))
            output = module.yaml.safe_load(dst.read_text())
            self.assertEqual("SyntheticProject", output["project"])
            self.assertTrue(output["metadata"]["enriched"])
            self.assertEqual(0, output["metadata"]["enrich_log"]["lines_enriched"])

    def test_empty_enrichment_input_still_fails(self):
        module = load_script("scripts/data/orcaflex/enrich-and-clean.py")
        with tempfile.TemporaryDirectory() as temporary:
            src, dst = Path(temporary) / "input.yaml", Path(temporary) / "out.yaml"
            src.write_text("")
            self.assertFalse(module.process_file(src, dst, None, None, [], []))
            self.assertFalse(dst.exists())

    def test_gtm_identifier_hits_do_not_change_validation(self):
        module = load_script("scripts/validation/validate_gtm_2554_matrix.py")
        with mock.patch.object(module, "count_claims", return_value=({}, [])), \
             mock.patch.object(module, "MIN_LIVE_TARGETS", 0):
            self.assertEqual([], module.validate([], "", "", [("x", "SyntheticProject")],
                                                 [("x", "email", "person@example.invalid")]))

    def test_gtm_count_evidence_failures_still_block(self):
        module = load_script("scripts/validation/validate_gtm_2554_matrix.py")
        errors = module.validate([], "", "", [], [])
        self.assertTrue(any("below" in error for error in errors))
        self.assertTrue(any("missing count claim" in error for error in errors))

    def test_gtm_report_does_not_claim_identifier_clearance(self):
        module = load_script("scripts/validation/validate_gtm_2554_matrix.py")
        report = module.render_scan([], [], [], [])
        self.assertIn("Identifier review: not performed", report)
        self.assertNotIn("Legal deny-list fixed-string hits: 0", report)

    def test_gtm_main_does_not_scan_contacts(self):
        module = load_script("scripts/validation/validate_gtm_2554_matrix.py")
        with tempfile.TemporaryDirectory() as temporary:
            fixture = Path(temporary) / "fixture.md"
            fixture.write_text("SyntheticProject person@example.invalid\n")
            with mock.patch.multiple(module, SCAFFOLD=fixture, SUMMARY=fixture,
                                     README=fixture, MIN_LIVE_TARGETS=0), \
                 mock.patch.object(module, "count_claims", return_value=({}, [])), \
                 mock.patch.object(module, "scan_contacts", side_effect=AssertionError("retired scan")), \
                 mock.patch.object(sys, "argv", ["validator"]):
                self.assertEqual(0, module.main())

    def test_enrichment_cli_does_not_load_identifier_list(self):
        module = load_script("scripts/data/orcaflex/enrich-and-clean.py")
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            source, destination = folder / "input", folder / "output"
            source.mkdir()
            (source / "fixture.yaml").write_text("project: SyntheticProject\n")
            with mock.patch.object(module, "_load_riser_loader", return_value=None), \
                 mock.patch.object(module, "_load_pipeline_lookup", return_value=None), \
                 mock.patch.object(module, "_load_rig_fleet", return_value=[]), \
                 mock.patch.object(module, "_load_deny_patterns", side_effect=AssertionError("retired scan")), \
                 mock.patch.object(sys, "argv", ["enricher", "--input", str(source),
                                  "--output", str(destination), "--deny-list", "missing.yaml"]):
                module.main()
            self.assertTrue((destination / "fixture.yaml").exists())

    def test_gtm_evidence_url_restrictions_remain(self):
        module = load_script("scripts/validation/validate_gtm_2554_matrix.py")
        self.assertFalse(module.evidence_urls_are_allowed("https://linkedin.com/in/synthetic"))
        self.assertFalse(module.deep_link_is_bounded("PENDING"))


if __name__ == "__main__":
    unittest.main()
