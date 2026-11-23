"""agy headless dispatch wiring tests (#3207).

Covers: agy in WRAPPERS; capability bindings flip agy from fail-closed; full
binding coverage (no future gap); the submit-to-agy.sh invocation SHAPE (agy's
prompt is --print's value, Go-duration timeout, no -p/--prompt, no trailing
positional — r1-F1/F2); the headless pre-flight. Real agy is never called —
stubbed via AGY_CMD (quota-safe).
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "ai" / "run_agent.py"
spec = importlib.util.spec_from_file_location("run_agent", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["run_agent"] = module
spec.loader.exec_module(module)

WRAPPER = REPO_ROOT / "scripts" / "review" / "submit-to-agy.sh"
PREFLIGHT = REPO_ROOT / "scripts" / "enforcement" / "check-agy-headless-capability.sh"
REVIEWER_DEF = REPO_ROOT / "config" / "agents" / "agent-defs" / "reviewer.agent.yaml"
BINDINGS = module.load_bindings()


# --- run_agent wiring -------------------------------------------------------

def test_agy_in_wrappers():
    assert "agy" in module.WRAPPERS
    assert module.WRAPPERS["agy"].name == "submit-to-agy.sh"


def test_resolve_capabilities_agy_not_unsupported():
    d = module.load_agent_def(REVIEWER_DEF)
    res = module.resolve_capabilities(d, "agy", BINDINGS)  # must not raise
    assert res["unsupported"] == []
    assert set(d["capabilities"]) <= set(res["advisory"])


def test_every_binding_has_agy():
    # r1-F3: a future capability without an agy row would silently fail-close agy.
    for cap, providers in BINDINGS.items():
        assert "agy" in providers, f"capability_bindings.{cap} missing an agy enforcement"


def test_prepare_run_agy_uses_wrapper():
    _manifest, dispatch = module.prepare_run(REVIEWER_DEF, "agy", BINDINGS, routed_skill=None)
    assert dispatch["wrapper"].endswith("submit-to-agy.sh")


# --- wrapper invocation shape (arg-recorder stub; no real agy) ---------------

def _arg_recorder(tmp_path: Path) -> tuple[Path, Path]:
    rec = tmp_path / "argv.bin"
    stub = tmp_path / "agy"
    # NUL-delimit so a multi-line prompt arg isn't split into multiple "args".
    stub.write_text(
        "#!/usr/bin/env bash\n"
        f'printf "%s\\0" "$@" > "{rec}"\n'
        'echo "STUB_AGY_OK"\n'
    )
    stub.chmod(0o755)
    return stub, rec


def test_submit_to_agy_invocation_shape(tmp_path):
    stub, rec = _arg_recorder(tmp_path)
    content = tmp_path / "diff.txt"
    content.write_text("CONTENT_MARKER_42\n")
    r = subprocess.run(
        ["bash", str(WRAPPER), "--file", str(content), "--prompt", "PROMPT_MARKER_7"],
        capture_output=True, text=True,
        env={**os.environ, "AGY_CMD": str(stub)},
    )
    assert r.returncode == 0, r.stderr
    assert "STUB_AGY_OK" in r.stdout
    args = rec.read_bytes().decode().split("\0")[:-1]  # NUL-delimited; drop trailing empty
    # r1-F1: prompt is the VALUE immediately after --print; no -p/--prompt to agy.
    assert "--print" in args
    val = args[args.index("--print") + 1]
    assert "PROMPT_MARKER_7" in val and "CONTENT_MARKER_42" in val
    assert "UNTRUSTED-CONTENT" in val  # prompt-injection boundary present (r3)
    assert "-p" not in args and "--prompt" not in args
    # r1-F2: Go-duration timeout flag present with a unit; permissions skipped.
    assert "--print-timeout" in args
    assert args[args.index("--print-timeout") + 1].endswith("s")
    assert "--dangerously-skip-permissions" in args
    # prompt must NOT be a trailing positional
    assert args[-1] != val


def test_submit_to_agy_missing_cli(tmp_path):
    content = tmp_path / "x.txt"; content.write_text("x")
    r = subprocess.run(
        ["bash", str(WRAPPER), "--file", str(content), "--prompt", "p"],
        capture_output=True, text=True,
        env={**os.environ, "AGY_CMD": str(tmp_path / "nope-not-here")},
    )
    assert r.returncode == 2
    assert "not found" in r.stderr.lower()


def test_submit_to_agy_requires_input(tmp_path):
    r = subprocess.run(["bash", str(WRAPPER), "--prompt", "p"], capture_output=True, text=True)
    assert r.returncode != 0


# --- headless pre-flight ----------------------------------------------------

def _fake_agy(tmp_path: Path, help_text: str) -> Path:
    stub = tmp_path / "agy"
    stub.write_text("#!/usr/bin/env bash\n"
                    'if [[ "$1" == "--help" ]]; then cat <<EOF\n' + help_text + "\nEOF\nfi\n")
    stub.chmod(0o755)
    return stub


def test_preflight_detects_print(tmp_path):
    stub = _fake_agy(tmp_path, "Flags:\n  -p          alias\n  --print     Run a single prompt non-interactively")
    r = subprocess.run(["bash", str(PREFLIGHT)], capture_output=True, text=True,
                       env={**os.environ, "AGY_CMD": str(stub)})
    assert r.returncode == 0


def test_preflight_rejects_when_no_print(tmp_path):
    # only a description mention of --print, not a real flag column -> must reject
    stub = _fake_agy(tmp_path, "Flags:\n  --interactive   start a session (see --print docs elsewhere)")
    r = subprocess.run(["bash", str(PREFLIGHT)], capture_output=True, text=True,
                       env={**os.environ, "AGY_CMD": str(stub)})
    assert r.returncode == 1


def test_preflight_absent_agy_is_not_failure(tmp_path):
    r = subprocess.run(["bash", str(PREFLIGHT)], capture_output=True, text=True,
                       env={**os.environ, "AGY_CMD": str(tmp_path / "absent")})
    assert r.returncode == 0
