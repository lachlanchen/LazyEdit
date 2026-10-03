from lazyedit.local_delivery import local_package_params
import pytest


def test_shared_delivery_is_opt_in_and_never_sent_to_remote_publisher(tmp_path, monkeypatch):
    package = tmp_path / 'prepared.zip'
    package.write_bytes(b'prepared')
    monkeypatch.delenv('LAZYEDIT_LOCAL_PACKAGE_ROOT', raising=False)
    assert local_package_params(package, 'http://127.0.0.1:8081/publish') == {}
    monkeypatch.setenv('LAZYEDIT_LOCAL_PACKAGE_ROOT', str(tmp_path))
    assert local_package_params(package, 'http://lazyingart:8081/publish') == {}
    assert local_package_params(package, 'http://127.0.0.1:8081/publish') == {'local_package': str(package)}
    assert local_package_params(package, 'http://[::1]:8081/publish') == {'local_package': str(package)}
    with pytest.raises(ValueError):
        local_package_params(tmp_path / 'missing.zip', 'http://127.0.0.1:8081/publish')
