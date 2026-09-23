## Verdict

MAJOR

## Retrieval

- Read the draft plan.
- Cross-checked llm-wiki-acma #209 code-review rounds 1–4.
- Cross-checked the llm-wiki-acma #216 plan and its convention, TDD, workflow, and code-review artifacts.
- Inspected the #216 inventory, hashing, validation, Git verification, and candidate-install modules.

## Findings

1. “Approved private roots” lacked caller-independent destination discovery, private classification, ignored/untracked transient-root checks, reparse-ancestor rejection, and durable log/review/comment sanitization.
2. A read-only drive path did not prove stable source identity. The plan needed canonical root plus stable volume/device identity, three rechecks, and a fence against drive substitution or mid-scan mutation.
3. Private checkpoints and journals could still carry attacker-controlled mutation paths. Exact-key, path-free schemas, trusted-root reconstruction, journal hash binding, and coordinated-tamper tests were missing.
4. Windows destination safety omitted case-fold and Unicode collisions, reserved names, trailing dot/space, ADS colons, surrogate names, traversal, reparse/junctions, and UTF-16 path bounds over every write surface.
5. “Adaptive two-level” allowed the agent to define a convenient denominator. A versioned inclusion predicate, root/child denominators, and explicit representation states were required.
6. Git TOCTOU safety was reduced to keywords. The plan needed an index-authoritative manifest, existing-tree ownership, parent snapshots, detached candidate, candidate-blob scan, exclusive lock, post-lock rechecks, `update-ref` CAS/rollback, and final equality in order.
7. Broad legacy descriptions still overlapped at discovery time.
8. The plan did not run the no-absolute-path gate against its own forensic fixtures or verify staged privacy evidence.

## Blockers

- Bind private residency and stable source identity before any post-approval write.
- Make coverage deterministic and journals non-executable.
- Preserve Windows and ordered Git transaction safety as testable contracts.

## Disposition

Draft v2 incorporates all eight findings and the cleanup/reference-name minor findings. Fresh re-review remains required.
