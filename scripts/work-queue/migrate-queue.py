#!/usr/bin/env python3
import os
import re

WORKSPACE_ROOT = os.getenv("WORKSPACE_ROOT", os.popen("git rev-parse --show-toplevel").read().strip())
QUEUE_DIR = os.path.join(WORKSPACE_ROOT, ".claude/work-queue")

ALLOWED_STATUSES = ["pending", "working", "done", "archived", "blocked", "failed"]
LEGACY_STATUSES = ["complete", "completed", "closed", "merged"]

def get_frontmatter(content):
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if match:
        return match.group(1), match.end()
    return None, 0

def update_status(file_path, new_status):
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        fm_str, end_pos = get_frontmatter(content)
        
        if fm_str is None:
            # Add basic frontmatter
            filename = os.path.basename(file_path)
            wrk_id = filename.replace(".md", "")
            new_fm = f"---\nid: {wrk_id}\nstatus: {new_status}\n---\n\n"
            new_content = new_fm + content
        else:
            # Replace or add status
            if re.search(r"^status:", fm_str, re.MULTILINE):
                new_fm_str = re.sub(r"^status:.*$", f"status: {new_status}", fm_str, flags=re.MULTILINE)
            else:
                new_fm_str = fm_str + f"\nstatus: {new_status}"
            new_content = "---\n" + new_fm_str + "\n---\n" + content[end_pos:]
        
        with open(file_path, 'w') as f:
            f.write(new_content)
        return True
    except Exception as e:
        print(f"  ✖ Error updating {file_path}: {e}")
        return False

def migrate():
    print("Migrating work-queue states...")
    
    # Folders to scan
    folders = {
        "pending": "pending",
        "working": "working",
        "blocked": "blocked",
        "done": "done",
        "archive": "archived"
    }

    for folder, expected_status in folders.items():
        dir_path = os.path.join(QUEUE_DIR, folder)
        if not os.path.exists(dir_path):
            continue
        
        for root, _, files in os.walk(dir_path):
            for filename in files:
                if not filename.endswith(".md") or not filename.startswith("WRK-"):
                    continue
                
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                except Exception as e:
                    print(f"  ✖ Error reading {file_path}: {e}")
                    continue
                
                fm_str, _ = get_frontmatter(content)
                
                if not fm_str:
                    print(f"  ✓ Adding missing frontmatter to {filename}, status={expected_status}")
                    update_status(file_path, expected_status)
                    continue
                
                status_match = re.search(r"^status:\s*(.*)$", fm_str, re.MULTILINE)
                current_status = ""
                if status_match:
                    current_status = status_match.group(1).strip().strip("'").strip('"')
                
                # Check if it needs migration
                needs_fix = False
                
                # 1. Folder/Status mismatch
                if current_status != expected_status:
                    needs_fix = True
                
                # 2. Legacy status
                if current_status in LEGACY_STATUSES:
                    needs_fix = True
                
                # 3. Non-standard status
                if current_status not in ALLOWED_STATUSES and current_status not in LEGACY_STATUSES:
                    needs_fix = True

                if needs_fix:
                    print(f"  ✓ Updating {filename}: '{current_status}' -> '{expected_status}'")
                    update_status(file_path, expected_status)

if __name__ == "__main__":
    migrate()
