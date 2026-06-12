---
name: crossprovider hermes himalaya-requires-rust-cargo-install-google-work
description: himalaya requires Rust/cargo install; Google Workspace OAuth entirely absent (no tokens, no libraries)
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [email, tooling, oauth]
---

himalaya (email CLI): 5,870 GitHub stars, requires Rust toolchain + cargo (not available on test machine). googleapis OAuth path completely missing—no google_token.json, no client secrets, no Python google-auth libraries installed. App Passwords approach (via himalaya TOML config) is fully documented in gmail-multi-account skill. OAuth setup would require: pip install google-auth google-auth-oauthlib google-api-python-client + credential generation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
