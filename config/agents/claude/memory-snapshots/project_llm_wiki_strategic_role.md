---
name: llm-wiki strategic role — trunk for code, clients, chatbots
description: llm-wiki is the basis and lifeline for all downstream knowledge consumers (code, client work, chatbots); improved/uplifted via public + legally-sanitized private sources
type: project
originSessionId: 16551784-4b91-4e6e-a344-efbed44673ec
---
`vamseeachanta/llm-wiki` is positioned as the **basis and lifeline** for all
downstream knowledge consumers: production code, client deliverables,
chatbots/agents, and other grounding surfaces. Stated by the user on
2026-05-07.

The repo is improved / uplifted / added to / progressed using two source
classes:

1. **Public sources** — engineering standards, published literature, public
   methodology references. Current dominant input.
2. **Private, legally sanitized sources** — internal notes, paid-standard
   reading, vendor PDFs, client-engagement learnings. *Sanitization-first*:
   synthesize methodology in own words, cite the canonical public standard,
   never paste license-restricted verbatim content.

**Why:** if downstream chatbots, code, and client deliverables ground on
llm-wiki, the wiki's coverage, quality, and license discipline become
load-bearing for the whole knowledge stack. A gap in llm-wiki = a gap in
every chatbot answer and every client deliverable that depends on it. A
license violation in llm-wiki = contamination of every downstream artifact
that ingests it. Conversely, each uplift compounds across all consumers.
This re-purposes the existing citation contract
(`workspace-hub/.claude/rules/calc-citation-contract.md`) from "calc-output
traceability" to "downstream-trust safety" — same mechanism, bigger stakes.

**How to apply:**

1. **Bias toward improvement work on llm-wiki.** When a session would
   otherwise produce one-off notes that conceptually belong in the wiki
   (engineering methodology, standards-derived constants, domain glossary
   entries), prefer routing the effort into a sourced wiki page with
   proper `code_id` / `publisher` / `revision` frontmatter rather than
   scratch notes in some other repo.
2. **Treat private-source work as sanitization-first.** Before drafting
   from internal or paid material:
   - Identify the public-source equivalent that can be cited.
   - Restate methodology in own words; never copy formulas/tables
     verbatim from license-restricted material.
   - Cite the canonical standard or primary literature, not the vendor
     derivative — per the `wikis/*/wiki/sources/` deny-list in the
     citation contract.
3. **Promotion path is the central workflow.** External-intel logs at
   `/mnt/ace/llm-wiki/docs/external-intel.md` are *pre-promotion holding
   pens*. When a non-vendor source corroborates a topic captured there,
   promote it to `wikis/<domain>/wiki/<slug>.md` with frontmatter and
   primary-source citations. The pre-promotion → published flow is the
   productive output, not the holding pen itself.
4. **Coverage gaps are first-class defects.** A missing wiki page on a
   topic that downstream code/chatbots need is a real product hole, not
   a docs miss. Track gaps the way you'd track bugs.
5. **License discipline is non-negotiable.** Vendor-marketing posts,
   paywalled excerpts, client-confidential material — none of these go
   into `wikis/`. Side-channel route: `/mnt/ace/llm-wiki/docs/` per the
   off-repo intel routing convention.
6. **Schema discipline = downstream programmability.** Pages without
   frontmatter (`code_id`, `publisher`, `revision`) cannot be
   programmatically resolved by chatbots or citation systems. Treat
   missing frontmatter as a defect even on otherwise-good prose pages.

**Cross-references:**

- `feedback_offrepo_intel_routing.md` — where intel that doesn't belong
  in published llm-wiki goes.
- `project_llm_wiki_spunout.md` — repo location, license boundary,
  pipeline-stays-in-workspace-hub mechanics.
- `project_doc_intel_operating_model.md` — doc-intel parent program
  context.
- `workspace-hub/.claude/rules/calc-citation-contract.md` — the
  schema-and-citation discipline that makes llm-wiki pages programmable.
