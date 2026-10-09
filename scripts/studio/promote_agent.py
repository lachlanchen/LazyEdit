#!/usr/bin/env python
"""Stage/activate the owner Studio chat adapter without restarting editing or Pi.

Private hosted workers are deliberately separate. Their acceptance locks and
normal image promotion procedure still apply.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--webdist', type=Path, required=True)
    parser.add_argument('--activate', action='store_true')
    args = parser.parse_args()
    os.umask(0o077)
    root = Path(__file__).resolve().parents[2]
    private = Path.home() / '.config/lazyedit-studio'
    config_file = private / 'worker.json'
    config = json.loads(config_file.read_text())
    old = Path(config['webRoot']).parent.parent
    unit = Path.home() / '.config/systemd/user/lazyedit-studio-worker.service'
    if not config.get('hostedAdminUsername') or str(old / 'hosted/ingress.mjs') not in unit.read_text():
        raise SystemExit('Expected the isolated original-owner ingress; no changes made')
    html = (args.webdist / 'index.html').read_text()
    if '/studio-context.js' not in html:
        html = html.replace('<head>', '<head><script src="/studio-context.js"></script>')
    if '/studio-session.js' not in html:
        html = html.replace('</head>', '<link rel="manifest" href="/manifest.webmanifest"><link rel="apple-touch-icon" href="/studio-icon.png"><script src="/studio-session.js" defer></script></head>')
    if 'id="studio-loading"' not in html:
        html = html.replace('</body>', (root/'studio/web/loading.html').read_text()+'</body>')
    sources = [*sorted((root/'studio').glob('*.mjs')), *sorted((root/'studio').glob('*.py'))]
    digest = hashlib.sha256(html.encode())
    for file in [*sources, *sorted((root/'studio/locales').glob('*.json'))]:
        digest.update(file.name.encode()); digest.update(file.read_bytes())
    revision = digest.hexdigest()[:12]
    release = old.parent / ('agent-' + revision)
    if release.exists():
        raise SystemExit('Release exists; inspect the existing private receipt before activating again')
    with tempfile.TemporaryDirectory(dir=old.parent, prefix='agent-stage-') as tmp:
        stage = Path(tmp) / 'release'
        shutil.copytree(old, stage)
        for file in sources:
            shutil.copy2(file, stage/'studio'/file.name)
        for directory in ['web', 'locales']:
            shutil.copytree(root/'studio'/directory, stage/'studio'/directory, dirs_exist_ok=True)
        shutil.rmtree(stage/'webdist')
        shutil.copytree(args.webdist, stage/'webdist')
        (stage/'webdist/index.html').write_text(html)
        subprocess.run(['node','--check',str(stage/'studio/server.mjs')],check=True)
        subprocess.run(['node','--check',str(stage/'studio/agent.mjs')],check=True)
        stage.rename(release)
    receipt = {'release': str(release), 'previous': str(old), 'activated': False,
               'preserved': ['Python editing backend', 'AutoPublish Pi', 'hosted workers', 'hosted gateway', 'LazyEdge tunnel']}
    if args.activate:
        queue = json.load(urllib.request.urlopen(f"http://127.0.0.1:{config['backendPort']}/api/autopublish/queue", timeout=20))
        if not isinstance(queue.get('jobs'), list) or any(j.get('status') in ['running','queued','processing','publishing','submitted'] for j in queue['jobs']):
            raise SystemExit('Owner queue is active or unavailable; release staged, service unchanged')
        db = sqlite3.connect(Path(config['database']).resolve().as_uri()+'?mode=ro',uri=True)
        pending = db.execute("SELECT count(*) FROM intents WHERE state='submitting' AND created>?", (int(time.time()*1000)-120000,)).fetchone()[0]
        db.close()
        if pending:
            raise SystemExit('A recent submission is unresolved; release staged, service unchanged')
        backup = private/'rollbacks'/('agent-'+revision)
        backup.mkdir(parents=True)
        shutil.copy2(config_file,backup/'worker.json');shutil.copy2(unit,backup/unit.name)
        config.update(webRoot=str(release/'studio/web'),staticRoot=str(release/'webdist'),python=sys.executable,sourceRoot=str(root))
        config_file.write_text(json.dumps(config,indent=2)+'\n')
        unit.write_text(unit.read_text().replace(str(old),str(release)))
        subprocess.run(['systemctl','--user','daemon-reload'],check=True)
        try:
            subprocess.run(['systemctl','--user','restart','lazyedit-studio-worker'],check=True)
            for attempt in range(15):
                try:
                    with urllib.request.urlopen(f"http://127.0.0.1:{config['port']}/healthz",timeout=2) as r:
                        assert json.load(r)['status']=='ok'
                    break
                except Exception:
                    if attempt==14: raise
                    time.sleep(1)
        except Exception:
            shutil.copy2(backup/'worker.json',config_file);shutil.copy2(backup/unit.name,unit)
            subprocess.run(['systemctl','--user','daemon-reload'],check=True)
            subprocess.run(['systemctl','--user','restart','lazyedit-studio-worker'],check=True)
            raise
        receipt.update(activated=True,rollback=str(backup))
    (private/'agent-release.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__ == '__main__':
    main()
