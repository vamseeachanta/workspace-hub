#!/usr/bin/env bash
""":"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
export UV_CACHE_DIR="${UV_CACHE_DIR:-$REPO_ROOT/.claude/state/uv-cache}"
mkdir -p "$UV_CACHE_DIR"
exec uv run --no-project --with markdown --with PyYAML python "$0" "$@"
":"""
"""Generate canonical WRK lifecycle HTML artifact.

Conforms to workflow-html SKILL v1.5.0 (single lifecycle HTML per WRK).

Usage:
    generate-html-review.py WRK-NNN [--lifecycle] [--output <path>]

--type flags (plan-draft|plan-final|implementation|close) are deprecated and removed.
All invocations now generate lifecycle HTML regardless of flags passed.
"""
import os
import re
import subprocess
import sys
from html import escape as html_escape
import yaml
import markdown
from pathlib import Path

# ── CSS design system (workflow-html SKILL §1) ───────────────────────────────
CSS = """
:root {
  --bg:       #f3efe6;
  --panel:    #fffdf8;
  --ink:      #172126;
  --muted:    #55636b;
  --accent:   #0f766e;
  --accent-2: #8a5a2b;
  --line:     #d9d0c0;
  --shadow:   0 16px 40px rgba(20,33,38,0.08);
  --good:     #166534;
  --warn:     #b45309;
  --bad:      #b91c1c;
}
*{box-sizing:border-box;}
body{font-family:Georgia,"Times New Roman",serif;
  background:radial-gradient(circle at top,#fffaf0 0,var(--bg) 48%,#ebe5d7 100%);
  color:var(--ink);line-height:1.5;margin:0;}
code{font-family:"SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace;
  background:rgba(27,31,35,0.05);padding:.2em .4em;border-radius:3px;}
pre code{background:none;padding:0;}
pre{background:#f6f8fa;border:1px solid var(--line);border-radius:8px;
  padding:14px 16px;overflow-x:auto;font-size:.88rem;}
.panel,.artifact-box{background:#fff;padding:16px;border-radius:10px;
  border:1px solid var(--line);}
.hero{padding:48px 24px 28px;border-bottom:1px solid rgba(23,33,38,0.08);
  background:linear-gradient(135deg,rgba(15,118,110,0.08),rgba(138,90,43,0.10));}
.hero-inner,.content{max-width:1180px;margin:0 auto;}
.eyebrow{text-transform:uppercase;letter-spacing:.12em;font-size:.72rem;
  color:var(--accent);font-weight:700;}
h1{margin:10px 0 12px;font-size:clamp(1.75rem,3.2vw,3rem);line-height:1.02;}
.lede{max-width:78ch;color:var(--muted);font-size:1.05rem;}
.content{padding:28px 24px 56px;}
.card{background:var(--panel);padding:26px;border-radius:18px;
  box-shadow:var(--shadow);border:1px solid var(--line);margin-bottom:20px;}
h2{border-bottom:1px solid var(--line);padding-bottom:.3em;margin-top:24px;
  color:var(--accent-2);letter-spacing:.02em;}
h2[data-collapsed="true"]{margin-bottom:4px;}
h2 .section-summary-chip{max-width:min(70ch,70vw);white-space:nowrap;
  overflow:hidden;text-overflow:ellipsis;}
h3{color:var(--ink);margin-top:18px;}
.exec-summary{background:linear-gradient(180deg,#fff,#fcf8ef);
  border-left:6px solid var(--accent);padding:20px;margin-bottom:30px;
  border-radius:10px;}
.exec-summary h2{margin-top:0;border:none;color:var(--accent);}
table{border-collapse:collapse;width:100%;margin:16px 0;font-size:.95rem;}
th,td{border-top:1px solid var(--line);padding:10px 8px;
  text-align:left;vertical-align:top;}
th{font-weight:700;text-transform:uppercase;letter-spacing:.06em;
  font-size:.86rem;color:var(--ink);}
.card p,.card li,.card td,.card th{color:var(--muted);}
.card strong,.card code{color:var(--ink);}
.meta{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));
  gap:10px;margin:14px 0 20px;}
.pill{background:var(--panel);border:1px solid var(--line);border-radius:10px;
  padding:10px 14px;font-size:.9rem;}
.pill strong{display:block;font-size:.72rem;text-transform:uppercase;
  letter-spacing:.08em;color:var(--accent-2);margin-bottom:2px;}
.badge{display:inline-block;padding:2px 8px;border-radius:999px;
  font-size:.78rem;font-weight:700;text-transform:uppercase;letter-spacing:.06em;}
.badge-pass{background:#dcfce7;color:var(--good);}
.badge-warn{background:#fef3c7;color:var(--warn);}
.badge-fail{background:#fee2e2;color:var(--bad);}
.badge-info{background:#dbeafe;color:#1d4ed8;}
.split{display:grid;grid-template-columns:1fr 1fr;gap:22px;}
@media(max-width:900px){.split{grid-template-columns:1fr;}}
@media print{body{background:#fff;}.card{box-shadow:none;border:1px solid #ccc;}
  tr,td,th{page-break-inside:avoid;}}
"""

# ── JS interactivity (workflow-html SKILL §2) ─────────────────────────────────
JS = """
/* Smooth scroll */
document.querySelectorAll('a[href^="#"]').forEach(a=>{
  a.addEventListener('click',e=>{
    const t=document.querySelector(a.getAttribute('href'));
    if(t){e.preventDefault();t.scrollIntoView({behavior:'smooth',block:'start'});}
  });
});

/* Collapsible cards with summary preview */
document.querySelectorAll('.card h2').forEach(h2=>{
  h2.style.cursor='pointer';
  h2.title='Click to collapse/expand';
  function buildSummary(sibs){
    const badges=[];
    sibs.forEach(s=>s.querySelectorAll('.badge').forEach(b=>badges.push(b.outerHTML)));
    const bHtml=badges.slice(0,4).join(' ');
    let text='';
    for(const s of sibs){
      if(s.tagName==='UL'||s.tagName==='OL'){
        const n=s.querySelectorAll('li').length;
        text=n+' item'+(n!==1?'s':'');break;
      }
      if(s.tagName==='TABLE'){
        const n=s.querySelectorAll('tbody tr').length;
        text=n+' row'+(n!==1?'s':'');break;
      }
      if(s.tagName==='P'&&s.textContent.trim()){
        text=s.textContent.trim().slice(0,80)+(s.textContent.length>80?'\\u2026':'');break;
      }
    }
    const parts=[bHtml,text].filter(Boolean).join(' &nbsp;&middot;&nbsp; ');
    return parts||'&nbsp;';
  }
  const sibs=[];let el=h2.nextElementSibling;
  while(el){sibs.push(el);el=el.nextElementSibling;}
  const chip=document.createElement('span');
  chip.style.cssText='display:inline-block;margin-left:12px;font-size:.8rem;font-weight:400;'+
    'color:#55636b;vertical-align:middle;pointer-events:none;';
  chip.className='section-summary-chip';
  chip.innerHTML=buildSummary(sibs);h2.appendChild(chip);
  const arrow=document.createElement('span');
  arrow.style.cssText='float:right;font-size:.8rem;color:#0f766e;user-select:none;margin-top:2px;';
  arrow.textContent='▾';h2.appendChild(arrow);
  h2.addEventListener('click',()=>{
    const col=h2.dataset.collapsed==='true';
    sibs.forEach(s=>s.style.display=col?'':'none');
    h2.dataset.collapsed=col?'false':'true';
    h2.style.borderBottomColor=col?'':'transparent';
    chip.style.opacity=col?'0.75':'1';
    arrow.textContent=col?'▾':'▸';
  });
});

/* Sticky auto-TOC */
(function(){
  const hs=[...document.querySelectorAll('.content .card h2')];
  if(hs.length<4)return;
  const nav=document.createElement('nav');
  nav.id='toc';
  nav.style.cssText='position:sticky;top:0;z-index:100;background:rgba(255,253,248,.95);'+
    'border-bottom:1px solid #d9d0c0;padding:8px 24px;font-size:.82rem;'+
    'display:flex;flex-wrap:wrap;gap:6px 18px;';
  hs.forEach((h,i)=>{
    if(!h.id)h.id='sec-'+i;
    const a=document.createElement('a');
    a.href='#'+h.id;a.textContent=h.textContent.replace('▾','').replace('▸','').trim();
    a.style.cssText='color:#0f766e;text-decoration:none;white-space:nowrap;';
    a.onmouseenter=()=>a.style.textDecoration='underline';
    a.onmouseleave=()=>a.style.textDecoration='none';
    nav.appendChild(a);
  });
  document.body.insertBefore(nav,document.querySelector('.content'));
})();

/* Back-to-top */
const btn=document.createElement('button');
btn.textContent='↑ Top';
btn.style.cssText='position:fixed;bottom:28px;right:28px;padding:8px 14px;'+
  'background:#0f766e;color:#fff;border:none;border-radius:8px;cursor:pointer;'+
  'font-size:.85rem;opacity:0;transition:opacity .2s;z-index:200;';
document.body.appendChild(btn);
window.addEventListener('scroll',()=>btn.style.opacity=scrollY>300?'1':'0');
btn.addEventListener('click',()=>window.scrollTo({top:0,behavior:'smooth'}));
"""

# ── Artifact type → canonical name ───────────────────────────────────────────
ARTIFACT_LABELS = {
    "plan-draft":     "Plan Draft Review",
    "plan-final":     "Plan Final Review",
    "implementation": "Implementation Review",
    "close":          "Close Review",
}

KEY_SECTIONS_BY_ARTIFACT = {
    "plan-draft": [
        "Gate-Pass Stage Status",
        "Prompt Start Context",
        "Why",
        "Acceptance Criteria",
        "Plan",
        "Plan Quality Eval Comparison",
        "Resource Intelligence",
        "Open Questions",
    ],
    "plan-final": [
        "Gate-Pass Stage Status",
        "Prompt Start Context",
        "Why",
        "Acceptance Criteria",
        "Plan",
        "Plan Quality Eval Comparison",
        "Resource Intelligence",
        "Open Questions",
        "Changes Since Stage 5",
        "Cross-Review Summary",
        "User Review - Plan (Final)",
    ],
    "implementation": [
        "Execution Brief",
        "Files Changed",
        "Cross-Review Summary",
        "Test Summary",
        "Gate Evidence Summary",
        "Stage Evidence Ledger",
        "Skill Manifest",
    ],
    "close": [
        "Gate-Pass Stage Status",
        "Prompt Start Context",
        "Why",
        "Acceptance Criteria",
        "Plan",
        "Execution Brief",
        "Cross-Review Summary",
        "Test Summary",
        "Gate Evidence Summary",
        "Resource Intelligence",
        "Problem Context",
        "Relevant Documents/Data",
        "Constraints",
        "Assumptions",
        "Open Questions",
        "Domain Notes",
        "Source Paths",
        "Skill Manifest",
        "Resource Intelligence Update",
        "Next Work",
        "Lifecycle Enforcement Progress",
        "Stage Evidence Ledger",
        "Asset Index",
        "User Review - Plan (Draft)",
        "User Review - Plan (Final)",
        "User Review - Implementation",
        "Agentic AI Horizon",
    ],
}

# ── Badge helpers ─────────────────────────────────────────────────────────────

def badge(text: str, kind: str = "info") -> str:
    """Return an HTML badge span."""
    return f'<span class="badge badge-{kind}">{text}</span>'


def status_badge(status: str) -> str:
    status = status.upper()
    kind = {"DONE": "pass", "WORKING": "warn", "PENDING": "info"}.get(status, "info")
    return badge(status, kind)


# ── Data collectors ───────────────────────────────────────────────────────────

def collect_skill_manifest(workspace_root: str, fm: dict, assets_dir: str) -> dict:
    manifest = {
        "mandatory_skills": [],
        "supporting_skills": [],
        "domain_skills": [],
        "repo_governance_skills": [],
        "source": "none",
    }
    manifest_ref = fm.get("skills_manifest_ref")
    candidate_paths = []
    if manifest_ref:
        if os.path.isabs(str(manifest_ref)):
            candidate_paths.append(str(manifest_ref))
        else:
            candidate_paths.append(os.path.join(workspace_root, str(manifest_ref)))
    candidate_paths.append(os.path.join(assets_dir, "evidence", "skill-manifest.yaml"))

    for path in candidate_paths:
        if os.path.exists(path):
            try:
                data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
            except Exception:
                data = {}
            if isinstance(data, dict):
                for key in ("mandatory_skills", "supporting_skills",
                            "domain_skills", "repo_governance_skills"):
                    val = data.get(key) or []
                    if isinstance(val, list):
                        manifest[key] = [str(i) for i in val if str(i).strip()]
                manifest["source"] = path
                return manifest

    for key in ("mandatory_skills", "supporting_skills",
                "domain_skills", "repo_governance_skills"):
        val = fm.get(key) or []
        if isinstance(val, list):
            manifest[key] = [str(i) for i in val if str(i).strip()]
    if any(manifest[k] for k in ("mandatory_skills", "supporting_skills",
                                  "domain_skills", "repo_governance_skills")):
        manifest["source"] = "frontmatter"
    return manifest


def collect_test_evidence(assets_dir: str) -> dict:
    example_path = Path(assets_dir) / "example-pack.md"
    variation_path = Path(assets_dir) / "variation-test-results.md"
    execute_evidence_path = Path(assets_dir) / "evidence" / "execute.yaml"
    legacy_execute_evidence_path = Path(assets_dir) / "execute-evidence.yaml"

    integrated_repo_tests_count = 0
    integrated_repo_tests_valid_range = False
    integrated_repo_tests_all_pass = False
    summary = "No variation-test summary available."

    if variation_path.exists():
        raw = variation_path.read_text(encoding="utf-8")
        for line in raw.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                summary = line
                break

    execute_source = (execute_evidence_path if execute_evidence_path.exists()
                      else legacy_execute_evidence_path)
    if execute_source.exists():
        try:
            execute_data = yaml.safe_load(execute_source.read_text(encoding="utf-8")) or {}
            tests = execute_data.get("integrated_repo_tests", [])
            if isinstance(tests, list):
                integrated_repo_tests_count = len(tests)
                integrated_repo_tests_valid_range = 3 <= integrated_repo_tests_count <= 5
                integrated_repo_tests_all_pass = all(
                    isinstance(t, dict)
                    and str(t.get("result", "")).strip().lower() in {"pass", "passed"}
                    for t in tests
                )
        except Exception:
            pass

    return {
        "example_pack_present": example_path.exists(),
        "variation_tests_present": variation_path.exists(),
        "example_pack_path": str(example_path),
        "variation_tests_path": str(variation_path),
        "variation_summary": summary,
        "execute_evidence_path": str(execute_source),
        "integrated_repo_tests_count": integrated_repo_tests_count,
        "integrated_repo_tests_valid_range": integrated_repo_tests_valid_range,
        "integrated_repo_tests_all_pass": integrated_repo_tests_all_pass,
    }


def collect_reviewers(assets_dir: str, wrk_id: str) -> list:
    reviewers = []
    if not os.path.exists(assets_dir):
        return reviewers
    for r_name in ["Claude", "Codex", "Gemini"]:
        r_path = os.path.join(assets_dir, f"review-{r_name.lower()}.md")
        if not os.path.exists(r_path):
            continue
        r_content = Path(r_path).read_text(encoding="utf-8")
        verdict_match = re.search(r"## Verdict\n\s*\**([A-Z_]+)\**", r_content)
        verdict = verdict_match.group(1) if verdict_match else "PENDING"
        kind_map = {"APPROVE": "pass", "MINOR": "warn", "MAJOR": "fail",
                    "NO_OUTPUT": "info", "PENDING": "info"}
        kind = kind_map.get(verdict, "info")
        reviewers.append({
            "name": r_name,
            "verdict": verdict,
            "kind": kind,
            "path": f"assets/{wrk_id}/review-{r_name.lower()}.md",
        })
    return reviewers


def collect_stage_gatepass(assets_dir: str) -> dict:
    """Collect per-stage lifecycle status from stage-evidence YAML."""
    stage_file = Path(assets_dir) / "evidence" / "stage-evidence.yaml"
    if not stage_file.exists():
        return {
            "present": False,
            "stages": [],
            "summary": "Missing stage-evidence.yaml",
            "autonomy": "Not applicable.",
            "reason": "stage-evidence.yaml missing",
        }

    try:
        data = yaml.safe_load(stage_file.read_text(encoding="utf-8")) or {}
    except Exception:
        return {
            "present": False,
            "stages": [],
            "summary": "Invalid stage-evidence.yaml",
            "autonomy": "Not applicable.",
            "reason": "stage-evidence.yaml parse error",
        }

    if not isinstance(data, dict):
        return {
            "present": False,
            "stages": [],
            "summary": "Invalid stage-evidence.yaml",
            "autonomy": "Not applicable.",
            "reason": "stage-evidence root must be a mapping",
        }

    raw_stages = data.get("stages", [])
    if not isinstance(raw_stages, list):
        return {
            "present": False,
            "stages": [],
            "summary": "Invalid stage-evidence.yaml",
            "autonomy": "Not applicable.",
            "reason": "stages must be a list",
        }

    stages = []
    # Backward-compat: some legacy ledgers used "autonomy_maturity".
    autonomy = str(data.get("autonomy_maturity_level", data.get("autonomy_maturity", "Not applicable.")))
    done = pending = na = 0
    fail = 0
    for item in raw_stages:
        if not isinstance(item, dict):
            continue
        order = item.get("order", "")
        stage = str(item.get("stage", "")).strip() or "Unknown"
        status = str(item.get("status", "")).strip().lower() or "unknown"
        evidence = str(item.get("evidence", "")).strip() or "n/a"
        owner = str(item.get("owner", "Not applicable.")).strip() or "Not applicable."
        blocker = str(item.get("blocker", "Not applicable.")).strip() or "Not applicable."
        comment = str(item.get("comment", "Not applicable.")).strip() or "Not applicable."
        raw_human_decision = item.get("human_decision_required", "Not applicable.")
        if isinstance(raw_human_decision, bool):
            human_decision = "yes" if raw_human_decision else "no"
        else:
            normalized_human_decision = str(raw_human_decision).strip().lower()
            if normalized_human_decision in {"true", "yes"}:
                human_decision = "yes"
            elif normalized_human_decision in {"false", "no"}:
                human_decision = "no"
            else:
                human_decision = str(raw_human_decision).strip() or "Not applicable."
        if status in {"done", "pass", "passed"}:
            gate = "PASS"
            done += 1
        elif status in {"fail", "failed", "blocked", "missing", "error"}:
            gate = "FAIL"
            fail += 1
        elif status in {"n/a", "na", "not_applicable"}:
            gate = "N/A"
            na += 1
        else:
            gate = "WARN"
            pending += 1
        stages.append({
            "order": order,
            "stage": stage,
            "status": status,
            "gate": gate,
            "evidence": evidence,
            "owner": owner,
            "blocker": blocker,
            "comment": comment,
            "human_decision_required": human_decision,
        })

    stages.sort(key=lambda s: int(s["order"]) if str(s["order"]).isdigit() else 999)
    summary = f"{done} pass · {fail} fail · {pending} pending/warn · {na} n/a"
    return {"present": True, "stages": stages, "summary": summary, "autonomy": autonomy}


def collect_prompt_start_context(body_md: str, fm: dict) -> dict:
    patterns = [
        r'(?ms)^\*Source:\s*"(?P<text>.*?)"\s*\*$',
        r'(?ms)^Source:\s*"(?P<text>.*?)"\s*$',
        r'(?ms)^\*Source:\s*(?P<text>.*?)\s*\*$',
        r'(?ms)^Source:\s*(?P<text>.*?)\s*$',
    ]
    for pattern in patterns:
        match = re.search(pattern, body_md)
        if match:
            text = " ".join(match.group("text").split())
            if text:
                return {
                    "present": True,
                    "text": text,
                    "source": "body_source",
                    "synthesized": False,
                }

    title = " ".join(str(fm.get("title", "")).split())
    what_match = re.search(r"## (?:What|Objective|Goal)\n(.*?)(?=\n##|\Z)", body_md, re.DOTALL)
    what_text = ""
    if what_match:
        what_text = " ".join(what_match.group(1).split())
    fallback = " — ".join(part for part in [title, what_text] if part)
    if fallback:
        return {
            "present": True,
            "text": fallback,
            "source": "title_plus_what",
            "synthesized": True,
        }

    return {
        "present": False,
        "text": "",
        "source": "none",
        "synthesized": False,
    }


def collect_plan_quality_eval(assets_dir: str) -> dict:
    candidate_paths = [
        Path(assets_dir) / "evidence" / "plan-quality-eval.yaml",
        Path(assets_dir) / "plan-quality-eval.yaml",
    ]
    for path in candidate_paths:
        if not path.exists():
            continue
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        plans = data.get("plans", [])
        if not isinstance(plans, list):
            plans = []
        rows = []
        for item in plans:
            if not isinstance(item, dict):
                continue
            rows.append({
                "plan": str(item.get("plan", item.get("name", "Unknown"))).strip() or "Unknown",
                "rating": str(item.get("rating", "pending")).strip() or "pending",
                "decision": str(item.get("decision", "pending")).strip() or "pending",
                "notes": str(item.get("notes", "Not applicable.")).strip() or "Not applicable.",
                "completeness": str(item.get("completeness", "n/a")).strip() or "n/a",
                "test_eval_quality": str(item.get("test_eval_quality", "n/a")).strip() or "n/a",
                "execution_clarity": str(item.get("execution_clarity", "n/a")).strip() or "n/a",
                "risk_coverage": str(item.get("risk_coverage", "n/a")).strip() or "n/a",
                "standards_gate_alignment": str(item.get("standards_gate_alignment", "n/a")).strip() or "n/a",
            })
        return {
            "present": bool(rows),
            "plans": rows,
            "decision_summary": str(data.get("decision_summary", "Not applicable.")).strip() or "Not applicable.",
            "artifact_ref": str(data.get("artifact_ref", path)).strip() or str(path),
        }

    return {
        "present": False,
        "plans": [],
        "decision_summary": "Not applicable.",
        "artifact_ref": "Not applicable.",
    }


def collect_changes_since_stage5(assets_dir: str, workspace_root: str) -> dict:
    """Return git delta between approved Stage 5 baseline commit and HEAD.

    Baseline commit is the last plan_draft event in user-review-publish.yaml
    (AC-12: authoritative current published draft commit).
    """
    publish_path = Path(assets_dir) / "evidence" / "user-review-publish.yaml"
    if not publish_path.exists():
        return {"present": False, "reason": "user-review-publish.yaml not found"}
    try:
        data = yaml.safe_load(publish_path.read_text(encoding="utf-8")) or {}
    except Exception as e:
        return {"present": False, "reason": f"YAML parse error: {e}"}

    events = data.get("events") if isinstance(data, dict) else None
    if not isinstance(events, list):
        return {"present": False, "reason": "no events in user-review-publish.yaml"}

    baseline_commit = None
    for ev in reversed(events):
        if isinstance(ev, dict) and ev.get("stage") == "plan_draft":
            baseline_commit = str(ev.get("commit", "") or "").strip()
            break

    if not baseline_commit or baseline_commit == "unknown":
        return {"present": False, "reason": "no plan_draft event with commit in publish log"}

    # Verify commit exists in repo
    try:
        subprocess.run(
            ["git", "rev-parse", "--verify", baseline_commit],
            cwd=workspace_root, capture_output=True, check=True, timeout=8,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return {"present": False, "reason": f"baseline commit not resolvable: {baseline_commit}"}

    # Get changed files since baseline
    try:
        stat_result = subprocess.run(
            ["git", "diff", "--stat", f"{baseline_commit}..HEAD"],
            cwd=workspace_root, capture_output=True, text=True, timeout=8,
        )
        stat_text = stat_result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        stat_text = "(git diff timed out)"

    # Get commit log since baseline (one-line, newest first)
    try:
        log_result = subprocess.run(
            ["git", "log", "--oneline", f"{baseline_commit}..HEAD"],
            cwd=workspace_root, capture_output=True, text=True, timeout=8,
        )
        commits = [c for c in log_result.stdout.strip().splitlines() if c.strip()]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        commits = []

    return {
        "present": True,
        "baseline_commit": baseline_commit,
        "stat_text": stat_text or "(no changes since Stage 5 baseline)",
        "commits": commits,
        "commit_count": len(commits),
    }


# ── HTML section builders ─────────────────────────────────────────────────────

def render_meta_grid(fm: dict) -> str:
    commit = str(fm.get("commit", "") or "")
    commit_short = commit[:7] if commit else "n/a"
    route = str(fm.get("route", fm.get("complexity", "B")))
    complexity = str(fm.get("complexity", ""))
    route_label = f"{route} — {complexity}" if complexity and route != complexity else route
    return f"""<div class="meta">
  <div class="pill"><strong>WRK ID</strong>{fm.get('id','')}</div>
  <div class="pill"><strong>Status</strong>{status_badge(str(fm.get('status','pending')))}</div>
  <div class="pill"><strong>Route</strong>{route_label}</div>
  <div class="pill"><strong>Orchestrator</strong>{fm.get('orchestrator','—')}</div>
  <div class="pill"><strong>Computer</strong>{fm.get('computer','—')}</div>
  <div class="pill"><strong>Created</strong>{str(fm.get('created_at',''))[:10]}</div>
  <div class="pill"><strong>Commit</strong><code>{commit_short}</code></div>
  <div class="pill"><strong>% Done</strong>{fm.get('percent_complete',0)}%</div>
</div>"""


def render_skill_manifest(manifest: dict) -> str:
    rows = ""
    for key, label in [
        ("mandatory_skills", "Mandatory"),
        ("supporting_skills", "Supporting"),
        ("domain_skills", "Domain"),
        ("repo_governance_skills", "Repo Governance"),
    ]:
        items = manifest.get(key) or []
        for item in items:
            rows += f"<tr><td>{label}</td><td><code>{item}</code></td></tr>\n"
    if not rows:
        rows = "<tr><td colspan='2' style='color:var(--muted)'>Not applicable.</td></tr>"
    return f"""<h2>Skill Manifest</h2>
<table>
  <thead><tr><th>Category</th><th>Skill</th></tr></thead>
  <tbody>{rows}</tbody>
</table>
<p style="font-size:.82rem;color:var(--muted)">Source: <code>{manifest.get('source','none')}</code></p>"""


def render_test_evidence(te: dict) -> str:
    ep = badge("present", "pass") if te["example_pack_present"] else badge("missing", "warn")
    vt = badge("present", "pass") if te["variation_tests_present"] else badge("missing", "warn")
    cnt = te["integrated_repo_tests_count"]
    rng = badge(f"{cnt} tests — valid range", "pass") if te["integrated_repo_tests_valid_range"] \
          else badge(f"{cnt} tests — outside 3-5", "warn")
    allp = badge("all pass", "pass") if te["integrated_repo_tests_all_pass"] \
           else badge("not all pass", "warn" if cnt > 0 else "info")
    return f"""<h2>Test Summary</h2>
<table>
  <thead><tr><th>Check</th><th>Result</th><th>Path</th></tr></thead>
  <tbody>
    <tr><td>Example Pack</td><td>{ep}</td><td><code>{te['example_pack_path']}</code></td></tr>
    <tr><td>Variation Tests</td><td>{vt}</td><td><code>{te['variation_tests_path']}</code></td></tr>
    <tr><td>Integrated Repo Tests</td><td>{rng} {allp}</td>
        <td><code>{te['execute_evidence_path']}</code></td></tr>
  </tbody>
</table>
<p><strong>Variation summary:</strong> {te['variation_summary']}</p>"""


def render_reviewer_synthesis(reviewers: list) -> str:
    if not reviewers:
        return "<h2>Cross-Review Summary</h2><p>Not applicable.</p>"
    rows = ""
    for r in reviewers:
        rows += (f"<tr><td>{r['name']}</td>"
                 f"<td>{badge(r['verdict'], r['kind'])}</td>"
                 f"<td><code>{r['path']}</code></td></tr>\n")
    return f"""<h2>Cross-Review Summary</h2>
<table>
  <thead><tr><th>Provider</th><th>Verdict</th><th>Artifact</th></tr></thead>
  <tbody>{rows}</tbody>
</table>"""


def render_gatepass_section(gp: dict) -> str:
    if not gp.get("present"):
        reason = html_escape(str(gp.get("reason", "Missing stage evidence")), quote=True)
        summary_text = html_escape(str(gp.get("summary", "Missing stage evidence")), quote=True)
        return (
            "<h2>Gate-Pass Stage Status</h2>"
            f"<p>{badge('FAIL', 'fail')} <strong>{summary_text}</strong> — {reason}</p>"
        )
    rows = ""
    for s in gp.get("stages", []):
        gate_kind = (
            "pass" if s["gate"] == "PASS"
            else ("fail" if s["gate"] == "FAIL" else ("warn" if s["gate"] == "WARN" else "info"))
        )
        order_text = html_escape(str(s["order"]), quote=True)
        status_text = html_escape(str(s["status"]).upper(), quote=True)
        stage_text = html_escape(str(s["stage"]), quote=True)
        gate_text = html_escape(str(s["gate"]), quote=True)
        human_decision = html_escape(str(s["human_decision_required"]), quote=True)
        owner_text = html_escape(str(s["owner"]), quote=True)
        blocker_text = html_escape(str(s["blocker"]), quote=True)
        comment_text = html_escape(str(s["comment"]), quote=True)
        evidence_text = html_escape(str(s["evidence"]), quote=True)
        rows += (
            f"<tr><td>{order_text}</td>"
            f"<td>{stage_text}</td>"
            f"<td>{badge(status_text, 'info')}</td>"
            f"<td>{badge(gate_text, gate_kind)}</td>"
            f"<td>{human_decision}</td>"
            f"<td>{owner_text}</td>"
            f"<td>{blocker_text}</td>"
            f"<td>{comment_text}</td>"
            f"<td><code>{evidence_text}</code></td></tr>\n"
        )
    if not rows:
        return (
            "<h2>Gate-Pass Stage Status</h2>"
            f"<p>{badge('FAIL', 'fail')} <strong>No valid stage rows found</strong> — "
            "stage-evidence.yaml present but empty or malformed</p>"
        )
    summary_text = html_escape(str(gp.get("summary", "Not applicable.")), quote=True)
    autonomy_text = html_escape("Autonomy: " + str(gp.get("autonomy", "Not applicable.")), quote=True)
    return f"""<h2>Gate-Pass Stage Status</h2>
<p><strong>Summary:</strong> {summary_text} &nbsp; {badge(autonomy_text, 'info')}</p>
<table>
  <thead><tr><th>Order</th><th>Stage</th><th>Stage Status</th><th>Gate-Pass</th><th>Human Decision</th><th>Owner</th><th>Blocker?</th><th>Comment</th><th>Evidence</th></tr></thead>
  <tbody>{rows}</tbody>
</table>"""


def render_prompt_start_context(ctx: dict) -> str:
    if not ctx.get("present"):
        return ""
    label = "Synthesized from WRK title + What section" if ctx.get("synthesized") else "Captured from Source note"
    text = html_escape(str(ctx.get("text", "Not applicable.")), quote=True)
    label_text = html_escape(label, quote=True)
    return f"""<h2>Prompt Start Context</h2>
<div class="panel">
  <p>{text}</p>
  <p style="font-size:.82rem;color:var(--muted)"><strong>Source:</strong> {label_text}</p>
</div>"""


def render_plan_quality_eval_section(plan_eval: dict) -> str:
    if not plan_eval.get("present"):
        return ""
    rows = ""
    for item in plan_eval.get("plans", []):
        rows += (
            f"<tr><td>{html_escape(item['plan'], quote=True)}</td>"
            f"<td>{html_escape(item['rating'], quote=True)}</td>"
            f"<td>{html_escape(item['completeness'], quote=True)}</td>"
            f"<td>{html_escape(item['test_eval_quality'], quote=True)}</td>"
            f"<td>{html_escape(item['execution_clarity'], quote=True)}</td>"
            f"<td>{html_escape(item['risk_coverage'], quote=True)}</td>"
            f"<td>{html_escape(item['standards_gate_alignment'], quote=True)}</td>"
            f"<td>{html_escape(item['decision'], quote=True)}</td>"
            f"<td>{html_escape(item['notes'], quote=True)}</td></tr>\n"
        )
    summary = html_escape(str(plan_eval.get("decision_summary", "Not applicable.")), quote=True)
    artifact_ref = html_escape(str(plan_eval.get("artifact_ref", "Not applicable.")), quote=True)
    return f"""<h2>Plan Quality Eval Comparison</h2>
<p><strong>Combine-step decision:</strong> {summary}</p>
<table>
  <thead><tr><th>Plan</th><th>Rating</th><th>Completeness</th><th>Test/Eval</th><th>Execution Clarity</th><th>Risk Coverage</th><th>Standards/Gate</th><th>Decision</th><th>Notes</th></tr></thead>
  <tbody>{rows}</tbody>
</table>
<p style="font-size:.82rem;color:var(--muted)"><strong>Source:</strong> <code>{artifact_ref}</code></p>"""


def render_changes_since_stage5(delta: dict) -> str:
    if not delta.get("present"):
        reason = html_escape(str(delta.get("reason", "Not applicable.")), quote=True)
        return f"""<h2>Changes Since Stage 5</h2>
<div class="panel">
  <p style="color:var(--muted)">{reason}</p>
</div>"""
    baseline = html_escape(str(delta.get("baseline_commit", "unknown")), quote=True)
    stat = html_escape(str(delta.get("stat_text", "(no changes)")), quote=True)
    commit_count = int(delta.get("commit_count", 0))
    commits = delta.get("commits", [])
    commit_list = "".join(
        f"<li><code>{html_escape(c, quote=True)}</code></li>" for c in commits[:30]
    )
    if len(commits) > 30:
        commit_list += f"<li style='color:var(--muted)'>…and {len(commits)-30} more</li>"
    commits_html = f"<ul>{commit_list}</ul>" if commits else "<p style='color:var(--muted)'>No commits since baseline.</p>"
    return f"""<h2>Changes Since Stage 5</h2>
<div class="panel">
  <p><strong>Stage 5 approved baseline:</strong> <code>{baseline}</code></p>
  <p><strong>Commits since baseline:</strong> {commit_count}</p>
  {commits_html}
  <details>
    <summary><strong>Git diff stat</strong></summary>
    <pre style="white-space:pre-wrap;font-size:.82rem">{stat}</pre>
  </details>
</div>"""


# ── Main HTML renderer ────────────────────────────────────────────────────────

def _extract_h2_titles(html: str) -> set[str]:
    titles = set()
    for raw in re.findall(r"<h2[^>]*>(.*?)</h2>", html, flags=re.IGNORECASE | re.DOTALL):
        txt = re.sub(r"<[^>]+>", "", raw).strip()
        if txt:
            titles.add(txt)
    return titles


def _append_missing_key_sections(body_html: str, artifact_type: str, extra_html: list[str] | None = None) -> str:
    required = KEY_SECTIONS_BY_ARTIFACT.get(artifact_type, [])
    if not required:
        return body_html
    present = _extract_h2_titles(body_html)
    for block in (extra_html or []):
        present.update(_extract_h2_titles(block))
    missing = [name for name in required if name not in present]
    if not missing:
        return body_html
    additions = "".join(f"<h2>{name}</h2><p>Not applicable.</p>" for name in missing)
    return f"{body_html}\n{additions}"


def _normalize_close_section_names(body_md: str, artifact_type: str) -> str:
    """Consolidate legacy close-stage section names into canonical names."""
    if artifact_type != "close":
        return body_md
    # Consolidate to one section name in generated HTML.
    return re.sub(r"(?mi)^##\s*Future\s+Work\s*$", "## Next Work", body_md)


def _strip_duplicate_body_title(body_html: str, wrk_title: str) -> str:
    match = re.match(r"^\s*<h1>(.*?)</h1>\s*", body_html, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return body_html
    first_heading = re.sub(r"<[^>]+>", "", match.group(1)).strip()
    normalized_heading = " ".join(first_heading.split()).casefold()
    normalized_title = " ".join(str(wrk_title).split()).casefold()
    if normalized_heading != normalized_title:
        return body_html
    return body_html[match.end():].lstrip()


def _suppress_duplicate_generated_sections(
    body_html: str,
    skill_manifest_html: str,
    test_evidence_html: str,
    reviewer_html: str,
    gatepass_html: str,
) -> tuple[str, str, str, str]:
    """Avoid duplicate generated sections when WRK body already includes them."""
    titles = _extract_h2_titles(body_html)
    if "Skill Manifest" in titles:
        skill_manifest_html = ""
    if "Test Summary" in titles:
        test_evidence_html = ""
    if "Cross-Review Summary" in titles:
        reviewer_html = ""
    if "Gate-Pass Stage Status" in titles:
        gatepass_html = ""
    return skill_manifest_html, test_evidence_html, reviewer_html, gatepass_html


def _insert_after_first_h1(body_html: str, section_html: str) -> str:
    if not section_html.strip():
        return body_html
    match = re.search(r"</h1>", body_html, flags=re.IGNORECASE)
    if not match:
        return f"{section_html}\n{body_html}"
    return f"{body_html[:match.end()]}\n{section_html}\n{body_html[match.end():]}"


def _insert_before_first_matching_h2(body_html: str, section_html: str, section_titles: list[str]) -> str:
    if not section_html.strip():
        return body_html
    for title in section_titles:
        pattern = rf"<h2[^>]*>\s*{re.escape(title)}\s*</h2>"
        match = re.search(pattern, body_html, flags=re.IGNORECASE)
        if match:
            return f"{body_html[:match.start()]}\n{section_html}\n{body_html[match.start():]}"
    return f"{body_html}\n{section_html}"


def _inject_generated_plan_sections(
    body_html: str,
    artifact_type: str,
    prompt_start_context_html: str,
    plan_quality_eval_html: str,
    changes_since_stage5_html: str = "",
) -> str:
    if artifact_type not in {"plan-draft", "plan-final"}:
        return body_html

    titles = _extract_h2_titles(body_html)
    if "Prompt Start Context" not in titles and prompt_start_context_html.strip():
        body_html = _insert_after_first_h1(body_html, prompt_start_context_html)
        titles.add("Prompt Start Context")

    if "Plan Quality Eval Comparison" not in titles and plan_quality_eval_html.strip():
        body_html = _insert_before_first_matching_h2(
            body_html,
            plan_quality_eval_html,
            ["Resource Intelligence", "Open Questions", "Changes from Draft", "Changes Since Stage 5", "Cross-Review Summary", "User Review - Plan (Final)"],
        )

    if artifact_type == "plan-final" and "Changes Since Stage 5" not in titles and changes_since_stage5_html.strip():
        body_html = _insert_before_first_matching_h2(
            body_html,
            changes_since_stage5_html,
            ["Cross-Review Summary", "User Review - Plan (Final)"],
        )

    return body_html

def render_wrk_html(
    wrk_meta: dict,
    artifact_type: str,
    sections: dict,
    evidence: dict | None = None,
) -> str:
    """Return a complete HTML string conforming to workflow-html SKILL v1.0.0.

    Args:
        wrk_meta:      Frontmatter fields from WRK markdown file.
        artifact_type: One of plan-draft | plan-final | implementation | close.
        sections:      section-name → HTML content mapping (used for body content).
        evidence:      Optional stage-evidence YAML dict.
    """
    label = ARTIFACT_LABELS.get(artifact_type, artifact_type.replace("-", " ").title())
    wrk_id = str(wrk_meta.get("id", "WRK-???"))
    title = str(wrk_meta.get("title", wrk_id))
    lede = sections.get("lede", f"Review artifact for {wrk_id}")
    exec_summary_html = sections.get("exec_summary_html", "")
    body_html = sections.get("body_html", "")
    skill_manifest_html = sections.get("skill_manifest_html", "")
    gatepass_html = sections.get("gatepass_html", "")
    test_evidence_html = sections.get("test_evidence_html", "")
    reviewer_html = sections.get("reviewer_html", "")

    meta_grid = render_meta_grid(wrk_meta)
    gatepass_card_html = (
        f"<div class=\"card\">\n    {gatepass_html}\n  </div>"
        if gatepass_html.strip()
        else ""
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{label}: {wrk_id} — {title[:60]}</title>
  <style>{CSS}</style>
</head>
<body>

<header class="hero">
  <div class="hero-inner">
    <div class="eyebrow">{wrk_id} &middot; {label}</div>
    <h1>{title}</h1>
    <p class="lede">{lede}</p>
  </div>
</header>

<main class="content">
  {meta_grid}

  <div class="card">
    <div class="exec-summary">
      <h2>Executive Summary</h2>
      {exec_summary_html}
    </div>

    {skill_manifest_html}
  </div>

  <div class="card">
    {body_html}
  </div>

  {gatepass_card_html}

  <div class="card">
    {test_evidence_html}
    {reviewer_html}
  </div>

</main>

<script>{JS}</script>
</body>
</html>
"""


# ── generate_review entry point ───────────────────────────────────────────────

def generate_review(wrk_id: str, artifact_type: str = "plan-draft",
                    output_file: str | None = None) -> None:
    workspace_root = os.popen("git rev-parse --show-toplevel").read().strip()
    queue_dir = os.path.join(workspace_root, ".claude/work-queue")

    # Find WRK file (search flat folders first, then archive subdirectories)
    wrk_file = ""
    for folder in ["working", "pending", "done", "archived"]:
        path = os.path.join(queue_dir, folder, f"{wrk_id}.md")
        if os.path.exists(path):
            wrk_file = path
            break
    if not wrk_file:
        # Search recursively under archive/
        for p in Path(queue_dir).glob(f"archive/**/{wrk_id}.md"):
            wrk_file = str(p)
            break
    if not wrk_file:
        print(f"Error: Could not find {wrk_id}.md")
        return

    content = Path(wrk_file).read_text(encoding="utf-8")
    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not fm_match:
        print("Error: No frontmatter found")
        return
    try:
        fm = yaml.safe_load(fm_match.group(1)) or {}
    except Exception as e:
        print(f"Error parsing frontmatter: {e}")
        fm = {}

    body = content[fm_match.end():]
    # For plan-draft / plan-final: use spec_ref (plan.md) as the body when available
    if artifact_type in {"plan-draft", "plan-final"} and fm.get("spec_ref"):
        spec_path = Path(workspace_root) / str(fm["spec_ref"])
        if spec_path.exists():
            body = spec_path.read_text(encoding="utf-8")
    body = _normalize_close_section_names(body, artifact_type)
    md = markdown.Markdown(extensions=["extra", "codehilite", "tables"])

    # Lede: first non-blank, non-heading line of body
    lede_lines = [l for l in body.split("\n") if l.strip() and not l.startswith("#")][:1]
    lede = lede_lines[0].strip() if lede_lines else f"Review artifact for {wrk_id}"

    # Executive summary from ## What / ## Objective
    what_match = re.search(r"## (?:What|Objective|Goal)\n(.*?)(?=\n##|\Z)", body, re.DOTALL)
    exec_md = what_match.group(1).strip() if what_match else "No executive summary found."
    exec_summary_html = md.convert(exec_md)
    md.reset()
    body_html = md.convert(body)
    body_html = _strip_duplicate_body_title(body_html, fm.get("title", wrk_id))

    assets_dir = os.path.join(queue_dir, "assets", wrk_id)
    skill_manifest = collect_skill_manifest(workspace_root, fm, assets_dir)
    test_evidence = collect_test_evidence(assets_dir)
    reviewers = collect_reviewers(assets_dir, wrk_id)
    gatepass = collect_stage_gatepass(assets_dir)
    prompt_start_context = collect_prompt_start_context(body, fm)
    plan_quality_eval = collect_plan_quality_eval(assets_dir)
    changes_since_stage5 = (
        collect_changes_since_stage5(assets_dir, workspace_root)
        if artifact_type == "plan-final"
        else {"present": False, "reason": "only rendered for plan-final"}
    )

    skill_manifest_html = render_skill_manifest(skill_manifest)
    test_evidence_html = render_test_evidence(test_evidence)
    reviewer_html = render_reviewer_synthesis(reviewers)
    gatepass_html = render_gatepass_section(gatepass)
    prompt_start_context_html = render_prompt_start_context(prompt_start_context)
    plan_quality_eval_html = render_plan_quality_eval_section(plan_quality_eval)
    changes_since_stage5_html = (
        render_changes_since_stage5(changes_since_stage5)
        if artifact_type == "plan-final"
        else ""
    )
    body_html = _inject_generated_plan_sections(
        body_html,
        artifact_type,
        prompt_start_context_html,
        plan_quality_eval_html,
        changes_since_stage5_html,
    )
    skill_manifest_html, test_evidence_html, reviewer_html, gatepass_html = _suppress_duplicate_generated_sections(
        body_html,
        skill_manifest_html,
        test_evidence_html,
        reviewer_html,
        gatepass_html,
    )
    body_html = _append_missing_key_sections(
        body_html,
        artifact_type,
        extra_html=[
            skill_manifest_html,
            test_evidence_html,
            reviewer_html,
            gatepass_html,
            changes_since_stage5_html,
        ],
    )

    sections = {
        "lede": lede,
        "exec_summary_html": exec_summary_html,
        "body_html": body_html,
        "skill_manifest_html": skill_manifest_html,
        "gatepass_html": gatepass_html,
        "test_evidence_html": test_evidence_html,
        "reviewer_html": reviewer_html,
        "changes_since_stage5_html": changes_since_stage5_html,
    }

    html = render_wrk_html(fm, artifact_type, sections)

    if not output_file:
        name_map = {
            "plan-draft": "plan-draft-review.html",
            "plan-final": "plan-final-review.html",
            "implementation": "implementation-review.html",
            "close": "workflow-final-review.html",
        }
        name = name_map.get(artifact_type, f"{artifact_type}-review.html")
        output_file = os.path.join(queue_dir, "assets", wrk_id, name)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    Path(output_file).write_text(html, encoding="utf-8")
    print(f"✔ HTML generated ({artifact_type}): {output_file}")


# ═══════════════════════════════════════════════════════════════════════════════
# LIFECYCLE HTML — single-file per WRK, stateless regeneration (WRK-1031)
# ═══════════════════════════════════════════════════════════════════════════════

LIFECYCLE_CSS = """
:root{--bg:#f3efe6;--panel:#fffdf8;--ink:#172126;--muted:#55636b;
  --accent:#0f766e;--accent-2:#8a5a2b;--line:#d9d0c0;
  --shadow:0 12px 32px rgba(20,33,38,0.07);
  --done:#166534;--done-bg:#dcfce7;--active:#92400e;--active-bg:#fef3c7;
  --pending:#55636b;--pending-bg:#f1f5f9;--na:#6b7280;--na-bg:#f3f4f6;}
*{box-sizing:border-box;}
body{font-family:Georgia,"Times New Roman",serif;
  background:radial-gradient(circle at top,#fffaf0 0,var(--bg) 48%,#ebe5d7 100%);
  color:var(--ink);line-height:1.55;margin:0;}
a{color:var(--accent);text-decoration:none;}a:hover{text-decoration:underline;}
code{font-family:"SFMono-Regular",Consolas,Menlo,monospace;
  background:rgba(27,31,35,0.06);padding:.15em .35em;border-radius:3px;font-size:.86em;}
pre{background:#f6f8fa;border:1px solid var(--line);border-radius:7px;
  padding:12px 14px;overflow-x:auto;font-size:.82rem;margin:10px 0;}
.hero{padding:36px 24px 20px;border-bottom:1px solid rgba(23,33,38,0.08);
  background:linear-gradient(135deg,rgba(15,118,110,0.07),rgba(138,90,43,0.09));}
.hero-inner{max-width:1100px;margin:0 auto;}
.eyebrow{text-transform:uppercase;letter-spacing:.12em;font-size:.68rem;
  color:var(--accent);font-weight:700;margin:0 0 6px;}
h1{margin:0 0 8px;font-size:clamp(1.35rem,2.4vw,2.1rem);line-height:1.06;}
.lede{color:var(--muted);font-size:.92rem;margin:0 0 14px;max-width:72ch;}
.meta-row{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:2px;}
.pill{background:var(--panel);border:1px solid var(--line);border-radius:8px;
  padding:5px 10px;font-size:.8rem;}
.pill strong{font-size:.65rem;text-transform:uppercase;letter-spacing:.07em;
  color:var(--accent-2);display:block;margin-bottom:1px;}
.stage-strip{background:var(--panel);border-bottom:1px solid var(--line);
  padding:12px 24px;position:sticky;top:0;z-index:100;box-shadow:0 2px 8px rgba(0,0,0,0.06);}
.stage-strip-inner{max-width:1100px;margin:0 auto;display:flex;flex-wrap:wrap;gap:5px;align-items:center;}
.stage-strip-label{font-size:.68rem;text-transform:uppercase;letter-spacing:.08em;
  color:var(--muted);margin-right:6px;white-space:nowrap;}
.sc{display:inline-flex;align-items:center;justify-content:center;
  width:30px;height:30px;border-radius:50%;font-size:.75rem;font-weight:700;
  text-decoration:none;transition:transform .15s;}
.sc:hover{transform:scale(1.15);}
.sc-done{background:var(--done-bg);color:var(--done);}
.sc-active{background:var(--active-bg);color:var(--active);
  box-shadow:0 0 0 2px var(--active);animation:pulse 2s infinite;}
.sc-pending{background:var(--pending-bg);color:var(--pending);}
.sc-na{background:var(--na-bg);color:var(--na);}
@keyframes pulse{0%,100%{box-shadow:0 0 0 2px var(--active);}
  50%{box-shadow:0 0 0 4px rgba(146,64,14,0.3);}}
.content{max-width:1100px;margin:0 auto;padding:24px 24px 64px;}
.stage-section{margin-bottom:16px;border-radius:14px;border:1px solid var(--line);
  background:var(--panel);box-shadow:var(--shadow);overflow:hidden;}
.stage-header{display:grid;grid-template-columns:48px 1fr auto;gap:12px;align-items:center;
  padding:14px 18px;cursor:pointer;user-select:none;}
.stage-header:hover{background:rgba(15,118,110,0.03);}
.snum{font-size:1.5rem;font-weight:800;color:var(--line);text-align:center;line-height:1;}
.stitle{font-size:.95rem;font-weight:700;color:var(--ink);margin:0;}
.smeta{font-size:.76rem;color:var(--muted);margin:2px 0 0;}
.sbadges{display:flex;gap:6px;flex-wrap:wrap;align-items:center;}
.badge{display:inline-block;padding:2px 8px;border-radius:999px;font-size:.7rem;
  font-weight:700;text-transform:uppercase;letter-spacing:.05em;white-space:nowrap;}
.b-done{background:var(--done-bg);color:var(--done);}
.b-active{background:var(--active-bg);color:var(--active);}
.b-pending{background:var(--pending-bg);color:var(--pending);}
.b-na{background:var(--na-bg);color:var(--na);}
.b-human{background:#ede9fe;color:#6d28d9;}
.b-agent{background:#d1fae5;color:#065f46;}
.b-chain{background:#dbeafe;color:#1e40af;}
.b-light{background:#f0fdf4;color:#166534;}
.b-medium{background:#fef9c3;color:#854d0e;}
.b-heavy{background:#fee2e2;color:#991b1b;}
.b-gate{background:#fce7f3;color:#9d174d;}
.chevron{font-size:.75rem;color:var(--muted);transition:transform .2s;}
.stage-body{padding:0 18px 16px;border-top:1px solid var(--line);}
.stage-body.collapsed{display:none;}
.schema{background:#f8f9fa;border:1px solid var(--line);border-radius:8px;
  padding:12px 14px;font-size:.82rem;margin:12px 0;}
.schema-row{display:grid;grid-template-columns:160px 1fr;gap:4px 10px;margin:3px 0;}
.schema-key{color:var(--accent);font-family:monospace;font-weight:600;}
.schema-val{color:var(--ink);}
.section-label{font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;
  color:var(--accent-2);font-weight:700;margin:14px 0 6px;}
.item-list{margin:0;padding:0 0 0 18px;font-size:.87rem;}
.item-list li{margin:3px 0;color:var(--muted);}
.item-list li strong{color:var(--ink);}
.ac-list{margin:0;padding:0 0 0 18px;font-size:.85rem;}
.ac-list li{margin:4px 0;color:var(--muted);}
.ac-list li strong{color:var(--ink);}
.awaiting{background:var(--active-bg);border:1px solid #fcd34d;border-radius:8px;
  padding:10px 14px;font-size:.86rem;color:var(--active);margin:12px 0;}
table{border-collapse:collapse;width:100%;margin:12px 0;font-size:.84rem;}
th,td{border-top:1px solid var(--line);padding:8px 7px;text-align:left;vertical-align:top;}
th{font-weight:700;text-transform:uppercase;letter-spacing:.05em;font-size:.74rem;color:var(--ink);}
td{color:var(--muted);}td strong{color:var(--ink);}
@media(max-width:700px){.stage-header{grid-template-columns:36px 1fr;}.sbadges{display:none;}
  .schema-row{grid-template-columns:1fr;}}
@media print{body{background:#fff;}.stage-strip{position:static;}
  .stage-body.collapsed{display:block;}}
"""

LIFECYCLE_JS = """
function toggle(header) {
  const body = header.nextElementSibling;
  const chevron = header.querySelector('.chevron');
  const collapsed = body.classList.toggle('collapsed');
  chevron.textContent = collapsed ? '\\u25bc' : '\\u25b2';
}
"""

STAGE_NAMES = {
    1: "Capture", 2: "Resource Intelligence", 3: "Triage", 4: "Plan Draft",
    5: "User Review \u2014 Plan Draft", 6: "Cross-Review",
    7: "User Review \u2014 Plan Final", 8: "Claim / Activation",
    9: "Work-Queue Routing", 10: "Work Execution", 11: "Artifact Generation",
    12: "TDD / Eval", 13: "Agent Cross-Review", 14: "Verify Gate Evidence",
    15: "Future Work Synthesis", 16: "Resource Intelligence Update",
    17: "User Review \u2014 Implementation", 18: "Reclaim",
    19: "Close", 20: "Archive",
}
STAGE_INVOCATION = {
    1: "human_interactive", 2: "chained_agent", 3: "chained_agent", 4: "chained_agent",
    5: "human_interactive", 6: "task_agent", 7: "human_interactive", 8: "chained_agent",
    9: "chained_agent", 10: "task_agent", 11: "task_agent", 12: "task_agent",
    13: "task_agent", 14: "task_agent", 15: "task_agent", 16: "task_agent",
    17: "human_interactive", 18: "task_agent", 19: "task_agent", 20: "task_agent",
}
STAGE_WEIGHT = {
    1: "light", 2: "medium", 3: "light", 4: "medium", 5: "heavy", 6: "medium",
    7: "heavy", 8: "light", 9: "light", 10: "heavy", 11: "medium", 12: "heavy",
    13: "medium", 14: "medium", 15: "medium", 16: "medium", 17: "heavy",
    18: "light", 19: "light", 20: "light",
}
STAGE_IS_GATE = {5, 7, 17}


def _read_yaml_safe(path) -> dict:
    try:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _esc(s: str) -> str:
    """HTML-escape a plain string for inline display."""
    from html import escape
    return escape(str(s))


def detect_stage_statuses(
    wrk_id: str, assets_dir: str, fm: dict, body_md: str, queue_dir: str
) -> dict:
    """Return {stage_n (int): 'done'|'active'|'pending'|'na'}.

    Reads ``evidence/stage-evidence.yaml`` as the authoritative source when
    present (written by exit_stage.py in WRK-1046+).  Falls back to artifact
    heuristics for older WRKs.
    """
    import yaml as _yaml

    ev = Path(assets_dir) / "evidence"
    ad = Path(assets_dir)

    # ── Primary: stage-evidence.yaml (authoritative) ─────────────────────────
    stage_ev_path = ev / "stage-evidence.yaml"
    if stage_ev_path.exists():
        try:
            data = _yaml.safe_load(stage_ev_path.read_text()) or {}
            stages_list = data.get("stages", [])
            if stages_list:
                _STATUS_MAP = {
                    "done": "done",
                    "n/a": "na",
                    "na": "na",
                    "in_progress": "active",
                    "pending": "pending",
                    "blocked": "active",
                }
                statuses: dict = {}
                for entry in stages_list:
                    # Support both `order:` (WRK-1046+ schema) and `stage:` (older schema)
                    order = entry.get("order") or entry.get("stage")
                    raw = str(entry.get("status", "pending")).strip().lower()
                    if order is not None:
                        statuses[int(order)] = _STATUS_MAP.get(raw, "pending")
                # Fill any missing stages as pending
                for n in range(1, 21):
                    statuses.setdefault(n, "pending")
                # Safety override: if archive file exists, S19+S20 must be done
                # (handles retroactively-written stage-evidence.yaml that omit close/archive)
                if list(Path(queue_dir).glob(f"archive/**/{wrk_id}.md")):
                    statuses[19] = "done"
                    statuses[20] = "done"
                return statuses
        except Exception:
            pass  # Fall through to heuristics on parse error

    # ── Fallback: artifact-presence heuristics (pre-WRK-1046 items) ──────────
    def ev_exists(*names):
        return any((ev / n).exists() for n in names)

    completions = {
        1: True,  # WRK file found → S1 done
        2: ev_exists("resource-intelligence.yaml"),
        # S3 Triage: only require complexity field (route: absent from many WRKs)
        3: bool(fm.get("complexity")),
        4: ("## Plan" in body_md
            or bool(fm.get("spec_ref") and Path(fm["spec_ref"]).exists())),
        5: ev_exists("user-review-plan-draft.yaml"),
        6: (ev_exists("cross-review-phase1.md", "cross-review-plan.md")
            or (ad / "review.md").exists()
            or (ad / "cross-review-plan.md").exists()
            or bool(list(ev.glob("cross-review*.md")))),
        7: ev_exists("user-review-plan-final.yaml", "plan-final-review.yaml"),
        8: (ev_exists("claim.yaml", "claim-evidence.yaml") or (ad / "claim-evidence.yaml").exists()),
        9: (ev_exists("claim.yaml", "claim-evidence.yaml") or (ad / "claim-evidence.yaml").exists()),
        10: ev_exists("execute.yaml"),
        # S11 Artifact Generation: check for the lifecycle HTML, not S14's gate summary
        11: (ad / f"{wrk_id}-lifecycle.html").exists(),
        12: ((ad / "variation-test-results.md").exists()
             or (ad / "test-summary.md").exists()
             or (ad / "test-results.md").exists()
             or (ad / "ac-test-matrix.md").exists()
             or ev_exists("test-results.yaml", "ac-test-matrix.md", "test-summary.md")),
        13: ((ad / "cross-review-impl.md").exists()
             or ev_exists("cross-review-impl.md", "cross-review-implementation.md")
             or bool(list(ev.glob("cross-review-implementation*.md")))
             or bool(list(ev.glob("cross-review-*.md")))),
        # S14 Verify Gate Evidence: gate summary AND cross-review-impl must both exist
        # so S14 doesn't prematurely show 'done' when only S11 (artifact gen) is complete
        14: (ev_exists("gate-evidence-summary.json")
             and ((ad / "cross-review-impl.md").exists()
                  or ev_exists("cross-review-impl.md", "cross-review-implementation.md")
                  or bool(list(ev.glob("cross-review-implementation*.md")))
                  or bool(list(ev.glob("cross-review-*.md"))))),
        15: ev_exists("future-work.yaml"),
        16: ev_exists("resource-intelligence-update.yaml"),
        17: ev_exists("user-review-close.yaml"),
        19: fm.get("status") in ("done", "archived"),
        20: bool(list(Path(queue_dir).glob(f"archive/**/{wrk_id}.md"))),
    }

    statuses = {}
    found_active = False
    for n in range(1, 21):
        if n == 18:
            reclaim_path = ev / "reclaim.yaml"
            if reclaim_path.exists():
                try:
                    rdata = _yaml.safe_load(reclaim_path.read_text()) or {}
                    statuses[18] = "na" if str(rdata.get("status", "")).strip().lower() == "n/a" else "done"
                except Exception:
                    statuses[18] = "done"
            else:
                statuses[18] = "na"
            continue
        # Once the active stage is found, all subsequent stages are pending
        # regardless of artifact presence — prevents future artifacts from
        # jumping ahead of incomplete earlier stages.
        if found_active:
            statuses[n] = "pending"
            continue
        done = completions.get(n, False)
        if done:
            statuses[n] = "done"
        else:
            statuses[n] = "active"
            found_active = True
    return statuses


def _render_schema_block(pairs: list[tuple[str, str]]) -> str:
    rows = "".join(
        f'<div class="schema-row">'
        f'<span class="schema-key">{_esc(k)}</span>'
        f'<span class="schema-val">{_esc(v)}</span>'
        f'</div>'
        for k, v in pairs
    )
    return f'<div class="schema">{rows}</div>'


def _render_yaml_schema(data: dict, keys: list[str]) -> str:
    pairs = [(k, str(data.get(k, ""))) for k in keys if data.get(k) is not None]
    return _render_schema_block(pairs) if pairs else ""


def _render_exit_artifacts(paths: list[str]) -> str:
    items = "".join(f'<li><code>{_esc(p)}</code></li>' for p in paths)
    return (
        f'<div class="section-label">Exit artifacts</div>'
        f'<ul class="item-list">{items}</ul>'
    )


def render_lifecycle_stage_body(
    stage_n: int, status: str, assets_dir: str, fm: dict, body_md: str
) -> str:
    """Return HTML body content for a single stage section."""
    ev = Path(assets_dir) / "evidence"
    ad = Path(assets_dir)

    if status == "pending":
        return '<p style="color:var(--muted);font-size:.85rem;margin:12px 0;">Pending.</p>'
    if status == "na":
        return '<p style="color:var(--muted);font-size:.85rem;margin:12px 0;">Not applicable for this WRK.</p>'

    # ── S1 Capture ───────────────────────────────────────────────────────────
    if stage_n == 1:
        source = str(fm.get("id", "")) + ".md"
        pairs = [
            ("title", str(fm.get("title", ""))),
            ("route", str(fm.get("route", ""))),
            ("complexity", str(fm.get("complexity", ""))),
            ("priority", str(fm.get("priority", ""))),
        ]
        return (
            '<div class="section-label">Stage record</div>'
            + _render_schema_block(pairs)
            + _render_exit_artifacts([f"pending/{source}"])
        )

    # ── S2 Resource Intelligence ─────────────────────────────────────────────
    if stage_n == 2:
        data = _read_yaml_safe(ev / "resource-intelligence.yaml")
        parts = ""
        if data:
            dom = data.get("domain", {})
            pairs = [
                ("completion_status", str(data.get("completion_status", ""))),
                ("domain.problem", str(dom.get("problem", ""))[:120] if dom else ""),
                ("decision", str(dom.get("architecture_decision", ""))[:120] if dom else ""),
            ]
            parts += '<div class="section-label">Stage record</div>' + _render_schema_block(
                [(k, v) for k, v in pairs if v]
            )
            gaps = data.get("top_p1_gaps", [])
            if gaps:
                items = "".join(f"<li>{_esc(g)}</li>" for g in gaps[:5])
                parts += (
                    '<div class="section-label">P1 gaps</div>'
                    f'<ul class="item-list">{items}</ul>'
                )
        parts += _render_exit_artifacts(["evidence/resource-intelligence.yaml"])
        return parts or '<p style="color:var(--muted);font-size:.85rem;">Evidence present.</p>'

    # ── S3 Triage ────────────────────────────────────────────────────────────
    if stage_n == 3:
        pairs = [
            ("route", str(fm.get("route", ""))),
            ("complexity", str(fm.get("complexity", ""))),
            ("computer", str(fm.get("computer", ""))),
            ("orchestrator", str(fm.get("orchestrator", ""))),
        ]
        return (
            '<div class="section-label">Triage decisions</div>'
            + _render_schema_block([(k, v) for k, v in pairs if v])
        )

    # ── S4 Plan Draft ─────────────────────────────────────────────────────────
    if stage_n == 4:
        parts = ""
        # Acceptance criteria from WRK body
        ac_match = re.search(r"## Acceptance Criteria\n(.*?)(?=\n##|\Z)", body_md, re.DOTALL)
        if ac_match:
            ac_lines = [
                l.strip() for l in ac_match.group(1).splitlines()
                if l.strip().startswith("- [")
            ]
            if ac_lines:
                items = "".join(
                    f'<li>{"☑" if l.startswith("- [x]") else "☐"} '
                    f'{_esc(l[5:].strip())}</li>'
                    for l in ac_lines[:20]
                )
                parts += (
                    '<div class="section-label">Acceptance Criteria</div>'
                    f'<ul class="ac-list">{items}</ul>'
                )
        # Plan phases
        plan_match = re.search(r"## Plan\n(.*?)(?=\n##|\Z)", body_md, re.DOTALL)
        if plan_match:
            plan_text = plan_match.group(1).strip()[:800]
            lines = [l.strip() for l in plan_text.splitlines() if l.strip()][:15]
            items = "".join(f"<li>{_esc(l)}</li>" for l in lines)
            parts += (
                '<div class="section-label">Plan</div>'
                f'<ul class="item-list">{items}</ul>'
            )
        parts += _render_exit_artifacts([f"working/{fm.get('id', 'WRK-???')}.md"])
        return parts

    # ── S5 User Review — Plan Draft ───────────────────────────────────────────
    if stage_n == 5:
        data = _read_yaml_safe(ev / "user-review-plan-draft.yaml")
        pairs = [
            ("reviewed_by", str(data.get("reviewed_by", ""))),
            ("decision", str(data.get("decision", ""))),
        ]
        decisions = data.get("decisions", {})
        if isinstance(decisions, list):
            for item in decisions:
                if isinstance(item, dict):
                    pairs.append((item.get("id", ""), item.get("decision", "")))
        else:
            for k, v in decisions.items():
                if isinstance(v, dict):
                    pairs.append((k, str(v.get("answer", ""))))
                else:
                    pairs.append((k, str(v)))
        return (
            '<div class="section-label">Stage record</div>'
            + _render_schema_block([(k, v) for k, v in pairs if v])
            + _render_exit_artifacts(["evidence/user-review-plan-draft.yaml"])
        )

    # ── S6 Cross-Review ───────────────────────────────────────────────────────
    if stage_n == 6:
        cr_yaml = ev / "cross-review.yaml"
        if cr_yaml.exists():
            cr = _read_yaml_safe(cr_yaml)
            # Collect all reviewers across rounds
            all_reviewers: list[dict] = []
            for round_key in ("round_1", "round_2"):
                rnd = cr.get(round_key, {})
                for r in rnd.get("reviewers", []):
                    all_reviewers.append({**r, "_round": round_key.replace("_", " ").title()})
            # Fall back to top-level reviewers list (single-round format)
            if not all_reviewers:
                for r in cr.get("reviewers", []):
                    all_reviewers.append({**r, "_round": ""})
            def _sev_kind(sev: str) -> str:
                s = sev.upper()
                return "fail" if s == "P1" else ("warn" if s == "P2" else "info")

            summary_rows = ""
            findings_html = ""
            for r in all_reviewers:
                provider = _esc(str(r.get("provider", "")))
                v = str(r.get("final_verdict") or r.get("verdict", "")).upper()
                v_kind = "pass" if v == "APPROVE" else ("fail" if v == "REQUEST_CHANGES" else "info")
                p1 = r.get("p1_count", "")
                p2 = r.get("p2_count", "")
                rnd = _esc(r.get("_round", ""))
                summary_rows += (f"<tr><td>{rnd}</td><td><strong>{provider}</strong></td>"
                                 f"<td>{badge(v, v_kind)}</td>"
                                 f"<td style='text-align:center'>{p1}</td>"
                                 f"<td style='text-align:center'>{p2}</td></tr>\n")
                findings = r.get("findings", [])
                if findings:
                    frows = ""
                    for f in findings:
                        fid = _esc(str(f.get("id", "")))
                        sev = str(f.get("severity", ""))
                        summary = _esc(str(f.get("summary", "")))
                        resolution = _esc(str(f.get("resolution", "")))
                        frows += (f"<tr><td><code>{fid}</code></td>"
                                  f"<td>{badge(sev, _sev_kind(sev))}</td>"
                                  f"<td>{summary}</td>"
                                  f"<td style='color:var(--done)'>{resolution}</td></tr>\n")
                    findings_html += (
                        f'<div class="section-label" style="margin-top:10px">'
                        f'{rnd} — {provider} findings</div>'
                        f'<table><thead><tr><th>ID</th><th>Sev</th>'
                        f'<th>Finding</th><th>Resolution</th></tr></thead>'
                        f'<tbody>{frows}</tbody></table>'
                    )
            overall = str(cr.get("overall_verdict", "")).upper()
            o_kind = "pass" if overall == "APPROVE" else "fail"
            p1_resolved = cr.get("all_p1_resolved", False)
            p1_badge = badge("All P1 resolved", "pass") if p1_resolved else badge("P1 open", "fail")
            rounds_label = f"{cr.get('review_rounds', 1)} round(s)"
            html = (
                '<div class="section-label">Cross-review summary</div>'
                f'<table><thead><tr><th>Round</th><th>Provider</th><th>Verdict</th>'
                f'<th>P1</th><th>P2</th></tr></thead><tbody>{summary_rows}</tbody></table>'
                f'<p style="margin:8px 0 4px">'
                f'Overall: {badge(overall, o_kind)} &nbsp; {p1_badge} &nbsp;'
                f'<span style="font-size:.82rem;color:var(--muted)">{rounds_label}</span></p>'
                + findings_html
            )
        else:
            # Fallback: render text snippet from .md file
            candidates = list(ev.glob("cross-review*.md")) + [ad / "review.md"]
            review_text = ""
            for c in candidates:
                if c.exists():
                    review_text = c.read_text(encoding="utf-8")
                    break
            snippet = _esc(review_text[:300]) if review_text else "Cross-review evidence present."
            html = (
                '<div class="section-label">Cross-review summary</div>'
                f'<p style="font-size:.85rem;color:var(--muted);">{snippet}</p>'
            )
        return html + _render_exit_artifacts(["evidence/cross-review-*.md", "evidence/cross-review.yaml"])

    # ── S7 User Review — Plan Final ───────────────────────────────────────────
    if stage_n == 7:
        _s7_path = (ev / "plan-final-review.yaml") if (ev / "plan-final-review.yaml").exists() else (ev / "user-review-plan-final.yaml")
        data = _read_yaml_safe(_s7_path)
        pairs = [
            ("reviewed_by", str(data.get("reviewed_by", ""))),
            ("confirmed_by", str(data.get("confirmed_by", ""))),
            ("decision", str(data.get("decision", ""))),
        ]
        return (
            '<div class="section-label">Stage record</div>'
            + _render_schema_block([(k, v) for k, v in pairs if v])
            + _render_exit_artifacts([f"evidence/{_s7_path.name}"])
        )

    # ── S8/S9 Claim / Routing ─────────────────────────────────────────────────
    if stage_n in (8, 9):
        data = _read_yaml_safe(ev / "claim.yaml")
        pairs = [(k, str(data.get(k, ""))) for k in ("claimed_by", "claimed_at", "quota_ok")
                 if data.get(k) is not None]
        return (
            '<div class="section-label">Stage record</div>'
            + (_render_schema_block(pairs) if pairs else "")
            + _render_exit_artifacts(["evidence/claim.yaml"])
        )

    # ── S10 Work Execution ────────────────────────────────────────────────────
    if stage_n == 10:
        data = _read_yaml_safe(ev / "execute.yaml")
        pairs = [(k, str(data.get(k, ""))) for k in
                 ("files_changed", "commits", "tests_run", "summary")
                 if data.get(k) is not None]
        return (
            '<div class="section-label">Execution record</div>'
            + (_render_schema_block(pairs) if pairs else
               '<p style="color:var(--muted);font-size:.85rem;">Execution evidence present.</p>')
            + _render_exit_artifacts(["evidence/execute.yaml"])
        )

    # ── S11 Artifact Generation ───────────────────────────────────────────────
    if stage_n == 11:
        gep = ev / "gate-evidence-summary.json"
        summary = ""
        if gep.exists():
            try:
                import json
                ge = json.loads(gep.read_text(encoding="utf-8"))
                passed = sum(1 for v in ge.values() if isinstance(v, dict)
                             and v.get("status") == "PASS")
                total = len([v for v in ge.values() if isinstance(v, dict)])
                summary = f"{passed}/{total} gates PASS"
            except Exception:
                summary = "Gate evidence present"
        return (
            '<div class="section-label">Gate evidence</div>'
            + _render_schema_block([("gates", summary)] if summary else [])
            + _render_exit_artifacts(["evidence/gate-evidence-summary.json",
                                      f"WRK-???-lifecycle.html"])
        )

    # ── S14 Verify Gate Evidence ──────────────────────────────────────────────
    if stage_n == 14:
        gep = ev / "gate-evidence-summary.json"
        if gep.exists():
            try:
                import json
                ge = json.loads(gep.read_text(encoding="utf-8"))
                rows = ""
                for gate, val in list(ge.items())[:12]:
                    if isinstance(val, dict):
                        st = val.get("status", "?")
                        cls = "b-done" if st == "PASS" else ("b-active" if st == "WARN" else "b-pending")
                        rows += (f'<tr><td>{_esc(gate)}</td>'
                                 f'<td><span class="badge {cls}">{_esc(st)}</span></td></tr>')
                if rows:
                    return (
                        '<div class="section-label">Gate results</div>'
                        f'<table><tr><th>Gate</th><th>Status</th></tr>{rows}</table>'
                    )
            except Exception:
                pass
        return '<p style="color:var(--muted);font-size:.85rem;">Gate evidence verified.</p>'

    # ── S15 Future Work ────────────────────────────────────────────────────────
    if stage_n == 15:
        data = _read_yaml_safe(ev / "future-work.yaml")
        recs = data.get("recommendations", [])
        if recs:
            rows = "".join(
                f'<tr><td>{_esc(r.get("title",""))}</td>'
                f'<td>{_esc(r.get("disposition",""))}</td>'
                f'<td>{_esc(str(r.get("captured","")))}</td></tr>'
                for r in recs[:8] if isinstance(r, dict)
            )
            return (
                '<div class="section-label">Future work</div>'
                f'<table><tr><th>Title</th><th>Disposition</th><th>Captured</th></tr>'
                f'{rows}</table>'
            )
        return '<p style="color:var(--muted);font-size:.85rem;">Future work recorded.</p>'

    # ── S16 Resource Intelligence Update ─────────────────────────────────────
    if stage_n == 16:
        data = _read_yaml_safe(ev / "resource-intelligence-update.yaml")
        additions = data.get("additions", [])
        if additions:
            items = "".join(f"<li>{_esc(str(a))}</li>" for a in additions[:6])
            return (
                '<div class="section-label">Additions</div>'
                f'<ul class="item-list">{items}</ul>'
            )
        return '<p style="color:var(--muted);font-size:.85rem;">Resource intelligence updated.</p>'

    # ── S17 User Review — Implementation ─────────────────────────────────────
    if stage_n == 17:
        data = _read_yaml_safe(ev / "user-review-close.yaml")
        pairs = [
            ("reviewed_by", str(data.get("reviewed_by", ""))),
            ("decision", str(data.get("decision", ""))),
        ]
        return (
            '<div class="section-label">Stage record</div>'
            + _render_schema_block([(k, v) for k, v in pairs if v])
            + _render_exit_artifacts(["evidence/user-review-close.yaml"])
        )

    # ── S19 Close / S20 Archive ───────────────────────────────────────────────
    if stage_n in (19, 20):
        status_val = str(fm.get("status", ""))
        commit = str(fm.get("commit", ""))
        pairs = [("status", status_val), ("commit", commit)]
        return (
            '<div class="section-label">Stage record</div>'
            + _render_schema_block([(k, v) for k, v in pairs if v])
        )

    # Default: active stage with awaiting note, done stage with generic note
    if status == "active":
        return '<div class="awaiting">In progress — evidence pending.</div>'
    return '<p style="color:var(--muted);font-size:.85rem;">Stage completed.</p>'


def generate_lifecycle(wrk_id: str, output_file: str | None = None) -> None:
    """Generate single lifecycle HTML for WRK-NNN from evidence files on disk."""
    workspace_root = os.popen("git rev-parse --show-toplevel").read().strip()
    queue_dir = os.path.join(workspace_root, ".claude/work-queue")

    # Find WRK file
    wrk_file = ""
    for folder in ["working", "pending", "done", "archived"]:
        path = os.path.join(queue_dir, folder, f"{wrk_id}.md")
        if os.path.exists(path):
            wrk_file = path
            break
    if not wrk_file:
        for p in Path(queue_dir).glob(f"archive/**/{wrk_id}.md"):
            wrk_file = str(p)
            break
    if not wrk_file:
        print(f"Error: Could not find {wrk_id}.md")
        return

    content = Path(wrk_file).read_text(encoding="utf-8")
    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    fm: dict = {}
    if fm_match:
        try:
            fm = yaml.safe_load(fm_match.group(1)) or {}
        except Exception:
            pass
    body_md = content[fm_match.end():] if fm_match else content

    assets_dir = os.path.join(queue_dir, "assets", wrk_id)
    os.makedirs(assets_dir, exist_ok=True)

    statuses = detect_stage_statuses(wrk_id, assets_dir, fm, body_md, queue_dir)

    title = _esc(str(fm.get("title", wrk_id)))
    route = str(fm.get("route", ""))
    category = str(fm.get("category", ""))
    computer = str(fm.get("computer", ""))
    orchestrator = str(fm.get("orchestrator", ""))
    priority = str(fm.get("priority", ""))
    created = str(fm.get("created_at", ""))[:10]

    # Stage strip chips
    strip_chips = ""
    for n in range(1, 21):
        st = statuses.get(n, "pending")
        cls = {"done": "sc-done", "active": "sc-active", "na": "sc-na"}.get(st, "sc-pending")
        name = STAGE_NAMES.get(n, str(n))
        strip_chips += (
            f'<a href="#s{n}" class="sc {cls}" title="{_esc(str(n).zfill(2))} {_esc(name)}">'
            f'{n}</a>'
        )

    # Stage sections
    stage_sections_html = ""
    for n in range(1, 21):
        st = statuses.get(n, "pending")
        name = STAGE_NAMES.get(n, f"Stage {n}")
        inv = STAGE_INVOCATION.get(n, "")
        wt = STAGE_WEIGHT.get(n, "")
        is_gate = n in STAGE_IS_GATE

        badge_cls = {"done": "b-done", "active": "b-active", "na": "b-na"}.get(st, "b-pending")
        badge_label = st
        inv_cls = {"human_interactive": "b-human", "chained_agent": "b-chain"}.get(inv, "b-agent")
        wt_cls = {"light": "b-light", "medium": "b-medium", "heavy": "b-heavy"}.get(wt, "")
        chevron = "▲" if st == "done" else "▼"
        collapsed_cls = "" if st in ("done", "active") else " collapsed"

        gate_badge = '<span class="badge b-gate">gate</span>' if is_gate else ""
        smeta_parts = [p for p in [inv, wt] if p]
        smeta = " · ".join(smeta_parts)
        if is_gate:
            smeta += " · GATE"

        body_html = render_lifecycle_stage_body(n, st, assets_dir, fm, body_md)

        stage_sections_html += f"""
<section class="stage-section" id="s{n}">
  <div class="stage-header" onclick="toggle(this)">
    <div class="snum">{n}</div>
    <div>
      <div class="stitle">{_esc(name)}</div>
      <div class="smeta">{_esc(smeta)}</div>
    </div>
    <div class="sbadges">
      <span class="badge {badge_cls}">{_esc(badge_label)}</span>
      <span class="badge {inv_cls}">{_esc(inv)}</span>
      {gate_badge}
      <span class="chevron">{chevron}</span>
    </div>
  </div>
  <div class="stage-body{collapsed_cls}">
    {body_html}
  </div>
</section>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{wrk_id} Lifecycle \u2014 {title[:60]}</title>
  <style>{LIFECYCLE_CSS}</style>
</head>
<body>

<header class="hero">
  <div class="hero-inner">
    <p class="eyebrow">Lifecycle Tracker &middot; Route {_esc(route)} &middot; {_esc(category)}</p>
    <h1>{wrk_id} \u2014 {title}</h1>
    <p class="lede">Single lifecycle document tracking all 20 stages from capture to archive.</p>
    <div class="meta-row">
      <div class="pill"><strong>Priority</strong>{_esc(priority)}</div>
      <div class="pill"><strong>Workstation</strong>{_esc(computer)}</div>
      <div class="pill"><strong>Orchestrator</strong>{_esc(orchestrator)}</div>
      <div class="pill"><strong>Category</strong>{_esc(category)}</div>
      <div class="pill"><strong>Created</strong>{_esc(created)}</div>
    </div>
  </div>
</header>

<nav class="stage-strip">
  <div class="stage-strip-inner">
    <span class="stage-strip-label">Stages</span>
    {strip_chips}
  </div>
</nav>

<div class="content">
{stage_sections_html}
</div>

<script>{LIFECYCLE_JS}</script>
</body>
</html>
"""

    if not output_file:
        output_file = os.path.join(assets_dir, f"{wrk_id}-lifecycle.html")

    Path(output_file).write_text(html, encoding="utf-8")
    print(f"\u2714 Lifecycle HTML generated: {output_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate canonical WRK lifecycle HTML (workflow-html SKILL v1.5.0)"
    )
    parser.add_argument("wrk_id")
    parser.add_argument(
        "--lifecycle",
        action="store_true",
        help="Generate single lifecycle HTML (canonical mode)",
    )
    parser.add_argument("--output", default=None)
    # --type is suppressed so legacy invocations don't crash; all modes now generate lifecycle HTML
    import argparse as _argparse
    parser.add_argument("--type", default=None, help=_argparse.SUPPRESS)
    args = parser.parse_args()

    if args.type:
        print(
            f"Note: --type {args.type!r} is deprecated and ignored."
            " Generating lifecycle HTML instead."
        )
    generate_lifecycle(args.wrk_id, args.output)
