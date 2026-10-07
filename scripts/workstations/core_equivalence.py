"""Read-only lean source contract; runtime and role evidence stay separate."""
from __future__ import annotations
import hashlib,os,platform,re,subprocess
from pathlib import Path
import yaml
from clone_profile import _read_metadata,_relative,_unchanged,_environment,_origin_url
from repo_footprint import _selection,_has_symlink_component

class UniqueLoader(yaml.SafeLoader):pass
def origin_digest(url:str)->str:
    return hashlib.sha256(url.removesuffix('.git').encode()).hexdigest()
def _mapping(loader,node,deep=False):
    pairs=loader.construct_pairs(node,deep=deep);result={}
    for key,value in pairs:
        if key in result:raise ValueError('duplicate profile key')
        result[key]=value
    return result
UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,_mapping)

def load_profile(path:Path,data:dict)->dict:
    raw=_read_metadata(Path(path),1024*1024)
    try:p=yaml.load(raw,Loader=UniqueLoader)
    except (yaml.YAMLError,TypeError) as exc:raise ValueError('malformed lean core profile') from None
    if not isinstance(p,dict) or type(p.get('schema_version')) is not int or p.get('schema_version')!=1 or not isinstance(p.get('profile_id'),str):raise ValueError('unsupported lean core profile')
    if not isinstance(p.get('membership_machine'),str):raise ValueError('profile needs existing registry membership authority')
    _,names,source=_selection(data,p['membership_machine'],'required')
    recipes=p.get('repositories')
    if not isinstance(recipes,dict) or set(recipes)!=set(names):raise ValueError('profile must cover every registry-required repository exactly')
    if type(p.get('budget_bytes')) is not int or not 0<p['budget_bytes']<=3_000_000_000:raise ValueError('invalid allocated core budget')
    for recipe in recipes.values():
        if not isinstance(recipe,dict) or not re.fullmatch('[0-9a-f]{40}',str(recipe.get('revision',''))):raise ValueError('profile requires explicit tested revision')
        if recipe.get('clone_policy') not in {'new_destination','sanitized_existing_only'}:raise ValueError('unsupported clone policy')
        if not isinstance(recipe.get('origin_url_sha256'),str) or not re.fullmatch('[0-9a-f]{64}',recipe['origin_url_sha256']):raise ValueError('invalid direct origin identity digest')
        for key in ('include_directories','required_paths'):
            values=recipe.get(key)
            if not isinstance(values,list) or not values or len(values)>20 or any(not isinstance(v,str) for v in values):raise ValueError('invalid selected profile paths')
            if len(set(values))!=len(values) or any(len(v)>255 or not _relative(v,allow_hidden=True) for v in values):raise ValueError('unsafe selected profile path')
        digests=recipe.get('required_digests',{})
        if not isinstance(digests,dict) or set(digests)!=set(recipe['required_paths']) or any(not isinstance(v,str) or not re.fullmatch('[0-9a-f]{64}',v) for v in digests.values()):raise ValueError('every required file needs reviewed content digest')
    return dict(p,selected_repositories=names,membership_source=source,profile_sha256=hashlib.sha256(raw.replace('\r\n','\n').encode()).hexdigest())

def _digest(path:Path)->str:
    before=path.stat()
    with path.open('rb') as stream:raw=stream.read(2*1024*1024+1)
    after=path.stat()
    if len(raw)>2*1024*1024 or (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)!=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns):raise ValueError('unavailable or changing approved file')
    return hashlib.sha256(raw.replace(b'\r\n',b'\n')).hexdigest()

def observe(data:dict,machine:str,root:Path,p:dict,*,run=None,hostname=None,os_name=None)->dict:
    run=run or subprocess.run;root=Path(root)
    target=(data.get('machines') or {}).get(machine)
    if not isinstance(target,dict) or not root.is_absolute():raise ValueError('explicit existing machine and absolute core root required')
    hostname=hostname or platform.node();os_name=os_name or {'Windows':'windows','Darwin':'macos','Linux':'linux'}.get(platform.system(),'unknown')
    aliases=[target.get('hostname'),*(target.get('hostname_aliases') or [])]
    identity=hostname.casefold() in {str(v).casefold() for v in aliases if v} and os_name==target.get('os')
    env=dict(_environment(),GIT_NO_LAZY_FETCH='1',GIT_OPTIONAL_LOCKS='0');rows=[]
    for name in p['selected_repositories']:
        path=root/name;recipe=p['repositories'][name];issues=[];unknown=False
        row={'repository':name,'expected_revision':recipe['revision'],'clone_policy':recipe['clone_policy']}
        try:
            if _has_symlink_component(path) or _has_symlink_component(path/'.git') or not path.is_dir() or not os.path.lexists(path/'.git'):raise ValueError('repository_unavailable_or_redirected')
            info=path.lstat();anchor=(info.st_dev,info.st_ino)
            if recipe.get('origin_url_sha256'):
                origin,_=_origin_url(path,name)
                if origin_digest(origin)!=recipe['origin_url_sha256']:issues.append('direct_origin_identity_mismatch')
            git=['git','--no-optional-locks','-c','core.fsmonitor=false','-C',str(path)]
            head=run(git+['rev-parse','--verify','HEAD'],env=env,capture_output=True,text=True,timeout=20)
            status=run(git+['status','--porcelain=v1','-z','--untracked-files=no'],env=env,capture_output=True,text=True,timeout=20)
            _unchanged(path,anchor)
            if head.returncode or status.returncode:raise ValueError('git_inspection_unavailable')
            pin=head.stdout.strip()
            if not re.fullmatch('[0-9a-f]{40}',pin):raise ValueError('git_revision_unavailable')
            row['observed_revision']=pin
            if pin!=recipe['revision']:issues.append('revision_mismatch')
            missing=[v for v in recipe['required_paths'] if _has_symlink_component(path/v) or not (path/v).exists()]
            row['missing_or_redirected_required_paths']=missing
            if missing:issues.append('required_path_unavailable')
            accepted=set()
            for relative,wanted in recipe.get('required_digests',{}).items():
                file=path/relative
                if _has_symlink_component(file) or not file.is_file():raise ValueError('approved_file_unavailable_or_redirected')
                if _digest(file)==wanted:accepted.add(relative)
                else:issues.append('approved_working_file_digest_mismatch')
            entries=[v for v in status.stdout.split('\0') if v]
            if any(len(v)<4 or v[:2]!=' M' or v[3:] not in accepted for v in entries):issues.append('unapproved_tracked_working_change')
            row['tracked_status_entries']=len(entries)
            final_head=run(git+['rev-parse','--verify','HEAD'],env=env,capture_output=True,text=True,timeout=20)
            final_status=run(git+['status','--porcelain=v1','-z','--untracked-files=no'],env=env,capture_output=True,text=True,timeout=20)
            if final_head.returncode or final_status.returncode or final_head.stdout!=head.stdout or final_status.stdout!=status.stdout:raise ValueError('git_state_changed_or_unavailable')
            _unchanged(path,anchor)
        except (OSError,ValueError,subprocess.TimeoutExpired):
            unknown=True;issues.append('inspection_unavailable')
        row.update(status='indeterminate' if unknown else 'different' if issues else 'equivalent',reason_codes=sorted(set(issues)));rows.append(row)
    states={r['status'] for r in rows}
    return {'schema_version':1,'profile_id':p['profile_id'],'profile_sha256':p['profile_sha256'],'target_machine':machine,
            'membership_source':p['membership_source'],'selected_repositories':p['selected_repositories'],'repositories':rows,
            'source_parity':'indeterminate' if 'indeterminate' in states else 'different' if 'different' in states else 'equivalent',
            'observed_identity':{'hostname':hostname,'os':os_name},'identity_matches':identity,
            'machine_roles':(target.get('harness_profile') or {}).get('roles',[]),
            'role_authority':'existing registry harness_profile plus config/workstations/harness-roles.yaml; declarations, not live license/GPU proof',
            'runtime_status':'not_verified','agent_runtime_qualified':False,
            'runtime_evidence_authority':'existing readiness provider_harness_parity, equality collectors/matrix and Foundation profile; not invoked by this checker',
            'scope':'pinned required source paths and approved working-file digests; ignored/task files governed separately by complete footprint and owners; no fleet/runtime/security attestation'}
