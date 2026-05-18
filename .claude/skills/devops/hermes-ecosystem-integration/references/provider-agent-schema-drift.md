# Provider agent schema drift during Hermes ecosystem work

Use this reference when a Hermes/provider background run fails because provider-specific agent definition config contains keys the provider wrapper no longer accepts.

## Pattern

Provider wrappers can diverge in accepted agent-definition keys. A config key that is harmless for one provider may be rejected by another during background or delegated runs. Treat these as configuration/schema drift, not as proof that the provider is unusable.

## Fix-first workflow

1. Identify the provider and the rejected key from the stderr/log line.
2. Locate the agent-definition/config artifact that injects the key.
3. Remove or conditionalize the unsupported key for that provider; do not add broad runtime suppression unless the provider docs require it.
4. Add/extend a regression check that validates generated provider configs do not include unsupported keys for that provider.
5. Re-run the smallest failing provider invocation or config-generation test.
6. If discovered during an unrelated issue closeout, create a separate follow-up GitHub issue and keep the original issue closeout scoped to its verified deliverables.

## Example class

A Gemini background/provider run may reject Claude-style control-plane fields such as `permissionMode` when those fields leak into Gemini agent definitions. The durable fix is to remove or provider-gate the unsupported key in the generated Gemini config, then verify the resulting config shape.

## Closeout rule

Do not blend provider schema drift into the issue that merely surfaced it unless that issue's approved plan includes provider config remediation. Capture it as a linked follow-up with labels for AI orchestration/tooling/config and verify the issue URL after creation.
