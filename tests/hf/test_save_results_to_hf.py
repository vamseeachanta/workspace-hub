import importlib.util, sys
from pathlib import Path
import pytest

# load the tool module by repo-relative path (tests/hf/ -> repo root is parents[2])
_TOOL = Path(__file__).resolve().parents[2] / "scripts" / "hf" / "save_results_to_hf.py"
_spec = importlib.util.spec_from_file_location("srhf", _TOOL)
srhf = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(srhf)


def test_flatten_dotted_keys_and_list_stringified():
    out = srhf._flatten({"a": {"b": 1}, "c": [1, 2]})
    assert out["a.b"] == 1
    assert out["c"] == "[1, 2]"  # lists are JSON-stringified (lossless)


def test_discover_list_of_dicts():
    t = srhf.discover_tables({"fields": [{"x": 1}, {"x": 2}]})
    assert "fields" in t and len(t["fields"]) == 2


def test_discover_dict_of_dicts_injects_id():
    # a scalar sibling ("note") stops the top level being read as one dict-of-dicts,
    # so walk recurses and finds `wells` as its own dict-of-dicts table.
    t = srhf.discover_tables({"wells": {"w1": {"depth": 10}, "w2": {"depth": 20}},
                              "note": "meta"})
    assert t["wells"][0]["_id"] == "w1"


def test_discover_bare_dict_of_dicts_is_single_records_table():
    # documents the tool's actual behavior: a bare dict-of-dicts at the top is one row.
    t = srhf.discover_tables({"w1": {"depth": 10}, "w2": {"depth": 20}})
    assert "records" in t and {r["_id"] for r in t["records"]} == {"w1", "w2"}


def test_clean_name_sanitizes():
    assert srhf._clean_name("RAO Table!") == "rao_table"


def test_numeric_stats_reports_min_max_nulls():
    import pandas as pd
    lines = srhf.numeric_stats("t", pd.DataFrame({"v": [1.0, 2.0, None]}))
    assert any("min=1.0" in l and "max=2.0" in l and "nulls=1" in l for l in lines)


def test_card_note_appears_in_card():
    card = srhf.build_card("aceengineer/x-y", {"t": {"rows": 1, "cols": 2}},
                           {"s.json": "a" * 40}, "cc-by-4.0", None, None, None,
                           "WITHHELD column z — see #99")
    assert "## Data-quality notes" in card
    assert "WITHHELD column z — see #99" in card


def test_card_note_absent_when_none():
    card = srhf.build_card("aceengineer/x-y", {"t": {"rows": 1, "cols": 2}},
                           {"s.json": "a" * 40}, "cc-by-4.0", None, None, None, None)
    assert "## Data-quality notes" not in card


def test_refuses_runs_target(monkeypatch):
    monkeypatch.setattr(sys, "argv",
                        ["prog", "--repo-id", "aceengineer/foo-runs", "--input", "x.json"])
    with pytest.raises(SystemExit) as exc:
        srhf.main()
    assert "runs" in str(exc.value).lower()


# --- C5 (wh#3488): rebuild-on-publish Vercel Deploy Hook trigger ---

class _FakeResp:
    status = 200
    def __enter__(self): return self
    def __exit__(self, *a): return False


def test_trigger_deploy_hook_fires_when_env_set(monkeypatch):
    calls = {}
    def fake_urlopen(req, timeout=None):
        calls["url"] = req.full_url
        calls["method"] = req.get_method()
        return _FakeResp()
    monkeypatch.setenv("VERCEL_DEPLOY_HOOK_URL", "https://hook.example/deploy/abc")
    monkeypatch.setattr(srhf.urllib.request, "urlopen", fake_urlopen)
    status = srhf.trigger_deploy_hook()
    assert status == 200
    assert calls["url"] == "https://hook.example/deploy/abc"
    assert calls["method"] == "POST"  # deploy hooks require POST


def test_trigger_deploy_hook_skips_when_env_unset(monkeypatch):
    monkeypatch.delenv("VERCEL_DEPLOY_HOOK_URL", raising=False)
    called = {"n": 0}
    monkeypatch.setattr(srhf.urllib.request, "urlopen",
                        lambda *a, **k: called.__setitem__("n", called["n"] + 1))
    assert srhf.trigger_deploy_hook() is None
    assert called["n"] == 0  # no network call when the hook isn't configured


def test_trigger_deploy_hook_disabled_flag_skips(monkeypatch):
    monkeypatch.setenv("VERCEL_DEPLOY_HOOK_URL", "https://hook.example/deploy/abc")
    called = {"n": 0}
    monkeypatch.setattr(srhf.urllib.request, "urlopen",
                        lambda *a, **k: called.__setitem__("n", called["n"] + 1))
    assert srhf.trigger_deploy_hook(enabled=False) is None
    assert called["n"] == 0


def test_trigger_deploy_hook_never_raises_on_failure(monkeypatch):
    monkeypatch.setenv("VERCEL_DEPLOY_HOOK_URL", "https://hook.example/deploy/abc")
    def boom(*a, **k):
        raise OSError("network down")
    monkeypatch.setattr(srhf.urllib.request, "urlopen", boom)
    # a failed rebuild trigger must NEVER fail an otherwise-successful publish
    assert srhf.trigger_deploy_hook() is None
