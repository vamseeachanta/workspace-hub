
## 2026-04-23 — Multi-provider session sweep (Claude + Codex + Hermes)

**Scope:** Sessions since last transfer commit `2a9a5ef4c` (2026-04-11): ~161 Claude JSONLs, ~364 Codex rollouts, ~250 Hermes sessions. Deepest signal on 2026-04-22/23 around issue #2460 (tier-1 indexing plan, r1→r16 adversarial-review loop).

**Three net-new learnings captured:**
- `topics/feedback_codex_sandbox_fallback_paths.md` (NEW) — Codex uses `js_repl` + GitHub connector + non-login shell retry when shell wrapper is sandbox-blocked. Prompts should authorize these explicitly; MAJOR verdicts lacking a fallback-read citation should be treated as weakly grounded. Complements existing `feedback_codex_sandbox_*` which cover what's blocked. *stale: 2026-04-30*
- `topics/feedback_codex_sustained_major_loop.md` (PROMOTED to git-tracked + UPDATED) — added #2460 as third anti-pattern instance (Codex MAJOR×8 consecutive). Meta-lesson: prose-level memory didn't self-enforce mid-flow even though the rule was present at session start. Flagged for Level-2 enforcement promotion per `.claude/rules/patterns.md`. *stale: 2026-05-15*
- `project_issue_2460_approval_binding.md` (auto-memory only) — approval markers must name four bindings: plan SHA, review-artifact paths + per-provider verdicts, approval-storage surface, revision cleanup protocol. Mutable file-path-only refs silently drift under plan rewrites.

**Signals processed:** Codex verdict sequence for #2460 today: MAJOR×8 → MINOR → REQUEST_CHANGES×2 → MINOR → APPROVE (closed 2026-04-23). Follow-ups filed: #2467, #2468, #2469 (worldenergydata flake8 lanes).
**Signals skipped:** Hermes model-default switch to gpt-5.5 on most recent session (operational observation, not durable learning); 16 background/exit-hook Claude sessions with no content.

## 2026-02-21 — Session 127 (QTF TOC Integration)

**Changes applied:**
- `MEMORY.md`: Updated session stats (127 sessions, 208 commits); added `loadRAOsDiffraction` first-order RAO warning to OrcaWave section; expanded QTF validation suite notes with 4-panel layout, TOC integration, and `BodyIncreaseRollDampingToTarget` cosmetic classification
- `orcawave-lessons.md`: New "OrcaWave QTF API Quirks" section — `loadRAOsDiffraction` warning, canonical 4-panel layout, `BodyIncreaseRollDampingToTarget` cosmetic rule
- `benchmark-patterns.md`: Added `BodyIncreaseRollDampingToTarget` to cosmetic column example; new "QTF Benchmark Patterns (Cases 3.x)" section

**Signals processed:** 3 (eco-review info: missing frontmatter in internal skills — staged, score 0.6)
**Signals skipped:** skill-candidate frontmatter fixes (internal/_internal skills — low-risk, no user-facing impact)
