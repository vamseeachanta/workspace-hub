"""Guards for the wiki_health_cron output relocation (workspace-hub#2835).

After the relocation, the cron must write its reports under docs/reports/ rather
than knowledge/wikis/, so its output is neither treated as a wiki domain nor
co-mingled with relocated wiki content.
"""

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CRON_PATH = REPO_ROOT / "scripts" / "knowledge" / "wiki_health_cron.py"


def _load_cron():
    spec = importlib.util.spec_from_file_location("wiki_health_cron", CRON_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_reports_dir_under_docs_reports():
    mod = _load_cron()
    rel = mod.REPORTS_DIR.relative_to(mod.REPO_ROOT)
    assert rel.parts[:2] == ("docs", "reports"), rel
    assert "wikis" not in rel.parts, f"report output must leave knowledge/wikis: {rel}"


def test_cron_has_no_hardcoded_absolute_path():
    text = CRON_PATH.read_text()
    assert "/mnt/" not in text, "cron must not hardcode an absolute path"
    assert "REPORTS_DIR = REPO_ROOT" in text, "REPORTS_DIR must be REPO_ROOT-relative"


def test_health_reports_excluded_even_if_dir_reappears(tmp_path, monkeypatch):
    """Guard the exclusion logic, not just the deletion: a stray health-reports/
    under WIKIS_DIR must still be excluded from the linted domain set."""
    mod = _load_cron()
    (tmp_path / "health-reports").mkdir()
    (tmp_path / "engineering").mkdir()
    monkeypatch.setattr(mod, "WIKIS_DIR", tmp_path)
    domains = mod.get_wiki_domains()
    assert "health-reports" not in domains
    assert "engineering" in domains
