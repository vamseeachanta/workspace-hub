# Phase 7: Solver Verification Gate - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-30
**Phase:** 07-solver-verification-gate
**Areas discussed:** Result transfer mechanism, Remote execution model, Smoke test scope & artifacts, Conditional import pattern, uv sync on Windows, Python version alignment, Test strategy for the gate

---

## Result Transfer Mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| Git push from Windows | Results committed and pushed from licensed-win-1, pulled on dev-primary. Versioned, traceable. | |
| Shared filesystem (SMB/NFS) | Both machines mount a shared directory. Fast but no version history. | |
| SCP / rsync over SSH | Script pushes results via SSH. Simple but no versioning. | |

**User's choice:** Git push from Windows (initially selected)

**Follow-up — Three-machine topology:**

| Option | Description | Selected |
|--------|-------------|----------|
| Git through all three | licensed-win-1 commits, win-2 and dev-primary pull. All versioned. | ✓ |
| Shared network drive | Common share mounted by all three. Fast, no history. | |
| Mixed — git + network share | Shared drive between Windows machines, git for dev-primary. | |

**User's choice:** Git through all three

**User clarification:** Three machines in play — licensed-win-1 (acma-ansys05) has license, win-2 (ws014) can process non-license items, dev-primary orchestrates. Direct network path between the two Windows machines.

**Follow-up — win-2 role:**

| Option | Description | Selected |
|--------|-------------|----------|
| Post-processing assistant | win-2 runs non-license Windows tasks | |
| Primary processing | win-2 does most processing | |
| Backup / overflow only | Available but dev-primary handles all non-license work | ✓ |

---

## Remote Execution Model

| Option | Description | Selected |
|--------|-------------|----------|
| SSH from dev-primary | SSH into licensed-win-1, run commands remotely | |
| Manual RDP session | RDP in, run commands manually | |
| Claude Code on licensed-win-1 | Run CC agent directly on licensed-win-1 | ✓ |

**User's choice:** Claude Code on licensed-win-1
**Notes:** User wants to trigger from dev-primary — "if we can trigger next step from dev-primary then great stuff at work"

**Follow-up — Fallback if remote trigger fails:**

| Option | Description | Selected |
|--------|-------------|----------|
| Manual CC session on win-1 | RDP in, run CC locally | |
| SSH fallback | Fall back to SSH commands | |
| Block until remote trigger works | Getting remote CC trigger IS the goal | ✓ |

**User's choice:** Block until remote trigger works — hard requirement

**Follow-up — Remote trigger mechanism:**

| Option | Description | Selected |
|--------|-------------|----------|
| Claude Code CLI remote dispatch | Use CC remote features | |
| SSH + Claude Code | SSH in, invoke claude CLI | |
| You decide | Claude has discretion | ✓ |

---

## Smoke Test Scope & Artifacts

| Option | Description | Selected |
|--------|-------------|----------|
| Verify + produce reference artifacts | Run real benchmark, save .owr + Excel as test fixtures | ✓ |
| Minimal verify only | Confirm import, load, calculate, extract | |
| Full benchmark suite | Run all L00-L06 | |

**Follow-up — Which benchmarks:**

| Option | Description | Selected |
|--------|-------------|----------|
| L00 (simplest) | Fastest, minimal complexity | |
| L00 + L01 (simple + moderate) | Two data points for broader coverage | ✓ |
| You decide | Claude picks based on available data | |

**Follow-up — Commit artifacts as fixtures:**

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, commit as test fixtures | Permanent reference data in repo | ✓ |
| Store outside repo | Shared drive, avoid repo bloat | |
| You decide | Claude picks based on file sizes | |

**Follow-up — Pass/fail criteria:**

| Option | Description | Selected |
|--------|-------------|----------|
| Binary: loads + calculates + extracts = pass | Simple go/no-go | ✓ |
| Binary + result sanity checks | Plus physics checks | |
| Quantitative comparison | Compare against known results | |

---

## Conditional Import Pattern

| Option | Description | Selected |
|--------|-------------|----------|
| try/except at module level | HAS_ORCFX flag, conditional checks | |
| Separate entry points | Split into solver-dependent and solver-independent packages | ✓ |
| You decide | Claude picks based on codebase | |

**Follow-up — Enforcement timing:**

| Option | Description | Selected |
|--------|-------------|----------|
| Verify boundary only | Confirm it works, defer refactoring | |
| Enforce + refactor now | Move OrcFxAPI-dependent code into separated modules now | ✓ |
| You decide | Claude determines appropriate level | |

**Follow-up — Boundary pattern:**

| Option | Description | Selected |
|--------|-------------|----------|
| Subpackage boundary | e.g., `diffraction/solver/` for OrcFxAPI code | ✓ |
| Marker/optional dependency group | Optional extra in pyproject.toml | |
| Both | Subpackage + optional dependency | |

---

## uv sync on Windows

| Option | Description | Selected |
|--------|-------------|----------|
| Already installed | uv present, just verify sync | ✓ |
| Not yet | Install as part of Phase 7 | |
| Not sure | Check during verification | |

**Follow-up — Main concern:**

| Option | Description | Selected |
|--------|-------------|----------|
| OrcFxAPI wheel compatibility | Verify uv resolves Windows-only wheel correctly | ✓ |
| Full dependency tree sync | All dependencies install cleanly | |
| Lock file consistency | Same uv.lock works cross-platform | |

---

## Python Version Alignment

| Option | Description | Selected |
|--------|-------------|----------|
| Match OrcFxAPI requirements | Let OrcFxAPI dictate version | ✓ |
| 3.12 everywhere | Latest stable OrcFxAPI supports | |
| You decide | Claude checks current state | |

---

## Test Strategy for the Gate

| Option | Description | Selected |
|--------|-------------|----------|
| pytest markers + fixtures | @pytest.mark.solver marker, .owr/.xlsx fixtures | ✓ |
| Smoke test script only | Standalone script, not pytest | |
| You decide | Claude designs based on existing patterns | |

---

## Claude's Discretion

- Remote CC trigger mechanism (SSH + CC, native remote dispatch, or other)
- Exact subpackage structure for solver-dependent code
- Python version selection within OrcFxAPI's supported range

## Deferred Ideas

None — discussion stayed within phase scope.
