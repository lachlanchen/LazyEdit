# Shipinhao Session And Form Commit Fix

Date: 2026-06-25

## Summary

This note documents the fix for two Shipinhao AutoPublish regressions:

1. Terminal-opened Shipinhao Chromium and code-opened Shipinhao Chromium did not reliably share the same login profile.
2. Shipinhao title/description fields could appear filled in the browser but not persist into the published post, because the description editor was being changed too directly in the DOM.

The verified fix is in AutoPublish commit:

- `7d51e0d fix shipinhao session reuse and form inputs`

The LazyEdit parent repo was updated to point at that submodule commit:

- `3f0e1fb update autopublish shipinhao fixes`

## Runtime Locations

- LazyEdit repo: `/home/lachlan/DiskMech/Projects/lazyedit`
- AutoPublish submodule: `/home/lachlan/DiskMech/Projects/lazyedit/AutoPublish`
- Live AutoPublish host: `lazyingart`
- Live AutoPublish repo: `/home/lachlan/Projects/autopub`
- Live AutoPublish tmux session: `autopub`
- Live AutoPublish HTTP endpoint: `http://lazyingart:8081`
- Shipinhao Chromium debug port: `127.0.0.1:5006`
- Shipinhao shared profile: `/home/lachlan/chromium_dev_session_5006`

## Symptoms

### Login Profile Split

Running `start_chromium_shipinhao` manually could require login, while the code-driven browser also required login, because each path could start or kill Chromium independently.

The desired behavior is:

- if the user logs in through the terminal helper, AutoPublish reuses that browser/profile;
- if AutoPublish opens/logs in the browser, the terminal helper reuses that browser/profile;
- the session survives for however long Shipinhao/WeChat allows.

### Description Not Persisting

Shipinhao showed the description field filled during automation, but the published post did not show the description.

Root cause: the automation was setting the `contenteditable` description editor mostly by direct DOM mutation (`textContent`/`innerHTML`) plus events. The Vue/editor state could fail to treat that as real user input, so the server-side publish payload could omit the description even though the textbox looked filled.

## Code Changes

### AutoPublish `app.py`

Changed browser startup from "kill and restart all Chromium sessions" to "reuse an existing debugging session when the port is open".

Important behavior:

- `stop_and_start_chromium_sessions()` now checks each platform port first.
- Shipinhao reuses port `5006` when it is already listening.
- Browser killing only happens when `AUTOPUBLISH_FORCE_BROWSER_RESTART` is set to `1`, `true`, `yes`, or `y`.

This avoids destroying a valid logged-in Shipinhao session right before publishing.

### AutoPublish `scripts/setup_chromium_alias_for_pi.sh`

Changed the Chromium aliases into shell functions.

Important behavior:

- `start_chromium_shipinhao` uses the same profile as the code path:
  - `/home/lachlan/chromium_dev_session_5006`
- If port `5006` is already open, it prints a reuse message and does not launch a second Chromium with a locked or separate profile.

Expected helper output:

```text
Reusing existing Chromium session for shipinhao on port 5006 (/home/lachlan/chromium_dev_session_5006).
```

### AutoPublish `pub_shipinhao.py`

Updated selectors and input behavior for the current Shipinhao UI.

Short title selector now covers the newer placeholder:

```text
填写短标题有机会获得更多流量
```

Description input now prefers real Selenium typing into the `contenteditable` editor:

1. switch into the Shipinhao content frame;
2. scroll and click `.input-editor[contenteditable]`;
3. select existing text with `Ctrl+A`;
4. delete existing content;
5. send the description in chunks through Selenium;
6. dispatch `input`, `change`, and `blur`;
7. read the field back and verify normalized text.

There is still a JavaScript fallback, but it now uses selection and `document.execCommand('insertText')` before falling back to direct DOM assignment.

This is important because Shipinhao's editor state must receive a real input path, not just a visible DOM text mutation.

## Deployment Steps Used

Compile locally before sync:

```bash
cd /home/lachlan/DiskMech/Projects/lazyedit
python -m py_compile AutoPublish/pub_shipinhao.py AutoPublish/app.py
```

Sync changed files to the Pi:

```bash
rsync -av AutoPublish/app.py AutoPublish/pub_shipinhao.py \
  lachlan@lazyingart:/home/lachlan/Projects/autopub/

rsync -av AutoPublish/scripts/setup_chromium_alias_for_pi.sh \
  lachlan@lazyingart:/home/lachlan/Projects/autopub/scripts/setup_chromium_alias_for_pi.sh
```

Install the updated Chromium helper functions on the Pi:

```bash
ssh lachlan@lazyingart \
  'cd /home/lachlan/Projects/autopub && bash scripts/setup_chromium_alias_for_pi.sh'
```

Compile on the Pi:

```bash
ssh lachlan@lazyingart \
  'cd /home/lachlan/Projects/autopub && python -m py_compile app.py pub_shipinhao.py'
```

Restart only the AutoPublish app process inside tmux. Do not kill the Chromium process unless explicitly needed:

```bash
ssh lachlan@lazyingart \
  'tmux send-keys -t autopub:0 C-c; sleep 2; \
   tmux send-keys -t autopub:0 "cd /home/lachlan/Projects/autopub && source /home/lachlan/venvs/autopub/bin/activate && python app.py --refresh-time 1800 --port 8081" C-m'
```

## Verification Commands

Check the Shipinhao browser and AutoPublish service on the Pi:

```bash
ssh lachlan@lazyingart \
  'ps -eo pid,cmd | rg "chromium.*remote-debugging-port=5006|python app.py --refresh-time" || true'
```

Check that the terminal helper reuses the same browser:

```bash
ssh lachlan@lazyingart \
  'bash -lc "source ~/scripts/sourced_chromium_aliases.sh; start_chromium_shipinhao"'
```

Check remote queue state:

```bash
curl -fsS http://lazyingart:8081/publish/queue | jq .
```

Tail the live Pi publishing log:

```bash
ssh lachlan@lazyingart \
  'tmux capture-pane -pt autopub:0 -S -180 | tail -n 180'
```

## Verified Publish Test

Test command from LazyEdit:

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python scripts/lazyedit_publish.py \
  --video-id 408 \
  --use-current-settings \
  --platforms shipinhao \
  --no-process \
  --guided-monitor \
  --remote-log-command "ssh lachlan@lazyingart 'tmux capture-pane -pt autopub:0 -S -200 | tail -n 200'" \
  --wait \
  --poll-seconds 10 \
  --publish-timeout 7200
```

Verified result:

- LazyEdit publish job: `216`
- Remote AutoPublish job: `job-1782353937853-1`
- Remote status: `done`
- Queue after publish: `queue_size: 0`, `is_publishing: false`

Important live log lines:

```text
Preparing Chromium sessions before publishing...
Reusing existing shipinhao Chromium session on port 5006.
Already logged in.
Shipinhao post-upload editor is stable: {'hasDescription': True, 'hasPreviewVideo': True, 'hasPublishButton': True, 'hasShortTitle': True, 'publishDisabled': False, 'ready': True, 'uploading': False}
Shipinhao description set (252 chars).
Shipinhao short title set to: '螢火蟲的森林重逢'
Shipinhao save draft result: {'className': 'weui-desktop-btn weui-desktop-btn_default', 'disabled': False, 'exists': True}
Shipinhao publish button ready: {'className': 'weui-desktop-btn weui-desktop-btn_primary', 'disabled': False, 'exists': True}
Process completed successfully!
Successfully published on ShiPinHao.
```

The user verified that the published Shipinhao post showed both title and description.

## Operational Notes

- If `/publish` is checked during a restart, LazyEdit can cache a temporary "autopublish service not reachable" result for about 30 seconds. Wait for the cache window and retry after confirming `http://lazyingart:8081/publish/queue` responds.
- The Pi repo has unrelated local runtime changes and generated files. Avoid a broad `git pull` or reset there unless those local changes are intentionally cleaned up. For this fix, the three touched live files were synced directly and verified to match `origin/main`.
- If future Shipinhao posts visibly fill the description editor but publish without description, inspect whether the input path is still using Selenium typing. Avoid returning to pure `textContent`/`innerHTML` mutation for the contenteditable editor.
- If the publish management list omits a description but the post detail shows it, that is probably Shipinhao list UI behavior, not an AutoPublish input failure.

