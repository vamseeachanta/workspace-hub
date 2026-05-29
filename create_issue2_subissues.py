import json, os, subprocess, textwrap, pathlib
repo='vamseeachanta/llm-wiki-acma'
out=pathlib.Path('C:/workspace-hub/issue2_subissues_created.json')
labels=['area:teams-bot','type:poc','status:ready-for-scope','security-review']
# create labels if absent
label_defs={
 'area:teams-bot':('0366d6','Teams bot / Hermes integration workstream'),
 'type:poc':('0e8a16','Proof-of-concept work item'),
 'status:ready-for-scope':('fbca04','Ready for scoped execution or review'),
 'security-review':('b60205','Requires security/privacy/permissions review'),
}
for name,(color,desc) in label_defs.items():
    subprocess.run(['gh','label','create',name,'--repo',repo,'--color',color,'--description',desc], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

issues=[
{
 'title':'Subissue of #2: Verify Teams tenant/app permissions and local Teams POC path',
 'labels':['area:teams-bot','type:poc','status:ready-for-scope','security-review'],
 'body':'''Parent: #2

## Objective
Determine which Microsoft Teams integration paths are actually permitted for this organization and this workstation before we spend time on the wrong POC route.

## Current local evidence
- Microsoft Teams is installed and running as `MSTeams_26120.3106.4722.3411_x64__8wekyb3d8bbwe`.
- Local Teams exposes protocol/deep-link handlers (`msteams`, `web+msteams`, etc.) and `ms-teams.exe` alias.
- Local Teams client does **not** by itself host a bot endpoint.
- Hermes status does not show a Teams messaging gateway configured.

## Scope
- Check whether Teams custom app upload / sideloading is allowed.
- Check whether incoming webhooks/connectors are allowed in the target Team/channel.
- Check whether Azure Bot registration is available and who can approve it.
- Check tenant app permission policies, app setup policies, and custom app policies.
- Identify the fastest allowed path among:
  1. Bot Framework Teams bot,
  2. Teams tab wrapping local/internal chatbot,
  3. incoming webhook demo bridge,
  4. deep-link/manual demo fallback.

## Deliverable
Create an HTML permissions checklist under `reports/teams-bot/issue-2/` with:
- reviewed setting,
- observed value/evidence,
- approver/owner if admin action is needed,
- go/no-go for each POC route,
- screenshots or redacted evidence where allowed.

## Acceptance criteria
- [ ] We know if custom Teams app upload/sideload is allowed.
- [ ] We know if incoming webhooks/connectors are allowed.
- [ ] We know if Azure Bot registration/admin consent is possible.
- [ ] We select one primary POC route and one fallback route.
- [ ] No Graph message-read permissions are requested by default.
'''
},
{
 'title':'Subissue of #2: Build approved repo knowledge pack for Oil & Gas Q&A POC',
 'labels':['area:teams-bot','type:poc','status:ready-for-scope'],
 'body':'''Parent: #2

## Objective
Create a small, approved, cited knowledge pack from the `llm-wiki-acma` repo ecosystem for the first Oil & Gas Q&A POC.

## Scope
- Inventory approved Markdown/HTML/report/manifests in the repo.
- Start with repo docs and report-layer artifacts; avoid raw `sources/` data unless explicitly approved.
- Create a machine-readable manifest with source IDs, file paths, repo revision, privacy classification, and allowed use.
- Produce a small retrieval corpus suitable for local RAG/search.
- Include enough domain material to answer a few representative Oil & Gas questions with citations.

## Deliverable
HTML-first report plus machine-readable manifest under `reports/teams-bot/issue-2/`, e.g.:
- `knowledge-pack.html`
- `knowledge-pack-manifest.json`
- optional `knowledge-pack-index.jsonl`

## Acceptance criteria
- [ ] Each indexed source has a stable source ID and repo path.
- [ ] Raw/private data access posture is documented.
- [ ] Each chunk can be traced back to an approved artifact.
- [ ] Test questions return cited source IDs.
- [ ] No client-sensitive raw text is exposed outside the private repo/report layer.
'''
},
{
 'title':'Subissue of #2: Implement minimal Hermes-backed Q&A service over repo knowledge pack',
 'labels':['area:teams-bot','type:poc','status:ready-for-scope'],
 'body':'''Parent: #2

## Objective
Create the smallest callable Q&A service that can answer Oil & Gas questions from the approved repo knowledge pack and produce a Teams-ready response schema.

## Scope
- Implement a local CLI or HTTP endpoint that accepts a question.
- Retrieve relevant knowledge-pack chunks and call Hermes/model path for a grounded answer.
- Return a structured response with:
  - concise answer,
  - citations/source IDs,
  - confidence/limitations,
  - follow-up suggestions,
  - redaction/safety status.
- Keep runtime repo access read-only or use pinned knowledge-pack files.

## Deliverable
- Minimal service/CLI implementation.
- HTML demo transcript showing sample questions and answers.
- Test fixture for at least 3 representative Oil & Gas questions.

## Acceptance criteria
- [ ] Runs locally without Teams dependency.
- [ ] Produces citations/source IDs for every substantive answer.
- [ ] Does not log prompts, raw retrieved snippets, model answers, credentials, or raw Teams payloads by default.
- [ ] Fails closed when no approved source is found.
- [ ] Output can be wrapped by Teams bot/tab/webhook routes.
'''
},
{
 'title':'Subissue of #2: Connect Q&A POC to fastest allowed Teams surface',
 'labels':['area:teams-bot','type:poc','status:ready-for-scope','security-review'],
 'body':'''Parent: #2

## Objective
Wire the minimal Q&A service into Microsoft Teams using the fastest route allowed by the tenant settings discovered in the permission-gate subissue.

## Candidate routes
1. Teams tab wrapping local/internal web chatbot.
2. Bot Framework Teams bot endpoint.
3. Incoming webhook bridge for demo-only posting.
4. Deep-link/manual share fallback if tenant blocks app install.

## Scope
- Select route based on documented permission evidence.
- Create minimal Teams app package/manifest or webhook config as applicable.
- Use Bot Framework activity context if using a bot; do not request broad Graph message-read scopes.
- Add a simple answer card/message format with citations and follow-up suggestions.

## Deliverable
- HTML integration report with screenshots/redacted evidence.
- Teams manifest or webhook/tab configuration files as appropriate.
- End-to-end demo transcript.

## Acceptance criteria
- [ ] The chosen route works in the local/org Teams environment or the exact blocker is documented.
- [ ] User can ask or submit a question and receive a cited answer/result in or through Teams.
- [ ] No broad Graph message-read scopes are used by default.
- [ ] All config/secrets are kept out of logs and repo commits.
'''
},
{
 'title':'Subissue of #2: Define security, identity, logging, and credential gates for Teams bot POC',
 'labels':['area:teams-bot','type:poc','status:ready-for-scope','security-review'],
 'body':'''Parent: #2

## Objective
Document and enforce the security baseline for any Teams/Hermes/repo POC before it touches real users or broader repo content.

## Scope
- Identity mapping: Teams user/channel/team context to repo content entitlements.
- Credential handling: pinned knowledge pack preferred; otherwise read-only GitHub App/deploy key stored in approved secret store.
- Logging: do not persist prompts, model answers, retrieved snippets, tokens, raw Teams message bodies, or credentials by default.
- Graph posture: Bot Framework activity context only unless a separate admin-approved Graph scope is justified.
- Prompt injection and data exfiltration test cases.

## Deliverable
HTML security checklist under `reports/teams-bot/issue-2/` with pass/fail status and required approvers.

## Acceptance criteria
- [ ] Least-privilege permissions documented.
- [ ] No forbidden Graph scopes in default POC.
- [ ] Secrets are not committed, dumped, logged, or included in transcripts.
- [ ] Repo access method has owner, rotation, and revocation path.
- [ ] Prompt-injection and unauthorized-content tests are listed and run before broader demo.
'''
},
{
 'title':'Subissue of #2: Produce HTML POC demo report and acceptance matrix',
 'labels':['area:teams-bot','type:poc','status:ready-for-scope'],
 'body':'''Parent: #2

## Objective
Package the POC outcome as an HTML-first review artifact so stakeholders can quickly approve, reject, or redirect the Teams bot effort.

## Scope
- Capture architecture used, route selected, repo sources used, and security posture.
- Include sample Oil & Gas questions, answers, citations, screenshots, and failure cases.
- Include acceptance matrix against issue #2 requirements and subissue acceptance criteria.
- Record open blockers and exact admin permissions still needed for production.

## Deliverable
`reports/teams-bot/issue-2/poc-demo-report.html` plus any supporting manifest JSON.

## Acceptance criteria
- [ ] Report renders correctly in browser.
- [ ] Includes citations/source IDs for every answer example.
- [ ] Includes pass/fail matrix and next-step recommendation.
- [ ] Includes privacy/publishability decision.
- [ ] Parent issue #2 is updated with report link and summary.
'''
},
]

created=[]
for item in issues:
    # avoid duplicates if rerun
    query=f'repo:{repo} is:issue in:title "{item["title"]}"'
    res=subprocess.run(['gh','search','issues',query,'--json','number,title,url','--limit','1'], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    existing=[]
    if res.returncode==0:
        try: existing=json.loads(res.stdout)
        except Exception: existing=[]
    if existing:
        created.append({'number':existing[0]['number'],'title':existing[0]['title'],'url':existing[0]['url'],'existing':True})
        continue
    body_path=pathlib.Path('C:/workspace-hub') / ('issue2_subissue_body_' + str(len(created)+1) + '.md')
    body_path.write_text(item['body'], encoding='utf-8')
    cmd=['gh','issue','create','--repo',repo,'--title',item['title'],'--body-file',str(body_path)]
    for lab in item['labels']:
        cmd += ['--label', lab]
    r=subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode!=0:
        raise SystemExit(f'failed creating {item["title"]}: {r.stderr}')
    url=r.stdout.strip()
    num=int(url.rstrip('/').split('/')[-1])
    created.append({'number':num,'title':item['title'],'url':url,'existing':False})

out.write_text(json.dumps(created, indent=2), encoding='utf-8')
print(json.dumps(created, indent=2))
