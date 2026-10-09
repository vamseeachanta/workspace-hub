"""Offline integrity regressions against the shipped review JavaScript."""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / "make_review_copy.py"


@unittest.skipUnless(shutil.which("node"), "Node is required")
class ReviewIntegrityTests(unittest.TestCase):
    def run_js(self, assertions, stored=None, extra=None, pre=""):
        source = TOOL.read_text(encoding="utf-8")
        script = re.search(r'<script id="rv-script">(.*?)</script>', source, re.S)[1]
        script = script.replace("})();", "globalThis.test={mergeFrom,render,payload,get:()=>items,set:v=>items=v};})();")
        harness = """
const assert=require('node:assert/strict');
const nodes=new Map();
const node=()=>({textContent:'',innerHTML:'',style:{},events:{},addEventListener(k,f){this.events[k]=f}});
global.document={querySelector:s=>{if(!nodes.has(s))nodes.set(s,node());return nodes.get(s)},addEventListener(){},body:{},createTreeWalker:()=>({nextNode:()=>null})};
global.NodeFilter={SHOW_TEXT:4,FILTER_REJECT:2,FILTER_ACCEPT:1};
const storage=new Map();
global.localStorage={getItem:k=>storage.get(k)||null,setItem(k,v){storage.set(k,v)}};
global.indexedDB={open:()=>{throw Error('unavailable')}};
global.location={pathname:'/reports/review.html'};
const settle=()=>new Promise(r=>setTimeout(r,20));
// In-memory folder: files maps name -> text. The page itself must be present for the folder to be accepted.
const makeDir=(name,files,perm)=>{files=files||{};const writes=[];return {name,files,writes,
  queryPermission:async()=>perm||'granted',requestPermission:async()=>perm||'granted',
  getFileHandle:async(n,o)=>{if(!(n in files)){if(!(o&&o.create))throw Object.assign(Error('none'),{name:'NotFoundError'});files[n]=''}
    return {getFile:async()=>({text:async()=>files[n]}),createWritable:async()=>({write:async t=>{writes.push(n);files[n]=t},close:async()=>{}})}}}};
const PAGE_TEXT='<html>const VERSION="__VERSION__";</html>';
const useStoredDir=dir=>{global.indexedDB={open:()=>{const r={};setTimeout(()=>{r.result={transaction:()=>{const tx={objectStore:()=>({get:()=>({result:dir}),put:()=>({})})};setTimeout(()=>tx.oncomplete&&tx.oncomplete(),0);return tx}};r.onsuccess&&r.onsuccess()},0);return r}}};
// Any attempt to build a download link fails the test.
document.createElement=t=>{throw Error('createElement('+t+') during Save: no download path may exist')};
"""
        initial = "storage.set('__KEY__'," + json.dumps(stored) + ");\n" if stored is not None else ""
        initial += "".join(f"storage.set({json.dumps(k)},{json.dumps(v)});\n" for k, v in (extra or {}).items())
        initial += pre + "\n"
        harness = harness.replace("global.localStorage={", "global.localStorage={get length(){return storage.size},key:i=>[...storage.keys()][i]??null,")
        program = harness + initial + script + "\n(async()=>{\n" + assertions + "\n})().catch(e=>{console.error(e);process.exitCode=1});"
        result = subprocess.run(["node", "-e", program], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_revision_mismatch_is_rejected(self):
        self.run_js("""
const wrong={page:'other.html',report_version:'wrong',comments:[{quote:'q',comment:'old',at:'a'}]};
const dir={getFileHandle:async()=>({getFile:async()=>({text:async()=>JSON.stringify(wrong)})})};
await assert.rejects(test.mergeFrom(dir),/revision|report/i);
assert.equal(test.get().length,0);
""")

    def test_current_edit_wins_over_saved_version(self):
        self.run_js("""
test.set([{id:'one',quote:'q',comment:'edited',at:'a'}]);
const saved={page:'__PAGE__',report_version:'__VERSION__',comments:[{id:'one',quote:'q',comment:'old',at:'a'}]};
const dir={getFileHandle:async()=>({getFile:async()=>({text:async()=>JSON.stringify(saved)})})};
await test.mergeFrom(dir);
assert.equal(test.get().length,1);
assert.equal(test.get()[0].comment,'edited');
""")

    def test_metadata_is_escaped(self):
        self.run_js("""
test.set([{quote:'q',comment:'ok',section:'<img src=x onerror=alert(1)>',data_src:'<svg onload=alert(2)>'}]);
test.render();
const html=nodes.get('#rv-list').innerHTML;
assert.ok(!html.includes('<img'));
assert.ok(!html.includes('<svg'));
assert.ok(html.includes('&lt;img'));
""")

    def test_deleted_comment_does_not_return(self):
        self.run_js("""
test.set([{id:'one',quote:'q',comment:'old',at:'a'}]);
nodes.get('#rv-list').events.click({target:{dataset:{del:'0'}}});
const saved={page:'__PAGE__',report_version:'__VERSION__',comments:[{id:'one',quote:'q',comment:'old',at:'a'}]};
const dir={getFileHandle:async()=>({getFile:async()=>({text:async()=>JSON.stringify(saved)})})};
await test.mergeFrom(dir);
assert.equal(test.get().length,0);
assert.deepEqual(JSON.parse(test.payload()).deleted_ids,['one']);
""")

    def test_load_mismatch_preserves_current_comments(self):
        self.run_js("""
test.set([{id:'current',quote:'q',comment:'keep',at:'a'}]);
global.FileReader=class{readAsText(){this.result=JSON.stringify({page:'wrong',report_version:'bad',comments:[]});this.onload()}};
nodes.get('#rv-load').events.change({target:{files:[{}],value:'x'}});
assert.equal(test.get()[0].comment,'keep');
assert.match(nodes.get('#rv-status').textContent,/Load stopped/);
""")

    def test_load_preserves_current_edits_and_deletions(self):
        self.run_js("""
test.set([{id:'deleted',quote:'q',comment:'remove',at:'a'},{id:'edit',quote:'q',comment:'current',at:'b'}]);
nodes.get('#rv-list').events.click({target:{dataset:{del:'0'}}});
global.FileReader=class{readAsText(){this.result=JSON.stringify({page:'__PAGE__',report_version:'__VERSION__',comments:[{id:'deleted',quote:'q',comment:'old',at:'a'},{id:'edit',quote:'q',comment:'old',at:'b'}]});this.onload()}};
nodes.get('#rv-load').events.change({target:{files:[{}],value:'x'}});
assert.equal(test.get().length,1);
assert.equal(test.get()[0].comment,'current');
assert.deepEqual(JSON.parse(test.payload()).deleted_ids,['deleted']);
""")

    def test_rejected_storage_is_preserved_after_persist(self):
        original = '[{"quote":"q","comment":"legacy","at":"a"}]'
        self.run_js("""
test.set([{id:'new',quote:'q',comment:'new',at:'b'}]);
nodes.get('#rv-list').events.input({target:{dataset:{i:'0'},value:'edited'}});
assert.equal(storage.get('__KEY__'),'[{"quote":"q","comment":"legacy","at":"a"}]');
""", stored=original)

    def test_other_revision_storage_is_preserved_after_add(self):
        original = json.dumps({"page": "__PAGE__", "report_version": "older", "comments": [{"id": "old", "quote": "q", "comment": "earlier", "at": "a"}]})
        self.run_js("""
test.set([{id:'new',quote:'q',comment:'new',at:'b'}]);
nodes.get('#rv-list').events.input({target:{dataset:{i:'0'},value:'edited'}});
assert.equal(storage.get('__KEY__'),""" + json.dumps(original) + """);
assert.equal(JSON.parse(storage.get('__KEY__|__VERSION__')).comments[0].comment,'edited');
""", stored=original)

    def test_matching_legacy_record_is_adopted(self):
        original = json.dumps({"page": "__PAGE__", "report_version": "__VERSION__", "comments": [{"id": "one", "quote": "q", "comment": "kept", "at": "a"}]})
        self.run_js("""
assert.equal(test.get().length,1);
assert.equal(test.get()[0].comment,'kept');
""", stored=original)

    def test_other_revision_comments_are_announced(self):
        older = json.dumps({"page": "__PAGE__", "report_version": "older", "comments": [{"id": "a", "quote": "q", "comment": "c", "at": "t"}, {"id": "b", "quote": "q", "comment": "d", "at": "t"}]})
        self.run_js("""
assert.equal(test.get().length,0);
assert.match(nodes.get('#rv-status').textContent,/2 comments.*older/);
""", extra={"__KEY__|older": older})

    def test_layer_has_no_download_path(self):
        source = TOOL.read_text(encoding="utf-8")
        layer = re.search(r'LAYER = r"""(.*?)"""', source, re.S)[1]
        for banned in (r"\.download\b", r"createObjectURL", r"new Blob", r"(?i)downloads"):
            self.assertIsNone(re.search(banned, layer), f"review layer still contains {banned}")

    def test_save_writes_beside_page(self):
        self.run_js("""
test.set([{id:'one',quote:'q',comment:'keep',at:'a'}]);
const dir=makeDir('reports',{'review.html':PAGE_TEXT});
global.window={showDirectoryPicker:async()=>dir};
await nodes.get('#rv-save').events.click();
assert.equal(dir.writes[0],'review.json');
assert.equal(dir.writes.length,2);
assert.match(dir.writes[1],/^review-\\d{8}T\\d{6}Z\\.json$/);
assert.equal(JSON.parse(dir.files['review.json']).comments[0].comment,'keep');
assert.equal(dir.files[dir.writes[1]],dir.files['review.json']);
assert.match(nodes.get('#rv-status').textContent,/Saved 1 comment/);
""")

    def test_every_save_keeps_a_utc_timestamped_copy(self):
        # Owner decision D03 (2026-10-08): <page>.json is the latest; every save also leaves
        # <page>-<UTC yyyymmddThhmmssZ>.json beside it, and earlier copies are never rewritten.
        self.run_js("""
test.set([{id:'one',quote:'q',comment:'first',at:'a'}]);
const dir=makeDir('reports',{'review.html':PAGE_TEXT});
global.window={showDirectoryPicker:async()=>dir};
await nodes.get('#rv-save').events.click();
assert.deepEqual(dir.writes,['review.json','review-20261008T213005Z.json']);
NOW='2026-10-08T22:01:59.987Z';
nodes.get('#rv-list').events.input({target:{dataset:{i:'0'},value:'second'}});
await nodes.get('#rv-save').events.click();
assert.deepEqual(dir.writes,['review.json','review-20261008T213005Z.json','review.json','review-20261008T220159Z.json']);
assert.equal(JSON.parse(dir.files['review-20261008T213005Z.json']).comments[0].comment,'first');
assert.equal(JSON.parse(dir.files['review-20261008T220159Z.json']).comments[0].comment,'second');
assert.equal(dir.files['review.json'],dir.files['review-20261008T220159Z.json']);
assert.match(nodes.get('#rv-status').textContent,/review-20261008T220159Z\\.json/);
""", pre="""
let NOW='2026-10-08T21:30:05.123Z';
const RealDate=Date;
global.Date=class extends RealDate{constructor(...a){super(...(a.length?a:[NOW]))}static now(){return new RealDate(NOW).getTime()}};
""")

    def test_save_refuses_folder_without_the_page(self):
        self.run_js("""
test.set([{id:'one',quote:'q',comment:'keep',at:'a'}]);
const dir=makeDir('Downloads',{});
global.window={showDirectoryPicker:async()=>dir};
await nodes.get('#rv-save').events.click();
assert.deepEqual(dir.writes,[]);
assert.match(nodes.get('#rv-status').textContent,/does not hold this page.*Nothing was saved/);
assert.equal(test.get()[0].comment,'keep');
""")

    def test_save_refuses_folder_with_other_revision_of_the_page(self):
        self.run_js("""
test.set([{id:'one',quote:'q',comment:'keep',at:'a'}]);
const dir=makeDir('old',{'review.html':'<html>const VERSION="older";</html>'});
global.window={showDirectoryPicker:async()=>dir};
await nodes.get('#rv-save').events.click();
assert.deepEqual(dir.writes,[]);
assert.match(nodes.get('#rv-status').textContent,/Nothing was saved/);
""")

    def test_save_without_file_system_access_keeps_comments_in_tab(self):
        self.run_js("""
test.set([{id:'one',quote:'q',comment:'keep',at:'a'}]);
global.window={};
await nodes.get('#rv-save').events.click();
assert.match(nodes.get('#rv-status').textContent,/Nothing was saved.*kept in this tab/);
assert.equal(test.get()[0].comment,'keep');
""")

    def test_save_with_refused_permission_keeps_comments_in_tab(self):
        self.run_js("""
await settle();
test.set([{id:'one',quote:'q',comment:'keep',at:'a'}]);
let picked=false;global.window={showDirectoryPicker:async()=>{picked=true;return dir}};
await nodes.get('#rv-save').events.click();
assert.equal(picked,false);
assert.deepEqual(dir.writes,[]);
assert.match(nodes.get('#rv-status').textContent,/permission.*Nothing was saved.*kept in this tab/i);
""", pre="const dir=makeDir('reports',{'review.html':PAGE_TEXT},'denied');useStoredDir(dir);")

    def test_cancelled_picker_saves_nothing(self):
        self.run_js("""
test.set([{id:'one',quote:'q',comment:'keep',at:'a'}]);
global.window={showDirectoryPicker:async()=>{throw Object.assign(Error('cancel'),{name:'AbortError'})}};
await nodes.get('#rv-save').events.click();
assert.match(nodes.get('#rv-status').textContent,/AbortError: cancel.*Nothing was saved/);
""")

    def test_failure_status_shows_error_name_and_message(self):
        self.run_js("""
test.set([{id:'one',quote:'q',comment:'keep',at:'a'}]);
global.window={showDirectoryPicker:async()=>{throw Object.assign(Error('Must be handling a user gesture'),{name:'SecurityError'})}};
await nodes.get('#rv-save').events.click();
assert.match(nodes.get('#rv-status').textContent,/SecurityError: Must be handling a user gesture.*Nothing was saved/);
""")

    def test_picker_is_called_before_any_await_when_no_folder_is_stored(self):
        # Transient user activation can be lost across awaits; the picker must be the click's first async step.
        self.run_js("""
await settle();
let inClick=false,calledInClick=null;
global.window={showDirectoryPicker:()=>{calledInClick=inClick;return new Promise(()=>{})}};
inClick=true;nodes.get('#rv-save').events.click();inClick=false;
assert.equal(calledInClick,true,'showDirectoryPicker was not called synchronously from the click');
""")

    def test_permission_is_requested_before_any_await_when_folder_is_stored(self):
        self.run_js("""
await settle();
inClick=true;nodes.get('#rv-save').events.click();inClick=false;
assert.equal(requestedInClick,true,'requestPermission was not called synchronously from the click');
await settle();
assert.equal(dir.writes[0],'review.json');
assert.match(dir.writes[1],/^review-\\d{8}T\\d{6}Z\\.json$/);
""", pre="""
let inClick=false,requestedInClick=null;
const dir=makeDir('reports',{'review.html':PAGE_TEXT},'prompt');
dir.requestPermission=async()=>{if(requestedInClick===null)requestedInClick=inClick;return 'granted'};
useStoredDir(dir);
global.window={showDirectoryPicker:async()=>{throw Error('picker must not open when a folder is stored')}};
""")

    def test_save_writes_revision_sibling_when_folder_holds_other_revision(self):
        self.run_js("""
await settle();
test.set([{id:'one',quote:'q',comment:'keep',at:'a'}]);
global.window={showDirectoryPicker:async()=>dir};
await nodes.get('#rv-save').events.click();
assert.equal(dir.files['review.json'],wrong);
const alt='review-__VERSION__'.slice(0,'review-'.length+12)+'.json';
assert.equal(dir.writes[0],alt);
assert.match(dir.writes[1],new RegExp('^'+alt.replace('.json','')+'-\\\\d{8}T\\\\d{6}Z\\\\.json$'));
assert.equal(JSON.parse(dir.files[alt]).comments[0].comment,'keep');
assert.match(nodes.get('#rv-status').textContent,/different report revision.*left unchanged.*saved/i);
assert.equal(test.get()[0].comment,'keep');
// A second Save merges from and rewrites the same sibling, still leaving the other revision untouched.
await nodes.get('#rv-save').events.click();
assert.equal(dir.files['review.json'],wrong);
assert.deepEqual(dir.writes.filter(n=>!/-\\d{8}T\\d{6}Z\\.json$/.test(n)),[alt,alt]);
assert.equal(dir.writes.length,4);
""", pre="""
const wrong=JSON.stringify({page:'__PAGE__',report_version:'older',comments:[{id:'x',quote:'q',comment:'theirs',at:'a'}]});
const dir=makeDir('reports',{'review.html':PAGE_TEXT,'review.json':wrong});
useStoredDir(dir);
""")

    def test_open_loads_comments_saved_beside_page(self):
        self.run_js("""
await new Promise(r=>setTimeout(r,20));
assert.equal(test.get().length,1);
assert.equal(test.get()[0].comment,'saved earlier');
assert.match(nodes.get('#rv-status').textContent,/Loaded 1 saved comment/);
""", pre="""
const saved=JSON.stringify({page:'__PAGE__',report_version:'__VERSION__',comments:[{id:'s',quote:'q',comment:'saved earlier',at:'a'}]});
useStoredDir(makeDir('reports',{'review.html':PAGE_TEXT,'review.json':saved}));
""")

    def test_open_without_permission_does_not_prompt(self):
        self.run_js("""
await new Promise(r=>setTimeout(r,20));
assert.equal(test.get().length,0);
assert.equal(asked,false);
""", pre="""
let asked=false;const d=makeDir('reports',{'review.html':PAGE_TEXT},'prompt');d.requestPermission=async()=>{asked=true;return 'granted'};
useStoredDir(d);
""")

    def test_imported_deletion_keeps_locally_edited_comment(self):
        self.run_js("""
test.set([{id:'one',quote:'q',comment:'old',at:'a'},{id:'two',quote:'q',comment:'plain',at:'b'}]);
nodes.get('#rv-list').events.input({target:{dataset:{i:'0'},value:'edited here'}});
global.FileReader=class{readAsText(){this.result=JSON.stringify({page:'__PAGE__',report_version:'__VERSION__',comments:[],deleted_ids:['one','two']});this.onload()}};
nodes.get('#rv-load').events.change({target:{files:[{}],value:'x'}});
assert.deepEqual(test.get().map(c=>c.id),['one']);
assert.equal(test.get()[0].comment,'edited here');
assert.deepEqual(JSON.parse(test.payload()).deleted_ids,['two']);
assert.match(nodes.get('#rv-status').textContent,/1 comment edited here was kept/);
""")

    def test_corrupt_store_warning_survives_other_revision_notice(self):
        older = json.dumps({"page": "__PAGE__", "report_version": "older", "comments": [{"id": "a", "quote": "q", "comment": "c", "at": "t"}]})
        self.run_js("""
const status=nodes.get('#rv-status').textContent;
assert.match(status,/could not be loaded/);
assert.match(status,/other revisions/);
test.set([{id:'new',quote:'q',comment:'new',at:'b'}]);
nodes.get('#rv-list').events.input({target:{dataset:{i:'0'},value:'edited'}});
assert.equal(storage.get('__KEY__|__VERSION__|unreadable'),'{not json');
""", extra={"__KEY__|__VERSION__": "{not json", "__KEY__|older": older})

    def test_imported_edit_timestamp_does_not_protect_against_deletion(self):
        self.run_js("""
const load=data=>{global.FileReader=class{readAsText(){this.result=JSON.stringify(data);this.onload()}};nodes.get('#rv-load').events.change({target:{files:[{}],value:'x'}})};
load({page:'__PAGE__',report_version:'__VERSION__',comments:[{id:'one',quote:'q',comment:'theirs',at:'a',edited_at:'remote'}]});
assert.equal(test.get().length,1);
load({page:'__PAGE__',report_version:'__VERSION__',comments:[],deleted_ids:['one']});
assert.equal(test.get().length,0);
assert.deepEqual(JSON.parse(test.payload()).deleted_ids,['one']);
""")

    def test_local_edit_protection_survives_reload_from_own_store(self):
        own = json.dumps({"page": "__PAGE__", "report_version": "__VERSION__", "comments": [{"id": "one", "quote": "q", "comment": "mine", "at": "a", "edited_at": "t"}], "deleted_ids": []})
        self.run_js("""
global.FileReader=class{readAsText(){this.result=JSON.stringify({page:'__PAGE__',report_version:'__VERSION__',comments:[],deleted_ids:['one']});this.onload()}};
nodes.get('#rv-load').events.change({target:{files:[{}],value:'x'}});
assert.equal(test.get().length,1);
assert.equal(test.get()[0].comment,'mine');
""", extra={"__KEY__|__VERSION__": own})

    def test_failed_backup_of_unreadable_store_blocks_overwrite(self):
        self.run_js("""
assert.match(nodes.get('#rv-status').textContent,/could not be copied/);
test.set([{id:'new',quote:'q',comment:'new',at:'b'}]);
nodes.get('#rv-list').events.input({target:{dataset:{i:'0'},value:'edited'}});
assert.equal(storage.get('__KEY__|__VERSION__'),'{not json');
assert.match(nodes.get('#rv-status').textContent,/Save comments/);
""", extra={"__KEY__|__VERSION__": "{not json"},
            pre="const realSet=global.localStorage.setItem;global.localStorage.setItem=function(k,v){if(k.endsWith('|unreadable'))throw Error('quota');return realSet.call(this,k,v)};")

    def test_kept_count_does_not_leak_into_next_folder_operation(self):
        self.run_js("""
test.set([{id:'one',quote:'q',comment:'old',at:'a'}]);
nodes.get('#rv-list').events.input({target:{dataset:{i:'0'},value:'edited here'}});
const del={page:'__PAGE__',report_version:'__VERSION__',comments:[],deleted_ids:['one']};
await test.mergeFrom({getFileHandle:async()=>({getFile:async()=>({text:async()=>JSON.stringify(del)})})});
global.window={showDirectoryPicker:async()=>makeDir('empty',{'review.html':PAGE_TEXT})};
await nodes.get('#rv-change').events.click();
assert.match(nodes.get('#rv-status').textContent,/Folder set to empty/);
assert.doesNotMatch(nodes.get('#rv-status').textContent,/edited here/);
""")

    def test_save_writes_revision_sibling_when_folder_export_is_malformed(self):
        self.run_js("""
test.set([{id:'one',quote:'q',comment:'keep',at:'a'}]);
const dir=makeDir('reports',{'review.html':PAGE_TEXT,'review.json':'{not json'});
global.window={showDirectoryPicker:async()=>dir};
await nodes.get('#rv-save').events.click();
assert.equal(dir.files['review.json'],'{not json');
assert.equal(dir.writes.length,2);
assert.notEqual(dir.writes[0],'review.json');
assert.equal(dir.writes[1],dir.writes[0].replace(/\\.json$/,'')+dir.writes[1].slice(-22));
assert.match(dir.writes[1],/-\\d{8}T\\d{6}Z\\.json$/);
assert.equal(JSON.parse(dir.files[dir.writes[0]]).comments[0].comment,'keep');
assert.match(nodes.get('#rv-status').textContent,/could not be merged.*left unchanged/i);
""")

    def test_save_stops_when_sibling_is_also_unreadable(self):
        self.run_js("""
test.set([{id:'one',quote:'q',comment:'keep',at:'a'}]);
const alt='review-'+'__VERSION__'.slice(0,12)+'.json';
const dir=makeDir('reports',{'review.html':PAGE_TEXT,'review.json':'{not json',[alt]:'{also bad'});
global.window={showDirectoryPicker:async()=>dir};
await nodes.get('#rv-save').events.click();
assert.deepEqual(dir.writes,[]);
assert.equal(dir.files[alt],'{also bad');
assert.match(nodes.get('#rv-status').textContent,/Nothing was saved/);
""")

    def test_committed_demo_matches_current_generator(self):
        source = TOOL.read_text(encoding="utf-8")
        layer = re.search(r'LAYER = r"""(.*?)"""', source, re.S)[1]
        pattern = re.sub(r'"__[A-Z]+__(?:\\\.json)?"', '"[^"\\\\n]*"', re.escape(layer))
        demo = (TOOL.parent / "demo" / "example-report-review.html").read_text(encoding="utf-8")
        self.assertIsNotNone(re.search(pattern, demo), "demo review copy is stale: regenerate it per README")
        folder = json.loads(re.search(r'FOLDER=("(?:[^"\\]|\\.)*")', demo)[1])
        self.assertNotRegex(folder, r'^([A-Za-z]:|[\\/])', "demo embeds an absolute local path")

    def test_generator_emits_noscript_note(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'report.html'
            output = Path(directory) / 'review.html'
            source.write_text('<body>Original</body>', encoding='utf-8')
            subprocess.run([sys.executable, str(TOOL), str(source), str(output), 'k', 'comments'], check=True, capture_output=True)
            self.assertIn('<noscript>', output.read_text(encoding='utf-8'))

    def test_export_name_is_optional_and_not_used_for_the_file_name(self):
        # The saved JSON is named after the page (<page stem>.json); EXPORT_NAME is accepted for compatibility only.
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'report.html'
            source.write_text('<body>Original</body>', encoding='utf-8')
            three = Path(directory) / 'three.html'
            r = subprocess.run([sys.executable, str(TOOL), str(source), str(three), 'k'], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            four = Path(directory) / 'four.html'
            r = subprocess.run([sys.executable, str(TOOL), str(source), str(four), 'k', 'zzz-legacy-export'], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertNotIn('zzz-legacy-export', four.read_text(encoding='utf-8'))

    def test_generator_rejects_source_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'report.html'
            source.write_text('<body>Original</body>', encoding='utf-8')
            original = source.read_bytes()
            result = subprocess.run([sys.executable, str(TOOL), str(source), str(source), 'key', 'comments'], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(source.read_bytes(), original)

    def test_generator_encodes_javascript_parameters(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'report.html'
            output = Path(directory) / 'review.html'
            source.write_text('<body>Original</body>', encoding='utf-8')
            result = subprocess.run([sys.executable, str(TOOL), str(source), str(output), 'x";alert(1);//</script>', 'comments'], capture_output=True)
            self.assertEqual(result.returncode, 0)
            scripts = re.findall(r'<script id="rv-script">(.*?)</script>', output.read_text(encoding='utf-8'), re.S)
            self.assertEqual(len(scripts), 1)
            checked = subprocess.run(['node', '--check'], input=scripts[0], text=True, capture_output=True)
            self.assertEqual(checked.returncode, 0, checked.stderr)
            self.assertIsNone(re.search(r"__[A-Z]+__", output.read_text(encoding='utf-8')))
            key = re.search(r'const KEY=(".*?(?<!\\)");', scripts[0])[1]
            self.assertEqual(json.loads(key), 'x";alert(1);//</script>')


if __name__ == "__main__":
    unittest.main()
