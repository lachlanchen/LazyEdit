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
