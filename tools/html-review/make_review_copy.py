"""Add a select-to-comment review layer to any local HTML page (report or decision board).

Select text -> "Comment" -> type the edit. Comments live in localStorage; "Save comments" writes
<page stem>.json beside the page (review-r2.html -> review-r2.json), in the folder that holds it
(chosen once through the File System Access API, checked to contain this page, then remembered per page
location; earlier saved comments are merged in), with the report file name and version, so the review
is self-contained beside the report. Comments are never written to Downloads: when the folder cannot be
written, nothing is saved, the comments stay in the tab and the status line says why. An export of
another revision beside the page is left unchanged and the comments go to <page stem>-<sha12>.json in
the same folder. Within a review round a save overwrites the JSON; a new round is a new page (-rN) and
so a new JSON. The source page is unchanged.
Usage:
  python make_review_copy.py SRC OUT KEY [EXPORT]   # any page
EXPORT is accepted for compatibility and ignored: the JSON file name is derived from the page name.
"""
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
args = sys.argv[1:]
if not 3 <= len(args) <= 4:
    sys.exit("usage: make_review_copy.py SRC OUT KEY [EXPORT]  (EXPORT is ignored; the JSON is named after the page)")
SRC = Path(args[0])
OUT = Path(args[1])
if SRC.resolve() == OUT.resolve():
    sys.exit("Source and review output must be different files.")
KEY = args[2]

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
  const payload=()=>JSON.stringify({...record(),report_folder:"__FOLDER__",exported_at:new Date().toISOString()},null,2);
  // Save writes BESIDE THIS PAGE, in the folder that holds it, and nowhere else (never as a download). Browsers cannot
  // write beside a page silently, so the first Save asks for that folder once; the folder must contain this page's
  // own file (SELF, same revision) or it is refused. The handle is kept in IndexedDB per page location (several
  // copies of a page in different folders each keep their own folder) and later Saves write straight to it.
  // When the folder cannot be written, nothing is saved, the comments stay in the tab and the status line says why.
  // The JSON is named after the page (<page stem>.json); a save overwrites it within a review round, and a new round
  // is a new page (-rN) and so a new JSON.
  const SELF=(()=>{try{return decodeURIComponent(location.pathname.split("/").pop()||"")}catch(e){return ""}})();
  const STEM=SELF.replace(/\.[^.]*$/,"")||"comments";
  const NAME=STEM+".json";
  const ALT=STEM+"-"+VERSION.slice(0,12)+".json";
  const DIRKEY=KEY+"|"+location.pathname;
  const NOTHING=" Nothing was saved; the comments are kept in this tab. Save again, or use Copy to send them.";
  const fail=(name,message)=>Object.assign(Error(message),{name});
  const plural=n=>`${n} comment${n===1?"":"s"}`;
  const idb=(mode,fn)=>new Promise((res,rej)=>{const r=indexedDB.open("rv-folders",1);r.onupgradeneeded=()=>r.result.createObjectStore("h");r.onsuccess=()=>{try{const tx=r.result.transaction("h",mode);const q=fn(tx.objectStore("h"));tx.oncomplete=()=>res(q&&q.result);tx.onerror=()=>rej(tx.error);tx.onabort=()=>rej(tx.error)}catch(e){rej(e)}};r.onerror=()=>rej(r.error)});
  const getDir=async()=>{try{return await idb("readonly",s=>s.get(DIRKEY))}catch(e){return null}};
  const putDir=async d=>{try{await idb("readwrite",s=>d?s.put(d,DIRKEY):s.delete(DIRKEY))}catch(e){}};
  // The remembered folder handle, read from IndexedDB at page load (below), so a Save click needs no await before
  // the picker or the permission request.
  let stored=null;
  async function mergeFrom(dir,name=NAME){
    kept=0;let fh;try{fh=await dir.getFileHandle(name)}catch(e){if(e.name==="NotFoundError")return 0;throw e}
    const n=merge(JSON.parse(await (await fh.getFile()).text()));
    persist();render();highlight();return n;
  }
  // The chosen folder must hold this page: a file named like this page whose text carries this revision.
  async function holdsPage(dir){
    if(!SELF) throw fail("WrongFolder","This page's file name cannot be read from its address, so the folder cannot be checked. Open the page file itself.");
    let fh;try{fh=await dir.getFileHandle(SELF)}catch(e){if(["NotFoundError","TypeMismatchError"].includes(e.name))throw fail("WrongFolder",`The folder ${dir.name} does not hold this page (${SELF}). Choose the folder that holds it.`);throw e}
    if(!(await (await fh.getFile()).text()).includes(VERSION)) throw fail("WrongFolder",`The ${SELF} in folder ${dir.name} is a different revision of this page. Choose the folder that holds this one.`);
  }
  // Which export file in dir takes the comments. NAME normally; when NAME belongs to another revision or cannot be
  // read or merged it is never written, and ALT (page stem + this revision) in the same folder is used instead.
  async function target(dir){
    const access=e=>["AbortError","SecurityError","NotAllowedError"].includes(e.name);
    try{return {name:NAME,merged:await mergeFrom(dir,NAME),note:""}}
    catch(e){
      if(access(e)) throw e;
      const note=e.name==="RevisionMismatch"?`The folder's ${NAME} belongs to a different report revision and was left unchanged; `:`The folder's ${NAME} could not be merged (${e.message}) and was left unchanged; `;
      try{return {name:ALT,merged:await mergeFrom(dir,ALT),note}}
      catch(e2){if(access(e2))throw e2;throw fail("Unmergeable",note+`${ALT} beside it could not be merged either (${e2.message}) and was left unchanged.`)}
    }
  }
  const detail=e=>`${e&&e.name}: ${e&&e.message}`;
  const why=e=>e.name==="AbortError"?`No folder was chosen (${detail(e)}).`:["NotAllowedError","SecurityError"].includes(e.name)?`The browser refused access to the folder (${detail(e)}).`:["WrongFolder","PermissionRefused","Unmergeable"].includes(e.name)?e.message:`Save stopped (${detail(e)}).`;
  const noApi="This browser cannot write files beside the page (no File System Access API); open the page from disk in Edge or Chrome.";
  const pick=()=>{try{return window.showDirectoryPicker({id:"rv-report-folder",mode:"readwrite"})}catch(e){return Promise.reject(e)}};
  // The click handler is synchronous up to the picker or permission request: no await may precede them, because
  // transient user activation can be lost across awaits and the browser then refuses the dialog.
  $("#rv-save").addEventListener("click",()=>{
    if(!window.showDirectoryPicker){$("#rv-status").textContent=noApi+NOTHING;return}
    const dir=stored;
    let first;
    if(dir){try{first=dir.requestPermission({mode:"readwrite"})}catch(e){first=Promise.reject(e)}}
    else first=pick();
    return save(dir,first);
  });
  async function save(dir,first){
    try{
      if(dir){
        if((await first)!=="granted") throw fail("PermissionRefused",`Permission to write to folder ${dir.name} was refused (use Folder… to choose it again).`);
        try{await holdsPage(dir)}catch(e){if(e.name!=="WrongFolder")throw e;stored=null;await putDir(null);throw fail("WrongFolder",e.message+" The remembered folder was forgotten; Save again to choose the folder.")}
      }else{
        dir=await first;await holdsPage(dir);stored=dir;await putDir(dir);
      }
      const t=await target(dir);
      const w=await (await dir.getFileHandle(t.name,{create:true})).createWritable(); await w.write(payload()); await w.close();
      $("#rv-status").textContent=(t.note?t.note+`saved ${plural(items.length)} to ${dir.name}/${t.name} instead`:`Saved ${plural(items.length)} to ${dir.name}/${t.name}`)+(t.merged?` (${t.merged} earlier merged in).`:".")+keptNote();
      $("#rv-folder").textContent=`Saving to: ${dir.name}/${t.name}`;
    }catch(e){$("#rv-status").textContent=why(e)+NOTHING}
  }
  $("#rv-change").addEventListener("click",()=>{
    if(!window.showDirectoryPicker){$("#rv-status").textContent=noApi;return}
    const first=pick();
    return (async()=>{try{ const dir=await first; await holdsPage(dir); const t=await target(dir); stored=dir; await putDir(dir); $("#rv-folder").textContent=`Saving to: ${dir.name}/${t.name}`; $("#rv-status").textContent=(t.note?t.note+`comments will be saved to ${t.name}. `:"")+(t.merged?`Loaded ${t.merged} saved comment${t.merged===1?"":"s"} from ${dir.name}/${t.name}.`:`Folder set to ${dir.name}.`)+keptNote(); }catch(e){$("#rv-status").textContent="Folder change stopped: "+why(e)}})();
  });
  // On open: read the remembered folder; when it is still writable without asking, load the comments saved beside the page.
  getDir().then(async d=>{
    if(d&&!stored) stored=d;
    $("#rv-folder").textContent=d?`Saving to: ${d.name}/${NAME}`:`First Save asks for the folder that holds this page: ${FOLDER}`;
    if(!d) return;
    try{
      if((await d.queryPermission({mode:"readwrite"}))!=="granted") return;
      await holdsPage(d); const t=await target(d);
      $("#rv-folder").textContent=`Saving to: ${d.name}/${t.name}`;
      if(t.merged||t.note) $("#rv-status").textContent=(notes.length?notes.join(" ")+" ":"")+(t.note?t.note+`comments will be saved to ${t.name}. `:"")+`Loaded ${t.merged} saved comment${t.merged===1?"":"s"} from ${d.name}/${t.name}.`+keptNote();
    }catch(e){}
  });
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
parameters = {"__KEY__": KEY, "__PAGE__": SRC.name,
              "__VERSION__": VERSION, "__FOLDER__": str(OUT.parent)}
def encode_parameter(match):
    value = parameters[match[1]] + (match[2] or "")
    return json.dumps(value).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


layer = re.sub(r'"(__[A-Z]+__)(\.json)?"', encode_parameter, LAYER)
if re.search(r"__[A-Z]+__", layer):
    sys.exit("Review layer has an unsubstituted placeholder.")
OUT.write_text(html.replace("</body>", layer + "\n</body>", 1), encoding="utf-8")
print(OUT)
