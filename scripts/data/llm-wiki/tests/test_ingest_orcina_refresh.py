import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from urllib.error import URLError

_SCRIPT_DIR = Path(__file__).resolve().parent.parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import orcina_refresh  # noqa: E402


def load_ingest_module():
    spec = importlib.util.spec_from_file_location("ingest_orcina", _SCRIPT_DIR / "ingest-orcina.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_head_pdf_network_failure_returns_none(monkeypatch):
    def fail(*args, **kwargs):
        raise URLError("connection refused")

    monkeypatch.setattr(orcina_refresh.urllib.request, "urlopen", fail)

    assert orcina_refresh.head_pdf("https://example.test/paper.pdf") is None


def test_changelog_path_appends_timestamp_on_collision(tmp_path):
    changelog_dir = tmp_path / "changelog"
    changelog_dir.mkdir()
    existing = changelog_dir / "2026-04-28-orcaflex-11.6c.md"
    existing.write_text("old", encoding="utf-8")

    path = orcina_refresh.changelog_path(
        tmp_path,
        "orcaflex-11.6c",
        now=orcina_refresh.datetime(2026, 4, 28, 12, 34, 56, tzinfo=orcina_refresh.timezone.utc),
    )

    assert path.name == "2026-04-28-orcaflex-11.6c-T123456.md"


def test_safe_get_papers_entry_tolerates_legacy_meta():
    stored = {"https://example.test/a.pdf": {"bytes_sha256": "abc"}}

    assert orcina_refresh.safe_get_papers_entry(stored, "https://example.test/a.pdf") is None


def test_write_changelog_renders_per_product_sections(tmp_path):
    path = orcina_refresh.write_changelog(
        tmp_path,
        "orcaflex-11.6c",
        {
            "product_topics": {
                "orcaflex": {"added": ["https://example.test/a"], "removed": [], "modified": []},
                "orcawave": {"added": [], "removed": ["https://example.test/b"], "modified": []},
                "orcfxapi": {"added": [], "removed": [], "modified": ["https://example.test/c"]},
            },
            "supplementary": {"added": [], "removed": [], "modified": []},
            "papers": {"added": [], "removed": [], "modified": []},
            "version_bump": {},
        },
        now=orcina_refresh.datetime(2026, 4, 28, tzinfo=orcina_refresh.timezone.utc),
    )

    body = path.read_text(encoding="utf-8")
    assert "### Product: OrcaFlex" in body
    assert "### Product: OrcaWave" in body
    assert "### Product: OrcFxAPI" in body


def test_refresh_prunes_legacy_papers_meta_without_entry_key(tmp_path, monkeypatch):
    mod = load_ingest_module()
    papers_dir = tmp_path / "papers"
    papers_dir.mkdir()
    meta_path = papers_dir / "papers_meta.json"
    meta_path.write_text(
        json.dumps({"https://example.test/old.pdf": {"bytes_sha256": "abc"}}),
        encoding="utf-8",
    )

    monkeypatch.setattr(mod, "fetch_page", lambda url: "<html><body>No PDFs now</body></html>")

    result = mod.ingest_papers(tmp_path, refresh=True)

    assert result["entries"] == []
    assert result["changes"]["removed"] == ["https://example.test/old.pdf"]
    assert json.loads(meta_path.read_text(encoding="utf-8")) == {}


def test_refresh_falls_back_to_download_when_head_fails(tmp_path, monkeypatch):
    mod = load_ingest_module()
    pdf_url = "https://www.orcina.com/test.pdf"
    pdf_bytes = b"stable pdf bytes"
    digest = hashlib.sha256(pdf_bytes).hexdigest()
    papers_dir = tmp_path / "papers"
    papers_dir.mkdir()
    meta_path = papers_dir / "papers_meta.json"
    entry = {
        "file": "papers/test.md",
        "title": "Test PDF",
        "source_url": pdf_url,
        "downloaded": "2026-04-28T00:00:00+00:00",
    }
    meta_path.write_text(
        json.dumps({pdf_url: {"last_modified": None, "content_length": None, "bytes_sha256": digest, "entry": entry}}),
        encoding="utf-8",
    )
    (papers_dir / "test.md").write_text("existing", encoding="utf-8")

    monkeypatch.setattr(mod, "fetch_page", lambda url: f'<a href="{pdf_url}">Test PDF</a>')
    monkeypatch.setattr(mod, "head_pdf", lambda url: None)
    monkeypatch.setattr(mod, "download_bytes", lambda url, timeout=60: pdf_bytes)
    monkeypatch.setattr(mod, "pdftotext_bytes", lambda data: (_ for _ in ()).throw(AssertionError("should not reconvert")))

    result = mod.ingest_papers(tmp_path, refresh=True)

    assert result["entries"] == [entry]
    assert result["changes"] == {"added": [], "removed": [], "modified": []}


def test_refresh_writes_changelog_under_resolved_root(tmp_path, monkeypatch):
    mod = load_ingest_module()

    monkeypatch.setattr(mod, "PRODUCTS", {"orcaflex": mod.PRODUCTS["orcaflex"]})
    monkeypatch.setattr(mod, "parse_toc_xml", lambda url: [])
    monkeypatch.setattr(mod, "ingest_supplementary", lambda output_root, refresh=False, force_full=False: {
        "entries": [],
        "changes": {"added": [], "removed": [], "modified": []},
        "versions": {"orcaflex": "11.6c", "orcawave": None, "orcfxapi": None},
    })
    monkeypatch.setattr(mod, "ingest_papers", lambda output_root, refresh=False, force_full=False: {
        "entries": [],
        "changes": {"added": [], "removed": [], "modified": []},
    })
    monkeypatch.setattr(mod, "resolve_wiki_dir", lambda: tmp_path)

    assert mod.main(["--refresh", "--products", "orcaflex"]) == 0

    changelogs = list((tmp_path / "changelog").glob("*.md"))
    assert len(changelogs) == 1

