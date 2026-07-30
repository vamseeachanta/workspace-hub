> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-30
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_validation_chain_bsee_first_then_interpretation.md

---
name: feedback_validation_chain_bsee_first_then_interpretation
description: Validation must run source-definitions-first (BSEE direct) → wed interpretation → analysis → published page → validation blog; definitions get ONE canonical home the code imports
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 8039d273-5c09-4441-a95a-d38206061b75
  modified: 2026-07-29T02:37:52.090Z
---

**Owner directive (2026-07-28, wed #1063 epic): "our validation should go through BSEE direct definitions... followed by wed interpretations etc." and "this kind of coherence is missing".**

**The required chain, in authority order — never skip or reorder:**
1. **Source-published definition** (BSEE direct: data dictionary, form instructions, CFR, portal field defs) — cite URL + retrieval date.
2. **wed interpretation** — only where tier 1 is silent, and **labelled as inference** with its evidence. Never presented as if published.
3. **Analysis / verdict** built on 1+2, every figure footnoted to its provenance.
4. **Published validation HTML** → `reports/lower_tertiary/*.html`, copied by `scripts/build_pages.py` into PUBLIC, and synced to aceengineer.com.
5. **Validation blog** — narrative record so the work is not re-churned. ⚠️ **The pipeline ALREADY EXISTS and was unused**: `aceengineer-website/config/content-sync.yaml` has `source: docs/` → `action: extract_blog` → `destination: src/blog/`, pattern `*.md`. Write the narrative as markdown under wed `docs/` and it flows to the website blog.

**What "coherence is missing" meant concretely (the failure to avoid):** the WAR activity-code table existed in THREE disconnected places — `docs/data-sources/bsee/data/WELL_ACTIVITY_CD/well_activity_cd_description.md` (and it is probably the WRONG domain, actually `BOREHOLE_STAT_CD`), a second hand-maintained copy in code at `lower_tertiary/ops_timeline.py:59` (`WAR_ACTIVITY_LABELS`), and prose scattered across issue bodies. Neither table imports the other, nothing declared which was authoritative, BSEE's own shipped definition files may be discarded at extraction, and no blog existed despite the pipeline being wired.

**RULE: definitions get ONE canonical home that CODE IMPORTS.** A doc table and a code dict that are maintained separately will diverge — that is the same defect class as the four/six drilling-day implementations. Doc and code must be generated from, or import, the same artifact.

**RULE: label provenance per row.** Every definition carries published / inferred / unknown. An invented meaning (e.g. for `PND`) propagates into published economics.

**RULE (owner, 2026-07-28): every UNKNOWN or ASSUMED item gets a FOOTNOTE on EVERY published surface — the validation blog included, not just the validation page.** The narrative surface must carry the same honesty apparatus as the data surface; a blog that reads as settled while the page carries the caveats is how an assumption gets laundered into fact. Footnote text should say what is unknown, what was assumed instead, what evidence supports the assumption, and what would settle it. Same numbering/footnote set reused across page and blog so the two cannot drift.

Related: [[project_dc_days_root_cause_war_codes]] [[feedback_report_hub_design_system]] [[feedback_document_discovered_data_sources_as_issues]] [[feedback_unique_live_links_traffic_credibility]]
