"""Policy examples use independent ordering, with explicit lexical final ties.

Three identical size-3 files have two excess copies: (3-1)*3 = 6 bytes
before protection. If one is protected and retained, two may be candidates.
"""

from copy import deepcopy

import pytest
from dedupe.dedupe_plan import make_plan, render_markdown


def row(label, path, mtime=1):
    return {
        "label": label,
        "root": 0,
        "path": path,
        "size": 3,
        "mtime": mtime,
        "sha256": "a" * 64,
        "sample_sha256": "b" * 64,
        "stage": "full",
        "manifest_complete": True,
    }


def groups(*rows):
    return {
        "version": 1,
        "across_labels": [
            {
                "status": "verified",
                "basis": "full_sha256",
                "size": 3,
                "sha256": "a" * 64,
                "files": list(rows),
            }
        ],
        "within_label": [],
        "candidate_groups": [],
    }


def test_label_preference_and_reason():
    plan = make_plan(
        groups(row("A", "a"), row("B", "b")),
        {"keep_preference": [{"labels": ["B", "A"]}]},
    )
    item = plan["groups"][0]
    assert item["keep"]["label"] == "B"
    assert item["candidates"][0]["label"] == "A"
    assert "label order" in item["candidates"][0]["reason"]


def test_order_of_criteria_is_respected():
    source = groups(row("A", "a"), row("B", "archive/longer"))
    plan = make_plan(
        source,
        {
            "keep_preference": [
                {"path_prefixes": ["archive/"]},
                {"labels": ["A", "B"]},
            ]
        },
    )
    assert plan["groups"][0]["keep"]["label"] == "B"


@pytest.mark.parametrize(
    "criterion,first,second,expected",
    [
        ("shorter_path", row("A", "long"), row("B", "b"), "B"),
        ("older_mtime", row("A", "a", 9), row("B", "b", 2), "B"),
        ({"labels": ["unknown"]}, row("A", "a"), row("B", "b"), "A"),
    ],
)
def test_tie_breaks(criterion, first, second, expected):
    plan = make_plan(groups(first, second), {"keep_preference": [criterion]})
    assert plan["groups"][0]["keep"]["label"] == expected


def test_protected_copy_is_kept_and_never_candidate():
    plan = make_plan(
        groups(row("A", "a"), row("B", "safe/b"), row("C", "c")),
        {"protect": ["safe/*"], "keep_preference": [{"labels": ["A"]}]},
    )
    item = plan["groups"][0]
    assert item["keep"]["label"] == "B"
    assert {r["label"] for r in item["candidates"]} == {"A", "C"}


def test_all_protected():
    plan = make_plan(groups(row("A", "a"), row("B", "b")), {"protect": ["*"]})
    item = plan["groups"][0]
    assert item["candidates"] == []
    assert len(item["retained"]) == 1


def test_qualified_protect_glob():
    plan = make_plan(groups(row("A", "same"), row("B", "same")), {"protect": ["B:0/*"]})
    assert plan["groups"][0]["keep"]["label"] == "B"


def test_candidates_are_not_used_for_removal_plan():
    source = {
        "version": 1,
        "across_labels": [],
        "within_label": [],
        "candidate_groups": [{"status": "candidate", "files": [row("A", "a")]}],
    }
    plan = make_plan(source, {})
    assert plan["groups"] == [] and plan["unverified_groups"] == 1


def test_incomplete_evidence_in_verified_group_rejected():
    a, b = row("A", "a"), row("B", "b")
    b["manifest_complete"] = False
    with pytest.raises(ValueError):
        make_plan(groups(a, b), {})


def test_deterministic_and_does_not_mutate_input():
    source = groups(row("B", "b"), row("A", "a"))
    original = deepcopy(source)
    one = make_plan(source, {})
    source["across_labels"][0]["files"].reverse()
    two = make_plan(source, {})
    assert one == two
    assert render_markdown(one) == render_markdown(two)
    assert (
        sorted(original["across_labels"][0]["files"], key=lambda r: r["label"])
        == (source["across_labels"][0]["files"])
    )


def test_header_and_verification_command():
    plan = make_plan(groups(row("A", "a space"), row("B", "b'quote")), {})
    text = render_markdown(plan)
    assert "**Nothing has been deleted." in text
    assert "separate explicit decision by the maintainer" in text
    command = plan["groups"][0]["candidates"][0]["verification_command"]
    assert command.startswith('sha256sum -- "${ROOT_1}"/')
    assert '"${ROOT_2}"/' in command
    assert plan["roots"] == [
        {"variable": "ROOT_1", "label": "A", "root": 0},
        {"variable": "ROOT_2", "label": "B", "root": 0},
    ]


@pytest.mark.parametrize(
    "policy",
    [
        {"keep_preference": ["unknown"]},
        {"protect": "all"},
        {"keep_preference": [{"labels": "A"}]},
        {"keep_preference": [{"other": []}]},
    ],
)
def test_bad_policy_rejected(policy):
    with pytest.raises(ValueError):
        make_plan(groups(row("A", "a"), row("B", "b")), policy)


def test_duplicate_identity_or_conflicting_digest_rejected():
    with pytest.raises(ValueError):
        make_plan(groups(row("A", "a"), row("A", "a")), {})
    b = row("B", "b")
    b["sha256"] = "c" * 64
    with pytest.raises(ValueError):
        make_plan(groups(row("A", "a"), b), {})


@pytest.mark.parametrize("separator", ["\r", "\n", "\u2028", "\u2029", "\x85"])
def test_rendered_commands_with_line_separators_are_withheld(separator):
    plan = make_plan(groups(row("A", "a"), row("B", "b" + separator + "copy")), {})
    text = render_markdown(plan)
    commands = [line[4:] for line in text.split("\n") if line.startswith("    ")]
    assert commands == []
    assert "Verification command withheld" in text
    assert separator in plan["groups"][0]["candidates"][0]["verification_command"]


@pytest.mark.parametrize("name", ["b space", "b'quote", "b\u00e9"])
def test_rendered_commands_preserve_arguments(name):
    import shlex

    plan = make_plan(groups(row("A", "a"), row("B", name)), {})
    text = render_markdown(plan)
    command = "\n".join(
        line[4:] for line in text.split("\n") if line.startswith("    ")
    )
    assert shlex.split(command) == ["sha256sum", "--", "${ROOT_1}/a", "${ROOT_2}/" + name]


@pytest.mark.parametrize("codepoint", [0xD800, 0xDBFF, 0xDC00, 0xDCFF, 0xDFFF])
def test_rendered_commands_with_surrogates_are_withheld(codepoint):
    surrogate = chr(codepoint)
    plan = make_plan(groups(row("A", "a"), row("B", "b" + surrogate)), {})
    text = render_markdown(plan)
    text.encode("utf-8")
    assert not any(line.startswith("    ") for line in text.split("\n"))
    assert "Verification command withheld" in text
    assert "surrogate" in text
    assert surrogate in plan["groups"][0]["candidates"][0]["verification_command"]


@pytest.mark.parametrize("keep_non_utf8", [True, False])
def test_non_utf8_filename_cli_pipeline(tmp_path, keep_non_utf8):
    import json
    import os
    import shlex
    import subprocess
    import sys
    from pathlib import Path

    if os.name != "posix":
        pytest.skip("requires POSIX byte filenames")
    root = tmp_path / "input"
    root.mkdir()
    raw_name = b"b\xff"
    name = os.fsdecode(raw_name)
    other = "z" if keep_non_utf8 else "a"
    for filename in (name, other):
        (root / filename).write_bytes(b"abc")
    before = {os.fsencode(p.name): p.read_bytes() for p in root.iterdir()}
    package = Path(__file__).resolve().parents[2] / "scripts" / "dedupe"

    def cli(script, *args):
        process = subprocess.run(
            [sys.executable, "-I", str(package / script), *map(str, args)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert process.returncode == 0, process.stderr

    config = tmp_path / "config.json"
    config.write_text(json.dumps({"roots": [str(root)]}), encoding="utf-8")
    manifest = tmp_path / "manifest.jsonl"
    cli("hash_inventory.py", "--config", config, "--label", "A", "--out", manifest)
    header = json.loads(manifest.read_text(encoding="utf-8").splitlines()[0])
    assert header["complete"] is True
    merged = tmp_path / "groups.json"
    cli("merge_manifests.py", manifest, "--out", merged)
    assert json.loads(merged.read_text(encoding="utf-8"))["totals"]["verified"] == {
        "groups": 1,
        "files": 2,
        "bytes_reclaimable": 3,
    }
    policy = tmp_path / "policy.json"
    policy.write_text("{}", encoding="utf-8")
    markdown = tmp_path / "plan.md"
    plan_json = tmp_path / "plan.json"
    cli(
        "dedupe_plan.py", merged, "--policy", policy, "--out", markdown,
        "--out-json", plan_json,
    )
    plan = json.loads(plan_json.read_text(encoding="utf-8"))
    group = plan["groups"][0]
    keep, candidate = group["keep"], group["candidates"][0]
    assert os.fsencode((keep if keep_non_utf8 else candidate)["path"]) == raw_name
    assert shlex.split(candidate["verification_command"]) == [
        "sha256sum", "--",
        "${ROOT_1}/" + keep["path"],
        "${ROOT_1}/" + candidate["path"],
    ]
    text = markdown.read_text(encoding="utf-8")
    assert "Verification command withheld" in text and "surrogate" in text
    assert not any(line.startswith("    ") for line in text.split("\n"))
    assert {os.fsencode(p.name): p.read_bytes() for p in root.iterdir()} == before
