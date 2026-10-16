import os
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'studio'))
from provider_credentials import load_openai_key_file


def test_explicit_file_overrides_inherited_key(tmp_path,monkeypatch):
    p=tmp_path/'key';p.write_text('replacement-test');p.chmod(0o600)
    monkeypatch.setenv('OPENAI_API_KEY','old-test')
    monkeypatch.setenv('OPENAI_API_KEY_FILE',str(p))
    assert load_openai_key_file()
    assert os.environ['OPENAI_API_KEY']=='replacement-test'


def test_absent_configuration_preserves_environment(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY_FILE',raising=False)
    monkeypatch.setenv('OPENAI_API_KEY','existing-test')
    assert not load_openai_key_file()
    assert os.environ['OPENAI_API_KEY']=='existing-test'


def test_invalid_file_fails_closed(tmp_path,monkeypatch):
    p=tmp_path/'key';p.write_text('test');p.chmod(0o644)
    monkeypatch.setenv('OPENAI_API_KEY_FILE',str(p))
    with pytest.raises(ValueError):load_openai_key_file()
    p.chmod(0o600);p.write_text('')
    with pytest.raises(ValueError):load_openai_key_file()
