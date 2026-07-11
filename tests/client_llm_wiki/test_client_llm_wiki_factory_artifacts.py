"""Executable contract tests for the complete client-wiki factory workflow."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / ".claude/skills/coordination/client-llm-wiki-factory/SKILL.md"
REGISTRY = "/private/authority/client-wikis.yml"
SHORT = "example"
REPO = "example/llm-wiki-example"


def _workflow() -> str:
    text = SKILL.read_text(encoding="utf-8")
    blocks = re.findall(r"```bash\n(.*?)```", text, re.DOTALL)
    return next(block for block in blocks if "# FACTORY_WORKFLOW_V2" in block)


def _tool_source() -> str:
    return r"""#!/usr/bin/env python3
import json, os, pathlib, sys
name, args = pathlib.Path(sys.argv[0]).name, sys.argv[1:]
log = pathlib.Path(os.environ["CALL_LOG"])
def record(stage):
    data = {"stage": stage, "argv": args,
            "author_name": os.environ.get("CLIENT_WIKI_GIT_AUTHOR_NAME"),
            "author_email": os.environ.get("CLIENT_WIKI_GIT_AUTHOR_EMAIL"),
            "registry_path": os.environ.get("REGISTRY_PATH")}
    with log.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(data, sort_keys=True) + "\n")
    if os.environ.get("FAIL_STAGE") == stage:
        raise SystemExit(23)
if name == "git":
    if args[:2] == ["rev-parse", "--show-toplevel"]:
        record("workspace"); print(os.environ["FAKE_WORKSPACE"])
    elif args and args[0] == "clone":
        record("clone"); target = pathlib.Path(args[2]); target.mkdir()
        (target / ".gitignore").write_text("private-output/\n")
        (target / ".claude").mkdir(); (target / ".claude/CLAUDE.md").write_text("safe\n")
    else: raise SystemExit(97)
elif name == "gh": record("create")
elif name == "yq":
    payload = json.load(sys.stdin); print(payload[args[1].removeprefix(".")])
elif name == "uv":
    command = next(item for item in ("validate-registry", "classify", "verify-private-repo",
                                      "render", "finalize-scaffold") if item in args)
    if command == "verify-private-repo":
        count = sum(json.loads(line)["stage"].startswith("attest") for line in log.read_text().splitlines()) if log.exists() else 0
        stage = "attest-first" if count == 0 else "attest-final"
    else: stage = command
    record(stage)
    if command == "classify":
        print(json.dumps({"repo": os.environ["EXPECTED_REPO"], "target": os.environ["EXPECTED_TARGET"],
                          "status": "wrong" if os.environ.get("FAIL_STAGE") == "status" else "planned"}))
    elif command == "render":
        destination = pathlib.Path(args[args.index("--manifest") + 1])
        if os.environ.get("FAIL_STAGE") == "manifest-persistence": raise SystemExit(24)
        if os.environ.get("RENDER_OUTCOME") == "absent": raise SystemExit(0)
        if os.environ.get("RENDER_OUTCOME") == "empty": destination.touch(); raise SystemExit(0)
        backing = destination.parent / ("." + destination.name + ".backing-123-0123456789abcdef")
        descriptor = os.open(backing, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        os.write(descriptor, b'{"version":1}\n'); os.fsync(descriptor); os.close(descriptor)
        os.link(backing, destination)
        print(json.dumps({"manifest": str(destination), "backing_name": backing.name, "size": 14}))
elif name == "registry-update": record("registry-update")
elif name == "check-client-wiki-registry.sh": record("checker")
else: raise SystemExit(98)
"""


def _fake_tools(tmp_path: Path) -> tuple[Path, Path, Path]:
    workspace = tmp_path / "workspace"
    checker = workspace / "scripts/enforcement/check-client-wiki-registry.sh"
    checker.parent.mkdir(parents=True)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    source = _tool_source()
    for name in ("git", "gh", "yq", "uv", "registry-update"):
        path = bin_dir / name
        path.write_text(source, encoding="utf-8")
        path.chmod(0o755)
    checker.write_text(source, encoding="utf-8")
    checker.chmod(0o755)
    return workspace, bin_dir, tmp_path / "calls.jsonl"


def _run(
    tmp_path: Path,
    *,
    fail_stage: str = "",
    omit: str = "",
    precondition: str = "",
    render_outcome: str = "",
):
    workspace, bin_dir, log = _fake_tools(tmp_path)
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    target = tmp_path / "llm-wiki-example"
    env = os.environ.copy()
    env.update(
        PATH=f"{bin_dir}:{env['PATH']}",
        CALL_LOG=str(log),
        FAIL_STAGE=fail_stage,
        RENDER_OUTCOME=render_outcome,
        FAKE_WORKSPACE=str(workspace),
        EXPECTED_REPO=REPO,
        EXPECTED_TARGET=str(target),
        WIKI_SIBLING_REGISTRY_PATH=REGISTRY,
        CLIENT_WIKI_SHORT_NAME=SHORT,
        CLIENT_WIKI_GIT_AUTHOR_NAME="Factory Author",
        CLIENT_WIKI_GIT_AUTHOR_EMAIL="factory@example.invalid",
        CLIENT_WIKI_MANIFEST_DIR=str(evidence),
        CLIENT_WIKI_REGISTRY_UPDATE_TOOL=str(bin_dir / "registry-update"),
    )
    if omit:
        env.pop(omit)
    if precondition == "manifest-missing":
        evidence.rmdir()
    elif precondition == "manifest-file":
        evidence.rmdir()
        evidence.write_text("not a directory")
    elif precondition == "manifest-symlink":
        evidence.rmdir()
        evidence.symlink_to(tmp_path)
    elif precondition == "updater-nonexec":
        (bin_dir / "registry-update").chmod(0o644)
    result = subprocess.run(
        ["bash", "-c", _workflow()], env=env, capture_output=True, text=True
    )
    calls = (
        [json.loads(line) for line in log.read_text().splitlines()]
        if log.exists()
        else []
    )
    return result, calls


def _assert_propagation(calls, tmp_path: Path) -> None:
    rendered, finalized = calls[7]["argv"], calls[8]["argv"]
    manifest = rendered[rendered.index("--manifest") + 1]
    assert finalized[finalized.index("--manifest") + 1] == manifest
    assert calls[1]["argv"][-3:] == ["validate-registry", "--registry", REGISTRY]
    assert calls[2]["argv"][-5:] == [
        "classify",
        "--registry",
        REGISTRY,
        "--short-name",
        SHORT,
    ]
    assert calls[3]["argv"] == [
        "repo",
        "create",
        REPO,
        "--private",
        "--description",
        "Private client knowledge wiki",
    ]
    assert calls[4]["argv"][-3:] == ["verify-private-repo", "--repo", REPO]
    assert calls[9]["argv"][-3:] == ["verify-private-repo", "--repo", REPO]
    for call in (calls[7], calls[8]):
        assert call["argv"][call["argv"].index("--registry") + 1] == REGISTRY
        assert call["argv"][call["argv"].index("--short-name") + 1] == SHORT
    assert calls[5]["argv"] == [
        "clone",
        f"https://github.com/{REPO}.git",
        str(tmp_path / "llm-wiki-example"),
    ]
    assert calls[6]["registry_path"] == REGISTRY


def test_complete_factory_workflow_propagates_authority_and_order(tmp_path):
    result, calls = _run(tmp_path)

    assert result.returncode == 0, result.stderr
    assert [call["stage"] for call in calls] == [
        "workspace",
        "validate-registry",
        "classify",
        "create",
        "attest-first",
        "clone",
        "checker",
        "render",
        "finalize-scaffold",
        "attest-final",
        "registry-update",
    ]
    _assert_propagation(calls, tmp_path)
    for call in calls[1:]:
        assert call["author_name"] == "Factory Author"
        assert call["author_email"] == "factory@example.invalid"
    assert calls[10]["argv"] == [
        "--registry",
        REGISTRY,
        "--short-name",
        SHORT,
        "--status",
        "bootstrapped",
        "--local-working-clone",
        str(tmp_path / "llm-wiki-example"),
    ]
    manifests = list((tmp_path / "evidence").glob("client-wiki-render.*.json"))
    assert len(manifests) == 1
    final = manifests[0]
    reported = json.loads(result.stdout.splitlines()[-1])
    backing = final.parent / reported["backing_name"]
    expected = b'{"version":1}\n'
    assert final.parent == tmp_path / "evidence"
    assert final.read_bytes() == backing.read_bytes() == expected
    assert reported["manifest"] == str(final)
    assert (final.stat().st_dev, final.stat().st_ino) == (
        backing.stat().st_dev,
        backing.stat().st_ino,
    )
    assert final.stat().st_nlink == backing.stat().st_nlink == 2
    assert final.stat().st_mode & 0o777 == backing.stat().st_mode & 0o777 == 0o600
    assert backing.exists()


@pytest.mark.parametrize(
    "precondition",
    ["manifest-missing", "manifest-file", "manifest-symlink", "updater-nonexec"],
)
def test_factory_precondition_failure_stops_before_validation(tmp_path, precondition):
    result, calls = _run(tmp_path, precondition=precondition)

    assert result.returncode != 0
    assert [call["stage"] for call in calls] == ["workspace"]


@pytest.mark.parametrize("outcome", ["absent", "empty"])
def test_render_zero_without_complete_manifest_stops_before_finalize(tmp_path, outcome):
    result, calls = _run(tmp_path, render_outcome=outcome)

    assert result.returncode != 0
    assert calls[-1]["stage"] == "render"
    assert all(call["stage"] != "registry-update" for call in calls)


@pytest.mark.parametrize(
    "stage",
    [
        "workspace",
        "validate-registry",
        "classify",
        "status",
        "create",
        "attest-first",
        "clone",
        "checker",
        "render",
        "manifest-persistence",
        "finalize-scaffold",
        "attest-final",
    ],
)
def test_every_factory_failure_suppresses_registry_update(tmp_path, stage):
    result, calls = _run(tmp_path, fail_stage=stage)

    assert result.returncode != 0
    assert all(call["stage"] != "registry-update" for call in calls)


@pytest.mark.parametrize(
    "missing",
    [
        "WIKI_SIBLING_REGISTRY_PATH",
        "CLIENT_WIKI_SHORT_NAME",
        "CLIENT_WIKI_GIT_AUTHOR_NAME",
        "CLIENT_WIKI_GIT_AUTHOR_EMAIL",
        "CLIENT_WIKI_MANIFEST_DIR",
        "CLIENT_WIKI_REGISTRY_UPDATE_TOOL",
    ],
)
def test_missing_required_environment_suppresses_all_mutation(tmp_path, missing):
    result, calls = _run(tmp_path, omit=missing)

    assert result.returncode != 0
    assert not any(
        call["stage"]
        in {"create", "clone", "render", "finalize-scaffold", "registry-update"}
        for call in calls
    )


def test_factory_has_fixed_transport_and_no_pathname_git_mutations():
    text = SKILL.read_text(encoding="utf-8")
    assert "| tee" not in text
    assert "credential.helper=!gh auth git-credential" in text
    assert "authoritative private registry" in text.lower()
    assert not re.search(r"git(?:\s+-C\s+\S+)?\s+(?:add|commit|push)\b", text)
