#!/usr/bin/env python
"""Roll private hosted images at an idle boundary, preserving every user volume.

Does not operate the owner backend, Pi, ingress or shared tunnel. Fixed Compose
templates come from the repository, never from a public user's request.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

os.umask(0o077)
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--state', type=Path, required=True)
parser.add_argument('--tag', required=True)
parser.add_argument('--sample', type=Path)
parser.add_argument('--sample-sha256')
args = parser.parse_args()
if not __import__('re').fullmatch(r'[a-zA-Z0-9_.-]{1,80}', args.tag):
    raise SystemExit('Invalid exact image tag')
root = args.state.resolve()
config_file = root / 'config.json'
config = json.loads(config_file.read_text())
control_file = root / 'compose.json'
control = json.loads(control_file.read_text())
cells = sorted((root / 'workspaces').glob('*/compose.json'))
images = {name: f'lazyedit-{name}:{args.tag}' for name in ('workspace', 'gateway', 'provisioner')}
for image in images.values():
    subprocess.run(['docker', 'image', 'inspect', image], check=True, stdout=subprocess.DEVNULL)
if args.sample:
    with args.sample.open('rb') as stream:
        if hashlib.file_digest(stream, 'sha256').hexdigest() != args.sample_sha256:
            raise SystemExit('Authorized sample hash mismatch')
    config.update(sampleFile=str(args.sample.resolve()), sampleSha256=args.sample_sha256)
probe = '''import json, urllib.request
for port,path in [(18787,"/api/autopublish/queue"),(8081,"/publish/queue")]:
 d=json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}{path}",timeout=10))
 jobs=d.get("jobs",[])
 if isinstance(jobs,dict): jobs=list(jobs.values())
 if d.get("is_publishing") or any(j.get("status") in ("queued","running","processing","pending","publishing") for j in jobs): raise SystemExit("Publication is active")
'''
for file in cells:
    compose = json.loads(file.read_text())
    subprocess.run(['docker', 'exec', compose['services']['worker']['container_name'], 'python', '-c', probe], check=True)
backup = root / 'rollbacks' / (args.tag + '-' + str(int(time.time())))
backup.mkdir(parents=True)
for file in [config_file, control_file, *cells]:
    relative = file.relative_to(root)
    destination = backup / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(file.read_bytes())
config['workerImage'] = images['workspace']
config_file.write_text(json.dumps(config, indent=2))
for name in ('gateway', 'provisioner'):
    control['services'][name]['image'] = images[name]
control_file.write_text(json.dumps(control, indent=2))
repository = Path(__file__).resolve().parents[2]
render = "import {workspaceCompose} from './hosted/compose.mjs'; console.log(JSON.stringify(workspaceCompose(JSON.parse(process.argv[1]),JSON.parse(process.argv[2]),process.argv[3]),null,2));"
for file in cells:
    seed = json.loads((file.parent / 'account.json').read_text())
    # Only non-secret workspace identity is passed to the renderer.
    result = subprocess.run(['node', '--input-type=module', '-e', render, json.dumps({'id': seed['id']}), json.dumps(config), str(file.parent)], cwd=repository, check=True, capture_output=True, text=True)
    file.write_text(result.stdout)
    subprocess.run(['docker', 'compose', '-f', str(file), 'up', '-d', '--no-deps', '--wait', '--wait-timeout', '180', 'worker'], check=True)
subprocess.run(['docker', 'compose', '-f', str(control_file), 'up', '-d', '--no-deps', 'gateway', 'provisioner'], check=True)
receipt = {'tag': args.tag, 'rollback': str(backup), 'workspaces': len(cells), 'volumesPreserved': True}
(root / 'last-promotion.json').write_text(json.dumps(receipt, indent=2))
print(json.dumps(receipt, indent=2))
