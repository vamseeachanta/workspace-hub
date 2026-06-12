### Verdict: MAJOR

### Summary
A mature, well-iterated T3 governance/validator plan (post-r4) that composes existing schema/routing/citation contracts rather than forking them, with strong fail-closed design and explicit MVP/follow-up boundaries. However, several genuine spec gaps remain: the contract's substance rests on un-attested cross-repo decision-content summaries, the publication-state pseudocode is internally inconsistent, a key staleness threshold is undefined, and the "MVP" is large enough that the residual validator-complexity risk flagged in r4 is not captured in the Risks section. Default to non-APPROVE until these are tightened.

### Issues Found
- [P2] Contract substance is derived from worldenergydata#450-#453 'tightened decisions' (lines 74-77), but the captured gh transcript (lines 140-145) verifies only issue NUMBER/STATE/TITLE — not the decision-body content the standard's enums and staged-publishing order are built on. The most load-bearing inputs to the contract are therefore unattested. (No Attested Evidence block was supplied to this review, so this cannot be discharged by construction.)
- [P2] classify_publication_state pseudocode is internally inconsistent: the signature is classify_publication_state(sources, output_residency, review_state, config) but the body branches on approved_with_notes_gate_status, which is never passed in and lives in a different file (insight_bundle_metadata.yml flywheel_wrapper). The data-flow for that gate field into the classifier is unspecified.
- [P2] 'MVP' is not minimal: 36 non-cuttable blocking tests plus a validator that simultaneously composes two JSON schemas, parses a fenced enum block from a Markdown standard, performs SHA-256 attestation with a timestamp window, enforces an allowlist-only projection, and does duplicate-run/ledger semantics — all in one PR. r4 explicitly flagged 'validator complexity,' yet validator over-scope/maintainability is absent from the Risks section.
- [P2] AC/MVP-boundary vs blocking-test mismatch persists: the MVP Boundary table puts 'Scheduler readiness | Validate two-clean-run records in fixtures' in #2975 scope, but test_two_clean_manual_runs_required_before_scheduling and test_clean_run_requires_reviewed_generated_diff are NOT in the blocking floor and are labeled 'may be promoted to follow-up.' Whether two-clean-run validation ships in #2975 is ambiguous.
- [P3] Staleness threshold is undefined: test_stale_pointer_existing_target_fails references an 'expired last_checked_at,' but no TTL/window governing when last_checked_at is considered stale is specified anywhere in the plan, so the check is not yet deterministic.
- [P3] test_forged_or_stale_legal_scan_evidence_fails requires the validator to re-read and re-hash the actual fixture artifacts and compare against the recorded hash to detect a 'mutated artifact after claimed scan pass.' The plan states the hash algorithm (sha256 raw bytes) but never states that the validator re-hashes on-disk files vs. trusting recorded hashes — the anti-forgery property depends on this being explicit.
- [P3] 'No duplicate ledger event identity' is enforced (test_duplicate_ledger_event_identity_fails) but 'identity' is not defined — event_id alone, or a composite of event_id/run_id/event_type? Undefined identity makes the duplicate check non-deterministic.
- [P3] Dual enum source of truth (config/ecosystem-wiki-flywheel/source-classification.yaml AND the standard's fenced machine-readable block, reconciled by test_standard_enum_table_matches_config) creates a maintenance/drift surface; acceptable but worth calling out the single-writer discipline so the two never diverge silently between edits.

### Suggestions
- Attest the decision-body content of worldenergydata#450-#453 (quote the exact tightened-decision text with a body hash or excerpt), not just titles, so the enum set and staged-publishing order are traceable to verified source. Alternatively, file the cross-repo-attestation follow-up (already listed) and explicitly mark lines 74-77 as 'paraphrase, not attested.'
- Fix the classify_publication_state signature to accept the wrapper/gate context explicitly (e.g., pass insight_bundle_metadata or approved_with_notes_gate_status), and state how validation order step 4 threads the wrapper field into the classifier.
- Add an explicit Risk entry for validator over-complexity/maintainability and state the mitigation concretely (helper-module split + per-surface test isolation + a hard line that no live-scan/hook/network logic enters this PR).
- Reconcile the MVP Boundary table with the blocking floor: either move test_two_clean_manual_runs_required_before_scheduling into the blocking subset or change the MVP table cell to 'follow-up' so scope is unambiguous.
- Specify the last_checked_at staleness window (or make it a config field) and assert it in the stale-pointer fixtures so the check is deterministic.
- State explicitly that the validator re-hashes on-disk fixture artifacts and compares to recorded hashes for the legal-scan attestation, and define ledger-event identity (the exact key tuple) used for duplicate detection.

### Questions for Author
- Were the tightened-decision BODIES of worldenergydata#450-#453 read and verified, or only the titles? The contract's enums and staged order depend on the body content.
- How does approved_with_notes_gate_status reach classify_publication_state given it lives in insight_bundle_metadata.yml and is absent from the function signature?
- Is two-clean-run fixture validation (and reviewed-generated-diff) actually shipping in #2975, or deferred? The MVP table and the blocking-test list disagree.
- What is the concrete staleness window for last_checked_at, and where is it configured?
- What key tuple constitutes a unique 'ledger event identity' for duplicate detection?
- Does the validator re-hash the actual artifact bytes on disk to catch post-scan mutation, or does it trust the hashes recorded in the manifest?
