---
name: reference-gmail-search-no-contacts-autocomplete
description: "Gmail MCP tools search messages only, not Google Contacts/autocomplete — a person only in deleted/cleaned-up mail becomes unfindable"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 98f98058-2d4f-4def-b990-4e321d552886
---

The claude.ai Gmail MCP tools (`search_threads`, `get_thread`, `create_draft`, label ops) operate **only on messages/threads, labels, and drafts**. There is **no contacts tool** — I cannot read Google Contacts or the auto-saved "Other contacts" list that powers Gmail's compose **autocomplete** (that lives in the People API, a separate source).

Consequence: `search_threads` can find an email address **only if the person appears in an actual message**. Someone you've only ever reached via autocomplete/Contacts (never in a received/sent thread) is invisible to me.

**Why it matters:** the user *deletes emails once the work is done — nothing important is left in the inbox* (see [[feedback-emails-are-ephemeral-strategy-repo-is-ssot]]). When the last message from/to a contact is deleted, that contact's address stops being findable via search even though it still lives in their Contacts and still pops up in the compose To-field autocomplete. So "I couldn't find X's email" from me may just mean X's threads were cleaned up — not that the user never had it; the durable record lives in the `aceengineer-strategy` repo, not Gmail.

**How to apply — recover the address before giving up:** the user's full contact rolodex is backed up (harvested from Outlook/Gmail exports) in `aceengineer-admin/admin/contacts/master_contacts.csv` (~2,600 rows: email, alt_emails, full_name, company, temperature…) — see [[project_contact_directory_collation]]. **Grep that CSV first**; it holds people who are NOT in any Gmail thread (contacts-only). Only if absent there, stage the draft complete with subject/body/cc and **leave the To field blank** for the user's autocomplete (the `to` field is optional in `create_draft`), or ask them to paste it. Never claim an address is unavailable without (a) grepping master_contacts.csv and (b) saying *why* Gmail search missed it (messages-only). Real example: Richard D'Souza (deepwater life-cycle poster co-author) — not in any thread, so Gmail-search-invisible, but found in master_contacts.csv as `dsouzarichard49@gmail.com`; drafted To=D'Souza, cc Terri Ivers (`terrance.ivers@gmail.com`).
