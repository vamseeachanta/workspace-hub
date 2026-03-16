---
name: miro-api-github-actions-integration
description: 'Sub-skill of miro-api: GitHub Actions Integration.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# GitHub Actions Integration

## GitHub Actions Integration


```yaml
# .github/workflows/miro-sync.yml
name: Sync to Miro

on:
  issues:
    types: [opened, labeled]
  pull_request:
    types: [opened, closed, merged]

jobs:
  sync-miro:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install miro-api requests

      - name: Create issue card in Miro
        if: github.event_name == 'issues'
        env:
          MIRO_ACCESS_TOKEN: ${{ secrets.MIRO_ACCESS_TOKEN }}
          MIRO_BOARD_ID: ${{ secrets.MIRO_BOARD_ID }}
        run: |
          python << 'EOF'
          import os
          from miro_api import Miro

          miro = Miro(access_token=os.environ["MIRO_ACCESS_TOKEN"])
          board_id = os.environ["MIRO_BOARD_ID"]

          # Create sticky note for new issue
          issue_title = "${{ github.event.issue.title }}"
          issue_number = "${{ github.event.issue.number }}"
          issue_url = "${{ github.event.issue.html_url }}"

          miro.sticky_notes.create(
              board_id=board_id,
              data={
                  "content": f"#{issue_number}: {issue_title}\n\n{issue_url}"
              },
              style={"fillColor": "yellow"},
              position={"x": 0, "y": 0, "origin": "center"},
          )
          print(f"Created sticky note for issue #{issue_number}")
          EOF

      - name: Update PR status in Miro
        if: github.event_name == 'pull_request'
        env:
          MIRO_ACCESS_TOKEN: ${{ secrets.MIRO_ACCESS_TOKEN }}
          MIRO_BOARD_ID: ${{ secrets.MIRO_BOARD_ID }}
        run: |
          python << 'EOF'
          import os
          from miro_api import Miro

          miro = Miro(access_token=os.environ["MIRO_ACCESS_TOKEN"])
          board_id = os.environ["MIRO_BOARD_ID"]

          pr_title = "${{ github.event.pull_request.title }}"
          pr_state = "${{ github.event.action }}"

          colors = {
              "opened": "light_blue",
              "closed": "red",
              "merged": "green",
          }

          miro.sticky_notes.create(
              board_id=board_id,
              data={"content": f"PR: {pr_title}\nStatus: {pr_state}"},
              style={"fillColor": colors.get(pr_state, "gray")},
              position={"x": 500, "y": 0, "origin": "center"},
          )
          EOF
```
