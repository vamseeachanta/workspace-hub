---
name: feedback-tests-that-pin-a-name-not-a-property
description: "A test asserting a literal identity (host name, rule, function string) protects the defect instead of the invariant — if it would still pass with the behaviour removed, it tests the text"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a873f663-bb0d-4ae1-9209-add92b7b1a13
  modified: 2026-07-31T14:11:46.883Z
---

**Assert the PROPERTY, never the identity. If a test would still pass with the behaviour deleted, it is testing text.**

**Why:** four instances in one day (2026-07-31), all written in good faith to protect something real:

| test | pinned | consequence |
|---|---|---|
| `test_route_glob.py` | literal `"licensed-win-1"` | **protected** the deckhand#579 defect — the host provably could not obtain a licence, suite stayed green |
| `test_cross_review_rule_wins_over_lane` | a live routing rule | would have blocked a *correct* fix; its real intent (#3029 "rule beats lane") survived as a synthetic-rule test |
| axis-cardinality wiring test | scanned `propose()` source for `"single_axes"` | **survived the mutation** — the identifier still appeared elsewhere |
| `test_route_capacity` predecessor | licence attestation only | passed a fix that was wrong on capacity |

**The tell:** the assertion still holds when the behaviour is removed. A name is a spelling; an invariant is a fact.

**How to apply:**

1. Ask "what must be TRUE?" not "what does it say today?" — *routes to a host with a dated licence attestation and heavy capacity*, not *routes to `licensed-win-1`*.
2. Prefer behavioural tests (monkeypatch, call the real entry point, assert the outcome) over `inspect.getsource` scans. Source scans are belt-and-braces behind a behavioural test, never the primary.
3. **Mutation-test every guard.** Break it deliberately and confirm the suite goes red. This is what caught the source-scan test that was passing while unwired.
4. Property-based assertions survive legitimate migrations for free: after the #579 → capacity rework, repointing the rules needed **no test edits**, because they assert the property.
5. A test written during an incident inherits that incident's blind spot — see [[feedback_check_the_dimension_you_were_not_burned_by]].

Related: [[feedback_absence_of_signal_reads_as_success]] — the same family, where a missing check reads greener than a failing one.
