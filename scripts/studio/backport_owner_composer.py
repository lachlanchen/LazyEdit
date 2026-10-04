#!/usr/bin/env python
"""Stage a narrow compatibility patch to a pinned original-owner adapter.

Private Docker workers, hosted ingress routing, web assets and credentials are
copied unchanged. Activation is deliberately separate, at a safe queue boundary.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


def patch_owner_server(source):
    if 'function ownerOnly(p)' not in source or 'config.ownerUsername' not in source:
        raise ValueError('Expected the original owner-only adapter')
    patches = {
        "scopes:p.scopes,issuer:origin": "scopes:p.scopes,capabilities:{editing:p.scopes.includes('publication.prepare'),publishing:p.scopes.includes('publication.publish')},issuer:origin",
        "{defaults:composerDefaults(settings),sessions:": "{capabilities:{editing:p.scopes.includes('publication.prepare'),publishing:p.scopes.includes('publication.publish')},defaults:composerDefaults(settings),sessions:",
    }
    for old, new in patches.items():
        if source.count(new) == 1 and old not in source:
            continue
        if source.count(old) != 1:
            raise ValueError('Adapter differs from the qualified baseline; do not overwrite it')
        source = source.replace(old, new)
    return source


def main():
    os.umask(0o077)
    root = Path(__file__).resolve().parents[2]
    private = Path.home() / '.config/lazyedit-studio'
    config_path = private / 'worker.json'
    config = json.loads(config_path.read_text())
    if not config.get('hostedIngressSecretFile') or not config.get('hostedAdminUsername'):
        raise SystemExit('Expected the existing isolated owner ingress')
    unit = Path.home() / '.config/systemd/user/lazyedit-studio-worker.service'
    old = Path(config['webRoot']).parent.parent
    if str(old / 'hosted/ingress.mjs') not in unit.read_text():
        raise SystemExit('Configuration and active unit disagree')
    source = patch_owner_server((old / 'studio/server.mjs').read_text())
    composer = (root / 'studio/composer.mjs').read_text()
    revision = hashlib.sha256((str(old) + source + composer).encode()).hexdigest()[:12]
    release = old.parent / ('owner-composer-' + revision)
    if release.exists():
        raise SystemExit('Patch already staged; inspect its receipt')
    with tempfile.TemporaryDirectory(dir=old.parent, prefix='owner-composer-stage-') as tmp:
        staged = Path(tmp) / 'release'
        shutil.copytree(old, staged)
        (staged / 'studio/server.mjs').write_text(source)
        (staged / 'studio/composer.mjs').write_text(composer)
        node = Path.home() / '.nvm/versions/node/v22.21.0/bin/node'
        subprocess.run([str(node), '--check', str(staged / 'studio/server.mjs')], check=True)
        subprocess.run([str(node), '--check', str(staged / 'studio/composer.mjs')], check=True)
        staged.rename(release)
    backup = private / 'rollbacks' / ('owner-composer-' + revision)
    backup.mkdir(parents=True)
    shutil.copy2(config_path, backup / 'worker.json')
    shutil.copy2(unit, backup / unit.name)
    config.update(webRoot=str(release / 'studio/web'), staticRoot=str(release / 'webdist'))
    config_path.write_text(json.dumps(config, indent=2))
    unit.write_text(unit.read_text().replace(str(old), str(release)))
    receipt = {'release': str(release), 'previous': str(old), 'rollback': str(backup),
               'changedFiles': ['studio/server.mjs', 'studio/composer.mjs'], 'activated': False}
    (private / 'owner-composer-release.json').write_text(json.dumps(receipt, indent=2))
    print(json.dumps(receipt, indent=2))
    print('Staged only; restart only lazyedit-studio-worker.service at an idle boundary.')


if __name__ == '__main__':
    main()
