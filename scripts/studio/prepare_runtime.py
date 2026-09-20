#!/usr/bin/env python
"""Prepare owner-private Studio state and isolated immutable LazyEdge runtime."""
import hashlib,json,os,pathlib,secrets,shutil,subprocess,tarfile
os.umask(0o077)
# Initial provisioning only; promotion is a separate command.
if (pathlib.Path.home()/'.config/lazyedit-studio/release.json').exists():
 raise SystemExit('Already provisioned. Use promote_local.py; do not reset live bindings.')
repo=pathlib.Path(__file__).resolve().parents[2]
private=pathlib.Path.home()/'.config/lazyedit-studio'; private.mkdir(parents=True,exist_ok=True)
share=pathlib.Path('/home/lachlan/Nutstore Files/Share/LazyEdit');share.mkdir(parents=True,exist_ok=True)
credentials=share/'studio-account.json'
if not credentials.exists():
 credentials.write_text(json.dumps({'url':'https://edit.lazying.art','username':'lachlanchen','password':secrets.token_urlsafe(24)},indent=2)+'\n');credentials.chmod(0o600)
for name in ['relay','upstream']:
 p=private/name
 if not p.exists():p.write_text(secrets.token_urlsafe(48)+'\n')
key=private/'tunnel_ed25519'
if not key.exists():subprocess.run(['ssh-keygen','-t','ed25519','-N','','-C','lazyedit-studio-only','-f',str(key)],check=True,stdout=subprocess.DEVNULL)
shutil.copyfile(pathlib.Path.home()/'.config/lazytunnel/edge_known_hosts',private/'known_hosts')
manifest=repo/'deploy/studio/lazyedge.yaml';shutil.copyfile(manifest,private/'lazyedge.yaml')
pkg=repo/'temp/studio-deploy/lazyingart-lazyedge-0.4.0.tgz';sha=hashlib.sha256(pkg.read_bytes()).hexdigest()
release=pathlib.Path.home()/'.local/share/lazyedit-studio/releases'/('lazyedge-0.4.0-'+sha[:12]);release.mkdir(parents=True,exist_ok=True)
if not (release/'package').exists():
 with tarfile.open(pkg) as tar:tar.extractall(release,filter='data')
 shutil.copytree('/home/lachlan/ProjectsLFS/LazyEdge/node_modules/yaml',release/'package/node_modules/yaml')
node=pathlib.Path.home()/'.nvm/versions/node/v22.21.0/bin/node';cli=release/'package/bin/lazyedge.mjs'
edge=repo/'temp/studio-deploy/edge-private';edge.mkdir(parents=True,exist_ok=True)
for name in ['relay','lazyedge.yaml']:shutil.copyfile(private/name,edge/name)
if not (edge/'client-token').exists():subprocess.run([str(node),str(cli),'token','issue','--store',str(edge/'tokens.json'),'--set','studio-facade','--out',str(edge/'client-token'),'--service','studio','--days','365','--hosts','edit.lazying.art','--paths','/studio/bridge'],check=True,stdout=subprocess.DEVNULL)
(private/'bindings.worker.json').write_text(json.dumps({'bindings':{'studio':{'relaySecretFile':str(private/'relay'),'upstreamAuthorizationFile':str(private/'upstream')}}},indent=2))
(edge/'bindings.edge.json').write_text(json.dumps({'bindings':{'studio':{'relaySecretFile':'/etc/lazystudio/relay','clientTokenStore':'/etc/lazystudio/tokens.json'}}},indent=2))
(edge/'facade.json').write_text(json.dumps({'role':'edge','host':'edit.lazying.art','port':18794,'gatewayPort':18795,'clientTokenFile':'/etc/lazystudio/client-token'},indent=2))
# The versioned release path is generated after the application bundle is tested.
(private/'worker.json').write_text(json.dumps({'role':'worker','host':'edit.lazying.art','port':18798,'backendPort':18787,'upstreamSecretFile':str(private/'upstream'),'database':str(private/'accounts.sqlite'),'dataRoot':str(repo/'DATA'),'webRoot':str(repo/'studio/web'),'staticRoot':str(repo/'temp/studio-deploy/webdist')},indent=2))
subprocess.run([str(node),str(cli),'render','openssh','--config',str(manifest),'--identity-file',str(key),'--known-hosts-file',str(private/'known_hosts')],stdout=(private/'ssh.conf').open('w'),check=True)
subprocess.run([str(node),str(cli),'render','accounts','--config',str(manifest),'--public-key-file',str(key)+'.pub'],stdout=(repo/'temp/studio-deploy/accounts.sh').open('w'),check=True)
subprocess.run([str(node),str(cli),'render','redirect-helper','--config',str(manifest)],stdout=(edge/'redirect-helper').open('w'),check=True)
# Each project must own its own runtime directory.
p=edge/'redirect-helper';p.write_text(p.read_text().replace('runtime_directory=/run/lazyedge-port-redirect','runtime_directory=/run/lazystudio-ingress'))
(private/'release.json').write_text(json.dumps({'lazyedgePackageSha256':sha,'lazyedgeRelease':str(release),'lazyedgeCLI':str(cli)},indent=2))
print('Prepared private credentials, dedicated SSH identity and role-split bindings; no values printed.')
print('LazyEdge package SHA256:',sha)
