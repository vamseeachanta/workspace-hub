# Legal rule authority

Issue #3522 Phase A establishes strict public codecs and secret-free CI scaffolding without migrating any legacy value. Public Git may contain schemas, opaque rule IDs, severity/target metadata, limits, and tooling. Rule bytes, keys, maps, manifests, anchors, ledgers, mirrors, reports, and COMPLETE records remain private.

`scripts/legal/manage_rule_authority.py validate-public` validates the checked-in registry and policy. `seal` is owner-only and offline. CI may only verify/audit an owner-provisioned envelope after the separately approved environment and ruleset transaction. Failures expose fixed command/verdict/return-code fields, never patterns, paths, endpoints, hashes, or parser fragments.

Phase A does not remove `.legal-deny-list.yaml`, provision a secret or environment, mutate rulesets/CODEOWNERS, perform a private scan, migrate values, create Phase B, promote a slot, or rewrite history.
