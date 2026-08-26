---
name: feedback-adversarial-review-catches-what-self-review-cannot
description: Codex REJECTed two CFD pages I had self-reviewed for days; verifying its findings against sources found most correct, one wrong, and one worse than reported.
metadata:
  type: feedback
---

Dispatching a genuinely adversarial cross-provider review of technical documents
pays even when the author has been careful. On 2026-08-25 Codex returned
**NOT-APPROVE on both** hull-CFD wiki pages I had been refining for days.

Outcome after verifying every finding against primary sources rather than
accepting or dismissing them:

- **Most were correct**, including a spliced value (a scale-comparison table
  paired `Cf 0.732` from one run with `(1+k) 0.807` from another, matching no row
  of the page's own matrix) and a causal overclaim (two points on *different
  hulls* presented as a Reynolds-number trend).
- **One was worse than Codex said.** It flagged a mis-stated uncertainty band;
  fetching the paper showed the figure existed nowhere in the source at all, and
  the same table reopened an elimination I had closed. See
  [[feedback-trace-quoted-uncertainty-to-source-table]].
- **One was wrong and I rejected it.** Codex argued `τ_w ∝ u_τ²` so `Cf ∝ k`, not
  `√k`. For the Launder–Spalding form `nutkWallFunction` uses, `u* = C_μ^¼√k` and
  `τ_w` is linear in `u*`, so `√k` is right. Its *secondary* point — that Spalding
  removes the direct algebraic path from k but not indirect coupling through the
  k–ω–ν_t solution — was valid and got incorporated.

**Why:** self-review cannot catch a value you carried forward confidently, because
confidence is exactly what makes it invisible. An outside reviewer with no stake
in the earlier reasoning finds it in one pass. But "full equal rights" means
findings are adjudicated on evidence, not adopted wholesale — accepting a wrong
finding to seem responsive corrupts the document just as much as ignoring a right
one.

**The reviewer can only check your reasoning, not your measurements.** Codex
concluded "none of these results is converged" and I published it. It was wrong —
because the drift numbers I had handed it were computed first-row-versus-last-row
of a trailing window, a statistic dominated by iteration oscillation that
overstated real movement by two orders of magnitude. On the window-mean test the
same runs sit at +0.004 % and +0.027 %, comfortably converged. The reviewer
reasoned correctly from bad inputs. **When a finding rests on a number you
supplied, re-derive the number before accepting the finding** — otherwise an
adversarial review launders your own measurement error into an external verdict.

**How to apply:** invoke via
`scripts/review/submit-to-codex.sh --file <path> --prompt <adversarial prompt>`
(handles the `CLAUDECODE` unset; **direct `codex exec` with `--full-auto` is
blocked by the auto-mode classifier**, and any `codex exec` invocation needs
`< /dev/null` or it hangs reading stdin). Force the stance in the prompt: state
that the default verdict is NOT-APPROVE, name the specific claims to attack, and
demand a severity + quoted text + replacement wording per finding. Then verify
each finding before acting. Related: [[feedback_adversarial_review_stance]],
[[feedback_cross_provider_review_payoff]],
[[feedback_verify_subagent_line_citations_not_just_claims]].
