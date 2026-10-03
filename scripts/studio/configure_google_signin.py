#!/usr/bin/env python
"""Configure Studio's own Google client in protected control-plane files.

This does not restart anything. After qualification, restart only the hosted
gateway at an idle boundary; preserve the saved rollback files.
"""
import argparse
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import stat
import tempfile
import time


def protected_file(path):
    path = Path(path)
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise ValueError("Use an owner-only regular configuration file")
    return path


def atomic_json(path, data):
    descriptor, temporary = tempfile.mkstemp(prefix=".oauth-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w") as stream:
            json.dump(data, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--client-json", type=Path, required=True)
    parser.add_argument("--enable", action="store_true", help="Enable the prepared client; real provider qualification is separate")
    args = parser.parse_args()
    root = args.state.resolve()
    info = root.stat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise ValueError("Use the protected hosted state directory")
    config_path = protected_file(root / "config.json")
    gateway_path = protected_file(root / "registry/gateway.json")
    config = json.loads(config_path.read_text())
    gateway = json.loads(gateway_path.read_text())
    client = json.loads(protected_file(args.client_json).read_text()).get("web", {})
    domain = config.get("domain", "")
    if not re.fullmatch(r"[a-z0-9.-]+", domain) or gateway.get("domain") != domain:
        raise ValueError("Hosted domain mismatch")
    redirect = f"https://{domain}/accounts/oauth/callback/google"
    if redirect not in client.get("redirect_uris", []):
        raise ValueError("Register the exact Studio HTTPS callback")
    if not re.fullmatch(r"[0-9]+-[A-Za-z0-9_-]+\.apps\.googleusercontent\.com", client.get("client_id", "")):
        raise ValueError("Invalid Google web client")
    secret = client.get("client_secret", "")
    if not isinstance(secret, str) or not 16 <= len(secret) <= 1024 or any(c.isspace() for c in secret):
        raise ValueError("Invalid Google client credential")
    existing = config.get("oauth", {})
    if existing != gateway.get("oauth", {}):
        raise ValueError("Reconcile existing provider configurations first")
    key = existing.get("encryptionKey") or secrets.token_hex(32)
    if not re.fullmatch(r"[a-f0-9]{64}", key):
        raise ValueError("Preserve the valid identity encryption key")
    backup = root / "rollbacks" / f"google-signin-{time.time_ns()}"
    backup.mkdir(parents=True)
    for file in (config_path, gateway_path):
        dest = backup / file.relative_to(root)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, dest)
    credential = root / "registry/google-client.secret"
    if credential.exists() or credential.is_symlink():
        protected_file(credential)
        shutil.copy2(credential, backup / "google-client.secret")
    descriptor, temporary = tempfile.mkstemp(prefix=".google-", dir=credential.parent)
    with os.fdopen(descriptor, "w") as stream:
        stream.write(secret + "\n")
    os.replace(temporary, credential)
    oauth = {**existing, "encryptionKey": key, "google": {
        "enabled": args.enable, "clientId": client["client_id"],
        "clientSecretFile": "/registry/google-client.secret",
    }}
    atomic_json(config_path, {**config, "oauth": oauth})
    atomic_json(gateway_path, {**gateway, "oauth": oauth})
    print(json.dumps({"provider": "google", "enabled": args.enable,
                      "rollback": str(backup), "restartPerformed": False,
                      "realSignInQualified": False}, indent=2))


if __name__ == "__main__":
    main()
