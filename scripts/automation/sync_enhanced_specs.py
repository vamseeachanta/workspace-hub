#!/usr/bin/env python3
"""
Sync Enhanced Specs Across All Repositories

This script ensures:
1. All repos have the enhanced-create-spec.md file
2. All repos have the create-module-agent.py and supporting files
3. No duplicate folders (agent-os vs .agent-os)
4. Consistent structure across all repositories
"""

import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
import json

# Configuration
BASE_PATH = Path("/mnt/github/github")
SOURCE_REPO = "aceengineer-admin"  # Repository with the correct enhanced specs

# List of all repositories to sync
REPOSITORIES = [
    "aceengineer-admin",
    "aceengineercode", 
    "aceengineer-website",
    "achantas-data",
    "achantas-media",
    "acma-projects",
    "ai-native-traditional-eng",
    "assethold",
    "assetutilities",
    "digitalmodel",
    "energy",
    "frontierdeepwater",
    "hobbies",
    "investments",
    "OGManufacturing",
    "rock-oil-field",
    "sabithaandkrishnaestates",
    "saipem",
    "sd-work",
    "seanation",
    "teamresumes",
    "worldenergydata"
]

# Files to sync
ENHANCED_SPEC_FILES = {
    ".agent-os/instructions/enhanced-create-spec.md": "Enhanced spec creation rules",
    "create-module-agent.py": "Module agent command",
    "agent_os": "Agent OS module directory"
}

def check_duplicate_folders(repo_path):
    """Check for duplicate agent-os folders (with and without dot)"""
    issues = []
    
    # Check for both .agent-os and agent-os
    dot_folder = repo_path / ".agent-os"
    no_dot_folder = repo_path / "agent-os"
    
    if dot_folder.exists() and no_dot_folder.exists():
        issues.append(f"Both .agent-os and agent-os folders exist")
        
    # Check for other variations
    for item in repo_path.iterdir():
        if item.is_dir():
            lower_name = item.name.lower()
            if "agent" in lower_name and "os" in lower_name:
                if item.name not in [".agent-os"]:
                    issues.append(f"Non-standard folder found: {item.name}")
    
    return issues

def fix_duplicate_folders(repo_path):
    """Fix duplicate folders by consolidating into .agent-os"""
    fixed = []
    
    # Standard folder should be .agent-os
    standard_folder = repo_path / ".agent-os"
    
    # List of possible duplicate folders
    possible_duplicates = [
        "agent-os",
        "agent_os",
        "AgentOS",
        "agentOS"
    ]
    
    for dup_name in possible_duplicates:
        dup_folder = repo_path / dup_name
        if dup_folder.exists():
            print(f"  Found duplicate folder: {dup_name}")
            
            if not standard_folder.exists():
                # Rename to standard
                print(f"  Renaming {dup_name} to .agent-os")
                dup_folder.rename(standard_folder)
                fixed.append(f"Renamed {dup_name} to .agent-os")
            else:
                # Merge contents
                print(f"  Merging {dup_name} into .agent-os")
                merge_folders(dup_folder, standard_folder)
                shutil.rmtree(dup_folder)
                fixed.append(f"Merged {dup_name} into .agent-os")
    
    return fixed

def merge_folders(source, destination):
    """Merge source folder into destination, preserving newer files"""
    for item in source.rglob("*"):
        if item.is_file():
            relative_path = item.relative_to(source)
            dest_path = destination / relative_path
            
            # Create parent directories if needed
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file if it doesn't exist or is newer
            if not dest_path.exists():
                shutil.copy2(item, dest_path)
            else:
                # Keep the newer file
                if item.stat().st_mtime > dest_path.stat().st_mtime:
                    shutil.copy2(item, dest_path)

def sync_enhanced_specs(repo_name):
    """Sync enhanced specs to a repository"""
    repo_path = BASE_PATH / repo_name
    source_path = BASE_PATH / SOURCE_REPO
    
    if not repo_path.exists():
        return {"status": "skipped", "reason": "Repository not found"}
    
    results = {
        "repository": repo_name,
        "status": "success",
        "actions": [],
        "issues_fixed": []
    }
    
    # First, fix any duplicate folders
    folder_issues = check_duplicate_folders(repo_path)
    if folder_issues:
        results["actions"].append("Fixed duplicate folders")
        fixes = fix_duplicate_folders(repo_path)
        results["issues_fixed"].extend(fixes)
    
    # Ensure .agent-os directory exists
    agent_os_dir = repo_path / ".agent-os"
    if not agent_os_dir.exists():
        agent_os_dir.mkdir(parents=True)
        results["actions"].append("Created .agent-os directory")
    
    # Ensure instructions directory exists
    instructions_dir = agent_os_dir / "instructions"
    if not instructions_dir.exists():
        instructions_dir.mkdir(parents=True)
        results["actions"].append("Created instructions directory")
    
    # Copy enhanced-create-spec.md
    source_enhanced = source_path / ".agent-os/instructions/enhanced-create-spec.md"
    dest_enhanced = instructions_dir / "enhanced-create-spec.md"
    
    if source_enhanced.exists():
        if not dest_enhanced.exists():
            shutil.copy2(source_enhanced, dest_enhanced)
            results["actions"].append("Added enhanced-create-spec.md")
        else:
            # Check if update needed
            if source_enhanced.stat().st_mtime > dest_enhanced.stat().st_mtime:
                shutil.copy2(source_enhanced, dest_enhanced)
                results["actions"].append("Updated enhanced-create-spec.md")
    
    # Copy create-module-agent.py
    source_module_agent = source_path / "create-module-agent.py"
    dest_module_agent = repo_path / "create-module-agent.py"
    
    if source_module_agent.exists():
        if not dest_module_agent.exists():
            shutil.copy2(source_module_agent, dest_module_agent)
            results["actions"].append("Added create-module-agent.py")
        else:
            # Check if update needed
            if source_module_agent.stat().st_mtime > dest_module_agent.stat().st_mtime:
                shutil.copy2(source_module_agent, dest_module_agent)
                results["actions"].append("Updated create-module-agent.py")
    
    # Copy agent_os directory
    source_agent_os = source_path / "agent_os"
    dest_agent_os = repo_path / "agent_os"
    
    if source_agent_os.exists():
        if not dest_agent_os.exists():
            shutil.copytree(source_agent_os, dest_agent_os)
            results["actions"].append("Added agent_os module directory")
        else:
            # Update files in agent_os
            merge_folders(source_agent_os, dest_agent_os)
            results["actions"].append("Updated agent_os module directory")
    
    # Check final status
    has_enhanced = (instructions_dir / "enhanced-create-spec.md").exists()
    has_module_agent = (repo_path / "create-module-agent.py").exists()
    has_agent_os = (repo_path / "agent_os").exists()
    
    if has_enhanced and has_module_agent and has_agent_os:
        results["enhanced_specs"] = "✅ Complete"
    elif has_enhanced:
        results["enhanced_specs"] = "⚠️ Partial (missing module agent)"
    else:
        results["enhanced_specs"] = "❌ Missing"
        results["status"] = "incomplete"
    
    return results

def main():
    """Main execution"""
    print("=" * 80)
    print("Enhanced Specs Synchronization")
    print("=" * 80)
    print(f"Syncing from: {SOURCE_REPO}")
    print(f"Total repositories: {len(REPOSITORIES)}")
    print()
    
    # Track results
    all_results = []
    successful = 0
    updated = 0
    issues_fixed = 0
    
    for repo in REPOSITORIES:
        print(f"\n📦 Processing: {repo}")
        print("-" * 40)
        
        result = sync_enhanced_specs(repo)
        all_results.append(result)
        
        if result.get("status") == "success":
            successful += 1
            
            if result.get("actions"):
                updated += 1
                print(f"  ✅ Actions taken:")
                for action in result["actions"]:
                    print(f"     - {action}")
            else:
                print(f"  ✅ Already up to date")
            
            if result.get("issues_fixed"):
                issues_fixed += len(result["issues_fixed"])
                print(f"  🔧 Issues fixed:")
                for fix in result["issues_fixed"]:
                    print(f"     - {fix}")
        else:
            print(f"  ⚠️ Status: {result.get('status')}")
            if result.get("reason"):
                print(f"     Reason: {result['reason']}")
    
    # Summary report
    print("\n" + "=" * 80)
    print("SYNCHRONIZATION SUMMARY")
    print("=" * 80)
    print(f"✅ Successful: {successful}/{len(REPOSITORIES)}")
    print(f"📝 Updated: {updated} repositories")
    print(f"🔧 Issues fixed: {issues_fixed}")
    
    # Detailed status
    print("\n📊 Repository Status:")
    print("-" * 40)
    for result in all_results:
        status_icon = "✅" if result.get("enhanced_specs", "").startswith("✅") else "⚠️"
        print(f"{status_icon} {result['repository']}: {result.get('enhanced_specs', 'Unknown')}")
    
    # Save report
    report_file = BASE_PATH / f"enhanced_specs_sync_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print(f"\n📄 Report saved to: {report_file}")
    
    # Git status check
    print("\n🔍 Checking for uncommitted changes...")
    for repo in REPOSITORIES:
        repo_path = BASE_PATH / repo
        if repo_path.exists():
            try:
                result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True
                )
                if result.stdout.strip():
                    print(f"  ⚠️ {repo}: Has uncommitted changes")
            except:
                pass
    
    print("\n✨ Synchronization complete!")
    print("\nNext steps:")
    print("1. Review the changes in each repository")
    print("2. Commit the changes with: git commit -m 'feat: Add enhanced spec creation'")
    print("3. Push to remote repositories")

if __name__ == "__main__":
    main()