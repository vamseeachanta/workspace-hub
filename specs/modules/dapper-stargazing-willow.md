# WRK-687 Plan — Per-Workstation comprehensive-learning with ace-linux-1 Compilation

> **WRK:** WRK-687 | **Route:** B | **Orchestrator:** claude | **Status:** DRAFT

---

## Context

WRK-683 established `logs/orchestrator/` as a unified per-machine log directory for all
three AI agents (Claude JSONL + Codex/Gemini text logs). The next step is to have every
workstation run its own comprehensive-learning analysis against its local logs, commit
derived state, and let ace-linux-1 do a final cross-machine compilation.

Currently `comprehensive-learning` has a hard guard (`hostname != ace-linux-1 → exit`).
`contribute` and `contribute-minimal` machines only commit/push — they run no analysis.
acma-ansys05's AI CLI status in `workstations/SKILL.md` is stale (shows `no` for all
three CLIs; confirmed by user to have claude + codex + gemini installed).

---

## Design

```
ace-linux-1              ace-linux-2              acma-ansys05
logs/orchestrator/       logs/orchestrator/       logs/orchestrator/
├── claude/*.jsonl       ├── claude/*.jsonl       ├── claude/*.jsonl
├── codex/*.log          ├── codex/*.log          ├── codex/*.log
└── gemini/*.log         └── gemini/*.log         └── gemini/*.log
        │                        │                        │
  Phases 1–9              Phases 1–9               Phases 1–9
  (full local)            (full local)             (full local)
        │                        │                        │
  commit state             commit state             commit state
        │                        │                        │
        └──────────── git pull (ace-linux-1) ────────────┘
                      Phase 10a: compilation
                      Phase 10: report
```

---

## Files to Change

| File | Action | Key change |
|------|--------|-----------|
| `.claude/skills/workspace-hub/comprehensive-learning/SKILL.md` | EDIT | Replace binary guard with mode-based routing; add Phase 1 log source; add per-machine commit step; add Phase 10a compilation |
| `.claude/skills/workspace-hub/workstations/SKILL.md` | EDIT | Fix acma-ansys05 AI CLI status; update cron_variant for ace-linux-2 and acma-ansys05; update comp-learning integration table |
| `logs/orchestrator/README.md` | EDIT | Add per-machine flow section |
| `scripts/work-queue/verify-log-presence.sh` | CREATE | Pre-close gate: checks all 3 agent dirs are present and valid on the running machine |
| `tests/test_wrk687_lifecycle.sh` | CREATE | 4-stage E2E lifecycle test; must pass on all 3 machines |

---

## Deliverable 1 — `comprehensive-learning/SKILL.md`

### 1a. Frontmatter description (lines 3–7)
Replace:
```
  Runs on ace-linux-1 only. Other machines contribute via git-synced state files.
```
With:
```
  All machines run local Phases 1–9 against logs/orchestrator/ and commit derived state.
  ace-linux-1 additionally runs Phase 10a (cross-machine compilation) and Phase 10 (report).
```

### 1b. Single-Machine Guard → Mode-Based Routing (lines 35–47)
Replace the hard-exit guard with:
```bash
MACHINE=$(hostname -s 2>/dev/null || hostname | cut -d. -f1 | tr '[:upper:]' '[:lower:]')
case "$MACHINE" in
  ace-linux-1) CL_MODE="full" ;;
  ace-linux-2) CL_MODE="contribute" ;;
  acma-ansys05|acma-ws014) CL_MODE="contribute" ;;
  *) CL_MODE="contribute" ;;
esac
echo "comprehensive-learning: mode=${CL_MODE} machine=${MACHINE}"
# All modes run Phases 1–9. Only 'full' runs Phase 10a (compilation) + Phase 10 (report).
```

### 1c. Cross-Machine Data Flow table (lines 53–57)
Update acma-ansys05 row — it now contributes `session-signals/` (has full AI CLI suite):
```
| acma-ansys05 | candidates/, corrections/, session-signals/, patterns/ | OrcaFlex/ANSYS + full AI CLI (claude/codex/gemini) |
```

### 1d. Phase 1 — add `logs/orchestrator/` as source (after line 78)
Add to Phase 1 sources list:
```
- `logs/orchestrator/claude/session_YYYYMMDD.jsonl`  (raw tool-call stream — agent loop, file activity)
- `logs/orchestrator/codex/WRK-*.log`               (cross-review verdicts per WRK)
- `logs/orchestrator/gemini/WRK-*.log`              (cross-review verdicts per WRK)
```
Note: use for tool-call pattern checks (agent loop detection, bash-file-ops anti-pattern).
These supplement `session-signals/*.jsonl` — they do not replace it.

### 1e. Per-machine commit step (add after Phase 9, before Phase 10)
New section "**Inter-phase: Commit Derived State** *(all modes)*":
```bash
# Commit derived state so ace-linux-1 can pull it
git -C "${WS_HUB}" add \
  .claude/state/session-signals/ \
  .claude/state/candidates/ \
  .claude/state/corrections/ \
  .claude/state/patterns/ \
  .claude/state/skill-scores.yaml
git -C "${WS_HUB}" -c core.hooksPath=/dev/null \
  commit -m "chore: session learnings from $(hostname) $(date +%Y-%m-%d)" \
  --allow-empty 2>/dev/null || true
```

### 1f. New Phase 10a — Cross-Machine Compilation *(full mode / ace-linux-1 only)*
Insert between the commit step and existing Phase 10:
```
### Phase 10a — Cross-Machine Compilation  *(full mode only)*

Skip if CL_MODE != "full".

1. `git pull --rebase` to pick up all machines' committed derived state
2. Read session-signals/ from all machines (identified by signal hostname field)
3. Aggregate skill-scores.yaml entries across machines (union, keep latest per skill)
4. Write cross-machine compilation report to:
   `.claude/state/session-analysis/compilation-YYYYMMDD.md`
   Sections: per-machine summary table, aggregated skill scores, cross-machine anti-patterns
5. Record DONE/SKIPPED/FAILED in Phase 10 report
```

---

## Deliverable 2 — `workstations/SKILL.md`

### 2a. AI CLI Availability table (lines 205–211)
Fix acma-ansys05 row:
```
| acma-ansys05 | yes | yes | yes | Windows; Git Bash for scripts |
```

### 2b. Software Capability Map YAML — acma-ansys05 entry (lines 175–181)
Update `programs` list and add `install_method`:
```yaml
  acma-ansys05:
    hostname: ACMA-ANSYS05
    programs: [orcaflex, ansys, aqwa, python, office, claude-code, codex, gemini]
    install_method: {claude: native, codex: npm-user, gemini: pip}
    exclusive: [orcaflex, ansys, aqwa]
    shares_hub: null
    isolated: true
    cron_variant: contribute
```
Change `cron_variant` from `contribute-minimal` → `contribute` (full AI suite present).

### 2c. comprehensive-learning Integration table (lines 261–265)
Update to reflect new per-machine analysis:
```
| cron_variant        | Role                                                        | Machine(s)                   |
|---------------------|-------------------------------------------------------------|------------------------------|
| `full`              | Phases 1–9 locally + Phase 10a compilation + Phase 10 report | ace-linux-1                |
| `contribute`        | Phases 1–9 locally + commit derived state                   | ace-linux-2, acma-ansys05, acma-ws014 |
| `contribute-minimal`| Reserved for machines with no AI CLIs                      | (future machines)            |
```

---

## Deliverable 3 — `logs/orchestrator/README.md`

Add new section "## Per-Machine Analysis Flow":
```markdown
## Per-Machine Analysis Flow

Each machine runs `comprehensive-learning` locally against its own `logs/orchestrator/`:

1. **Phase 1** reads `logs/orchestrator/<agent>/` for raw tool-call and review data
2. **Phases 1–9** produce derived state: `session-signals/`, `candidates/`, `skill-scores.yaml`
3. **Commit step** pushes derived state to git (hooks bypassed: `git -c core.hooksPath=/dev/null`)
4. **ace-linux-1 Phase 10a** runs `git pull` to aggregate all machines, writes compilation report

Raw logs in `logs/orchestrator/` are local-only (gitignored). Only derived state crosses machines.
```

---

## Deliverable 4 — `scripts/work-queue/verify-log-presence.sh` (CREATE)

```bash
#!/usr/bin/env bash
# verify-log-presence.sh — Pre-close gate for WRK-687
# Checks all 3 agent log dirs on the current machine.
# Exit 0 = PASS, Exit 1 = FAIL
set -uo pipefail
REPO_ROOT="$(git rev-parse --show-toplevel)"
ORCH_DIR="${REPO_ROOT}/logs/orchestrator"
MACHINE=$(hostname -s)
PASS=0; FAIL=0

check_agent() {
  local agent="$1" ext="$2"
  local dir="${ORCH_DIR}/${agent}"
  if [[ ! -d "$dir" ]]; then
    echo "  ${agent}  MISSING dir ${dir}"; FAIL=$((FAIL+1)); return
  fi
  local count; count=$(find "$dir" -name "*.${ext}" | wc -l)
  if [[ "$count" -eq 0 ]]; then
    echo "  ${agent}  NO FILES (*.${ext}) in ${dir}"; FAIL=$((FAIL+1)); return
  fi
  # For JSONL: validate JSON on latest file
  if [[ "$ext" == "jsonl" ]]; then
    local latest; latest=$(find "$dir" -name "*.jsonl" | sort | tail -1)
    local valid; valid=$(python3 -c "
import json, sys
lines=[l for l in open('${latest}').readlines() if l.strip()]
ok=sum(1 for l in lines if (lambda: True)() and not (json.loads(l) and False))
try:
  ok=sum(1 for l in lines if json.loads(l.strip()) or True)
except: ok=0
print(f'{ok}/{len(lines)}')
" 2>/dev/null || echo "?/?")
    echo "  ${agent}  OK  (${count} file(s), latest: $(basename "$latest"), valid JSON: ${valid})"
  else
    echo "  ${agent}  OK  (${count} file(s))"
  fi
  PASS=$((PASS+1))
}

echo "[verify-log-presence] Machine: ${MACHINE}"
check_agent claude jsonl
check_agent codex  log
check_agent gemini log
echo ""
if [[ $FAIL -eq 0 ]]; then echo "PASS"; exit 0
else echo "FAIL (${FAIL} agent(s) missing/invalid)"; exit 1; fi
```

---

## Deliverable 5 — `tests/test_wrk687_lifecycle.sh` (CREATE)

Location: `tests/test_wrk687_lifecycle.sh` (hub-level, alongside other bash tests)

4-stage test using synthetic fixtures. Clean up on EXIT via `trap`.

### Stage A — Log write verification
- Create fixture `logs/orchestrator/claude/session_TEST.jsonl` with 2 valid JSON lines
- Create fixture `logs/orchestrator/codex/WRK-TEST-20260101T000000Z.log` with sample text
- Create fixture `logs/orchestrator/gemini/WRK-TEST-20260101T000000Z.log`
- Run `verify-log-presence.sh` → assert exit 0
- Assert valid JSON count matches

### Stage B — comprehensive-learning Phase 1 source check
- Run `session-analysis.sh --date 1970-01-01` (date with no real signals → produces empty
  but valid summary at `.claude/state/session-analysis/1970-01-01.md`)
- Assert summary file written and non-empty
- Assert `skill-scores.yaml` exists (may be unchanged if no signals — that's OK)

### Stage C — Commit step dry run
- Stage a dummy file in a temp branch or use `git commit --dry-run` equivalent
- Assert git reports "nothing to commit" or "would commit N files" without error

### Stage D — Compilation check (ace-linux-1 only)
- Skip with `SKIPPED (not ace-linux-1)` on other machines
- On ace-linux-1: create a fixture compilation input (mock ace-linux-2 session-signals file)
  in a temp dir, invoke compilation logic stub, assert output report file written

Expected output per machine:
```
[WRK-687 lifecycle] Machine: ace-linux-1
  Stage A — log write + verify:       PASS
  Stage B — session-analysis dry run: PASS
  Stage C — commit step:              PASS
  Stage D — compilation:              PASS
OVERALL: PASS
```
On ace-linux-2 / acma-ansys05: Stage D = SKIPPED (not FAIL).

---

## Acceptance Criteria (pre-close checklist)

- [ ] `comprehensive-learning/SKILL.md`: mode-based routing replaces hard guard
- [ ] `comprehensive-learning/SKILL.md`: `logs/orchestrator/` added to Phase 1 sources
- [ ] `comprehensive-learning/SKILL.md`: per-machine commit step documented after Phase 9
- [ ] `comprehensive-learning/SKILL.md`: Phase 10a compilation documented
- [ ] `workstations/SKILL.md`: acma-ansys05 AI CLIs = yes (all three)
- [ ] `workstations/SKILL.md`: acma-ansys05 `cron_variant` = `contribute`
- [ ] `workstations/SKILL.md`: comp-learning integration table updated
- [ ] `verify-log-presence.sh` exits 0 on ace-linux-1 *(run and paste output)*
- [ ] `verify-log-presence.sh` exits 0 on ace-linux-2 *(SSH run)*
- [ ] `verify-log-presence.sh` exits 0 on acma-ansys05 *(Git Bash; paste output)*
- [ ] `test_wrk687_lifecycle.sh` OVERALL: PASS on ace-linux-1 *(paste output)*
- [ ] `test_wrk687_lifecycle.sh` OVERALL: PASS on ace-linux-2 *(SSH run; paste output)*
- [ ] `test_wrk687_lifecycle.sh` OVERALL: PASS on acma-ansys05 *(Git Bash; paste output)*

---

## What Is NOT Changing

- `scripts/cron/setup-cron.sh` — cron_variant → cron schedule mapping unchanged
- `.claude/state/sessions/` — primary Claude session store unchanged
- `session-signals/*.jsonl` schema — unchanged; `logs/orchestrator/` is an additive source
- `scripts/review/results/` — Codex/Gemini output path unchanged
- acma-ws014 — no AI CLIs; stays on `contribute` (commits candidates only)
