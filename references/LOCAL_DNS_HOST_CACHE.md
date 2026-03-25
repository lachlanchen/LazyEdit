# Local DNS Host Cache

## Why This Exists

Some home routers resolve local hostnames correctly, but the local Linux resolver path may still fail on single-label names such as:

```text
lazyingart
```

Example failure:

```bash
ping lazyingart
# ping: lazyingart: Temporary failure in name resolution
```

At the same time, the router DNS may already know the correct host:

```bash
nslookup lazyingart 192.168.1.1
```

If that returns an IP, the issue is not the router record. The issue is that local stub resolution is not using that single-label hostname successfully.

## Script

Use [`scripts/cache_host_from_dns.sh`](../scripts/cache_host_from_dns.sh).

Purpose:

- discover a real DNS server from the machine
- query that DNS server for a hostname
- cache the resolved result into `/etc/hosts`
- avoid hardcoding the IP in advance

Default target hostname:

- `lazyingart`

## Typical Usage

```bash
sudo ./scripts/cache_host_from_dns.sh
```

Explicit hostname:

```bash
sudo ./scripts/cache_host_from_dns.sh --hostname lazyingart
```

Force a specific DNS server:

```bash
sudo ./scripts/cache_host_from_dns.sh --hostname lazyingart --dns-server 192.168.1.1
```

## What The Script Does

1. tries the local resolver with `getent hosts`
2. if that fails, discovers DNS servers from:
   - `resolvectl`
   - `/run/systemd/resolve/resolv.conf`
   - `/etc/resolv.conf`
   - default gateway as a fallback
3. queries those DNS servers with `nslookup` or `dig`
4. if a real IP is found, updates `/etc/hosts`
5. creates a backup of `/etc/hosts`
6. avoids duplicate entries for the same hostname
7. replaces a stale entry if the hostname exists with a different IP

## Resulting Entry

The script appends a tagged cache line like:

```text
192.168.1.111 lazyingart # lazyedit-host-cache
```

The exact IP is discovered dynamically. It is not required to be hardcoded in the script.

## Why `/etc/hosts` Is Used At All

This is not meant to replace real DNS.

It is a local cache/fallback for cases where:

- router DNS is correct
- local resolution path is inconsistent
- a hostname must work immediately for scripts, ping, or browser access

## Verification

After running the script, these should work:

```bash
getent hosts lazyingart
ping -c 1 lazyingart
```

## Safety

- the script is idempotent for the target hostname
- it backs up `/etc/hosts` before changing it
- it only writes after resolving a real IP
- if no IP can be resolved, it exits with an error instead of writing a guessed value
