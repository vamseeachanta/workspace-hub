"""Shared CSS constants for calculation report HTML output.

Extends the workflow-html warm-parchment design system with
calculation-specific styles (equation blocks, pass/fail badges,
chart containers).
"""

# ── Base warm-parchment design system (shared with workflow-html) ───────────
BASE_CSS = """\
:root {
  --bg:         #f3efe6;
  --panel:      #fffdf8;
  --ink:        #172126;
  --muted:      #55636b;
  --accent:     #0f766e;
  --accent-2:   #8a5a2b;
  --line:       #d9d0c0;
  --shadow:     0 16px 40px rgba(20,33,38,0.08);
  --good:       #166534;
  --warn:       #b45309;
  --bad:        #b91c1c;
}
*{box-sizing:border-box;}
body{font-family:Georgia,"Times New Roman",serif;
  background:radial-gradient(circle at top,#fffaf0 0,var(--bg) 48%,#ebe5d7 100%);
  color:var(--ink);line-height:1.55;margin:0;padding:0;}
a{color:var(--accent);text-decoration:none;}
a:hover{text-decoration:underline;}
code{font-family:"SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace;
  background:rgba(27,31,35,0.06);padding:.2em .4em;border-radius:3px;font-size:.88em;}
"""

# ── Hero header ─────────────────────────────────────────────────────────────
HERO_CSS = """\
.hero{padding:28px 24px 20px;border-bottom:1px solid rgba(23,33,38,0.08);
  background:linear-gradient(135deg,rgba(15,118,110,0.07),rgba(138,90,43,0.09));}
.hero-inner{max-width:1100px;margin:0 auto;}
.eyebrow{text-transform:uppercase;letter-spacing:.12em;font-size:.68rem;
  color:var(--accent);font-weight:700;margin:0 0 6px;}
h1.report-title{margin:0 0 8px;font-size:clamp(1.6rem,3vw,2.4rem);line-height:1.1;}
.lede{color:var(--muted);font-size:.92rem;margin:0 0 14px;max-width:72ch;}
"""

# ── Meta chips ──────────────────────────────────────────────────────────────
META_CSS = """\
.meta-chips{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 2px;}
.meta-chip{background:var(--panel);border:1px solid var(--line);border-radius:8px;
  padding:5px 10px;font-size:.8rem;}
.meta-chip strong{font-size:.65rem;text-transform:uppercase;letter-spacing:.07em;
  color:var(--accent-2);display:block;margin-bottom:1px;}
"""

# ── Content layout ──────────────────────────────────────────────────────────
LAYOUT_CSS = """\
.content{max-width:1100px;margin:0 auto;padding:24px 24px 56px;}
.card{background:var(--panel);padding:26px;border-radius:18px;
  box-shadow:var(--shadow);border:1px solid var(--line);margin-bottom:20px;}
.card h2{border-bottom:1px solid var(--line);padding-bottom:.3em;margin-top:0;
  color:var(--accent-2);letter-spacing:.02em;font-size:1.2rem;}
.card p,.card li,.card td,.card th{color:var(--muted);}
.card strong,.card code{color:var(--ink);}
"""

# ── Tables ──────────────────────────────────────────────────────────────────
TABLE_CSS = """\
table{border-collapse:collapse;width:100%;margin:14px 0;font-size:.9rem;}
thead th{background:var(--panel);border-bottom:2px solid var(--accent);
  font-weight:700;text-transform:uppercase;letter-spacing:.06em;
  font-size:.78rem;padding:8px 10px;text-align:left;color:var(--ink);}
tbody td{border-bottom:1px solid var(--line);padding:7px 10px;
  color:var(--muted);vertical-align:top;}
tbody tr:last-child td{border-bottom:none;}
tbody td strong,tbody td code{color:var(--ink);}
tbody tr:hover>td{background:rgba(15,118,110,.03);}
"""

# ── Badges ──────────────────────────────────────────────────────────────────
BADGE_CSS = """\
.badge{display:inline-block;padding:2px 8px;border-radius:999px;
  font-size:.78rem;font-weight:700;text-transform:uppercase;letter-spacing:.06em;
  white-space:nowrap;}
.badge-pass{background:#dcfce7;color:var(--good);}
.badge-fail{background:#fee2e2;color:var(--bad);}
.badge-draft{background:#fef3c7;color:var(--warn);}
.badge-reviewed{background:#dbeafe;color:#1d4ed8;}
.badge-approved{background:#dcfce7;color:var(--good);}
"""

# ── Equations (KaTeX display blocks) ────────────────────────────────────────
EQUATION_CSS = """\
.equation-block{background:#f8f9fa;border:1px solid var(--line);border-radius:10px;
  padding:16px 20px;margin:12px 0;position:relative;}
.equation-block .eq-number{position:absolute;right:16px;top:50%;transform:translateY(-50%);
  font-size:.82rem;color:var(--muted);font-weight:700;}
.equation-name{font-size:.85rem;font-weight:700;color:var(--accent);margin-bottom:6px;}
.equation-desc{font-size:.85rem;color:var(--muted);margin-top:8px;}
.variable-list{margin:8px 0 0;padding:0 0 0 18px;font-size:.82rem;}
.variable-list li{margin:2px 0;color:var(--muted);}
.variable-list li .var-sym{color:var(--ink);font-weight:600;}
"""

# ── Charts ──────────────────────────────────────────────────────────────────
CHART_CSS = """\
.chart-container{margin:16px 0;position:relative;}
.chart-container canvas{max-height:400px;width:100%;}
.chart-title{font-size:.9rem;font-weight:700;color:var(--accent-2);margin-bottom:8px;}
"""

# ── Collapsible sections ───────────────────────────────────────────────────
COLLAPSIBLE_CSS = """\
details{margin:8px 0;}
details summary{cursor:pointer;font-weight:700;color:var(--accent);
  font-size:.9rem;padding:4px 0;}
details summary:hover{text-decoration:underline;}
details[open] summary{margin-bottom:8px;}
"""

# ── Footer ──────────────────────────────────────────────────────────────────
FOOTER_CSS = """\
.report-footer{text-align:center;padding:20px;font-size:.75rem;color:var(--muted);
  border-top:1px solid var(--line);margin-top:40px;}
"""

# ── Print media ─────────────────────────────────────────────────────────────
PRINT_CSS = """\
@media print{
  body{background:#fff;}
  .card{box-shadow:none;border:1px solid #ccc;break-inside:avoid;}
  .hero{background:#f8f8f8;border-bottom:2px solid #333;}
  .chart-container canvas{max-height:300px;}
}
"""

# ── Combined CSS ────────────────────────────────────────────────────────────
FULL_CSS = "\n".join([
    BASE_CSS, HERO_CSS, META_CSS, LAYOUT_CSS, TABLE_CSS,
    BADGE_CSS, EQUATION_CSS, CHART_CSS, COLLAPSIBLE_CSS,
    FOOTER_CSS, PRINT_CSS,
])
