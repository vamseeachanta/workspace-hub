# Final Integrator Review — 2026-04-19 Revision of #2209 Durable/Transient Boundary

> **Reviewer role:** Integrator (4-role dispatch)
> **Date:** 2026-04-19
> **Deliverable:** `docs/document-intelligence/durable-vs-transient-knowledge-boundary.md` (revised this run)
> **In-run adversarial review:** `scripts/review/results/2026-04-19-revision-2209-claude-review.md` (verdict: PASS)
> **Cross-provider gate baseline:** `2026-04-17-plan-2209-claude-adversarial.md` + `2026-04-17-plan-2209-codex-adversarial.md`

## Verdict: **APPROVED** — ready to commit

## Integrator checklist

| Gate | Status |
|---|---|
| Parent amendments A–E applied in revised deliverable | PASS |
| All 8 MAJOR findings resolved | PASS |
| All 5 MINOR findings addressed (3 fixed, 1 resolved by 2026-04-17 Codex landing, 1 partial-enforceability acknowledged in Section 11) | PASS |
| Quality-bar: zero invented-layer classifications in active use | PASS (mechanical grep + semantic read) |
| Quality-bar: frontmatter reframed per parent Section 8.1 | PASS (Section 10.1 explicitly defers to per-wiki CLAUDE.md) |
| Quality-bar: every 2026-04-17 finding has explicit disposition | PASS (Section 13 revision-history table lists all 13) |
| Cross-provider gate already satisfied for the underlying plan | PASS (2026-04-17 Claude + Codex artifacts on disk) |
| Allowed-write-path constraints honored | PASS (only the 4 enumerated paths written) |
| Forbidden paths untouched | PASS (parent operating model, siblings #2207/#2206, code/data, config, tests) |
| Content preservation (no unnecessary rewrite) | PASS (retained AP-1..AP-8 anti-patterns, promotion-criteria core structure, retention-table shape, and glossary scaffold) |

## Substantive resolution summary

### MAJOR defects in the 2026-04-11 deliverable that are now fixed

1. **Invented "Between L5 and L6" layer.** Removed everywhere in active classification; retained only in explicit-negation rationales and in AP-9 guardrail. Recurring-run outputs reclassified as L5 individually with L5→L3 synthesis promotion per parent Section 2 worked examples.

2. **`.planning/plan-approved/` misclassified as transient L6 with "delete at closure" retention.** Reclassified as L5 governance audit evidence with permanent retention; GR-7 added as a guardrail against deletion; AP-10 added as an anti-pattern; Section 10.2 explicitly warns against adding deletion to `issue-planning-mode` closure step.

3. **"L3-adjacent" classification of the operating-model doc and similar normative architecture docs.** Removed. Section 4.2 now classifies normative architecture docs as L3 per parent Section 2 worked examples.

4. **Frontmatter required-set conflicting with #2207 and the engineering wiki's own `CLAUDE.md`.** Reframed per parent Section 8.1: per-wiki `CLAUDE.md` is the binding authority; this policy declares additional recommended fields layered over the parent baseline floor (`title`, `last_updated`, `doc_key`).

5. **`.planning/` collapsed into one L6 bucket.** Split into 7 sub-classes in Section 4.8, each with distinct layer and retention: plan-approved (L5 permanent), HANDOFF.json (L6 short), quick (L6 issue-tied), research (L6 30-day), archive (inherit), discoveries (L6 14-day), verified (L5 permanent).

6. **Uncommitted `.claude/state/session-signals/` example cited as in-repo evidence.** Removed; Section 4.9 now distinguishes committed vs local-only subtrees and documents why the 2026-04-11 citation was wrong.

7. **Handoff retention depending on metadata live handoffs don't carry.** Section 8.4 declares the "associated issue" signal non-computable for handoffs lacking issue references; date-based fall-back specified (90 days); template migration queued in Section 10.1 #4.

8. **Cross-provider review absent.** Resolved on 2026-04-17 (Codex review landed on disk).

### MINOR improvements

1. Terminology split: "transient" reserved for L6; "execution-bound" for L5 knowledge property.
2. Retention table marked advisory pending #2237 cleanup workflow.
3. Stability demoted from hard gate to soft signal; `under-revision` tag allows unstable-but-promoted findings.
4. Handoff retention tied to associated-issue lifecycle (F6).
5. Promotion audit trail: three concrete auditable mechanisms defined (Section 7.4); "no silent promotion" declared partially enforceable (Section 11 open-question 6).

## Content preservation audit

The revised document is a targeted revision, not a rewrite. I spot-checked preserved content:

- Section 4.1 LLM-Wikis: "What wikis are for / NOT for" lists unchanged in substance
- Section 4.6 Registries (was 4.3): structure and anti-use lists preserved
- Section 5.1 classification decision tree: structure preserved, L5/L6 outcomes refined
- Section 6.2 forbidden bridges: all original entries preserved; one "raw dump" entry reworded to L5 vocabulary
- Section 7.2 promotion process: 5-step structure preserved; step 4 upgraded with §7.4 reference
- Section 7.3 promotion anti-patterns: 4 entries preserved; "Mass-promoting weekly review findings" reworded to "Mass-promoting individual recurring-run findings"
- Section 9.1 anti-patterns: AP-1..AP-8 preserved verbatim; AP-9 (layer invention) and AP-10 (deleting governance evidence) added
- Section 12 follow-on sequence: extended from 8 to 11 items, preserving original intent and adding the new implementation surfaces driven by this revision
- Glossary: preserved with additions for `promoted_from`, parent baseline floor, `doc_key`, `merged_at`; removed "Recurring-operational artifact" class (replaced by "Recurring-run output" description)

No adjacent content was accidentally deleted. No imports/cross-references were mangled. No duplicate definitions introduced.

## Risks and deferrals

| Risk | Mitigation |
|---|---|
| Wiki `CLAUDE.md` files do not yet declare `doc_key` as required (parent Section 8.1 baseline floor) | Section 12 item 1 queues the update; #2206 FRONT-1 must not enforce the floor until the wiki CLAUDE.md files are updated |
| Handoff templates do not yet carry issue references | Section 8.4 date-based fall-back prevents premature enforcement; Section 10.1 #4 queues template migration |
| Promotion audit trail only partially enforceable | Section 11 open-question 6 acknowledges; Section 10.3 "Promotion audit trail checker" queues the implementation |
| `.planning/archive/` layer-inheritance rule may confuse conformance check GUARD-1 | Flagged in in-run review M2; GUARD-1 implementation (#2206) must allow archive-inheritance without false-positives |
| Domain-wiki `CLAUDE.md` files may decline some Section 10.1 recommendations | Section 10.1 scope note already anticipates this; recommendations are explicitly layered, not mandatory |

## Approval

**Approved for commit** to the worktree branch. No push; PR-time review is separate.

Integrator: Claude (4-role dispatch integrator)
Date: 2026-04-19
