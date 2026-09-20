#!/usr/bin/env python
"""Create an immutable Studio build and local service units; no backend restart."""
import hashlib,json,os,pathlib,shutil,subprocess,tarfile
os.umask(0o077)
r=pathlib.Path(__file__).resolve().parents[2]; p=pathlib.Path.home()/'.config/lazyedit-studio';node=pathlib.Path.home()/'.nvm/versions/node/v22.21.0/bin/node'
dist=r/'temp/studio-deploy/webdist';index=dist/'index.html';s=index.read_text()
if '/studio-session.js' not in s:s=s.replace('</head>','<link rel="manifest" href="/manifest.webmanifest"><link rel="apple-touch-icon" href="/studio-icon.png"><script src="/studio-session.js"></script></head>');index.write_text(s)
archive=r/'temp/studio-deploy/studio-release.tar.gz'
with tarfile.open(archive,'w:gz') as tar:
 for f in sorted((r/'studio').rglob('*')):
  if f.is_file():tar.add(f,arcname=str(f.relative_to(r)))
 tar.add(dist,arcname='webdist')
sha=hashlib.sha256(archive.read_bytes()).hexdigest();release=pathlib.Path.home()/'.local/share/lazyedit-studio/releases'/('studio-'+sha[:12]);release.mkdir(parents=True,exist_ok=True)
with tarfile.open(archive) as tar:tar.extractall(release,filter='data')
c=json.loads((p/'worker.json').read_text());c.update(webRoot=str(release/'studio/web'),staticRoot=str(release/'webdist'));(p/'worker.json').write_text(json.dumps(c,indent=2))
# Account bootstrap reads the protected file; no values are written to output.
js=f"import {{AuthStore}} from {json.dumps(str(release/'studio/auth.mjs'))};import{{readFileSync}}from'node:fs';const c=JSON.parse(readFileSync(process.argv[1]));new AuthStore(process.argv[2]).addOwner(c.username,c.password);"
subprocess.run([str(node),'--input-type=module','-e',js,'/home/lachlan/Nutstore Files/Share/LazyEdit/studio-account.json',str(p/'accounts.sqlite')],check=True)
edge=json.loads((p/'release.json').read_text());cli=edge['lazyedgeCLI']
units=pathlib.Path.home()/'.config/systemd/user';units.mkdir(parents=True,exist_ok=True)
commands={
'lazyedit-studio-worker':f'{node} {release}/studio/server.mjs {p}/worker.json',
'lazyedit-studio-guard':f'{node} {cli} serve worker --config {p}/lazyedge.yaml --bindings {p}/bindings.worker.json',
'lazyedit-studio-tunnel':f'/usr/bin/ssh -F {p}/ssh.conf -N lazyedge-edge'}
for name,cmd in commands.items():
 (units/(name+'.service')).write_text(f'''[Unit]
Description={name} isolated Studio service
After=network-online.target
[Service]
Type=simple
ExecStart={cmd}
Restart=always
RestartSec=5
TimeoutStopSec=15
UMask=0077
Environment=PATH={node.parent}:/usr/bin:/bin
[Install]
WantedBy=default.target
''')
edge.update(studioSha256=sha,studioRelease=str(release));(p/'release.json').write_text(json.dumps(edge,indent=2))
print('Studio archive SHA256:',sha)
