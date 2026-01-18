import json
import os
import re
import time
from datetime import datetime
from typing import Any, Iterable

import requests


DEFAULT_NEGATIVE_PROMPT = (
    "blurry, low quality, chaotic, deformed, watermark, bad anatomy, shaky camera view point"
)

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
VIDEO_EXTENSIONS = (".mp4", ".mov", ".webm", ".mkv")
AUDIO_EXTENSIONS = (".mp3", ".wav", ".m4a", ".aac", ".ogg")


def _utc_timestamp() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _render_prompt(template: str, values: dict[str, str]) -> str:
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered


def _strip_code_fences(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()
    return cleaned


def _parse_json_from_text(text: str) -> dict[str, Any]:
    if not text:
        raise ValueError("Empty response content")
    cleaned = _strip_code_fences(text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or start >= end:
            raise
        return json.loads(cleaned[start : end + 1])


def _find_first_url(payload: Any, extensions: Iterable[str]) -> str | None:
    if isinstance(payload, str):
        value = payload.strip()
        lower_value = value.lower()
        if lower_value.startswith("http") and lower_value.split("?")[0].endswith(tuple(extensions)):
            return value
        return None
    if isinstance(payload, dict):
        for key in (
            "image_url",
            "imageUrl",
            "video_url",
            "videoUrl",
            "audio_url",
            "audioUrl",
            "file_url",
            "fileUrl",
            "url",
            "result_url",
            "resultUrl",
            "output_url",
            "outputUrl",
        ):
            if key in payload and isinstance(payload[key], str):
                candidate = _find_first_url(payload[key], extensions)
                if candidate:
                    return candidate
        for value in payload.values():
            candidate = _find_first_url(value, extensions)
            if candidate:
                return candidate
    if isinstance(payload, list):
        for value in payload:
            candidate = _find_first_url(value, extensions)
            if candidate:
                return candidate
    return None


def _extract_status(payload: Any) -> str | None:
    if isinstance(payload, dict):
        for key in ("status", "state", "task_status", "taskStatus"):
            value = payload.get(key)
            if isinstance(value, str):
                return value.lower()
        data = payload.get("data")
        if data is not None:
            return _extract_status(data)
    if isinstance(payload, list) and payload:
        return _extract_status(payload[0])
    return None


def _extract_task_id(payload: Any) -> str | None:
    if isinstance(payload, dict):
        for key in ("_id", "id", "task_id", "taskId"):
            value = payload.get(key)
            if isinstance(value, str):
                return value
            if isinstance(value, (int, float)):
                return str(value)
        data = payload.get("data")
        if data is not None:
            return _extract_task_id(data)
    if isinstance(payload, list) and payload:
        return _extract_task_id(payload[0])
    return None


def _log_event(events: list[dict[str, Any]], stage: str, message: str, data: dict[str, Any] | None = None) -> None:
    entry = {"ts": _utc_timestamp(), "stage": stage, "message": message}
    if data:
        entry["data"] = data
    events.append(entry)
    print(f"[V+A2E] {stage}: {message}")


def _ratio_to_dimensions(aspect_ratio: str) -> tuple[int, int]:
    ratio = (aspect_ratio or "9:16").strip()
    mapping = {
        "9:16": (768, 1344),
        "16:9": (1344, 768),
        "1:1": (1024, 1024),
        "4:3": (1024, 768),
        "3:4": (768, 1024),
    }
    return mapping.get(ratio, (768, 1344))


class VenicePromptGenerator:
    def __init__(self, template_dir: str) -> None:
        self.template_dir = template_dir
        self.api_base = os.getenv("VENICE_API_BASE", "https://api.venice.ai").rstrip("/")
        self.api_key = os.getenv("VENICE_API_KEY", "").strip()
        self.model = os.getenv("VENICE_MODEL", "venice-2.0").strip() or "venice-2.0"
        self.timeout = float(os.getenv("VENICE_TIMEOUT_SECONDS", "60"))
        self.chat_endpoint = os.getenv("VENICE_CHAT_ENDPOINT", "/v1/chat/completions")
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
        self.session.headers.update({"Content-Type": "application/json"})

    def generate(self, idea: str, audio_language: str | None = None) -> dict[str, Any]:
        if not self.api_key:
            raise RuntimeError("VENICE_API_KEY is not configured")
        prompt_path = os.path.join(self.template_dir, "prompt.json")
        schema_path = os.path.join(self.template_dir, "schema.json")
        with open(prompt_path, "r", encoding="utf-8") as handle:
            prompt_payload = json.load(handle)
        with open(schema_path, "r", encoding="utf-8") as handle:
            schema_payload = json.load(handle)

        system_content = prompt_payload.get("system") or "You are an AI assistant."
        user_template = prompt_payload.get("user") or ""
        prompt = _render_prompt(
            user_template,
            {
                "IDEA_PROMPT": idea or "Create a cinematic video prompt.",
                "AUDIO_LANGUAGE": audio_language or "auto",
            },
        )

        response = self._call_venice(system_content, prompt)
        result = self._extract_json_from_response(response)
        self._validate_schema(result, schema_payload)
        return result

    def _call_venice(self, system_content: str, prompt: str) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.6,
        }
        url = f"{self.api_base}{self.chat_endpoint}"
        response = self.session.post(url, json=payload, timeout=self.timeout)
        if not response.ok:
            raise RuntimeError(f"Venice request failed ({response.status_code}): {response.text}")
        return response.json()

    @staticmethod
    def _extract_json_from_response(payload: dict[str, Any]) -> dict[str, Any]:
        content = None
        if isinstance(payload, dict):
            choices = payload.get("choices")
            if isinstance(choices, list) and choices:
                message = choices[0].get("message") if isinstance(choices[0], dict) else None
                if isinstance(message, dict):
                    content = message.get("content")
        if isinstance(content, str):
            return _parse_json_from_text(content)
        return payload if isinstance(payload, dict) else {}

    @staticmethod
    def _validate_schema(result: dict[str, Any], schema: dict[str, Any]) -> None:
        required = schema.get("required", [])
        if not isinstance(result, dict):
            raise ValueError("Prompt result is not a JSON object")
        missing = [key for key in required if key not in result]
        if missing:
            raise ValueError(f"Prompt result missing required keys: {missing}")


class A2EClient:
    def __init__(self) -> None:
        self.api_base = os.getenv("A2E_API_BASE", "https://video.a2e.ai").rstrip("/")
        self.api_key = os.getenv("A2E_API_KEY", "").strip()
        self.timeout = float(os.getenv("A2E_TIMEOUT_SECONDS", "60"))
        self.poll_interval = float(os.getenv("A2E_POLL_INTERVAL_SECONDS", "3"))
        self.poll_timeout = float(os.getenv("A2E_POLL_TIMEOUT_SECONDS", "240"))
        self.tts_endpoint = os.getenv("A2E_TTS_ENDPOINT", "").strip()
        self.tts_status_endpoint = os.getenv("A2E_TTS_STATUS_ENDPOINT", "").strip()
        self.tts_voice_id = os.getenv("A2E_TTS_VOICE_ID", "").strip()
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
        self.session.headers.update({"Content-Type": "application/json"})

    def create_text_to_image(self, prompt: str, width: int, height: int) -> tuple[str, dict[str, Any]]:
        payload = {
            "name": f"venice_a2e_image_{_utc_timestamp()}",
            "prompt": prompt,
            "width": width,
            "height": height,
            "model_type": "a2e",
        }
        response = self._post("/api/v1/userText2Image/start", payload)
        task_id = _extract_task_id(response)
        if not task_id:
            raise RuntimeError("A2E text-to-image did not return a task id")
        return task_id, response

    def create_image_to_video(
        self,
        image_url: str,
        prompt: str,
        video_time: int,
        negative_prompt: str,
    ) -> tuple[str, dict[str, Any]]:
        payload = {
            "name": f"venice_a2e_video_{_utc_timestamp()}",
            "model_type": "GENERAL",
            "image_url": image_url,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "video_time": int(video_time),
            "extend_prompt": True,
            "skip_face_enhance": False,
        }
        response = self._post("/api/v1/userImage2Video/start", payload)
        task_id = _extract_task_id(response)
        if not task_id:
            raise RuntimeError("A2E image-to-video did not return a task id")
        return task_id, response

    def create_talking_video(
        self,
        video_url: str,
        audio_url: str,
        prompt: str,
        negative_prompt: str,
        duration: int,
    ) -> tuple[str, dict[str, Any]]:
        payload = {
            "name": f"venice_a2e_talking_{_utc_timestamp()}",
            "video_url": video_url,
            "audio_url": audio_url,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "duration": int(duration),
        }
        response = self._post("/api/v1/talkingVideo/start", payload)
        task_id = _extract_task_id(response)
        if not task_id:
            raise RuntimeError("A2E talking video did not return a task id")
        return task_id, response

    def generate_tts(self, text: str, language: str | None = None) -> tuple[str, dict[str, Any]]:
        if not self.tts_endpoint:
            raise RuntimeError("A2E_TTS_ENDPOINT is not configured")
        payload: dict[str, Any] = {"text": text}
        if self.tts_voice_id:
            payload["voice_id"] = self.tts_voice_id
        if language and language != "auto":
            payload["language"] = language
        response = self._post(self.tts_endpoint, payload)
        audio_url = _find_first_url(response, AUDIO_EXTENSIONS)
        if audio_url:
            return audio_url, response
        task_id = _extract_task_id(response)
        if not task_id:
            raise RuntimeError("A2E TTS did not return audio or task id")
        if not self.tts_status_endpoint:
            raise RuntimeError("A2E_TTS_STATUS_ENDPOINT is not configured for async TTS")
        audio_url = self.wait_for_media_url(
            self.tts_status_endpoint.format(task_id=task_id),
            AUDIO_EXTENSIONS,
        )
        return audio_url, response

    def wait_for_media_url(self, endpoint: str, extensions: Iterable[str]) -> str:
        deadline = time.time() + self.poll_timeout
        while time.time() < deadline:
            response = self._get(endpoint)
            url = _find_first_url(response, extensions)
            if url:
                return url
            status = _extract_status(response)
            if status in {"failed", "error", "canceled"}:
                raise RuntimeError(f"A2E task failed with status={status}")
            time.sleep(self.poll_interval)
        raise TimeoutError("A2E task timed out")

    def wait_for_task(self, endpoint: str, extensions: Iterable[str]) -> tuple[str, dict[str, Any]]:
        deadline = time.time() + self.poll_timeout
        while time.time() < deadline:
            response = self._get(endpoint)
            url = _find_first_url(response, extensions)
            if url:
                return url, response
            status = _extract_status(response)
            if status in {"failed", "error", "canceled"}:
                raise RuntimeError(f"A2E task failed with status={status}")
            time.sleep(self.poll_interval)
        raise TimeoutError("A2E task timed out")

    def _post(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.api_base}{endpoint}"
        response = self.session.post(url, json=payload, timeout=self.timeout)
        if not response.ok:
            raise RuntimeError(f"A2E request failed ({response.status_code}): {response.text}")
        return response.json()

    def _get(self, endpoint: str) -> dict[str, Any]:
        url = f"{self.api_base}{endpoint}"
        response = self.session.get(url, timeout=self.timeout)
        if not response.ok:
            raise RuntimeError(f"A2E request failed ({response.status_code}): {response.text}")
        return response.json()


def run_venice_a2e_pipeline(
    template_dir: str,
    idea: str,
    image_prompt: str | None = None,
    video_prompt: str | None = None,
    audio_text: str | None = None,
    audio_language: str | None = None,
    aspect_ratio: str | None = None,
    video_time: int | None = None,
    width: int | None = None,
    height: int | None = None,
    negative_prompt: str | None = None,
) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    prompts: dict[str, Any] = {}
    if not video_time:
        video_time = 10
    if not width or not height:
        width, height = _ratio_to_dimensions(aspect_ratio or "9:16")
    negative_prompt = negative_prompt or DEFAULT_NEGATIVE_PROMPT

    _log_event(events, "start", "Starting Venice + A2E pipeline.")

    if not image_prompt or not video_prompt or not audio_text:
        _log_event(events, "venice", "Generating prompts with Venice.")
        generator = VenicePromptGenerator(template_dir=template_dir)
        prompts = generator.generate(idea=idea, audio_language=audio_language)
        image_prompt = prompts.get("image_prompt", "").strip()
        video_prompt = prompts.get("video_prompt", "").strip()
        audio_text = prompts.get("audio_text", "").strip()
    else:
        prompts = {
            "image_prompt": image_prompt,
            "video_prompt": video_prompt,
            "audio_text": audio_text,
        }

    if not image_prompt or not video_prompt or not audio_text:
        raise RuntimeError("Missing prompts after Venice generation")

    _log_event(events, "venice", "Prompts ready.", {"image_prompt": image_prompt, "video_prompt": video_prompt})

    client = A2EClient()
    if not client.api_key:
        raise RuntimeError("A2E_API_KEY is not configured")

    _log_event(events, "a2e_image", "Requesting image generation.")
    image_task_id, image_task_payload = client.create_text_to_image(image_prompt, width, height)
    _log_event(events, "a2e_image", "Image task queued.", {"task_id": image_task_id})
    image_url, image_detail = client.wait_for_task(
        f"/api/v1/userText2Image/{image_task_id}",
        IMAGE_EXTENSIONS,
    )
    _log_event(events, "a2e_image", "Image ready.", {"image_url": image_url})

    _log_event(events, "a2e_video", "Requesting image-to-video.")
    video_task_id, _ = client.create_image_to_video(
        image_url=image_url,
        prompt=video_prompt,
        video_time=int(video_time),
        negative_prompt=negative_prompt,
    )
    _log_event(events, "a2e_video", "Video task queued.", {"task_id": video_task_id})
    video_url, video_detail = client.wait_for_task(
        f"/api/v1/userImage2Video/{video_task_id}",
        VIDEO_EXTENSIONS,
    )
    _log_event(events, "a2e_video", "Video ready.", {"video_url": video_url})

    _log_event(events, "a2e_audio", "Generating audio (TTS).")
    audio_url, audio_detail = client.generate_tts(audio_text, language=audio_language)
    _log_event(events, "a2e_audio", "Audio ready.", {"audio_url": audio_url})

    _log_event(events, "a2e_talking", "Requesting talking video.")
    talking_task_id, _ = client.create_talking_video(
        video_url=video_url,
        audio_url=audio_url,
        prompt=video_prompt,
        negative_prompt=negative_prompt,
        duration=int(video_time),
    )
    _log_event(events, "a2e_talking", "Talking video task queued.", {"task_id": talking_task_id})
    talking_video_url, talking_detail = client.wait_for_task(
        f"/api/v1/talkingVideo/{talking_task_id}",
        VIDEO_EXTENSIONS,
    )
    _log_event(events, "a2e_talking", "Talking video ready.", {"video_url": talking_video_url})

    return {
        "idea": idea,
        "prompts": prompts,
        "image_prompt": image_prompt,
        "video_prompt": video_prompt,
        "audio_text": audio_text,
        "image_url": image_url,
        "video_url": video_url,
        "audio_url": audio_url,
        "talking_video_url": talking_video_url,
        "events": events,
        "debug": {
            "image_task": image_task_payload,
            "image_detail": image_detail,
            "video_detail": video_detail,
            "audio_detail": audio_detail,
            "talking_detail": talking_detail,
        },
    }
