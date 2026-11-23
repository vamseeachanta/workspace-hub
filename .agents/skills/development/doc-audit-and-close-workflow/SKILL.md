---
name: doc-audit-and-close-workflow
category: development
description: A repeatable workflow for executing a batch of documentation, audit, or planning tasks. For each task, it audits the current state, creates a plan/report, commits the result, and closes the corresponding GitHub issue. The process is designed to be idempotent.
---

### Trigger

When a user provides a list of structured tasks that each involve:
1.  Auditing or analyzing a state.
2.  Creating or updating a documentation or plan file (e.g., `.md`).
3.  Committing the file to Git.
4.  Closing a corresponding GitHub issue.

This skill is ideal for cron jobs or scripted, multi-step administrative actions.

### Workflow

1.  **Parse Tasks:** Break down the user prompt into a list of discrete tasks. Each task should have an associated file path, content creation step, commit message, and issue number.

2.  **Iterate Through Tasks:** Execute the following steps for each task in the list, one by one. Do not proceed to the next task until the current one is complete.

3.  **Audit & Idempotency Check:** Before creating the file, check if it already exists using `read_file` or `search_files`. This is the most critical step to prevent re-doing work or overwriting existing progress.

4.  **Conditional File Creation:**
    *   **If the file does NOT exist:** Perform the necessary research steps (e.g., `search_files`, `read_file`) to gather context. Then, use `write_file` to create the specified document.
    *   **If the file already exists:** Do nothing. Acknowledge that this step has already been completed and move on. Do not overwrite the file.

5.  **Commit Changes:**
    *   Use `terminal` to execute `git add <file_path>`.
    *   Use `terminal` to execute `git commit -m "<commit_message>"`.
    *   **Note:** This command may fail or return a non-zero exit code if there are no changes to commit (i.e., if the file already existed). This is expected and should not be treated as an error. The workflow should continue.

6.  **Close GitHub Issue:**
    *   Use `terminal` to execute `gh issue close <issue_number> -c "<comment>"`.
    *   **Note:** This command may return a message indicating the issue is already closed. This is expected and should not be treated as an error.

7.  **Report Completion:** After completing all tasks, provide a summary report of the actions taken for each task, noting which steps were performed and which were skipped because they were already complete.

### Example Task Structure (from user prompt)

```
TASK 1: Mount Drive Resource Audit (#1776)
- Read docs/document-intelligence/ for mount drive docs
- Search for legal scan results: search_files pattern="legal" output_mode=files_only
- Create: docs/document-intelligence/mount-drive-audit.md covering resources...
- Commit: git add that file && git commit -m "doc-intel: mount drive resource audit (#1776)"
- Close: gh issue close 1776 -c "Mount drive audit completed..."
```