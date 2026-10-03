"""One owner's runtime. Terminate together if any essential service fails."""
import os
from pathlib import Path
import signal
import subprocess
import time
from urllib.parse import quote

os.umask(0o077)
for part in ('home', 'data', 'studio', 'cache', 'temp', 'translation_logs',
             'publisher', 'publisher/logs', 'publisher/temp', 'publisher/temp_screenshot'):
    Path('/state', part).mkdir(parents=True, exist_ok=True)

# Never source shell code or print secrets. Each workspace has its own provider file.
provider = Path('/bootstrap/providers.env')
if provider.exists():
    allowed = {'OPENAI_API_KEY', 'DEEPSEEK_API_KEY', 'DEEPSEEK_MODEL',
               'LAZYEDIT_TRANSLATION_PROVIDER', 'LAZYEDIT_TRANSLATION_MODEL',
               'FROM_EMAIL', 'TO_EMAIL', 'APP_PASSWORD', 'APIKEY_2CAPTCHA'}
    for line in provider.read_text().splitlines():
        key, sep, value = line.partition('=')
        if sep and key.strip() in allowed:
            os.environ[key.strip()] = value.strip().strip('"\'')

password = Path('/run/secrets/db_password').read_text().strip()
os.environ['LAZYEDIT_DATABASE_URL'] = f'postgresql://lazyedit:{quote(password, safe="")}@database/lazyedit'
os.environ.setdefault('LAZYEDIT_CAPTION_PRIMARY_SCRIPT', '/opt/lazyedit/vit-gpt2-image-captioning/vit_captioner_video.py')
os.environ.setdefault('LAZYEDIT_CAPTION_PRIMARY_ROOT', '/opt/lazyedit/vit-gpt2-image-captioning')
if Path('/samples/vancouver.mp4').is_file():
    subprocess.run(['python', '-m', 'hosted.seed_sample'], cwd='/opt/lazyedit', check=True, timeout=60)
processes = []


def stop(*_):
    for p in reversed(processes):
        if p.poll() is None:
            p.terminate()
    end = time.monotonic() + 20
    for p in processes:
        try:
            p.wait(timeout=max(0.1, end-time.monotonic()))
        except subprocess.TimeoutExpired:
            p.kill()


signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
signal.signal(signal.SIGINT, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
try:
    processes.append(subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1440x1000x24', '-nolisten', 'tcp', '-ac', '-noreset']))
    for _ in range(50):
        if Path('/tmp/.X11-unix/X99').exists():
            break
        time.sleep(0.1)
    for command, cwd in [
        (['openbox', '--sm-disable', '--config-file', '/opt/lazyedit/hosted/openbox-rc.xml'], '/state'),
        (['x11vnc', '-display', ':99', '-localhost', '-nopw', '-forever', '-shared', '-rfbport', '5900', '-quiet'], '/state'),
        (['websockify', '--web=/usr/share/novnc', '127.0.0.1:6080', '127.0.0.1:5900'], '/state'),
        (['python', 'app.py'], '/opt/lazyedit'),
        (['python', 'container_runtime.py'], '/opt/lazyedit/AutoPublish'),
        (['node', 'hosted/cell.mjs'], '/opt/lazyedit'),
    ]:
        processes.append(subprocess.Popen(command, cwd=cwd))
    while all(p.poll() is None for p in processes):
        time.sleep(1)
    raise RuntimeError('An essential workspace service stopped; restarting the workspace')
except KeyboardInterrupt:
    pass
finally:
    stop()
