#!/usr/bin/env python3
"""
Verify Enhanced Specs Installation Across All Repositories

This script verifies that all repositories have:
1. Enhanced specs properly installed
2. No duplicate folders
3. Correct file structure
"""

import os
from pathlib import Path
from datetime import datetime
import json

# Configuration
BASE_PATH = Path("/mnt/github/github")

# List of all repositories to check
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

def verify_repo(repo_name):
    """Verify a repository has enhanced specs properly installed"""
    repo_path = BASE_PATH / repo_name
    
    if not repo_path.exists():
        return {
            "repository": repo_name,
            "status": "❌ Not Found",
            "details": "Repository directory not found"
        }
    
    issues = []
    has_features = {
        "enhanced_specs": False,
        "module_agent": False,
        "agent_os_module": False,
        "standard_structure": False
    }
    
    # Check for .agent-os directory (standard)
    agent_os_dir = repo_path / ".agent-os"
    if agent_os_dir.exists():
        has_features["standard_structure"] = True
    else:
        issues.append("Missing .agent-os directory")
    
    # Check for duplicate folders (but agent_os is valid - it's the Python module)
    duplicate_folders = []
    for folder_name in ["agent-os", "AgentOS", "agentOS"]:  # Removed agent_os as it's valid
        if (repo_path / folder_name).exists():
            duplicate_folders.append(folder_name)
    
    if duplicate_folders:
        issues.append(f"Duplicate folders found: {', '.join(duplicate_folders)}")
    
    # Check for enhanced-create-spec.md
    enhanced_spec_file = agent_os_dir / "instructions" / "enhanced-create-spec.md"
    if enhanced_spec_file.exists():
        has_features["enhanced_specs"] = True
    else:
        issues.append("Missing enhanced-create-spec.md")
    
    # Check for create-module-agent.py
    module_agent_file = repo_path / "create-module-agent.py"
    if module_agent_file.exists():
        has_features["module_agent"] = True
    else:
        issues.append("Missing create-module-agent.py")
    
    # Check for agent_os module directory (should be separate from .agent-os)
    agent_os_module = repo_path / "agent_os"
    if agent_os_module.exists() and agent_os_module.is_dir():
        # Check if it has the commands subdirectory
        if (agent_os_module / "commands").exists():
            has_features["agent_os_module"] = True
        else:
            issues.append("agent_os exists but missing commands subdirectory")
    else:
        # Check if it was mistakenly moved into .agent-os
        if (agent_os_dir / "commands" / "create_module_agent.py").exists():
            issues.append("agent_os module merged into .agent-os (should be separate)")
        else:
            issues.append("Missing agent_os module directory")
    
    # Determine overall status
    if all(has_features.values()) and not issues:
        status = "✅ Complete"
    elif has_features["enhanced_specs"]:
        status = "⚠️ Partial"
    else:
        status = "❌ Missing"
    
    return {
        "repository": repo_name,
        "status": status,
        "has_enhanced_specs": has_features["enhanced_specs"],
        "has_module_agent": has_features["module_agent"],
        "has_agent_os_module": has_features["agent_os_module"],
        "has_standard_structure": has_features["standard_structure"],
        "issues": issues
    }

def main():
    """Main execution"""
    print("=" * 80)
    print("Enhanced Specs Installation Verification")
    print("=" * 80)
    print(f"Checking {len(REPOSITORIES)} repositories...")
    print()
    
    results = []
    complete_count = 0
    partial_count = 0
    missing_count = 0
    
    for repo in REPOSITORIES:
        result = verify_repo(repo)
        results.append(result)
        
        print(f"{result['status']} {repo}")
        
        if "✅" in result['status']:
            complete_count += 1
        elif "⚠️" in result['status']:
            partial_count += 1
            if result['issues']:
                for issue in result['issues']:
                    print(f"    ⚠️ {issue}")
        else:
            missing_count += 1
            if result['issues']:
                for issue in result['issues']:
                    print(f"    ❌ {issue}")
    
    # Summary
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    print(f"✅ Complete: {complete_count}")
    print(f"⚠️ Partial: {partial_count}")
    print(f"❌ Missing: {missing_count}")
    print(f"📊 Total: {len(REPOSITORIES)}")
    
    # Detailed breakdown
    print("\n📋 Feature Breakdown:")
    print("-" * 40)
    
    features_count = {
        "enhanced_specs": 0,
        "module_agent": 0,
        "agent_os_module": 0,
        "standard_structure": 0
    }
    
    for result in results:
        if result['has_enhanced_specs']:
            features_count['enhanced_specs'] += 1
        if result['has_module_agent']:
            features_count['module_agent'] += 1
        if result['has_agent_os_module']:
            features_count['agent_os_module'] += 1
        if result['has_standard_structure']:
            features_count['standard_structure'] += 1
    
    print(f"📁 Standard .agent-os structure: {features_count['standard_structure']}/{len(REPOSITORIES)}")
    print(f"📄 Enhanced specs file: {features_count['enhanced_specs']}/{len(REPOSITORIES)}")
    print(f"🐍 Module agent command: {features_count['module_agent']}/{len(REPOSITORIES)}")
    print(f"📦 Agent OS module: {features_count['agent_os_module']}/{len(REPOSITORIES)}")
    
    # Save detailed report
    report_file = BASE_PATH / f"enhanced_specs_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    # Recommendations
    if partial_count > 0 or missing_count > 0:
        print("\n🔧 Recommendations:")
        print("-" * 40)
        print("1. Run the sync script again to fix missing components")
        print("2. Check for agent_os modules that may have been merged into .agent-os")
        print("3. Ensure create-module-agent.py is in the repository root")
        print("4. Verify that agent_os is a separate directory from .agent-os")

if __name__ == "__main__":
    main()