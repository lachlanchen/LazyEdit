"""Exercise the real metadata worker without starting the application/services."""

import ast
from contextlib import contextmanager
import json
import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest


def run_metadata_worker(tmp_path, *, status="empty", notes="", speech="", caption=""):
    tree = ast.parse((Path(__file__).resolve().parents[1] / "app.py").read_text())
    handler = next(n for n in tree.body if isinstance(n, ast.ClassDef)
                   and n.name == "VideoMetadataHandler")
    post = next(n for n in handler.body if n.name == "post")
    worker = next(n for n in post.body if isinstance(n, ast.FunctionDef)
                  and n.name == "_run")
    source = str(tmp_path / "cat.mov")
    cursor = Mock()
    cursor.fetchone.return_value = (source, "cat")

    @contextmanager
    def get_cursor():
        yield cursor

    database = SimpleNamespace(
        ensure_schema=Mock(), get_cursor=get_cursor,
        get_latest_frame_caption=Mock(return_value=(
            (1, "completed", None, None, "caption", None, None) if caption else None
        )),
        add_video_metadata=Mock(return_value=42),
    )
    generator = Mock()
    generator.generate_metadata_from_template.return_value = {"title": "Cat loaf"}
    placeholder = Mock(return_value={"title": "placeholder"})
    env = dict(
        os=os, json=json, ldb=database, video_id_i=657, lang="en",
        use_polished=True, use_cache=False, publication_session_id=None,
        custom_notes=notes, METADATA_TEMPLATE_DIR=str(tmp_path), METADATA_TEMPLATE_MAP={},
        Subtitle2Metadata=Mock(return_value=generator),
        _ensure_local_video_path=lambda *args: (source, None),
        preprocess_if_needed=lambda path: path,
        _ensure_global_polished_subtitles=Mock(),
        _get_latest_global_transcription=lambda *args: (
            1, "polished", status, "speech.json", "speech.srt", "speech.md", None, None
        ),
        _read_text_file=lambda path: caption if path == "caption" else speech,
        _publication_session_dir=lambda folder, *args, **kwargs: folder,
        _metadata_openai_client=Mock(), _build_placeholder_metadata=placeholder,
        _sanitize_title=lambda title: title, media_url_for_path=lambda path: path,
    )
    exec(compile(ast.Module(body=[worker], type_ignores=[]), "app.py", "exec"), env)
    return env["_run"](), generator, placeholder


@pytest.mark.parametrize("status", ["empty", "no_audio", "completed"])
def test_context_generates_metadata_without_speech(tmp_path, status):
    result, generator, placeholder = run_metadata_worker(
        tmp_path, status=status, notes="A cat in 香箱座り pose."
    )
    assert result[0] == 200
    assert result[1]["metadata"]["title"] == "Cat loaf"
    args = generator.generate_metadata_from_template.call_args.kwargs
    assert args["transcription_text"] == ""
    assert args["custom_notes"] == "A cat in 香箱座り pose."
    placeholder.assert_not_called()


@pytest.mark.parametrize("notes", ["", " \n\t"])
def test_no_context_or_speech_keeps_placeholder(tmp_path, notes):
    result, generator, placeholder = run_metadata_worker(tmp_path, notes=notes)
    assert result[1]["metadata"]["title"] == "placeholder"
    generator.generate_metadata_from_template.assert_not_called()
    placeholder.assert_called_once()


@pytest.mark.parametrize("speech,caption", [("Hello, cat.", ""), ("", "Cat on a bench.")])
def test_speech_and_visual_caption_fallback_still_work(tmp_path, speech, caption):
    result, generator, placeholder = run_metadata_worker(
        tmp_path, status="completed", speech=speech, caption=caption
    )
    assert result[0] == 200
    assert generator.generate_metadata_from_template.call_args.kwargs["transcription_text"] == (speech or caption)
    placeholder.assert_not_called()
