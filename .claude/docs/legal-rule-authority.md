# Legal rule authority

Public tooling and metadata are separated from all private rule bytes, keys,
manifests, anchors, ledgers, mirrors, envelopes, and reports. The normative
contract is `docs/plans/evidence/2026-07-13-issue-3522-rule-authority-contract.md`.

## Phase A bootstrap

Phase A adds only synthetic public registry/policy data, deterministic public
validation, immutable reusable tooling, and an owner transaction preview. It
does not decode or scan a private authority envelope. The caller runs from the
trusted base through `pull_request_target`; it never checks out or executes PR
content. Same-repository requests invoke a reusable workflow pinned to a full
commit SHA. The reusable workflow owns the `legal-rule-authority` Environment.

## Fork boundary

Fork requests terminate in the trusted caller with the constant public result
`owner review required`. That happens before the protected Environment,
authority loading, or data scanning. A fork cannot satisfy the required check.
A maintainer may privately clean a candidate and create an independent
same-repository PR; the original fork remains nonmergeable.

## Owner transaction preview

The exact proposed owner, CODEOWNERS paths, Environment policy, GitHub Actions
integration ID, target ref, ruleset, and required check are frozen in
`docs/plans/evidence/2026-07-14-issue-3522-phase-a-owner-preview.json`.
Readback tooling accepts captured JSON fixtures only; it makes no provider call.
The owner must separately approve and perform every live configuration change,
then compare normalized API readback with the preview before Phase B.

## Dual-slot cutover and rollback

CURRENT remains active for ordinary requests. PENDING is selected only when its
anchor binds the exact candidate head OID. Promotion is a separately approved
compare-and-swap over unchanged CURRENT, expected merge tree, and PENDING
identity. Rollback is allowed only if the promoted identity still matches the
preview, and restores the exact prior CURRENT. Phase A performs neither action.

## Explicitly not performed

No environment, CODEOWNERS, ruleset, or secret was mutated. No envelope was
created, provisioned, or read. No provider request, private scan, Phase B
migration, legacy deletion, history rewrite, force-push, ref deletion, CAS,
promotion, or rollback was performed. Existing legal enforcement remains live.
