# Idea Compass typed links — repo convention

> **Status:** adopted (piloted 2026-09-25 on `pilot/idea-compass-links`, traversal-tested, merged to main)
> **Purpose:** make notes agent-navigable. A fresh agent dropped onto any note
> should orient in seconds: why it exists, what details hang off it, what
> precedent to compare, what was already rejected, and what comes next.

Adapted from the Idea Compass framework (K-Plex / Sketch Your Mind): every link
has a *direction* and a *meaning*, not just "see also".

## Frontmatter block

Add a YAML frontmatter block at the top of decision/plan/doctrine notes:

```yaml
---
compass:
  hub: true                        # entry point for a topic cluster (optional)
  parent: docs/plans/README.md        # broader context / WHY this note exists
  children:                           # deep dives / details / follow-up work
    - docs/plans/2026-06-03-issue-2911-prepush-worktree-skip.md
  friends:                            # similar precedent cases — compare before deciding
    - docs/ecosystem/windows-skill-junction-git-trap.md
  challengers:                        # rejected alternatives + reason (do NOT re-litigate)
    - note: docs/plans/2026-04-21-issue-2203-pre-push-worktree-aware-tier1-gate.md
      why: "MAJORx9 on scope complexity; #2911 is the intentionally narrower cut"
  prev: docs/governance/flywheel-icp-decision.md   # previous in a sequence (optional)
  next: TODO:docs/plans/2026-10-xx-followup.md     # next in a sequence (optional)
  memory:                                         # experiential "why" — hub notes MUST link these (rule 7)
    - .claude/memory/topics/feedback_amend_clobbers_parallel_branch_in_shared_checkout.md
---
```

## Field meanings

| Field | Direction | Meaning | Answers |
|---|---|---|---|
| `parent` | up | Broader context, epic, or doctrine this note serves | Why does this exist? |
| `children` | down | Implementation details, sub-plans, follow-ups | Where are the details? |
| `friends` | left | Similar cases / prior art worth comparing | Has this been solved before? |
| `challengers` | right | Alternatives considered and rejected, with `why` | What should I NOT re-propose? |
| `prev` / `next` | sideways | Position in a time/dependency sequence | What happened before/after? |
| `hub` | — | Marks this note as the entry point for its topic cluster. A cold agent given only a topic starts at the hub, then follows children/friends/challengers outward. | Where do I start on this topic? |
| `memory` | out | Experiential memory-topic notes holding the lived "why" behind this note. **Required on hub notes** (rule 7). | What did we learn the hard way here? |

## Cluster index

One-line entry points per topic cluster (pilot). A cold agent given a topic
starts at the hub note, then traverses `children` / `friends` / `challengers`.

| Topic | Hub note |
|---|---|
| Worktree & pre-push hygiene decisions | `docs/plans/2026-06-12-issue-3041-repo-ecosystem-hygiene-audit.md` |
| Registry schema reconciliation (v2) | `docs/plans/2026-06-28-issue-3295-registry-schema-v2-reconcile.md` |
| Per-machine repo placement decisions | `docs/plans/2026-05-20-issue-2770-ace-linux-1-placement-decision.md` |
| Flywheel strategy (wedge + ICP) | `docs/governance/flywheel-wedge-decision.md` |
| Public data corpus routing | `docs/governance/2026-05-20-public-data-corpus-routing-decision.md` |

## Rules

1. **One idea per note.** If a note needs two parents, it is two notes.
2. **Repo-relative paths.** All link targets are paths relative to the repo
   root, so they resolve in any checkout and survive renames via git history.
3. **Placeholders are first-class.** A link target that does not exist yet is
   marked with a `TODO:` prefix (e.g. `TODO:docs/plans/2026-10-xx-x.md`).
   Placeholders are *work orders*: visible gaps, not vague feelings.
   Every non-placeholder target MUST resolve to an existing file — verify with
   `git ls-files` or a path check before committing.
4. **Challengers always carry `why`.** A challenger without a reason is just a
   link; the reason is what stops the next agent re-litigating the decision.
5. **Keep it lightweight.** Only decision/plan/doctrine notes get compass
   blocks — not every README, not generated reports. Aim: the notes an agent
   needs for catch-up, not an index of everything.
6. **Inferred links stay out.** Auto-suggested "related notes" are hypotheses;
   only *deliberately declared* links go in the block. If a script generates
   suggestions, they live elsewhere, clearly marked as inferred.
7. **Hubs link outward to memory.** Every hub note MUST carry a `memory:` list
   pointing at the relevant `.claude/memory/topics/` entries (find them via
   `.claude/memory/topics/INDEX.md`). The traversal test showed the richest
   "why" material lives in experiential memory notes, which the compass trail
   alone does not surface — without this link, agents get the decisions but
   miss the hard-won lessons. Omit the field only when no memory topic is
   genuinely relevant; never force-fit.

## Verifying a retrofit

```bash
# every non-TODO: target must exist
git grep -h -A20 '^compass:' -- 'docs/**/*.md' | grep -oP '(?<=: )(TODO:)?docs/\S+\.md' \
  | grep -v '^TODO:' | while read p; do [ -f "$p" ] || echo "BROKEN: $p"; done
```

## Adoption

Piloted 2026-09-25 on `pilot/idea-compass-links` (10 notes + 5 hub flags),
validated by a head-to-head traversal test: a fresh agent given only a topic
used ~2x fewer tool calls with the convention, self-discovered the links
unprompted, and lost no accuracy. Refinement from the test: rule 7 (hubs link
outward to memory topics), because the baseline agent's wider sweep surfaced
experiential "why" material the compass trail alone missed.

Going forward: every new decision/plan/doctrine note gets a compass block;
cluster parents get `hub: true` plus `memory:` links. No backfill mandate —
retrofit opportunistically when a note is touched.
