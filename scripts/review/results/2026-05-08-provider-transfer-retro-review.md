# Retroactive Adversarial Review — Provider Session Learning Transfer

Scope:
- Commit `916743102 docs(provider): transfer session learning audit`
- Follow-up skill patch `513378ecb docs: clarify adversarial review requirements for skill transfers`
- User correction: meaningful harness, file-structure, test-suite, docs/report, skill-transfer, governance, and workflow work must not skip workflow gates; prompt depth may scale from sanity-check to thorough review.

Prompt artifact: `scripts/review/results/2026-05-08-provider-transfer-retro-review-prompt.md`

## Verdicts

| Reviewer | Verdict | Notes |
| --- | --- | --- |
| Codex | MINOR | No blocker if review evidence is recorded durably; requested exact provenance handles, review artifact paths, clerical-change carve-outs, and `python3` hygiene cleanup. Codex could not inspect files directly because its shell sandbox failed with `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`, so it reviewed from supplied prompt evidence. |
| Claude | MAJOR | Found blocking policy/skill mismatch and weak enforcement placement; also flagged duplicate-issue ambiguity (#2657 vs #2650), weak evidence wording, undefined meaningful threshold, and Hermes-vs-Claude memory-parity wording. |

Overall result: **MAJOR until remediation applied**. This artifact records the review that was missing from the original transfer and drives the remediation patch.

## Blocking findings and remediation status

| ID | Finding | Remediation status |
| --- | --- | --- |
| C1 | `multi-provider-adversarial-review` said two-provider default while `docs/standards/AI_REVIEW_ROUTING_POLICY.md` says three-provider/three-agent default. | Remediated by aligning the skill with the policy: three-provider default; reductions only under policy reduction rules. |
| C2 | Review rule lived only as a late verification bullet and would not block the pre-commit/pre-push failure mode. | Remediated in `provider-session-learning-transfer` by adding a pre-close adversarial review gate before commit/push/final closeout. Hook-level promotion remains a possible future hardening path. |
| H1 | "Review evidence exists" could be satisfied by self-attestation and did not require verdicts/artifacts/URLs/SHA binding. | Remediated by requiring reviewer verdicts, durable review artifact paths under `scripts/review/results/`, issue/PR comment URLs when they exist, evaluated commit SHA or exact revision identifier, and omission explanations; authoring provider does not count as an independent reviewer. |
| H2 | "Meaningful work" was subjective and could waste spend or reopen rationalization gaps. | Remediated by splitting thorough-review vs scaled-sanity-check vs clerical-waiver categories. |
| H3 | Possible duplicate issue #2657 vs broad llm-wiki spinout cleanup #2650. | Remediated by recording #2657 as a narrower provider-session audit-rule drift issue and linking #2650 as the checked broad tracker. |
| M1 | Transfer report implied Hermes memory bridge parity verified Claude memory parity. | Remediated by rewording the report: Hermes bridge parity was verified; Claude-memory parity was not separately verified in this pass. |
| M2 | Two-provider wording did not exclude the authoring provider. | Remediated: authoring provider does not count as independent reviewer. |
| M3 | Verification/provenance lacked exact issue/comment links. | Remediated by adding #2310/#2312/#2655 comment URLs and #2657 issue URL to the transfer report. |

## Follow-up remediation review

After the remediation patch, Codex and Claude re-reviewed the scoped changes.

| Reviewer | Verdict | Notes |
| --- | --- | --- |
| Codex | MINOR | No blockers. Requested durable prompt path and clearer single-sanity-check wording. |
| Claude | MINOR | No blockers. Requested terminology alignment (`three-provider`), SHA-bound evidence requirements, tracked review-prompt artifact, and sustained-MAJOR cycle-break note. |
| Gemini | Unavailable | Gemini CLI failed before producing a verdict because repository Gemini agent definitions contained unsupported `permissionMode` keys; this unavailability is recorded as reviewer evidence rather than silently treated as approval. |

Applied follow-up remediation:
- moved the retro prompt into `scripts/review/results/2026-05-08-provider-transfer-retro-review-prompt.md`
- changed the review skill to `three-provider` terminology
- changed evidence requirements to include committed artifact path, issue/PR URL when present, evaluated SHA/revision, and omission explanations
- replaced ambiguous "single sanity-check review" wording with reduction in reviewer count or prompt depth under policy rules
- added the sustained single-provider `MAJOR` cycle-break note
- updated the provider-transfer verification bullet to check Step 8 evidence rather than restating a weaker duplicate rule

## Follow-up observations

- Hook-level enforcement for direct-to-main commits touching skills/hooks/standards/reports was recommended by Claude as stronger future hardening. The current remediation improves the canonical workflow and skills; hook promotion should be handled as a planned enforcement-hardening issue if needed.
- The `multi-provider-adversarial-review` skill had historical examples using `python3`; the remediation patch migrated those command examples to `uv run python` in the same change. Keep the commit message explicit so workflow-gate and command-hygiene changes are discoverable.
- This review artifact intentionally records provider verdicts and remediation status so the retroactive gate is durable in-repo rather than only in chat.
