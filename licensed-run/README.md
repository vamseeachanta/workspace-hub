# Retired delivery helpers

Deckhand retired 2026-10-18 (deckhand issue 599).

The former setup, polling and synchronization batch entry points now exit with
an error before accessing any repository, queue, policy or solver. No replacement
execution route is asserted here.

The independent model-building and validation helpers in this directory are
outside the retired delivery channel.
