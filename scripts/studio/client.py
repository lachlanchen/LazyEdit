#!/usr/bin/env python
"""Private Studio client: resume uploads and request editing without global settings changes."""
import argparse,hashlib,json,os,pathlib,requests
os.umask(0o077)
p=argparse.ArgumentParser();p.add_argument('--server',default='https://edit.lazying.art');p.add_argument('--state',type=pathlib.Path,default=pathlib.Path.home()/'.config/lazyedit-studio/client-session.json')
sub=p.add_subparsers(dest='command',required=True)
a=sub.add_parser('login');a.add_argument('--account-file',type=pathlib.Path,required=True)
sub.add_parser('account');sub.add_parser('unlink');a=sub.add_parser('upload');a.add_argument('video',type=pathlib.Path)
for op in ['status','artifact','process','publish']:
 a=sub.add_parser(op);a.add_argument('video_id',type=int)
 if op=='process':a.add_argument('--request',type=pathlib.Path,required=True)
 if op=='publish':a.add_argument('--review',type=pathlib.Path,required=True)
 if op in ['process','publish']:a.add_argument('--idempotency-key',required=True)
a=p.parse_args();base=a.server.rstrip('/');session=requests.Session()
def call(method,path,**kw):
 r=session.request(method,base+path,timeout=900,**kw)
 # A large upload may outlive the 15-minute access token. Authentication fails
 # before dispatch, so retry only this explicit 401 after one serialized refresh.
 if r.status_code==401 and path not in ['/auth/login','/auth/token']:
  refresh();r=session.request(method,base+path,timeout=900,**kw)
 try:d=r.json()
 except ValueError:raise RuntimeError(f'Studio HTTP {r.status_code}')
 if not r.ok:raise RuntimeError(f'Studio HTTP {r.status_code}: {d.get("error","Request failed")}')
 return d
def save(d):
 a.state.parent.mkdir(parents=True,exist_ok=True);tmp=a.state.with_suffix('.tmp');tmp.write_text(json.dumps(d,indent=2));tmp.chmod(0o600);tmp.replace(a.state)
def refresh():
 global t
 stored=json.loads(a.state.read_text());t=call('POST','/auth/token',json={'grant_type':'refresh_token','refresh_token':stored['refresh_token']});save(t);session.headers['Authorization']='Bearer '+t['access_token']
if a.command=='login':
 c=json.loads(a.account_file.read_text());t=call('POST','/auth/login',json={'username':c['username'],'password':c['password'],'mode':'token','client_name':'Studio CLI'});save(t);print('Signed in. Credentials saved privately.');raise SystemExit
refresh()
if a.command=='account':result=call('GET','/v1/studio/account')
elif a.command=='unlink':result=call('POST','/auth/revoke',json={'grant_id':t['grant_id']});a.state.unlink()
elif a.command=='upload':
 video=a.video.resolve()
 with video.open('rb') as f:
  h=hashlib.sha256()
  for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
 sha=h.hexdigest();resume=a.state.with_name('upload-'+sha+'.json')
 if resume.exists():
  u=json.loads(resume.read_text());u=call('GET','/v1/studio/upload?uploadId='+u['uploadId'])
 else:
  u=call('POST','/v1/studio/uploads',json={'filename':video.name,'size':video.stat().st_size,'sha256':sha});resume.write_text(json.dumps(u))
 if u.get('receipt'):result=u['receipt']
 else:
  with video.open('rb') as f:
   offset=u['offset'];f.seek(offset)
   while chunk:=f.read(8*1024*1024):
    part=call('PUT','/v1/studio/upload-part?uploadId='+u['uploadId'],data=chunk,headers={'Upload-Offset':str(offset)});offset=part['offset'];print(f'{offset}/{video.stat().st_size}',flush=True)
  result=call('POST','/v1/studio/upload-complete',json={'uploadId':u['uploadId']})
 resume.unlink(missing_ok=True)
elif a.command=='status':result=call('GET',f'/api/videos/{a.video_id}/process-status')
elif a.command=='artifact':result=call('GET',f'/v1/studio/artifact?videoId={a.video_id}')
elif a.command=='process':result=call('POST',f'/api/videos/{a.video_id}/process',json=json.loads(a.request.read_text()),headers={'Idempotency-Key':a.idempotency_key})
elif a.command=='publish':result=call('POST',f'/api/videos/{a.video_id}/publish',json=json.loads(a.review.read_text()),headers={'Idempotency-Key':a.idempotency_key})
print(json.dumps(result,ensure_ascii=False,indent=2))
