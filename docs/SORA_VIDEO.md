# Sora Video Generation (Preview)

Create, iterate on, and download videos using OpenAI’s Sora 2 API via the helper scripts in `agi/`.

## Requirements
- Environment variable `OPENAI_API_KEY` set for the project that has Videos API enabled.
- Optional project scoping: set `OPENAI_PROJECT` (or `OPENAI_PROJECT_ID`) if you use multiple projects.
- Python deps: `openai` and `httpx` (installed via your existing environment).

## Models
- `sora-2` – faster and cheaper, good for iteration.
- `sora-2-pro` – higher quality, slower, and more expensive.

## Supported Parameters
- Seconds: `4`, `8`, or `12`
- Size (resolution):
  - Landscape: `1280x720`, `1792x1024`
  - Portrait: `720x1280`, `1024x1792`

If you pass unsupported values, the API returns HTTP 400 with a message like:
- `Invalid value: '15'. Supported values are: '4', '8', and '12'.`
- `Invalid value: '1920x1080'. Supported values are: '720x1280', '1280x720', '1024x1792', and '1792x1024'.`

## CLI Helpers
Two scripts live under `agi/`:
- `agi/video_requests.py` – generic helper to create → poll → download.
- `agi/demo_fantasy_woman.py` – demo with a safe, tasteful default prompt.

### Quick Demo (default prompt)
```bash
# From repo root, inside the conda env (python from lazyedit env)
python -m agi.demo_fantasy_woman \
  --seconds 8 \
  --size 1280x720 \
  --output DATA/sora_oracle_valley.mp4
```

### Custom Prompt (English/Japanese examples)
```bash
# English
python -m agi.demo_fantasy_woman \
  --prompt "A fictional adult woman known as the Oracle of the Mist Valley stands on a wind-swept cliff at dawn..." \
  --seconds 8 \
  --size 1280x720 \
  --output DATA/sora_oracle_valley_en.mp4

# Japanese (12s, landscape)
python -m agi.demo_fantasy_woman \
  --prompt "夜明けの霧の谷。伝説の女神官『霧の谷のオラクル』が断崖に立つ..." \
  --seconds 12 \
  --size 1280x720 \
  --output DATA/sora_oracle_valley_jp.mp4
```

### Low-Level Helper (arbitrary prompt)
```bash
python agi/video_requests.py \
  --prompt "Wide tracking shot of a teal coupe through a desert highway" \
  --model sora-2 \
  --size 1280x720 \
  --seconds 8 \
  --output DATA/sora_demo.mp4
```

## Troubleshooting
- 403 Forbidden: Usually means your project/key does not have Videos API enabled (or wrong project). Set `OPENAI_PROJECT` to the project ID that has access.
- 400 Invalid value: Adjust `--seconds` to 4/8/12 and `--size` to one of the supported resolutions above.
- Slow completion: Renders can take minutes. The helper shows a progress bar and polls every 10 seconds.

## Notes
- Content policy: prompts must be suitable for under‑18 audiences and avoid real people/copyrighted characters.
- Costs: billed per generated second; higher for `sora-2-pro`.
- Download URLs expire within about 1 hour—files are saved immediately to your local `DATA/` path.

