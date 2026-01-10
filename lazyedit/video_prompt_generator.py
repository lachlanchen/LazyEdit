import json
import os
from typing import Any

from lazyedit.openai_request_json import OpenAIRequestJSONBase


class VideoPromptGenerator(OpenAIRequestJSONBase):
    _AUDIO_LANGUAGE_NAMES = {
        "en": "English",
        "zh": "Chinese",
        "ja": "Japanese",
        "ko": "Korean",
        "vi": "Vietnamese",
        "ar": "Arabic",
        "fr": "French",
        "es": "Spanish",
    }

    def __init__(
        self,
        template_dir: str,
        use_cache: bool = True,
        max_retries: int = 3,
        cache_dir: str = "cache/video_prompts",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        kwargs["use_cache"] = use_cache
        kwargs["max_retries"] = max_retries
        kwargs["cache_dir"] = cache_dir
        super().__init__(*args, **kwargs)
        self.template_dir = template_dir

    def generate(
        self,
        prompt_spec: str,
        schema_name: str = "video_prompt",
    ) -> dict:
        prompt_path = os.path.join(self.template_dir, "prompt.json")
        schema_path = os.path.join(self.template_dir, "schema.json")
        with open(prompt_path, "r", encoding="utf-8") as handle:
            prompt_payload = json.load(handle)
        with open(schema_path, "r", encoding="utf-8") as handle:
            json_schema = json.load(handle)

        system_content = prompt_payload.get("system") or "You are an AI assistant."
        user_template = prompt_payload.get("user") or ""
        prompt_spec_text = prompt_spec if isinstance(prompt_spec, str) else json.dumps(prompt_spec, ensure_ascii=False, indent=2)
        audio_language, audio_language_name = self._extract_audio_language(prompt_spec_text)
        prompt = self._render_prompt_template(
            user_template,
            {
                "PROMPT_SPEC": prompt_spec_text or "None",
                "IDEA_PROMPT": prompt_spec_text or "None",
                "AUDIO_LANGUAGE": audio_language,
                "AUDIO_LANGUAGE_NAME": audio_language_name,
            },
        )
        return self.send_request_with_json_schema(
            prompt=prompt,
            json_schema=json_schema,
            system_content=system_content,
            schema_name=schema_name,
        )

    @staticmethod
    def _extract_audio_language(prompt_spec_text: str) -> tuple[str, str]:
        audio_language = "auto"
        try:
            payload = json.loads(prompt_spec_text)
        except Exception:
            payload = None

        value = None
        if isinstance(payload, dict):
            value = payload.get("audioLanguage") or payload.get("audio_language")
        if isinstance(value, list):
            value = value[0] if value else None
        if isinstance(value, str) and value.strip():
            audio_language = value.strip()

        if audio_language == "auto":
            audio_language_name = "auto (choose the most suitable language)"
        else:
            audio_language_name = VideoPromptGenerator._AUDIO_LANGUAGE_NAMES.get(audio_language, audio_language)
        return audio_language, audio_language_name

    @staticmethod
    def _render_prompt_template(template: str, values: dict[str, str]) -> str:
        rendered = template
        for key, value in values.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", value)
        return rendered
