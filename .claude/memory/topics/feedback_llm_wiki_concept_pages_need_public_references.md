> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-22
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_llm_wiki_concept_pages_need_public_references.md

---
name: llm-wiki concept pages need public references
description: Concept pages in vamseeachanta/llm-wiki added from external posts must be grounded with public concrete references (textbooks, ISBN/DOI-cited papers, public-domain manuals) — not left sourced only to the trigger post
type: feedback
originSessionId: 714b2423-3b30-4ff5-8d73-dca937209407
---
Concept pages added to vamseeachanta/llm-wiki from external/social-media sources (LinkedIn posts, blog articles, practitioner essays) must be grounded with **public concrete references** — verified textbooks, standards-with-DOI/ISBN, or public-domain technical manuals — not left sourced solely to the LinkedIn/blog post that triggered the ingest. The trigger post belongs only on the `sources/` page (which is a summary of THAT specific post); the `concepts/` page must anchor on the broader public-citable literature.

**Why:** llm-wiki is CC-BY-4.0 — a synthesis wiki, not a link-repository. A concept page sourced only to a single LinkedIn essay fails the schema's lint-workflow criterion #6 ("data gaps fillable by external sources") on day one. The trigger post is the *prompt*; the textbook/standard references are the *anchor*. Confirmed by user explicit feedback 2026-05-07: after the first-draft Rötzer wave-shoaling concept page cited only the LinkedIn post, user said "research if needed" and required public concrete references before commit. Result: USACE CEM, Wienke & Oumeraci 2005 (DOI 10.1016/j.coastaleng.2004.12.008), Dean & Dalrymple 1991, Goda 2010, Battjes & Janssen 1978 added before the commit landed.

**How to apply:**

- The `sources/<post-slug>.md` page can and should cite only the post — it's a summary of that one source. URL preserved, brief Relevance + Use-as-wiki-source sections.
- The `concepts/<topic>.md` page (if a gap-fill concept page is being created from the post) must have a dedicated "Public references" section listing verified citables. Verify titles, authors, years, DOIs, and ISBNs via WebSearch before commit — mis-citing in a public OSS commit is worse than no citation.
- Prefer references in this order: (1) public-domain manuals (USACE CEM, NOAA, USGS); (2) canonical textbooks with stable ISBNs; (3) DOI-cited journal papers from publishers (Elsevier, Wiley, Springer, World Scientific); (4) classic conference proceedings (e.g., ICCE for coastal engineering).
- Cross-link existing in-wiki source pages (e.g., the PNA series, Tupper's Introduction to Naval Architecture) rather than restating their citations — keeps the existing source pages authoritative for their texts and avoids citation duplication.
- Skip an unverified citation rather than commit-then-patch. A reference you almost remember is worse than one you've confirmed.
- Log entry should record the references added (with DOI/ISBN where applicable) so the audit trail captures the grounding, not just the trigger.
