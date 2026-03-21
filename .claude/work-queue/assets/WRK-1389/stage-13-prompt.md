# Stage 13 Prompt Package — WRK-1389
## Stage: Agent Cross-Review
**Invocation:** task_agent
**Weight:** medium
**Context budget:** 8 KB

## Exit artifacts (must exist before calling exit-stage.sh)
  - `assets/WRK-NNN/review.md`

## Stage Micro-Skill (rules for this stage)
```
Stage 13 · Agent Cross-Review | task_agent | medium | parallel — 3 providers
Entry: ac-test-matrix.md, evidence/execute.yaml
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Mandatory: ALL 3 providers (Claude + Codex + Gemini). Same Opus-fallback rule as Stage 6:
quota exhausted OR ≥2 existing Codex reviews → auto-substitute Claude Opus (claude-opus-4-6).
Checklist:
0. EnterPlanMode — analyze all implementation + tests before recording any verdict
1. Send implementation + tests to Codex and Gemini simultaneously
2. Each provider reviews: security, correctness, missing ACs, code quality
3. Collect verdicts (APPROVE|REVISE) with P1/P2 findings
4. Write review.md via Write tool (verdict, reviewers[], findings)
Review verdict format:
- Verdicts: APPROVE or REVISE only — no MINOR/MAJOR/PARTIAL
- P1 findings: must-fix before merge (security, correctness, missing ACs)
- P2 findings: should-fix, non-blocking (style, naming, minor improvements)
- Any P1 finding → verdict REVISE; P2-only → verdict APPROVE
- review.md structure: verdict, reviewers[], p1_findings[], p2_findings[]
Exit: review.md (verdict: APPROVE|REVISE; all 3 providers listed)

```

## Entry reads

### assets/WRK-NNN/evidence/execute.yaml
```
[entry_reads: assets/WRK-NNN/evidence/execute.yaml — file not found]
```

### assets/WRK-NNN/ac-test-matrix.md
```
[entry_reads: assets/WRK-NNN/ac-test-matrix.md — file not found]
```

### assets/WRK-NNN/ac-test-matrix.md
```
[entry_reads: assets/WRK-NNN/ac-test-matrix.md — file not found]
```

**Blocking condition:** review.md missing or not all 3 providers reviewed