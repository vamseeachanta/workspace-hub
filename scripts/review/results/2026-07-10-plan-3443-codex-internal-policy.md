# Adversarial plan review — #3443 policy/security

> Reviewer: Codex internal parallel reviewer (Arendt)
> Stage: plan, revision 1
> Verdict: MAJOR
> Provider-diverse gate credit: none; same-provider review only

## Defects found

1. A private/internal early return could skip mandatory privacy, IP, provenance, and raw-residency controls.
2. Caller-supplied surface selection could launder public-egress as internal.
3. The skip could activate without a staged and CI secret gate operating on the same evidence.
4. Visibility alone could authorize posture; identity and policy changes were not independently authorized.
5. A public registry/report could expose private repository topology and PR URLs.
6. The downstream engine had no pinned distribution contract, the legacy deny-list migration was missing from the artifact map, generated runtimes were omitted, and activation could precede replacement gates.

## Required disposition

Revision 2 will use a composite same-manifest verdict; protected action floors; signed immutable repository/policy/engine attestations; trusted entrypoint-derived operations; private detailed governance storage; deterministic local and SHA-pinned CI distribution; one-to-one legacy-rule migration; generated runtime verification; and strict-install-before-skip activation.
