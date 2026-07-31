> Git-tracked snapshot from Claude auto-memory. Captured: 2026-07-31
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_public_by_default_client_custom_private.md

---
name: feedback_public_by_default_client_custom_private
description: "Data-classification default: analysis/results are PUBLIC; only custom analysis a client specifically reached out for is PRIVATE"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad5ef142-80b1-4f1e-b3bc-4d162ec58029
---

**Default classification for what can be surfaced publicly (website, HF datasets, capability pages, Pages): PUBLIC. The ONLY private tier is custom analysis a client specifically reached out for / commissioned.** (Owner, 2026-07-13.)

**Why:** the ecosystem's analysis is built on public data (BSEE, NOAA, public regulatory filings) and public/derivable methodology — it's a marketing + capability-demonstration asset, meant to be seen. Withholding is the exception (correctness holds, in-flight verification), not the norm. Client-commissioned custom work is the genuinely confidential tier.

**How to apply:**
- Surfacing corrected public-data results (e.g. LT field economics NPV/breakeven, life-to-date on BSEE) on aceengineer.com / HF is the DEFAULT-right action once correctness is cleared — don't treat "public economics numbers" as inherently sensitive.
- A `withheld_columns` / hold is a TEMPORARY correctness guardrail (cf. #971 economics), not a permanent privacy stance — re-surface once the correctness gate clears.
- PRIVATE routing still applies to: client-commissioned custom analysis, and separately vendor-licensed codes/standards data (that's [[codes-standards-data-routing]], a different axis — licensing, not client-custom).
- Still confirm before the *first* public disclosure of a class of number (the trigger-pull is the owner's), but the default posture is "public unless client-custom." See [[feedback_one_result_everywhere]] (clean single-result product language on those public surfaces).

Applied: C9 (wh#3485) — surfacing corrected life-to-date economics on the public hub is correct because it's public-data analysis, not client-custom. See [[project_wed_economics_c9_session_handoff]], [[project_hf_backed_website_capability_surfaces]].
