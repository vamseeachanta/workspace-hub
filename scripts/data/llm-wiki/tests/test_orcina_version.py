import json
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent.parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import orcina_version as mod  # noqa: E402


def test_detect_current_version_from_fixture():
    html = """
    <html><body>
      <h2>OrcaFlex 11.6c</h2>
      <p>OrcaWave 11.6c is available.</p>
      <li>OrcFxAPI 11.6c release notes</li>
    </body></html>
    """

    assert mod.detect_current_version(html) == {
        "orcaflex": "11.6c",
        "orcawave": "11.6c",
        "orcfxapi": "11.6c",
    }


def test_detect_returns_none_when_missing():
    versions = mod.detect_current_version("<h1>OrcaFlex 11.6c</h1>")

    assert versions["orcaflex"] == "11.6c"
    assert versions["orcawave"] is None
    assert versions["orcfxapi"] is None


def test_detect_tolerates_unexpected_version_format():
    html = "OrcaFlex 12.0 OrcaWave 13.0a-beta OrcFxAPI 11.6c"

    assert mod.detect_current_version(html) == {
        "orcaflex": "12.0",
        "orcawave": "13.0a-beta",
        "orcfxapi": "11.6c",
    }


def test_load_stored_version_missing_key(tmp_path):
    index_path = tmp_path / "index.json"
    index_path.write_text(json.dumps({"product": "OrcaFlex"}), encoding="utf-8")

    assert mod.load_stored_version(index_path) is None


def test_load_stored_version_present(tmp_path):
    index_path = tmp_path / "index.json"
    index_path.write_text(json.dumps({"upstream_version": "11.6c"}), encoding="utf-8")

    assert mod.load_stored_version(index_path) == "11.6c"


def test_diff_versions_bump():
    stored = {"orcaflex": "11.6b", "orcawave": "11.6c", "orcfxapi": None}
    current = {"orcaflex": "11.6c", "orcawave": "11.6c", "orcfxapi": "11.6c"}

    assert mod.diff_versions(stored, current) == {
        "orcaflex": ("11.6b", "11.6c"),
        "orcfxapi": (None, "11.6c"),
    }

