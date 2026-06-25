# Conversion funnel + hooks (reference)

A campaign funnel has a **stage** and, at every transition, a **hook** — the deliberate
action that pulls a person to the next stage. Design the hook, don't hope for it.

## The stage → hook model (B2B organic + outreach)

| Stage | What it is | Hook to the next stage |
|-------|-----------|------------------------|
| 1. Reach | A stranger sees a post / touch | Specific, role-targeted promise; high-dwell native format; re-share in first 60 min |
| 2. Engagement | They like / comment / open | Convert the reaction to a **follow / connection**; comment-gate ("comment WORD → I'll send X") |
| 3. Audience | They follow / connect | Turn passive → engaged: newsletter, consistent proof cadence, page CTA button |
| 4. Conversation | DM / call / form fill | Lead-magnet exchange: deliver the asset, capture email, book the call |
| 5. Qualify | Right person, real need | Route: supplier-registration / scoped quick win / specialist conversation |
| Outcome | Registration · RFQ / won work · retainer | Log it; turn the win into the next post (the funnel feeds itself) |

## How to render it as a flowchart for a deliverable
- Two columns: **stage box** (left) and **hook box** (right), with a downward arrow + the
  trigger label ("they follow", "they raise a hand") between rows.
- Color the stages as a darkening ramp into a highlighted "outcome" box.
- Keep page 1 a short summary; put the full funnel on a following page.
- A self-contained HTML/CSS flowchart renders cleanly to PDF via headless Chrome — see the
  `capability-collateral` skill's `references/html-to-pdf.md`.

## Hook design principles
- **One ask per stage.** Each transition has exactly one next action.
- **Asymmetric value first.** Give the proof/asset before asking for time.
- **Lower the cost of "yes."** Scope quick wins a buyer can approve in one email.
- **Instrument every hook.** If you can't measure how many crossed, you can't improve it.
