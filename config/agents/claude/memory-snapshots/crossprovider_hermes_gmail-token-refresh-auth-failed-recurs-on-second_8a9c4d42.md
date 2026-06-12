---
name: crossprovider hermes gmail-token-refresh-auth-failed-recurs-on-second
description: Gmail token refresh AUTH_FAILED recurs on secondary accounts; token life assumption is violated
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [gmail-auth, token-lifecycle, account-maintenance]
---

Personal (achantav@gmail.com) and SKEstates Inc (skestatesinc@gmail.com) show persistent AUTH_FAILED on 2026-04-29 digest run. Refresh tokens are not persisting across runs or session boundaries; reauthentication loop needed or token lifetime assumptions require revision.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
