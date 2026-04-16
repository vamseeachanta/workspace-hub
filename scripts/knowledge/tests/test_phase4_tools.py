import importlib.util
import json
from pathlib import Path

from unittest.mock import patch


def load_module(module_name: str, relative_path: str):
    repo_root = Path(__file__).resolve().parents[3]
    module_path = repo_root / relative_path
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_doc_key_lookup_json_output_returns_success_and_valid_json(capsys):
    module = load_module("doc_key_lookup", "scripts/knowledge/doc-key-lookup.py")

    with patch.object(module, "search_index_by_key", return_value=[]), \
         patch.object(module, "search_index_by_path", return_value=[{"path": "docs/example.pdf"}]), \
         patch.object(module, "search_standards_ledger", return_value=[{"id": "API-RP-2SK", "doc_path": "/tmp/example.pdf"}]), \
         patch.object(module, "search_wiki_pages", return_value=[{"domain": "marine-engineering", "page": "knowledge/wikis/marine-engineering/wiki/sources/example.md", "title": "Example"}]):
        exit_code = module.run_lookup("API-RP-2SK", by="standard", json_output=True)

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert exit_code == 0
    assert payload["lookup_type"] == "standard"
    assert len(payload["index_records"]) == 1
    assert len(payload["standards_ledger"]) == 1
    assert len(payload["wiki_pages"]) == 1


def test_pyramid_dt1_requires_added_field(tmp_path):
    module = load_module("pyramid_conformance_check", "scripts/knowledge/pyramid-conformance-check.py")

    repo_root = tmp_path
    wiki_dir = repo_root / "knowledge" / "wikis" / "engineering" / "wiki" / "entities"
    wiki_dir.mkdir(parents=True)
    page = wiki_dir / "sample.md"
    page.write_text(
        "---\n"
        'title: "Sample"\n'
        "tags: [example]\n"
        "last_updated: 2026-04-16\n"
        "---\n\n"
        "# Sample\n",
        encoding="utf-8",
    )

    with patch.object(module, "REPO_ROOT", repo_root), \
         patch.object(module, "WIKIS_DIR", repo_root / "knowledge" / "wikis"), \
         patch.object(module, "WIKI_DOMAINS", ["engineering"]):
        result = module.check_dt1()

    assert result.status == "fail"
    assert any("missing added" in evidence for evidence in result.evidence)
