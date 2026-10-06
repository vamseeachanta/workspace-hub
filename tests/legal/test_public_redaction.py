"""Tests for scripts/legal/public_redaction.py (owner decisions C20, S01).

Every generator that writes a PUBLIC file of this repository from text it does
not control -- GitHub issue titles and bodies, host agent state -- applies the
identifier gate's single ``Redactor`` before writing. The private list extends
the redactor when the host has one; without it the public rules apply (S01).
A named file that is missing, or rules that cannot load, still stop the job.
Names here are synthetic.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "scripts" / "legal" / "public_redaction.py"

SYNTH_WORD = "zorblaxcorp"
SYNTH_PHRASE = "Quux Marine Nine"


def load():
    spec = importlib.util.spec_from_file_location("public_redaction_under_test", MODULE)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def deny_list(tmp_path, monkeypatch):
    p = tmp_path / "deny.txt"
    p.write_text(f"# synthetic\n{SYNTH_WORD}\nre:(?i)quux\\s+marine\\s+nine\n", encoding="utf-8")
    monkeypatch.setenv("WORKSPACE_HUB_DENY_LIST", str(p))
    monkeypatch.delenv("LEGAL_CLIENT_MAP", raising=False)
    return p


def test_redactor_is_the_gate_redactor(deny_list):
    mod = load()
    red = mod.load_redactor()
    ci = mod._gate()
    assert isinstance(red, ci.Redactor)


def test_redacts_private_word_and_pattern(deny_list):
    mod = load()
    red = mod.load_redactor()
    out = red.redact(f"Issue for {SYNTH_WORD.title()} on the {SYNTH_PHRASE} hull")
    assert SYNTH_WORD not in out.lower()
    assert "quux" not in out.lower()
    assert "[redacted]" in out
    assert "hull" in out


def test_loads_without_a_private_list_and_redacts_public_classes(monkeypatch, tmp_path):
    """Owner decision S01: a host without the private list still runs; the
    redactor applies the public rules instead of stopping the job."""
    monkeypatch.delenv("WORKSPACE_HUB_DENY_LIST", raising=False)
    monkeypatch.delenv("LEGAL_CLIENT_MAP", raising=False)
    mod = load()
    ci = mod._gate()
    monkeypatch.setattr(ci, "DEFAULT_PRIVATE", str(tmp_path / "absent.txt"))
    red = mod.load_redactor()
    # Synthetic shapes assembled at run time so this file itself passes the gate.
    job, host = "B1" + "999", "zz-" + "ws" + "099"
    out = red.redact(f"job {job} on host {host}")
    assert job not in out and host not in out


def test_codename_map_patterns_are_applied(tmp_path, monkeypatch, deny_list):
    m = tmp_path / "map.yaml"
    m.write_text(
        "rules:\n"
        "  - {pattern: 'florpco', replacement: 'client-z', word_bound: true}\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("LEGAL_CLIENT_MAP", str(m))
    mod = load()
    red = mod.load_redactor()
    assert "florpco" not in red.redact("the Florpco riser").lower()


def test_fails_closed_when_named_codename_map_is_missing(tmp_path, monkeypatch, deny_list):
    monkeypatch.setenv("LEGAL_CLIENT_MAP", str(tmp_path / "nomap.yaml"))
    mod = load()
    with pytest.raises(mod.RedactorUnavailable):
        mod.load_redactor()


def test_fails_closed_when_named_private_list_is_missing(monkeypatch, tmp_path):
    monkeypatch.setenv("WORKSPACE_HUB_DENY_LIST", str(tmp_path / "missing.txt"))
    mod = load()
    with pytest.raises(mod.RedactorUnavailable):
        mod.load_redactor()


def test_fails_closed_when_rules_file_is_missing(monkeypatch, tmp_path, deny_list):
    mod = load()
    ci = mod._gate()
    monkeypatch.setattr(ci, "RULES", str(tmp_path / "no-rules.yaml"))
    with pytest.raises(mod.RedactorUnavailable):
        mod.load_redactor()


def test_fails_closed_when_rules_have_no_names_or_patterns(monkeypatch, tmp_path):
    """A rules file that loads but carries no hashed names and no private list
    redacts nothing a name-bearing title needs: refuse it."""
    rules = tmp_path / "rules.yaml"
    rules.write_text("salt: s\nstructural: []\nhashed_names: []\n", encoding="utf-8")
    monkeypatch.delenv("WORKSPACE_HUB_DENY_LIST", raising=False)
    mod = load()
    ci = mod._gate()
    monkeypatch.setattr(ci, "RULES", str(rules))
    monkeypatch.setattr(ci, "DEFAULT_PRIVATE", str(tmp_path / "absent.txt"))
    with pytest.raises(mod.RedactorUnavailable):
        mod.load_redactor()


def test_redact_tree_values_and_keys_idempotent(deny_list):
    mod = load()
    red = mod.load_redactor()
    data = {
        "title": f"{SYNTH_WORD} riser",
        "n": 3,
        "flag": True,
        "none": None,
        "labels": ["ok", f"x-{SYNTH_WORD}"],
        f"{SYNTH_WORD}-key": {"nested": [f"{SYNTH_PHRASE}"]},
    }
    out = mod.redact_tree(data, red)
    blob = json.dumps(out)
    assert SYNTH_WORD not in blob.lower() and "quux" not in blob.lower()
    assert out["n"] == 3 and out["flag"] is True and out["none"] is None
    assert out["labels"][0] == "ok"
    assert mod.redact_tree(out, red) == out
    # the input is not mutated
    assert data["title"] == f"{SYNTH_WORD} riser"


def test_redact_json_file_stays_valid(tmp_path, deny_list):
    mod = load()
    red = mod.load_redactor()
    src = tmp_path / "a.json"
    drive = "D" + ":"  # assembled so this file passes the gate
    src.write_text(json.dumps({"path": drive + '\\ws\\x\\"q', "t": SYNTH_WORD}), encoding="utf-8")
    text = mod.redact_file_text(src.read_text(encoding="utf-8"), ".json", red)
    obj = json.loads(text)
    assert SYNTH_WORD not in text.lower()
    assert "t" in obj


def test_redact_jsonl_keeps_clean_lines_byte_identical(tmp_path, deny_list):
    mod = load()
    red = mod.load_redactor()
    clean = '{"a":1,  "b":"plain text"}'
    profile = "C" + ":\\\\" + "Users"  # assembled so this file passes the gate
    dirty = json.dumps({"text": f"see {SYNTH_WORD} and {profile}\\\\someone\\\\x \\\" q"})
    text = mod.redact_file_text(clean + "\n" + dirty + "\n", ".jsonl", red)
    lines = text.splitlines()
    assert lines[0] == clean
    assert SYNTH_WORD not in lines[1].lower()
    json.loads(lines[1])


def _cli(args, env):
    return subprocess.run(
        [sys.executable, str(MODULE), *args], capture_output=True, text=True, env=env
    )


def test_cli_copy_redacts_content(tmp_path, deny_list):
    src = tmp_path / "history.jsonl"
    src.write_text(json.dumps({"text": f"{SYNTH_WORD} job"}) + "\n", encoding="utf-8")
    dest = tmp_path / "out" / "history.jsonl"
    env = dict(os.environ)
    r = _cli(["copy", str(src), str(dest)], env)
    assert r.returncode == 0, r.stderr
    assert dest.exists()
    assert SYNTH_WORD not in dest.read_text(encoding="utf-8").lower()
    assert SYNTH_WORD not in (r.stdout + r.stderr).lower()


def test_cli_copy_skips_a_file_whose_name_carries_an_identifier(tmp_path, deny_list):
    src = tmp_path / f"note_{SYNTH_WORD}_lifecycle.md"
    src.write_text("clean body\n", encoding="utf-8")
    destdir = tmp_path / "out"
    destdir.mkdir()
    env = dict(os.environ)
    r = _cli(["copy", str(src), str(destdir / src.name)], env)
    assert r.returncode == 0, r.stderr
    assert list(destdir.iterdir()) == []
    assert SYNTH_WORD not in (r.stdout + r.stderr).lower()


def test_cli_copy_fails_closed_and_writes_nothing(tmp_path):
    src = tmp_path / "h.jsonl"
    src.write_text(f"{SYNTH_WORD}\n", encoding="utf-8")
    dest = tmp_path / "out.jsonl"
    env = dict(os.environ)
    env["WORKSPACE_HUB_DENY_LIST"] = str(tmp_path / "missing.txt")
    r = _cli(["copy", str(src), str(dest)], env)
    assert r.returncode == 3
    assert not dest.exists()


def test_cli_in_place_and_check(tmp_path, deny_list):
    f = tmp_path / "board.yaml"
    f.write_text(f"title: {SYNTH_WORD} board\n", encoding="utf-8")
    env = dict(os.environ)
    assert _cli(["check", str(f)], env).returncode == 1
    assert _cli(["inplace", str(f)], env).returncode == 0
    assert SYNTH_WORD not in f.read_text(encoding="utf-8").lower()
    assert _cli(["check", str(f)], env).returncode == 0


def test_cli_self_check(tmp_path, deny_list):
    env = dict(os.environ)
    assert _cli(["self-check"], env).returncode == 0
    env["WORKSPACE_HUB_DENY_LIST"] = str(tmp_path / "missing.txt")
    assert _cli(["self-check"], env).returncode == 3


def _strict_json(text):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            assert key not in out, "redaction must not create duplicate keys"
            out[key] = value
        return out
    return json.loads(text, object_pairs_hook=unique)


def _collision_fixture():
    return {
        "companies": {SYNTH_WORD: {"count": 2}, SYNTH_PHRASE: {"count": 3}},
        "jobs": [{"company": SYNTH_WORD, "score": 12.5},
                 {"company": SYNTH_PHRASE, "score": 18.75}],
        "repeat": {SYNTH_WORD: 9},
        "flags": [True, False, None],
    }


def test_colliding_tree_keys_keep_every_entry_and_reference(deny_list):
    mod = load()
    red = mod.load_redactor()
    source = _collision_fixture()
    out = mod.redact_tree(source, red)
    keys = list(out["companies"])
    assert len(keys) == 2 and len(set(keys)) == 2
    assert list(out["companies"].values()) == [{"count": 2}, {"count": 3}]
    assert [x["company"] for x in out["jobs"]] == keys
    assert list(out["repeat"]) == keys[:1]
    assert [x["score"] for x in out["jobs"]] == [12.5, 18.75]
    assert out["flags"] == source["flags"]
    assert mod.redact_tree(out, red) == out
    assert source == _collision_fixture()
    assert SYNTH_WORD not in json.dumps(out).lower()
    assert "quux" not in json.dumps(out).lower()


def test_json_collision_preserves_numeric_lexemes_and_relationships(deny_list):
    mod = load()
    red = mod.load_redactor()
    source = json.dumps(_collision_fixture(), ensure_ascii=False)
    # Preserve the original JSON numeric spelling instead of reserializing floats.
    source = source.replace('"score": 12.5', '"score": 1.0000000000000001')
    source = source.replace('"count": 3', '"count": 9007199254740993')
    result = mod.redact_file_text(source, ".json", red)
    out = _strict_json(result)
    assert len(out["companies"]) == 2
    assert [x["company"] for x in out["jobs"]] == list(out["companies"])
    assert '"score": 1.0000000000000001' in result
    assert '"count": 9007199254740993' in result
    assert mod.redact_file_text(result, ".json", red) == result


def test_aliases_do_not_overwrite_existing_or_later_keys_and_values(deny_list):
    mod = load()
    red = mod.load_redactor()
    stem = red.redact(SYNTH_WORD)
    source = {
        "companies": {SYNTH_WORD: 2, stem: 8, SYNTH_PHRASE: 3},
        "later": {stem + " [a]": 11},
        "literal": stem + " [b]",
    }
    out = mod.redact_tree(source, red)
    assert len(out["companies"]) == 3
    assert out["companies"][stem] == 8
    assert list(out["companies"].values()) == [2, 8, 3]
    assert out["later"] == source["later"] and out["literal"] == source["literal"]
    aliases = [k for k in out["companies"] if k != stem]
    assert not set(aliases) & {stem + " [a]", stem + " [b]"}
    assert mod.redact_tree(out, red) == out


def test_colliding_jsonl_records_stay_valid_and_clean_lines_unchanged(deny_list):
    mod = load()
    red = mod.load_redactor()
    clean = '{"a":1,  "b":"plain text"}'
    dirty = json.dumps(_collision_fixture())
    result = mod.redact_file_text(clean + "\n" + dirty + "\n", ".jsonl", red)
    lines = result.splitlines()
    assert lines[0] == clean
    out = _strict_json(lines[1])
    assert len(out["companies"]) == 2
    assert [v["count"] for v in out["companies"].values()] == [2, 3]
    assert mod.redact_file_text(result, ".jsonl", red) == result


def test_preexisting_duplicate_json_keys_fail_closed_without_exposing_keys(deny_list):
    mod = load()
    red = mod.load_redactor()
    source = '{' + json.dumps(SYNTH_WORD) + ': 2, ' + json.dumps(SYNTH_WORD) + ': 3}'
    with pytest.raises(mod.RedactorUnavailable) as exc:
        mod.redact_file_text(source, ".json", red)
    assert SYNTH_WORD not in str(exc.value).lower()


def test_cli_duplicate_json_refuses_copy_and_leaves_original_intact(tmp_path, deny_list):
    source = '{' + json.dumps(SYNTH_WORD) + ': 2, ' + json.dumps(SYNTH_WORD) + ': 3}'
    src, dest = tmp_path / "input.json", tmp_path / "output.json"
    src.write_text(source, encoding="utf-8")
    result = _cli(["copy", str(src), str(dest)], dict(os.environ))
    assert result.returncode == 3 and not dest.exists()
    assert src.read_text(encoding="utf-8") == source
    assert SYNTH_WORD not in (result.stdout + result.stderr).lower()
    result = _cli(["inplace", str(src)], dict(os.environ))
    assert result.returncode == 3 and src.read_text(encoding="utf-8") == source


class _SyntheticMask:
    def redact(self, value):
        return "[redacted]" if value.startswith("fixture-company-") else value


def test_aggregate_collision_preservation_and_idempotence():
    mod = load()
    red = _SyntheticMask()
    source = {"companies": {f"fixture-company-{i}": {"count": i, "value": i + .125}
                             for i in range(80)}}
    source["references"] = list(source["companies"])
    source["nested"] = [{key: value} for key, value in source["companies"].items()]
    result = mod.redact_file_text(json.dumps(source), ".json", red)
    out = _strict_json(result)
    assert len(out["companies"]) == 80 and len(set(out["companies"])) == 80
    assert list(out["companies"].values()) == list(source["companies"].values())
    assert out["references"] == list(out["companies"])
    assert [list(row)[0] for row in out["nested"]] == out["references"]
    assert mod.redact_file_text(result, ".json", red) == result
    assert "fixture-company-" not in result


def test_unsafe_alias_generation_fails_closed():
    mod = load()
    class MaskEverything:
        def redact(self, value):
            return "[redacted]"
    with pytest.raises(mod.RedactorUnavailable):
        mod.redact_tree({"fixture-first": 2, "fixture-second": 3}, MaskEverything())


def test_collision_json_decodes_escaped_keys_and_preserves_unicode(deny_list):
    mod = load()
    red = mod.load_redactor()
    escaped_word = '\\u007a' + SYNTH_WORD[1:]
    source = ('{"companies":{"' + escaped_word + '":2,' + json.dumps(SYNTH_PHRASE) +
              ':3},"reference":"' + escaped_word + '","unicode":"\\u03c0"}')
    result = mod.redact_file_text(source, ".json", red)
    out = _strict_json(result)
    assert len(out["companies"]) == 2
    assert list(out["companies"].values()) == [2, 3]
    assert out["reference"] == list(out["companies"])[0]
    assert '"unicode":"\\u03c0"' in result
    assert mod.redact_file_text(result, ".json", red) == result


def test_json_collision_preserves_unbounded_numeric_tokens(deny_list):
    mod = load()
    red = mod.load_redactor()
    huge_integer = "9" * 5001
    numeric_text = huge_integer + ",1e400,-0.0,1.0,1.00"
    source = ('{"companies":{' + json.dumps(SYNTH_WORD) + ':2,' +
              json.dumps(SYNTH_PHRASE) + ':3},"numbers":[' + numeric_text + ']}')
    result = mod.redact_file_text(source, ".json", red)
    out = json.loads(result, parse_int=str, parse_float=str)
    assert len(out["companies"]) == 2
    assert out["numbers"] == [huge_integer, "1e400", "-0.0", "1.0", "1.00"]
    assert '"numbers":[' + numeric_text + ']' in result
    assert mod.redact_file_text(result, ".json", red) == result


@pytest.mark.parametrize("token", ["NaN", "Infinity", "-Infinity"])
def test_nonfinite_json_number_refused(deny_list, token):
    mod = load()
    red = mod.load_redactor()
    with pytest.raises(mod.RedactorUnavailable):
        mod.redact_file_text('{"number":' + token + '}', ".json", red)


def test_jsonl_collision_preserves_bom_crlf_blanks_and_failed_file(tmp_path, deny_list):
    mod = load()
    red = mod.load_redactor()
    clean = '\ufeff{"a":1,  "b":"plain text"}\r\n\r\n'
    source = clean + json.dumps(_collision_fixture()) + "\r\n"
    result = mod.redact_file_text(source, ".jsonl", red)
    assert result.startswith(clean) and result.endswith("\r\n")
    assert result.count("\r\n") == source.count("\r\n")
    assert len(_strict_json(result.splitlines()[-1])["companies"]) == 2
    assert mod.redact_file_text(result, ".jsonl", red) == result
    ambiguous = '{' + json.dumps(SYNTH_WORD) + ':2,' + json.dumps(SYNTH_WORD) + ':3}'
    failed_source = json.dumps(_collision_fixture()) + "\n" + ambiguous + "\n"
    src = tmp_path / "records.jsonl"
    src.write_text(failed_source, encoding="utf-8")
    q = _cli(["inplace", str(src)], dict(os.environ))
    assert q.returncode == 3 and src.read_text(encoding="utf-8") == failed_source
    assert SYNTH_WORD not in (q.stdout + q.stderr).lower()


def test_aliases_independent_of_python_hash_seed(tmp_path, deny_list):
    source = json.dumps(_collision_fixture())
    src = tmp_path / "source.json"
    src.write_text(source, encoding="utf-8")
    outputs = []
    for seed in ["1", "37"]:
        target = tmp_path / ("output-" + seed + ".json")
        env = dict(os.environ, PYTHONHASHSEED=seed)
        q = _cli(["copy", str(src), str(target)], env)
        assert q.returncode == 0, q.stderr
        outputs.append(target.read_bytes())
    assert outputs[0] == outputs[1]


def test_key_aliases_append_to_partial_redaction_and_redactor_is_pure(deny_list):
    deny_list.write_text(deny_list.read_text(encoding="utf-8") + "florpco\n", encoding="utf-8")
    mod = load()
    red = mod.load_redactor()
    first = "prefix_" + SYNTH_WORD + "_suffix"
    second = "prefix_florpco_suffix"
    stem = red.redact(first)
    assert stem == red.redact(second)
    assert red.redact(first) == red.redact(first)
    assert red.redact(stem) == stem
    source = {first: {"n": 2}, second: {"n": 3}, "reference": first}
    out = mod.redact_tree(source, red)
    assert len(out) == 3
    assert all(key.startswith(stem + " [") for key in list(out)[:2])
    assert out["reference"] == list(out)[0]
    assert mod.redact_tree(out, red) == out


def test_alias_reference_matching_does_not_change_substring_redaction(deny_list):
    mod = load()
    red = mod.load_redactor()
    source = _collision_fixture()
    source["description"] = "see " + SYNTH_WORD + " today"
    out = mod.redact_tree(source, red)
    assert out["description"] == red.redact(source["description"])
    assert out["description"] == "see [redacted] today"
    assert len(out["companies"]) == 2


def test_tree_nonstring_keys_and_tuple_types_keep_existing_behavior(deny_list):
    mod = load()
    red = mod.load_redactor()
    source = {3: (SYNTH_WORD, 7, True, None), ("fixture-key", 2): False}
    out = mod.redact_tree(source, red)
    assert list(out) == list(source)
    assert isinstance(out[3], tuple) and out[3] == (red.redact(SYNTH_WORD), 7, True, None)
    assert source[3][0] == SYNTH_WORD
