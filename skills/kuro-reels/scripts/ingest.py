"""Read LINE CSV/ZIP and propose stable chat matches; never generate scripts.
Example: python ingest.py chats.zip --project PROJECT --commit
No third-party dependencies. Raw messages are not printed to the terminal.
"""
import argparse, csv, hashlib, io, json, re, unicodedata, zipfile
from pathlib import Path, PurePosixPath

def norm(s):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', s)).strip()

def digest(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def parse_csv(raw, source):
    rows=list(csv.reader(io.StringIO(raw.decode('utf-8-sig'))))
    header=next((i for i,r in enumerate(rows) if len(r)>=5 and r[0]=='傳送者類型' and r[4]=='內容'),None)
    if header is None: raise ValueError(f'Not a LINE CSV: {source}')
    messages=[]
    for number,r in enumerate(rows[header+1:],header+2):
        if len(r)<5: continue
        messages.append(dict(role=r[0],sender=r[1],date=r[2],time=r[3],text=r[4],record=number))
    user_names=list(dict.fromkeys(m['sender'] for m in messages if m['role']=='User'))
    keys=[digest('\x1f'.join(norm(m[k]) for k in ('role','date','time','text'))) for m in messages]
    anchors=[]
    for m,k in zip(messages,keys):
        if m['role']=='User' and len(norm(m['text']))>=10 and not re.search('已傳送|轉贈|OPENPOINT',m['text']): anchors.append(k)
    return dict(source=source,file_sha256=hashlib.sha256(raw).hexdigest(),snapshot_sha256=digest('\n'.join(keys)),names=user_names,message_keys=keys,anchors=anchors,messages=messages,timezone=next((r[1] for r in rows[:header] if len(r)>1 and r[0]=='時區'),'unknown'))

def sources(path):
    if path.suffix.lower()=='.zip':
        with zipfile.ZipFile(path) as z:
            for info in sorted(z.infolist(),key=lambda x:x.filename):
                name=info.filename.replace('\\','/')
                p=PurePosixPath(name)
                if p.is_absolute() or '..' in p.parts or ':' in name: raise ValueError('Unsafe ZIP member')
                if name.lower().endswith('.csv'): yield name,z.read(info)
    elif path.is_dir():
        for p in sorted(path.rglob('*.csv')): yield str(p.relative_to(path)),p.read_bytes()
    else: yield path.name,path.read_bytes()

def run(path,project,commit=False):
    statepath=project/'data/ingest_state.json'
    state=json.loads(statepath.read_text(encoding='utf-8')) if statepath.exists() else {'version':1,'chats':{}}
    manifestpath=project/'data/story_manifest.json'
    manifest=json.loads(manifestpath.read_text(encoding='utf-8')) if manifestpath.exists() else {'stories':[]}
    generated={s['chat_id'] for s in manifest['stories']}
    report=[]
    for source,raw in sources(path):
        c=parse_csv(raw,source); exact=None; matches=[]
        keyset=set(c['message_keys']); anch=set(c['anchors'])
        for cid,old in state['chats'].items():
            if c['snapshot_sha256'] in old.get('snapshots',[]): exact=cid; break
            shared=keyset.intersection(old['message_keys'])
            overlap=anch.intersection(old.get('anchors',[]))
            if len(shared)>=3 and overlap: matches.append((len(shared),cid))
        if exact:
            cid=exact; old=state['chats'][cid]
            status='exact_duplicate' if cid in generated or old.get('reviewed') else 'pending_review'
        elif matches:
            matches.sort(reverse=True)
            if len(matches)>1 and matches[0][0]==matches[1][0]:
                cid='chat-'+c['snapshot_sha256'][:16]; status='identity_review'
            else: cid=matches[0][1];status='updated'
        else:
            same_name=any(set(c['names']).intersection(v.get('names',[])) for v in state['chats'].values())
            cid='chat-'+c['snapshot_sha256'][:16];status='identity_review' if same_name else 'new'
        old=state['chats'].get(cid,{})
        newkeys=keyset-set(old.get('message_keys',[]))
        report.append({'source':source,'chat_id':cid,'status':status,'new_message_count':len(newkeys),'snapshot_sha256':c['snapshot_sha256'],'file_sha256':c['file_sha256'],'names':c['names'],'new_message_keys':sorted(newkeys)})
        state['chats'][cid]={'names':sorted(set(c['names']+old.get('names',[]))), 'message_keys':sorted(keyset|set(old.get('message_keys',[]))), 'anchors':sorted(anch|set(old.get('anchors',[]))), 'snapshots':sorted(set(old.get('snapshots',[])+[c['snapshot_sha256']])), 'sources':sorted(set(old.get('sources',[])+[source])), 'reviewed':old.get('reviewed',False) if not newkeys else False}
    if commit:
        statepath.parent.mkdir(parents=True,exist_ok=True)
        temp=statepath.with_suffix('.tmp');temp.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8');temp.replace(statepath)
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('--project',type=Path,required=True);p.add_argument('--commit',action='store_true');p.add_argument('--report',type=Path)
    a=p.parse_args(); report=run(a.input,a.project,a.commit)
    if a.report:
        a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    counts={s:sum(r['status']==s for r in report) for s in sorted({r['status'] for r in report})}
    print(json.dumps({'csv_count':len(report),'statuses':counts},ensure_ascii=False))
