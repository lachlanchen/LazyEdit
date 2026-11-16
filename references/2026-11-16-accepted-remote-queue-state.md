# Keep accepted remote jobs out of the local dispatch pool

Queue polling can see a newly accepted remote receipt before the upload request finishes returning. When that receipt says `queued`, the old reconciler wrote `queued` into the local job row. The local worker then claimed the same row again, rebuilt the package and tried to dispatch it a second time. One observed attempt was rejected by AutoPublish's busy-package guard, leaving a misleading local failure while the accepted remote job continued normally.

A remote queue position is presentation state. After acceptance, the local dispatch is already in progress. Receipt reconciliation now keeps the local row `running` while continuing to show the remote `queued` state in the UI. Matching active receipts also repair older false conflict states without creating another publication. Terminal remote results still finish the local job normally.

The local claim query additionally excludes rows with an existing remote job ID or remote status. This prevents a stale queued row or an uncertain dispatch from becoming new local work even if a caller writes the wrong local status.

Validation:

```bash
python -m pytest tests/test_remote_queued_publish_receipt.py tests/test_publish_dispatch.py tests/test_lazyedit_publish_cli.py -q
```

All 31 tests pass. A separate PostgreSQL check executed the exact claim function against a temporary shadow table inside a rolled-back transaction: a fresh job was claimed, while accepted and uncertain remote dispatches were not. No production queue rows were changed by that test.

Activate backend changes only after verifying that local editing/preparation is idle and accepted jobs have durable remote receipts. Preserve native AutoPublish work, message/job identity, hosted acceptance locks and other app processes. Do not resend an accepted job merely because the old local detail says `Publish failed`.
