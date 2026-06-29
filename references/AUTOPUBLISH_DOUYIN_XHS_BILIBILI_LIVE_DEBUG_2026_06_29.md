# AutoPublish Douyin/XHS/Bilibili Live Debug Notes

Date: 2026-06-29

## Context

The MV publish target was:

```text
/home/lachlan/DiskMech/Projects/lazyedit/DATA/aya_chan_hikari_ame_full_mv_song_locked_portrait_fg30_bottom40_2026-06-29/aya_chan_hikari_ame_full_mv_song_locked_portrait_fg30_bottom40_2026-06-29.mp4
```

It was repackaged through LazyEdit as video id `427`, publication session `17`,
category `lalamv`, no burned subtitles, and the configured LazyEdit logo.

## Things To Remember

- If a file is already under LazyEdit `DATA/`, publish by `--video-id` or use a
  non-colliding `--filename`. Uploading the same `DATA/<stem>/<filename>` path
  through LazyEdit can truncate the source file.
- On the Pi, Chromium creator sessions need `--password-store=basic` so the
  post-reboot keyring does not block page creation. Manual aliases and
  AutoPublish launch flags should match.
- XiaoHongShu now uses a custom `xhs-publish-btn` for the final red publish
  control. Close hashtag popovers with Escape/blur before clicking publish.
- Bilibili can show an optional SMS verification overlay for upload-completion
  notifications. Close it; it is not the account-login QR flow.
- Bilibili custom cover upload is optional. If the cover dialog does not open,
  keep the default generated cover and continue publishing.
- Bilibili retries must reset the SPA upload page and track the current
  filename's own upload row. Generic `上传完成` selectors can match stale rows.
- If Bilibili reports `0.0MB/0.0MB` and the browser-side `preupload` request
  returns code `601` with `您上传视频过快，请您稍作休息后再继续`, stop retrying and
  wait for cooldown. Repeated retries extend the cooldown.

## Useful Commands

Check the remote queue:

```bash
ssh lachlan@lazyingart 'curl -fsS http://127.0.0.1:8081/publish/queue | python3 -m json.tool'
```

Tail the Pi AutoPublish session:

```bash
ssh lachlan@lazyingart 'tmux capture-pane -pt autopub:0 -S -140 | tail -100'
```

Probe Bilibili cooldown from the logged-in browser:

```bash
ssh lachlan@lazyingart "cd ~/Projects/autopub && /home/lachlan/venvs/autopub/bin/python - <<'PY'
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
opts = Options(); opts.add_experimental_option('debuggerAddress', '127.0.0.1:5005')
d = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=opts)
url = 'https://member.bilibili.com/preupload?r=upos&profile=ugcfx%2Fbup&ssl=0&version=2.14.0.0&build=2140000&webVersion=2.14.0&probe_version=20250923&upcdn=txa&zone=cs&name=cooldown_probe.mp4&size=38363139'
script = '''
const url = arguments[0];
const cb = arguments[arguments.length - 1];
fetch(url, {credentials: 'include'}).then(async r => cb({status:r.status, text:(await r.text()).slice(0,500)})).catch(e => cb({error:String(e)}));
'''
print(d.execute_async_script(script, url))
PY"
```

Retry a prepared LazyEdit publication session:

```bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate lazyedit
python scripts/lazyedit_publish.py \
  --video-id 427 \
  --publication-session-id 17 \
  --platforms bilibili \
  --publish-category lalamv \
  --no-process \
  --new-run \
  --no-burn-subtitles \
  --logo-position top-left \
  --wait \
  --guided-monitor \
  --poll-seconds 15 \
  --remote-log-command "ssh lachlan@lazyingart 'tmux capture-pane -pt autopub:0 -S -120 | tail -80'"
```

## Source Of Truth

The detailed AutoPublish-side record is:

```text
AutoPublish/docs/DOUYIN_XHS_BILIBILI_DEBUG.md
```
