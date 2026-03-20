# Module: Setup — Claude Code in Action

Source: https://anthropic.skilljar.com/claude-code-in-action/301615
Docs: https://code.claude.com/docs/en/quickstart

## Installation

| Platform | Command |
|----------|---------|
| macOS (Homebrew) | `brew install --cask claude-code` |
| macOS / Linux / WSL | `curl -fsSL https://claude.ai/install.sh \| bash` |
| Windows CMD | `curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd` |

After install: run `claude` → prompted to authenticate on first run.

## Cloud Provider Variants

- **AWS Bedrock**: https://code.claude.com/docs/en/amazon-bedrock
- **Google Cloud Vertex**: https://code.claude.com/docs/en/google-vertex-ai

## Workspace Status

Already installed on dev-primary (claude=2.1.71), dev-secondary (claude=2.1.56), licensed-win-1 (Windows).
Auth via Anthropic direct (not Bedrock/Vertex).
