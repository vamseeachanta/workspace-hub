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
    def run_js(self, assertions, stored=None, extra=None):
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
"""
        initial = "storage.set('__KEY__'," + json.dumps(stored) + ");\n" if stored is not None else ""
        initial += "".join(f"storage.set({json.dumps(k)},{json.dumps(v)});\n" for k, v in (extra or {}).items())
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

    def test_save_falls_back_to_download_when_folder_holds_other_revision(self):
        self.run_js("""
test.set([{id:'one',quote:'q',comment:'keep',at:'a'}]);
const wrong={page:'__PAGE__',report_version:'older',comments:[]};
let written=false;
const dir={name:'d',queryPermission:async()=>'granted',getFileHandle:async(n,o)=>{if(o&&o.create){written=true;return {createWritable:async()=>({write:async()=>{},close:async()=>{}})}}return {getFile:async()=>({text:async()=>JSON.stringify(wrong)})}}};
global.window={showDirectoryPicker:async()=>dir};
global.indexedDB={open:()=>{const r={};setTimeout(()=>{r.result={transaction:()=>{const tx={objectStore:()=>({get:()=>({result:dir}),put:()=>({})})};setTimeout(()=>tx.oncomplete&&tx.oncomplete(),0);return tx}};r.onsuccess&&r.onsuccess()},0);return r}};
let clicked=false;
global.URL={createObjectURL:()=>'blob:x'};global.Blob=class{};
document.createElement=()=>({click(){clicked=true},remove(){}});document.body.append=()=>{};
await nodes.get('#rv-save').events.click();
assert.equal(written,false);
assert.equal(clicked,true);
assert.match(nodes.get('#rv-status').textContent,/different report revision/i);
assert.equal(test.get()[0].comment,'keep');
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

    def test_save_falls_back_to_download_when_folder_export_is_malformed(self):
        self.run_js("""
test.set([{id:'one',quote:'q',comment:'keep',at:'a'}]);
let written=false;
const dir={name:'d',queryPermission:async()=>'granted',getFileHandle:async(n,o)=>{if(o&&o.create){written=true;return {createWritable:async()=>({write:async()=>{},close:async()=>{}})}}return {getFile:async()=>({text:async()=>'{not json'})}}};
global.window={showDirectoryPicker:async()=>dir};
global.indexedDB={open:()=>{const r={};setTimeout(()=>{r.result={transaction:()=>{const tx={objectStore:()=>({get:()=>({result:dir}),put:()=>({})})};setTimeout(()=>tx.oncomplete&&tx.oncomplete(),0);return tx}};r.onsuccess&&r.onsuccess()},0);return r}};
let clicked=false;
global.URL={createObjectURL:()=>'blob:x'};global.Blob=class{};
document.createElement=()=>({click(){clicked=true},remove(){}});document.body.append=()=>{};
await nodes.get('#rv-save').events.click();
assert.equal(written,false);
assert.equal(clicked,true);
assert.match(nodes.get('#rv-status').textContent,/could not be merged/i);
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
