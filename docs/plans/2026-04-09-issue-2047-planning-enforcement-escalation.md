# Plan for #2047: Implement Stronger Enforcement for Issue Planning Workflow If Audit Fails

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-04-09
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2047
> **Review artifacts:** pending

---

## Resource Intelligence Summary

### Existing repo code
- Found: `.claude/hooks/plan-approval-gate.sh` — PreToolUse hook, blocks Write/Edit without approval marker
- Found: `scripts/enforcement/require-plan-approval.sh` — pre-commit hook for plan approval
- Found: `scripts/review/cross-review-gate.sh` — cross-review enforcement (WARNING mode)
- Found: `.claude/skills/coordination/engineering-issue-workflow/SKILL.md` — documents 3-phase enforcement escalation
- Found: `docs/standards/HARD-STOP-POLICY.md` — defines bypass conditions and logging
- Gap: No Hermes prefill mechanism for planning workflow injection
- Gap: No Claude Code SessionStart hook for automatic workflow detection

### Standards
N/A — operations/governance task

### Documents consulted
- Issue #2045 — onboarding (prerequisite)
- Issue #2046 — compliance audit (triggers this issue)
- `engineering-issue-workflow/SKILL.md` — defines 3-phase enforcement strategy
- Issue #1876 — tracks Option 2+3 implementation

### Gaps identified
- Hermes has no session-start hooks — relies on AGENTS.md (always loaded) and skills (on demand)
- Claude Code hooks exist but self-approval detection has edge cases (120s window, uncommitted check)
- `.claude/skills/` path is not in the gate safe list, creating chicken-and-egg for governance edits
- No logging dashboard for bypass events

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-04-09-issue-2047-planning-enforcement-escalation.md` |
| Hermes prefill config | `~/.hermes/config.yaml` (if Option 2) |
| SessionStart hook | `.claude/settings.json` (if Option 3) |
| Bypass log | `logs/hooks/plan-gate-bypass.jsonl` |

---

## Deliverable

Stronger enforcement mechanisms (Hermes prefill and/or Claude Code SessionStart hooks) that automatically inject the planning workflow at session start, triggered only if the #2046 compliance audit shows continued non-compliance after the #2045 onboarding.

---

## Pseudocode

```
# Option 2: Hermes prefill
hermes_config.yaml:
  prefill_messages_file: 'docs/standards/engineering-workflow-prefill.md'
  # Auto-injects workflow instructions at every Hermes session start

# Option 3: Claude Code SessionStart hook
settings.json:
  hooks:
    SessionStart:
      - command: "bash .claude/hooks/detect-engineering-issue.sh"
        # Scans conversation for issue references
        # If engineering issue detected, injects workflow instructions

# Plan-approval gate improvement
plan-approval-gate.sh:
  add .claude/skills/ to safe_paths  # governance edits should not require approval
  improve self-approval detection  # extend window, check git author
```

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `.claude/hooks/plan-approval-gate.sh` | Add `.claude/skills/` to safe paths |
| Create | `.claude/hooks/detect-engineering-issue.sh` | SessionStart hook for issue detection |
| Modify | `.claude/settings.json` | Add SessionStart hook reference |
| Create | `docs/standards/engineering-workflow-prefill.md` | Hermes prefill content |
| Modify | `~/.hermes/config.yaml` | Add prefill_messages_file reference |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| test_safe_path_includes_skills | gate allows .claude/skills/ edits | file_path=.claude/skills/foo/SKILL.md | exit 0 (allowed) |
| test_session_start_detects_issue | hook detects issue reference in prompt | "Working on #1234" | injects workflow |
| test_hermes_prefill_loads | prefill file is valid markdown | cat prefill file | valid markdown |
| test_bypass_logged | bypass events written to log | SKIP_PLAN_APPROVAL_GATE=1 | entry in bypass.jsonl |

---

## Acceptance Criteria

- [ ] Plan-approval gate allows `.claude/skills/` edits without approval marker
- [ ] SessionStart hook detects engineering issues and injects workflow (if Option 3)
- [ ] Hermes prefill file created and referenced in config (if Option 2)
- [ ] Bypass events are logged to `logs/hooks/plan-gate-bypass.jsonl`
- [ ] All existing enforcement still works (no regressions)

---

## Adversarial Review Summary

| Provider | Verdict | Key findings |
|---|---|---|
| Pending | — | Review not yet run |

**Overall result:** PENDING

---

## Risks and Open Questions

- **Risk:** SessionStart hooks add latency to every Claude Code session start
- **Risk:** Hermes prefill may conflict with other prefill content
- **Open:** Should this be triggered automatically based on #2046 audit results, or manually?
- **Open:** Should the safe path addition for `.claude/skills/` be done immediately (as part of #2045) or deferred to this issue?
- **Dependency:** This issue should only be implemented if #2046 audit shows < 50% compliance after #2045 onboarding

---

## Complexity: T2

**T2** — multiple hooks and config files across different agent systems, moderate testing needed.
