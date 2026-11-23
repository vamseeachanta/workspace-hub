---
name: investigative-issue-workdown
description: A robust workflow for handling a batch of related investigative tasks that require file system research, documentation, and version control.
---
# Skill: Investigative Issue Workdown

## Description

A robust workflow for handling a batch of related investigative tasks, such as those assigned by a cron job or a project board. This pattern is ideal for tasks that require researching the file system, generating a report or artifact, committing the result to version control, and closing the source issue.

## When to use this skill

Trigger this skill when you are assigned 2-5 related tasks in a single prompt, where each task follows a similar "investigate -> document -> commit -> close" lifecycle. It is particularly useful when the investigation involves searching across large or numerous directories.

## Workflow Steps

1.  **Initial Planning:** List the assigned tasks.
2.  **Sequential Execution:** Address each task one by one to ensure reliability and clear separation of work.
3.  **Investigation:** Use file system tools like `search_files` to gather the necessary information for the current task. If a required path is inaccessible, note this finding and proceed.
4.  **Documentation:** Create the required artifact (typically a Markdown report) using `write_file` and populate it with your findings.
5.  **Version Control:** Use `terminal` to `git add` and `git commit` the newly created file. Use a clear commit message that references the task or issue number.
6.  **Task Closure:** Use `terminal` to interact with the issue tracker CLI (e.g., `gh issue close 1234`) to close the completed task.
7.  **Iterate:** Repeat steps 3-6 for the next task until all are complete.
8.  **Final Summary:** Conclude with a summary of the work performed, listing each completed task and the artifact created.

## Pitfalls & Best Practices

- **Avoid `execute_code` for Batch File Searches:** Do **not** use a single `execute_code` block to run multiple `search_files` calls in a loop, especially on large or complex directory structures. This approach is prone to intermittent `JSONDecodeError` failures when tool outputs are large or contain unexpected characters, making the script unreliable.
- **Prefer Sequential Tool Calls:** The most robust method for file system investigation is to use direct, sequential `search_files` tool calls from the main agent loop for each query. While this may appear less concurrent, it is far more reliable and provides clearer, more debuggable outputs.
- **Handle Inaccessible Paths Gracefully:** If a file path or network mount is unavailable during the investigation, do not halt the entire batch. Document the inaccessibility in your report for that specific task and continue with the remaining tasks.
