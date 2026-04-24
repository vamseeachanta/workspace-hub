# Achantav Gmail Sweep — Pre-Session Plan

**Date:** 2026-04-24
**Method:** Same as ace sweep (see `docs/sessions/2026-04-24-gmail-ace-sweep.md`)
**Account:** achantav@gmail.com
**Status:** Draft — user must confirm decisions below before filter install

## Hypothesis about inbox composition

Based on #1966 (994 clean contacts; colleague 68, alumni 39, client 37, financial 27, vendor 27, personal 14) plus routing-yaml Personal block:

- **Career networking** — LinkedIn dominant; reply.linkedin.com InMail relays.
- **School / family ops** — ParentSquare (time-sensitive).
- **Dev notifications** — GitHub, Vercel, OpenRouter.
- **Personal finance / tax** — TurboTax; possibly bank/brokerage.
- **Industry light** — ogj@news.ogj.com.
- **Marketing noise** — per #1990, ~27k promo/social/spam is the main cleanup target.
- **Self-shuttle** — #1990: 164 personal→ace, 19 ace→personal. Not bulk; leave.

Volume likely larger/noisier than ace. CRE N/A. Industry minor. AutoNoise biggest lever.

## Proposed filter set

### CRE filter
**N/A.** CRE listings flow to the ace account only; no sandsig/marcus-millichap pattern in routing-yaml Personal block. Skip.

### AutoNoise filter
**Proposed From clause (seed set — user should extend live):**

```
from:(@collide.io OR @promote.weebly.com OR @e.swimoutlet.com OR @email.myflighthub.com OR @mail.urbanairparks.com OR @e.stantonoptical.com OR @lists.wikimedia.org OR @jongordon.com OR @atticbuddies.com OR @email.theparkingspot.com OR @academia-mail.com OR @accounts.google.com OR @suzeorman.com OR @marketing.goindigo.in OR @deeplearning.ai OR @gamemail.com OR @m.learn.coursera.org OR @irctc.co.in OR @info.tatacapital.co.in OR @info.dpam.com OR @blueskysfund.com OR @indianstarllc.ccsend.com OR @reply.linkedin.com OR @talkmatch.com OR @sale.craigslist.org)
```

**Rationale:**
- Rows 1-22: carry over from ace AutoNoise (cross-listed marketing/travel/newsletter noise likely present on personal too).
- `reply.linkedin.com` — 8 LinkedIn InMail relays flagged in #1966 spam review.
- `talkmatch.com` — 8 entries flagged as dating/social, likely unwanted.
- `sale.craigslist.org` — 9 entries, flagged spam in #1966.

### Industry filter
Minimal. Proposed:
```
from:(ogj@news.ogj.com OR @substack.com)
```
Matches the one clear industry sender in routing-yaml Personal block; substack optional if user subscribes to newsletters on this account.

### VIP filter
Family/close-friend senders not enumerable from repo. Framework: **user enumerates 5-10 senders live** (surname `achanta*`, close friends, must-keep .edu alumni). Clause: `from:(<addrs>) → Star + Important + Never spam`.

## Decisions user must make before filter install

1. **linkedin.com** — AutoNoise (marketing digest/job-alert noise) OR Industry (career-reference archive)? Routing-yaml says archive; ace sweep skipped it.
2. **parentsquare.com** — KEEP in inbox (school alerts are time-sensitive) OR label-and-skip? Recommend keep-in-inbox.
3. **github.com** — VIP (dev-signal dependabot/PR alerts) OR dedicated `GitHub` label + skip-inbox (per ace-sweep gap #4)? Recommend dedicated label.
4. **vercel.com / openrouter.ai** — fold into `GitHub` label as "Dev" OR separate `Dev` label?
5. **em1.turbotax.intuit.com** — Industry/Tax label (seasonal, archive) OR inbox (tax-season actionable)? Recommend `Tax` label, skip-inbox outside Jan-Apr.
6. **Self-forward shuttle** (achantav→ace) — leave alone (per #1990) OR add label `Shuttle` for visibility?
7. **VIP seed list** — list 5-10 names/addresses to star.
8. **Override-filters setting** — flip to "Don't override filters" (ace lesson S1)? Recommend YES.

## Gaps where live inbox scan is needed

- Family / close-friend sender addresses (not in repo).
- New noise domains accumulated since routing-yaml was written (#1990 estimated 27k promo/social/spam; most specific domains unnamed).
- Whether LinkedIn digests dominate vs. direct-message InMail (changes the filter shape).
- Whether financial-institution senders (bank, brokerage, 401k) need a `Finance` label.
- Seth Equities / SPARK / Indian Eagle equivalents on this account.
- Whether the #1990 self-forward pattern has grown since 2026-04-06.

## Estimated time savings

If user answers the 8 decisions above and supplies the VIP seed list before session start, browser work ≈ **15-20 min** instead of 45 min. Without VIP list, still ~25 min (VIP filter deferred to a follow-up).
