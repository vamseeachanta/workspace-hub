---
name: feedback-trace-quoted-uncertainty-to-source-table
description: A benchmark band becomes an acceptance criterion only after you have opened the source table; "±2.5 %" survived a full campaign and was in no paper.
metadata:
  type: feedback
---

Before a published tolerance is used as an acceptance criterion, open the source
table and read what the number actually is. On the B1552/KCS hull-CFD campaign
(2026-08-25) I quoted **"(1+k) = 1.117 ± 2.5 % comparison-error spread"** across
wiki pages, the client report, task descriptions and review prompts for days.
Korkmaz Ocean Eng 220:108451 Table 9 in fact reports `Mean(I) = 0.117` with
`σ(I) = 1.2 %` — a **standard deviation over unsystematically varied CFD
submissions**. Not experimental. Not a comparison error. Not a tolerance anyone
certified. The ±2.5 % appears nowhere in the paper.

Three things went wrong at once, and each is the general case:

- **An ensemble mean was treated as ground truth.** 1.117 is where 7 CFD codes
  happened to land, not what a towing tank measured.
- **A scatter statistic was promoted to an acceptance band.** Missing by 8.5 %
  reads as "just outside ±2.5 %" but is ~7σ against the real 1.2 %.
- **The same table held a finding I had already ruled out.** `Mean(I) 0.117` vs
  `Mean(N) 0.165` says the *friction line* moves the answer 4.3 % — more than
  any numerical setting I was sweeping — while my page said "friction-line
  choice: eliminated". Opening the table both corrected the band and reopened
  a closed elimination.

**Why:** an unverified band is worse than no band. It sets the bar in the wrong
place, silently, and every downstream judgement inherits it — including what
gets told to a client as "the acceptance band".

**How to apply:** any time a tolerance, spread, band or uncertainty is quoted
from literature, fetch the source and cite table + row + the source's own wording
for the statistic. `pdftotext -layout` on the publisher/repository PDF is usually
enough. If the source cannot be opened, say the band is an engineering judgement
and own it as yours — which is what the B1552 report now does. Related:
[[feedback-adversarial-review-catches-what-self-review-cannot]],
[[feedback_validation_chain_bsee_first_then_interpretation]].
