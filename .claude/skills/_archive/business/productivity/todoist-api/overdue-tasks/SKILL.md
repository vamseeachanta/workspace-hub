---
name: todoist-api-overdue-tasks
description: 'Sub-skill of todoist-api: Overdue Tasks.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Overdue Tasks

## Overdue Tasks


"""
    for task in overdue:
        report += f"- [{priority_emoji(task.priority)}] {task.content} (Due: {task.due.string})\n"

    report += "\n## Today's Tasks by Project\n"
    for project_id, project_data in projects.items():
        report += f"\n### {project_data['name']}\n"
        for task in project_data["tasks"]:
            report += f"- [{priority_emoji(task.priority)}] {task.content}\n"

    report += "\n## High Priority (Upcoming)\n"
    for task in high_priority[:5]:
        due = task.due.string if task.due else "No date"
        report += f"- [{priority_emoji(task.priority)}] {task.content} (Due: {due})\n"

    return report

def priority_emoji(priority):
    """Convert priority number to visual indicator"""
    return {4: "!", 3: "*", 2: "-", 1: " "}.get(priority, " ")

if __name__ == "__main__":
    report = generate_daily_report()
    print(report)


*See sub-skills for full details.*
