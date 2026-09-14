# Digitalmodel 716 — plan review disposition

Scope: bounded offline validator repair. Main disposition: no unresolved material plan finding after revision 3; user approval remains required. No implementation or native qualification occurred.

- [Claude r1](../../../docs/reports/2026-09-11-digitalmodel-716-claude-review.md): actual MINOR against revision 1.
- [Codex r1](../../../docs/reports/2026-09-11-digitalmodel-716-codex-review.md): actual REQUEST_CHANGES, one MAJOR against revision 1.
- [Codex r2](../../../docs/reports/2026-09-11-digitalmodel-716-codex-r2.md): advisory APPROVE against revision 2.
- [Final plan](../../../docs/plans/2026-09-11-digitalmodel-716-validator.html): revision 3 adds main inline audit/test clarifications. No unanimous final-revision provider approval is claimed.

## Findings resolved or rejected

1. Codex C1 accepted: only preceding effective setters can establish state at a maximum assignment. Later setters cannot prove invalidity. Revision 2 treats an unresolved include, repeated General/relevant keys or ambiguous aliases as uncertain before dictionary collapse; cyclic aliases must terminate with a diagnostic. Tests cover maximum-before-enable/disable/incompatible-method, include boundaries and duplicate mappings. Codex r2 verified closure.
2. Claude test-rewrite clarification accepted: revision 3 explicitly replaces both flat/nested nonexistent-property assertions with conditional fixtures, while retaining unrelated invalid-property rejection. The original fixture has null/no active mode, so it does not become a valid active-mode fixture merely by changing the rule.
3. Claude reversed-order/absent-mode ERROR prescription rejected. It contradicts inherited context and Codex's verified counterexample. A known incompatible preceding state errors; unknown inherited state warns. Generator canonical ordering remains preserved, without claiming every alternate overlay ordering invalid.
4. Claude audit reproducibility concern accepted. Revision 3 specifies identical frozen inputs/environment, fresh baseline/candidate directories, complete generated file manifests including parameters, and per-file SHA-256/relative-path equality with no missing/extra cases/files. Every remaining error/warning remains visible.
5. Claude invented CI check and warnings-do-not-block-merge claim rejected. No evidence established that proposed check exists. Existing repository test workflows will run the relevant tests; the full corpus audit is explicitly a local PR evidence gate. No warning waiver or model-qualification claim follows.

## Verified evidence and scope

Main reran the generator variable-step class and invalid-property class: six existing tests pass while asserting contradictory contracts. The six case maxima preserve enabled values/order; the 19 unknown-name warnings concern six features supported by the linked Orcina documentation and existing schema/builder mappings. These findings justify a bounded static grammar repair; native value/readback and nested feature semantics remain unverified.

Remote main advanced to 90bcff859220cc473c790831a2ed9f81a603cc80. Main fetched it in the isolated digitalmodel worktree and checked the affected validator/generator/test paths against a7fe3775: no diff. Live worktrees remained preserved.

The three mooring representatives require separate native preparation: restart-script null spelling, turret drawing dependency, an arbitrary-model bounded one-thread harness, and reference results. The readiness report treats the spelling as a reproduced defect class/risk, not a fresh native failure for these models. Mooring topology's July patch exists; pretension mechanics remain unqualified.

Generalizable defect class for future validators: a final parsed dictionary is not the state at a sequential setter. Collapsed duplicates, aliases and unresolved includes must not authorize a definite-load-failure claim. This will be posted to the existing corpus/validation owners for reuse.
