#!/usr/bin/env python3
import os
import re
from datetime import datetime, date

WORKSPACE_ROOT = os.getenv("WORKSPACE_ROOT", os.popen("git rev-parse --show-toplevel").read().strip())
QUEUE_DIR = os.path.join(WORKSPACE_ROOT, ".claude/work-queue")

def get_frontmatter(content):
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if match:
        return match.group(1), match.end()
    return None, 0

def parse_date(value):
    if not value or not isinstance(value, str):
        return None
    cleaned = re.sub(r"\.\d+", "", value)
    cleaned = re.sub(r"[+-]\d{2}:\d{2}$", "", cleaned)
    cleaned = cleaned.rstrip("Z")
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue
    return None

def report():
    print("# WRK-624 Manual Remediation Report")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d')}")
    print("\n## Stale Working Items (>7 days)")
    
    working_dir = os.path.join(QUEUE_DIR, "working")
    today = date.today()
    stale_found = False
    
    if os.path.exists(working_dir):
        for filename in sorted(os.listdir(working_dir)):
            if not filename.endswith(".md"): continue
            file_path = os.path.join(working_dir, filename)
            
            # Use file mtime as fallback if created_at is missing
            mtime = date.fromtimestamp(os.path.getmtime(file_path))
            
            with open(file_path, 'r') as f:
                content = f.read()
            fm_str, _ = get_frontmatter(content)
            if not fm_str: continue
            
            created_at_match = re.search(r"^created_at:\s*(.*)$", fm_str, re.MULTILINE)
            created_date = parse_date(created_at_match.group(1).strip()) if created_at_match else mtime
            
            if created_date and (today - created_date).days > 7:
                print(f"- {filename} (Age: {(today - created_date).days} days)")
                stale_found = True
    
    if not stale_found:
        print("None found.")

    print("\n## Stale Blocked Items (>14 days)")
    blocked_dir = os.path.join(QUEUE_DIR, "blocked")
    stale_blocked_found = False
    
    if os.path.exists(blocked_dir):
        for filename in sorted(os.listdir(blocked_dir)):
            if not filename.endswith(".md"): continue
            file_path = os.path.join(blocked_dir, filename)
            
            mtime = date.fromtimestamp(os.path.getmtime(file_path))
            
            with open(file_path, 'r') as f:
                content = f.read()
            fm_str, _ = get_frontmatter(content)
            if not fm_str: continue
            
            created_at_match = re.search(r"^created_at:\s*(.*)$", fm_str, re.MULTILINE)
            created_date = parse_date(created_at_match.group(1).strip()) if created_at_match else mtime
            
            if created_date and (today - created_date).days > 14:
                print(f"- {filename} (Age: {(today - created_date).days} days)")
                stale_blocked_found = True
    
    if not stale_blocked_found:
        print("None found.")

    print("\n## Ambiguous Items (Missing required metadata)")
    # Just a sample of required metadata for Route C/Canonical transition
    required_fields = ["priority", "complexity", "route", "provider"]
    ambiguous_found = False
    
    for folder in ["pending", "working", "blocked"]:
        dir_path = os.path.join(QUEUE_DIR, folder)
        if not os.path.exists(dir_path): continue
        for filename in sorted(os.listdir(dir_path)):
            if not filename.endswith(".md") or not filename.startswith("WRK-"): continue
            file_path = os.path.join(dir_path, filename)
            with open(file_path, 'r') as f:
                content = f.read()
            fm_str, _ = get_frontmatter(content)
            if not fm_str:
                print(f"- {filename} (Missing frontmatter)")
                ambiguous_found = True
                continue
            
            missing = []
            for field in required_fields:
                status_field = re.search(fr"^{field}:", fm_str, re.MULTILINE)
                if not status_field:
                    missing.append(field)
            
            if missing:
                print(f"- {filename} (Missing: {', '.join(missing)})")
                ambiguous_found = True
    
    if not ambiguous_found:
        print("None found.")

if __name__ == "__main__":
    report()
