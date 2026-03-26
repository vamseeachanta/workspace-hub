# File Structure Skills — Knowledge Map

> **WRK-689** | Updated: 2026-03-03

Quick reference: which skill to invoke for which file-structure scenario.

---

## Skills in This Cluster

| Skill | Version | Invocation | Scope |
|-------|---------|-----------|-------|
| [`file-taxonomy`](../skills/workspace-hub/file-taxonomy/SKILL.md) | 1.6.0 | `/file-taxonomy` | Where to put output files; format guide; gitignore policy; AI log locations |
| [`repo-structure`](../skills/workspace-hub/repo-structure/SKILL.md) | 1.4.0 | `/repo-structure` | Source layout, test mirroring, root cleanliness, docs classification |
| [`clean-code`](../skills/workspace-hub/clean-code/SKILL.md) | 2.1.0 | `/clean-code` | File/function size limits, God Object detection, refactor guidance |
| [`infrastructure-layout`](../skills/workspace-hub/infrastructure-layout/SKILL.md) | 1.0.0 | `/infrastructure-layout` | `infrastructure/` sub-domain layout (config/persistence/validation/utils/solvers) |

---

## Relationship Diagram

```
                 ┌────────────────────────────────────┐
                 │           repo-structure            │
                 │  (top-level dirs, tier rules,       │
                 │   root cleanliness, gitignore)      │
                 └──────────────┬─────────────────────┘
                                │ see_also
               ┌────────────────┼────────────────────┐
               ▼                ▼                    ▼
     ┌──────────────────┐  ┌──────────────┐  ┌──────────────────────┐
     │  infrastructure  │  │ file-taxonomy │  │     clean-code        │
     │  -layout         │  │              │  │                       │
     │  (infrastructure/│  │ WHERE to     │  │ HOW LARGE: file/fn    │
     │   sub-packages)  │  │ write files  │  │ size limits, God Obj  │
     └──────────────────┘  │ + log paths  │  └──────────────────────┘
                           └──────────────┘
```

**Dependency rule**: check `repo-structure` first to understand what directories exist,
then `file-taxonomy` to decide where to put a new file.

---

## Scenario Lookup

| Scenario | Primary Skill | Notes |
|----------|--------------|-------|
| Creating a new directory in a repo | `repo-structure` | Check tier rules first |
| Writing a generated report (HTML/PDF/MD) | `file-taxonomy` | → `reports/<domain>/` |
| Writing computation output (arrays, matrices) | `file-taxonomy` | → `results/<domain>/` |
| Placing test fixtures | `file-taxonomy` + `repo-structure` | → `tests/<domain>/fixtures/` |
| Adding a new Python module to `src/` | `repo-structure` + `clean-code` | Check 400-line limit |
| Refactoring a 600+ line file | `clean-code` | God Object detection flowchart |
| Adding cross-cutting infra code | `infrastructure-layout` | 5-domain layout |
| Writing runtime config (YAML/JSON) | `file-taxonomy` | → `config/<domain>/` |
| Placing notebooks | `file-taxonomy` | → `notebooks/<domain>/` (NOT src/) |
| Finding AI session logs | `file-taxonomy` | See "AI Agent Log & Session File Locations" section |
| Writing a design spec (pre-build) | `file-taxonomy` | → `.planning/ (GSD phases)` |
| Locating Codex session data | `file-taxonomy` | `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` |
| Locating Gemini session data | `file-taxonomy` | `~/.gemini/tmp/<project>/chats/session-*.json` |
| Understanding gitignore policy | `file-taxonomy` | Gitignore Policy table |
| Provider prompt templates | `file-taxonomy` | → `.codex/prompts/` or `.gemini/prompts/` |
| Moving files out of `src/` | `repo-structure` | Enforce zero-tolerance rules |

---

## Coverage Gaps

| Scenario | Gap | Suggested Action |
|----------|-----|-----------------|
| Database migration files | Not covered by any skill | Add to `file-taxonomy` decision tree |
| Docker / container files | Not explicitly covered | `repo-structure` mentions root files; expand if needed |
| Generated protobuf / OpenAPI schemas | Not covered | Add to `file-taxonomy` as "schema/ canonical dir" |
| licensed-win-1 Windows path conventions | Partially covered | `file-taxonomy` log section has Windows note; may need dedicated section |

---

## Meta-Note: Skill Size Violations

Both `clean-code` and `infrastructure-layout` exceed the 400-line hard limit they themselves enforce:

| Skill | Lines | Status |
|-------|-------|--------|
| `clean-code` | 491 | ⚠ exceeds own 400-line hard limit |
| `infrastructure-layout` | 511 | ⚠ exceeds own 400-line hard limit |
| `repo-structure` | 411 | ⚠ marginally over |
| `file-taxonomy` | ~235 | ✓ within limit |

Skills are exempt from the 400-line rule (they are documentation, not Python modules),
but this is worth tracking — long skills are harder to read and maintain.

---

## Version History

| Date | Change |
|------|--------|
| 2026-03-03 | Created (WRK-689) — 4-skill cluster, scenario lookup, gap analysis |
