Latest Codex re-review update:

- Verdict: MAJOR
- Ready for user approval: No

Current remaining blockers:
1. Rollback scope is still not fully reconciled against the issue's original required deliverable.
2. The rollback child is still a placeholder (`#NNNN`) rather than a real dependency.
3. Direct-push / PR / CI / dashboard responsibilities are clearer now, but some blocking-vs-advisory distinctions still need tightening.
4. Provider bootstrap validation still needs to move further from text-presence checks toward behavior-level enforcement proof.

Immediate next fix direction:
- replace `#NNNN` with a real child issue
- explicitly reconcile #2018 scope vs rollback requirement in issue/plan language
- tighten acceptance criteria to distinguish blocking controls, advisory/reporting controls, and deferred child work
- strengthen provider bootstrap validation beyond grep-style checks
