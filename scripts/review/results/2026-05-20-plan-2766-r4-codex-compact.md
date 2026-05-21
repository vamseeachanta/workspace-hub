## Verdict
MAJOR

## Retrieval adequacy
adequate

## Findings
- MAJOR `Proposed Registry Semantics`: `telegram_hermes.data_access_profile.repos` “may include explicitly classified current non-tier-1 repos used by dispatch,” but the plan never names the exact allowed runtime non-tier-1 set. That leaves implementation free to include or omit any current non-tier-1 repo, creating ambiguous dispatch/runtime access behavior.

- MAJOR `Pseudocode` / `Acceptance Criteria`: warning-only readiness behavior is not decided. The plan says “if the existing readiness code blocks dispatch on any warning, keep that behavior explicit; otherwise do not newly block dispatch,” and AC says it is “pinned by tests against existing readiness policy.” This is not implementation-ready from the provided text because expected `status`, `dispatchable`, and `overall_status` for warning-only repo placement remain unspecified.

- MAJOR `Proposed Registry Semantics` / `Acceptance Criteria`: historical provenance is required, but the proposed YAML only stores `historically_moved_not_currently_present` as a flat name list. The plan requires “source-comment provenance” and “source issue/comment references,” but defines no registry/report/checker schema for comment URLs, comment IDs, timestamps, or claimed prior state. This makes the provenance acceptance criterion unfalsifiable or likely to be bolted on inconsistently.

- MAJOR `Pseudocode`: historical entries are internally inconsistent. It says “historical absence => severity from historical_absence_policy plus source-provenance warning,” while the TDD list says `test_historical_repos_are_not_expected_as_current_checkouts` verifies they “do not trigger missing-current warnings.” The plan needs a distinct `historical_state_changed_since_prior_comment` warning, not a generic absence warning that contradicts the test intent.

- MINOR `Artifact Map`: “R3 review evidence | to be generated after this revision” is stale for an R4 review, and the acceptance criteria later mention “R3/R4 adversarial review artifacts.” This creates avoidable gate confusion around which review artifacts must exist before `status:plan-review`.

- MINOR `Resource Intelligence Summary`: “This R3 plan does not retroactively authorize those moves” is stale wording in an R4 plan. It is not a blocker by itself, but it weakens traceability in a gate artifact.

## Blockers
1. Define the exact `telegram_hermes.data_access_profile.repos` target list or an unambiguous inclusion rule with required evidence.
2. Choose and state the expected readiness behavior for warning-only repo placement.
3. Add a concrete provenance schema for historical/anomaly entries.
4. Resolve the historical “absence warning” vs “not expected as current checkout” contradiction.
5. Fix stale R3/R4 artifact references before label transition.
