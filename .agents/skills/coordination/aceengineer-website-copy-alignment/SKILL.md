---
name: aceengineer-website-copy-alignment
description: Verify proposed copy changes to vamseeachanta/aceengineer-website against canonical sources in workspace-hub (llm-wiki, live site, strategy repo) before shipping. Produces a GitHub issue on the site repo documenting the check with a Match / Drift / Gap verdict.
version: 1.0.0
author: Codex
license: MIT
metadata:
  tags: [aceengineer, website, copy-review, canonical-check, design-system, cross-repo]
  related_skills: [llm-wiki-roadmap-integration, knowledge-source-recon, llm-wiki-ecosystem-gap-to-issues, ecosystem-terminology]
---

# AceEngineer Website Copy Alignment

## Use when

- A&CE Design System project (separate Codex.ai project) hands off a copy review and defers the canonical check to Codex because it cannot reach workspace-hub.
- About to ship lede / hero / capability / service-line / firm-description text changes to `aceengineer-website`.
- User says things like: "check the About page against llm-wiki", "does this copy match our canonical phrasing?", "before we ship this to aceengineer.com verify it against workspace-hub".

**Do NOT** run this on every aceengineer-website commit — scope is copy/marketing/firm-positioning text only. Build-system, JS, CSS, asset changes do not need this skill.

## Canonical source map

The canonical source for site copy is **NOT llm-wiki** — that is the #1 trap from the 2026-04-24 handoff that surfaced this skill. Consult sources in this priority order:

| Priority | Source | Path | What lives here | Privacy |
|---|---|---|---|---|
| 1 | **Live `about.html` / `engineering.html` / `services.html`** | `aceengineer-website/content/*.html` and repo-root `*.html` | Shipped firm framing, positioning lines, capability headings, schema.org descriptions — already public. | Public. |
| 2 | **`aceengineer-strategy` positioning docs** | `aceengineer-strategy/strategy/{positioning,go-to-market,ideal-customer,competitors,pricing-model}.md` | **True canonical** firm positioning, forbidden phrases, target headlines, credential claims. | **PRIVATE — do not quote verbatim in public issues.** See Privacy Wall below. |
| 3 | **llm-wiki curated pages** | `knowledge/wikis/{engineering,marine-engineering,naval-architecture,maritime-law}/wiki/` | Methodology, domain concepts, standards. **Explicitly out of scope for firm copy** per `engineering/wiki/overview.md`. | Public (git-tracked). |
| 4 | **llm-wiki raw papers** | `knowledge/wikis/engineering/raw/papers/` | Drafts, synthesis notes, strategy write-ups. Sometimes has recent positioning language before it lands in `aceengineer-strategy`. | Public — but review carefully, some docs are intended as internal. |
| 5 | **Tier-1 repo READMEs** | `{assetutilities,digitalmodel,worldenergydata,assethold,OGManufacturing}/README.md` | Package capability descriptions — useful when copy mentions specific modules. | Public. |

Resolve the llm-wiki data root programmatically:
```
python3 scripts/data/llm-wiki/resolve_wiki_path.py
```
Resolution order: `$LLM_WIKI_DATA_DIR` → `config/llm-wiki.yaml:data_dir` → `data/llm-wiki` → fallback `knowledge/wikis`.

### No embedded llm-wiki in tier-1 repos

Per the 2026-04-23 decision (GH #2398 CLOSED — _llm-wiki stays embedded in hub_), none of `assetutilities / digitalmodel / worldenergydata / assethold / OGManufacturing / aceengineer-website` contain an `llm-wiki/` subtree. If you find one, that is news and the decision may have been reversed — re-read `.Codex/memory/project_llm_wiki_stays_embedded.md` before proceeding.

## Privacy Wall

The `aceengineer-strategy` repo's agent-config enforces a privacy wall (see that repo's `.Codex/` directory for the authoritative policy):
- No cross-references to public engineering repos
- No PII in commits (contact details, deal terms, pricing specifics)

When filing the **public** issue on `vamseeachanta/aceengineer-website`:

| Safe to cite publicly | Must NOT appear in the public issue |
|---|---|
| Live site copy (it's already public) | Revenue targets, ARR numbers, retainer pricing |
| Schema.org / meta / OG tag content | Prospect names, target account lists |
| Public tier-1 repo READMEs | WRK-NNN identifiers from aceengineer-strategy |
| Public GitHub issue numbers | Direct quotes from `aceengineer-strategy/strategy/*.md` |
| Paraphrased positioning rules (e.g. "firm, not consultancy") | Quoted positioning text verbatim |

**Rule of thumb:** if it's not already visible on `aceengineer.com` or in a public repo, don't reproduce it. Derive the rule, cite the live-site evidence.

## Steps

1. **Load context.**
   - Read `.Codex/memory/MEMORY.md` for recent aceengineer-related entries.
   - Read the handoff / design-review notes the user pasted (the proposed copy + surrounding context).
   - `cd /mnt/local-analysis/workspace-hub && git status` — verify clean state.

2. **Identify what is being changed.** Classify the copy by type:
   - **Firm description / lede** (who we are) → priority sources: 1, 2
   - **Service lines / capability titles** → priority sources: 1 (`engineering.html`), 2 (`positioning.md`)
   - **Domain/technical descriptions** → priority sources: 1, 3 (llm-wiki IS in scope here)
   - **Credentials / numbers** → priority sources: 1 (schema.org), 2 (`positioning.md` Core Differentiation table), 5 (tier-1 READMEs for module counts)

3. **Search canonical sources in priority order.** Typical commands:
   ```bash
   # Public sources first
   grep -E '<meta name="description"|"description":' /mnt/local-analysis/workspace-hub/aceengineer-website/{about,index,services,engineering,contact,faq}.html 2>/dev/null
   grep -E 'class="(section-title|lead|hero)' /mnt/local-analysis/workspace-hub/aceengineer-website/*.html

   # Private strategy (read for context, don't quote in public issue)
   grep -rli -E '<keywords>' /mnt/local-analysis/workspace-hub/aceengineer-strategy/strategy/

   # llm-wiki (likely a miss for firm copy, but scan domain-related claims)
   cd /mnt/local-analysis/workspace-hub/knowledge/wikis && grep -rli -E '<keyword>' .

   # Tier-1 READMEs
   grep -l -E '<module claim>' /mnt/local-analysis/workspace-hub/{assetutilities,digitalmodel,worldenergydata,assethold,OGManufacturing}/README.md
   ```

4. **Classify the verdict.** Exactly one of:
   - **A — MATCH**: proposed copy aligns with priority-1/2 canonical sources. No change needed. Issue is "verified, no action".
   - **B — DRIFT**: canonical source(s) say something different or better. Capture the diff in a table so the design-system session can patch on the next pass.
   - **C — GAP**: canonical source doesn't cover this copy type. Decide whether (a) the proposed copy should become the new canonical (and where it should live) or (b) a new canonical-source doc should be authored first.
   - A verdict can be **B+C hybrid** when drift is found against priority-1 (live site) AND priority-3 (llm-wiki) doesn't cover the topic. State both.

5. **Ensure labels exist on `vamseeachanta/aceengineer-website`.** Handoff template uses `content` and `design-system` — create them if missing (one-time, idempotent):
   ```bash
   gh label create content --repo vamseeachanta/aceengineer-website \
     --description 'Copy, wording, text content changes' --color 0E8A16 2>/dev/null
   gh label create design-system --repo vamseeachanta/aceengineer-website \
     --description 'A&CE Design System alignment' --color 5319E7 2>/dev/null
   ```

6. **File the issue** using the template below. The title pattern is:
   ```
   <page/section> — align <topic> with <canonical-source-name> canonical copy
   ```

7. **Report back to the user with a one-liner** and — if verdict B — also paste the recommended replacement text so it can be dropped straight into the design-system session:
   ```
   Filed <issue-url> — verdict: <A/B/C>. <Next action.>
   ```
   For verdict B, include the recommended new lede verbatim as a quoted block in the chat reply.

8. **Do NOT self-commit copy changes** to `aceengineer-website` from this skill. The skill is review-only. The design-system session owns the edit; this skill verifies and documents.

## Issue template

```
## Source

Flagged during <source-context> (<YYYY-MM-DD>). <Who deferred to Codex and why>.

## Proposed copy (under review)

> <paste proposed copy verbatim>

## llm-wiki (workspace-hub) check

- **Path checked:** <paths>
- **Tier-1 repos scanned:** assetutilities, digitalmodel, worldenergydata, assethold, OGManufacturing, plus aceengineer-website. <presence/absence of llm-wiki in each>
- **Verdict:** **<A/B/C>**. <One-paragraph rationale citing `knowledge/wikis/engineering/wiki/overview.md` scope lock if relevant.>

## Cross-check against <the-actual-canonical-source>

<Table: dimension | canonical says | proposed says | conflict?>

## Recommendation

<Numbered list, 2-5 items>

## Files affected

<List — do NOT include proposed edits here, this issue documents the check only>

## Done when

- <testable acceptance criteria>
- Cross-referenced in design-system HANDOFF.md exit notes

---
_Verification trail: <file:line citations to public sources only>._
```

## Pitfalls

| Rationalization | Reality |
|---|---|
| "llm-wiki is the obvious canonical source for firm copy." | It is not. `knowledge/wikis/engineering/wiki/overview.md` locks scope to methodology. Firm copy lives in `aceengineer-strategy` (private) and the live site itself. |
| "I'll just quote positioning.md in the issue for completeness." | Privacy wall breach. Paraphrase the rule, cite live-site evidence that embodies it. |
| "No canonical match means just ship the proposed copy." | No — verdict C means the canonical source should be decided and (optionally) created first. Shipping without a canonical source is what creates future drift. |
| "Proposed and live copy use different words but probably mean the same thing." | The live `about.html` contains *explicit negative constraints* (e.g. "We deliver automated workflows, not consulting hours" and "AceEngineer is the firm … not a contractor with a laptop"). Treat explicit negatives in live copy as hard canonical rules; any synonym that lands on the forbidden side (e.g. "consulting practice") is a drift, not a rephrasing. |
| "I should file the issue AND fix the copy in the same PR." | No. Review-and-file only. The design-system session owns the edit. Mixing roles means a broken design-system exit note and a stale canonical-check paper trail. |
| "Labels `content` / `design-system` already exist — skip the create step." | They didn't on 2026-04-24. `gh label create` is idempotent when guarded with `2>/dev/null`; run it unconditionally. |
| "A match is boring; no issue needed." | File it anyway. A recorded "verified, no action" closes the loop so the next design-system session doesn't re-request the same check. |

## Iron Law

> Every copy change targeting `aceengineer-website` that originates from the A&CE Design System project exits through a filed issue on `vamseeachanta/aceengineer-website` tagged `content,design-system`, with an explicit Match / Drift / Gap verdict grounded in at least one priority-1 (live-site) citation.

## Example execution (2026-04-24)

- Trigger: design-system `about.html` lede review, handoff from separate Codex.ai project.
- Proposed lede introduced "consulting practice" framing.
- Live `about.html` already rejected that framing ("We deliver automated workflows, not consulting hours"; "AceEngineer is the firm ... not a contractor with a laptop").
- Verdict: **B+C** (DRIFT against live site + GAP in llm-wiki).
- Outcome: issue filed at `vamseeachanta/aceengineer-website#6`.
