#!/usr/bin/env python3
"""
Repository Health Analyzer
Analyzes repository health across 5 dimensions with unified scoring
"""

import subprocess
from pathlib import Path
import json
from datetime import datetime, timedelta

def analyze_repository(repo_path):
    """Analyze repository health."""
    health = {
        "repository": repo_path.name,
        "timestamp": datetime.now().isoformat(),
        "scores": {},
        "total_score": 0,
        "grade": "F",
        "issues": [],
        "recommendations": []
    }

    # Git Health (30 points)
    git_score, git_issues = check_git_health(repo_path)
    health["scores"]["git"] = git_score
    health["issues"].extend(git_issues)

    # Code Quality (25 points)
    quality_score, quality_issues = check_code_quality(repo_path)
    health["scores"]["quality"] = quality_score
    health["issues"].extend(quality_issues)

    # Compliance (25 points)
    compliance_score, compliance_issues = check_compliance(repo_path)
    health["scores"]["compliance"] = compliance_score
    health["issues"].extend(compliance_issues)

    # Activity (10 points)
    activity_score, activity_info = check_activity(repo_path)
    health["scores"]["activity"] = activity_score
    if activity_info:
        health["last_commit"] = activity_info

    # Dependencies (10 points)
    deps_score, deps_issues = check_dependencies(repo_path)
    health["scores"]["dependencies"] = deps_score
    health["issues"].extend(deps_issues)

    # Calculate total
    health["total_score"] = sum(health["scores"].values())

    # Assign grade
    health["grade"] = calculate_grade(health["total_score"])

    # Generate recommendations
    health["recommendations"] = generate_recommendations(health)

    return health

def check_git_health(repo_path):
    """Check git health (max 30 points)."""
    score = 30
    issues = []

    # Check for uncommitted changes
    result = subprocess.run(
        ["git", "-C", str(repo_path), "status", "--porcelain"],
        capture_output=True, text=True
    )
    if result.stdout.strip():
        lines = result.stdout.strip().split('\n')
        score -= 10
        issues.append(f"Uncommitted changes: {len(lines)} files modified")

    # Check if up to date with remote
    result = subprocess.run(
        ["git", "-C", str(repo_path), "status"],
        capture_output=True, text=True
    )
    if "behind" in result.stdout:
        score -= 10
        issues.append("Behind remote: needs pull")

    # Check for merge conflicts
    if "unmerged" in result.stdout:
        score -= 10
        issues.append("Merge conflicts detected")

    return max(0, score), issues

def check_code_quality(repo_path):
    """Check code quality (max 25 points)."""
    score = 25
    issues = []

    # Check test coverage
    coverage_file = repo_path / ".coverage"
    if not coverage_file.exists():
        score -= 15
        issues.append("No test coverage file found")

    # Check for pytest.ini or setup.cfg
    if not (repo_path / "pytest.ini").exists() and not (repo_path / "setup.cfg").exists():
        score -= 5
        issues.append("No test configuration found")

    # Check documentation
    docs_dir = repo_path / "docs"
    if not docs_dir.exists():
        score -= 5
        issues.append("No docs/ directory found")
    else:
        md_files = list(docs_dir.glob("**/*.md"))
        if not md_files:
            issues.append("docs/ directory exists but empty")
        else:
            issues.append(f"Documentation present: {len(md_files)} markdown files")

    return max(0, score), issues

def check_compliance(repo_path):
    """Check compliance (max 25 points)."""
    score = 25
    issues = []

    # CLAUDE.md
    if not (repo_path / "CLAUDE.md").exists():
        score -= 10
        issues.append("CLAUDE.md missing")

    # Agent OS structure
    agent_os = repo_path / ".agent-os/product"
    if not agent_os.exists():
        score -= 10
        issues.append(".agent-os/product/ structure missing")
    else:
        # Check for required Agent OS files
        required_files = ["mission.md", "tech-stack.md", "roadmap.md"]
        for file in required_files:
            if not (agent_os / file).exists():
                issues.append(f"Missing Agent OS file: {file}")

    # Git hooks
    post_commit = repo_path / ".git/hooks/post-commit"
    pre_commit = repo_path / ".git/hooks/pre-commit"

    if not post_commit.exists() and not pre_commit.exists():
        score -= 5
        issues.append("No git hooks installed")
    else:
        hooks = []
        if post_commit.exists():
            hooks.append("post-commit")
        if pre_commit.exists():
            hooks.append("pre-commit")
        issues.append(f"Git hooks installed: {', '.join(hooks)}")

    return max(0, score), issues

def check_activity(repo_path):
    """Check activity (max 10 points)."""
    result = subprocess.run(
        ["git", "-C", str(repo_path), "log", "-1", "--format=%ci"],
        capture_output=True, text=True
    )

    if result.returncode == 0 and result.stdout.strip():
        last_commit_str = result.stdout.strip().split()[0]
        try:
            last_commit = datetime.fromisoformat(last_commit_str)
            days_ago = (datetime.now() - last_commit).days

            if days_ago <= 7:
                return 10, f"{days_ago} days ago (very active)"
            elif days_ago <= 30:
                return 7, f"{days_ago} days ago (active)"
            elif days_ago <= 90:
                return 4, f"{days_ago} days ago (moderate)"
            else:
                return 0, f"{days_ago} days ago (stale)"
        except:
            pass

    return 0, "No commit history"

def check_dependencies(repo_path):
    """Check dependencies (max 10 points)."""
    score = 10
    issues = []

    # Check for uv.lock
    if (repo_path / "uv.lock").exists():
        issues.append("UV lock file present")
    elif (repo_path / "requirements.txt").exists():
        issues.append("requirements.txt present")
        score -= 2

    # Check for package-lock.json
    if (repo_path / "package-lock.json").exists():
        issues.append("npm lock file present")
    elif (repo_path / "package.json").exists():
        issues.append("package.json present (no lock)")
        score -= 2

    # Check pyproject.toml
    if (repo_path / "pyproject.toml").exists():
        issues.append("pyproject.toml present")

    # If no dependency files at all
    if not any([
        (repo_path / "uv.lock").exists(),
        (repo_path / "requirements.txt").exists(),
        (repo_path / "package.json").exists(),
        (repo_path / "pyproject.toml").exists()
    ]):
        score -= 5
        issues.append("No dependency management files found")

    return max(0, score), issues

def calculate_grade(score):
    """Calculate letter grade from score."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"

def generate_recommendations(health):
    """Generate recommendations based on health analysis."""
    recommendations = []

    # Git health recommendations
    if health["scores"]["git"] < 30:
        recommendations.append("🔴 Git: Commit uncommitted changes and sync with remote")

    # Code quality recommendations
    if health["scores"]["quality"] < 20:
        recommendations.append("🔴 Quality: Set up test coverage and documentation")
    elif health["scores"]["quality"] < 25:
        recommendations.append("🟡 Quality: Improve test coverage to 80%+")

    # Compliance recommendations
    if health["scores"]["compliance"] < 20:
        recommendations.append("🔴 Compliance: Install CLAUDE.md and Agent OS structure")
    elif health["scores"]["compliance"] < 25:
        recommendations.append("🟡 Compliance: Install git hooks for automation")

    # Activity recommendations
    if health["scores"]["activity"] < 5:
        recommendations.append("🟡 Activity: Repository appears stale, consider archiving or updating")

    # Dependencies recommendations
    if health["scores"]["dependencies"] < 8:
        recommendations.append("🟡 Dependencies: Set up proper dependency management (UV recommended)")

    return recommendations

def print_health_report(health):
    """Print formatted health report to console."""
    print("\n" + "="*70)
    print(f"  Repository Health Report: {health['repository']}")
    print("="*70)
    print(f"\n📊 Overall Score: {health['total_score']}/100 (Grade: {health['grade']})")
    print("\n🔍 Dimension Scores:")
    print(f"  • Git Health:      {health['scores']['git']}/30")
    print(f"  • Code Quality:    {health['scores']['quality']}/25")
    print(f"  • Compliance:      {health['scores']['compliance']}/25")
    print(f"  • Activity:        {health['scores']['activity']}/10")
    print(f"  • Dependencies:    {health['scores']['dependencies']}/10")

    if health.get("last_commit"):
        print(f"\n⏰ Last Commit: {health['last_commit']}")

    if health["issues"]:
        print("\n⚠️  Issues Detected:")
        for issue in health["issues"]:
            print(f"  • {issue}")

    if health["recommendations"]:
        print("\n💡 Recommendations:")
        for rec in health["recommendations"]:
            print(f"  {rec}")

    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    import sys

    # Determine repository to analyze
    if len(sys.argv) > 1:
        repo_path = Path(sys.argv[1])
    else:
        # Default to current directory
        repo_path = Path.cwd()

    if not repo_path.exists():
        print(f"❌ Error: Repository path does not exist: {repo_path}")
        sys.exit(1)

    if not (repo_path / ".git").exists():
        print(f"❌ Error: Not a git repository: {repo_path}")
        sys.exit(1)

    print(f"\n🔬 Analyzing repository: {repo_path.name}")
    print(f"📁 Path: {repo_path.absolute()}")

    # Analyze repository
    health = analyze_repository(repo_path)

    # Print report
    print_health_report(health)

    # Save JSON report
    report_path = Path("reports/health") / f"{repo_path.name}_health.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, 'w') as f:
        json.dump(health, f, indent=2)

    print(f"💾 Detailed report saved to: {report_path}")
    print(f"🕐 Analysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
