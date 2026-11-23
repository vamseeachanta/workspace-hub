"""Issue 3936: ingestion and automation must not invoke retired gates."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SHELL_CALLERS = (
    "scripts/cron/commit-learning-artifacts.sh",
    "scripts/hermes/backfill-skills-to-repo.sh",
    "scripts/readiness/nightly-readiness.sh",
    "scripts/readiness/remediate-harness.sh",
    "config/shell/bashrc-snippets.sh",
)


def load_phase(name):
    path = ROOT / "scripts/data/document-index" / name
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RetiredScannerCallers(unittest.TestCase):
    def test_ingestion_writes_outputs_without_a_scanner(self):
        for name in ("phase-d-data-sources.py", "phase-e-registry.py"):
            with self.subTest(phase=name), tempfile.TemporaryDirectory() as temp:
                module = load_phase(name)
                cfg = {"output": {"enhancement_plan": "plan.yaml",
                    "index_path": "index.jsonl", "summaries_dir": "summaries",
                    "registry_path": "registry.yaml"}}
                items = {"standards": [{"title": "Synthetic reference"}],
                         "apis": [], "gaps": []}
                with mock.patch.object(module, "HUB_ROOT", Path(temp)), \
                     mock.patch.object(module, "load_config", return_value=cfg), \
                     mock.patch.object(module, "load_index", return_value=[]), \
                     mock.patch.object(module, "load_enhancement_plan", return_value={"by_domain": {"test": []}}), \
                     mock.patch.object(module, "run_legal_scan", create=True, side_effect=AssertionError("retired gate called")):
                    if name.startswith("phase-d"):
                        with mock.patch.object(module, "load_deny_list", return_value=[]), \
                             mock.patch.object(module, "collect_repo_items", return_value=items), \
                             mock.patch.object(sys, "argv", [name, "--repo", "digitalmodel"]):
                            self.assertEqual(module.main(), 0)
                        self.assertTrue((Path(temp) / "specs/data-sources/digitalmodel.yaml").is_file())
                    else:
                        with mock.patch.object(sys, "argv", [name]):
                            self.assertEqual(module.main(), 0)
                        self.assertTrue((Path(temp) / "registry.yaml").is_file())
                        with mock.patch.object(sys, "argv", [name, "--skip-legal"]), \
                             self.assertLogs(module.logger, level="WARNING") as logs:
                            self.assertEqual(module.main(), 0)
                        self.assertIn("ignored", " ".join(logs.output))

    def test_shell_automation_has_no_retired_gate_or_bypass(self):
        for name in SHELL_CALLERS:
            text = (ROOT / name).read_text(encoding="utf-8")
            active = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))
            with self.subTest(path=name):
                self.assertNotIn("legal-sanity-scan", active)
                self.assertNotIn("check_identifiers.py", active)
                self.assertNotIn("--no-verify", active)

    def test_snapshot_redaction_and_normal_commits_remain(self):
        learning = (ROOT / SHELL_CALLERS[0]).read_text(encoding="utf-8")
        backfill = (ROOT / SHELL_CALLERS[1]).read_text(encoding="utf-8")
        self.assertIn('"$PUBLIC_REDACTION" inplace', learning)
        self.assertIn("git_safe_commit", learning)
        self.assertIn('git commit -m "hermes: backfill', backfill)


if __name__ == "__main__":
    unittest.main()
