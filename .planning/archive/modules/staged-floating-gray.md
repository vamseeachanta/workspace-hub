# Plan: WRK-308 — Move pre-commit skill validation + readiness checks to nightly cron

## Context

Two sets of checks were running synchronously in the commit/session path and
causing slowness on Windows/MINGW:

1. **Pre-commit**: `validate-skills.sh` scanned 480 SKILL.md files on every
   commit (5+ min on Windows). Blocked commits during WRK-304/307 session.

2. **Stop hook**: `ensure-readiness.sh` (444 lines, 10 checks) ran at every
   session end. Already deleted from Stop hooks in WRK-304 (commit a1854cd),
   but its checks are now unhoused — they need a new home.

Decision (consistent with WRK-304 lean-session philosophy):
- Remove skill validation from pre-commit → nightly cron
- Move 9 of 10 readiness checks → nightly cron (Phase 6 ecosystem health)
- R9 (session snapshot check) → re-wire to session-start readiness hook only

CI (`skills-validation.yml`) remains the safety net for skill frontmatter on PRs.

## Files to Change

| File | Change |
|------|--------|
| `.git/hooks/pre-commit` | Remove `validate-skills.sh` call; leave minimal valid hook |
| `scripts/cron/comprehensive-learning-nightly.sh` | Add Step 4: skill validation + Step 5: readiness checks |
| `scripts/skills/install-skill-validator-hook.sh` | Remove skill validation from installed hook template |
| `.claude/hooks/readiness/readiness.sh` | Keep (PreToolUse hook, fast WRK gate) — no change |
| `comprehensive-learning` SKILL.md | Document readiness checks in Phase 6 |
| `WRK-308.md` | Update scope and acceptance criteria |

**Not changed:** `scripts/skills/validate-skills.sh`, `.github/workflows/skills-validation.yml`

## Readiness Check Disposition

| Check | What it validates | Nightly placement |
|---|---|---|
| R1 | Memory files ≤ 200 lines | Phase 6 ecosystem health |
| R5 | Context budget ≤ 16KB | Phase 6 ecosystem health |
| R6 | Submodules on tracking branches, ≤5 commits behind | Phase 6 ecosystem health |
| R9 | Session snapshot <48h old | **Session-start only** — re-wire to `readiness.sh` (PreToolUse) |
| R-CODEX | CODEX.md MAX_TEAMMATES matches settings.json | Phase 6 ecosystem health |
| R-MODEL | No stale model IDs in scripts/ | Phase 6 ecosystem health (weekly guard) |
| R-REGISTRY | model-registry.yaml ≤ 14 days old | Phase 6 ecosystem health (weekly guard) |
| R-XPROV | CODEX.md + GEMINI.md contain legal + TDD mandates | Phase 6 ecosystem health |
| R-SKILLS | session-signals/ fresh, skills committed in 7 days | Phase 1 / Phase 9 |
| R-HARNESS | CLAUDE.md, AGENTS.md, CODEX.md, GEMINI.md ≤ 25 lines | Phase 6 ecosystem health |

R9 is the only check that is session-scoped (checking "is there a recent snapshot
to resume from"). It belongs in `readiness.sh` (PreToolUse), not the nightly run.

## Implementation

### 1. `.git/hooks/pre-commit` — remove skill validation

```bash
#!/usr/bin/env bash
set -euo pipefail
# Pre-commit checks — skill validation moved to nightly cron (WRK-308)
```

### 2. `scripts/cron/comprehensive-learning-nightly.sh` — add Steps 4 and 5

Insert between rsync (Step 2) and pipeline exec (Step 3):

```bash
# Step 4: validate skill frontmatter (best-effort)
echo "--- Skill validation $(date +%Y-%m-%dT%H:%M:%S) ---"
bash scripts/skills/validate-skills.sh .claude/skills || \
  echo "WARNING: skill validation issues found — see above"

# Step 5: readiness checks (best-effort — 9 checks from former ensure-readiness.sh)
echo "--- Readiness checks $(date +%Y-%m-%dT%H:%M:%S) ---"
READINESS_SCRIPT="scripts/readiness/nightly-readiness.sh"
[[ -f "$READINESS_SCRIPT" ]] && bash "$READINESS_SCRIPT" || \
  echo "INFO: nightly-readiness.sh not yet created (WRK-308 pending)"
```

### 3. `scripts/readiness/nightly-readiness.sh` — new file

Extract the 9 cron-suitable checks from the deleted `ensure-readiness.sh`
into a new script. Each check outputs a one-line result; failures append to
`.claude/state/readiness-issues.md` for Phase 6 to pick up.

Checks to include: R1, R5, R6, R-CODEX, R-MODEL, R-REGISTRY, R-XPROV,
R-SKILLS, R-HARNESS. Each wraps in `|| true` so no single failure aborts
the nightly run.

### 4. `scripts/skills/install-skill-validator-hook.sh`

Remove the skill validation heredoc from the hook template. Fresh installs
get a lean pre-commit hook matching the updated `.git/hooks/pre-commit` above.

### 5. `comprehensive-learning` SKILL.md — Phase 6 note

Add a bullet to Phase 6 (WRK Feedback / Ecosystem):

```
- Run `scripts/readiness/nightly-readiness.sh` — surfaces R1/R5/R6/R-CODEX/
  R-MODEL/R-REGISTRY/R-XPROV/R-SKILLS/R-HARNESS issues in the report
```

### 6. `WRK-308.md` — update scope

Update the acceptance criteria to reflect nightly-cron approach (remove
staged-files filter references; add nightly Steps 4+5 and readiness script).

## Verification

1. `time git commit --allow-empty -m "test"` — pre-commit exits in < 1s
2. `bash scripts/cron/comprehensive-learning-nightly.sh` (dry-run / manual) —
   Steps 4+5 logged, skill validation passes, readiness checks complete
3. `cat .claude/state/readiness-issues.md` after nightly run — any R1/R5 etc.
   issues visible
4. `bash scripts/skills/install-skill-validator-hook.sh` on a fresh repo —
   pre-commit installed without skill validation line
5. CI: `skills-validation.yml` passes unchanged
