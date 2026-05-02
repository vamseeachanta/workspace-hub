> Git-tracked snapshot from Claude auto-memory. Captured: 2026-04-28
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_recruiter_engagement.md

---
name: Recruiter engagement criteria — consulting-level and credible-source only
description: Do not draft replies to generic drive-by recruiter outreach; user only engages at consulting level from very credible reach-out sources
type: feedback
originSessionId: 512141a1-fd1b-4872-bcc8-66a1e93059d6
---
The user only engages with recruiter outreach when both of these hold:
- **Consulting-level role** (not generic IC/staff positions that don't match senior experience)
- **Very credible reach-out source** — not drive-by link spam, not generic outreach blasting many candidates

**Why:** Generic recruiter outreach (e.g., a single `kloudhire.com` URL with no personalization, "OPEN rate", no role-specifics) does not match the user's experience level and wastes response effort. The user has deep O&G + marine engineering + AI-automation expertise; responding to low-quality outreach signals availability at the wrong level.

**How to apply:**
- During email triage, classify recruiter mail that is (a) generic / (b) not explicitly consulting-level / (c) drive-by link spam as `noise` or `archive`, NOT `actionable:needs_reply`.
- Do NOT auto-draft replies to such outreach even if the user is in an active job-search context (career-search context alone is insufficient — source quality is the gate).
- Only draft responses when the outreach meets both criteria: consulting-level role + credible named source (specific company, personalized message, clear rate/scope signals).

**Discard path:** when a drafted reply is determined to be to generic/drive-by outreach after the fact, the user prefers to **discard the draft** rather than send a polite decline. Silence is fine.

**Signals of a drive-by outreach to watch for:**
- Just a single kloudhire / indeed / external-platform URL with no role detail
- "OPEN rate" or "multiple requirements" phrasing (= blast)
- No mention of specific company or client
- No scope / tech-stack specifics in the body
- Subject like "RE - AI Engineer" or generic role title
- Sender domain is a recruiter-aggregator (rephers.com, stepstoprogress.com, disys.com — also visible in routing config)

**Signals of a credible outreach to draft for:**
- Named hiring company or client
- Specific tech stack matching user's expertise (OrcaFlex/ANSYS/marine/subsea/LLM-agents)
- Scope and duration specified
- Rate band or salary clearly stated
- Evidence the recruiter researched the user's background (e.g., mentions specific past projects, publications, or open-source work)
