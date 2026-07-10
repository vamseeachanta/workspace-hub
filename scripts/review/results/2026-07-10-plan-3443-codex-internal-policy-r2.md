# Adversarial plan re-review — #3443 policy/security

> Reviewer: Codex internal parallel reviewer (Arendt)
> Stage: plan, revision 2
> Verdict: MAJOR
> Provider-diverse gate credit: none; same-provider review only

## Defects found

1. Signed posture/review authority lacked trust roots, signer roles, canonical bytes, key custody, rotation, revocation, and clock policy.
2. Activation was circular or replayable because the attestation carrier and final candidate/control binding were undefined.
3. A readable check did not prove active, correctly scoped, bypass-free enforcement.
4. Producer-supplied public-egress manifests could omit or mutate transferred files; mutable PR/issue metadata could outlive its check.
5. A stdlib-only zipapp could not parse YAML or verify Ed25519 without a dependency contract.
6. The private authority path had no containment, visibility, ACL, symlink, atomic-write, or leak controls.
7. A literal-string bypass checker would block its own plan/tests and safe historical guidance.

## Required disposition

Revision 3 will specify canonical JSON and role-separated Ed25519 trust roots, use a live external control-digest attestation, verify exact ruleset semantics, make the gate enumerate and transport the scanned artifact, invalidate mutable metadata evidence, vendor/hash dependencies with an SBOM, enforce a verified private journal root, and make bypass detection semantic with exact signed fixture allowances.
