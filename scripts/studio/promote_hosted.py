#!/usr/bin/env python
"""Stage the same-domain hosted ingress without restarting the owner backend."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

os.umask(0o077)
p = argparse.ArgumentParser()
p.add_argument('--state', required=True)
a = p.parse_args()
root = Path(__file__).resolve().parents[2]
private = Path.home() / '.config/lazyedit-studio'
config_path = private / 'worker.json'
config = json.loads(config_path.read_text())
old_release = Path(config['webRoot']).parent.parent
state = Path(a.state).resolve()
if not (state / 'registry/ingress.secret').is_file():
    raise SystemExit('Initialize the private same-host registry first')
digest = hashlib.sha256()
for directory in ('studio', 'hosted'):
    for source in sorted((root / directory).glob('*.mjs')):
        digest.update(source.relative_to(root).as_posix().encode())
        digest.update(source.read_bytes())
revision = digest.hexdigest()[:12]
release = old_release.parent / ('hosted-' + revision)
if release.exists():
    raise SystemExit('Release already staged; inspect its receipt before retrying')
with tempfile.TemporaryDirectory(dir=old_release.parent, prefix='hosted-stage-') as tmp:
    staged = Path(tmp) / 'release'
    shutil.copytree(old_release, staged)
    shutil.copytree(root / 'hosted', staged / 'hosted', dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns('*.test.mjs', 'test.mjs'))
    for source in (root / 'studio').glob('*.mjs'):
        shutil.copy2(source, staged / 'studio' / source.name)
    staged.rename(release)
backup = private / 'rollbacks' / ('hosted-' + revision)
backup.mkdir(parents=True)
units = Path.home() / '.config/systemd/user'
for name in ('lazyedit-studio-worker.service', 'lazyedit-studio-guard.service'):
    shutil.copy2(units / name, backup / name)
shutil.copy2(config_path, backup / 'worker.json')
config.update(hostedIngressSecretFile=str(state / 'registry/ingress.secret'),
              python=sys.executable, sourceRoot=str(root),
              webRoot=str(release / 'studio/web'), staticRoot=str(release / 'webdist'))
config_path.write_text(json.dumps(config, indent=2))
worker = units / 'lazyedit-studio-worker.service'
text = worker.read_text()
line = next(line for line in text.splitlines() if line.startswith('ExecStart='))
worker.write_text(text.replace(line, 'ExecStart=' + str(Path.home() / '.nvm/versions/node/v22.21.0/bin/node') +
    ' ' + str(release / 'hosted/ingress.mjs') + ' ' + str(config_path)))
guard = units / 'lazyedit-studio-guard.service'
text = guard.read_text()
line = next(line for line in text.splitlines() if line.startswith('ExecStart='))
package = old_release.parent / 'lazyedge-0.4.0-a58ea8b9ec72/package'
guard.write_text(text.replace(line, 'ExecStart=' + str(Path.home() / '.nvm/versions/node/v22.21.0/bin/node') +
    ' ' + str(release / 'hosted/lazyedge-runtime.mjs') + ' worker ' + str(package) +
    ' ' + str(private / 'lazyedge.yaml') + ' ' + str(private / 'bindings.worker.json')))
receipt = {'revision': revision, 'release': str(release), 'previous': str(old_release),
           'rollback': str(backup), 'hostedState': str(state)}
(private / 'hosted-release.json').write_text(json.dumps(receipt, indent=2))
print(json.dumps(receipt, indent=2))
print('Staged only; daemon-reload and restart the two Studio units after edge staging.')
