#!/usr/bin/env python
"""Stage tested adapter modules, preserving web assets and every other service."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tarfile
import tempfile

os.umask(0o077)
root = Path(__file__).resolve().parents[2]
private = Path.home() / '.config/lazyedit-studio'
config_path = private / 'worker.json'
config = json.loads(config_path.read_text())
old_release = Path(config['webRoot']).parent.parent
release_root = old_release.parent
unit = Path.home() / '.config/systemd/user/lazyedit-studio-worker.service'
with tempfile.TemporaryDirectory(dir=release_root, prefix='worker-stage-') as tmp:
    staged = Path(tmp) / 'release'
    shutil.copytree(old_release, staged)
    for source in (root / 'studio').glob('*.mjs'):
        shutil.copy2(source, staged / 'studio' / source.name)
    shutil.copy2(root / 'studio/layout_preview.py', staged / 'studio/layout_preview.py')
    archive = Path(tmp) / 'worker.tar.gz'
    with tarfile.open(archive, 'w:gz') as tar:
        tar.add(staged, arcname='.')
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    release = release_root / ('studio-' + digest[:12])
    staged.rename(release)
    backup = private / 'rollbacks' / digest[:12]
    backup.mkdir(parents=True, exist_ok=True)
    shutil.copy2(config_path, backup / 'worker.json')
    shutil.copy2(unit, backup / unit.name)
    config.update(webRoot=str(release / 'studio/web'), staticRoot=str(release / 'webdist'),
                  python=sys.executable, sourceRoot=str(root))
    config_path.write_text(json.dumps(config, indent=2))
    unit.write_text(unit.read_text().replace(str(old_release), str(release)))
    receipt = {'sha256': digest, 'release': str(release), 'previous': str(old_release), 'rollback': str(backup)}
    (private / 'worker-release.json').write_text(json.dumps(receipt, indent=2))
    print(json.dumps(receipt, indent=2))
print('Staged only. Run daemon-reload and restart lazyedit-studio-worker to activate.')
