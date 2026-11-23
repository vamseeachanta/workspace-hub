"""Pydantic schema for .claude/state/reflect-state.yaml"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ChecklistStatus(str, Enum):
    """Status values used in the reflect checklist."""

    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    NONE = "none"


class PhasesCompleted(BaseModel):
    """Tracks which reflection phases have completed."""

    model_config = {"extra": "allow"}

    reflect: bool = False
    abstract: bool = False
    generalize: bool = False
    store: bool = False


class ReflectMetrics(BaseModel):
    """Metrics gathered during the reflect phase."""

    model_config = {"extra": "allow"}

    repos_analyzed: int = Field(default=0, ge=0)
    commits_found: int = Field(default=0, ge=0)
    patterns_extracted: int = Field(default=0, ge=0)
    script_ideas_found: int = Field(default=0, ge=0)
    sessions_analyzed: int = Field(default=0, ge=0)
    conversations_analyzed: int = Field(default=0, ge=0)
    corrections_detected: int = Field(default=0, ge=0)
    correction_file_types: int = Field(default=0, ge=0)
    correction_chains: int = Field(default=0, ge=0)
    correction_top_extension: str = ""
    correction_long_chains: int = Field(default=0, ge=0)


class ReflectChecklist(BaseModel):
    """Checklist items from the reflect analysis (~50 fields)."""

    model_config = {"extra": "allow"}

    # Cross review
    cross_review: ChecklistStatus = ChecklistStatus.NONE
    pending_reviews: int = Field(default=0, ge=0)
    gemini_pending: int = Field(default=0, ge=0)
    codex_pending: int = Field(default=0, ge=0)
    claude_pending: int = Field(default=0, ge=0)

    # Skills
    skills_development: ChecklistStatus = ChecklistStatus.NONE
    skills_created: int = Field(default=0, ge=0)
    skills_enhanced: int = Field(default=0, ge=0)

    # File structure
    file_structure: ChecklistStatus = ChecklistStatus.NONE
    orphan_docs: int = Field(default=0, ge=0)
    orphan_scripts: int = Field(default=0, ge=0)

    # Context management
    context_management: ChecklistStatus = ChecklistStatus.NONE
    avg_session_msgs: int = Field(default=0, ge=0)
    correction_rate: int = Field(default=0, ge=0)

    # Best practices
    best_practices: ChecklistStatus = ChecklistStatus.NONE
    repos_with_tests: int = Field(default=0, ge=0)
    uncommitted_changes: int = Field(default=0, ge=0)

    # Submodule sync
    submodule_sync: ChecklistStatus = ChecklistStatus.NONE
    submodules_dirty: int = Field(default=0, ge=0)
    submodules_unpushed: int = Field(default=0, ge=0)
    submodules_total: int = Field(default=0, ge=0)

    # CLAUDE.md health
    claude_md_health: ChecklistStatus = ChecklistStatus.NONE
    claude_md_oversized: int = Field(default=0, ge=0)
    claude_md_total: int = Field(default=0, ge=0)

    # Hook installation
    hook_installation: ChecklistStatus = ChecklistStatus.NONE
    hooks_installed: int = Field(default=0, ge=0)
    hooks_expected: int = Field(default=0, ge=0)
    hooks_coverage: float = Field(default=0, ge=0)

    # Stale branches
    stale_branches: ChecklistStatus = ChecklistStatus.NONE
    stale_branch_count: int = Field(default=0, ge=0)

    # GitHub Actions
    github_actions: ChecklistStatus = ChecklistStatus.NONE
    actions_failing: int = Field(default=0, ge=0)
    actions_total: int = Field(default=0, ge=0)

    # Folder structure
    folder_structure_detailed: ChecklistStatus = ChecklistStatus.NONE
    structure_issues: int = Field(default=0, ge=0)
    root_files: int = Field(default=0, ge=0)

    # Test coverage
    test_coverage: ChecklistStatus = ChecklistStatus.NONE
    avg_coverage: float = Field(default=0, ge=0)
    coverage_repos: int = Field(default=0, ge=0)
    low_coverage_repos: int = Field(default=0, ge=0)

    # Test pass/fail
    test_pass_fail: ChecklistStatus = ChecklistStatus.NONE
    test_pass_count: int = Field(default=0, ge=0)
    test_fail_count: int = Field(default=0, ge=0)
    tested_repos: int = Field(default=0, ge=0)

    # Refactor
    refactor: ChecklistStatus = ChecklistStatus.NONE
    large_files: int = Field(default=0, ge=0)
    todo_count: int = Field(default=0, ge=0)

    # ACE Engineer cron
    aceengineer_cron: ChecklistStatus = ChecklistStatus.NONE
    aceengineer_stats_date: Optional[date] = None
    aceengineer_report_date: Optional[date] = None

    # Session RAG
    session_rag: ChecklistStatus = ChecklistStatus.NONE
    session_rag_date: Optional[date] = None
    session_rag_sessions: int = Field(default=0, ge=0)
    session_rag_events: int = Field(default=0, ge=0)

    # CC insights
    cc_insights: ChecklistStatus = ChecklistStatus.NONE
    cc_version: str = ""
    cc_last_reviewed: str = ""
    cc_general_count: int = Field(default=0, ge=0)
    cc_specific_count: int = Field(default=0, ge=0)

    # Work queue
    work_queue: ChecklistStatus = ChecklistStatus.NONE
    wq_pending: int = Field(default=0, ge=0)
    wq_working: int = Field(default=0, ge=0)
    wq_blocked: int = Field(default=0, ge=0)
    wq_stale: int = Field(default=0, ge=0)

    # Skill evaluation
    skill_eval: ChecklistStatus = ChecklistStatus.NONE
    skill_eval_total: int = Field(default=0, ge=0)
    skill_eval_passed: int = Field(default=0, ge=0)
    skill_eval_critical: int = Field(default=0, ge=0)
    skill_eval_warnings: int = Field(default=0, ge=0)

    # Capability map
    capability_map: ChecklistStatus = ChecklistStatus.NONE
    capability_repos: int = Field(default=0, ge=0)
    capability_domains: int = Field(default=0, ge=0)
    capability_gaps: int = Field(default=0, ge=0)
    capability_date: Optional[date] = None

    # Knowledge base
    knowledge_base: ChecklistStatus = ChecklistStatus.NONE
    kb_total: int = Field(default=0, ge=0)
    kb_active: int = Field(default=0, ge=0)
    kb_stale: int = Field(default=0, ge=0)
    kb_avg_confidence: float = Field(default=0, ge=0, le=1.0)


class ActionsTaken(BaseModel):
    """Actions taken during the reflect run."""

    model_config = {"extra": "allow"}

    skills_created: int = Field(default=0, ge=0)
    skills_enhanced: int = Field(default=0, ge=0)
    learnings_stored: int = Field(default=0, ge=0)
    knowledge_captured: int = Field(default=0, ge=0)
    stale_reviews_approved: int = Field(default=0, ge=0)


class ReflectFiles(BaseModel):
    """File paths produced by the reflect run."""

    model_config = {"extra": "allow"}

    analysis: Optional[str] = None
    patterns: Optional[str] = None
    conversations: Optional[str] = None
    trends: Optional[str] = None
    report: Optional[str] = None
    skill_eval_report: Optional[str] = None

    @field_validator("*", mode="before")
    @classmethod
    def coerce_none_string(cls, v: object) -> object:
        """Convert the string 'none' to actual None."""
        if isinstance(v, str) and v.lower() == "none":
            return None
        return v


class ReflectState(BaseModel):
    """Top-level schema for reflect-state.yaml."""

    model_config = {"extra": "allow"}

    version: str
    last_run: datetime
    analysis_window_days: int = Field(ge=1)
    dry_run: bool = False
    phases_completed: PhasesCompleted = PhasesCompleted()
    metrics: ReflectMetrics = ReflectMetrics()
    checklist: ReflectChecklist = ReflectChecklist()
    actions_taken: ActionsTaken = ActionsTaken()
    files: ReflectFiles = ReflectFiles()
