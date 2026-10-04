import importlib.util
from pathlib import Path

import pytest


path = Path(__file__).resolve().parents[1] / 'scripts/studio/backport_owner_composer.py'
spec = importlib.util.spec_from_file_location('owner_composer_backport', path)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


def test_permissions_come_from_the_authenticated_scope_and_owner_gate_survives():
    source = """function ownerOnly(p){if(config.ownerUsername) fail(403)}
json(res,200,{scopes:p.scopes,issuer:origin});
json(res,200,{defaults:composerDefaults(settings),sessions:[]});"""
    result = helper.patch_owner_server(source)
    assert result.startswith(source.splitlines()[0])
    assert result.count("publishing:p.scopes.includes('publication.publish')") == 2
    assert helper.patch_owner_server(result) == result
    with pytest.raises(ValueError, match='baseline'):
        helper.patch_owner_server(source.replace('scopes:p.scopes,issuer:origin', 'issuer:origin'))
    with pytest.raises(ValueError, match='owner-only'):
        helper.patch_owner_server(source.replace('function ownerOnly(p)', 'function other(p)'))
