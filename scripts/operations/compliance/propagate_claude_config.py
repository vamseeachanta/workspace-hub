#!/usr/bin/env python3
"""
ABOUTME: Propagates CLAUDE.md configuration to all repositories
ABOUTME: Updates interactive mode and file organization standards
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import List, Tuple

# Color codes for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'

def read_source_claude_md(workspace_dir: Path) -> str:
    """Read the source CLAUDE.md from workspace-hub root"""
    source_file = workspace_dir / "CLAUDE.md"
    if not source_file.exists():
        print(f"{Colors.RED}✗{Colors.NC} Source CLAUDE.md not found in workspace-hub")
        sys.exit(1)

    return source_file.read_text(encoding='utf-8')

def extract_interactive_section(content: str) -> str:
    """Extract the Interactive Engagement section from CLAUDE.md"""
    pattern = r'(## Interactive Engagement \(MANDATORY\).*?)(?=\n## [^#]|\Z)'
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        print(f"{Colors.RED}✗{Colors.NC} Interactive Engagement section not found in source")
        sys.exit(1)

    return match.group(1).rstrip()

def extract_file_org_section(content: str) -> str:
    """Extract the AI Folder Organization section from CLAUDE.md"""
    # Look for the section after "File Organization Rules"
    pattern = r'(### 🤖 AI Folder Organization Responsibility.*?)(?=\n### [^#]|\n## [^#]|\Z)'
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        return None

    return match.group(1).rstrip()

def update_repository_claude_md(
    repo_path: Path,
    interactive_section: str,
    file_org_section: str
) -> Tuple[bool, str]:
    """
    Update CLAUDE.md in a repository
    Returns: (success, message)
    """
    repo_name = repo_path.name
    claude_md = repo_path / "CLAUDE.md"

    if not claude_md.exists():
        return True, f"{Colors.YELLOW}⚠{Colors.NC} No CLAUDE.md in {repo_name} - skipping"

    # Create backup
    backup_file = claude_md.with_suffix(f'.md.backup-{datetime.now().strftime("%Y%m%d-%H%M%S")}')
    content = claude_md.read_text(encoding='utf-8')
    backup_file.write_text(content, encoding='utf-8')

    # Track changes
    changes = []

    # Replace or add Interactive Engagement section
    interactive_pattern = r'## Interactive Engagement \(MANDATORY\).*?(?=\n## [^#]|\Z)'
    proactive_pattern = r'## Proactiveness.*?(?=\n## [^#]|\Z)'

    if re.search(interactive_pattern, content, re.DOTALL):
        # Update existing Interactive Engagement section
        content = re.sub(interactive_pattern, interactive_section, content, flags=re.DOTALL)
        changes.append("Updated Interactive Engagement section")
    elif re.search(proactive_pattern, content, re.DOTALL):
        # Replace Proactiveness with Interactive Engagement
        content = re.sub(proactive_pattern, interactive_section, content, flags=re.DOTALL)
        changes.append("Replaced Proactiveness with Interactive Engagement")
    elif "## Our relationship" in content:
        # Add after Our relationship section
        relationship_pattern = r'(## Our relationship.*?(?=\n## [^#]))'
        content = re.sub(
            relationship_pattern,
            r'\1\n\n' + interactive_section + '\n',
            content,
            flags=re.DOTALL
        )
        changes.append("Added Interactive Engagement after Our relationship")
    else:
        # Add at beginning after first header
        lines = content.split('\n')
        insert_pos = 1 if lines[0].startswith('#') else 0
        lines.insert(insert_pos, '\n' + interactive_section + '\n')
        content = '\n'.join(lines)
        changes.append("Added Interactive Engagement at beginning")

    # Add or update File Organization section if present in source
    if file_org_section:
        file_org_pattern = r'### 🤖 AI Folder Organization Responsibility.*?(?=\n### [^#]|\n## [^#]|\Z)'

        if re.search(file_org_pattern, content, re.DOTALL):
            # Update existing section
            content = re.sub(file_org_pattern, file_org_section, content, flags=re.DOTALL)
            changes.append("Updated AI Folder Organization section")
        elif "### 📁 File Organization Rules" in content:
            # Add after File Organization Rules
            file_rules_pattern = r'(### 📁 File Organization Rules.*?(?=\n### [^#]))'
            content = re.sub(
                file_rules_pattern,
                r'\1\n\n' + file_org_section + '\n',
                content,
                flags=re.DOTALL
            )
            changes.append("Added AI Folder Organization section")

    # Write updated content
    claude_md.write_text(content, encoding='utf-8')

    status = f"{Colors.GREEN}✓{Colors.NC} Updated {repo_name}/CLAUDE.md"
    if changes:
        status += f"\n   Changes: {', '.join(changes)}"

    return True, status

def main():
    """Main execution"""
    script_dir = Path(__file__).parent
    workspace_dir = script_dir.parent

    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}   CLAUDE.md Configuration Propagation Tool{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    print()
    print("This will update CLAUDE.md in all repositories with:")
    print("- Interactive Engagement (mandatory question-asking)")
    print("- AI Folder Organization Responsibility")
    print()

    # Read source configuration
    print(f"{Colors.BLUE}Reading source configuration...{Colors.NC}")
    source_content = read_source_claude_md(workspace_dir)
    interactive_section = extract_interactive_section(source_content)
    file_org_section = extract_file_org_section(source_content)

    print(f"{Colors.GREEN}✓{Colors.NC} Extracted Interactive Engagement section")
    if file_org_section:
        print(f"{Colors.GREEN}✓{Colors.NC} Extracted AI Folder Organization section")
    else:
        print(f"{Colors.YELLOW}⚠{Colors.NC} No AI Folder Organization section found")
    print()

    # Find all repositories
    repos = [
        d for d in workspace_dir.iterdir()
        if d.is_dir() and not d.name.startswith('.')
    ]
    repos.sort()

    print(f"{Colors.BLUE}Found {len(repos)} directories{Colors.NC}")
    print()

    # Update each repository
    updated = 0
    skipped = 0
    failed = 0

    for repo in repos:
        try:
            success, message = update_repository_claude_md(
                repo,
                interactive_section,
                file_org_section
            )
            print(message)

            if "skipping" in message:
                skipped += 1
            elif success:
                updated += 1
            else:
                failed += 1
        except Exception as e:
            print(f"{Colors.RED}✗{Colors.NC} Error updating {repo.name}: {e}")
            failed += 1

    # Summary
    print()
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.GREEN}✓ Updated:{Colors.NC} {updated} repositories")
    print(f"{Colors.YELLOW}⚠ Skipped:{Colors.NC} {skipped} repositories (no CLAUDE.md)")
    if failed > 0:
        print(f"{Colors.RED}✗ Failed:{Colors.NC} {failed} repositories")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")

    # Verify workspace-hub
    workspace_claude = workspace_dir / "CLAUDE.md"
    if workspace_claude.exists():
        content = workspace_claude.read_text()
        if "## Interactive Engagement (MANDATORY)" in content:
            print(f"{Colors.GREEN}✓{Colors.NC} Verified: workspace-hub CLAUDE.md has Interactive Engagement")
        else:
            print(f"{Colors.RED}✗{Colors.NC} Warning: workspace-hub CLAUDE.md missing Interactive Engagement")

    print()
    print("Backup files created with .backup-YYYYMMDD-HHMMSS extension")
    print("Review changes before committing to git")

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
