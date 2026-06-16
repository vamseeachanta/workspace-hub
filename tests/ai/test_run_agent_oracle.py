"""Behavioral-parity oracle for the portable `reviewer` agent (G1 / #3116).

The acceptance bar that the adversarial review demanded: NOT "all providers emit
valid JSON" (the wrappers force that anyway) but "the SAME agent definition,
materialized per provider, surfaces a KNOWN PLANTED DEFECT on every provider."

This test invokes the real Codex/Gemini CLIs and is SLOW + network/CLI-dependent,
so it is gated behind RUN_PROVIDER_ORACLE=1. The fast unit suite
(test_run_agent.py) stays fully offline.

  RUN_PROVIDER_ORACLE=1 uv run --no-project --with pytest --with pyyaml \
      python -m pytest tests/ai/test_run_agent_oracle.py -q -s
"""
from __future__ import annotations

import importlib.util
import os
import re
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

REVIEWER = REPO_ROOT / "config" / "agents" / "agent-defs" / "reviewer.agent.yaml"
DIFF = REPO_ROOT / "tests" / "ai" / "fixtures" / "planted_defect.diff"
# The planted defect: eval() / code-injection. Either token counts as "found".
DEFECT_RE = re.compile(r"\beval\b|code[- ]?(execution|injection)|arbitrary code", re.I)
VERDICT_RE = re.compile(r"\"?verdict\"?\s*[:=]\s*\"?(MAJOR|MINOR|REJECT)\b", re.I)

# submit-to-*.sh exit codes that still carry usable structured output:
#   0 = rendered + validated VALID; 6 = raw structured output present (renderer
#   not blessed, e.g. uv-render nuance). Both mean the agent RAN and produced a
#   review. NO_OUTPUT(5)/quota(3)/timeout(124)/untrusted(55) are real failures.
OUTPUT_PRESENT_EXITS = {0, 6}

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_PROVIDER_ORACLE") != "1",
    reason="set RUN_PROVIDER_ORACLE=1 to run the slow real-CLI behavioral oracle",
)


@pytest.mark.parametrize("provider", ["codex", "gemini"])
def test_provider_surfaces_planted_defect(provider):
    manifest, dispatch = module.prepare_run(REVIEWER, provider)
    assert manifest["prompt_hash"]  # same def -> same hash across providers
    run = module.dispatch_run(dispatch, str(DIFF), provider)
    print(f"\n[{provider}] exit={run['exit_code']}\n{run['stdout'][:1500]}")
    # The agent must have RUN and produced structured output (not a transport failure)...
    assert run["exit_code"] in OUTPUT_PRESENT_EXITS, (
        f"{provider} transport failure exit={run['exit_code']}: {run['stderr'][:500]}"
    )
    # ...flagged the defect (verdict >= MINOR)...
    assert VERDICT_RE.search(run["stdout"]), f"{provider} returned no MINOR/MAJOR/REJECT verdict"
    # ...and NAMED the planted eval() RCE (behavioral parity, not just schema validity).
    assert DEFECT_RE.search(run["stdout"]), f"{provider} did not surface the planted eval() defect"
