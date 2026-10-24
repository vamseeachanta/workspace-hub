"""End-to-end preservation and static mutation checks use temporary trees only.

The CLI example has two size-3 copies per label: four equal files yield one
verified group with (4-1)*3 = 9 reclaimable bytes. Keeping A leaves three
proposals. Every expected path, size and mtime is observed before execution,
and the independently computed digest snapshot must be identical afterward.
"""

import ast
import hashlib
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

import pytest
from dedupe import _common
from dedupe.hash_inventory import run

PACKAGE = Path(__file__).resolve().parents[2] / "scripts" / "dedupe"


def snapshot(root):
    result = {}
    for path in sorted(root.rglob("*")):
        info = path.lstat()
        result[path.relative_to(root).as_posix()] = (
            info.st_size,
            info.st_mtime_ns,
            hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None,
        )
    return result


def cli(script, *args, expected=0):
    process = subprocess.run(
        [sys.executable, "-I", str(PACKAGE / script), *map(str, args)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert process.returncode == expected, process.stderr
    return process


def test_full_pipeline_leaves_entire_input_tree_unchanged(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    output = tmp_path / "output"
    output.mkdir()
    for label in ["A", "B"]:
        root = data / label
        root.mkdir()
        (root / "a space").write_bytes(b"abc")
        (root / "b'quote").write_bytes(b"abc")
        (root / "unique").write_bytes(b"longer unique file")
        (root / "link").symlink_to("a space")
    before = snapshot(data)
    manifests = []
    for label in ["A", "B"]:
        config = output / (label + ".config.json")
        config.write_text(json.dumps({"roots": [str(data / label)]}))
        manifest = output / (label + ".jsonl")
        cache = output / (label + ".cache.json")
        args = [
            "--config",
            config,
            "--label",
            label,
            "--out",
            manifest,
            "--cache",
            cache,
        ]
        cli("hash_inventory.py", *args)
        cli("hash_inventory.py", *args)
        manifests.append(manifest)
    merged = output / "groups.json"
    cli("merge_manifests.py", *manifests, "--out", merged)
    assert json.loads(merged.read_text())["totals"]["verified"] == {
        "groups": 1,
        "files": 4,
        "bytes_reclaimable": 9,
    }
    policy = output / "policy.json"
    policy.write_text(json.dumps({"keep_preference": [{"labels": ["A", "B"]}]}))
    markdown = output / "plan.md"
    plan_json = output / "plan.json"
    cli(
        "dedupe_plan.py",
        merged,
        "--policy",
        policy,
        "--out",
        markdown,
        "--out-json",
        plan_json,
    )
    plan = json.loads(plan_json.read_text())
    assert len(plan["groups"][0]["candidates"]) == 3
    assert snapshot(data) == before
    first = markdown.read_bytes(), plan_json.read_bytes()
    cli(
        "dedupe_plan.py",
        merged,
        "--policy",
        policy,
        "--out",
        markdown,
        "--out-json",
        plan_json,
    )
    assert (markdown.read_bytes(), plan_json.read_bytes()) == first


def test_no_scanned_file_mutation_primitives():
    """AST greps every module, allowing only atomic_write_output's os.replace."""
    replacements = []
    forbidden = {"remove", "unlink", "rmtree", "move", "rename", "link", "symlink"}
    for path in sorted(PACKAGE.glob("*.py")):
        tree = ast.parse(path.read_text())
        parents = {
            child: parent
            for parent in ast.walk(tree)
            for child in ast.iter_child_nodes(parent)
        }
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(
                node.func, ast.Attribute
            ):
                continue
            assert node.func.attr not in forbidden, (path.name, node.lineno)
            if node.func.attr == "replace":
                ancestor = node
                while ancestor in parents and not isinstance(ancestor, ast.FunctionDef):
                    ancestor = parents[ancestor]
                assert path.name == "_common.py"
                assert isinstance(ancestor, ast.FunctionDef)
                assert ancestor.name == "atomic_write_output"
                assert ast.unparse(node.func) == "os.replace"
                assert [ast.unparse(arg) for arg in node.args] == [
                    "temporary_output",
                    "destination",
                ]
                replacements.append(node)
    assert len(replacements) == 1


def test_hard_link_output_alias_refused(tmp_path):
    root = tmp_path / "input"
    root.mkdir()
    path = root / "a"
    path.write_bytes(b"same")
    out = tmp_path / "output"
    os.link(path, out)
    with pytest.raises(ValueError):
        run({"roots": [str(root)]}, "A", out)
    assert path.read_bytes() == b"same"


def test_input_alias_and_output_collision_refused(tmp_path):
    inputs = tmp_path / "input.json"
    inputs.write_text("{}")
    with pytest.raises(ValueError):
        _common.distinct_outputs([inputs], inputs=[inputs])
    with pytest.raises(ValueError):
        _common.distinct_outputs([inputs, inputs])


def test_shell_verification_arguments_are_literal(tmp_path):
    """shlex must recover exactly two literal filenames, even with shell syntax."""
    from dedupe.dedupe_plan import make_plan
    from test_plan import groups, row

    plan = make_plan(groups(row("A", "$(echo surprise)"), row("B", "b'quote")), {})
    command = plan["groups"][0]["candidates"][0]["verification_command"]
    assert shlex.split(command) == [
        "sha256sum",
        "--",
        "${ROOT_1}/$(echo surprise)",
        "${ROOT_2}/b'quote",
    ]


def test_budget_cli_exit_and_incomplete_header(tmp_path):
    root = tmp_path / "input"
    root.mkdir()
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"roots": [str(root)]}))
    out = tmp_path / "partial.jsonl"
    # Synthetic budget input, smaller than traversal work; no timing acceptance limit.
    cli(
        "hash_inventory.py",
        "--config",
        config,
        "--label",
        "A",
        "--out",
        out,
        "--max-seconds",
        "1e-100",
        expected=1,
    )
    assert not json.loads(out.read_text().splitlines()[0])["complete"]
