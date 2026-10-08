"""Add a select-to-comment review layer to any local HTML page (report or decision board).

Select text -> "Comment" -> type the edit. Comments live in localStorage; "Save comments" writes
<export>.json into the report's own folder (chosen once, then remembered; earlier saved comments are
merged in), with the report file name and version, so the review is self-contained beside the report.
Browsers without the File System Access API fall back to Downloads. The source page is unchanged.
Usage:
  python make_review_copy.py SRC OUT KEY EXPORT   # any page
"""
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
args = sys.argv[1:]
if len(args) < 4:
    sys.exit("usage: make_review_copy.py SRC OUT KEY EXPORT")
SRC = Path(args[0])
OUT = Path(args[1])
if SRC.resolve() == OUT.resolve():
    sys.exit("Source and review output must be different files.")
KEY = args[2]
EXPORT = args[3]

LAYER = r"""
<style id="rv-style">
#rv-btn{position:absolute;z-index:9999;display:none;background:#1F5A7A;color:#fff;border:0;border-radius:4px;padding:4px 10px;font:600 12px system-ui;cursor:pointer;box-shadow:0 2px 6px rgba(0,0,0,.25)}
#rv-panel{position:fixed;right:12px;bottom:12px;width:340px;max-height:70vh;display:flex;flex-direction:column;background:#fff;color:#16252E;border:1px solid #D3DBDF;border-radius:8px;box-shadow:0 6px 24px rgba(0,0,0,.18);font:13px/1.45 system-ui;z-index:9998}
#rv-panel header{display:flex;gap:6px;align-items:center;padding:8px 10px;border-bottom:1px solid #E6ECEE;font-weight:600}
#rv-panel header span{flex:1}
#rv-panel button{font:inherit;font-size:12px;border:1px solid #1F5A7A;background:#1F5A7A;color:#fff;border-radius:4px;padding:3px 8px;cursor:pointer}
#rv-panel button.ghost{background:transparent;color:#1F5A7A}
#rv-list{overflow:auto;padding:8px 10px;display:flex;flex-direction:column;gap:8px}
.rv-item{border:1px solid #E6ECEE;border-radius:6px;padding:6px 8px}
.rv-item .q{color:#6B7A83;font-style:italic;max-height:3.2em;overflow:hidden}
.rv-item .s{font-size:11px;color:#1F5A7A}
.rv-item textarea,#rv-edit textarea{width:100%;min-height:52px;font:inherit;border:1px solid #D3DBDF;border-radius:4px;padding:4px}
#rv-edit{display:none;padding:8px 10px;border-top:1px solid #E6ECEE}
mark.rv-hl{background:#FBE7A8;padding:0 1px}
#rv-status{font-size:11px;color:#6B7A83;padding:0 10px 8px}
@media print{#rv-panel,#rv-btn{display:none}}
</style>
<noscript><div style="position:fixed;right:12px;bottom:12px;max-width:340px;background:#FBE7A8;color:#16252E;padding:8px 10px;border-radius:6px;font:13px system-ui;z-index:9998">Scripts are blocked in this view, so comments cannot be added. Save the file and open it from disk in Edge or Chrome.</div></noscript>
<button id="rv-btn" type="button">Comment</button>
<div id="rv-panel" aria-label="Review comments">
  <header><span>Review comments (<b id="rv-count">0</b>)</span>
    <button type="button" id="rv-save">Save comments</button>
    <button type="button" class="ghost" id="rv-copy">Copy</button>
    <label class="ghost" style="cursor:pointer;border:1px solid #1F5A7A;border-radius:4px;padding:3px 8px;color:#1F5A7A;font-size:12px">Load<input id="rv-load" type="file" accept=".json" hidden></label>
  </header>
  <div id="rv-edit"><div class="q" id="rv-quote"></div>
    <textarea id="rv-text" placeholder="Your edit or comment (e.g. replace with …, delete, move, clarify). Tip: press Windows+H to dictate instead of typing."></textarea>
    <div style="display:flex;gap:6px;margin-top:6px"><button type="button" id="rv-add">Add</button><button type="button" class="ghost" id="rv-cancel">Cancel</button></div></div>
  <div id="rv-list"></div>
  <div id="rv-status">Select text in the report, then click Comment. When done, Save comments: they are written beside this report and reloaded next time.</div>
  <div style="font-size:11px;color:#1F5A7A;padding:0 10px 8px;display:flex;gap:6px;align-items:center"><span id="rv-folder" style="flex:1"></span><button type="button" class="ghost" id="rv-change" style="font-size:11px;padding:1px 6px">Folder…</button></div>
</div>
<script id="rv-script">
(function(){
  const KEY="__KEY__";
  const $=s=>document.querySelector(s);
  const PAGE="__PAGE__", VERSION="__VERSION__", FOLDER="__FOLDER__";
  let items=[], deleted=new Set();
  const identity=c=>c.id||("legacy:"+JSON.stringify([c.quote,c.at]));
  function checked(data){
    if(!data||data.page!==PAGE||data.report_version!==VERSION) throw Object.assign(Error("Comments belong to a different report revision."),{name:"RevisionMismatch"});
    if(!Array.isArray(data.comments)||data.comments.some(c=>!c||typeof c.quote!=="string"||typeof c.comment!=="string"||typeof c.at!=="string"||["id","section","data_src","edited_at"].some(k=>c[k]!==undefined&&typeof c[k]!=="string"))) throw Error("Invalid comments file.");
    if(data.deleted_ids!==undefined&&(!Array.isArray(data.deleted_ids)||data.deleted_ids.some(id=>typeof id!=="string"))) throw Error("Invalid deletion records.");
    return data.comments.map(c=>({...c,id:identity(c)}));
  }
  // Records are stored per revision (STORE). The bare KEY may hold a legacy array or another revision's record:
  // it is read once and adopted only when it matches this revision, and it is never written, so nothing is lost.
  const STORE=KEY+"|"+VERSION;
  // An imported deletion record does not remove a comment edited here (edited_at): the local edit is kept and
  // counted in `kept`, so a deletion made elsewhere never silently discards newer local text. edited_at is honoured
  // only from this browser's own record (own=true); imported files have it stripped, so a remote edit gains no protection.
  let kept=0;
  function merge(data,own){
    const incoming=checked(data).map(c=>{if(own)return c;const{edited_at,...rest}=c;return rest});kept=0;
    (data.deleted_ids||[]).forEach(id=>{const local=items.find(c=>identity(c)===id);if(local&&local.edited_at){kept++;return}deleted.add(id)});
    items=items.filter(c=>!deleted.has(identity(c)));
    const have=new Set(items.map(identity));let n=0;
    incoming.forEach(c=>{if(!have.has(c.id)&&!deleted.has(c.id)){items.push(c);have.add(c.id);n++}});
    return n;
  }
  const keptNote=()=>kept?` ${kept} comment${kept>1?"s":""} edited here ${kept>1?"were":"was"} kept although the file records ${kept>1?"them":"it"} as deleted.`:"";
  const notes=[];let frozen=false;
  // An unreadable own record is copied to STORE|unreadable before anything may overwrite it. If that copy fails,
  // storage for this revision is frozen (persist() writes nothing) so the original is never lost.
  try{const own=localStorage.getItem(STORE);if(own){try{merge(JSON.parse(own),true)}catch(e){try{localStorage.setItem(STORE+"|unreadable",own);notes.push("Stored comments could not be loaded for this revision; a copy is kept in browser storage under the suffix |unreadable. Load a matching exported file.")}catch(_){frozen=true;notes.push("Stored comments could not be loaded for this revision and could not be copied, so browser storage for this revision is left unchanged. Use Save comments or Copy before closing.")}}}else{const legacy=localStorage.getItem(KEY);if(legacy)merge(JSON.parse(legacy))}}catch(e){notes.push("Stored comments could not be loaded for this revision. Load a matching exported file.")}
  // Comments kept for other revisions of this page are never shown here; say so, so they are not taken as lost.
  try{const others=[];for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(k&&k!==STORE&&k.startsWith(KEY+"|")&&!k.endsWith("|unreadable")){try{others.push([k.slice(KEY.length+1),(JSON.parse(localStorage.getItem(k)).comments||[]).length])}catch(e){}}}
    const n=others.reduce((s,o)=>s+o[1],0);if(n)notes.push(`${n} comments are stored in this browser for other revisions of this report (${others.map(o=>o[0]).join(", ")}). They are not merged into this revision; a review copy generated from that revision can Save or Copy them.`)}catch(e){}
  if(notes.length)$("#rv-status").textContent=notes.join(" ");
  let pending=null;
  const record=()=>({page:PAGE,report_version:VERSION,comments:items,deleted_ids:[...deleted]});
  const persist=()=>{if(frozen){$("#rv-status").textContent="Browser storage for this revision is left unchanged (its unreadable record could not be copied). Use Save comments or Copy before closing.";return}try{localStorage.setItem(STORE,JSON.stringify(record()))}catch(e){$("#rv-status").textContent="Browser storage unavailable — use Save comments before closing."}};
  function sectionOf(node){
    let el=node.nodeType===1?node:node.parentElement;
    while(el&&el!==document.body){
      let p=el; while(p){ if(/^H[1-4]$/.test(p.tagName)) return (p.id?("#"+p.id+" "):"")+p.textContent.trim().slice(0,90); p=p.previousElementSibling; }
      el=el.parentElement;
    }
    return "";
  }
  function srcOf(node){let el=node.nodeType===1?node:node.parentElement;while(el&&el!==document.body){if(el.dataset&&el.dataset.src)return el.dataset.src;el=el.parentElement}return ""}
  function render(){
    $("#rv-count").textContent=items.length;
    $("#rv-list").innerHTML=items.map((c,i)=>`<div class="rv-item"><div class="s">${esc(c.section||"(no heading)")}${c.data_src?" · data-src "+esc(c.data_src):""}</div><div class="q">“${esc(c.quote)}”</div><textarea data-i="${i}">${esc(c.comment)}</textarea><div style="text-align:right"><button type="button" class="ghost" data-del="${i}">Delete</button></div></div>`).join("");
  }
  const esc=s=>String(s||"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  function highlight(){ items.forEach(c=>{ if(!c.quote) return; const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT,{acceptNode:n=>n.parentElement.closest("#rv-panel,script,style,mark.rv-hl")?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_ACCEPT}); let n; const q=c.quote.slice(0,80); while((n=w.nextNode())){ const k=n.nodeValue.indexOf(q); if(k>=0){ const r=document.createRange(); r.setStart(n,k); r.setEnd(n,k+q.length); const m=document.createElement("mark"); m.className="rv-hl"; m.title=c.comment; try{r.surroundContents(m)}catch(e){} break; } } }); }
  document.addEventListener("mouseup",e=>{
    if(e.target.closest("#rv-panel,#rv-btn")) return;
    const sel=window.getSelection(); const t=sel&&sel.toString().trim();
    const b=$("#rv-btn");
    if(!t){b.style.display="none";return}
    const r=sel.getRangeAt(0).getBoundingClientRect();
    b.style.left=(window.scrollX+r.right-60)+"px"; b.style.top=(window.scrollY+r.bottom+6)+"px"; b.style.display="block";
    pending={quote:t.slice(0,600),section:sectionOf(sel.anchorNode),data_src:srcOf(sel.anchorNode)};
  });
  $("#rv-btn").addEventListener("click",()=>{ if(!pending) return; $("#rv-btn").style.display="none"; $("#rv-quote").textContent="“"+pending.quote.slice(0,200)+"”"; $("#rv-edit").style.display="block"; $("#rv-text").value=""; $("#rv-text").focus(); });
  $("#rv-cancel").addEventListener("click",()=>{ $("#rv-edit").style.display="none"; pending=null; });
  $("#rv-add").addEventListener("click",()=>{ const txt=$("#rv-text").value.trim(); if(!pending||!txt) return; items.push({...pending,id:crypto.randomUUID(),comment:txt,at:new Date().toISOString()}); persist(); render(); highlight(); $("#rv-edit").style.display="none"; pending=null; $("#rv-status").textContent="Comment added. Save comments when done."; });
  $("#rv-list").addEventListener("input",e=>{ if(e.target.dataset.i!==undefined){ const c=items[+e.target.dataset.i]; c.comment=e.target.value; c.edited_at=new Date().toISOString(); persist(); } });
  $("#rv-list").addEventListener("click",e=>{ if(e.target.dataset.del!==undefined){ deleted.add(identity(items[+e.target.dataset.del]));items.splice(+e.target.dataset.del,1); persist(); render(); } });
  const NAME="__EXPORT__.json";
  const payload=()=>JSON.stringify({...record(),report_folder:"__FOLDER__",exported_at:new Date().toISOString()},null,2);
  // Save into the REPORT'S OWN FOLDER. Browsers cannot write beside a page silently, so the first Save asks for
  // that folder once (the dialog opens there by id); the folder handle is kept in IndexedDB and later Saves write
  // The export file is written there directly. Comments already in that file are merged in first.
  // is lost if this browser's storage was cleared. Browsers without the File System Access API fall back to Downloads.
  const idb=(mode,fn)=>new Promise((res,rej)=>{const r=indexedDB.open("rv-folders",1);r.onupgradeneeded=()=>r.result.createObjectStore("h");r.onsuccess=()=>{try{const tx=r.result.transaction("h",mode);const q=fn(tx.objectStore("h"));tx.oncomplete=()=>res(q&&q.result);tx.onerror=()=>rej(tx.error);tx.onabort=()=>rej(tx.error)}catch(e){rej(e)}};r.onerror=()=>rej(r.error)});
  const getDir=async()=>{try{return await idb("readonly",s=>s.get(KEY))}catch(e){return null}};
  const putDir=async d=>{try{await idb("readwrite",s=>s.put(d,KEY))}catch(e){}};
  async function mergeFrom(dir){
    kept=0;let fh;try{fh=await dir.getFileHandle(NAME)}catch(e){if(e.name==="NotFoundError")return 0;throw e}
    const n=merge(JSON.parse(await (await fh.getFile()).text()));
    persist();render();highlight();return n;
  }
  async function folder(ask){
    let dir=await getDir();
    if(dir && (await dir.queryPermission({mode:"readwrite"}))!=="granted" && (await dir.requestPermission({mode:"readwrite"}))!=="granted") dir=null;
    if(!dir && ask){ dir=await window.showDirectoryPicker({id:"rv-report-folder",mode:"readwrite"}); await putDir(dir); }
    return dir;
  }
  $("#rv-save").addEventListener("click",async()=>{
    let note="";
    if (window.showDirectoryPicker) {
      try {
        const dir=await folder(true);
        let merged;
        // Any failure to read or merge the folder's existing export (other revision, malformed JSON, invalid records)
        // leaves that file unchanged and falls back to a download; only permission and write failures stop Save.
        try{merged=await mergeFrom(dir)}catch(e){if(["AbortError","SecurityError","NotAllowedError"].includes(e.name))throw e;e.fromMerge=true;throw e}
        const w=await (await dir.getFileHandle(NAME,{create:true})).createWritable(); await w.write(payload()); await w.close();
        $("#rv-status").textContent=`Saved ${items.length} comments to ${dir.name}/${NAME}`+(merged?` (${merged} earlier comments merged in).`:".")+keptNote();
        $("#rv-folder").textContent=`Saving to: ${dir.name}/${NAME}`; return;
      } catch(e) {
        if(e.fromMerge) note=e.name==="RevisionMismatch"?`The folder's ${NAME} belongs to a different report revision and was left unchanged. `:`The folder's ${NAME} could not be merged (${e.message}) and was left unchanged. `;
        else if(!["AbortError","SecurityError","NotAllowedError"].includes(e.name)){ $("#rv-status").textContent="Save stopped: "+e.message+" Choose another folder or use Copy.";return; }
      }
    }
    const a=document.createElement("a"); a.href=URL.createObjectURL(new Blob([payload()],{type:"application/json"})); a.download=NAME; document.body.append(a); a.click(); a.remove();
    $("#rv-status").textContent=note+`Download requested for ${NAME} (${items.length} comments). Check the browser download location and confirm the file exists.`;
  });
  $("#rv-change").addEventListener("click",async()=>{ try{ const dir=await window.showDirectoryPicker({id:"rv-report-folder",mode:"readwrite"}); const n=await mergeFrom(dir); await putDir(dir); $("#rv-folder").textContent=`Saving to: ${dir.name}/${NAME}`; $("#rv-status").textContent=(n?`Loaded ${n} saved comments from ${dir.name}.`:`Folder set to ${dir.name}.`)+keptNote(); }catch(e){$("#rv-status").textContent="Folder change stopped: "+e.message} });
  getDir().then(d=>{ $("#rv-folder").textContent=d?`Saving to: ${d.name}/${NAME}`:`First Save asks for the report folder: ${FOLDER}`; });
  $("#rv-copy").addEventListener("click",async()=>{
    const text=payload();
    try { await navigator.clipboard.writeText(text); $("#rv-status").textContent=`Copied ${items.length} comments; paste them into your reply email.`; }
    catch(e) { const t=document.createElement("textarea"); t.value=text; document.body.append(t); t.select(); try{document.execCommand("copy")}catch(_){} t.remove(); $("#rv-status").textContent="Copied (fallback). If nothing pasted, use Save comments."; }
  });
  $("#rv-load").addEventListener("change",e=>{ const f=e.target.files[0]; if(!f) return; const rd=new FileReader(); rd.onload=()=>{ try{ const n=merge(JSON.parse(rd.result));persist(); render(); highlight(); $("#rv-status").textContent=`Loaded ${n} new comments; ${items.length} in total. Comments already here keep their current text; deletion records are combined.`+keptNote(); }catch(err){ $("#rv-status").textContent="Load stopped: "+err.message; } }; rd.readAsText(f); e.target.value=""; });
  render(); highlight();
})();
</script>
"""

html = SRC.read_text(encoding="utf-8")
if "</body>" not in html:          # an artifact-style page (no skeleton): wrap it
    html = ('<!doctype html><html><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1"></head><body>\n' + html + "\n</body></html>")
VERSION = hashlib.sha256(SRC.read_bytes()).hexdigest()[:12] + " " + datetime.fromtimestamp(SRC.stat().st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
parameters = {"__KEY__": KEY, "__EXPORT__": EXPORT, "__PAGE__": SRC.name,
              "__VERSION__": VERSION, "__FOLDER__": str(OUT.parent)}
def encode_parameter(match):
    value = parameters[match[1]] + (match[2] or "")
    return json.dumps(value).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


layer = re.sub(r'"(__[A-Z]+__)(\.json)?"', encode_parameter, LAYER)
if re.search(r"__[A-Z]+__", layer):
    sys.exit("Review layer has an unsubstituted placeholder.")
OUT.write_text(html.replace("</body>", layer + "\n</body>", 1), encoding="utf-8")
print(OUT)
