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


# --- visibility enforcement (workspace-hub#3483) -------------------------------------
# create_repo(private=..., exist_ok=True) only applies private= at CREATION, so an
# existing dataset kept its old visibility while the tool printed the requested one.


class _FakeApi:
    """Duck-typed stand-in for HfApi — no huggingface_hub import needed."""

    def __init__(self, private=True):
        self._private = private
        self.calls = []

    def update_repo_settings(self, repo_id, repo_type, private):
        self.calls.append(("settings", repo_id, repo_type, private))
        self._private = private

    def dataset_info(self, repo_id):
        return type("Info", (), {"private": self._private})()


class _LegacyApi:
    """Older hub (< 0.25): exposes update_repo_visibility and NOT update_repo_settings.

    Deliberately does not inherit _FakeApi — inheriting would leave update_repo_settings
    resolvable via the MRO, so hasattr() would still find it and the fallback branch
    would never be exercised.
    """

    def __init__(self, private=True):
        self._private = private
        self.calls = []

    def update_repo_visibility(self, repo_id, repo_type, private):
        self.calls.append(("visibility", repo_id, repo_type, private))
        self._private = private

    def dataset_info(self, repo_id):
        return type("Info", (), {"private": self._private})()


def test_ensure_visibility_flips_existing_private_repo_to_public():
    api = _FakeApi(private=True)  # dataset already exists, and is private
    srhf.ensure_visibility(api, "aceengineer/x", public=True)
    assert api.calls == [("settings", "aceengineer/x", "dataset", False)]


def test_ensure_visibility_enforces_private_rather_than_relying_on_default():
    api = _FakeApi(private=False)  # already public; --public NOT passed
    srhf.ensure_visibility(api, "aceengineer/x", public=False)
    # private-by-default is a fail-safe only if it is actually asserted on the remote
    assert api.calls == [("settings", "aceengineer/x", "dataset", True)]


def test_ensure_visibility_falls_back_to_update_repo_visibility_on_older_hub():
    api = _LegacyApi(private=True)
    assert not hasattr(api, "update_repo_settings")
    srhf.ensure_visibility(api, "aceengineer/x", public=True)
    assert api.calls == [("visibility", "aceengineer/x", "dataset", False)]


def test_ensure_visibility_exits_when_no_visibility_api_exists():
    class _Ancient:
        pass
    with pytest.raises(SystemExit) as e:
        srhf.ensure_visibility(_Ancient(), "aceengineer/x", public=True)
    assert "VISIBILITY" in str(e.value)


def test_verify_visibility_returns_actual_when_it_matches():
    api = _FakeApi(private=False)
    assert srhf.verify_visibility(api, "aceengineer/x", public=True) is False


def test_verify_visibility_exits_when_remote_disagrees():
    # the #3483 failure mode: asked for public, remote is still private
    api = _FakeApi(private=True)
    with pytest.raises(SystemExit) as e:
        srhf.verify_visibility(api, "aceengineer/x", public=True)
    msg = str(e.value)
    assert "VISIBILITY FAILED" in msg and "PRIVATE" in msg


def test_ensure_then_verify_is_the_fixed_path():
    # end to end on the duck-typed api: the flip makes the readback agree
    api = _FakeApi(private=True)
    srhf.ensure_visibility(api, "aceengineer/x", public=True)
    assert srhf.verify_visibility(api, "aceengineer/x", public=True) is False


# --- section maps vs row sets (workspace-hub#3699) ------------------------------------
# A dict whose values are all dicts is only a table if it holds no nested tables.


def test_section_map_with_nested_series_is_not_one_table():
    # the real shape from digitalmodel/docs/api/structural/wall-thickness-explorer.json
    doc = {
        "meta": {"od_mm": 273.0, "grade": "X65"},
        "min_wall_pass": {"DNV-ST-F101": 19.5, "DNV-ST-F201": 8.0},
        "series": {
            "DNV-ST-F101": [{"w": 8.0, "u": 8.7}, {"w": 8.5, "u": 7.9}],
            "DNV-ST-F201": [{"w": 8.0, "u": 0.59}],
        },
    }
    t = srhf.discover_tables(doc)
    # must NOT collapse the file into a single records table
    assert "records" not in t
    # each series is its own table, found by recursing past the section map
    assert t["series.DNV-ST-F101"] == [{"w": 8.0, "u": 8.7}, {"w": 8.5, "u": 7.9}]
    assert len(t["series.DNV-ST-F201"]) == 1


def test_section_map_does_not_mix_scalar_and_list_into_one_column():
    # the exact parquet failure: DNV-ST-F101 held a float in one row and a
    # JSON-stringified list in another, giving an unconvertible object column
    doc = {"min_wall_pass": {"A": 19.5}, "series": {"A": [{"w": 1.0}]}}
    t = srhf.discover_tables(doc)
    for rows in t.values():
        for row in rows:
            for col, val in row.items():
                assert not isinstance(val, dict), f"{col} still nested"


def test_plain_dict_of_dicts_is_still_one_table():
    # regression guard: the documented behaviour must not change
    t = srhf.discover_tables({"w1": {"depth": 10}, "w2": {"depth": 20}})
    assert "records" in t and {r["_id"] for r in t["records"]} == {"w1", "w2"}


def test_contains_nested_table_detects_both_shapes():
    assert srhf._contains_nested_table({"s": [{"a": 1}]})            # list-of-dicts
    assert srhf._contains_nested_table({"s": {"k": [{"a": 1}]}})     # dict-of-lists-of-dicts
    assert not srhf._contains_nested_table({"s": {"a": 1}})          # plain scalars


def test_deeply_nested_section_map_is_not_one_table():
    # cathodic-protection-explorer.json: rows are FOUR levels down.
    doc = {
        "meta": {"structures": ["4-leg jacket"], "climates": ["temperate"]},
        "series": {
            "4-leg jacket": {
                "temperate": {
                    "bare": [{"l": 10.0, "mass": 12692.3}, {"l": 15.0, "mass": 19038.4}],
                    "good-coating": [{"l": 10.0, "mass": 11103.8}],
                },
            },
        },
    }
    t = srhf.discover_tables(doc)
    assert "records" not in t, "the file collapsed into one row-per-section table again"
    assert t["series.4-leg jacket.temperate.bare"] == [
        {"l": 10.0, "mass": 12692.3}, {"l": 15.0, "mass": 19038.4}]
    assert len(t["series.4-leg jacket.temperate.good-coating"]) == 1


def test_contains_nested_table_is_recursive():
    assert srhf._contains_nested_table({"a": {"b": {"c": [{"x": 1}]}}})
    assert not srhf._contains_nested_table({"a": {"b": {"c": {"x": 1}}}})


def test_contains_nested_table_bounded_on_pathological_depth():
    # a very deep scalar-only nest must terminate and report False, not recurse forever
    node = {"leaf": 1}
    for _ in range(40):
        node = {"d": node}
    assert srhf._contains_nested_table(node) is False
