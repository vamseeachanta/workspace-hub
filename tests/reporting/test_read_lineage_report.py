"""Synthetic observations for issue #2180, not live resolver expectations.

Independent hand enumeration: the resolved chain has two recorded steps;
the ambiguous observation has two candidates; the cycle is a -> b -> a.
The four inventory rows remain four rows, including repeated observations.
No policy threshold or suppression decision is calculated by these tests.
"""

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from read_lineage_report import build_inventory, render_json


SCRIPT = Path(__file__).resolve().parents[2] / "scripts/reporting/read_lineage_report.py"


@pytest.fixture
def traces():
    return [
        {
            "raw_token": "aliases/old.md",
            "steps": [
                {"kind": "repo_alias", "input": "aliases/old.md", "output": "aliases/new.md"},
                {"kind": "repo_alias", "input": "aliases/new.md", "output": "docs/read.md"},
            ],
            "disposition": "resolved",
            "evidence": {"state": "observed", "references": ["evidence/resolved.json"]},
        },
        {
            "raw_token": "aliases/missing.md",
            "steps": [],
            "disposition": "unresolved",
            "evidence": {"state": "unknown", "reason": "not_recorded", "references": None},
        },
        {
            "raw_token": "aliases/shared.md",
            "steps": [
                {
                    "kind": "repo_alias", "input": "aliases/shared.md", "output": None,
                    "candidates": ["docs/right.md", "docs/left.md"],
                    "evidence": {"state": "unknown"},
                },
            ],
            "disposition": "ambiguous",
        },
        {
            "raw_token": "aliases/a.md",
            "steps": [
                {"kind": "repo_alias", "input": "aliases/a.md", "output": "aliases/b.md"},
                {"kind": "repo_alias", "input": "aliases/b.md", "output": "aliases/a.md"},
            ],
            "disposition": "cyclic",
        },
    ]


def test_lineage_preserves_all_recorded_steps(traces):
    inventory = build_inventory(traces)
    resolved = next(row for row in inventory["traces"] if row["disposition"] == "resolved")
    assert resolved == {
        "raw_token": "aliases/old.md",
        "steps": [
            {"kind": "repo_alias", "input": "aliases/old.md", "output": "aliases/new.md"},
            {"kind": "repo_alias", "input": "aliases/new.md", "output": "docs/read.md"},
        ],
        "disposition": "resolved",
        "evidence": {"state": "observed", "references": ["evidence/resolved.json"]},
    }


def test_ambiguous_trace_stays_ambiguous(traces):
    ambiguous = next(row for row in build_inventory(traces)["traces"]
                     if row["raw_token"] == "aliases/shared.md")
    assert ambiguous["disposition"] == "ambiguous"
    assert ambiguous["steps"] == [{
        "kind": "repo_alias", "input": "aliases/shared.md", "output": None,
        "candidates": ["docs/right.md", "docs/left.md"],
        "evidence": {"state": "unknown"},
    }]


def test_trace_cycle_is_reported(traces):
    cyclic = next(row for row in build_inventory(traces)["traces"]
                  if row["raw_token"] == "aliases/a.md")
    assert cyclic["disposition"] == "cyclic"
    assert [step["output"] for step in cyclic["steps"]] == ["aliases/b.md", "aliases/a.md"]


def test_unknown_evidence_and_null_disposition_are_preserved(traces):
    unresolved = next(row for row in build_inventory(traces)["traces"]
                      if row["raw_token"] == "aliases/missing.md")
    assert unresolved == {
        "raw_token": "aliases/missing.md", "steps": [], "disposition": "unresolved",
        "evidence": {"state": "unknown", "reason": "not_recorded", "references": None},
    }
    unknown = {"raw_token": None, "steps": [], "disposition": None, "evidence": None}
    assert build_inventory([unknown])["traces"] == [unknown]


def test_inventory_sorting_is_deterministic_and_input_is_unchanged(traces):
    original = copy.deepcopy(traces)
    expected_tokens = ["aliases/a.md", "aliases/missing.md", "aliases/old.md", "aliases/shared.md"]
    assert [row["raw_token"] for row in build_inventory(traces)["traces"]] == expected_tokens
    assert render_json(traces) == render_json(reversed(traces))
    assert traces == original
    result = build_inventory(traces)
    result["traces"].clear()
    assert traces == original
    resolved = next(row for row in build_inventory(traces)["traces"]
                    if row["disposition"] == "resolved")
    resolved["steps"].clear()
    resolved["evidence"]["references"].clear()
    assert traces == original


def test_same_token_ties_duplicates_and_candidate_order_are_preserved():
    left = {"raw_token": "alias.md", "steps": [], "disposition": "unresolved"}
    right = {"raw_token": "alias.md", "steps": [], "disposition": "ambiguous"}
    assert build_inventory([left, right, left])["traces"] == [right, left, left]
    assert render_json([left, right]) == render_json([right, left])


def test_json_contract_and_empty_inventory():
    assert render_json([]) == '{\n  "traces": []\n}\n'
    observation = {"raw_token": "docs/read.md", "steps": [], "disposition": "not_evaluated"}
    assert json.loads(render_json([observation])) == {"traces": [observation]}
    reordered = dict(reversed(list(observation.items())))
    assert render_json([reordered]) == render_json([observation])


def test_does_not_resolve_or_infer_dispositions():
    # A recorded loop and candidate do not authorize overriding a caller status.
    observation = {
        "raw_token": "aliases/a.md", "disposition": "not_evaluated",
        "steps": [{"kind": "repo_alias", "input": "aliases/a.md", "output": "aliases/a.md",
                   "candidates": ["docs/read.md"]}],
    }
    assert build_inventory([observation]) == {"traces": [observation]}


@pytest.mark.parametrize("field", ["raw_token", "input", "output", "candidates", "references"])
def test_filesystem_paths_are_rejected_without_echoing_them(tmp_path, field):
    private_path = str(tmp_path / "private.md")
    observation = {
        "raw_token": "docs/read.md", "disposition": "unresolved",
        "steps": [{"kind": "repo_alias", "input": "old/read.md", "output": "docs/read.md",
                   "candidates": []}],
        "evidence": {"state": "unknown", "references": []},
    }
    if field == "raw_token":
        observation[field] = private_path
    elif field == "references":
        observation["evidence"][field] = [private_path]
    else:
        observation["steps"][0][field] = [private_path] if field == "candidates" else private_path
    with pytest.raises(ValueError) as error:
        build_inventory([observation])
    assert private_path not in str(error.value)


@pytest.mark.parametrize("token", ["../read.md", "~/read.md", "X:\\private\\read.md",
                                   "//remote/read.md", "file:read.md", "read\nexcerpt", ""])
def test_unsafe_tokens_are_rejected(token):
    with pytest.raises(ValueError):
        build_inventory([{"raw_token": token, "steps": [], "disposition": "unresolved"}])


@pytest.mark.parametrize("observation", [
    {},
    {"raw_token": "read.md", "disposition": "unresolved", "steps": None},
    {"raw_token": "read.md", "disposition": False, "steps": []},
    {"raw_token": "read.md", "disposition": "unresolved", "steps": [], "transcript": "excerpt"},
    {"raw_token": "read.md", "disposition": "unresolved", "steps": [],
     "evidence": {"state": "unknown", "reason": "raw transcript excerpt"}},
    {"raw_token": "read.md", "disposition": "unresolved",
     "steps": [{"kind": "repo_alias", "input": "read.md"}]},
])
def test_malformed_or_unapproved_fields_are_not_silently_dropped(observation):
    with pytest.raises(ValueError):
        build_inventory([observation])


def test_cli_file_and_stdin_emit_the_same_inventory(tmp_path, traces):
    source = tmp_path / "traces.json"
    source.write_text(json.dumps(traces), encoding="utf-8", newline="\n")
    original = source.read_bytes()
    file_run = subprocess.run([sys.executable, "-I", str(SCRIPT), str(source)],
                              capture_output=True, text=True, cwd=tmp_path, check=True)
    stdin_run = subprocess.run([sys.executable, "-I", str(SCRIPT)], input=json.dumps(traces),
                               capture_output=True, text=True, cwd=tmp_path, check=True)
    assert json.loads(file_run.stdout) == {"traces": sorted(traces, key=lambda row: row["raw_token"])}
    assert stdin_run.stdout == file_run.stdout
    assert not file_run.stderr and not stdin_run.stderr
    assert source.read_bytes() == original


@pytest.mark.parametrize("payload", ["{", "{}", '[{"raw_token":"a","raw_token":"b"}]',
                                     '[{"raw_token":NaN}]'])
def test_cli_invalid_json_returns_no_partial_inventory(tmp_path, payload):
    result = subprocess.run([sys.executable, "-I", str(SCRIPT)], input=payload,
                            capture_output=True, text=True, cwd=tmp_path)
    assert result.returncode != 0
    assert result.stdout == ""
    assert result.stderr == "invalid lineage input\n"


def test_cli_missing_file_does_not_expose_caller_path(tmp_path):
    result = subprocess.run([sys.executable, "-I", str(SCRIPT), str(tmp_path / "missing.json")],
                            capture_output=True, text=True, cwd=tmp_path)
    assert result.returncode != 0
    assert result.stdout == ""
    assert result.stderr == "invalid lineage input\n"


@pytest.mark.parametrize("argument_kind", ["extra_filename", "unknown_option"])
def test_cli_argument_errors_do_not_expose_caller_path(tmp_path, argument_kind):
    caller_path = (tmp_path / "input.json").as_posix()
    arguments = (["input.json", caller_path] if argument_kind == "extra_filename"
                 else ["--unknown=" + caller_path])
    result = subprocess.run([sys.executable, "-I", str(SCRIPT), *arguments],
                            capture_output=True, text=True, cwd=tmp_path)
    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr == "invalid lineage arguments\n"
