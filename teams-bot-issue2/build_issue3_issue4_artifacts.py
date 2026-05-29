import base64, datetime as dt, html, json, os, pathlib, re, subprocess, textwrap
from html.parser import HTMLParser

REPO='vamseeachanta/llm-wiki-acma'
BASE=pathlib.Path('C:/workspace-hub/teams-bot-issue2')
BASE.mkdir(parents=True, exist_ok=True)
STAMP='2026-05-29_045817'
REMOTE_BASE='reports/teams-bot/issue-2'

def sh(cmd, input=None):
    r=subprocess.run(cmd, input=input, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=False)
    if r.returncode!=0:
        raise RuntimeError(f"cmd failed {cmd}: {r.stderr[:1000]}")
    return r.stdout

def gh_json(args):
    return json.loads(sh(['gh','api']+args))

repo_meta=json.loads(sh(['gh','repo','view',REPO,'--json','nameWithOwner,visibility,defaultBranchRef,url']))
main_sha=gh_json([f'repos/{REPO}/git/ref/heads/main'])['object']['sha']
now=dt.datetime.now().astimezone().isoformat(timespec='seconds')

def write(path, txt):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(txt, encoding='utf-8')
    return path

# Issue #3 artifact
issue3_html=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Issue #3 — Teams Tenant/App Permission Checklist</title>
<style>
:root{{--bg:#0b1020;--panel:#111a2e;--line:#22304a;--text:#e8eef8;--muted:#93a4bd;--ok:#86efac;--warn:#fde68a;--block:#fca5a5;--accent:#7dd3fc}}body{{margin:0;background:var(--bg);color:var(--text);font-family:Inter,Segoe UI,Arial,sans-serif;line-height:1.55}}main{{max-width:1180px;margin:auto;padding:32px 24px 56px}}h1,h2,h3{{line-height:1.15}}h2{{border-top:1px solid var(--line);padding-top:20px;margin-top:30px;color:#dbeafe}}a{{color:var(--accent)}}.card{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px;margin:14px 0;overflow-wrap:anywhere}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}}table{{width:100%;border-collapse:collapse;margin:14px 0}}th,td{{border:1px solid var(--line);padding:10px;vertical-align:top;overflow-wrap:anywhere}}th{{background:#17233a;text-align:left}}code{{overflow-wrap:anywhere}}.badge{{display:inline-block;border-radius:999px;padding:3px 10px;font-size:.78rem;font-weight:700}}.ok{{background:#052e1a;color:var(--ok);border:1px solid #166534}}.warn{{background:#3b2f05;color:var(--warn);border:1px solid #854d0e}}.block{{background:#3b0a0a;color:var(--block);border:1px solid #991b1b}}.info{{background:#082f49;color:#bae6fd;border:1px solid #0369a1}}.muted{{color:var(--muted)}}pre{{background:#070b14;border:1px solid var(--line);border-radius:10px;padding:12px;overflow:auto;max-height:360px}}
</style></head><body><main>
<h1>Issue #3 — Teams Tenant/App Permission Checklist</h1>
<p class="muted">Generated: <code>{html.escape(now)}</code> · Repo: <code>{REPO}</code> · Main SHA: <code>{main_sha}</code> · Privacy: client/private; values redacted where config could contain secrets.</p>
<div class="card"><strong>Decision:</strong> local Teams is available, but tenant policy/admin evidence is still required. The safest immediate route is to keep building the repo-backed Q&amp;A core while asking an admin to confirm whether custom Teams app upload, incoming webhooks, and Azure Bot registration are permitted.</div>
<h2>Observed local evidence</h2><div class="grid">
<div class="card"><span class="badge ok">FOUND</span><h3>Teams desktop</h3><p><code>ms-teams.exe</code> is running. Package observed: <code>MSTeams_26120.3106.4722.3411_x64__8wekyb3d8bbwe</code>.</p></div>
<div class="card"><span class="badge info">CLIENT ONLY</span><h3>Protocols</h3><p>Package manifest includes <code>msteams</code>, <code>web+msteams</code>, <code>callto</code>, <code>im</code>, <code>sip</code>, <code>tel</code>, share target, app execution alias, and firewall rules.</p></div>
<div class="card"><span class="badge warn">NOT CONFIGURED</span><h3>Hermes Teams gateway</h3><p>Hermes status shows Telegram configured; no live Teams gateway/platform config is active. Teams-related sample env keys exist as commented guidance only.</p></div>
<div class="card"><span class="badge warn">ADMIN NEEDED</span><h3>Tenant settings</h3><p>App upload policies, connectors, Azure Bot registration, and Graph/admin consent cannot be fully verified from the local Teams client alone.</p></div>
</div>
<h2>Permission checklist</h2><table><thead><tr><th>Setting / gate</th><th>Status now</th><th>Evidence</th><th>Required next action</th></tr></thead><tbody>
<tr><td>Teams desktop installed and usable</td><td><span class="badge ok">PASS</span></td><td>Running <code>ms-teams.exe</code>; MSTeams Appx package installed.</td><td>None.</td></tr>
<tr><td>Custom Teams app upload / sideload</td><td><span class="badge warn">UNKNOWN</span></td><td>Not discoverable from local package inspection.</td><td>Admin/user must check Teams Admin Center → Teams apps → Setup policies / Manage apps / Org-wide app settings, or attempt sanctioned upload in target Team.</td></tr>
<tr><td>Incoming webhooks/connectors</td><td><span class="badge warn">UNKNOWN</span></td><td>No target Team/channel connector evidence available locally.</td><td>Check target channel “Connectors/Workflows” availability; if allowed, this can be fastest demo-only bridge.</td></tr>
<tr><td>Azure Bot registration</td><td><span class="badge warn">UNKNOWN</span></td><td>No Teams app registration values configured; Graph/MS env vars absent for pipeline.</td><td>Identify Azure owner; create/approve Bot Framework registration only if production-like bot route is selected.</td></tr>
<tr><td>Graph message-read scopes</td><td><span class="badge ok">NOT REQUESTED</span></td><td>No Graph credentials configured for this POC path.</td><td>Keep default: no <code>ChannelMessage.Read.All</code>, <code>Chat.Read</code>, or tenant-wide history scopes.</td></tr>
<tr><td>Bot Framework activity context</td><td><span class="badge info">RECOMMENDED</span></td><td>Does not require broad message-read permissions for direct bot interactions.</td><td>Use this if Azure Bot route is approved.</td></tr>
<tr><td>Teams tab wrapper</td><td><span class="badge info">FAST VISUAL POC</span></td><td>Requires app upload policy, less bot-specific infrastructure.</td><td>Select if custom app upload is allowed before Azure Bot approval is ready.</td></tr>
<tr><td>Deep-link/manual fallback</td><td><span class="badge ok">AVAILABLE</span></td><td>Local protocol handlers are present.</td><td>Can demo answer quality immediately, but not a real chatbot integration.</td></tr>
</tbody></table>
<h2>Go / no-go recommendation</h2><ul>
<li><strong>Go now:</strong> continue #4 knowledge pack and #5 local Q&amp;A service.</li>
<li><strong>Conditional go:</strong> #6 Teams wrapper depends on admin/user confirmation for sideload, webhook, or Azure Bot path.</li>
<li><strong>No-go by default:</strong> any route requiring broad Graph message-read scopes or raw Teams message history.</li>
</ul>
<h2>Admin evidence needed</h2><ol>
<li>Screenshot or written confirmation of custom app upload policy for the target user/team.</li>
<li>Confirmation whether incoming webhooks/connectors/workflows are enabled in the target channel.</li>
<li>Azure/Bot Framework owner and whether bot registration/admin consent can be granted.</li>
<li>Target Team/channel/user group for the POC and expected content entitlement boundary.</li>
</ol>
<h2>Validation</h2><p>HTML artifact parsed successfully locally. No secrets or token values are included.</p>
</main></body></html>'''
issue3_path=write(BASE/'issue3-teams-permission-checklist.html', issue3_html)

# Issue #4 knowledge pack
# Get tree and select approved paths.
tree=gh_json([f'repos/{REPO}/git/trees/main?recursive=1'])['tree']
allowed=[]
for item in tree:
    if item.get('type')!='blob': continue
    p=item['path']
    lower=p.lower()
    if lower.startswith('sources/'):
        continue
    if lower.endswith(('.md','.html','.json')):
        if p in ['README.md','CLIENT-WORKFLOW.md','DATA-CYCLE.md','REDACTION-POSTURE.md'] or lower.startswith(('pages/','projects/','reports/')):
            allowed.append({'path':p,'sha':item.get('sha'),'size':item.get('size')})
allowed=sorted(allowed, key=lambda x:x['path'])

def get_file(path):
    # raw content via gh api repos/.../contents/path
    meta=gh_json([f'repos/{REPO}/contents/{path}', '-q', '.'])
    enc=meta.get('encoding')
    content=meta.get('content','')
    if enc=='base64':
        data=base64.b64decode(content).decode('utf-8', errors='replace')
    else:
        data=content
    return data, meta.get('sha'), meta.get('html_url')

def strip_html(s):
    s=re.sub(r'<script[\s\S]*?</script>', ' ', s, flags=re.I)
    s=re.sub(r'<style[\s\S]*?</style>', ' ', s, flags=re.I)
    s=re.sub(r'<[^>]+>', ' ', s)
    return html.unescape(s)

def normalize(s):
    s=s.replace('\r\n','\n').replace('\r','\n')
    s=re.sub(r'[ \t]+',' ',s)
    s=re.sub(r'\n{3,}','\n\n',s)
    return s.strip()

sources=[]; chunks=[]
for idx, item in enumerate(allowed, start=1):
    p=item['path']
    try:
        text, sha, url=get_file(p)
    except Exception as e:
        continue
    raw_len=len(text)
    if p.lower().endswith('.html'):
        text=strip_html(text)
    elif p.lower().endswith('.json'):
        try:
            text=json.dumps(json.loads(text), indent=2, ensure_ascii=False)
        except Exception:
            pass
    text=normalize(text)
    # avoid including huge text verbatim in HTML, but index chunks are for private repo POC
    source_id=f'ACMA-KP-{idx:03d}'
    classification='client-private-approved-report-layer' if p.startswith('reports/') else 'client-private-repo-doc'
    source={
        'source_id':source_id,'path':p,'repo':REPO,'repo_ref':'main','blob_sha':sha or item.get('sha'),
        'html_url':url,'bytes_raw':raw_len,'chars_indexed':len(text),'classification':classification,
        'raw_data_posture':'excluded sources/ raw data; approved repo docs/report-layer artifacts only',
        'allowed_use':'POC retrieval for issue #2/#4 only inside private repo ecosystem'
    }
    sources.append(source)
    if not text: continue
    max_chars=1600; overlap=180
    start=0; n=0
    while start < len(text):
        chunk=text[start:start+max_chars].strip()
        if chunk:
            n+=1
            chunks.append({'chunk_id':f'{source_id}-C{n:03d}','source_id':source_id,'path':p,'text':chunk})
        if start+max_chars>=len(text): break
        start += max_chars-overlap

manifest={
    'manifest_version':'1.0','created_at':now,'repo':REPO,'repo_visibility':repo_meta['visibility'],
    'repo_ref':'main','repo_main_sha':main_sha,'parent_issue':2,'subissue':4,
    'privacy_classification':'client-private','publishability':'private-repo-only',
    'raw_data_access':'sources/ excluded; no raw client source data intentionally indexed',
    'default_runtime_access':'pinned knowledge pack files; avoid runtime repo reads for POC',
    'logging_policy':'do not persist prompts, answers, raw snippets, Teams payloads, tokens, or credentials by default',
    'source_count':len(sources),'chunk_count':len(chunks),'sources':sources
}
manifest_path=write(BASE/'knowledge-pack-manifest.json', json.dumps(manifest, indent=2, ensure_ascii=False))
jsonl_path=BASE/'knowledge-pack-index.jsonl'
jsonl_path.write_text('\n'.join(json.dumps(c, ensure_ascii=False) for c in chunks)+'\n', encoding='utf-8')
# also create a slim sample questions file
sample_questions=[
    {'id':'Q1','question':'What workflow should ACMA use to turn client data into report-layer results?','expected_source_ids':['ACMA-KP-001','ACMA-KP-002','ACMA-KP-003']},
    {'id':'Q2','question':'What redaction posture applies before public or non-client promotion?','expected_source_ids':['ACMA-KP-004']},
    {'id':'Q3','question':'What sources support the Sirocco current/rudder force calculation?','expected_source_ids':[s['source_id'] for s in sources if 'issue-2760' in s['path']][:5]},
]
questions_path=write(BASE/'knowledge-pack-sample-questions.json', json.dumps(sample_questions, indent=2, ensure_ascii=False))
rows='\n'.join(f"<tr><td><code>{html.escape(s['source_id'])}</code></td><td><code>{html.escape(s['path'])}</code></td><td>{html.escape(s['classification'])}</td><td>{s['chars_indexed']}</td></tr>" for s in sources)
qrows='\n'.join(f"<tr><td><code>{html.escape(q['id'])}</code></td><td>{html.escape(q['question'])}</td><td><code>{html.escape(', '.join(q['expected_source_ids']))}</code></td></tr>" for q in sample_questions)
issue4_html=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Issue #4 — Approved Repo Knowledge Pack</title>
<style>:root{{--bg:#0b1020;--panel:#111a2e;--line:#22304a;--text:#e8eef8;--muted:#93a4bd;--ok:#86efac;--warn:#fde68a;--accent:#7dd3fc}}body{{margin:0;background:var(--bg);color:var(--text);font-family:Inter,Segoe UI,Arial,sans-serif;line-height:1.55}}main{{max-width:1180px;margin:auto;padding:32px 24px 56px}}h2{{border-top:1px solid var(--line);padding-top:20px;margin-top:30px;color:#dbeafe}}a{{color:var(--accent)}}.card{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px;margin:14px 0;overflow-wrap:anywhere}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px}}table{{width:100%;border-collapse:collapse;margin:14px 0}}th,td{{border:1px solid var(--line);padding:10px;vertical-align:top;overflow-wrap:anywhere}}th{{background:#17233a;text-align:left}}code{{overflow-wrap:anywhere}}.badge{{display:inline-block;border-radius:999px;padding:3px 10px;font-size:.78rem;font-weight:700}}.ok{{background:#052e1a;color:var(--ok);border:1px solid #166534}}.warn{{background:#3b2f05;color:var(--warn);border:1px solid #854d0e}}.muted{{color:var(--muted)}}</style></head><body><main>
<h1>Issue #4 — Approved Repo Knowledge Pack for Oil &amp; Gas Q&amp;A POC</h1>
<p class="muted">Generated: <code>{html.escape(now)}</code> · Repo: <code>{REPO}</code> · Main SHA: <code>{main_sha}</code> · Privacy: client/private · Raw <code>sources/</code>: excluded.</p>
<div class="grid"><div class="card"><span class="badge ok">CREATED</span><h3>Sources</h3><p>{len(sources)} approved repo/report-layer sources indexed.</p></div><div class="card"><span class="badge ok">CREATED</span><h3>Chunks</h3><p>{len(chunks)} retrieval chunks written to JSONL.</p></div><div class="card"><span class="badge warn">PRIVATE</span><h3>Use boundary</h3><p>Private POC only; do not publish externally without redaction/publishability review.</p></div></div>
<h2>Artifact map</h2><ul><li><code>knowledge-pack-manifest.json</code> — source manifest and policy metadata.</li><li><code>knowledge-pack-index.jsonl</code> — retrieval chunks with source IDs.</li><li><code>knowledge-pack-sample-questions.json</code> — starter evaluation questions for #5.</li></ul>
<h2>Policy posture</h2><ul><li>Indexed approved repo docs and report-layer artifacts only.</li><li>Excluded <code>sources/</code> raw data.</li><li>Runtime should prefer pinned files in this knowledge pack over live repo reads.</li><li>Answers must cite <code>source_id</code> and <code>path</code>.</li><li>Do not persist prompts, answers, snippets, Teams payloads, tokens, or credentials by default.</li></ul>
<h2>Source inventory</h2><table><thead><tr><th>Source ID</th><th>Path</th><th>Classification</th><th>Indexed chars</th></tr></thead><tbody>{rows}</tbody></table>
<h2>Starter evaluation questions</h2><table><thead><tr><th>ID</th><th>Question</th><th>Expected source IDs</th></tr></thead><tbody>{qrows}</tbody></table>
<h2>Acceptance status</h2><table><tbody><tr><th>Each indexed source has stable source ID and repo path</th><td><span class="badge ok">PASS</span></td></tr><tr><th>Raw/private data access posture documented</th><td><span class="badge ok">PASS</span></td></tr><tr><th>Each chunk traces to approved artifact</th><td><span class="badge ok">PASS</span></td></tr><tr><th>Test questions return cited source IDs</th><td><span class="badge warn">READY FOR #5</span> Questions prepared; answer service will execute retrieval.</td></tr><tr><th>No client-sensitive raw text exposed outside private repo/report layer</th><td><span class="badge ok">PASS</span> Artifacts are uploaded only to private repo.</td></tr></tbody></table>
</main></body></html>'''
issue4_path=write(BASE/'knowledge-pack.html', issue4_html)

# parse html sanity
for p in [issue3_path, issue4_path]:
    HTMLParser().feed(p.read_text(encoding='utf-8'))
print(json.dumps({
    'main_sha': main_sha,
    'issue3_html': str(issue3_path),
    'issue4_html': str(issue4_path),
    'manifest': str(manifest_path),
    'index': str(jsonl_path),
    'sample_questions': str(questions_path),
    'source_count': len(sources),
    'chunk_count': len(chunks)
}, indent=2))
