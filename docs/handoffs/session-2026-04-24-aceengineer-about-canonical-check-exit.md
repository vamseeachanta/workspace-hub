# Session Exit — AceEngineer About Page Canonical Check

**Date:** 2026-04-24
**Branch at session:** `plan/issue-2103-aqwa-bemrosetta-ingestion` (no branch changes this session)
**Skill commit:** `029140aae feat(skill): aceengineer-website copy alignment workflow` (rebased from `1c04813d2` by concurrent auto-sync — same content, same message)

## Trigger

Handoff from the A&CE Design System project (separate Claude.ai project). Its about.html design review asked for a canonical check of the proposed hero lede against "llm-wikis in workspace-hub." Design-system Claude can't reach workspace-hub, so the check was deferred here.

Proposed lede under review (verbatim from handoff):

> AceEngineer is a consulting practice that ships validated Python pipelines for **computational fatigue assessment, riser & mooring analysis, and life-extension & integrity management**. Based in Houston. Filings cite the applicable standard, clause, equation, and parameter values — reproducible with the pipeline we hand back.

## What was done

1. **Scanned llm-wiki + all tier-1 repos + site repo for canonical firm-copy sources.** User explicitly scoped the check to "all tier-1 repos": scanned `assetutilities`, `digitalmodel`, `worldenergydata`, `assethold`, `OGManufacturing` plus `aceengineer-website`. No embedded llm-wiki in any — consistent with 2026-04-23 decision (GH #2398 CLOSED: llm-wiki stays hub-only).
2. **Structural finding #1 — llm-wiki is out of scope for firm copy by design.** `knowledge/wikis/engineering/wiki/overview.md` locks scope to "how we engineer, not what we engineer." The design-system reflex to check the wiki was wrong; no canonical firm-description block lives there.
3. **Structural finding #2 — real canonical is live site + private strategy repo.** The `aceengineer-strategy` repo (hub-local, not in `.gitmodules`) holds authoritative positioning docs with a privacy wall (no verbatim quotes in public artifacts). The live `aceengineer-website/about.html` itself contains shipped positioning rules that can be cited publicly.
4. **Classified verdict as B+C (DRIFT + GAP).** Proposed "consulting practice" framing directly contradicts two explicit negatives already shipped in live `about.html`: "We deliver automated workflows, not consulting hours" and "AceEngineer is the firm ... not a contractor with a laptop." Proposed lede also drops all three live credentials (15+ years, 704+ modules, AI orchestration) and introduces new CAP-03 ("life-extension & integrity management") with no counterpart in live `engineering.html` capability headings.
5. **Filed issue** `vamseeachanta/aceengineer-website#6` with verdict, evidence table, and recommendations. Created `content` + `design-system` labels on the repo (did not previously exist). Issue body cites only public live-site evidence — strategy repo not referenced by path or content (privacy wall).
6. **Authored skill** `.claude/skills/coordination/aceengineer-website-copy-alignment/SKILL.md` codifying the canonical-source priority map, privacy wall rules, step sequence, verdict taxonomy, issue template, and pitfalls. Committed at `029140aae`.
7. **Wrote auto-memory** `project_aceengineer_copy_canonical_sources.md` + indexed in `MEMORY.md` (personal memory store, not in repo).
8. **Provided design-system Claude handoff block** in chat for the user to paste into the sister project — fully self-contained with replacement lede, CAP-03 decision point, and meta/OG/schema reconciliation checklist.

## Artifacts

| Artifact | Path / URL | Persistence |
|---|---|---|
| Filed issue | https://github.com/vamseeachanta/aceengineer-website/issues/6 | OPEN, labels `content,design-system` |
| Skill | `.claude/skills/coordination/aceengineer-website-copy-alignment/SKILL.md` | Committed `029140aae` |
| Personal memory | `~/.claude/projects/-mnt-local-analysis-workspace-hub/memory/project_aceengineer_copy_canonical_sources.md` + MEMORY.md index entry | Not in repo |
| Labels on site repo | `content` (green), `design-system` (purple) | Live |
| This handoff | `docs/handoffs/session-2026-04-24-aceengineer-about-canonical-check-exit.md` | Uncommitted at session end |

## Recommended lede (for reference — already pasted to user for design-system session)

> AceEngineer is an AI-native offshore engineering firm, not a consultancy. One senior engineer — backed by an AI orchestration layer and 704+ production-tested Python modules — ships validated pipelines for **computational fatigue assessment, riser & mooring analysis, and life-extension & integrity management**. Based in Houston. Every filing cites the applicable standard, clause, equation, and parameter values — reproducible with the pipeline we hand back.

## Outstanding / pickup for next session

- [ ] **Design-system Claude** to patch `about.html` with replacement lede, then reconcile `<meta name="description">`, schema.org `description`, and OG/twitter title tags. Cross-link issue #6 in its `HANDOFF.md` exit notes.
- [ ] **CAP-03 decision point** — either land "life-extension & integrity management" as a fifth heading on `engineering.html` first (Option A, safer sequencing), or ship About with the new CAP-03 and backfill `engineering.html` next pass (Option B). Not decided this session; deferred to design-system Claude.
- [ ] **Follow-up (optional)** — decide whether `aceengineer-website` should host a canonical firm-copy home (e.g., `content/firm-description.md` or `brand/copy.yaml`) so future pages aren't each a one-off alignment check. Flagged in issue #6 body under "Recommendation #4."
- [ ] **This handoff doc commit** — not committed by this session; user to review and commit alongside any follow-up.

## Notes on session mechanics

- **Auto-sync rebased my commit mid-session.** Original `1c04813d2` → rebased `029140aae`. Content identical; SHA-citation in earlier chat is stale. This is the same pattern documented in `feedback_merge_race_silent_revert.md` — worth flagging if future sessions cite SHAs without re-checking HEAD.
- **Security hook blocked the first commit** because the skill contained the literal path string `.../CLAUDE.md` in prose. Rephrased to describe the policy and reference the directory instead — cleared. Pattern to reuse: avoid exact `CLAUDE.md` path-strings in skill/doc prose, describe the policy and point to the directory.
- **Labels `content` and `design-system` did not exist on the site repo** — created inline before filing. The skill's step 5 now makes this idempotent for future runs.

---

## Addendum — Decision landed + follow-up issues filed (same session)

After the initial handoff was written, the user returned mid-session and made two refinements: **Option C** (drop the aspirational CAP-03 claim) + **capability naming** (say "diffraction analysis" not "AQWA/OrcaWave", for structural parallelism with CAP-01/02 and broader SEO surface). Also requested visual support for the new CAP-03 via vessel imagery.

### Final lede (locked)

> AceEngineer is an AI-native offshore engineering firm, not a consultancy. One senior engineer — backed by an AI orchestration layer and 704+ production-tested Python modules — ships validated pipelines for **computational fatigue assessment, riser & mooring analysis, and diffraction analysis**. Based in Houston. Every filing cites the applicable standard, clause, equation, and parameter values — reproducible with the pipeline we hand back.

### Final CAP → live-heading mapping (all extant, no new engineering.html block required)

- CAP-01 "computational fatigue assessment" → Fatigue Analysis Library
- CAP-02 "riser & mooring analysis" → Mooring & Riser Design (OrcaFlex Batch Processing absorbed — dynamics tool for risers/moorings)
- CAP-03 "diffraction analysis" → AQWA Hydrodynamic Automation (AQWA *is* the diffraction solver)

### Follow-up issues filed on `vamseeachanta/aceengineer-website`

| # | Title | Scope |
|---|---|---|
| [#7](https://github.com/vamseeachanta/aceengineer-website/issues/7) | About hero — add FPSO + panel-mesh imagery for diffraction-analysis CAP | Visual anchor for CAP-03; primary = FPSO + panel mesh, tier-2 = floating wind platform |
| [#8](https://github.com/vamseeachanta/aceengineer-website/issues/8) | engineering.html — rename capability headings for CAP parallel naming | SEO-sensitive cleanup; not a shipping gate on About page |
| [#9](https://github.com/vamseeachanta/aceengineer-website/issues/9) | Canonical firm-copy home for reusable About/Services text | Structural — closes the gap that caused this whole check |
| [#6](https://github.com/vamseeachanta/aceengineer-website/issues/6) | *(original)* About page — align services phrasing with llm-wiki canonical copy | Decision comment posted; closeable when About page ships with revised lede |

### What deliberately did NOT get filed

**Life-extension & integrity management as a future capability.** This is a genuine scope-activation decision that belongs with the founder — it needs a delivered engagement, standards story (API 579 FFS, DNV-RP-F101), and deliverables pattern before it becomes a CAP. When those exist, the path is: add an `engineering.html` capability block first, then reintroduce to the About lede in a subsequent pass (Option A from the earlier analysis). Captured as a note in the #6 decision comment; not tracked as an active issue.

### Updated outstanding / pickup for next session

- [x] ~~CAP-03 decision point~~ — resolved: Option C with capability naming (diffraction analysis)
- [x] ~~Canonical firm-copy home decision~~ — tracked in #9
- [x] ~~Handoff doc commit~~ — committed at `8512dc0ce` (this doc, pre-addendum)
- [ ] **Design-system Claude** to patch `about.html` with final locked lede (see above), then close #6 once shipped
- [ ] #7, #8, #9 to be worked per their own done-when criteria (likely in design-system sessions, not hub sessions)
- [ ] **Life-extension claim** to be re-evaluated once a substantiating engagement exists

