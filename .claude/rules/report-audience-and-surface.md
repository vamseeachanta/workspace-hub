# Report audience and surface — agent rule

**When to apply:** authoring, editing, exporting or publishing any engineering report, status page, brief or calc deliverable — HTML, PDF, Markdown or Artifact. Fires before the first line of content, not at export time.

**Why:** an internal status page and a client deliverable are **different documents, not one document at two levels of polish**. Internal pages legitimately carry cost models, host and machine names, per-run rates, and a candid record of defects found in our own tooling. None of that belongs in a client document: to an audience that needs only the method, it reads as commercial disclosure and self-criticism. The failure mode is not malice — it is polishing an internal page and calling it a deliverable.

**The inversion that catches people:** the same fact is redacted on one surface and *required* on another. **The discriminator is the surface, not the sensitivity of the fact.**

| Surface | Client identifiers (legal name, project/job ID, vessel, drawing refs) | Cost models, host names, per-run rates | Candid defects in our own tooling |
|---|---|---|---|
| **Internal** — repo-local, not published, not issued | allowed | allowed | allowed, and usually the point |
| **Client deliverable** — issued to the client who owns the data | **REQUIRED** — they know who they are; a deliverable stripped of their own project ID is unreviewable | **never** | **never** |
| **Hosted** — published to a URL (Artifact, static host, share link), even private-by-default | **REDACT** | **never** | **never** |

**How to apply:**

1. **Name the surface before writing.** If you cannot say which of the three rows the document is, you are not ready to write it.
2. **Hosted is stricter than private-on-disk.** Publishing is effectively irreversible: content can be cached, crawled or indexed and outlive deletion of the page. "Private by default" is a default, not a guarantee. Never treat a share link as a private channel.
3. **workspace-hub is a PUBLIC repo.** Nothing written into it names a client. Use "a client hull", "a client deliverable". Same for any file that will land in public `llm-wiki`.
4. **Client-wiki posture is the authority for the identifier classes.** Client legal name and project IDs are REDACT-class; personal names, coordinates and vessel names are FLAG-FOR-REVIEW — see the client wiki's `REDACTION-POSTURE.md`. Report residency must mirror source-data residency (its `DATA-CYCLE.md`); **no agent self-approves a promotion** across a residency boundary.
5. **Never write "validated" without a named referent.** Where no experiment or benchmark exists for the specific artefact, the honest claim is a *verified prediction with a stated numerical-uncertainty band, plus an explicit statement that modelling error is not inside that band*. Verdict vocabulary is `implausible` / `not_implausible` — never "passed" or "validated". A plausibility band cannot confirm; it can only fail to contradict. Rationale and worked precedent: [`report-claim-discipline`](../skills/development/report-claim-discipline/SKILL.md).

**Do NOT apply when:** the artifact is an internal scratch note, a test fixture, or a log — the internal row already permits everything. This rule constrains what *leaves*; it does not add ceremony to work that stays put.

**Enforcement gradient** (per [`patterns.md`](patterns.md)): Level 0 prose now. Level 2 already exists for one column — `scripts/legal/legal-sanity-scan.sh` against `.legal-deny-list.yaml` catches client identifiers in committed code. Target a `scripts/enforcement/check-report-surface.sh` that (a) runs the deny-list over any file under a hosted-artifact output path, and (b) greps report sources for `validated`/`passed` in a verdict position with no referent field set. Both are exit 0/1 checks.

**Related:** [`report-claim-discipline`](../skills/development/report-claim-discipline/SKILL.md) (what a report may claim, and how to say it), [`calc-citation-contract.md`](calc-citation-contract.md) (standards-derived constants), [`wiki-sibling-routing.md`](wiki-sibling-routing.md) (client-slug routing), [`svg-pdf-portability.md`](svg-pdf-portability.md) (PDF-bound SVG), [`patterns.md`](patterns.md).
