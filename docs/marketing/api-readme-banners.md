# API README banner audit

The read-only audit checks the README checklist in issue #3300. It checks text
placement and contract elements, and requires an independently inspected catalog
status. It does not establish current API availability or engineering validity.

## Revision history

| Revision | Date | Change and reason |
|---|---|---|
| Initial | 2026-10-22 | Add a repeatable banner audit and a historical-catalog gate to prevent unsupported rollout claims. |

## Scope and sources

The issue's checklist is authoritative for this task: `digitalmodel`,
`worldenergydata`, `deckhand`, `deckhand-sandbox`, and `aceengineer-website`.
It differs from the full ecosystem repository registry.

- Issue #3300, **Draft banner snippet**, **Checklist** and **Dependencies**:
  common contract, repository set, catalog deployment prerequisite and tailored
  introductions. The issue comments record earlier merged banners; they do not
  establish their current contents.
- Linked issues `deckhand#497` and `deckhand#501`: API response contract and
  catalog ownership. The audit does not regenerate or execute either API.
- [Public catalog](https://aceengineer.com/api-catalog.html), inspected
  2026-10-22: the page is titled **Historical workflow catalog** and states that
  the former service is not currently offered. HTTP 200 establishes that the page
  can be retrieved, not that a live API exists. Current catalog status is
  `historical`; rollout is `NOT_EVALUATED`.
- [CommonMark 0.31.2, ATX headings](https://spec.commonmark.org/0.31.2/#atx-headings)
  and [fenced code blocks](https://spec.commonmark.org/0.31.2/#fenced-code-blocks):
  syntax basis for section boundaries and ignoring fenced examples. The audit
  implements a limited text convention, not a complete Markdown renderer.

No engineering equations, coefficients, workflow counts or numerical acceptance
limits are introduced. The required values are the issue's textual contract and
an explicit catalog-status input.

## Method

Run [the audit](../../scripts/marketing/api_readme_banners.py) against explicit
README snapshots. It performs no network requests, repository discovery or
writes. Input paths are never included in its JSON report.

Each repository must contain one contiguous blockquote before the first ATX
subsection. That quote must contain all of the following:

- Deckhand API identification;
- API path terminology;
- `POST /api/run`;
- `standards-traceable HTML report URL`;
- determinism wording, either `deterministic` or `same input, same output`;
- an HTTPS link to the catalog page, allowing its `www` redirect host;
- the reference locator `docs/deckhand/API.md`.

Markdown emphasis and code delimiters do not affect matching. Fenced examples
and text below a subsection cannot satisfy the introduction requirement. Separate
quotes cannot combine to satisfy one banner. Repository-specific lead wording
and the truth of broader capability claims still require maintainer review.

Supply `--catalog-status live`, `historical` or `unverified` based on independent
inspection. There is no default and no HTTP-status inference. This input is a
recorded assertion, not authenticated deployment evidence. A non-live catalog
always gives overall `NOT_EVALUATED`, while individual text defects remain
visible as `FAIL` rows. With a declared live catalog, known defects give overall
`FAIL`; otherwise an absent or unreadable snapshot gives `NOT_EVALUATED`. Only
complete matching snapshots and a declared live catalog give `PASS`. The command
returns success only for `PASS`; malformed arguments are usage errors.

## Worked example: complete text, historical catalog

Input: save this synthetic banner as `snapshots/complete.md`. It demonstrates
matching syntax and is not approved wording for a currently unavailable service.

```markdown
# Example

> **Part of the Deckhand API — the API for real-world work.**
> The workflows here are API paths: `POST /api/run` returns a
> **standards-traceable HTML report URL**, deterministic for the same inputs.
> Catalog: https://aceengineer.com/api-catalog.html
> API reference: deckhand `docs/deckhand/API.md`

## Usage
```

Use that fixture for every member of the issue checklist:

```sh
python scripts/marketing/api_readme_banners.py \
  --catalog-status historical \
  --readme digitalmodel=snapshots/complete.md \
  --readme worldenergydata=snapshots/complete.md \
  --readme deckhand=snapshots/complete.md \
  --readme deckhand-sandbox=snapshots/complete.md \
  --readme aceengineer-website=snapshots/complete.md
```

Independent answer: all required tokens occur together in the introductory
quote, so every repository's text row is `PASS`. The catalog input is historical,
so the overall result is `NOT_EVALUATED` and the command returns failure. Changing
the catalog input to `live` would pass the text gate only; it would not prove
hosting, authentication, report generation or capability qualification.

[The tests](../../tests/marketing/test_api_readme_banners.py) execute this example
using temporary files, compare the expected Boolean results, and verify that the
input bytes remain unchanged. Negative cases delete individual contract tokens,
move the banner below a heading, substitute misleading destinations, omit
snapshots, and supply malformed or duplicate arguments.

## Observed state and remaining work

Inspection on 2026-10-22 found existing API introductions in `deckhand`,
`deckhand-sandbox` and `aceengineer-website`. The first two match the text contract;
the website introduction lacks the API-reference locator. The inspected
`digitalmodel` and `worldenergydata` introductions do not contain the API banner.
These observations concern retrieved default-branch snapshots only. They are not
pinned deployment evidence or a claim that historic merged changes never existed.

All rollout remains `NOT_EVALUATED` while the public catalog describes a
historical service. Before changing other repositories, the maintainers should
reconcile the issue's live-service framing with the current catalog, inspect the
then-current API reference, and prepare separate draft changes where needed.
Do not add live path counts or claim CAD/CAM, manufacturing or safety are shipped.
Do not copy current live-service claims from another README as proof.

The issue remains open: this change supplies the audit, explicit catalog gate,
tests and worked example in the coordinating repository. It does not edit the
other repositories, revive the service, install a periodic task or update the
separate presence-sync implementation.
