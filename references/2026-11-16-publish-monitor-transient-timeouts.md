# Keep following a dispatched publication after a status timeout

The publish CLI could exit with `ERROR: timed out` while its accepted AutoPublish job was still running. The timeout came from a status request, not a confirmed publication failure. Starting the CLI again with `--publish` would create another dispatch and risk a duplicate post.

`wait_for_publish` now retries read-only queue polling after transport errors, incomplete HTTP responses, invalid JSON responses, or temporary HTTP failures (408, 429, 500, 502, 503, 504). It keeps the original local job ID and overall monitoring deadline. Authentication and other permanent HTTP errors still stop the monitor. Native terminal job failures are still reported as failures.

This change does not retry upload or submission, change a queue entry, restart a browser, or treat an unavailable status as success. After an interrupted monitor, resume `wait_for_publish` with the existing job ID; reconcile its remote receipt before considering any platform-specific recovery.

Validation:

```bash
/home/lachlan/miniconda3/envs/lazyedit/bin/python -m pytest tests/test_lazyedit_publish_cli.py -q
```

All 23 tests pass, including regressions for timeout recovery using GET requests only, temporary server recovery, immediate authentication failure, and the original overall timeout.
