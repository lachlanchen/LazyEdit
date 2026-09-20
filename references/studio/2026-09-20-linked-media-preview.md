# Linked Media Preview Repair

## Defect And Bounded Fix

An owned media row can outlive the backend video. The linked-client `/media/`
authorization loop previously aborted on that row's 404, even when the requested
file existed and belonged to another valid video. It also continued looking up
unrelated records after ownership was already proven.

Skip only a parsed backend 404 during candidate lookup. Stop after the first
verified matching owned directory. Preserve scope, token, ownership, normalized
path, realpath containment and byte-range checks. Unexpected statuses, malformed
replies and backend failures still fail closed before ownership is established.
Do not delete ownership records or grant access merely because a file exists.

## Regression Tests

```sh
node --test studio/test.mjs studio/session.test.mjs studio/media.test.mjs
```

Node 22 is required for the existing SQLite implementation. New HTTP-level
tests reproduce deleted rows before/after a match, GET/HEAD/Range playback,
unrelated backend failures after a proven match, missing/other-owner media,
non-404 failures, malformed replies, missing scope, revoked grants, traversal
and symlink escape. The pre-fix test run failed three cases; all 15 tests pass
after the fix.

## Rollout Scope

The owner authorized restarting only the Studio worker. Package an immutable
copy of the current release with the tested server change and new test file;
preserve the exact deployed web assets and other server modules. Retarget only
the worker unit/config, retaining their original bytes for rollback. Do not run
account bootstrap, rewrite guard/tunnel units, restart the original backend,
change LazyTunnel/edge/firewall, or roll back a live account database.

The baseline live test proved a valid video detail returned 200 while its
authenticated preview returned 404. Acceptance requires the same video to
return matching bytes/digest, HEAD 200 and Range 206 after deployment, with
anonymous/revoked access denied. Test through the LightMind browser companion
as well. This repair does not authorize processing or a social-media post.

Deployment and final live acceptance are recorded after verification.
