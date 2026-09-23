# Adversarial plan review: issue #3544 — FD broker transaction R16

- Date: 2026-07-15
- Reviewed commit: `46fe41621bd2c36c0b1173b2384090fb89efe108`
- Verdict: **MAJOR**

## Finding

The outer bootstrap consumed the independently approved decoded-source digest
instead of carrying it across the launcher boundary. Later stages could only
compare approval `outer_bootstrap.sha256` with the same parsed approval field,
not with an independent value representing the executed command root.

The correction must preserve that identity across outer bootstrap, launcher,
broker, verifier, and authority through an internal argument or retained sealed
identity FD and compare it before approval consumption.

No files or external state were changed by the reviewer.
