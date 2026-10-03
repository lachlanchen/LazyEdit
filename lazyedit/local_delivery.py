"""Opt-in same-workspace ZIP handoff; remote/Pi delivery stays unchanged."""
import os
from pathlib import Path
from urllib.parse import urlsplit


def local_package_params(zip_path, url):
    configured = os.getenv('LAZYEDIT_LOCAL_PACKAGE_ROOT')
    endpoint = urlsplit(url)
    if not configured or endpoint.scheme != 'http' or endpoint.hostname not in {'127.0.0.1', 'localhost', '::1'}:
        return {}
    root, package = Path(configured).resolve(), Path(zip_path).resolve()
    if not package.is_relative_to(root) or not package.is_file() or package.suffix.lower() != '.zip':
        raise ValueError('Local publish package must be a ZIP inside this workspace data root')
    return {'local_package': str(package)}
