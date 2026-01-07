import json
import os
from typing import Any

from lazyedit.openai_request_json import OpenAIRequestJSONBase


class VideoPromptGenerator(OpenAIRequestJSONBase):
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
        prompt = self._render_prompt_template(
            user_template,
            {
                "PROMPT_SPEC": prompt_spec or "None",
                "IDEA_PROMPT": prompt_spec or "None",
            },
        )
        return self.send_request_with_json_schema(
            prompt=prompt,
            json_schema=json_schema,
            system_content=system_content,
            schema_name=schema_name,
        )

    @staticmethod
    def _render_prompt_template(template: str, values: dict[str, str]) -> str:
        rendered = template
        for key, value in values.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", value)
        return rendered
