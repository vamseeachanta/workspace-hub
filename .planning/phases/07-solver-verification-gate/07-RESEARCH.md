# Phase 7: Solver Verification Gate - Research

**Researched:** 2026-03-30
**Domain:** Cross-machine solver verification, remote Claude Code execution, license boundary enforcement
**Confidence:** HIGH

## Summary

Phase 7 is a go/no-go gate, not a development phase. It verifies three things before any v1.1 development proceeds: (1) OrcFxAPI loads, solves, and exports on licensed-win-1, (2) remote Claude Code execution works from dev-primary to licensed-win-1, and (3) the codebase enforces a clean solver/non-solver module boundary. This phase directly addresses the WRK-031 stall -- a complete diffraction framework was built on Linux that could not execute on Windows because solver verification was deferred.

The codebase already has four files that directly import OrcFxAPI: `orcawave_converter.py`, `orcawave_data_extraction.py`, and the `orcawave/reporting/builder.py` (plus its sections which receive the OrcFxAPI object as a parameter). All other code -- input schemas, spec conversion, runners, validators, exporters, batch orchestration -- is license-free. The module separation (D-12, D-13) involves moving these OrcFxAPI-dependent files into a dedicated subpackage (e.g., `diffraction/solver/`) so that the import boundary is enforced by package structure rather than runtime try/except guards. The `result_extractor.py` already demonstrates the pattern: conditional import of `OrcaWaveConverter` with a `CONVERTER_AVAILABLE` flag.

Remote execution from dev-primary to licensed-win-1 is the foundational architecture for the entire v1.1 milestone. The recommended approach is SSH + `claude -p` (headless mode). This requires: (1) enabling OpenSSH Server on licensed-win-1 (Windows 11 has it built-in), (2) SSH key authentication from dev-primary, and (3) invoking Claude Code in non-interactive mode with `claude -p "prompt" --allowedTools "Bash,Read,Edit"`. This pattern gives dev-primary the ability to dispatch solver tasks to licensed-win-1 programmatically.

**Primary recommendation:** Verify OrcFxAPI on licensed-win-1 first, establish SSH + Claude Code headless remote execution second, then refactor the module boundary third. All three must pass before Phase 7 is complete.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Three-machine architecture: licensed-win-1 (acma-ansys05, OrcaFlex/OrcaWave license), win-2 (ws014, backup/overflow), dev-primary (Linux, orchestration/processing)
- **D-02:** dev-primary is the primary processing machine for all non-license work. win-2 is backup/overflow only -- not part of the primary pipeline
- **D-03:** Direct network path exists between licensed-win-1 and win-2
- **D-04:** Git push through all three machines -- licensed-win-1 commits and pushes solver results (.owr + Excel), dev-primary and win-2 pull. Versioned and traceable
- **D-05:** Smoke test artifacts (L00 + L01 .owr and Excel) committed to digitalmodel repo as permanent test fixtures for downstream phases
- **D-06:** Claude Code on licensed-win-1 as the solver execution agent, triggered remotely from dev-primary
- **D-07:** Remote CC trigger from dev-primary is a HARD REQUIREMENT for Phase 7 -- block until it works. Not a nice-to-have
- **D-08:** Phase 7 has two verification gates: (1) OrcFxAPI functional on licensed-win-1, (2) remote CC trigger from dev-primary to licensed-win-1
- **D-09:** Run L00 (simplest) and L01 (moderate) benchmark cases through solver, producing reference .owr + Excel artifacts
- **D-10:** Binary pass/fail criteria: OrcFxAPI imports, loads .owd, runs calculation, extracts at least one result set = pass. No physics sanity checks at this gate
- **D-11:** Artifacts committed to digitalmodel repo as permanent test fixtures for later phases to consume without solver access
- **D-12:** Separate entry points pattern -- solver-dependent code in its own subpackage (e.g., `diffraction/solver/`), everything outside is license-free. No conditional `try/except import` hacks
- **D-13:** Phase 7 enforces this separation now (refactor), not just verifies it's possible. Clean boundary before development phases begin
- **D-14:** uv already installed on licensed-win-1 -- verify `uv sync` works with OrcFxAPI wheel compatibility as primary concern
- **D-15:** Python version follows OrcFxAPI compatibility requirements (currently supports 3.9-3.14). Align all machines to the highest version OrcFxAPI supports
- **D-16:** Create `@pytest.mark.solver` marker for tests requiring OrcFxAPI. CI skips solver-marked tests on Linux
- **D-17:** pytest fixtures providing .owr/.xlsx reference data so solver-free tests can use real results without needing OrcFxAPI installed

### Claude's Discretion
- Remote CC trigger mechanism (SSH + CC, native remote dispatch, or other approach)
- Exact subpackage structure for solver-dependent code separation
- Python version selection within OrcFxAPI's supported range

### Deferred Ideas (OUT OF SCOPE)
None -- discussion stayed within phase scope
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| INFRA-01 | All spec generation, report rendering, sensitivity planning, correctness gates, and dashboard generation runs license-free on any machine | Module separation research (D-12/D-13) identifies exactly which files need OrcFxAPI and which are already license-free. Subpackage boundary enforces this at import level. |
| INFRA-02 | Only solver execution and result export requires licensed machine (licensed-win-1); results portable via .owr + Excel | Smoke test verification (D-09/D-10) proves this on actual hardware. Git-based result transfer (D-04) provides portability mechanism. |
</phase_requirements>

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| OrcFxAPI | 11.6.2 | OrcaWave/OrcaFlex Python API -- solver execution, result extraction | Only API for OrcaWave automation. py3-none-any wheel, requires OrcFxAPI DLL from OrcaFlex installation |
| pytest | 7.4+ (existing) | Test framework, markers, fixtures | Already configured in digitalmodel with strict-markers |
| uv | 0.6+ (existing on licensed-win-1) | Python environment and dependency management | Already installed on all three machines per manifest |
| Claude Code CLI | latest | Non-interactive solver execution agent on licensed-win-1 | `claude -p` headless mode for programmatic dispatch from dev-primary |
| OpenSSH Server | built-in Windows 11 | SSH access to licensed-win-1 from dev-primary | Built into Windows 11 Pro, no third-party software needed |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| openpyxl | 3.1+ (existing) | Excel export of solver results | During smoke test to produce .xlsx artifacts alongside .owr |
| numpy | <2.0.0 (existing) | Array handling for result extraction | Already a dependency, used by OrcFxAPI result properties |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| SSH + Claude Code | Tailscale + Claude Code | Tailscale pending setup on licensed-win-1 (action item); SSH is built-in and ready now |
| SSH + Claude Code | Manual RDP + local CC | User explicitly rejected this -- remote trigger is a hard requirement (D-07) |
| OpenSSH Server | PuTTY/WinSCP | Non-standard on Windows 11; OpenSSH is the native solution |

**Installation (on licensed-win-1):**
```powershell
# Enable OpenSSH Server (run as Administrator)
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'
New-NetFirewallRule -Name 'OpenSSH-Server' -DisplayName 'OpenSSH Server' -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22

# Verify uv and Python
uv --version
uv python list
uv sync
```

**Version verification:** OrcFxAPI 11.6.2 confirmed on PyPI (released 2026-02-23). py3-none-any wheel (54.6 kB). Requires Python >=3.9, supports up to 3.14 per Orcina docs. No source distribution -- wheel only.

## Architecture Patterns

### Recommended Project Structure (after refactoring)

```
src/digitalmodel/hydrodynamics/diffraction/
  __init__.py
  input_schemas.py         # License-free (DiffractionSpec, Pydantic)
  output_schemas.py        # License-free (DiffractionResults)
  spec_converter.py        # License-free
  orcawave_backend.py      # License-free (spec -> YAML)
  orcawave_runner.py       # License-free (invokes orcawave.exe, dry-run capable)
  orcawave_batch_runner.py # License-free (orchestration)
  output_validator.py      # License-free (physics validation on results)
  result_extractor.py      # License-free (bridge layer, conditionally imports solver/)
  comparison_framework.py  # License-free
  ...

  solver/                  # NEW: License-required subpackage
    __init__.py            # Imports OrcFxAPI at package level -- fails clearly if not available
    orcawave_converter.py  # MOVED from parent (OrcFxAPI.Diffraction -> DiffractionResults)
    data_extraction.py     # MOVED from parent (OrcFxAPI property access)
    smoke_test.py          # NEW: Binary go/no-go test script

src/digitalmodel/orcawave/reporting/
  builder.py               # Uses solver/ for _load_diffraction() -- already has lazy import
  sections/                # License-free if they receive pre-extracted data; currently receive raw OrcFxAPI object
```

### Pattern 1: Subpackage Boundary for License Isolation

**What:** Move all files that `import OrcFxAPI` into a `solver/` subpackage. The subpackage's `__init__.py` imports OrcFxAPI at the top level, providing a single clear failure point.

**When to use:** Any code that directly calls OrcFxAPI methods or accesses OrcFxAPI objects.

**Current state -- files that import OrcFxAPI (in src/digitalmodel/):**
1. `hydrodynamics/diffraction/orcawave_converter.py` -- `import OrcFxAPI` in try/except
2. `hydrodynamics/diffraction/orcawave_data_extraction.py` -- `import OrcFxAPI` in try/except
3. `orcawave/reporting/builder.py` -- `import OrcFxAPI` inside `_load_diffraction()` method

**Files that do NOT import OrcFxAPI but receive OrcFxAPI objects:**
4. `orcawave/reporting/sections/model_summary.py` -- receives `diff: OrcFxAPI.Diffraction` param
5. `orcawave/reporting/sections/rao_plots.py` -- receives `diff: OrcFxAPI.Diffraction` param
6. All other section modules in `orcawave/reporting/sections/`

**Refactoring approach:**
```python
# solver/__init__.py -- clean failure point
import OrcFxAPI  # Fails immediately if DLL not available

from .orcawave_converter import OrcaWaveConverter
from .data_extraction import OrcaWaveDataExtractor

__all__ = ["OrcFxAPI", "OrcaWaveConverter", "OrcaWaveDataExtractor"]
```

```python
# result_extractor.py -- conditional import (existing pattern, adjust path)
try:
    from digitalmodel.hydrodynamics.diffraction.solver import OrcaWaveConverter
    CONVERTER_AVAILABLE = True
except ImportError:
    OrcaWaveConverter = None
    CONVERTER_AVAILABLE = False
```

### Pattern 2: Remote Claude Code Execution via SSH

**What:** dev-primary dispatches solver tasks to licensed-win-1 by SSH-ing in and running `claude -p` in headless mode.

**When to use:** Any task that requires OrcFxAPI execution (solver runs, result extraction from .owr files).

**Example dispatch from dev-primary:**
```bash
# One-shot solver verification from dev-primary
ssh user@licensed-win-1 'cd D:\workspace-hub\digitalmodel && claude -p "Run the OrcFxAPI smoke test: import OrcFxAPI, load test01.owd from L00, calculate, extract one result set. Report pass/fail." --allowedTools "Bash,Read"'
```

**Example structured output:**
```bash
# Get structured pass/fail result
ssh user@licensed-win-1 'cd D:\workspace-hub\digitalmodel && claude -p "Run the solver smoke test script at tests/solver/smoke_test.py and report the result" --allowedTools "Bash,Read" --output-format json' | jq -r '.result'
```

**Key flags:**
- `-p` / `--print`: Non-interactive mode, single prompt execution
- `--allowedTools "Bash,Read,Edit"`: Auto-approve tools without prompting
- `--output-format json`: Structured output with session ID and metadata
- `--bare`: Skip auto-discovery for faster startup (optional, good for scripts)
- `--continue` / `--resume`: Multi-step conversations if needed

### Pattern 3: Git-Based Result Transfer

**What:** Solver results committed on licensed-win-1, pushed to origin, pulled by dev-primary and win-2.

**When to use:** After any solver execution that produces artifacts (.owr, .xlsx).

**Example flow:**
```bash
# On licensed-win-1 (via remote CC or SSH):
cd D:\workspace-hub\digitalmodel
git add tests/fixtures/solver/L00_test01.owr tests/fixtures/solver/L00_test01.xlsx
git commit -m "feat(solver): add L00 smoke test reference artifacts"
git push origin main

# On dev-primary:
git pull origin main
# Artifacts now available for license-free test consumption
```

### Anti-Patterns to Avoid

- **try/except at module level with HAS_ORCFX flag:** D-12 explicitly rejects this. Instead, use subpackage boundary. If code needs OrcFxAPI, it imports from `solver/` subpackage and that import either succeeds or fails cleanly.
- **Mocking OrcFxAPI with sys.modules injection:** The existing pattern (`sys.modules['OrcFxAPI'] = MockOrcFxAPI()`) is fragile. For Phase 7 tests, use real artifacts (.owr/.xlsx fixtures) consumed by license-free code, not mock API objects.
- **Running solver tasks on dev-primary:** OrcFxAPI requires Windows DLLs. Never attempt to import or execute on Linux.
- **Hardcoded absolute paths in test fixtures:** Use `Path(__file__).parent / "fixtures"` pattern (already established in conftest.py).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| SSH to Windows | Custom SSH client wrapper | OpenSSH built into Windows 11 | Native, supported, already proven. `Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0` |
| Remote task execution | Custom RPC/API server | `claude -p` headless mode over SSH | Already designed for programmatic execution, handles tool approval, returns structured output |
| Python environment | Manual pip install + venv | `uv sync` | Already installed on licensed-win-1, handles cross-platform wheel resolution |
| Result transfer | SCP/rsync scripts | `git push` / `git pull` | Versioned, traceable, works with existing workflow. D-04 locks this decision |
| License check | Custom license verification | `OrcFxAPI.DLLVersion()` | Built-in function returns version string if licensed, throws if not |

**Key insight:** The entire remote execution infrastructure uses existing tools (SSH, Claude Code CLI, git, uv). Nothing custom needs to be built -- only configured and verified.

## Common Pitfalls

### Pitfall 1: OrcFxAPI Wheel vs. DLL Confusion

**What goes wrong:** `pip install OrcFxAPI` (or `uv add OrcFxAPI`) installs the Python wrapper (54.6 kB py3-none-any wheel) but NOT the OrcFxAPI DLL. The DLL comes from OrcaFlex installation. Without the DLL, `import OrcFxAPI` succeeds but `OrcFxAPI.Model()` or `OrcFxAPI.Diffraction()` throws a DLL loading error.
**Why it happens:** The PyPI wheel is a pure-Python wrapper that delegates to the native DLL. OrcaFlex must be installed separately.
**How to avoid:** Verify the full chain: (1) `import OrcFxAPI` succeeds, (2) `OrcFxAPI.DLLVersion()` returns a version string, (3) `OrcFxAPI.Diffraction()` constructor succeeds. All three must pass.
**Warning signs:** `import OrcFxAPI` works but any actual API call throws `DLLError` or `OSError`.

### Pitfall 2: OpenSSH Default Shell on Windows

**What goes wrong:** Windows OpenSSH defaults to `cmd.exe` as the login shell. Claude Code expects a POSIX-like shell or PowerShell. Commands sent via SSH may fail due to shell differences.
**Why it happens:** OpenSSH Server on Windows uses cmd.exe unless explicitly configured to use PowerShell or Git Bash.
**How to avoid:** Configure the default shell to PowerShell:
```powershell
New-ItemProperty -Path "HKLM:\SOFTWARE\OpenSSH" -Name DefaultShell -Value "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -PropertyType String -Force
```
Or for Git Bash (MINGW64, already installed per manifest):
```powershell
New-ItemProperty -Path "HKLM:\SOFTWARE\OpenSSH" -Name DefaultShell -Value "C:\Program Files\Git\bin\bash.exe" -PropertyType String -Force
```
**Warning signs:** SSH connection works but commands fail with "is not recognized as an internal or external command."

### Pitfall 3: uv sync TLS Certificate Issue on Windows

**What goes wrong:** uv 0.11.0+ uses `rustls-platform-verifier` for TLS, which may fail on Windows machines behind corporate proxies or with non-standard certificate chains. `uv sync` fails with TLS/SSL errors.
**Why it happens:** Research synthesis (2026-03-29) flagged this as a specific risk for licensed-win-1.
**How to avoid:** Test `uv sync` on licensed-win-1 before depending on it. If TLS fails, set `UV_NATIVE_TLS=1` to use the OS native TLS stack, or configure proxy certificates.
**Warning signs:** `uv sync` fails with "certificate verify failed" or "unable to get local issuer certificate."

### Pitfall 4: OrcaWave .owd vs .owr File Confusion

**What goes wrong:** The smoke test needs `.owd` (input) files to load and solve, producing `.owr` (result) files. Loading an `.owr` file with `Diffraction()` constructor works but gives you a results-only model that cannot re-calculate.
**Why it happens:** Both file types are OrcaWave data files. The `.owd` is the input model, `.owr` is the output results.
**How to avoid:** For smoke test: load `.owd` -> `Calculate()` -> save as `.owr`. For result extraction: load `.owr` directly.
**Warning signs:** "Cannot calculate" errors when trying to run a calculation on an `.owr` file.

### Pitfall 5: Git Line Endings Cross-Platform

**What goes wrong:** Git on Windows may auto-convert line endings (CRLF/LF), causing diffs in YAML files or scripts committed from licensed-win-1 that show as "changed" on dev-primary.
**Why it happens:** Default `core.autocrlf` differs between Windows (true) and Linux (input/false).
**How to avoid:** Ensure `.gitattributes` in digitalmodel repo specifies `* text=auto` and `*.yml text eol=lf`. Verify git config on licensed-win-1.
**Warning signs:** Unexpected diffs showing only whitespace/line-ending changes after pulling from licensed-win-1.

### Pitfall 6: Claude Code Not Installed on licensed-win-1

**What goes wrong:** SSH works, but `claude` command not found on licensed-win-1.
**Why it happens:** The manifest shows `claude: ">=1.0"` in `agent_clis` for licensed-win-1, but this is the desired state, not necessarily the current state. The manifest also has no OrcaFlex installed (per notes).
**How to avoid:** First task of Phase 7 must verify: `claude --version` works on licensed-win-1. If not, install it (npm/brew/standalone installer).
**Warning signs:** `command not found: claude` over SSH.

## Code Examples

### Smoke Test Script (for licensed-win-1)

```python
# tests/solver/smoke_test.py
"""Binary pass/fail OrcFxAPI smoke test for licensed-win-1.

Run: python tests/solver/smoke_test.py
Pass criteria: OrcFxAPI imports, DLL loads, .owd loads, calculates, extracts result.
"""
import sys
from pathlib import Path

def smoke_test() -> bool:
    """Return True if OrcFxAPI is fully functional."""
    # Step 1: Import
    try:
        import OrcFxAPI
    except ImportError:
        print("FAIL: Cannot import OrcFxAPI")
        return False

    # Step 2: DLL version
    try:
        version = OrcFxAPI.DLLVersion()
        print(f"OK: OrcFxAPI DLL version: {version}")
    except Exception as e:
        print(f"FAIL: DLL not loaded: {e}")
        return False

    # Step 3: Load .owd
    owd_path = Path(__file__).parent.parent.parent / "docs/domains/orcawave/L00_validation_wamit/2.1/OrcaWave v11.0 files/test01.owd"
    try:
        diff = OrcFxAPI.Diffraction(str(owd_path))
        print(f"OK: Loaded {owd_path.name}, state={diff.state}")
    except Exception as e:
        print(f"FAIL: Cannot load .owd: {e}")
        return False

    # Step 4: Calculate
    try:
        diff.Calculate()
        print(f"OK: Calculation complete, state={diff.state}")
    except Exception as e:
        print(f"FAIL: Calculation failed: {e}")
        return False

    # Step 5: Extract one result
    try:
        freqs = diff.frequencies
        print(f"OK: Extracted {len(freqs)} frequencies")
    except Exception as e:
        print(f"FAIL: Result extraction failed: {e}")
        return False

    print("PASS: All smoke test checks passed")
    return True

if __name__ == "__main__":
    success = smoke_test()
    sys.exit(0 if success else 1)
```

### pytest Marker Configuration

```python
# Addition to pyproject.toml [tool.pytest.ini_options] markers list:
# "solver: marks tests requiring OrcFxAPI on licensed machine (deselect with '-m \"not solver\"')"

# Addition to pytest.ini markers section:
# solver: Tests requiring OrcFxAPI on licensed machine (deselect with '-m "not solver"')
```

### pytest Fixture for Solver Artifacts

```python
# tests/conftest.py or tests/hydrodynamics/diffraction/conftest.py
import pytest
from pathlib import Path

SOLVER_FIXTURES_DIR = Path(__file__).parent / "fixtures" / "solver"

@pytest.fixture
def l00_owr_path():
    """Path to L00 reference .owr file (committed artifact from Phase 7)."""
    path = SOLVER_FIXTURES_DIR / "L00_test01.owr"
    if not path.exists():
        pytest.skip("L00 .owr fixture not available (requires solver run on licensed-win-1)")
    return path

@pytest.fixture
def l01_owr_path():
    """Path to L01 reference .owr file (committed artifact from Phase 7)."""
    path = SOLVER_FIXTURES_DIR / "L01_001_ship_raos.owr"
    if not path.exists():
        pytest.skip("L01 .owr fixture not available (requires solver run on licensed-win-1)")
    return path
```

### Remote Dispatch Script (from dev-primary)

```bash
#!/usr/bin/env bash
# scripts/remote-solver-dispatch.sh
# Dispatch a solver task to licensed-win-1 via SSH + Claude Code headless

REMOTE_HOST="user@192.168.0.184"  # licensed-win-1 primary NIC
REMOTE_REPO="D:/workspace-hub/digitalmodel"

ssh "$REMOTE_HOST" "cd $REMOTE_REPO && claude -p \"$1\" --allowedTools \"Bash,Read,Edit\" --output-format json"
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual RDP + run solver | SSH + Claude Code headless dispatch | 2026 (Claude Code -p mode) | Eliminates manual intervention, enables scripted automation |
| try/except import OrcFxAPI at module level | Subpackage boundary with clean import failure | Best practice as of Python packaging conventions | No runtime overhead, clear error messages, import-time isolation |
| OrcFxAPI requires OrcaFlex installer | OrcFxAPI available as PyPI wheel (v11.6.2) | 2024+ (Orcina PyPI publishing) | `uv add OrcFxAPI` works, but still needs DLL from OrcaFlex installation |
| Python 3.8-3.12 for OrcFxAPI | Python 3.9-3.14 supported | OrcFxAPI 11.6.x (2026) | Can use latest Python; dropped 3.8 support |

**Deprecated/outdated:**
- `InstallPythonInterface.bat`: Still works but `pip install OrcFxAPI` is the modern approach. The bat file is for environments where pip is not available.
- 32-bit Python: OrcFxAPI strongly recommends 64-bit. 32-bit has known bugs.

## Open Questions

1. **Is OrcaFlex/OrcaWave actually installed on licensed-win-1?**
   - What we know: Hardware inventory says "OrcaFlex/OrcaWave licensed" in the role description. Licensed software table lists both. But the manifest `windows_exe_paths.orcaflex` is empty with comment "not installed on this machine (license host only -- OrcaFlex not present)."
   - What's unclear: Contradiction between hardware assessment (lists OrcaFlex/OrcaWave) and manifest (says not installed). May mean the license server is hosted here but the software itself needs installation.
   - Recommendation: First task is `ssh licensed-win-1` and verify: `where orcawave.exe` and `python -c "import OrcFxAPI; print(OrcFxAPI.DLLVersion())"`. If not installed, installing OrcaFlex/OrcaWave is a prerequisite blocker.

2. **Is Claude Code installed on licensed-win-1?**
   - What we know: Manifest says `claude: ">=1.0"` in agent_clis, which is the target spec.
   - What's unclear: Whether this is currently installed or aspirational.
   - Recommendation: Verify `claude --version` via SSH. Install if needed (npm install -g @anthropic-ai/claude-code or standalone installer).

3. **SSH key authentication from dev-primary to licensed-win-1?**
   - What we know: licensed-win-1 manifest says "No SSH -- access physically or via GUI." OpenSSH is not yet enabled.
   - What's unclear: Whether there are firewall/network restrictions beyond the standard Windows configuration.
   - Recommendation: Enable OpenSSH Server and test key-based auth. This is a Phase 7 prerequisite task.

4. **What Python version is installed on licensed-win-1?**
   - What we know: OrcFxAPI 11.6.2 supports Python 3.9-3.14. dev-primary has Python 3.10+.
   - What's unclear: Current Python version on licensed-win-1. Orcina provides an embedded Python distribution with OrcaFlex.
   - Recommendation: Check `python --version` on licensed-win-1. If using Orcina's embedded Python, verify it's new enough. If not, `uv python install 3.12` installs a standalone Python.

5. **File sizes of .owr artifacts for git?**
   - What we know: L00 is the simplest case (unit box), L01 is a ship with real geometry.
   - What's unclear: How large .owr files are. Git handles binary files but large files (>50MB) should use Git LFS.
   - Recommendation: Check .owr sizes after generation. If under 10MB, commit directly. If larger, evaluate Git LFS.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| OpenSSH Server (licensed-win-1) | Remote execution (D-06, D-07) | Needs setup | Built-in Windows 11 | -- (BLOCKER: must enable) |
| OrcaFlex/OrcaWave (licensed-win-1) | Solver execution (D-09, D-10) | Unclear (see Open Question 1) | -- | -- (BLOCKER if not installed) |
| OrcFxAPI wheel (licensed-win-1) | Python API (D-10) | Available on PyPI | 11.6.2 | -- |
| Claude Code CLI (licensed-win-1) | Remote CC execution (D-06) | Unclear (see Open Question 2) | >= 1.0 | -- (BLOCKER: D-07 hard requirement) |
| uv (licensed-win-1) | Python env management (D-14) | Reported installed | >= 0.1 | Manual pip + venv |
| Python (licensed-win-1) | Runtime (D-15) | Unclear version | Need 3.9-3.14 | `uv python install 3.12` |
| Git (licensed-win-1) | Result transfer (D-04) | Assumed (Git Bash noted in manifest) | -- | -- |
| SSH client (dev-primary) | Remote dispatch | Available (Ubuntu 24.04) | Built-in | -- |
| pytest (digitalmodel) | Test markers (D-16, D-17) | Available | 7.4+ | -- |

**Missing dependencies with no fallback (BLOCKERS):**
- OpenSSH Server on licensed-win-1 must be enabled before anything else
- OrcaFlex/OrcaWave installation status on licensed-win-1 must be confirmed
- Claude Code CLI on licensed-win-1 must be installed/verified

**Missing dependencies with fallback:**
- None -- all missing items are hard blockers per D-07

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 7.4+ (existing in digitalmodel) |
| Config file | `digitalmodel/pytest.ini` and `digitalmodel/pyproject.toml` [tool.pytest.ini_options] |
| Quick run command | `uv run pytest tests/hydrodynamics/diffraction/ -m "not solver" -x --tb=short` |
| Full suite command | `uv run pytest tests/ -x --tb=short` |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| INFRA-01 | All non-solver code imports without OrcFxAPI | unit | `uv run python -c "from digitalmodel.hydrodynamics.diffraction import input_schemas, output_schemas, spec_converter, orcawave_backend, orcawave_runner"` | Wave 0 |
| INFRA-02 | OrcFxAPI smoke test passes on licensed-win-1 | integration (solver) | `uv run python tests/solver/smoke_test.py` (on licensed-win-1) | Wave 0 |
| D-06 | Remote CC dispatch works from dev-primary | smoke (manual + script) | `ssh user@192.168.0.184 'claude -p "echo PING" --bare'` | Wave 0 |
| D-09 | L00+L01 .owr artifacts produced | integration (solver) | `uv run pytest tests/solver/ -m solver -x` (on licensed-win-1) | Wave 0 |
| D-12 | solver/ subpackage exists, non-solver code does not import OrcFxAPI | unit | `uv run pytest tests/hydrodynamics/diffraction/test_module_boundary.py -x` | Wave 0 |
| D-16 | @pytest.mark.solver marker registered and functional | unit | `uv run pytest --markers \| grep solver` | Wave 0 |
| D-17 | .owr/.xlsx fixtures loadable without OrcFxAPI | unit | `uv run pytest tests/hydrodynamics/diffraction/test_solver_fixtures.py -m "not solver" -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `uv run pytest tests/hydrodynamics/diffraction/ -m "not solver" -x --tb=short`
- **Per wave merge:** `uv run pytest tests/ -x --tb=short`
- **Phase gate:** All non-solver tests pass on dev-primary + smoke test passes on licensed-win-1

### Wave 0 Gaps
- [ ] `tests/solver/smoke_test.py` -- binary smoke test for OrcFxAPI on licensed-win-1
- [ ] `tests/solver/conftest.py` -- solver-specific fixtures and skipif logic
- [ ] `tests/hydrodynamics/diffraction/test_module_boundary.py` -- verify import isolation
- [ ] `tests/hydrodynamics/diffraction/test_solver_fixtures.py` -- verify .owr/.xlsx fixtures loadable
- [ ] `@pytest.mark.solver` marker in both pytest.ini and pyproject.toml
- [ ] `.gitattributes` update for binary file handling (.owr, .xlsx)

## Sources

### Primary (HIGH confidence)
- [OrcFxAPI PyPI - v11.6.2](https://pypi.org/project/OrcFxAPI/) - Version, wheel format, Python requirement verified
- [OrcFxAPI Installation Docs](https://www.orcina.com/webhelp/OrcFxAPI/Content/html/Pythoninterface,Installation.htm) - DLL requirement, Python 3.9-3.14 support, embedded Python distribution
- [Claude Code Headless/Programmatic Mode](https://code.claude.com/docs/en/headless) - `-p` flag, `--allowedTools`, `--output-format json`, `--bare` mode, session continuation
- [Microsoft OpenSSH Server Setup](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse) - Windows 11 built-in, PowerShell commands for enable/configure
- Direct codebase inspection: `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/` -- 40+ files analyzed for OrcFxAPI import patterns
- Direct codebase inspection: `digitalmodel/pyproject.toml` -- dependency list, pytest configuration, markers
- `.planning/archive/modules/hardware-inventory/licensed-win-1.md` -- machine specs, pending actions, software inventory
- `.planning/archive/modules/hardware-inventory/manifests/licensed-win-1.yml` -- workspace root D:\workspace-hub, agent CLIs, domain tools

### Secondary (MEDIUM confidence)
- `.planning/research/PITFALLS.md` -- Pitfall 4 (solver not verified), Pitfall 6 (cross-platform), documented WRK-031 stall history
- `.planning/research/ARCHITECTURE.md` -- Layer map, component responsibilities, OrcFxAPI integration points
- `.planning/research/SUMMARY.md` -- Phase 0 rationale, stack decisions, overall confidence assessment
- [Windows 11 OpenSSH default shell configuration](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh-server-configuration) -- DefaultShell registry key

### Tertiary (LOW confidence)
- `.planning/research/2026-03-29-synthesis.md` -- uv TLS change risk on Windows (flagged, not verified)
- Claude Code remote SSH patterns -- community blog posts describe patterns but no official "remote dispatch" feature documentation exists

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- OrcFxAPI version verified on PyPI, Claude Code headless mode verified in official docs, OpenSSH verified in Microsoft docs
- Architecture: HIGH -- Module boundary based on direct codebase inspection of 40+ files; exactly 3 files import OrcFxAPI in src/
- Pitfalls: HIGH -- Based on documented project failures (WRK-031 stall, hardware inventory contradictions, manifest notes)
- Remote execution: MEDIUM -- SSH + `claude -p` is well-documented individually but the combined pattern (SSH into Windows + run Claude Code) is not officially documented as a supported workflow
- Environment availability: LOW -- Critical dependencies on licensed-win-1 are unverified (OrcaFlex installation, Claude Code CLI, OpenSSH state)

**Research date:** 2026-03-30
**Valid until:** 2026-04-06 (7 days -- fast-moving due to unverified blockers that could change scope)

---
*Phase: 07-solver-verification-gate*
*Research completed: 2026-03-30*
