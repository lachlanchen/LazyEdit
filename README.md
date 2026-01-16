<p align="center">
  <img src="https://raw.githubusercontent.com/lachlanchen/lachlanchen/main/logos/banner.png" alt="LazyingArt banner" />
</p>

<p>
  <b>Languages:</b>
  <a href="README.md">English</a>
  · <a href="i18n/README.zh-Hant.md">中文（繁體）</a>
  · <a href="i18n/README.zh-Hans.md">中文 (简体)</a>
  · <a href="i18n/README.ja.md">日本語</a>
  · <a href="i18n/README.ko.md">한국어</a>
  · <a href="i18n/README.vi.md">Tiếng Việt</a>
  · <a href="i18n/README.ar.md">العربية</a>
  · <a href="i18n/README.fr.md">Français</a>
  · <a href="i18n/README.es.md">Español</a>
</p>

## Demos

<table>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_01_home_upload.png" alt="Home upload" width="240" />
      <br /><sub>Home · Upload</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_02_home_generate.png" alt="Home generate" width="240" />
      <br /><sub>Home · Generate</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_03_home_remix.png" alt="Home remix" width="240" />
      <br /><sub>Home · Remix</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_04_library.png" alt="Library list" width="240" />
      <br /><sub>Library</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_05_video_overview.png" alt="Video overview" width="240" />
      <br /><sub>Video overview</sub>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="figs/demos/demo_06_translation_preview.png" alt="Translation preview" width="240" />
      <br /><sub>Translation preview</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_07_burn_slots.png" alt="Burn slots" width="240" />
      <br /><sub>Burn slots</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_08_burn_layout.png" alt="Burn layout" width="240" />
      <br /><sub>Burn layout</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_09_keyframes_captions.png" alt="Keyframes and captions" width="240" />
      <br /><sub>Keyframes + captions</sub>
    </td>
    <td align="center">
      <img src="figs/demos/demo_10_metadata_generator.png" alt="Metadata generator" width="240" />
      <br /><sub>Metadata generator</sub>
    </td>
  </tr>
</table>

# LazyEdit

LazyEdit is a web app for end-to-end video creation, processing, and publishing. It combines prompt-based generation (Stage A/B/C), a multi-step processing pipeline, and an optional AutoPublish flow for social platforms.

## What it does

- **Generate**: Stage A/B/C prompt flow with Sora 2 and Veo 3.1 (via GRSAI).
- **Process**: transcribe → polish → translate → burn subtitles → keyframes → captions → metadata.
- **Publish**: package outputs and send to AutoPublish (optional).
- **Visual polish**: subtitle layouts, multilingual furigana/IPA/romaji, logo overlays, cover extraction.

## Submodules

- **AutoPublish** (`AutoPublish/`) - optional publishing pipeline
- **MultilingualWhisper** (`whisper_with_lang_detect/`) - transcription + VAD pipeline
- **VideoCaptionerWithVit** (`vit-gpt2-image-captioning/`) - ViT + GPT-2 captioning
- **VideoCaptionerWithClip** (`clip-gpt-captioning/`) - CLIP + GPT captioning (fallback)

## Quick start (dev)

```bash
git clone git@github.com:lachlanchen/LazyEdit.git
cd LazyEdit
git submodule update --init --recursive

conda activate lazyedit
python app.py -m lazyedit
```

Open http://localhost:8787 (set `LAZYEDIT_PORT` or `PORT` to change).

## Service install (optional)

The service installer does **not** generate config/scripts. Ensure these exist and are correct for your deployment:

- `lazyedit_config.sh`
- `start_lazyedit.sh`
- `stop_lazyedit.sh`

Then run:

```bash
sudo ./install_lazyedit.sh /path/to/lazyedit
```

Service commands:

- `sudo systemctl start lazyedit.service`
- `sudo systemctl stop lazyedit.service`
- `sudo systemctl status lazyedit.service`
- `sudo journalctl -u lazyedit.service`

## Configuration

Copy `.env.example` to `.env` and update values as needed.

Key overrides:

- `LAZYEDIT_PORT`, `PORT`
- `LAZYEDIT_UPLOAD_DIR`
- `LAZYEDIT_AUTOPUBLISH_URL`
- `LAZYEDIT_WHISPER_*` (script + models)
- `LAZYEDIT_CAPTION_*` (captioning scripts/roots)
- `GRSAI_API_BASE`, `GRSAI_API_KEY` (Veo)
- `OPENAI_API_KEY` (Sora + metadata)

## Project structure

- `app.py` - Tornado backend entrypoint
- `lazyedit/` - core processing logic
- `agi/` - video generation providers (Sora/Veo)
- `AutoPublish/` - optional publishing service (submodule)
- `whisper_with_lang_detect/` - transcription pipeline (submodule)
- `vit-gpt2-image-captioning/` - primary captioner (submodule)
- `clip-gpt-captioning/` - fallback captioner (submodule)
- `DATA/` - outputs (generated videos, processed assets)

## AutoPublish integration

AutoPublish runs as a separate service. Configure `LAZYEDIT_AUTOPUBLISH_URL` to point at the AutoPublish `/publish` endpoint.

## Troubleshooting

- Run `git submodule update --init --recursive` if captions/transcribe fail due to missing code.
- Ensure FFmpeg is installed and on PATH.
- Confirm your conda env matches the paths in `.env` and `lazyedit_config.sh`.
- For GPU issues, verify CUDA drivers and that your env has the right torch build.

## What your support makes possible

- <b>Keep tools open</b>: hosting, inference, data storage, and community ops.  
- <b>Ship faster</b>: weeks of focused open-source time on EchoMind, LazyEdit, and MultilingualWhisper.  
- <b>Prototype wearables</b>: optics, sensors, and neuromorphic/edge components for IdeasGlass + LightMind.  
- <b>Access for all</b>: subsidized deployments for students, creators, and community groups.

### Donate

<div align="center">
<table style="margin:0 auto; text-align:center; border-collapse:collapse;">
  <tr>
    <td style="text-align:center; vertical-align:middle; padding:6px 12px;">
      <a href="https://chat.lazying.art/donate">https://chat.lazying.art/donate</a>
    </td>
    <td style="text-align:center; vertical-align:middle; padding:6px 12px;">
      <a href="https://chat.lazying.art/donate"><img src="https://raw.githubusercontent.com/lachlanchen/lachlanchen/main/figs/donate_button.svg" alt="Donate" height="44"></a>
    </td>
  </tr>
  <tr>
    <td style="text-align:center; vertical-align:middle; padding:6px 12px;">
      <a href="https://paypal.me/RongzhouChen">
        <img src="https://img.shields.io/badge/PayPal-Donate-003087?logo=paypal&logoColor=white" alt="Donate with PayPal">
      </a>
    </td>
    <td style="text-align:center; vertical-align:middle; padding:6px 12px;">
      <a href="https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400">
        <img src="https://img.shields.io/badge/Stripe-Donate-635bff?logo=stripe&logoColor=white" alt="Donate with Stripe">
      </a>
    </td>
  </tr>
  <tr>
    <td style="text-align:center; vertical-align:middle; padding:6px 12px;"><strong>WeChat</strong></td>
    <td style="text-align:center; vertical-align:middle; padding:6px 12px;"><strong>Alipay</strong></td>
  </tr>
  <tr>
    <td style="text-align:center; vertical-align:middle; padding:6px 12px;"><img alt="WeChat QR" src="https://raw.githubusercontent.com/lachlanchen/lachlanchen/main/figs/donate_wechat.png" width="240"/></td>
    <td style="text-align:center; vertical-align:middle; padding:6px 12px;"><img alt="Alipay QR" src="https://raw.githubusercontent.com/lachlanchen/lachlanchen/main/figs/donate_alipay.png" width="240"/></td>
  </tr>
</table>
</div>

**支援 / Donate**

- ご支援は研究・開発と運用の継続に役立ち、より多くのオープンなプロジェクトを皆さんに届ける力になります。  
- 你的支持将用于研发与运维，帮助我持续公开分享更多项目与改进。  
- Your support sustains my research, development, and ops so I can keep sharing more open projects and improvements.

## License

[Apache-2.0](LICENSE)

## Acknowledgements

LazyEdit uses several open-source libraries and tools including:
- FFmpeg for video processing
- OpenAI models for AI capabilities
- Tornado web framework
- MoviePy for video editing
- CJKWrap for multilingual text processing
