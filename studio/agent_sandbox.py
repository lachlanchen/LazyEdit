"""Private, bounded AgInTi/Codex planner service; never a publication worker."""
import hmac
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from agent_plan import SYSTEM

MAX_BYTES = 100000
FIELDS = set('burnSubtitles languages lift rows fontScale fontBold outlineBold background bottomSpace logo logoPosition category platforms context metadataDirection correct contextForMetadata mode sessionID'.split())


class Unavailable(Exception):
    pass


def decision(text):
    value = json.loads(text)
    if not isinstance(value, dict) or set(value) != {'decision', 'message', 'changes'}:
        raise ValueError('Invalid plan')
    if value['decision'] not in ('run', 'reply') or not isinstance(value['message'], str) or not 0 < len(value['message'].strip()) <= 2000:
        raise ValueError('Invalid plan')
    if not isinstance(value['changes'], dict) or set(value['changes']) - FIELDS:
        raise ValueError('Invalid plan')
    # Full form/type/capability validation remains in Studio before dispatch.
    return value


def secret(name):
    path = os.environ.get(name + '_FILE')
    return Path(path).read_text().strip() if path else ''


def run_bounded(argv, prompt, env, cwd, seconds):
    """Bound memory, time and process tree; discard diagnostics and private prompts."""
    with subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                          stderr=subprocess.DEVNULL, cwd=cwd, env=env,
                          start_new_session=True) as process:
        try:
            # Prompt is bounded; writer avoids a blocked stdin defeating deadline.
            def feed():
                try:
                    process.stdin.write(prompt.encode()); process.stdin.close()
                except (BrokenPipeError, OSError):
                    pass
            writer = threading.Thread(target=feed, daemon=True); writer.start()
            deadline = time.monotonic() + seconds
            output = bytearray()
            with selectors.DefaultSelector() as poll:
                poll.register(process.stdout, selectors.EVENT_READ)
                while poll.get_map():
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise Unavailable()
                    for key, _ in poll.select(min(remaining, .2)):
                        chunk = os.read(key.fileobj.fileno(), 8192)
                        if not chunk:
                            poll.unregister(key.fileobj)
                        else:
                            output.extend(chunk)
                            if len(output) > MAX_BYTES:
                                raise ValueError('Oversized output')
                process.wait(timeout=max(.01, deadline - time.monotonic()))
            if process.returncode:
                raise Unavailable()
            return output.decode()
        finally:
            # Kill descendants even if the CLI parent already exited.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()


def invoke(engine, prompt, root, runner=run_bounded):
    home = root / engine; home.mkdir(mode=0o700)
    env = {'PATH': '/usr/local/bin:/usr/bin:/bin', 'HOME': str(home),
           'TMPDIR': str(home), 'CI': '1', 'NO_COLOR': '1'}
    if engine == 'aginti':
        key = secret('DEEPSEEK_API_KEY')
        if not key:
            raise Unavailable()
        env['DEEPSEEK_API_KEY'] = key
        env['ALLOW_WRAPPER_TOOLS'] = 'false'
        argv = ['aginti', 'run', '--stdin', '--json', '--no-auto-update',
                '--task-profile', 'chatops', '--no-scs', '-s', 'safe',
                '--sandbox-mode', 'host', '--no-shell', '--no-file-tools',
                '--no-web-search', '--no-mcp', '--no-parallel-scouts',
                '--no-auxiliary-tools', '--max-steps', '2',
                '--dynamic-steps', 'off', '--routing', 'manual', '--provider', 'deepseek',
                '--model', os.environ.get('AGINTI_MODEL', 'deepseek-v4-flash')]
        raw = json.loads(runner(argv, prompt, env, home, 40))
        if raw.get('ok') is not True or raw.get('failed') or raw.get('stopped'):
            raise Unavailable()
        return decision(raw['result'])
    key = secret('CODEX_API_KEY')
    if not key:
        raise Unavailable()
    env.update(CODEX_API_KEY=key, CODEX_HOME=str(home / '.codex'))
    argv = ['codex', 'exec', '--ephemeral', '--skip-git-repo-check',
            '--sandbox', 'read-only', '-c', 'features.shell_tool=false',
            '-c', 'web_search="disabled"', '-c', 'model_reasoning_effort="low"',
            '-m', os.environ.get('CODEX_MODEL', 'gpt-5.4-mini'), '-']
    return decision(runner(argv, prompt, env, home, 30))


def plan(payload, invoke_fn=invoke):
    if not isinstance(payload, dict):
        raise ValueError('Invalid request')
    # Caller settings cannot change executables, providers, credentials or sandbox.
    payload = {k: v for k, v in payload.items() if k != 'modelSettings'}
    prompt = SYSTEM + '\nReturn only the JSON object, no markdown.\nInput data:\n' + json.dumps(payload, ensure_ascii=False)
    with tempfile.TemporaryDirectory(prefix='studio-agent-') as directory:
        root = Path(directory)
        try:
            return invoke_fn('aginti', prompt, root)
        except (Unavailable, subprocess.TimeoutExpired):
            # No fallback for invalid/unsafe model output; it must fail closed.
            if os.environ.get('CODEX_FALLBACK', '0') != '1':
                raise
            return invoke_fn('codex', prompt, root)


class Server(ThreadingHTTPServer):
    daemon_threads = True
    request_queue_size = 4
    connections = threading.BoundedSemaphore(8)

    def process_request(self, request, address):
        if not self.connections.acquire(blocking=False):
            self.shutdown_request(request)
            return
        try:
            super().process_request(request, address)
        except Exception:
            self.connections.release()
            raise

    def process_request_thread(self, request, address):
        try:
            super().process_request_thread(request, address)
        finally:
            self.connections.release()


class Handler(BaseHTTPRequestHandler):
    gate = threading.BoundedSemaphore(1)
    token = ''

    def log_message(self, *_):
        pass

    def setup(self):
        super().setup(); self.connection.settimeout(5)

    def send_json(self, status, value):
        body = json.dumps(value).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers(); self.wfile.write(body)

    def authorized(self):
        return hmac.compare_digest(self.headers.get('Authorization', ''), 'Bearer ' + self.token)

    def do_GET(self):
        self.send_json(200 if self.authorized() and self.path == '/health' else 404,
                       {'ok': self.authorized() and self.path == '/health'})

    def do_POST(self):
        if not self.authorized():
            return self.send_json(401, {'error': 'unauthorized'})
        if self.path != '/v1/plan':
            return self.send_json(404, {'error': 'not_found'})
        if not self.gate.acquire(blocking=False):
            return self.send_json(429, {'error': 'busy'})
        try:
            if self.headers.get('Transfer-Encoding'):
                raise ValueError()
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= MAX_BYTES:
                raise ValueError()
            payload = json.loads(self.rfile.read(size))
            result = plan(payload)
            self.send_json(200, result)
        except (ValueError, KeyError, TypeError):
            self.send_json(422, {'error': 'invalid_plan_or_request'})
        except Exception:
            self.send_json(503, {'error': 'planner_unavailable'})
        finally:
            self.gate.release()


if __name__ == '__main__':
    Handler.token = secret('STUDIO_AGENT_TOKEN')
    if len(Handler.token) < 32:
        raise SystemExit('A dedicated service token is required')
    Server(('0.0.0.0', 8092), Handler).serve_forever()
