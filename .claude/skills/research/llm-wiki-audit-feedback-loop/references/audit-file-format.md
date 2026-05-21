# Audit file format — full specification

Concrete format for `wikis/<domain>/audit/<id>.md` files. Adapted from
[lewislulu/llm-wiki-skill audit-shared](https://github.com/lewislulu/llm-wiki-skill).

---

## Filename convention

```
<YYYYMMDD>-<HHMMSS>-<short-slug>.md
```

- `YYYYMMDD-HHMMSS` is when the audit was filed (local time, no separator)
- `short-slug` is kebab-case, 3–6 words, describes what the feedback is about
- Filename must match the `id:` frontmatter field exactly

Examples:
```
20260520-143022-mooring-mbl-calc-error.md
20260520-151105-orcaflex-version-drift.md
20260520-180937-dnv-os-e301-edition-history-missing.md
```

---

## Frontmatter spec

```yaml
---
id: <YYYYMMDD-HHMMSS-slug>                # matches filename
target: wikis/<domain>/<path>/<page>.md   # repo-relative
anchor_before: |                          # ~3 lines preceding anchor_text
  <verbatim text>
anchor_text: |                            # exact text the comment is about
  <verbatim text>
anchor_after: |                           # ~3 lines following anchor_text
  <verbatim text>
severity: low | medium | high             # processing priority
action: revise | remove | clarify | annotate-contradiction
filed_by: <handle>                        # human handle or agent id
filed_at: <ISO 8601 with TZ>              # e.g., 2026-05-20T14:30:22-05:00
state: open | resolved
related: [<other-audit-id>]               # optional; for multi-page feedback
---
```

### Field semantics

| Field | Required | Notes |
|---|---|---|
| `id` | yes | Stable identifier; filename must match |
| `target` | yes | Repo-relative path; never absolute |
| `anchor_before` | yes | Block-literal `\|` form; preserves leading whitespace and newlines |
| `anchor_text` | yes | The text range the comment is about; verbatim from target |
| `anchor_after` | yes | Block-literal form |
| `severity` | yes | `low` (cosmetic / minor), `medium` (factual / clarity), `high` (incorrect calc, broken citation, contradicts source) |
| `action` | yes | What kind of fix is being proposed (see below) |
| `filed_by` | yes | `vamsee` / `claude-session-<id>` / `codex-session-<id>` / `gemini-session-<id>` |
| `filed_at` | yes | ISO 8601 with explicit TZ offset |
| `state` | yes | `open` while in `audit/`; `resolved` once moved to `audit/resolved/` |
| `related` | no | List of other audit IDs for multi-page feedback |

### Action types

| Action | Meaning |
|---|---|
| `revise` | Replace text with corrected version |
| `remove` | Delete text without replacement |
| `clarify` | Existing text is ambiguous; rewrite for clarity |
| `annotate-contradiction` | Two sources disagree; add side-by-side annotation |

---

## Body spec

```markdown
# Feedback

<Free-form markdown describing what is wrong / missing / contradictory.
Cite sources where applicable.>

# Recommended action

<Specific proposed fix. Include verbatim replacement text where
applicable. If the audit author has a strong preference for how the
fix should land, state it here; the processor can override with
rationale.>
```

Optional sections:

```markdown
# Related sources

- [[summaries/<slug>]] — source supporting the feedback
- <URL> — external source

# Why this matters

<Optional 1–3 sentence justification — why is this worth filing as an
audit rather than fixing inline?>
```

---

## Resolution section (appended on close)

```markdown
# Resolution

<YYYY-MM-DD> · <accepted | partial | rejected | deferred>.
<1–4 sentences describing what was done and why.>
Cascade-updated: <list of other pages touched, if any>.
```

Examples by resolution state:

### Accept

```markdown
# Resolution

2026-05-20 · accepted.
Fixed safety factor from 1.67 to 1.5 per DNV-OS-E301 (2023) table 4-2
row 3. Added Edition history section noting 2018 → 2023 change.
Cascade-updated: wikis/engineering/concepts/mooring-safety-factors.md.
```

### Partial

```markdown
# Resolution

2026-05-20 · partial.
Applied the safety factor fix (1.67 → 1.5). Deferred the
edition-history section — needs the 2018 edition text to do justice
to the change log. Filed follow-on audit 20260520-184411-dnv-edition-history.
```

### Reject

```markdown
# Resolution

2026-05-20 · rejected.
The 1.67 value is correct for the legacy 2018 edition still cited by
the upstream client's project basis-of-design (acma project 2024-03).
The wiki page documents the value as legacy and the citation explicitly
notes the edition. Not a bug.
```

### Defer

```markdown
# Resolution

2026-05-20 · deferred.
The 2023 revision text is paywalled; we cannot independently verify
table 4-2 without the source document. Added to engineering wiki's
open-questions list (wikis/engineering/CLAUDE.md). Will re-process
once we have the 2023 edition under wikis/engineering/sources/refs/.
```

Deferred audits remain in `audit/` (NOT `audit/resolved/`) until upgraded.

---

## Lifecycle state machine

```
   ┌─────────┐
   │  open   │  in audit/
   └────┬────┘
        │
        ├──── accept ────────┐
        │                    │
        ├──── partial ───────┤
        │                    ▼
        ├──── reject ───► resolved
        │                  in audit/resolved/
        │                    ▲
        └──── defer ─────────┘
              (stays in audit/)
              upgrade later
```

`defer` is the only non-terminal state. Every other resolution moves
the file to `audit/resolved/` and is final.

---

## Anti-patterns

- Filename does not match `id:` — breaks `audit_review.py` lookups
- `anchor_text` is paraphrased rather than verbatim — anchor algorithm fails
- `anchor_before` / `anchor_after` are empty or 1 line — ambiguous in long files
- Resolution appended without moving file to `resolved/` — clutters open inbox
- Rejected audit deleted entirely — loses rejection history
- Multi-page feedback in one audit — split into one audit per target page; cross-reference via `related:`
- Block-literal `\|` collapsed to flow-style `>` — loses leading whitespace and breaks anchor matching on indented code/quotes

---

## Future tooling

A `scripts/knowledge/audit_review.py` script can be built when audit
volume justifies it. The expected interface:

```bash
# List open audits across all domain wikis
uv run scripts/knowledge/audit_review.py --all-domains

# List open audits for one wiki, grouped by target page
uv run scripts/knowledge/audit_review.py --wiki engineering --open

# Show specific audit by id
uv run scripts/knowledge/audit_review.py --id 20260520-143022-mooring-mbl-calc-error

# Re-locate anchor in target file (drift check)
uv run scripts/knowledge/audit_review.py --id <id> --locate
```

Output should match the SKILL.md lifecycle vocabulary so processing
sessions can be scripted.
