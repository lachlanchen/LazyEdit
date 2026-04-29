# XiaoHongShu AutoPublish Layout Change Reference (March 2026)

This note captures the March 2026 XiaoHongShu web publish changes and the fixes
needed so LazyEdit -> AutoPublish publishing keeps working.

## What Broke

- The XiaoHongShu upload flow no longer exposed the old upload-ready marker
  `替换视频`.
- The page now uses a different publish layout and a different title/editor DOM.
- The old AutoPublish flow logged success immediately after clicking `发布`
  without verifying that the publish actually completed.
- Runtime secrets on `lazyingart` were no longer in `~/.bashrc`; they had been
  moved into the AutoPublish repo `.env`.

## Current Working XiaoHongShu DOM Signals

These markers were verified against the live page on `lazyingart`:

- Upload-ready / upload-complete marker:
  - `重新上传`
- Title input:
  - `input[placeholder="填写标题会有更多赞哦"]`
- Description editor:
  - `.tiptap.ProseMirror[contenteditable="true"]`
- Publish button area:
  - `.publish-page-publish-btn`
- Publish button:
  - the red button with text `发布`
  - current class included `custom-button bg-red`

## Verified Publish Behavior

When the real red `发布` button is clicked successfully:

- the compose page leaves the old publish state
- the URL changes to:
  - `https://creator.xiaohongshu.com/publish/publish?source=&published=true`
- the note then appears in note management

This behavior was verified live on `lazyingart` by publishing the note titled:

- `面對挑戰的時刻`

That note appeared in XHS note management on:

- `2026年03月25日 19:17`

## AutoPublish Fixes Applied

### 1. Upload readiness detection

`AutoPublish/pub_xhs.py` was updated to:

- accept `重新上传` as the upload-complete marker
- accept the title input and the ProseMirror editor as readiness signals
- target the current title placeholder and the current ProseMirror editor

### 2. Publish verification

`AutoPublish/pub_xhs.py` was updated to:

- target the bottom red `发布` button explicitly
- use Selenium click first, then JS click as fallback
- wait for a real post-publish state instead of assuming success immediately
- treat `published=true` or note-manager state as publish confirmation
- save an HTML snapshot on publish timeout/failure

### 3. Runtime env source

`AutoPublish/load_env.py` and `AutoPublish/app.py` were updated so runtime env
loading now works like this:

1. read repo-local `.env` first
2. use `.bashrc` only as fallback for missing values

This makes the repo `.env` the source of truth for AutoPublish runtime secrets.

### 4. Late-March runtime fixes on `lazyingart`

After the initial XHS layout fix, the live `lazyingart` runtime still exposed a
few operational issues:

- Gmail SMTP login mail for login-required screenshots was failing with:
  - `SMTPAuthenticationError: 535 Username and Password not accepted`
- the code still logged stale wording mentioning SendGrid, even though the live
  mail path was already SMTP-based
- account-name checks on some platforms still preferred the old string:
  - `陈苗LazyingArt懒人艺术`
- the newer visible account label is now commonly:
  - `LazyingArt懒人艺术`

The live AutoPublish code was updated so that:

- SMTP uses `APP_PASSWORD` as the real Gmail auth secret
- `SENDGRID_API_KEY` is no longer treated as the default Gmail password fallback
- startup env validation treats `APP_PASSWORD` as a critical variable
- login selectors for XiaoHongShu / ShiPinHao / Douyin prefer
  `LazyingArt懒人艺术` while still accepting the older names
- Shipinhao login-mail failure messages now refer to SMTP/auth failure, not
  SendGrid

Important operational note:

- the Gmail failure was confirmed to be a real Google-side auth rejection, not
  an env parser bug
- updating `APP_PASSWORD` in `~/Projects/autopub/.env` fixed SMTP auth and test
  sends again

### 5. What `localhost:<random_port>` means in Selenium timeouts

When AutoPublish logs an error like:

- `HTTPConnectionPool(host='localhost', port=56581): Read timed out`

that `localhost` port is the temporary local ChromeDriver HTTP server created by
Selenium, not XiaoHongShu or any remote platform.

On the failing `lazyingart` run, the stack showed the timeout happened during:

- `self.driver.get(url)` inside `login_xiaohongshu.py`

This means:

- Python could talk to ChromeDriver
- ChromeDriver then hung waiting for the attached Chromium instance to complete
  the browser command

On `lazyingart`, the related Chromium log showed GPU / GL init failures
(`Unsupported GLX version`, `EGL_NOT_INITIALIZED`), so the timeout should be
treated as a local browser/runtime stall, not a remote-site connectivity issue.

### 6. DISPLAY / xdotool caveat

`bring_to_front()` uses `xdotool`, which needs a valid X `DISPLAY`.

If AutoPublish is started manually with a bare command such as:

```bash
cd ~/Projects/autopub
/home/lachlan/venvs/autopub/bin/python app.py --refresh-time 1800 --port 8081
```

then Chromium can still launch because individual browser commands prefix
`DISPLAY=:1`, but `xdotool` can fail with:

- `Can't open display: (null)`

Preferred start path on `lazyingart`:

```bash
~/Projects/autopub/scripts/start_autopub_tmux.sh
```

That wrapper exports `DISPLAY=:1`, loads `.env`, and starts the tmux session in
the expected runtime environment.

## Current Runtime Paths

- LazyEdit deployment:
  - `/home/lachlan/DiskMech/Projects/lazyedit`
- AutoPublish source copy inside LazyEdit:
  - `/home/lachlan/DiskMech/Projects/lazyedit/AutoPublish`
- Live AutoPublish host:
  - `lazyingart`
- Live AutoPublish repo on host:
  - `/home/lachlan/Projects/autopub`
- Live AutoPublish secrets file:
  - `/home/lachlan/Projects/autopub/.env`

## Relevant Code Paths

- LazyEdit publish endpoint:
  - `app.py`
  - `POST /api/videos/{id}/publish`
- AutoPublish XHS publisher:
  - `AutoPublish/pub_xhs.py`
- AutoPublish env loader:
  - `AutoPublish/load_env.py`

## Useful Operational Checks

### Confirm the live env source

```bash
cd ~/Projects/autopub
/home/lachlan/venvs/autopub/bin/python load_env.py
```

Expected result:

- it should report loading from `~/Projects/autopub/.env`
- it should find `TULING_*`, `FROM_EMAIL`, `TO_EMAIL`, `APP_PASSWORD`

### Restart AutoPublish in tmux

```bash
ssh lazyingart
~/Projects/autopub/scripts/start_autopub_tmux.sh
```

### Confirm listener

```bash
ssh lazyingart
ss -ltnp | grep 8081
```

## Practical Debugging Checklist

If XiaoHongShu breaks again:

1. Check whether the upload-ready marker text changed again.
2. Inspect the title input placeholder.
3. Inspect the description editor class and whether it is still ProseMirror.
4. Confirm the real publish button is still inside `.publish-page-publish-btn`.
5. Do not trust a successful click alone; verify the post-publish URL or note-manager state.
6. If env vars are missing at startup, check `~/Projects/autopub/.env` before touching `.bashrc`.
7. If the timeout mentions `localhost:<port>`, inspect ChromeDriver/Chromium state before assuming the platform site is down.
8. If login screenshots stop emailing, verify the current Gmail `APP_PASSWORD` with a direct SMTP login test.

## Commit History To Remember

Key AutoPublish fixes from this incident:

- `18540a5` `fix xiaohongshu upload readiness detection`
- `2fcefad` `verify xiaohongshu publish completion`
- `1f2451e` `prefer repo dotenv over bashrc for runtime env`
