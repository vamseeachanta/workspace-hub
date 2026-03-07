#!/usr/bin/env bash
""":"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
export UV_CACHE_DIR="${UV_CACHE_DIR:-$REPO_ROOT/.claude/state/uv-cache}"
mkdir -p "$UV_CACHE_DIR"
exec uv run --no-project --with markdown --with PyYAML python "$0" "$@"
":"""
"""Generate canonical WRK HTML review artifacts.

Conforms to workflow-html SKILL v1.0.0 (warm-parchment design system,
collapsible cards, sticky TOC, back-to-top button).

Usage:
    generate-html-review.py WRK-NNN [--type plan-draft|plan-final|implementation|close]
                                     [--output <path>]

Legacy positional args still accepted: WRK-NNN [--stage draft] [--type plan]
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


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate canonical WRK HTML review (workflow-html SKILL v1.0.0)"
    )
    parser.add_argument("wrk_id")
    # New canonical flag
    parser.add_argument(
        "--type",
        default="plan-draft",
        choices=["plan-draft", "plan-final", "implementation", "close",
                 # legacy values
                 "plan", "governance"],
        help="Artifact type",
    )
    parser.add_argument("--output", default=None)
    # Legacy compat
    parser.add_argument("--stage", default=None,
                        help="Legacy: draft|final (maps to plan-draft|plan-final)")
    args = parser.parse_args()

    # Map legacy --type plan + --stage draft/final → canonical names
    artifact_type = args.type
    if artifact_type == "plan":
        artifact_type = "plan-final" if args.stage == "final" else "plan-draft"
    elif artifact_type == "governance":
        artifact_type = "close"

    generate_review(args.wrk_id, artifact_type, args.output)
