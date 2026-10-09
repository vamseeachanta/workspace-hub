# Public Surface Guard Reusable Workflow

Public repositories can adopt the workspace-hub guard with one reusable-workflow job:

```yaml
jobs:
  public-surface-guard:
    uses: vamseeachanta/workspace-hub/.github/workflows/public-surface-guard.yml@main
```

The blocking job fails on host IPs, denylisted physical hostnames, secret-shaped strings, and private keys in PR added lines. The O13 client-identifier job is warn-only and posts one masked PR comment when the configured client-codename registry contains a probable match.
