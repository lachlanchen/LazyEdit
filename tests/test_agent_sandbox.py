import importlib.util
import json
import os
from pathlib import Path
import sys
import time

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'studio'))
import agent_sandbox as agent
import agent_plan


def test_fail_closed_unknown_fields():
    with pytest.raises(ValueError):
        agent.decision(json.dumps({'decision':'run','message':'ok','changes':{'command':'rm -rf /'}}))


def test_fallback_only_runtime_failure(monkeypatch):
    monkeypatch.setenv('CODEX_FALLBACK','1')
    calls=[]; roots=[]
    def invoke(engine,prompt,root):
        calls.append(engine); roots.append(root)
        if engine=='aginti': raise agent.Unavailable()
        return {'decision':'reply','message':'ok','changes':{}}
    assert agent.plan({'message':'hello'},invoke)['decision']=='reply'
    assert calls==['aginti','codex']
    assert not roots[0].exists()
    calls.clear()
    def invalid(engine,*args):
        calls.append(engine); raise ValueError('unsafe output')
    with pytest.raises(ValueError): agent.plan({},invalid)
    assert calls==['aginti']


def test_model_settings_do_not_control_runtime():
    def invoke(engine,prompt,root):
        assert 'evil-model' not in prompt
        return {'decision':'reply','message':'ok','changes':{}}
    agent.plan({'modelSettings':{'model':'evil-model'}},invoke)


def test_deadline_and_output_bound(tmp_path):
    started=time.monotonic()
    with pytest.raises(agent.Unavailable):
        agent.run_bounded([sys.executable,'-c','import time; time.sleep(20)'],'',os.environ,tmp_path,.15)
    assert time.monotonic()-started < 3
    with pytest.raises(ValueError):
        agent.run_bounded([sys.executable,'-c','print("x"*200000)'],'',os.environ,tmp_path,2)


def test_private_environment_and_fixed_tools(tmp_path,monkeypatch):
    key=tmp_path/'key'; key.write_text('fake-test-key')
    monkeypatch.setenv('DEEPSEEK_API_KEY_FILE',str(key))
    monkeypatch.setenv('OWNER_SECRET','never-inherit')
    def runner(argv,prompt,env,cwd,seconds):
        assert 'OWNER_SECRET' not in env
        assert '--no-shell' in argv and '--no-file-tools' in argv
        assert env['ALLOW_WRAPPER_TOOLS']=='false'
        assert '--no-mcp' in argv and '--no-web-search' in argv
        assert env['HOME']==str(cwd)
        return json.dumps({'ok':True,'result':json.dumps({'decision':'reply','message':'ok','changes':{}})})
    agent.invoke('aginti','hello',tmp_path,runner)


def test_endpoint_rejects_insecure_remote_and_credentials(monkeypatch):
    for url in ['http://public.example','http://user:pass@localhost','https://example.com/?token=x']:
        monkeypatch.setenv('STUDIO_AGENT_URL',url)
        with pytest.raises(ValueError): agent_plan.sandbox_plan({})


def test_http_auth_size_busy_and_valid_plan(monkeypatch):
    import threading
    import urllib.request
    import urllib.error
    monkeypatch.setattr(agent.Handler,'token','x'*40)
    monkeypatch.setattr(agent,'plan',lambda value:{'decision':'reply','message':'ok','changes':{}})
    server=agent.Server(('127.0.0.1',0),agent.Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
    def request(token='x'*40,body=b'{}'):
        return urllib.request.urlopen(urllib.request.Request(
            f'http://127.0.0.1:{server.server_port}/v1/plan',data=body,
            headers={'Authorization':'Bearer '+token}),timeout=2)
    try:
        with pytest.raises(urllib.error.HTTPError) as err: request('wrong')
        assert err.value.code==401
        with pytest.raises(urllib.error.HTTPError) as err: request(body=b'x'*100001)
        assert err.value.code==422
        agent.Handler.gate.acquire()
        try:
            with pytest.raises(urllib.error.HTTPError) as err: request()
            assert err.value.code==429
        finally:agent.Handler.gate.release()
        with request() as response: assert json.load(response)['message']=='ok'
    finally:server.shutdown(); server.server_close(); thread.join()
