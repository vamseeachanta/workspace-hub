# Session exit handoff — 2026-05-17 (sub-issue approvals + Phase B redaction)

Continuation of the 2026-05-16 session arc. Prior handoffs:
1. `2026-05-16-issue-40-wave1-92-plan-paths-a-b-exit.md` — paths A + B parallel
2. `2026-05-16-phase-5-execution-complete-exit.md` — Phase 5 epic execution
3. `2026-05-16-phase-5-hygiene-wave2-final-exit.md` — Phase 5 hygiene + Wave 2 + memory updates (incl. addendum on 4 sub-issues filed)

This handoff covers 2026-05-17 actions: 3 Wave 2 follow-up sub-issues approved, 1 closed-as-obsolete per user reframing, Wave 2 corpus manifest Phase B redacted.

## Outcomes

| Commit | Repo | Change |
|---|---|---|
| _(GH label flips only)_ | llm-wiki | [#96](https://github.com/vamseeachanta/llm-wiki/issues/96) + [#97](https://github.com/vamseeachanta/llm-wiki/issues/97) + [#98](https://github.com/vamseeachanta/llm-wiki/issues/98) → `status:plan-approved` |
| _(GH issue close)_ | llm-wiki | [#99](https://github.com/vamseeachanta/llm-wiki/issues/99) CLOSED as not-planned per user reframing |
| [`f30e0e86`](https://github.com/vamseeachanta/llm-wiki/commit/f30e0e86) | llm-wiki | Wave 2 corpus manifest Phase B redacted (forward-only) |

## Key user direction this segment

User flagged: `/mnt/ace/rock-oil-field/` is **not** wrong-domain — it is a **client repo serving the data layer** for the user's professional work. The original Wave 2 framing ("wrong-domain note as governance addition") missed this. Correct framing: the directory is operationally correctly-domain for its actual purpose (off-repo client data infrastructure), and the existing `feedback_offrepo_intel_routing` governance boundary already applies — no in-repo "wrong-domain note" is needed.

The implication that emerged from this reframing: the Wave 2 corpus manifest's Phase B section ([`0413ed87`](https://github.com/vamseeachanta/llm-wiki/commit/0413ed87)) enumerated 22 rows referencing client/employer materials (client names, project names, vessel names, document IDs, employer-internal training references). Per the off-repo data-layer governance boundary, these should not appear in a published repository even at path/title/license-note level.

## Phase B remediation

User chose **forward-only redact to one paragraph** (2-axis decision via AskUserQuestion):

- **Scope**: full redact (replace all 22 rows + reconnaissance heading + Phase B summary with a single paragraph)
- **History**: forward-only (new commit replaces content; original Phase B stays in git history at `0413ed87`)

Rationale for forward-only over force-push: standard public-repo guidance for non-credential content leaks is forward-redact + accept history retention. Force-push history rewrite is reserved for credential / regulated-PII leaks and has costs (breaks forks, may not catch GitHub's internal mirrors / search engine caches / GH archive program).

Remediation file: [`docs/research/reservoir-engineering-corpus.md`](https://github.com/vamseeachanta/llm-wiki/blob/main/docs/research/reservoir-engineering-corpus.md):
- Phase B section: 22-row table redacted to one paragraph (~100 words) documenting that sweep occurred + yielded zero in-scope sources + off-repo data-layer boundary applies + no path-level enumeration carried into public manifest
- Reconnaissance paragraph rewritten to remove client/project/vessel/employer references
- Phase B summary line removed
- Summary table updated: Phase B columns `_(redacted)_`; totals 64 → 42 publicly-enumerated rows
- Frontmatter classifications reconciled (also fixes pre-existing count discrepancy: frontmatter had 56 but body summed to 64; new state internally consistent at 42)
- Notes + gap analysis + forward references all reframed
- Original Phase B content remains in git history at [`0413ed87`](https://github.com/vamseeachanta/llm-wiki/commit/0413ed87)

File shrunk 145 → 121 lines (28.8KB → 21.4KB). Zero client/employer leakage in current state (verified via grep for `chevron|shell perdido|talos|ballymore|MD2|FJR|subsea-7|S7|seven arctic|StormGeo|GEDS|document-IDs` → zero matches).

## Plan acceptance impact

24/30 high-quality and 34/50 mixed-quality targets **unchanged** by the redaction (Phase B contributed 0 to ingest/defer regardless of enumeration). The targets remain closeable via the now-approved #96 + #97 + #98 work.

## Open work for next session

### Approved sub-issues awaiting implementation (3)
1. [#96](https://github.com/vamseeachanta/llm-wiki/issues/96) license-verification for 10 `defer` rows — ~30-60 min
2. [#97](https://github.com/vamseeachanta/llm-wiki/issues/97) arXiv expansion — ~45-60 min
3. [#98](https://github.com/vamseeachanta/llm-wiki/issues/98) Kansas Geological Survey reuse-permission email — ~15 min draft + send; async response

Per #40 comment, recommended sequencing: #98 first (lowest-effort, async); #96 + #97 to close ≥30/≥50 corpus target; then Wave 3 (concept-page authoring) once #96 + #97 land.

### Wave 3 ahead (waits on #96 + #97)
Wave 3 = concept pages for gamma-ray-log-interpretation + dip-azimuth + formation-tops (the 3 forward-reference placeholders from Wave 1 founding). Should NOT begin until #96 + #97 finalize the `ingest`-tier source pool. ~60-90 min via subagent.

## Discipline notes worth carrying forward (new this segment)

- **Name-based local-directory assumptions are dangerous.** The plan body labeled `/mnt/ace/rock-oil-field/` as "top candidate by name" — pure-name reasoning. Actual content invalidated the assumption. The reconnaissance subagent caught it. The user's reframing then refined what the finding meant — the directory wasn't "wrong-domain" (a research-corpus framing), it was correctly-domain for its actual purpose (client-data infrastructure). Lesson: plan bodies should name directories AND verify the assumption against actual content before committing to walk them.
- **Off-repo data-layer boundary covers more than direct content.** `feedback_offrepo_intel_routing` says off-repo client data shouldn't be in published repos. The Wave 2 manifest violated this NOT by reproducing content but by enumerating PATHS, TITLES, CLIENT NAMES, PROJECT NAMES, VESSEL NAMES, DOCUMENT IDs at the row level. These are derived identifiers, not content, but they leak client identification just as effectively. The governance boundary extends to derived metadata, not just content.
- **Forward-only redaction is the right default for non-credential content leaks** on small/recent public repos. Force-push history rewrite is a heavier tool that should be reserved for credentials, regulated PII, or extreme cases. Trade-off this session: original Phase B content stays in git history at `0413ed87` (recoverable via `git show 0413ed87:docs/research/reservoir-engineering-corpus.md`), but no propagation continues into forks/mirrors going forward from `f30e0e86`.
- **Frontmatter-vs-body count consistency is hard to maintain in subagent-produced research artifacts.** The Wave 2 manifest had frontmatter `total_candidates: 56` but body summary `Total: 64` — a 8-row discrepancy that survived initial validation. The redaction commit reconciled both to 42 as a side effect. Future research subagents should be prompted to do a final consistency check before reporting "ready to commit".

## Workspace state at exit

- llm-wiki main: [`f30e0e86`](https://github.com/vamseeachanta/llm-wiki/commit/f30e0e86) on origin, clean
- workspace-hub main: was at [`240682d07`](https://github.com/vamseeachanta/workspace-hub/commit/240682d07) (prior handoff addendum); this handoff commit will be the only added work
- No active background agents

## Next-session first-step recommendation

Given the 3 approved sub-issues all advance #40 toward Wave 3 readiness:

1. **#98 first** (~15 min draft + send) — async response time TBD, so file-and-forget
2. **#96 second** (~30-60 min) — per-row WebFetch on remaining defer rows
3. **#97 third** (~45-60 min) — arXiv expansion
4. **Then Wave 3** (~60-90 min) — concept-page authoring once `ingest` pool finalized

Total estimated implementation budget for the remaining #40 path: ~2.5-3.5 hours across 2-3 fresh sessions. Each can be done independently.

**Do not** start Wave 3 concept-page authoring until #96 + #97 land. **Do not** re-add the Wave 2 manifest Phase B per-row content; if a future need arises to reference local-corpus walks for client-data verification, do that in off-repo notes per `feedback_offrepo_intel_routing`.
