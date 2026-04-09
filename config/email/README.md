# Email Communication Style Profiles

Per-account style profiles that agents use when drafting email replies and outreach messages.

## Files

| File | Account | Tone |
|---|---|---|
| `ace-style.yaml` | vamsee.achanta@aceengineer.com | Professional-technical, concise |
| `personal-style.yaml` | achantav@gmail.com | Casual-terse, abbreviated |
| `skestates-style.yaml` | skestatesinc@gmail.com | Business-formal-warm |

## How Agents Should Use These Profiles

1. **Identify the sending account** — which Gmail account is the reply going from?
2. **Load the matching style profile** — read `config/email/{account}-style.yaml`
3. **Determine formality context** — check the `formality_rules` list for the situation (new client, ongoing thread, vendor follow-up, etc.)
4. **Apply greeting, closing, and signature** — use the patterns from the profile, not generic defaults
5. **Match tone and length** — ACE is concise (2-5 sentences), personal is ultra-short (1-2), SKEstates is medium (3-6)
6. **Use example messages** for calibration — the `examples` section shows real patterns

## Account Selection Guide

| Recipient Type | Account | Profile |
|---|---|---|
| Engineering clients, colleagues, recruiters | ace | `ace-style.yaml` |
| Family, friends, personal business | personal | `personal-style.yaml` |
| Tenants (Family Dollar, Dollar Tree) | skestates | `skestates-style.yaml` |
| Vendors (property maintenance, pest, HVAC) | skestates | `skestates-style.yaml` |
| Insurance, HOA, tax/CPA (property) | skestates | `skestates-style.yaml` |
| Banks, personal finance, taxes (personal) | personal | `personal-style.yaml` |

## Integration Points

- **gmail-triage** skill: uses profiles when suggesting draft responses in the daily digest
- **gmail-outreach** skill: uses profiles for touchbase message drafting (see `#1986` reference in that skill)
- **email-as-queue workflow**: profiles inform the ACT stage when drafting replies

## Updating Profiles

Profiles are derived from analysis of ~30 sent emails per account. To refresh:
1. Re-analyze recent sent messages for pattern changes
2. Update the relevant YAML file
3. Commit with reference to #1986

## Reference

- GitHub issue: [#1986](https://github.com/vamseeachanta/workspace-hub/issues/1986)
- Parent issue: [#1963](https://github.com/vamseeachanta/workspace-hub/issues/1963)
- Email workflow design: `docs/design/email-as-queue-workflow.md`
