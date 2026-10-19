# Guarded repository planning fallback

Deckhand retired 2026-10-18 (deckhand issue 599). The former bot
scope-activation commands no longer apply.

If a repository operation is denied by an active authorization control:

1. Preserve the denial and report the missing authorization or context.
2. Do not bypass the control or interpret an inaccessible private repository as
   absent.
3. Keep useful local planning separate from live GitHub issue state. Without
   real issue numbers, do not create canonical issue-numbered plans.
4. A local planning bundle may record proposed issue structure, dependencies,
   tests, affected paths and the unresolved authorization requirement.
5. Resume GitHub writes only after the applicable repository authorization is
   established.

No replacement delivery or scope-activation route is documented here.
