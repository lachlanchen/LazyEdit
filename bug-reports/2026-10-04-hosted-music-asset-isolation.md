# Hosted music package asset isolation

The hosted cell forwarded music package requests to the legacy package builder
without validating its filesystem arguments. The owner CLI legitimately accepts
local absolute paths, but a hosted member must not copy runtime files into a
downloadable music package or override the workspace's publisher endpoint.

`hosted/music-input.mjs` validates every file alias consumed by
`MusicPackageHandler`, canonicalizes only files within the member's media root,
and rejects lexical traversal, sibling-prefix paths and symlink escapes.
`hosted/cell.mjs` validates a bounded authenticated, same-origin JSON request
before forwarding its normalized body to the fixed local package endpoint.
Ordinary metadata, lyrics text and queue flags are preserved. No owner backend
or Pi publication script changes are required.

`hosted/music-input.test.mjs` uses its own cell, fake backend and harmless
fixtures. A valid private package reaches the backend with normalized paths.
Unauthenticated requests, outside assets and publisher overrides are rejected;
the backend receives exactly one valid request. All 32 hosted/Studio contract
tests passed with the new regression. No production file was exfiltrated and no
external post was created during qualification.

Run the complete suite, including the base contract files:

```bash
NODE_PATH="$PWD/app/node_modules" node --test \
  hosted/test.mjs hosted/*.test.mjs studio/test.mjs studio/*.test.mjs
```

Promote only immutable private workspace images at an idle queue boundary with
`scripts/studio/promote_cells.py`. Keep databases, media and profiles; do not
restart the original owner backend or Pi. See the [account handoff](../references/2026-10-04-hosted-account-and-release-handoff.md).

The first live promotion stopped before changing any service because the old
helper enumerated retained Compose receipts, including a deleted test member.
`promotion_workspaces.py` now reads the registry without writing it, selects
only ready members and verifies each Compose/bootstrap identity. Deleted
receipts are never replayed. Unfinished provisioning/deletion or mismatched
identity stops the upgrade. Two focused pytest cases passed for deleted
receipts, unchanged registry state, incomplete cleanup and identity mismatch.

The corrected promotion completed for both permanent workers and the
gateway/provisioner on `native-login-20261004f` (image source `27fbae0`). Live
authenticated administrator and member requests verified normal private asset
forwarding, outside-file rejection and publisher-override rejection. Both
workers were healthy and the original owner backend/Pi were preserved. No
package or external post was created during the live checks.
