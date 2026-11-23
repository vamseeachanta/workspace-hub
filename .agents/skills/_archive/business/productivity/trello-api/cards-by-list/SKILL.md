---
name: trello-api-cards-by-list
description: 'Sub-skill of trello-api: Cards by List.'
version: 1.0.0
category: business
type: reference
scripts_exempt: true
---

# Cards by List

## Cards by List


"""

    for list_name, list_data in analytics["lists"].items():
        report += f"### {list_name} ({list_data['card_count']} cards)\n\n"

        if list_data["cards"]:
            for card in list_data["cards"][:5]:  # Show top 5
                overdue_marker = " [OVERDUE]" if card.get("overdue") else ""
                report += f"- {card['name']}{overdue_marker}\n"
            if len(list_data["cards"]) > 5:
                report += f"- ... and {len(list_data['cards']) - 5} more\n"
        report += "\n"

    report += "## Label Usage\n\n"
    report += "| Label | Count |\n"
    report += "|-------|-------|\n"

    for label, count in sorted(
        analytics["labels"].items(),
        key=lambda x: x[1],
        reverse=True
    ):
        report += f"| {label} | {count} |\n"

    return report

*See sub-skills for full details.*
