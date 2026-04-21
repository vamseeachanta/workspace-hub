### Verdict: MAJOR

### Summary
The plan is close, but two material integrity gaps remain: the evidence/bookkeeping around review waves is internally inconsistent with the attested evidence, and the AGENTS immutability check is tied to an un-attested hardcoded blob that is likely brittle in implementation. The overall scope and validator strategy are otherwise strong and well-bounded.

### Issues Found
- [P1] Critical: The review-artifact bookkeeping conflicts with the attested evidence. The attestation verifies five timestamped review waves (`141459`, `142328`, `143224`, `154852`, `160111`), but the plan text claims waves 1–6 remain recorded and also summarizes a wave 7 review cycle without corresponding attested artifact paths. That makes the acceptance criteria and readiness narrative internally inconsistent.
- [P1] Critical: `test_agents_file_unchanged` depends on a hardcoded blob SHA (`b4a14216f383b98ebcd70c9bf98ffed26c3eb1bf`) that is not attested in the evidence block. Because the plan intends future implementation after approval, pinning the test to an external blob literal is brittle and may fail for reasons unrelated to this packet's actual requirement (`AGENTS.md` unchanged in this work`).
- [P2] Important: The plan mixes two different evidence models for AGENTS invariance: attested line-count evidence and a non-attested exact blob baseline. The former supports 'do not edit in this packet'; the latter adds a stronger claim without verified provenance. That weakens feasibility of the validator/test contract.
- [P2] Important: Acceptance criteria still say 'The contract explicitly names `workspace-hub` as the control plane,' which is imprecise relative to the stricter canonical terminology contract requiring `workspace-hub is the ecosystem control plane` and forbidding collapse with `GSD is the control plane`. That wording invites future drift back into the ambiguity this plan is trying to eliminate.
- [P3] Minor: The deliverable and file-touch list are clear, but the plan does not explicitly state whether the validator itself will be runnable standalone from CI beyond pytest coverage (for example a direct `uv run` invocation or exit-code contract). That is not blocking, but it would improve operational clarity for the follow-up CI issue.

### Suggestions
- Normalize the review-wave accounting to exactly what is attested now. Either reduce all references to the five verified waves, or add fresh attestation for the additional wave(s) before keeping waves 6/7 in metadata, acceptance criteria, and summary.
- Replace the hardcoded AGENTS blob assertion with a packet-local invariance check, such as comparing `AGENTS.md` against the pre-change branch state for this implementation or asserting no diff for that file in the worktree. If the exact blob must stay, add it to the attested evidence block first.
- Tighten all prose to the canonical phrase `workspace-hub is the ecosystem control plane` wherever acceptance criteria or summary language currently shortens it to `control plane`.
- Add one explicit operational contract for the validator script itself: command, expected exit behavior, and whether pytest shells out to it or imports it as a module.

### Questions for Author
- Should the canonical source of truth for review-wave completeness be the attested artifact list, or do you intend to regenerate attestation to cover the claimed wave-6/wave-7 artifacts?
- Do you want `test_agents_file_unchanged` to enforce 'unchanged during this packet' or 'matches one historic blob exactly'? Those are different guarantees and should be encoded differently.
