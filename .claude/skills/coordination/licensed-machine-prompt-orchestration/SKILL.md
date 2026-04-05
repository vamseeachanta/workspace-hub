---
name: licensed-machine-prompt-orchestration
description: Design self-contained prompts for licensed machines (Windows, no Hermes) that Claude Code / Codex / Gemini CLIs can execute autonomously. Covers fixture generation, solver validation, and cross-machine data bridging.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [licensed-machine, prompts, orchestration, solver, fixtures, cross-machine]
    related_skills: [digitalmodel-orcawave-orcaflex-workflow, overnight-parallel-agent-prompts]
---

# Licensed-Machine Prompt Orchestration

Use this skill when you need to prepare work for a machine that has commercial solver licenses (OrcFxAPI, ANSYS, etc.) but does NOT have Hermes installed. The machine typically has Claude Code CLI, Codex CLI, and/or Gemini CLI available.

## When to use

- Generating solver fixtures (.owr, .sim, .dat) that require licensed APIs
- Validating dev-primary pipeline outputs against authoritative solver data
- Running calculations that can only execute on the licensed machine
- Any cross-machine workflow where dev-primary prepares code and the licensed machine produces evidence

## Prompt design principles (learned from 3 iterations)

### 1. Self-contained — no external context assumed

The agent on the licensed machine has NO memory, NO skills, NO Hermes. Every prompt must include:
- Exact workspace path (e.g., `D:\workspace-hub`)
- Which Python command to use (`python` not `uv run` on Windows)
- Full inline scripts — do NOT reference functions in packages the agent might not find
- `git pull` as the first step, `git push` as the last step

### 2. Inline Python over module imports

BAD (breaks when sys.path isn't set up):
```
from digitalmodel.hydrodynamics.hull_library.rao_extractor import xlsx_to_rao_data
```

GOOD (works anywhere):
```python
python -c "
import OrcFxAPI
d = OrcFxAPI.Diffraction()
d.LoadResults(r'path\to\file.owr')
print('Frequencies:', len(d.frequencies))
"
```

For longer scripts, use `python << 'PYEOF'` heredoc on Git Bash, or write a temp .py file.

If you MUST import from the repo, prefix with:
```python
import sys; sys.path.insert(0, r'digitalmodel\src')
```

### 3. Each prompt writes to non-overlapping paths

Structure prompts so Terminal 1 runs them sequentially and each writes to different directories:
- PROMPT 1 → `digitalmodel/tests/fixtures/solver/hemisphere.*`
- PROMPT 2 → `digitalmodel/tests/fixtures/solver/L02_*`
- PROMPT 3 → `output/orcaflex_validation/*`

This avoids git contention if prompts are accidentally parallelized.

### 4. Graceful failure — always comment on the issue

Every prompt must have a failure path that:
1. Catches the error
2. Comments on the relevant GitHub issue explaining what failed
3. Moves on to the next prompt

Example:
```
If it fails, skip to STEP 5 and do:
    gh issue comment 1789 --body "Hemisphere BLOCKED. Error: [paste]. Moving on."
```

### 5. Verify before commit

Every prompt should include a verification step BETWEEN generation and commit:
```python
# Verify the fixture loads
python -c "import OrcFxAPI; d=OrcFxAPI.Diffraction(); d.LoadResults(r'path.owr'); print('OK:', len(d.frequencies), 'freqs')"
```

### 6. Use the same xlsx export template everywhere

When generating xlsx sidecars from .owr files, use this canonical template. It produces the "pipeline format" that the rao_extractor.py can auto-detect:

Sheets: Summary, RAOs, AddedMass, Damping, Discretization
- RAOs columns: `{DOF}_Mag_H{heading}`, `{DOF}_Phase_H{heading}`
- AddedMass/Damping columns: `{DOFi}_{DOFj}` for full 6x6

CRITICAL: Sort frequencies ascending (`sort_idx = np.argsort(freq_rad)`) before writing.

## Licensed-machine prompt file structure

Place prompts at: `docs/plans/licensed-win-1-session-N-prompts.md`

Standard sections:
1. **Prerequisites** — git pull, pip install checks, OrcFxAPI version verify
2. **PROMPT N** blocks — each with Priority, Time estimate, Issue reference, STEP-by-STEP instructions
3. **Execution Plan** — Terminal 1 (sequential claude -p commands), Terminal 2 (verification)
4. **Git Contention Map** — table showing which prompt writes where
5. **Key Reminders** — python not uv run, git pull/push, digitalmodel is separate repo

## Execution on the licensed machine

```powershell
cd D:\workspace-hub
git pull origin main
cd digitalmodel && git pull origin main && cd ..

claude -p "Read docs/plans/licensed-win-1-session-N-prompts.md, execute PROMPT 1. Use python (not uv run). Commit and push results."
claude -p "Read docs/plans/licensed-win-1-session-N-prompts.md, execute PROMPT 2. Use python (not uv run). Commit and push results."
```

## Cross-machine data bridge pattern

The key insight from this work stream: **use xlsx as the license-free data bridge**.

1. Licensed machine runs the solver → produces binary .owr
2. Licensed machine ALSO exports .xlsx sidecar (openpyxl, inline script)
3. Both .owr + .xlsx are committed to fixtures/
4. Dev-primary reads ONLY the .xlsx (no solver license needed)
5. Licensed machine validates xlsx matches .owr at machine-epsilon precision

This pattern works for any proprietary binary format where you need dev-primary to work without the licensed reader.

## OrcFxAPI version pitfalls (discovered on licensed-win-1)

| Pattern | Works | Does NOT work |
|---------|-------|---------------|
| Frequency count | `len(np.array(d.frequencies))` | `d.frequencyCount` |
| Heading count | `len(np.array(d.headings))` | `d.headingCount` |
| Body count | `np.array(d.addedMass).shape[1] // 6` | `d.bodyCount` |
| Model objects | count manually | `model.objectCount` |

Always use the numpy-array approach for portability across OrcFxAPI versions.

## Validation script pattern

After generating fixtures, always create a validation script that compares xlsx against .owr:

```python
# Pattern: load .owr with OrcFxAPI, load .xlsx with openpyxl, compare
# Validate: frequencies, RAO amplitudes (relative), added mass (absolute)
# Threshold: machine epsilon for pipeline-format xlsx (bit-exact)
# Store script at: scripts/solver/validate_xlsx_against_owr.py
```

The validation proves the xlsx sidecar is trustworthy — dev-primary work inherits this proof.

## Session report pattern

After each licensed-machine session, create:
`docs/reports/YYYY-MM-DD-licensed-win-1-session-N-report.md`

Include: outcomes table (DONE/BLOCKED per prompt), new fixtures, validation results, issue comments posted, API lessons learned, remaining work.
