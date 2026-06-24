# Plan for #2730: fix(gemini): remove unsupported permissionMode keys from agent definitions

> **Status:** draft
> **Complexity:** T1
> **Date:** 2026-06-24
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/2730
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-06-24-plan-2730-claude.md | ...-codex.md | ...-gemini.md

---

## Resource Intelligence Summary

### Existing repo code

- Found: `.gemini/agents/gsd-executor.md` — `permissionMode: acceptEdits` on line 4 (SHA `9770309eeb84e6178b48ebf900edd14ef85a9270`, confirmed via MCP read 2026-06-24)
- Found: `.gemini/agents/gsd-debugger.md` — `permissionMode: acceptEdits` on line 4 (SHA `ae96c9a2a818d492941b009786cb5e4db0fa71a4`, confirmed via MCP read 2026-06-24)
- Found: 17 total agent definition files in `.gemini/agents/` — only the above 2 are identified in the issue; implementer must run `grep -rn "permissionMode" .gemini/agents/` to confirm scope covers all files
- Found: No generator script or template in `.gemini/` producing these files — agent files are hand-authored. Confirmed by listing `.gemini/agents/` (only `.md` definition files, no `.sh`/`.py`/scripts sub-dir)
- Found: `scripts/enforcement/check-no-abs-paths.sh` and `scripts/enforcement/check-harness-file-size.sh` — Level-2 enforcement precedent; this plan follows the same pattern for the new schema guard
- Gap: Gemini CLI accepted frontmatter schema is not pinned in the repo — implementer must check `gemini --version` and the CLI's schema validation source to confirm `permissionMode` is permanently unsupported (not just version-locked)

### Standards

| Standard | Status | Source |
|---|---|---|
| Gemini CLI agent definition schema | gap — not in ledger | Issue body + Gemini CLI validation error messages |
| Enforcement gradient (prose→script→hook) | applied | `.claude/rules/patterns.md` |

### LLM Wiki pages consulted

- No relevant wiki pages — this is a CLI tool schema compatibility issue, not an engineering domain topic

### Documents consulted

- `#2730` issue body (2026-05-17) — names exact 2 files, quotes verbatim Gemini CLI validation error, scopes fix to removal or conditional generation of the key; verified OPEN 2026-06-24
- Issue comment 4481300310 (2026-05-18) — user prompt to implement; no plan or implementation artifact produced; issue remained open
- `.claude/rules/patterns.md` — enforcement gradient; Level-2 script (shell) is appropriate for a binary key-presence check
- `scripts/enforcement/check-no-abs-paths.sh` — prior-art pattern for Level-2 enforcement scripts in this repo

### Gaps identified

- Gemini CLI schema version not pinned — must verify at implementation time that removal (not upgrade) is correct
- Remaining 15 agent files not individually audited — grep scan during implementation will determine if any others carry `permissionMode`
- No existing test harness for `.gemini/agents/` frontmatter — the new script doubles as the test and the guard

### Evidence (embedded verification)

**Issue statuses** (verified 2026-06-24T via MCP):
- `#2730` — OPEN — fix(gemini): remove unsupported permissionMode keys from agent definitions
- `#2720` — CLOSED (referenced in issue body as context; not a dependency)

**File existence** (confirmed 2026-06-24 via MCP directory listing and file read):
- EXISTS: `.gemini/agents/gsd-executor.md`
- EXISTS: `.gemini/agents/gsd-debugger.md`
- MISSING (new — this plan creates): `scripts/enforcement/check-gemini-agent-schema.sh`

**Line excerpts** (verbatim from MCP file read of gsd-executor.md lines 1-6):
```
---
name: gsd-executor
description: Executes GSD plans with atomic commits, deviation handling...
permissionMode: acceptEdits    ← OFFENDING KEY — line 4
# hooks:
```

**Line excerpts** (verbatim from MCP file read of gsd-debugger.md lines 1-6):
```
---
name: gsd-debugger
description: Investigates bugs using scientific method, manages debug sessions...
permissionMode: acceptEdits    ← OFFENDING KEY — line 4
# hooks:
```

**Gap proofs**:
- No generator found: `.gemini/agents/` directory listing (MCP 2026-06-24) shows only 17 `.md` files — no `.sh`, `.py`, or `scripts/` sub-directory
- `grep -rn "permissionMode" .gemini/agents/` — to be run during implementation; issue body confirms it currently returns exactly `gsd-executor.md:4` and `gsd-debugger.md:4`

**Reproduction proofs** (verbatim from issue body — cannot run Gemini CLI in this session):
```
Agent loading error: Failed to load agent from .../gsd-executor.md: Validation failed:
  Agent Definition: Unrecognized key(s) in object: 'permissionMode'
Agent loading error: Failed to load agent from .../gsd-debugger.md: Validation failed:
  Agent Definition: Unrecognized key(s) in object: 'permissionMode'
```
- Reproduced during `#2720` closeout session (2026-05-17); user confirmed in issue body
- Failure mode matches issue claim: YES

<!-- Verification: 4 distinct sources consulted (issue body, enforcement rules, prior-art scripts, MCP file reads). Minimum 3 met. -->

---

## Artifact Map

| Artifact | Path |
|---|---|
| This plan | `docs/plans/2026-06-24-issue-2730-gemini-agent-remove-permissionmode.md` |
| Fix — executor | `.gemini/agents/gsd-executor.md` (remove `permissionMode: acceptEdits` line) |
| Fix — debugger | `.gemini/agents/gsd-debugger.md` (remove `permissionMode: acceptEdits` line) |
| Regression guard | `scripts/enforcement/check-gemini-agent-schema.sh` |
| Plan review — Claude | `scripts/review/results/2026-06-24-plan-2730-claude.md` |
| Plan review — Codex | `scripts/review/results/2026-06-24-plan-2730-codex.md` |
| Plan review — Gemini | `scripts/review/results/2026-06-24-plan-2730-gemini.md` |

---

## Deliverable

The `permissionMode: acceptEdits` key is removed from all `.gemini/agents/*.md` files that carry it, a regression guard script `scripts/enforcement/check-gemini-agent-schema.sh` catches unsupported frontmatter keys going forward (Level-2 per `.claude/rules/patterns.md`), and `gemini` launched from the repo root produces zero `Agent loading error:` lines for agent definition files.

---

## Files to Change

| Action | Path | Reason |
|---|---|---|
| Modify | `.gemini/agents/gsd-executor.md` | Remove `permissionMode: acceptEdits` from frontmatter (line 4) |
| Modify | `.gemini/agents/gsd-debugger.md` | Remove `permissionMode: acceptEdits` from frontmatter (line 4) |
| Modify | `.gemini/agents/<any-others>` | Remove same key if grep scan surfaces additional violations during implementation |
| Create | `scripts/enforcement/check-gemini-agent-schema.sh` | Level-2 guard: exit 1 if any `.gemini/agents/*.md` contains a denied frontmatter key |

---

## TDD Test List

| Test name | What it verifies | Expected input | Expected output |
|---|---|---|---|
| `test_no_permissionMode_executor` | Key absent from gsd-executor.md | `.gemini/agents/gsd-executor.md` | `grep permissionMode` → empty, exit 1 |
| `test_no_permissionMode_debugger` | Key absent from gsd-debugger.md | `.gemini/agents/gsd-debugger.md` | `grep permissionMode` → empty, exit 1 |
| `test_no_permissionMode_all_agents` | No agent file has the key | All 17 `.gemini/agents/*.md` | `grep -rn permissionMode .gemini/agents/` → empty |
| `test_guard_exits_0_on_clean` | Guard script passes clean state | Post-fix repo | `check-gemini-agent-schema.sh` → exit 0 |
| `test_guard_exits_1_on_violation` | Guard script fails if key re-introduced | Tmp file with `permissionMode: test` | `check-gemini-agent-schema.sh` → exit 1 with message |

Tests implemented as assertions in a companion `tests/enforcement/test_check_gemini_agent_schema.sh` (Bats or plain shell) following the pattern in `scripts/enforcement/` prior art.

---

## Acceptance Criteria

- [ ] `grep -rn "permissionMode" .gemini/agents/` returns empty (exit 1 with no output)
- [ ] `gemini` launches from repo root with zero `Agent loading error:` lines for agent definition validation
- [ ] `scripts/enforcement/check-gemini-agent-schema.sh` exits 0 on the post-fix state
- [ ] `scripts/enforcement/check-gemini-agent-schema.sh` exits 1 when pointed at a file containing `permissionMode: anything`
- [ ] All other frontmatter keys in both files (`name`, `description`, `tools`, commented `hooks:`) are preserved verbatim
- [ ] No regression: remaining `.gemini/agents/*.md` files unmodified unless grep surfaces additional violations

---

## Adversarial Review Summary

<!-- Pending — to be dispatched via scripts/review/plan-review-fanout.sh after status:plan-review is set. -->

| Provider | Verdict | Key findings |
|---|---|---|
| Claude | TBD | — |
| Codex | TBD | — |
| Gemini | TBD | — |

**Overall result:** Pending

---

## Risks and Open Questions

- **Risk:** `permissionMode` may be valid in a *newer* Gemini CLI version rather than an obsolete one — implementer must run `gemini --version` and confirm schema before removing. If upgrading the CLI would make the key valid, the correct fix is a CLI upgrade + note, not removal.
- **Risk:** Other `.gemini/agents/*.md` files may have `permissionMode` not listed in the issue body — plan covers all files via grep scan; fix all violations found, not just the named 2.
- **Risk:** Commented-out `# hooks:` block in both files uses Windows-absolute paths (`D:/workspace-hub/...`) which are already in violation of `.claude/rules/coding-style.md` (no hardcoded absolute paths). This pre-existing issue is out of scope for this plan — log as a follow-on, do not fix inline.
- **Open:** Should `check-gemini-agent-schema.sh` be promoted to a pre-commit hook (Level-3)? Recommend yes per `.claude/rules/patterns.md`, but defer to a follow-on issue — Level-2 script is sufficient for this plan.
- **Open:** Does `permissionMode` removal affect any downstream Gemini CLI feature that was relying on `acceptEdits` behaviour? Gemini CLI's validation rejection suggests the key is never processed; removal has no functional effect beyond silencing the error.

---

## Complexity: T1

**T1** — surgical removal of one known line from each of 2 known files, plus an additive enforcement script with no cross-module dependencies. All file paths confirmed. No logic changes.
