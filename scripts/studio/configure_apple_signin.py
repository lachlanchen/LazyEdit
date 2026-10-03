#!/usr/bin/env python
"""Prepare Studio's own Apple web identity without changing another app.

Like configure_google_signin.py, this saves protected configuration and a
rollback, but never restarts services or claims a real sign-in passed.
"""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import time

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import load_pem_private_key

from configure_google_signin import atomic_json, protected_file


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--client-json", type=Path, required=True)
    parser.add_argument("--enable", action="store_true")
    args = parser.parse_args()
    root = args.state.resolve()
    info = root.stat()
    if not root.is_dir() or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise ValueError("Use the protected hosted state directory")
    config_path = protected_file(root / "config.json")
    gateway_path = protected_file(root / "registry/gateway.json")
    config = json.loads(config_path.read_text())
    gateway = json.loads(gateway_path.read_text())
    client = json.loads(protected_file(args.client_json).read_text())
    domain = config.get("domain", "")
    if not re.fullmatch(r"[a-z0-9.-]+", domain) or gateway.get("domain") != domain:
        raise ValueError("Hosted domain mismatch")
    if client.get("redirectURI") != f"https://{domain}/accounts/oauth/callback/apple":
        raise ValueError("Register the exact Studio HTTPS callback")
    if client.get("primaryAppId") != "art.lazying.lazyedit" or client.get("clientId") != "art.lazying.lazyedit.web":
        raise ValueError("Use LazyEdit's own primary App ID and web Services ID")
    if any(not re.fullmatch(r"[A-Z0-9]{10}", client.get(k, "")) for k in ("teamId", "keyId")):
        raise ValueError("Invalid Apple signing identity")
    key_path = protected_file(client["privateKeyFile"])
    key = load_pem_private_key(key_path.read_bytes(), password=None)
    if not isinstance(key, ec.EllipticCurvePrivateKey) or not isinstance(key.curve, ec.SECP256R1):
        raise ValueError("Use the downloaded Apple P-256 private key")
    existing = config.get("oauth", {})
    if existing != gateway.get("oauth", {}) or not re.fullmatch(r"[a-f0-9]{64}", existing.get("encryptionKey", "")):
        raise ValueError("Preserve and reconcile the existing identity encryption key")
    backup = root / "rollbacks" / f"apple-signin-{time.time_ns()}"
    backup.mkdir(parents=True)
    for file in (config_path, gateway_path):
        dest = backup / file.relative_to(root)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, dest)
    credential = root / "registry/apple-signin.p8"
    if credential.exists() or credential.is_symlink():
        protected_file(credential)
        shutil.copy2(credential, backup / credential.name)
    descriptor, temporary = tempfile.mkstemp(prefix=".apple-", dir=credential.parent)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(key_path.read_bytes())
    os.replace(temporary, credential)
    oauth = {**existing, "apple": {
        "enabled": args.enable, "clientId": client["clientId"],
        "teamId": client["teamId"], "keyId": client["keyId"],
        "privateKeyFile": "/registry/apple-signin.p8",
    }}
    atomic_json(config_path, {**config, "oauth": oauth})
    atomic_json(gateway_path, {**gateway, "oauth": oauth})
    print(json.dumps({"provider": "apple", "enabled": args.enable,
                      "rollback": str(backup), "restartPerformed": False,
                      "realSignInQualified": False}, indent=2))


if __name__ == "__main__":
    main()
