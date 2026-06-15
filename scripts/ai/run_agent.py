#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Portable bounded-worker agent runner (G1 / #3116).

Define a worker ONCE in config/agents/agent-defs/<name>.agent.yaml, then invoke it
on Claude / Codex / Gemini through the existing review wrappers. The portable
unit (the .agent.yaml) is decoupled from the runtime (the harness) — the
Omnigent "define once, materialize per harness" pattern applied to agents.

Capability enforcement is harness-dependent and EXPLICIT (no false abstraction):
  - ENFORCED   : Claude Code subagent accepts a tools: allowlist -> native tools.
  - ADVISORY   : Codex/Gemini are monolithic CLIs -> capability is a prompt
                 preamble, NOT a sandbox.
  - UNSUPPORTED: harness cannot provide it -> FAIL CLOSED before dispatch.

Bindings live in config/agents/provider-capabilities.yaml -> capability_bindings
(single source of truth; no parallel capability-map.yaml).

This module is a pure resolver + thin dispatch wrapper. It deliberately does NOT
re-implement provider quirks — dispatch reuses scripts/review/submit-to-*.sh,
which already carry the per-provider guards (Codex CLAUDECODE stdin-hang #2684,
Gemini workspace-trust, quota fallback, output validation).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CAPS_PATH = REPO_ROOT / "config" / "agents" / "provider-capabilities.yaml"
AGENT_DEFS_DIR = REPO_ROOT / "config" / "agents" / "agent-defs"

# Non-Claude providers dispatch through the existing review wrappers.
WRAPPERS = {
    "codex": REPO_ROOT / "scripts" / "review" / "submit-to-codex.sh",
    "gemini": REPO_ROOT / "scripts" / "review" / "submit-to-gemini.sh",
    "claude": Path("<claude-subagent>"),  # materialized as a Claude subagent, not a wrapper
}


class UnsupportedCapabilityError(RuntimeError):
    """A requested capability is `unsupported` on the target provider.

    Raised BEFORE any dispatch so an agent never runs on a harness that cannot
    honor its declared capabilities (the plan's mandated fail-closed guard).
    """


# --- loading ----------------------------------------------------------------

def load_agent_def(path: Path | str) -> dict:
    """Load a portable *.agent.yaml definition (by path or bare name)."""
    p = Path(path)
    if not p.exists() and "/" not in str(path) and not str(path).endswith(".yaml"):
        p = AGENT_DEFS_DIR / f"{path}.agent.yaml"
    with open(p, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    for field in ("name", "role", "prompt", "capabilities"):
        if field not in data:
            raise ValueError(f"{p}: agent def missing required field {field!r}")
    if data["role"] != "worker":
        raise ValueError(f"{p}: G1 supports role: worker only (got {data['role']!r})")
    return data


def load_bindings(path: Path | str = DEFAULT_CAPS_PATH) -> dict:
    """Load capability_bindings from provider-capabilities.yaml (source of truth)."""
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    bindings = data.get("capability_bindings")
    if not bindings:
        raise ValueError(f"{path}: no capability_bindings block")
    return bindings


# --- resolution (fail-closed) ----------------------------------------------

def resolve_capabilities(agent_def: dict, provider: str, bindings: dict) -> dict:
    """Classify each declared capability for `provider`.

    Returns {enforced, advisory, unsupported, native}. Raises
    UnsupportedCapabilityError if ANY capability is unsupported on the provider
    (fail closed — never partially dispatch).
    """
    enforced, advisory, unsupported, native = [], [], [], {}
    for cap in agent_def["capabilities"]:
        if cap not in bindings:
            # referential integrity: unknown capability is a hard error
            raise ValueError(
                f"capability {cap!r} not in capability_bindings — fix the def or bindings"
            )
        entry = bindings[cap].get(provider)
        enf = entry.get("enforcement") if isinstance(entry, dict) else None
        if enf == "enforced":
            enforced.append(cap)
            native[cap] = entry.get("native", [])
        elif enf == "advisory":
            advisory.append(cap)
        else:  # missing provider key or explicit "unsupported"
            unsupported.append(cap)
    if unsupported:
        raise UnsupportedCapabilityError(
            f"agent {agent_def['name']!r} needs {unsupported} which are unsupported on "
            f"{provider!r} — refusing to dispatch"
        )
    return {"enforced": enforced, "advisory": advisory, "unsupported": unsupported, "native": native}


# --- manifest + materialization ---------------------------------------------

def _prompt_hash(agent_def: dict) -> str:
    return hashlib.sha256(agent_def["prompt"].encode("utf-8")).hexdigest()


def build_manifest(agent_def: dict, provider: str, bindings: dict) -> dict:
    """Auditable run manifest (emitted per invocation)."""
    res = resolve_capabilities(agent_def, provider, bindings)
    enforcement = {
        cap: bindings[cap][provider]["enforcement"] for cap in agent_def["capabilities"]
    }
    return {
        "agent": agent_def["name"],
        "provider": provider,
        "prompt_hash": _prompt_hash(agent_def),
        "enforcement": enforcement,
        "enforced": res["enforced"],
        "advisory": res["advisory"],
        "unsupported": res["unsupported"],  # always [] here (else we raised)
        "native_tools": res["native"],
        "wrapper": str(WRAPPERS[provider]),
        "output_contract": agent_def.get("output_contract"),
    }


def materialize_prompt(agent_def: dict, provider: str, res: dict) -> str:
    """Render the provider prompt: identity-ref + advisory caps + agent prompt.

    Ordering preserves the untrusted-content boundary: shared identity -> agent
    prompt -> (caller appends user task + untrusted content via the wrapper).
    """
    lines = []
    if res["advisory"]:
        lines.append(
            "# Advisory capabilities (this CLI cannot be sandboxed): "
            + ", ".join(res["advisory"])
        )
    if res["enforced"]:
        lines.append("# Enforced capabilities: " + ", ".join(res["enforced"]))
    lines.append(agent_def["prompt"].rstrip())
    return "\n".join(lines) + "\n"


def prepare_run(agent_def_path: Path | str, provider: str, bindings: dict | None = None):
    """Resolve + manifest + materialize. FAILS CLOSED before returning dispatch."""
    agent_def = load_agent_def(agent_def_path)
    if bindings is None:
        bindings = load_bindings()
    res = resolve_capabilities(agent_def, provider, bindings)  # raises on unsupported
    manifest = build_manifest(agent_def, provider, bindings)
    dispatch = {
        "wrapper": str(WRAPPERS[provider]),
        "prompt": materialize_prompt(agent_def, provider, res),
    }
    return manifest, dispatch


# --- dispatch (integration; reuses the existing wrappers) -------------------

def dispatch_run(dispatch: dict, content_file: str, provider: str) -> dict:
    """Invoke the provider wrapper. Reuses submit-to-*.sh per-provider guards."""
    import os

    wrapper = dispatch["wrapper"]
    cmd = ["bash", wrapper, "--file", content_file, "--prompt", dispatch["prompt"]]
    env = dict(os.environ)
    if provider == "codex":
        env.pop("CLAUDECODE", None)  # #2684 stdin-hang
    elif provider == "gemini":
        env["GEMINI_CLI_TRUST_WORKSPACE"] = "true"
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return {"exit_code": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run a portable worker agent on a provider.")
    ap.add_argument("--agent", required=True, help="agent name or path to *.agent.yaml")
    ap.add_argument("--provider", required=True, choices=sorted(WRAPPERS))
    ap.add_argument("--file", help="content/diff file under review (enables dispatch)")
    ap.add_argument("--execute", action="store_true", help="actually invoke the wrapper")
    args = ap.parse_args(argv)
    try:
        manifest, dispatch = prepare_run(args.agent, args.provider)
    except UnsupportedCapabilityError as e:
        print(json.dumps({"status": "fail-closed", "reason": str(e)}), file=sys.stderr)
        return 2
    out = {"manifest": manifest}
    if args.execute and args.file:
        out["run"] = dispatch_run(dispatch, args.file, args.provider)
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
