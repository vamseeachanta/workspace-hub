# Session report: #2205 amendment + child revision campaign

> **Date:** 2026-04-19
> **Scope:** Parent operating-model amendments + three child revisions + three follow-on issues + parent closure
> **Trigger:** 2026-04-17 cross-provider adversarial review of #2206/#2207/#2209 surfaced 38 findings and 3 parent-level systemic patterns requiring amendments

---

## Arc

### Phase 1 — Amendment-decision gathering
Three parent-level patterns identified by the 2026-04-17 review could not be resolved within any single child (per #2205 Section 10 conflict-resolution clause):
1. **Frontmatter schema authority** — 4-way disagreement between #2207/#2209/#2206 and live `knowledge/wikis/*/CLAUDE.md`.
2. **Identity namespace + status vocabulary** — live code emits `md5:`/`sha256:` mixed namespace; live data has `gap` status not in any child's enum; `provenance.py:82` stamps `discovered` at merge time, contradicting the field name.
3. **Invented layers** — #2209 classified weekly-review as "between L5 and L6"; #2206 classified `docs/document-intelligence/` as "L3-adjacent". Both self-fail #2206's own GUARD-1.

Recommendations accepted: **1A with baseline floor, 2.a yes / 2.b yes / 2.c = rename `discovered` → `merged_at`, 3B (tighten rule, no new layers)**.

### Phase 2 — Parent amendment
`docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` patched:
- **§2** — Worked-example table classifying normative architecture docs (L3), recurring operational (L5 with L5→L3 promotion), handoffs (L6), plans (L5), reviews (L5). Forbidden-inventions subsection bans "between L_n and L_m", "L_n-adjacent", hybrid layers.
- **§3** — `<algorithm>:<hex>` namespace; 7-state status superset; `discovered` → `merged_at` rename.
- **§8.1 (new)** — Per-wiki `CLAUDE.md` as L3 schema authority; baseline floor `{title, last_updated, doc_key}`; children layer additional fields on top.

Amendment comment on parent: [#2205#issuecomment-4277238819](https://github.com/vamseeachanta/workspace-hub/issues/2205#issuecomment-4277238819).

### Phase 3 — Per-child revision dispatch
Three agent-team dispatch prompts written at `docs/plans/2026-04-19-revision-dispatch-prompt-{2206,2207,2209}-*.md`. Each dispatched to a `general-purpose` agent in isolated git worktree (background, parallel).

Each agent: read dispatch prompt → grounded against amended parent + live code + 2026-04-17 reviews → revised deliverable → ran in-run adversarial + integrator review → committed to worktree branch → posted summary on child issue.

### Phase 4 — Merge + recover + close
All three branches merged to main with `--no-ff`. #2209 merge hit an auto-sync race — merge commit `4b91149a2` recorded parent link correctly but its tree silently reverted #2209's contributions. Detected by post-merge content verification (main line count did not match branch line count). Recovered via `git checkout worktree-agent-aa0cc1e2 -- <files>` + commit `087f9839f`.

Lesson written to memory: `feedback_merge_race_silent_revert.md`.

### Phase 5 — Follow-ons + closure
Three follow-on issues filed for residuals that cannot close within child scope:
- **#2360** — Update wiki `CLAUDE.md` files to declare `doc_key` (blocks #2206 FRONT-1)
- **#2361** — Rename `discovered` → `merged_at` in `scripts/data/document-index/provenance.py` (blocks #2206 ID-7)
- **#2362** — Phase E back-population of `doc_key` on `standards-transfer-ledger.yaml` (closes #2207 grandfather)

Parent #2205 closed with final summary (reopen-comment-close dance since `gh issue close --comment` silently drops on already-closed issues).

---

## Artifacts created or modified

| Artifact | Path | Action |
|---|---|---|
| Parent operating model | `docs/document-intelligence/llm-wiki-resource-doc-intelligence-operating-model.md` | Amended (+113 lines, §2/§3/§8.1) |
| Provenance contract (#2207) | `docs/document-intelligence/standards-codes-provenance-reuse-contract.md` | Revised (465→619 lines) |
| Durable/transient boundary (#2209) | `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` | Revised (465→661 lines) |
| Conformance checks (#2206) | `docs/document-intelligence/pyramid-conformance-checks.md` | Revised (?→717 lines; 6 new checks) |
| Dispatch prompts | `docs/plans/2026-04-19-revision-dispatch-prompt-{2206,2207,2209}-*.md` | New |
| Review artifacts | `scripts/review/results/2026-04-19-revision-{2206,2207,2209}-{claude,final}-review.md` | 6 new files |
| Plan-approved markers | `.planning/plan-approved/{2206,2207,2209}.md` | 3 new |
| Session report (this doc) | `docs/reports/2026-04-19-2205-amendment-campaign.md` | New |

## Commits landed on main (local, not pushed)

| SHA | Subject |
|---|---|
| `929af2394` | chore(sync): auto-sync 2026-04-19 (carried parent amendment + dispatch prompts) |
| `d2b23ca80` | Merge #2207 revision — amendment + 2026-04-17 findings |
| `4b91149a2` | Merge #2209 revision — amendment + 2026-04-17 findings (**tree silently reverted by auto-sync race**) |
| `087f9839f` | fix(doc-intel): restore #2209 revision — prior merge silently reverted content |
| `d54f3771d` | Merge #2206 revision — amendment + 2026-04-17 findings |

Plus unrelated auto-sync commits interleaved: `1f7fd855b`, `979684cdd`, `d06413a4f`, `9f931bcdb`, `6521c2ab9`, `f2a4b9b5f`, `20ca05434`, `e348e76b1`.

## GitHub state

| Issue | State | Key comment |
|---|---|---|
| #2205 | CLOSED (completed) | [#issuecomment-4277603783](https://github.com/vamseeachanta/workspace-hub/issues/2205#issuecomment-4277603783) (closure summary) |
| #2207 | status:plan-approved, OPEN | [#issuecomment-4277434561](https://github.com/vamseeachanta/workspace-hub/issues/2207#issuecomment-4277434561) (revision summary) |
| #2209 | status:plan-approved, OPEN | [#issuecomment-4277443099](https://github.com/vamseeachanta/workspace-hub/issues/2209#issuecomment-4277443099) (revision summary) |
| #2206 | status:plan-approved, OPEN | [#issuecomment-4277453079](https://github.com/vamseeachanta/workspace-hub/issues/2206#issuecomment-4277453079) (revision summary) |
| #2360 | OPEN | Filed this session (wiki CLAUDE.md migration) |
| #2361 | OPEN | Filed this session (provenance.py rename) |
| #2362 | OPEN | Filed this session (Phase E back-population) |

## Findings disposition

38 findings across three children resolved:

| Child | MAJOR resolved | MINOR resolved | Deferred | Verdict |
|---|---|---|---|---|
| #2207 | 5/5 | 5/5 (1 PARTIAL, 1 out-of-contract) | 0 | APPROVE |
| #2209 | 8/8 | 5/5 | 0 | APPROVED |
| #2206 | Full disposition in `scripts/review/results/2026-04-19-revision-2206-claude-review.md` | — | 5 MINOR residuals documented | APPROVED |

## New conformance checks added (under #2206)

- **FRONT-1** — Wiki `CLAUDE.md` baseline-floor enforcement (blocked by #2360 until wiki files update)
- **GUARD-1 (strengthened)** — Three forbidden-invention regexes with self-match scoping
- **ID-3 (redefined)** — `<algorithm>:<hex>` namespace conformance
- **FLOW-6** — Status vocabulary superset conformance
- **ID-7** — `merged_at` migration check (blocked by #2361 until code-side rename)
- **ACC-7** — Navigation count-claim drift detection

Check matrix: 33 → 38 total; automatable-now: 18 → 24.

## Residual risks carried forward

1. Wiki `CLAUDE.md` files don't yet declare `doc_key` — #2360 tracks
2. Promotion audit trail partially enforceable — three mechanisms defined in #2209 §7.4; operational implementation deferred
3. Handoff templates lack issue references — template migration queued under #2209 §10.1
4. `.planning/archive/` layer-inheritance needs GUARD-1 whitelist note — #2206 R4
5. CF-3 binary-vs-heuristic split under-specified at policy level — per-work-item annotations operative

## Operational takeaways

1. **Always verify merge tree content, not just parents.** Auto-sync can produce parent-link-only zombie merges. See `feedback_merge_race_silent_revert.md`.
2. **Children cannot self-approve amendments that cross their scope.** The Section 10 conflict-resolution clause worked as designed — three patterns escalated to parent, user decided, children revised against amended parent.
3. **Worktree isolation is the right shape for parallel revision runs on distinct deliverables.** Three agents completed independent revisions concurrently with zero file collisions; commits stayed on separate branches until explicit merge.
4. **`gh issue close --comment` silently drops on already-closed issues.** Use reopen-comment-close to recover, or post comment first then close. Covered in `feedback_gh_issue_close_silent_comment_drop.md`.
