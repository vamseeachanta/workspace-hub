---
name: devtools-testing-devtools-skills
description: 'Sub-skill of devtools: Testing DevTools Skills.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Testing DevTools Skills

## Testing DevTools Skills


Validate configurations and setups:

```bash
#!/bin/bash
# test_devtools.sh

test_docker() {
    docker --version && echo "PASS: Docker installed" || echo "FAIL: Docker not found"
    docker compose version && echo "PASS: Compose installed" || echo "FAIL: Compose not found"
}

test_cli_tools() {
    command -v fzf && echo "PASS: fzf installed" || echo "FAIL: fzf not found"
    command -v fd && echo "PASS: fd installed" || echo "FAIL: fd not found"
    command -v rg && echo "PASS: ripgrep installed" || echo "FAIL: ripgrep not found"
    command -v bat && echo "PASS: bat installed" || echo "FAIL: bat not found"
}

test_git_config() {
    git config --get rerere.enabled && echo "PASS: rerere enabled" || echo "WARN: rerere disabled"
    git config --get pull.rebase && echo "PASS: pull.rebase set" || echo "WARN: pull.rebase not set"
}

test_vscode() {
    code --version && echo "PASS: VS Code installed" || echo "FAIL: VS Code not found"

*See sub-skills for full details.*
