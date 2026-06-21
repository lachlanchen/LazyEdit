import json

from lazyedit.subtitles_burner.burner import _load_burner_module


def test_speaker_only_tokens_keep_caption_text(tmp_path):
    _load_burner_module()
    import subtitles_burner.burner as burner_mod

    payload = [
        {
            "start": "00:00:00,000",
            "end": "00:00:02,000",
            "ja": "写真大丈夫?",
            "ruby": "写真[しゃしん]大丈夫[だいじょうぶ]?",
            "tokens": [{"text": "🔊", "type": "speaker"}],
        }
    ]
    subtitle_json = tmp_path / "ja_speaker_only.json"
    subtitle_json.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    segments = burner_mod.load_segments_from_json(
        str(subtitle_json),
        text_key="ja",
        ruby_key="ruby",
        auto_ruby=True,
        strip_kana=True,
        kana_romaji=True,
    )

    assert len(segments) == 1
    rendered_text = "".join(token.text for token in segments[0].tokens)
    assert "🔊" in rendered_text
    assert "写真" in rendered_text
