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
3. **Verify the destination and rights.** Repository identifier gates are retired under [issue 3936](https://github.com/vamseeachanta/workspace-hub/issues/3936). Identifiers may flow through authorized repository work. Do not infer disclosure rights from a name alone or assume every wiki is public; verify actual repository visibility and source-specific publication authority.
   O13 recorded by the PM establishes a narrow warn-only public-repo PR check for probable client identifiers; the check posts masked reviewer guidance and does not restore a blocking identifier gate under issue 3936.
4. **Client-wiki posture is the authority for the identifier classes.** Client legal name and project IDs are REDACT-class; personal names, coordinates and vessel names are FLAG-FOR-REVIEW — see the client wiki's `REDACTION-POSTURE.md`. Report residency must mirror source-data residency (its `DATA-CYCLE.md`); **no agent self-approves a promotion** across a residency boundary.
5. **Never write "validated" without a named referent.** Where no experiment or benchmark exists for the specific artefact, the honest claim is a *verified prediction with a stated numerical-uncertainty band, plus an explicit statement that modelling error is not inside that band*. Verdict vocabulary is `implausible` / `not_implausible` — never "passed" or "validated". A plausibility band cannot confirm; it can only fail to contradict. Rationale and worked precedent: [`report-claim-discipline`](../skills/development/report-claim-discipline/SKILL.md).

6. **Leak remediation covers every layer the identifier reached, not only the file.** When a client identifier or a host name is found on a public or hosted surface, fixing the tree closes one layer. The same string usually also sits in **commit messages, PR titles and bodies, issue titles and bodies, and their comments** (and sometimes the branch name), and those outlive the file fix. Before reporting the leak closed:
   - **Enumerate each layer.** Search the tree, `git log --all --grep`, and PR / issue / comment text (`gh search prs`, `gh search issues`) for the identifier and its obvious variants.
   - **Scrub what is editable.** Edit PR and issue titles, bodies and comments in place to the codename or role-slug. GitHub keeps the earlier text in the edit history, so delete the old revisions there as well. Reword commit messages on a branch that is not yet merged, or squash-merge with a clean message.
   - **Do not rewrite merged public history on your own authority.** A leaked commit message already on a public default branch is an owner decision. Record it as a residual and escalate.
   - **Report per layer.** State tree / commit messages / PR text / issue text as `clean`, `scrubbed` or `residual`, in the same way a failure is reported by layer (`feedback_classify_failure_layer_before_reporting`). "Leak fixed" with only the tree checked is the defect this item exists to stop.
   - **Write the remediation itself clean.** The fix commit, PR body and issue text must not quote the leaked string; name it by class ("a client vessel name", "a Windows host name").

**Do NOT apply when:** the artifact is an internal scratch note, a test fixture, or a log — the internal row already permits everything. This rule constrains what *leaves*; it does not add ceremony to work that stays put.

**Final verification:** Follow [FINAL_REPORT_VERIFICATION.md](../../docs/standards/FINAL_REPORT_VERIFICATION.md) before issuing the actual report and its attachments/embedded data. Record audience, artifact revision/digests, identifier decisions, source rights, independent secret-check evidence, reviewer/date and unresolved findings. This is manual review, not a replacement automatic identifier gate. `legal-sanity-scan` and identifier-only repository gates are retired; do not require or recreate them. Keep independent secret/access controls and technical claim checks.

**Related:** [`report-claim-discipline`](../skills/development/report-claim-discipline/SKILL.md) (what a report may claim, and how to say it), [`calc-citation-contract.md`](calc-citation-contract.md) (standards-derived constants), [`wiki-sibling-routing.md`](wiki-sibling-routing.md) (client-slug routing), [`svg-pdf-portability.md`](svg-pdf-portability.md) (PDF-bound SVG), [`patterns.md`](patterns.md).
