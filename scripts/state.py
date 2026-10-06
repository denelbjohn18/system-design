"""Local state store: canonical JSON, locked writes, CAS revisions and backups.
Markdown files are derived views, not the source of truth. No network access.
"""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import sys
import tempfile
import uuid

SCHEMA = 1
MAX_BYTES = 2_000_000
INTERVALS = (1, 3, 7, 14, 30)
PLUGIN = Path(__file__).resolve().parents[1]

class StateError(Exception):
    pass


def utc(value):
    try:
        out = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
        if out.tzinfo is None:
            raise ValueError()
        return out.astimezone(dt.timezone.utc)
    except (ValueError, AttributeError, TypeError):
        raise StateError('Use an ISO timestamp with timezone.')


def safe_root(raw):
    root = Path(raw).expanduser().absolute()
    if not root.is_dir() or root.is_symlink():
        raise StateError('Select a real, non-symlink workspace directory.')
    # Reject linked ancestors as well as the selected leaf.
    if any(p.is_symlink() for p in (root, *root.parents)):
        raise StateError('Workspace ancestry contains a symlink.')
    root = root.resolve()
    if root in (Path.home().resolve(), Path(root.anchor)) or root == PLUGIN or PLUGIN in root.parents:
        raise StateError('Select a dedicated study workspace, not home/root/plugin.')
    return root


def directory(root, create=False):
    state = root / '.system-design'
    if state.is_symlink():
        raise StateError('State directory must not be a symlink.')
    if create:
        state.mkdir(exist_ok=True)
    if not state.is_dir():
        raise StateError('No state exists. Run sd-learn onboarding first.')
    return state


def regular(path, required=True):
    if path.is_symlink():
        raise StateError('Linked state files are refused: ' + path.name)
    if path.exists() and not path.is_file():
        raise StateError('Expected a regular file: ' + path.name)
    if required and not path.is_file():
        raise StateError('Missing state file: ' + path.name)
    if path.is_file() and path.stat().st_size > MAX_BYTES:
        raise StateError('State file exceeds size limit: ' + path.name)


def objectives():
    return json.loads((PLUGIN/'objectives.json').read_text(encoding='utf-8'))


def validate(data, root):
    if not isinstance(data, dict) or data.get('schema_version') != SCHEMA:
        raise StateError('Unsupported or missing schema version; explicit migration required.')
    if data.get('workspace_root') != str(root):
        raise StateError('State belongs to a different workspace. Do not inherit its scores.')
    if data.get('curriculum_version') != '2026-10-06.1':
        raise StateError('Curriculum version mismatch; review migration first.')
    if type(data.get('revision')) is not int or data['revision'] < 0:
        raise StateError('Invalid revision.')
    if data.get('mode') not in ('active', 'paused') or not isinstance(data.get('profile'), dict):
        raise StateError('Invalid profile/mode.')
    topics = data.get('concepts')
    if not isinstance(topics, dict) or set(topics) != set(objectives()['concepts']):
        raise StateError('Concept coverage/IDs do not match this curriculum.')
    for key, item in topics.items():
        if not isinstance(item, dict) or item.get('status') not in ('unseen','assisted','provisional','retained','overview','deferred'):
            raise StateError('Invalid concept status: '+key)
        if type(item.get('interval_index')) is not int or not 0 <= item['interval_index'] < len(INTERVALS):
            raise StateError('Invalid interval index: '+key)
        for field in ('due_at','last_independent_at'):
            if item.get(field) is not None:
                utc(item[field])
        if not isinstance(item.get('attempts'), list):
            raise StateError('Invalid attempts: '+key)
    for cid,item in topics.items():
        for attempt in item['attempts']:
            if not isinstance(attempt,dict) or not attempt.get('learner_quote') or not attempt.get('probe'):
                raise StateError('Invalid evidence: '+cid)
            utc(attempt.get('at'))
    if not isinstance(data.get('checkpoint'), dict):
        raise StateError('Invalid checkpoint.')
    return data


def load(root, check_views=True):
    state = directory(root)
    # A broken/edited companion must produce a useful diagnostic, not silent restore.
    for name in (('state.json','profile.md','curriculum.md','progress.md') if check_views else ('state.json',)):
        regular(state/name)
    try:
        data = json.loads((state/'state.json').read_text(encoding='utf-8'))
    except (OSError, ValueError, UnicodeError):
        raise StateError('Cannot parse state.json. Keep files intact and inspect a backup.')
    return validate(data,root)


def atomic(path, content):
    regular(path,required=False)
    fd, temp = tempfile.mkstemp(prefix='.sd-write-',dir=str(path.parent))
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as f:
            f.write(content);f.flush();os.fsync(f.fileno())
        os.replace(temp,path)
    finally:
        if os.path.exists(temp):os.unlink(temp)


def views(data):
    profile = '# Profile (derived view)\nLearning mode: '+data['mode']+'\nRevision: '+str(data['revision'])+'\n'+json.dumps(data['profile'],indent=2,ensure_ascii=False)+'\n'
    rows=['# Curriculum (derived view)','Revision: '+str(data['revision']),'| ID | Concept | Status | Due UTC |','| --- | --- | --- | --- |']
    catalog=objectives()['concepts']
    for key,item in data['concepts'].items():
        rows.append('| '+key+' | '+catalog[key]['label'].replace('|','\\|')+' | '+item['status']+' | '+str(item['due_at'] or '-')+' |')
    progress='# Progress (derived view)\nRevision: '+str(data['revision'])+'\n## Current checkpoint\n'+json.dumps(data['checkpoint'],indent=2,ensure_ascii=False)+'\n\n## Recent evidence\n'
    attempts=[dict(x,concept_id=k) for k,i in data['concepts'].items() for x in i['attempts']]
    attempts.sort(key=lambda x:x['at'])
    progress+=json.dumps(attempts[-20:],indent=2,ensure_ascii=False)+'\n'
    return {'profile.md':profile,'curriculum.md':'\n'.join(rows)+'\n','progress.md':progress}


def commit(root, data, expected=None, initial=False):
    state=directory(root,create=initial)
    lock=state/'.write-lock'
    # mkdir is atomic on local filesystems. Never steal an existing/stale lock silently.
    try:lock.mkdir()
    except FileExistsError:raise StateError('State is locked. Close other sessions; inspect lock before manual recovery.')
    try:
        (lock/'owner.json').write_text(json.dumps({'pid':os.getpid(),'at':dt.datetime.now(dt.timezone.utc).isoformat()}))
        for name in ('state.json','profile.md','curriculum.md','progress.md'):
            regular(state/name,required=False)
        previous=None
        if (state/'state.json').exists():
            previous=load(root,check_views=False)
        if initial:
            if previous is not None or any((state/n).exists() for n in ('profile.md','curriculum.md','progress.md')):
                raise StateError('Existing or legacy state found. No automatic overwrite or migration.')
        elif previous is None or expected != previous['revision']:
            raise StateError('Revision conflict. Read current state and retry intentionally.')
        data['revision']=0 if initial else expected+1
        validate(data,root)
        encoded=json.dumps(data,indent=2,ensure_ascii=False)+'\n'
        if len(encoded.encode())>MAX_BYTES:
            raise StateError('State limit reached. Export/archive history before further writes.')
        # Views first; authoritative JSON last. An interruption can leave stale views,
        # but never a half-written canonical state. repair-views regenerates from JSON.
        if previous is not None:
            backups=state/'backups'
            if backups.is_symlink():raise StateError('Linked backup directory refused.')
            backups.mkdir(exist_ok=True)
            atomic(backups/f'revision-{previous["revision"]:08d}.json',json.dumps(previous,indent=2)+'\n')
        for name,text in views(data).items():atomic(state/name,text)
        atomic(state/'state.json',encoded)
        # Flush directory metadata where the OS supports it.
        try:
            fd=os.open(state,os.O_RDONLY);os.fsync(fd);os.close(fd)
        except OSError:pass
        return data
    finally:
        (lock/'owner.json').unlink(missing_ok=True);lock.rmdir()


def initialize(root,profile):
    concepts={key:{'status':'unseen','interval_index':0,'due_at':None,'last_independent_at':None,'attempts':[]} for key in objectives()['concepts']}
    data={'schema_version':SCHEMA,'curriculum_version':'2026-10-06.1','revision':0,'workspace_root':str(root),'learner_id':str(uuid.uuid4()),'mode':'active','profile':profile,'checkpoint':{'stage':'onboarding','next_opener':'What happens when you open a website?'},'concepts':concepts}
    return commit(root,data,initial=True)


def record(data,cid,result,evidence,when):
    if cid not in data['concepts'] or result not in ('assisted','miss','independent','overview','defer'):
        raise StateError('Unknown concept/result.')
    if not isinstance(evidence,dict) or not evidence.get('learner_quote') or not evidence.get('probe'):
        raise StateError('Evidence requires learner_quote and probe; no bare score updates.')
    now=utc(when);item=data['concepts'][cid];objective=objectives()['concepts'][cid]
    if item['attempts'] and now < utc(item['attempts'][-1]['at']):
        raise StateError('Attempt time precedes existing evidence.')
    if result=='independent':
        if evidence.get('hint_used') is not False or evidence.get('fresh_scenario') is not True:
            raise StateError('Independent result requires no hint and a fresh scenario.')
        needed=objective['dimensions']
        if evidence.get('rubric',{})!={d:2 for d in needed}:
            raise StateError('Independent result requires applicable objective dimensions, all demonstrated.')
        old=utc(item['last_independent_at']) if item['last_independent_at'] else None
        if old and now-old>=dt.timedelta(hours=24) and (not item['due_at'] or now>=utc(item['due_at'])):
            item['status']='retained';item['interval_index']=min(4,item['interval_index']+1)
        else:
            if item['status']!='retained':item['status']='provisional'
            # Same-day fresh practice must not postpone the scheduled recall.
            if old:
                item['attempts'].append(dict(evidence,at=now.isoformat(),result='independent-practice'))
                return data
        item['last_independent_at']=now.isoformat()
    elif result in ('assisted','miss'):
        item['status']='assisted';item['interval_index']=0
        # A failed intervening recall breaks the previous retention streak.
        item['last_independent_at']=None
    elif result=='overview':
        if objective['required']:raise StateError('Required concept cannot pass as overview.')
        item['status']='overview'
    else:item['status']='deferred'
    item['due_at']=(now+dt.timedelta(days=INTERVALS[item['interval_index']])).isoformat() if result not in ('overview','defer') else None
    item['attempts'].append(dict(evidence,at=now.isoformat(),result=result))
    return data


def selection(data,when):
    now=utc(when);order=list(objectives()['concepts'])
    due=[k for k in order if data['concepts'][k]['due_at'] and utc(data['concepts'][k]['due_at'])<=now]
    due.sort(key=lambda k:(utc(data['concepts'][k]['due_at']),0 if data['concepts'][k]['status']=='assisted' else 1,k))
    # Provisional/retained items advance; deferred items don't bounce back immediately.
    next_id=next((k for k in order if data['concepts'][k]['status'] in ('unseen','assisted')),None)
    return {'due_count':len(due),'review_ids':due[:3],'next_concept':next_id,'deferred_ids':[k for k in order if data['concepts'][k]['status']=='deferred']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['init','show','apply','next','repair-views'])
    parser.add_argument('--root',required=True)
    args=parser.parse_args()
    try:
        root=safe_root(args.root)
        if args.command=='init':out=initialize(root,json.load(sys.stdin))
        else:
            data=load(root,check_views=args.command!='repair-views')
            if args.command=='show':out=data
            elif args.command=='next':out=selection(data,dt.datetime.now(dt.timezone.utc).isoformat())
            elif args.command=='repair-views':
                # Normal locked CAS commit regenerates derived files, keeps evidence intact.
                out=commit(root,data,data['revision'])
            else:
                request=json.load(sys.stdin)
                expected=request.get('expected_revision')
                if type(expected) is not int or expected!=data['revision']:raise StateError('Revision conflict.')
                action=request.get('action')
                if action=='attempt':data=record(data,request['concept_id'],request['result'],request['evidence'],request['at'])
                elif action=='checkpoint':
                    if not isinstance(request.get('value'),dict):raise StateError('Checkpoint must be an object.')
                    data['checkpoint']=request['value']
                elif action=='profile':
                    if not isinstance(request.get('value'),dict):raise StateError('Profile must be an object.')
                    data['profile'].update(request['value'])
                elif action=='resume-concept':
                    cid=request.get('concept_id')
                    if cid not in data['concepts'] or data['concepts'][cid]['status']!='deferred':raise StateError('Select a deferred concept.')
                    data['concepts'][cid]['status']='assisted' if data['concepts'][cid]['attempts'] else 'unseen'
                elif action=='mode':
                    if request.get('value') not in ('active','paused'):raise StateError('Invalid mode.')
                    data['mode']=request['value']
                else:raise StateError('Unsupported action; no direct status/replacement writes.')
                out=commit(root,data,expected)
        print(json.dumps(out,ensure_ascii=False))
    except (StateError,OSError,ValueError,KeyError,TypeError) as exc:
        print(json.dumps({'error':str(exc),'saved':False}),file=sys.stderr);return 1
    return 0

if __name__=='__main__':sys.exit(main())
