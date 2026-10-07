"""Contract tests use local fixtures; no provider invocation, network or installs."""
import hashlib,importlib.util,json,os,subprocess,sys
from pathlib import Path
import pytest,yaml
ROOT=Path(__file__).resolve().parents[2];HELPER=ROOT/'scripts/workstations/core_equivalence.py'
@pytest.fixture
def mod():
    sys.path.insert(0,str(HELPER.parent))
    try:
        spec=importlib.util.spec_from_file_location('core_equivalence',HELPER);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
    finally:sys.path.pop(0)
@pytest.fixture
def fixture(tmp_path):
    data={'machines':{'authority':{'repos':['one','two','noncore'],'tier1_baseline':{'required':['one','two']}},'target':{'hostname':'host','os':'windows','harness_profile':{'roles':['licensed-solver']}}}}
    profile={'schema_version':1,'profile_id':'fixture','membership_machine':'authority','budget_bytes':3000000000,'repositories':{r:{'revision':'a'*40,'origin_url_sha256':hashlib.sha256(('https://example.invalid/'+r).encode()).hexdigest(),'include_directories':['src'],'required_paths':['src/module.py'],'required_digests':{'src/module.py':hashlib.sha256(b'pass\n').hexdigest()},'clone_policy':'new_destination'} for r in ('one','two')}}
    path=tmp_path/'profile.yaml';path.write_text(yaml.safe_dump(profile));root=tmp_path/'core';root.mkdir()
    for r in ('one','two'):
        p=root/r;(p/'.git/objects').mkdir(parents=True);(p/'.git/HEAD').write_text('ref: refs/heads/main\n');(p/'.git/config').write_text('[remote "origin"]\nurl = https://example.invalid/'+r+'.git\n');(p/'src').mkdir();(p/'src/module.py').write_text('pass\n')
    return data,profile,path,root
def runner(head='a'*40,dirty='',fail=False):
    def run(cmd,**kwargs):
        assert kwargs['env']['GIT_NO_LAZY_FETCH']=='1';assert kwargs['env']['GIT_OPTIONAL_LOCKS']=='0'
        return subprocess.CompletedProcess(cmd,1 if fail else 0,head+'\n' if 'rev-parse' in cmd else dirty,'never expose this stderr')
    return run
def test_membership_comes_from_existing_authority_even_target_has_no_baseline(mod,fixture):
    data,profile,path,root=fixture;loaded=mod.load_profile(path,data)
    assert loaded['selected_repositories']==['one','two']
    report=mod.observe(data,'target',root,loaded,run=runner(),hostname='HOST',os_name='windows')
    assert report['source_parity']=='equivalent';assert report['identity_matches']
    assert report['machine_roles']==['licensed-solver'];assert report['agent_runtime_qualified'] is False
    assert report['runtime_status']=='not_verified'
@pytest.mark.parametrize('change',['missing','extra','bad_revision','unsafe_path','duplicate_path','bad_budget','bad_schema','bad_clone_policy'])
def test_malformed_or_excluding_profiles_fail_closed(mod,fixture,change):
    data,p,path,root=fixture
    if change=='missing':p['repositories'].pop('two')
    elif change=='extra':p['repositories']['extra']=p['repositories']['one']
    elif change=='bad_revision':p['repositories']['one']['revision']='main'
    elif change=='unsafe_path':p['repositories']['one']['include_directories']=['src/.Git']
    elif change=='duplicate_path':p['repositories']['one']['include_directories']=['src','src']
    elif change=='bad_budget':p['budget_bytes']=0
    elif change=='bad_schema':p['schema_version']=2
    else:p['repositories']['one']['clone_policy']='delete_old'
    path.write_text(yaml.safe_dump(p))
    with pytest.raises(ValueError):mod.load_profile(path,data)
def test_duplicate_yaml_keys_rejected(mod,fixture):
    data,p,path,root=fixture;path.write_text(path.read_text()+'schema_version: 1\n')
    with pytest.raises(ValueError):mod.load_profile(path,data)
@pytest.mark.parametrize('kind',['missing_repo','missing_path','wrong_head','dirty','git_failure','redirect'])
def test_missing_different_and_uninspectable_not_equivalent(mod,fixture,kind):
    data,p,path,root=fixture;loaded=mod.load_profile(path,data);run=runner()
    if kind=='missing_repo':
        root=root.parent/'partial';(root/'one/.git').mkdir(parents=True);(root/'one/src').mkdir();(root/'one/src/module.py').write_text('pass\n')
    elif kind=='missing_path':(root/'one/src/module.py').unlink()
    elif kind=='wrong_head':run=runner(head='b'*40)
    elif kind=='dirty':run=runner(dirty=' M src/other.py\0')
    elif kind=='git_failure':run=runner(fail=True)
    else:
        (root/'one/src/module.py').unlink()
        try:(root/'one/src/module.py').symlink_to(root/'two/src/module.py')
        except OSError:pytest.skip('no symlink privilege; native redirect guard covered separately')
    report=mod.observe(data,'target',root,loaded,run=run,hostname='host',os_name='windows')
    assert report['source_parity']!='equivalent'
    assert len(report['repositories'])==2
    assert 'never expose' not in json.dumps(report)
def test_authorized_working_digest_is_normalized_and_other_dirty_files_still_fail(mod,fixture):
    import hashlib
    data,p,path,root=fixture
    p['repositories']['one']['required_digests']={'src/module.py':hashlib.sha256(b'pass\n').hexdigest()}
    path.write_text(yaml.safe_dump(p));(root/'one/src/module.py').write_bytes(b'pass\r\n')
    loaded=mod.load_profile(path,data)
    report=mod.observe(data,'target',root,loaded,run=runner(dirty=' M src/module.py\0 M src/other.py\0'),hostname='host',os_name='windows')
    # A matching approved file never permits an additional dirty path.
    assert report['source_parity']=='different'
    (root/'one/src/module.py').write_bytes(b'changed\n')
    assert mod.observe(data,'target',root,loaded,run=runner(),hostname='host',os_name='windows')['source_parity']=='different'
def test_wrong_machine_identity_not_concealed_by_matching_source(mod,fixture):
    data,p,path,root=fixture;r=mod.observe(data,'target',root,mod.load_profile(path,data),run=runner(),hostname='other',os_name='linux')
    assert r['source_parity']=='equivalent';assert not r['identity_matches'];assert not r['agent_runtime_qualified']

def test_checker_profile_receipt_uses_all_authority_members_and_preserves_runtime_unknown(fixture,tmp_path):
    data,p,path,root=fixture
    for name in ('one','two'):
        repo=root/name
        for args in (['init','-q'],['config','core.autocrlf','false'],['add','src/module.py'],['-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm','fixture']):
            subprocess.run(['git','-C',str(repo),*args],check=True,capture_output=True)
        p['repositories'][name]['revision']=subprocess.run(['git','-C',str(repo),'rev-parse','HEAD'],check=True,capture_output=True,text=True).stdout.strip()
    import platform
    data['machines']['target'].update(hostname=platform.node(),os={'Windows':'windows','Darwin':'macos','Linux':'linux'}[platform.system()])
    registry=tmp_path/'registry.yaml';registry.write_text(yaml.safe_dump(data));path.write_text(yaml.safe_dump(p))
    script=ROOT/'scripts/workstations/check-tier1-repo-baseline.py'
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
    args=[sys.executable,'-B',str(script),'--registry',str(registry),'--machine','target','--repo-root',str(root),'--footprint-only','--core-profile',str(path)]
    before=sorted(root.rglob('*'));result=subprocess.run(args,env=env,capture_output=True,text=True,timeout=30)
    assert result.returncode==0,result.stderr
    report=json.loads(result.stdout)
    assert report['selected_repositories']==['one','two'];assert report['target_machine_id']=='target';assert report['membership_machine_id']=='authority'
    assert report['core_contract']['source_parity']=='equivalent';assert report['core_contract']['agent_runtime_qualified'] is False
    assert sorted(root.rglob('*'))==before
    result=subprocess.run(args+['--footprint-selection','registered'],env=env,capture_output=True,text=True,timeout=30)
    assert result.returncode!=0

def test_profile_clone_plan_blocks_sanitized_existing_only_and_never_clones(fixture,tmp_path):
    data,p,path,root=fixture;p['repositories']['one']['clone_policy']='sanitized_existing_only';path.write_text(yaml.safe_dump(p))
    registry=tmp_path/'registry.yaml';registry.write_text(yaml.safe_dump(data));urls=tmp_path/'repos.conf';urls.write_text('one=https://example.invalid/one.git\n')
    script=ROOT/'scripts/workstations/clone_profile.py'
    result=subprocess.run([sys.executable,'-B',str(script),'one','--profile','lean','--destination',str(tmp_path/'one'),'--machine','authority','--registry',str(registry),'--repos-config',str(urls),'--baseline-profile',str(path),'--dry-run'],capture_output=True,text=True,timeout=20)
    assert result.returncode!=0;assert 'sanitized existing' in result.stderr;assert not (tmp_path/'one').exists()

def test_profile_clone_plan_reuses_recipe_pin_without_mutation(fixture,tmp_path):
    data,p,path,root=fixture
    registry=tmp_path/'registry.yaml';registry.write_text(yaml.safe_dump(data));urls=tmp_path/'repos.conf';urls.write_text('one=https://example.invalid/one.git\n')
    script=ROOT/'scripts/workstations/clone_profile.py'
    result=subprocess.run([sys.executable,'-B',str(script),'one','--profile','lean','--destination',str(tmp_path/'one'),'--machine','authority','--registry',str(registry),'--repos-config',str(urls),'--baseline-profile',str(path),'--dry-run'],capture_output=True,text=True,timeout=20)
    assert result.returncode==0,result.stderr;plan=json.loads(result.stdout)
    assert plan['expected_head']=='a'*40;assert plan['include_directories']==['src'];assert not (tmp_path/'one').exists()

def test_conflicting_origin_stops_profile_clone_before_destination(fixture,tmp_path):
    import hashlib
    data,p,path,root=fixture
    p['repositories']['one']['origin_url_sha256']=hashlib.sha256(b'https://example.invalid/reviewed').hexdigest()
    path.write_text(yaml.safe_dump(p));registry=tmp_path/'registry.yaml';registry.write_text(yaml.safe_dump(data))
    urls=tmp_path/'repos.conf';urls.write_text('one=https://example.invalid/legacy.git\n')
    result=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/workstations/clone_profile.py'),'one','--profile','lean','--destination',str(tmp_path/'one'),'--machine','authority','--registry',str(registry),'--repos-config',str(urls),'--baseline-profile',str(path),'--dry-run'],capture_output=True,text=True,timeout=20)
    assert result.returncode!=0;assert not (tmp_path/'one').exists()

def test_origin_identity_digest_normalizes_only_git_suffix(mod):
    assert mod.origin_digest('https://example.invalid/one.git')==mod.origin_digest('https://example.invalid/one')
    assert mod.origin_digest('https://example.invalid/other')!=mod.origin_digest('https://example.invalid/one')

@pytest.mark.parametrize('field',['origin_url_sha256','required_digests'])
def test_omitted_identity_or_content_binding_is_rejected(mod,fixture,field):
    data,p,path,root=fixture;p['repositories']['one'].pop(field);path.write_text(yaml.safe_dump(p))
    with pytest.raises(ValueError):mod.load_profile(path,data)

def test_staged_change_never_accepted_as_working_overlay(mod,fixture):
    data,p,path,root=fixture
    report=mod.observe(data,'target',root,mod.load_profile(path,data),run=runner(dirty='M  src/module.py\0'),hostname='host',os_name='windows')
    assert report['source_parity']=='different'

def test_hidden_required_content_change_rejected_without_git_dirty_status(mod,fixture):
    data,p,path,root=fixture;(root/'one/src/module.py').write_text('hidden change\n')
    report=mod.observe(data,'target',root,mod.load_profile(path,data),run=runner(),hostname='host',os_name='windows')
    assert report['source_parity']=='different'

def test_revision_change_during_observation_is_indeterminate(mod,fixture):
    data,p,path,root=fixture;calls={}
    def changing(cmd,**kwargs):
        if 'rev-parse' in cmd:
            key=cmd[cmd.index('-C')+1];calls[key]=calls.get(key,0)+1
            return subprocess.CompletedProcess(cmd,0,('a' if calls[key]==1 else 'b')*40+'\n','')
        return runner()(cmd,**kwargs)
    report=mod.observe(data,'target',root,mod.load_profile(path,data),run=changing,hostname='host',os_name='windows')
    assert report['source_parity']=='indeterminate'
