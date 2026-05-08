# Retroactive Adversarial Review — Provider Session Learning Transfer

Scope:
- Commit `916743102 docs(provider): transfer session learning audit`
- Follow-up skill patch `513378ecb docs: clarify adversarial review requirements for skill transfers`
- User correction: meaningful harness, file-structure, test-suite, docs/report, skill-transfer, governance, and workflow work must not skip workflow gates; prompt depth may scale from sanity-check to thorough review.

Prompt artifact: `.planning/quick/review-916743102-provider-transfer-retro.md`

## Verdicts

| Reviewer | Verdict | Notes |
| --- | --- | --- |
| Codex | MINOR | No blocker if review evidence is recorded durably; requested exact provenance handles, review artifact paths, clerical-change carve-outs, and `python3` hygiene cleanup. Codex could not inspect files directly because its shell sandbox failed with `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`, so it reviewed from supplied prompt evidence. |
| Claude | MAJOR | Found blocking policy/skill mismatch and weak enforcement placement; also flagged duplicate-issue ambiguity (#2657 vs #2650), weak evidence wording, undefined meaningful threshold, and Hermes-vs-Claude memory-parity wording. |

Overall result: **MAJOR until remediation applied**. This artifact records the review that was missing from the original transfer and drives the remediation patch.

## Blocking findings and remediation status

| ID | Finding | Remediation status |
| --- | --- | --- |
| C1 | `multi-provider-adversarial-review` said two-provider default while `docs/standards/AI_REVIEW_ROUTING_POLICY.md` says three-agent default. | Remediated by aligning the skill with the policy: three-agent default; reductions only under policy reduction rules. |
| C2 | Review rule lived only as a late verification bullet and would not block the pre-commit/pre-push failure mode. | Remediated in `provider-session-learning-transfer` by adding a pre-close adversarial review gate before commit/push/final closeout. Hook-level promotion remains a possible future hardening path. |
| H1 | "Review evidence exists" could be satisfied by self-attestation and did not require verdicts/artifact paths. | Remediated by requiring reviewer verdicts and durable artifact paths or issue/PR comment URLs; authoring provider does not count as an independent reviewer. |
| H2 | "Meaningful work" was subjective and could waste spend or reopen rationalization gaps. | Remediated by splitting thorough-review vs scaled-sanity-check vs clerical-waiver categories. |
| H3 | Possible duplicate issue #2657 vs broad llm-wiki spinout cleanup #2650. | Remediated by recording #2657 as a narrower provider-session audit-rule drift issue and linking #2650 as the checked broad tracker. |
| M1 | Transfer report implied Hermes memory bridge parity verified Claude memory parity. | Remediated by rewording the report: Hermes bridge parity was verified; Claude-memory parity was not separately verified in this pass. |
| M2 | Two-provider wording did not exclude the authoring provider. | Remediated: authoring provider does not count as independent reviewer. |
| M3 | Verification/provenance lacked exact issue/comment links. | Remediated by adding #2310/#2312/#2655 comment URLs and #2657 issue URL to the transfer report. |

## Follow-up observations

- Hook-level enforcement for direct-to-main commits touching skills/hooks/standards/reports was recommended by Claude as stronger future hardening. The current remediation improves the canonical workflow and skills; hook promotion should be handled as a planned enforcement-hardening issue if needed.
- The `multi-provider-adversarial-review` skill still contains historical examples using `python3`; this was pre-existing and not required to close the immediate workflow-skip correction, but should be cleaned up in a separate command-hygiene pass.
- This review artifact intentionally records provider verdicts and remediation status so the retroactive gate is durable in-repo rather than only in chat.
