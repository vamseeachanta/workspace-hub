---
name: agent-teams-1-create-team
description: 'Sub-skill of agent-teams: 1. Create team (+5).'
version: 1.0.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# 1. Create team (+5)

## 1. Create team

```python
TeamCreate(team_name="my-work", description="Implementing WRK-205")
```


## 2. Create tasks

```python
TaskCreate(subject="Build SKILLS_GRAPH.yaml", description="...", activeForm="Building graph YAML")
TaskCreate(subject="Script diverged canonical_ref", description="...", activeForm="Scripting canonical refs")
```


## 3. Spawn teammates

```python
Task(
    subagent_type="general-purpose",
    name="graph-builder",
    team_name="my-work",
    prompt="You are graph-builder. Check TaskList for your work..."
)
Task(
    subagent_type="Bash",
    name="script-runner",
    team_name="my-work",
    prompt="You are script-runner. Check TaskList for your work..."
)
```


## 4. Assign tasks

```python
TaskUpdate(taskId="1", owner="graph-builder", status="in_progress")
TaskUpdate(taskId="2", owner="script-runner", status="in_progress")
```


## 5. Stay responsive

While teammates work, the main orchestrator stays available for user messages.
Use `run_in_background=True` for long tasks. Check progress with `TaskList`.


## 6. Shutdown

```python
SendMessage(type="shutdown_request", recipient="graph-builder", content="Work complete")
SendMessage(type="shutdown_request", recipient="script-runner", content="Work complete")
# After both confirm shutdown:
TeamDelete()
```
