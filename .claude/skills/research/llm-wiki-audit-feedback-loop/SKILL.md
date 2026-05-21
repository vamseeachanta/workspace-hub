---
name: llm-wiki-audit-feedback-loop
description: >-
  Durable feedback loop for correcting llm-wiki pages without losing the
  correction to chat history. Use when (1) a human notices a wiki page is wrong,
  outdated, or contradicts a source, (2) processing the `audit/` inbox of a
  domain wiki, (3) reviewing what feedback has been resolved vs deferred,
  (4) needing to leave a comment on a specific text range that survives line-
  number drift. Implements the anchored-text audit file pattern from
  lewislulu/llm-wiki-skill, adapted for workspace-hub's domain-wiki layout
  under /mnt/local-analysis/llm-wiki/wikis/<domain>/. Extends the 5-op model
  (compile/ingest/query/lint) from research/llm-wiki with the missing
  `audit` op. Never silently delete feedback — rejected audits stay archived
  with rejection rationale.
metadata:
  category: research
  related_skills:
    - research/llm-wiki
    - research/llm-wiki-page-shape-contract
    - research/llm-wiki-cadence-governance
  related_issues:
    - vamseeachanta/workspace-hub#2374
    - vamseeachanta/workspace-hub#2392
  references:
    - references/audit-file-format.md
---

# llm-wiki audit / feedback loop

The wiki is AI-written; it is wrong sometimes. Sources are human-written;
they contradict each other. Inline chat corrections evaporate when context
compresses. The `audit/` inbox is the durable correction surface — one file
per comment, anchored to a text range, processed under one of four
resolution states, and **never silently deleted**.

Pattern provenance: [lewislulu/llm-wiki-skill audit-shared](https://github.com/lewislulu/llm-wiki-skill).
Anchor algorithm choice (before/text/after window) is robust against
line-number drift, which is what makes the file format usable across
multiple editing surfaces (CLI, Obsidian plugin, web viewer if/when we
build one).

---

## When this skill applies

| Trigger | Action |
|---|---|
| Human spots a factual error in a wiki page | File an audit entry; do NOT just fix it in chat |
| Cascade-update from new source contradicts existing wiki content | File an audit + annotate in-line; let resolution decide |
| Lint pass flags a heuristic issue (orphan, missing cross-link, freq-mentioned no page) | File an audit; lint script may auto-file |
| Reviewer's cross-provider review finds a defect class in wiki content | File an audit per finding |
| Wiki page contradicts a `feedback_*` memory entry | File an audit; resolution may require updating memory OR wiki |
| You just want to make a small typo fix | **Skip this skill** — edit in place, log it normally |
| You want to retract content entirely | File an audit with `severity: high` + `action: remove` |

---

## Directory layout

```
/mnt/local-analysis/llm-wiki/wikis/<domain>/
├── audit/                    ← open feedback inbox (one file per comment)
│   ├── 20260520-143022-mooring-mbl-calc-error.md
│   └── 20260520-151105-orcaflex-version-drift.md
├── audit/resolved/           ← processed feedback — NEVER deleted
│   ├── 20260519-091233-yaw-moment-citation-fixed.md
│   └── 20260519-093045-acoustic-impedance-rejected.md
└── log/
    └── 20260520.md           ← per-day operation log; every audit resolution logs here
```

`audit/` lives **inside the wiki domain** so multiple domain wikis maintain
independent inboxes. Cross-domain audits (rare) live under whichever domain's
page the comment anchors to.

---

## Audit file format (see `references/audit-file-format.md` for full spec)

```markdown
---
id: 20260520-143022-mooring-mbl-calc-error
target: wikis/engineering/standards/dnv-os-e301.md
anchor_before: |
  ## Safety factor application
  
  The minimum breaking load (MBL) is reduced by the
anchor_text: |
  safety factor 1.67 for ULS conditions per
anchor_after: |
  table 4-2, row 3, before being compared against
  the calculated tension envelope.
severity: high                     # low | medium | high
action: revise                     # revise | remove | clarify | annotate-contradiction
filed_by: vamsee
filed_at: 2026-05-20T14:30:22-05:00
state: open                        # open | resolved
---

# Feedback

The DNV-OS-E301 2023 revision actually specifies 1.5 for ULS in
table 4-2 row 3, not 1.67. The 1.67 value is from the 2018 revision
(table 4-1, row 2) and should not apply to current calcs.

# Recommended action

Update the page to cite the 2023 revision's table 4-2 row 3
(safety factor = 1.5) and add an `## Edition history` section noting
the 2018 → 2023 change. The mooring_design.py citation registry
already points at the 2023 edition; the wiki is the only place still
referencing 1.67.
```

Frontmatter contract:

| Field | Required | Purpose |
|---|---|---|
| `id` | yes | `<YYYYMMDD-HHMMSS-slug>`; filename matches `id` exactly |
| `target` | yes | Repo-relative path to the wiki page being commented on |
| `anchor_before` | yes | ~3 lines immediately preceding `anchor_text` in the target file |
| `anchor_text` | yes | The exact text range the comment is about |
| `anchor_after` | yes | ~3 lines immediately following `anchor_text` |
| `severity` | yes | `low` / `medium` / `high` — drives processing priority |
| `action` | yes | `revise` / `remove` / `clarify` / `annotate-contradiction` |
| `filed_by` | yes | Human handle or agent id |
| `filed_at` | yes | ISO 8601 timestamp with TZ offset |
| `state` | yes | `open` (in `audit/`) or `resolved` (in `audit/resolved/`) |

---

## The four resolution states

Every audit lands in exactly one state. Never delete.

### `accept` — apply the correction

1. Locate the exact range in the target file. Use the `anchor_before` /
   `anchor_text` / `anchor_after` window; line numbers may have drifted
   since the audit was filed.
2. Apply the correction. Bump the target page's `updated:` frontmatter
   date. Run cascade-update scan per `llm-wiki-page-shape-contract` Rule 5
   — the fix may ripple to other pages.
3. Append a `# Resolution` section to the audit file:
   ```markdown
   # Resolution

   2026-05-20 · accepted.
   Fixed safety factor from 1.67 to 1.5 per DNV-OS-E301 (2023) table 4-2
   row 3. Added Edition history section noting 2018 → 2023 change.
   Cascade-updated: wikis/engineering/concepts/mooring-safety-factors.md
   (referenced the old value).
   ```
4. Move file from `audit/` to `audit/resolved/`. Filename unchanged.
5. Log in `log/YYYYMMDD.md`:
   ```
   ## [HH:MM] audit | resolved 20260520-143022-mooring-mbl-calc-error — accepted; fixed DNV-OS-E301 safety factor
   ```

### `partial` — apply some, not all

Same as `accept`, but the resolution section explains what was applied
and what was deferred. If the deferred portion needs follow-up, file a
new audit referencing this one's `id`. Log line includes ` — partial`.

### `reject` — feedback declined

1. Do not modify the target file.
2. Append a `# Resolution` section with the rejection rationale:
   ```markdown
   # Resolution

   2026-05-20 · rejected.
   The 1.67 value is correct for the legacy 2018 edition still cited by
   the upstream client's project basis-of-design (acma project 2024-03).
   The wiki page documents the value as legacy and the citation explicitly
   notes the edition. Not a bug.
   ```
3. Move file from `audit/` to `audit/resolved/`. Filename unchanged.
4. Log:
   ```
   ## [HH:MM] audit | resolved <id> — rejected; <one-line rationale>
   ```

**Never delete rejected audits.** Rejection history is valuable — it
prevents the same feedback being re-filed by a different reviewer next
month, and it documents the wiki's position on a contested point.

### `defer` — needs more research

1. Do not modify the target file.
2. Add the open question to `wikis/<domain>/CLAUDE.md` under an
   "Open research questions" section (create if missing).
3. Append a `# Resolution` section noting the defer:
   ```markdown
   # Resolution

   2026-05-20 · deferred.
   The 2023 revision text is paywalled; we cannot independently verify
   table 4-2 without the source document. Added to engineering wiki's
   open-questions list. Will re-process once we have the 2023 edition
   in `knowledge/wikis/engineering/wiki/standards/sources/`.
   ```
4. **Leave the audit in `audit/`** (NOT `audit/resolved/`). Deferred
   audits remain open until upgraded to `accept` / `partial` / `reject`.
5. Log:
   ```
   ## [HH:MM] audit | deferred <id> — <reason>
   ```

---

## Anchor-window resolution algorithm

When applying an audit's correction, the target file's line numbers may
have drifted since the audit was filed. The before/text/after window
makes the audit robust:

1. Search the target file for `anchor_text` (literal string match).
2. If exactly one match: verify the preceding ~3 lines match `anchor_before`
   and the following ~3 lines match `anchor_after`. If both match, apply.
3. If zero matches: the text was deleted or rewritten since the audit was
   filed. Re-read the audit body and either (a) find the equivalent new
   range, then apply, or (b) defer with reason "anchor text gone — need
   to re-locate intent".
4. If multiple matches: use `anchor_before` and `anchor_after` to
   disambiguate. If still ambiguous: defer with reason "ambiguous anchor".

This algorithm matches lewislulu's `audit-shared/src/anchor.ts` semantics.
A future Python port should live at `scripts/knowledge/audit_anchor.py`
when we have multiple audits to process programmatically.

---

## Processing cadence

| Cadence | What runs |
|---|---|
| Per session that touches a wiki page | Scan `audit/*.md` for that target before editing — open audits may already answer the question |
| Weekly (per `research/llm-wiki-cadence-governance`) | Process all `audit/<domain>/*.md` files; aim for ≤7 day median resolution time |
| Before any wiki PR | Lint pass per `llm-wiki-page-shape-contract` post-conversion checklist; audits against changed files must be processed first |

---

## Anti-patterns

- **Silently deleting audits** — even rejected ones. Rejection history matters.
- **Fixing the page without filing an audit** when feedback came from a non-author. The audit records *who flagged it* and *what was said* — critical for traceability.
- **Using audits for typo fixes** — single-character fixes are noise; just edit in place and log normally. Audits are for substantive corrections.
- **Filing an audit without an anchor window** — the audit is unprocessable; the anchor IS the surface area for resolution.
- **Resolving an audit by editing it instead of moving to `resolved/`** — leaves the inbox cluttered and breaks `audit_review.py` queries (when we build one).
- **Cross-domain audits without explicit target paths** — every audit is anchored to exactly one wiki page. If feedback spans multiple, file one audit per affected page and cross-reference via `related: [<other-audit-id>]` frontmatter.

---

## Hand-off back to `research/llm-wiki`

```bash
# Open audits for a domain wiki
ls /mnt/local-analysis/llm-wiki/wikis/<domain>/audit/*.md 2>/dev/null

# After applying a fix:
git add wikis/<domain>/<target-page>.md \
        wikis/<domain>/audit/resolved/<audit-id>.md \
        wikis/<domain>/log/YYYYMMDD.md
git rm wikis/<domain>/audit/<audit-id>.md
git commit -m "wiki(<domain>): resolve audit <id> — <action>; <one-line>" \
  -- wikis/<domain>/<target-page>.md \
     wikis/<domain>/audit/resolved/<audit-id>.md \
     wikis/<domain>/log/YYYYMMDD.md
```

Pathspec form `git commit -m "..." -- <files>` per
`feedback_multi_agent_commit_serialization`.

---

## What this skill is NOT

- Not for in-chat one-off corrections that don't need to survive context loss
- Not for typo fixes — just edit in place
- Not a CLI tool — this is the file-format contract; a Python `audit_review.py` script can be built later when audit volume justifies it
- Not for non-wiki repos — audits target wiki pages specifically

## Related must-fire rules

- `feedback_attestation_enables_contradiction_detection` — audit-driven contradictions are a defect class, not noise
- `feedback_silent_verdict_flip_defect_class` — standards-page audits should check section + edition, not just code_id
- `feedback_n_night_blocker_promote_to_replan` — if the same defect class keeps re-filing across audits, the underlying wiki structure may need a redesign, not another fix
- `feedback_never_offer_to_self_label_plan_approved` — high-severity audits proposing major restructure should route through a planned issue, not direct-apply
- `feedback_subagent_write_phantom` — if a subagent processes audits, main session verifies the `audit/` → `audit/resolved/` move actually happened on disk
