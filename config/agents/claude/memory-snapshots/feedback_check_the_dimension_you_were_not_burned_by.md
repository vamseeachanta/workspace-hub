---
name: feedback-check-the-dimension-you-were-not-burned-by
description: "After fixing a defect on one dimension, the fix often fails on a dimension you did not think to check — and the test you write will encode the same blind spot"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a873f663-bb0d-4ae1-9209-add92b7b1a13
  modified: 2026-07-31T14:11:30.013Z
---

**When fixing a defect, name the dimensions the thing must satisfy BEFORE choosing a fix — and check every one, not the one that just bit you.**

**Why:** 2026-07-31, twice in one day, same subsystem.

1. deckhand#579: solver/hydro work routed to a host whose capability list was **inherited from a retired machine** — 177 issues aimed at a box that could not obtain an OrcaFlex licence. I fixed it by repointing to the host with the only dated **licence** attestation.
2. Owner: *"ws014 is not powerful enough."* That host is a **workstation**. The one I routed away from is the 64-core / 255.7 GB batch node. I had traded a licence failure for a **capacity** failure and called it fixed.

Capability was two dimensions — licence AND capacity — and I only re-checked the one I had just been burned by.

**The sharper half:** the test I wrote that morning **passed my wrong answer cleanly**. It asserted a proven licence and said nothing about capacity. A test written in the shadow of one incident inherits that incident's blind spot, then certifies the next failure as correct.

**How to apply:**

1. Before fixing, write down every dimension the target must satisfy. For a routing target: licence, capacity, reachability, concurrency budget, data access. For a label: vocabulary, cardinality, who consumes it.
2. Assert **all** of them, or state in the test which are deliberately out of scope and where they are covered.
3. Treat a green test written during an incident as evidence about that incident only.
4. **Rerouting is not always the fix.** When the *designated* target is blocked on a prerequisite, silently sending work to a lesser one hides the blockage — it runs badly instead of visibly waiting. Prefer an explicit, dated `blocked_on` that names the prerequisite. See [[feedback_absence_of_signal_reads_as_success]].
5. Get a second party to review the **design**, not just the code. A Codex design review the same day caught two fail-open defects in `apply_wip()` *before* I built on them — cheaper than finding them after.

Landed as `capacity:` + `blocked_on:` in `.claude/memory/kanban/routing-rules.yaml` and `tests/dispatch/test_route_capacity.py` (workspace-hub PR #3730).
