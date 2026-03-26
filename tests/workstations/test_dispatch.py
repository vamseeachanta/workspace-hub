"""Tests for workstation dispatch scoring logic.

Reimplements the scoring algorithm from scripts/operations/workstation-dispatch.sh
in Python and validates it against the live registry.yaml.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = REPO_ROOT / "config" / "workstations" / "registry.yaml"
DISPATCH_SCRIPT = REPO_ROOT / "scripts" / "operations" / "workstation-dispatch.sh"


# ── Registry loader ──────────────────────────────────────────────────────────

def load_registry() -> dict:
    """Load and return the machines dict from registry.yaml."""
    with open(REGISTRY_PATH) as f:
        return yaml.safe_load(f).get("machines", {})


# ── Scoring logic (faithful reimplementation of the shell script) ────────────

def get_caps(machine: dict) -> set[str]:
    """Flatten a machine's capabilities into a single set.

    Rules (from workstation-dispatch.sh lines 109-119):
    - Merge agent_clis + languages + tools
    - If gpu is truthy and not literally True, add the gpu string value
    - If gpu is truthy at all, also add the literal "gpu"
    """
    caps: set[str] = set()
    c = machine.get("capabilities", {})
    for key in ("agent_clis", "languages", "tools"):
        caps.update(c.get(key) or [])
    gpu = c.get("gpu")
    if gpu and gpu is not True:
        caps.add(str(gpu))
    if gpu:
        caps.add("gpu")
    return caps


def select_machine(
    registry: dict,
    required: set[str],
    this_host: str,
    prefer: str = "",
) -> list[tuple[int, str, bool, Optional[str]]]:
    """Score and rank machines. Returns sorted candidates list.

    Each entry: (score, machine_name, is_local, ssh_target).
    Highest score first. Empty list means no match.

    Scoring (from workstation-dispatch.sh lines 133-139):
      prefer match = +100
      is_local     = +10
      excess caps  = -1 per extra capability (tighter fit wins)

    Filtering:
      - Machine must have SSH or be local
      - Machine must have all required capabilities
    """
    candidates: list[tuple[int, str, bool, Optional[str]]] = []
    for name, m in registry.items():
        ssh = m.get("ssh")
        hostnames = [m["hostname"]] + (m.get("hostname_aliases") or [])
        is_local = this_host in [h.lower() for h in hostnames]

        # Must have SSH or be local
        if not ssh and not is_local:
            continue

        # Must satisfy all requirements
        caps = get_caps(m)
        if not required.issubset(caps):
            continue

        # Score
        score = 0
        if name == prefer:
            score += 100
        if is_local:
            score += 10
        score -= len(caps - required)  # tighter fit is better

        candidates.append((score, name, is_local, ssh))

    candidates.sort(key=lambda x: -x[0])
    return candidates


def best_machine(
    registry: dict,
    required: set[str],
    this_host: str,
    prefer: str = "",
) -> Optional[str]:
    """Return the name of the best-fit machine, or None if no match."""
    candidates = select_machine(registry, required, this_host, prefer)
    return candidates[0][1] if candidates else None


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def registry() -> dict:
    return load_registry()


# ── Scoring tests ────────────────────────────────────────────────────────────

class TestScoringLogic:
    """Unit tests for the dispatch scoring algorithm."""

    def test_prefer_overrides_local(self, registry: dict) -> None:
        """A task with prefer=dev-primary selects dev-primary even when
        running on dev-secondary (which would otherwise get the local bonus)."""
        result = best_machine(
            registry,
            required={"python3", "uv", "git"},
            this_host="ace-linux-2",  # dev-secondary is local
            prefer="dev-primary",
        )
        assert result == "dev-primary"

    def test_local_preferred_when_no_prefer(self, registry: dict) -> None:
        """Without a prefer hint, the local machine wins if it has the capabilities."""
        result = best_machine(
            registry,
            required={"python3", "bash"},
            this_host="ace-linux-2",  # dev-secondary is local
            prefer="",
        )
        assert result == "dev-secondary"

    def test_tighter_fit_breaks_ties(self, registry: dict) -> None:
        """Between two remote machines with the same base score, the one with
        fewer excess capabilities (tighter fit) wins."""
        # Simulate from a host that is neither dev-primary nor dev-secondary
        # so both are remote (no local bonus). No prefer hint either.
        # Both have python3 + bash. dev-primary has fewer total caps than
        # dev-secondary (which has blender, openfoam, etc.), so dev-primary
        # should win on tighter fit.
        candidates = select_machine(
            registry,
            required={"python3", "bash"},
            this_host="nonexistent-host",
            prefer="",
        )
        # Filter to just the two linux machines that have SSH
        linux_candidates = [c for c in candidates if c[1] in ("dev-primary", "dev-secondary")]
        assert len(linux_candidates) == 2
        # dev-primary should rank higher (fewer excess caps)
        names = [c[1] for c in linux_candidates]
        assert names[0] == "dev-primary", (
            f"Expected dev-primary to rank first (tighter fit) but got {names}"
        )

    def test_missing_capability_excludes_machine(self, registry: dict) -> None:
        """A machine missing a required capability is never selected."""
        candidates = select_machine(
            registry,
            required={"python3", "orcaflex"},
            this_host="nonexistent-host",
            prefer="",
        )
        selected_names = {c[1] for c in candidates}
        # dev-primary and dev-secondary don't have orcaflex
        assert "dev-primary" not in selected_names
        assert "dev-secondary" not in selected_names

    def test_no_ssh_excludes_non_local(self, registry: dict) -> None:
        """Machines with ssh=null are excluded unless they are the local machine."""
        # licensed-win-1 has no SSH; running from a non-local host should exclude it
        candidates = select_machine(
            registry,
            required={"bash"},
            this_host="nonexistent-host",
            prefer="",
        )
        selected_names = {c[1] for c in candidates}
        assert "licensed-win-1" not in selected_names
        assert "licensed-win-2" not in selected_names

        # But if we ARE on licensed-win-1, it should be included
        candidates_local = select_machine(
            registry,
            required={"bash"},
            this_host="licensed-win-1",
            prefer="",
        )
        selected_names_local = {c[1] for c in candidates_local}
        assert "licensed-win-1" in selected_names_local

    def test_claude_gemini_requires_selects_dev_primary(self, registry: dict) -> None:
        """Requiring [claude, gemini] should only match dev-primary among
        SSH-reachable machines (dev-secondary has only claude, not gemini)."""
        candidates = select_machine(
            registry,
            required={"claude", "gemini"},
            this_host="nonexistent-host",
            prefer="",
        )
        selected_names = {c[1] for c in candidates}
        assert "dev-primary" in selected_names
        # dev-secondary has claude but not gemini
        assert "dev-secondary" not in selected_names

    def test_gpu_capability_detection(self, registry: dict) -> None:
        """A machine with gpu='nvidia-t400' should match both requires=[gpu]
        and requires=[nvidia-t400]."""
        caps = get_caps(registry["dev-secondary"])
        assert "gpu" in caps, "Generic 'gpu' token should be in capabilities"
        assert "nvidia-t400" in caps, "Specific GPU string should be in capabilities"

        # Machine with gpu=false should have neither
        caps_no_gpu = get_caps(registry["dev-primary"])
        assert "gpu" not in caps_no_gpu
        assert "nvidia-t400" not in caps_no_gpu

        # Dispatch with requires=[gpu] should select dev-secondary (SSH-reachable)
        result = best_machine(
            registry,
            required={"gpu"},
            this_host="nonexistent-host",
            prefer="",
        )
        assert result == "dev-secondary"

    def test_no_match_returns_empty(self, registry: dict) -> None:
        """Requiring [orcaflex] from SSH-reachable machines returns no candidates
        (Windows machines have orcaflex but no SSH)."""
        candidates = select_machine(
            registry,
            required={"orcaflex"},
            this_host="nonexistent-host",
            prefer="",
        )
        assert candidates == [], f"Expected no candidates but got {candidates}"


# ── Dispatch dry-run tests (subprocess) ──────────────────────────────────────

class TestDispatchDryRun:
    """Integration tests that invoke workstation-dispatch.sh --dry-run."""

    @pytest.fixture(autouse=True)
    def _skip_if_no_script(self) -> None:
        if not DISPATCH_SCRIPT.exists():
            pytest.skip(f"Dispatch script not found at {DISPATCH_SCRIPT}")

    @pytest.fixture(autouse=True)
    def _skip_if_no_uv(self) -> None:
        result = subprocess.run(
            ["which", "uv"], capture_output=True, text=True
        )
        if result.returncode != 0:
            pytest.skip("uv not available on PATH")

    def test_dispatch_dry_run_task(self) -> None:
        """Run workstation-dispatch.sh --task benchmark-regression --dry-run.
        Should exit 0 and mention dev-primary or dev-secondary."""
        result = subprocess.run(
            ["bash", str(DISPATCH_SCRIPT), "--task", "benchmark-regression", "--dry-run"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(REPO_ROOT),
        )
        assert result.returncode == 0, (
            f"Expected exit 0 but got {result.returncode}\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        output = result.stdout + result.stderr
        assert "dev-primary" in output or "dev-secondary" in output, (
            f"Expected dev-primary or dev-secondary in output:\n{output}"
        )

    def test_dispatch_dry_run_requires(self) -> None:
        """Run workstation-dispatch.sh --requires claude,gemini --command 'test' --dry-run.
        Should select dev-primary (only SSH-reachable machine with both)."""
        result = subprocess.run(
            [
                "bash", str(DISPATCH_SCRIPT),
                "--requires", "claude,gemini",
                "--command", "echo test",
                "--dry-run",
            ],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(REPO_ROOT),
        )
        assert result.returncode == 0, (
            f"Expected exit 0 but got {result.returncode}\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        output = result.stdout + result.stderr
        assert "dev-primary" in output, (
            f"Expected dev-primary in output:\n{output}"
        )
