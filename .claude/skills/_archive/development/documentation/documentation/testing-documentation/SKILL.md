---
name: documentation-testing-documentation
description: 'Sub-skill of documentation: Testing Documentation.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Testing Documentation

## Testing Documentation


Validate documentation quality:

```bash
#!/bin/bash
# test_docs.sh

test_markdown_lint() {
    markdownlint docs/**/*.md && echo "PASS: Markdown lint" || echo "FAIL: Markdown lint"
}

test_build() {
    mkdocs build --strict && echo "PASS: Build successful" || echo "FAIL: Build failed"
}

test_links() {
    find docs -name '*.md' -exec markdown-link-check -q {} \; && \
        echo "PASS: Links valid" || echo "FAIL: Broken links found"
}

test_spelling() {
    cspell docs/**/*.md && echo "PASS: Spelling" || echo "FAIL: Spelling errors"
}

# Run all tests
test_markdown_lint
test_build
test_links
test_spelling
```
