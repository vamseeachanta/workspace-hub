# Evidence-gate reruns and remote verification

Use this pattern when a plan-review loop keeps returning MAJOR findings about evidence strength, validator overclaiming, or missing durable review artifacts.

## Pattern
1. Treat each MAJOR review finding as a fresh requirement against the exact plan revision reviewed. Patch the plan and related artifacts, then rerun validation before another provider wave.
2. If a validator checks structural properties only (counts, required fields, deny/contact regexes, URL shape), say so in the plan. Do not claim it semantically proves official-domain correctness, privacy safety, or legal sufficiency unless it actually encodes those checks.
3. When an issue requires evidence URLs for every contractor/fleet/content claim, acceptance criteria must preserve that requirement. Do not weaken it into corporate-root-only evidence unless the plan explicitly marks the claim as bounded/no-public-proof and reviewers accept that boundary.
4. Add any new validation script or generated artifact to the plan's Files to Change / Artifact Map before asking reviewers to rely on it.
5. Promotion requires durable artifacts, not just `/tmp` fanout outputs. Copy final provider reviews and synthesis to the repo (for example `scripts/review/results/...`) and commit them before moving an issue to `status:plan-review` or claiming the gate cleared.
6. If a push or pre-push hook times out after partial output, do not assume the commit reached `origin/main`. Start the next turn by comparing local `HEAD` and `origin/main`, then push/retry before rerunning reviews.
7. Provider `UNAVAILABLE` is not a clean review. Either wait/retry, use a documented approved substitute, or keep the issue blocked with the unavailability artifact preserved.

## Concrete example
A GTM contractor-matrix plan had validator PASS (`live_countable=20 high=12 deny_hits=0 contact_hits=0 errors=0`) but Codex still returned MAJOR because the plan overclaimed official-domain validation and had not archived r2 artifacts on `main`. The fix was to tighten evidence acceptance criteria, add the validator to the artifact map, make manual semantic review explicit, commit/push, verify remote SHA, and only then rerun the fanout review.
