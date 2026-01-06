# Repository Guidelines

## Project Structure & Module Organization
- `app.py`: Tornado web app entry; orchestrates the end‑to‑end pipeline.
- `lazyedit/`: Core modules (e.g., `subtitle_translate.py`, `subtitle_metadata.py`, `video_captioner.py`, `utils.py`).
- `DATA/`, `translation_logs/`, `temp/`: Inputs/outputs and logs produced at runtime; avoid committing large media.
- `fonts/`, `weights/`: Rendering assets and model weights.
- `start_lazyedit.sh`, `install_lazyedit.sh`, `lazyedit_config.sh`: Service startup and environment configuration.
 - `furigana` (symlink): External dependency; do not modify in‑repo.
 - `echomind` (symlink): External dependency; do not modify in‑repo.

Note on symlinks: Never edit files inside symlinked directories from this repository. Treat them as read-only, external dependencies used for reference at runtime or for code generation.

## Build, Test, and Development Commands
- Install system deps and generate service/config:
  ```bash
  chmod +x install_lazyedit.sh
  ./install_lazyedit.sh
  ```
- Run locally (development):
  ```bash
  source ~/miniconda3/etc/profile.d/conda.sh
  conda activate lazyedit
  # Always use the conda env's interpreter
  # Do NOT use `python3`; use `python` so it resolves to
  # /home/lachlan/miniconda3/envs/lazyedit/bin/python
  python app.py -m lazyedit
  ```
- Manage background service and tmux session:
  ```bash
  sudo systemctl {start|stop|status} lazyedit.service
  ./start_lazyedit.sh  # starts tmux session "lazyedit"
  ```

## Coding Style & Naming Conventions
- Python 3.10+, PEP 8, 4‑space indentation.
- Filenames/functions: snake_case (e.g., `subtitle_metadata.py`). Classes: CapWords. Constants: UPPER_CASE.
- Keep modules small and cohesive under `lazyedit/`.
- Logging: use existing `print` patterns for consistency; if adding structured logs, prefer Python `logging` (INFO/ERROR) without broad refactors.
- Formatting: no enforced tool; optional `black`/`ruff` is fine—avoid reformatting unrelated files.

## Testing Guidelines
- No formal unit tests yet. Validate changes via the web UI at `http://localhost:8081` using a short sample in `DATA/`.
- If adding tests, use `pytest` with `tests/test_*.py`; keep fixture videos tiny and store under `tests/fixtures/`.
- Prefer deterministic checks (e.g., `.srt` timing, generated cover image existence) over long video diffs.

## Commit & Pull Request Guidelines
- Commit messages: short, imperative, and scoped. Examples:
  - `add preprocessing for Honor videos`
  - `fix ffmpeg 7 compatibility`
- PRs include: purpose + linked issue, repro steps or sample command, before/after notes or screenshots for visual changes, and a checklist: runs locally, no large binaries committed, config/docs updated (`lazyedit_config.sh`, README if needed).

## Security & Configuration Tips
- Never commit API keys or credentials; use environment variables.
- GPU selection: `CUDA_VISIBLE_DEVICES` is set in `app.py`—adjust locally but avoid committing machine‑specific values.
- Large media belongs in `DATA/` or external storage; keep the repository lightweight.
