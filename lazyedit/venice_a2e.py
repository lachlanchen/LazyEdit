import hashlib
import json
import os
import re
import time
from datetime import datetime
from typing import Any, Callable, Iterable

import requests


DEFAULT_NEGATIVE_PROMPT = (
    "blurry, low quality, chaotic, deformed, watermark, bad anatomy, shaky camera view point"
)

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
VIDEO_EXTENSIONS = (".mp4", ".mov", ".webm", ".mkv")
AUDIO_EXTENSIONS = (".mp3", ".wav", ".m4a", ".aac", ".ogg")
DEFAULT_TTS_ENDPOINT = "/api/v1/video/send_tts"
DEFAULT_TTS_VOICE_LIST_ENDPOINTS = (
    "/api/v1/tts/most_used",
    "/api/v1/tts/preview/list",
    "/api/v1/anchor/voice_list",
)


def _utc_timestamp() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _coerce_str(value: Any) -> str | None:
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned or None
    if isinstance(value, (int, float)):
        return str(value)
    return None


def _extract_voice_candidates(payload: Any) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    seen: set[tuple[str | None, str | None, str | None, str | None]] = set()

    def consider(item: Any) -> None:
        if not isinstance(item, dict):
            return
        user_voice_id = _coerce_str(item.get("user_voice_id") or item.get("userVoiceId"))
        tts_id = _coerce_str(item.get("tts_id") or item.get("ttsId"))
        voice_id = _coerce_str(
            item.get("voice_id") or item.get("voiceId") or item.get("_id") or item.get("id")
        )
        if not (user_voice_id or tts_id or voice_id):
            return
        name = _coerce_str(
            item.get("name")
            or item.get("voice_name")
            or item.get("voiceName")
            or item.get("title")
            or item.get("label")
        )
        key = (user_voice_id, tts_id, voice_id, name)
        if key in seen:
            return
        seen.add(key)
        candidates.append(
            {
                "user_voice_id": user_voice_id,
                "tts_id": tts_id,
                "voice_id": voice_id,
                "name": name,
            }
        )

    def visit(node: Any) -> None:
        if isinstance(node, list):
            for entry in node:
                visit(entry)
            return
        if isinstance(node, dict):
            consider(node)
            for key in ("data", "list", "rows", "records", "items", "result", "results"):
                if key in node:
                    visit(node[key])
            for value in node.values():
                if isinstance(value, (dict, list)):
                    visit(value)

    visit(payload)
    return candidates


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


def _extract_message(payload: Any) -> str | None:
    if isinstance(payload, dict):
        for key in ("message", "msg", "error", "detail", "description"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        data = payload.get("data")
        if data is not None:
            return _extract_message(data)
    if isinstance(payload, list) and payload:
        return _extract_message(payload[0])
    return None


def _summarize_payload(payload: Any) -> dict[str, Any]:
    if isinstance(payload, dict):
        summary: dict[str, Any] = {"keys": list(payload.keys())[:12]}
        data = payload.get("data")
        if isinstance(data, dict):
            summary["data_keys"] = list(data.keys())[:12]
        return summary
    if isinstance(payload, list):
        summary = {"list_len": len(payload)}
        if payload and isinstance(payload[0], dict):
            summary["first_keys"] = list(payload[0].keys())[:12]
        return summary
    return {"type": type(payload).__name__}


def _extract_progress(payload: Any) -> float | None:
    if isinstance(payload, dict):
        for key in (
            "progress",
            "progress_pct",
            "progressPercent",
            "progress_percent",
            "percentage",
            "percent",
            "pct",
        ):
            value = payload.get(key)
            if isinstance(value, (int, float)):
                pct = float(value)
                if 0 < pct <= 1:
                    pct *= 100
                return pct
            if isinstance(value, str):
                try:
                    pct = float(value.strip().rstrip("%"))
                    if 0 < pct <= 1:
                        pct *= 100
                    return pct
                except ValueError:
                    continue
        data = payload.get("data")
        if data is not None:
            return _extract_progress(data)
    if isinstance(payload, list) and payload:
        return _extract_progress(payload[0])
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


def _progress_logger(
    events: list[dict[str, Any]],
    stage: str,
    label: str,
) -> Callable[[str | None, float | None], None]:
    last_status: str | None = None
    last_progress: float | None = None

    def _log(status: str | None, progress: float | None) -> None:
        nonlocal last_status, last_progress
        if status == last_status and progress == last_progress:
            return
        last_status = status
        last_progress = progress
        details = {}
        if status:
            details["status"] = status
        if progress is not None:
            details["progress"] = round(progress, 1)
        if details:
            message = label + " (" + ", ".join(f"{k}={v}" for k, v in details.items()) + ")"
            _log_event(events, stage, message, details)

    return _log


def _poll_logger(
    events: list[dict[str, Any]],
    stage: str,
    label: str,
    log_every: float | None,
) -> Callable[[str | None, float | None, str | None, int, float], None]:
    last_logged = -1.0

    def _log(
        status: str | None,
        progress: float | None,
        message: str | None,
        attempt: int,
        elapsed: float,
    ) -> None:
        nonlocal last_logged
        if log_every is None or log_every <= 0:
            return
        if last_logged >= 0 and (elapsed - last_logged) < log_every:
            return
        last_logged = elapsed
        details: dict[str, Any] = {"attempt": attempt, "elapsed": round(elapsed, 1)}
        if status:
            details["status"] = status
        if progress is not None:
            details["progress"] = round(progress, 1)
        if message:
            trimmed = message.strip()
            if len(trimmed) > 160:
                trimmed = trimmed[:157] + "..."
            details["message"] = trimmed
        ordered_keys = ("attempt", "elapsed", "status", "progress", "message")
        message_parts = [f"{key}={details[key]}" for key in ordered_keys if key in details]
        message_text = label
        if message_parts:
            message_text += " (" + ", ".join(message_parts) + ")"
        _log_event(events, stage, message_text, details)

    return _log


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


def _format_timeout_message(
    elapsed: float,
    status: str | None,
    progress: float | None,
    message: str | None = None,
) -> str:
    details: list[str] = [f"elapsed={elapsed:.0f}s"]
    if status:
        details.append(f"last_status={status}")
    if progress is not None:
        details.append(f"last_progress={round(progress, 1)}")
    if message:
        details.append(f"last_message={message}")
    return "A2E task timed out (" + ", ".join(details) + ")"


class VenicePromptGenerator:
    def __init__(
        self,
        template_dir: str,
        model: str | None = None,
        use_cache: bool = True,
        cache_dir: str | None = None,
    ) -> None:
        self.template_dir = template_dir
        self.api_base = os.getenv("VENICE_API_BASE", "https://api.venice.ai/api/v1").rstrip("/")
        self.api_key = os.getenv("VENICE_API_KEY", "").strip()
        env_model = os.getenv("VENICE_MODEL", "venice-uncensored").strip() or "venice-uncensored"
        self.model = (model or env_model).strip() or env_model
        self.use_cache = use_cache
        self.cache_dir = cache_dir or os.getenv("VENICE_CACHE_DIR", "cache/venice_prompts")
        self._ensure_dir_exists(self.cache_dir)
        self.timeout = float(os.getenv("VENICE_TIMEOUT_SECONDS", "60"))
        self.chat_endpoint = os.getenv("VENICE_CHAT_ENDPOINT", "/chat/completions")
        if self.api_base.endswith("/api/v1") and self.chat_endpoint.startswith("/v1/"):
            self.chat_endpoint = self.chat_endpoint[len("/v1") :]
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

        cache_path = self._build_cache_path(
            prompt=prompt,
            system_content=system_content,
            schema_payload=schema_payload,
            schema_name="venice_a2e_prompt",
        )
        cached = self._load_cache(cache_path)
        if cached is not None:
            try:
                self._validate_schema(cached, schema_payload)
                print("[V+A2E] venice cache hit.")
                return cached
            except Exception:
                self._safe_remove(cache_path)

        response = self._call_venice(system_content, prompt)
        result = self._extract_json_from_response(response)
        self._validate_schema(result, schema_payload)
        self._save_cache(cache_path, prompt, system_content, result)
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
    def _ensure_dir_exists(path: str) -> None:
        if not os.path.exists(path):
            os.makedirs(path)

    def _build_cache_path(
        self,
        prompt: str,
        system_content: str,
        schema_payload: dict[str, Any],
        schema_name: str,
    ) -> str:
        payload = json.dumps(
            {
                "model": self.model,
                "prompt": prompt,
                "system": system_content,
                "schema": schema_payload,
                "schema_name": schema_name,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        return os.path.join(self.cache_dir, f"{digest}.json")

    def _load_cache(self, cache_path: str) -> dict[str, Any] | None:
        if not self.use_cache or not os.path.exists(cache_path):
            return None
        try:
            with open(cache_path, "r", encoding="utf-8") as handle:
                cached = json.load(handle)
            if not isinstance(cached, dict):
                raise ValueError("Cache payload is not an object")
            response = cached.get("response")
            if not isinstance(response, dict):
                raise ValueError("Cached response is not an object")
            return response
        except (json.JSONDecodeError, ValueError) as exc:
            print(f"[V+A2E] cache invalid ({exc}), ignoring: {cache_path}")
            self._safe_remove(cache_path)
            return None

    def _save_cache(
        self,
        cache_path: str,
        prompt: str,
        system_content: str,
        response: dict[str, Any],
    ) -> None:
        if not self.use_cache:
            return
        payload = {
            "prompt": prompt,
            "system": system_content,
            "model": self.model,
            "response": response,
            "ts": _utc_timestamp(),
        }
        with open(cache_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)

    @staticmethod
    def _safe_remove(path: str) -> None:
        try:
            os.remove(path)
        except Exception:
            pass

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
        self.poll_timeout = self._parse_poll_timeout(os.getenv("A2E_POLL_TIMEOUT_SECONDS", "1800"))
        try:
            self.poll_log_seconds = float(os.getenv("A2E_POLL_LOG_SECONDS", "15"))
        except Exception:
            self.poll_log_seconds = 15.0
        self.poll_log_payload = self._parse_bool_env(os.getenv("A2E_POLL_LOG_PAYLOAD", ""), False)
        self.tts_endpoint = os.getenv("A2E_TTS_ENDPOINT", "").strip() or DEFAULT_TTS_ENDPOINT
        self.tts_status_endpoint = os.getenv("A2E_TTS_STATUS_ENDPOINT", "").strip()
        self.tts_user_voice_id = os.getenv("A2E_TTS_USER_VOICE_ID", "").strip()
        self.tts_id = os.getenv("A2E_TTS_ID", "").strip()
        self.tts_voice_id = os.getenv("A2E_TTS_VOICE_ID", "").strip()
        self.tts_voice_list_endpoints = self._parse_voice_list_endpoints(
            os.getenv("A2E_TTS_VOICE_LIST_ENDPOINTS", "")
        )
        self._tts_voice_cache: tuple[str | None, str | None, str | None] | None = None
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
        self.session.headers.update({"Content-Type": "application/json"})

    @staticmethod
    def _parse_poll_timeout(value: str | None) -> float | None:
        default_timeout = 1800.0
        if value is None:
            return default_timeout
        raw = str(value).strip().lower()
        if raw in {"none", "no", "off", "disable", "disabled", "infinite", "inf"}:
            return None
        try:
            parsed = float(raw)
        except Exception:
            return default_timeout
        if parsed <= 0:
            return None
        return max(parsed, default_timeout)

    @staticmethod
    def _parse_bool_env(value: str | None, default: bool) -> bool:
        if value is None:
            return default
        raw = str(value).strip().lower()
        if raw in {"1", "true", "yes", "y", "on"}:
            return True
        if raw in {"0", "false", "no", "n", "off"}:
            return False
        return default

    @staticmethod
    def _parse_voice_list_endpoints(raw: str) -> tuple[str, ...]:
        if raw:
            endpoints = [entry.strip() for entry in raw.split(",") if entry.strip()]
            return tuple(endpoints)
        return DEFAULT_TTS_VOICE_LIST_ENDPOINTS

    def _resolve_default_tts_voice(self) -> tuple[str | None, str | None, str | None]:
        if self._tts_voice_cache is not None:
            return self._tts_voice_cache
        for endpoint in self.tts_voice_list_endpoints:
            try:
                payload = self._get(endpoint)
            except Exception:
                continue
            candidates = _extract_voice_candidates(payload)
            if not candidates:
                continue
            choice = candidates[0]
            user_voice_id = _coerce_str(choice.get("user_voice_id"))
            tts_id = _coerce_str(choice.get("tts_id"))
            if not user_voice_id and not tts_id:
                tts_id = _coerce_str(choice.get("voice_id"))
            if user_voice_id or tts_id:
                self._tts_voice_cache = (user_voice_id, tts_id, endpoint)
                return user_voice_id, tts_id, endpoint
        self._tts_voice_cache = (None, None, None)
        return None, None, None

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

    def generate_tts(
        self,
        text: str,
        language: str | None = None,
        on_update: Callable[[str | None, float | None], None] | None = None,
        on_poll: Callable[[str | None, float | None, str | None, int, float], None] | None = None,
    ) -> tuple[str, dict[str, Any]]:
        if not self.tts_endpoint:
            raise RuntimeError("A2E_TTS_ENDPOINT is not configured")
        user_voice_id = self.tts_user_voice_id or self.tts_voice_id
        tts_id = self.tts_id
        if not user_voice_id and not tts_id:
            user_voice_id, tts_id, _ = self._resolve_default_tts_voice()
        if not user_voice_id and not tts_id:
            raise RuntimeError(
                "A2E TTS voice not available (set A2E_TTS_USER_VOICE_ID or A2E_TTS_ID)"
            )
        payload: dict[str, Any] = {"text": text, "msg": text}
        if user_voice_id:
            payload["user_voice_id"] = user_voice_id
        if tts_id:
            payload["tts_id"] = tts_id
        if language and language != "auto":
            payload["language"] = language
            payload["lang"] = language
        response = self._post(self.tts_endpoint, payload)
        audio_url = _find_first_url(response, AUDIO_EXTENSIONS)
        if audio_url:
            if on_update:
                on_update("ready", 100)
            return audio_url, response
        task_id = _extract_task_id(response)
        if not task_id:
            raise RuntimeError("A2E TTS did not return audio or task id")
        if not self.tts_status_endpoint:
            raise RuntimeError("A2E_TTS_STATUS_ENDPOINT is not configured for async TTS")
        audio_url = self.wait_for_media_url(
            self.tts_status_endpoint.format(task_id=task_id),
            AUDIO_EXTENSIONS,
            on_update=on_update,
            on_poll=on_poll,
        )
        return audio_url, response

    def wait_for_media_url(
        self,
        endpoint: str,
        extensions: Iterable[str],
        on_update: Callable[[str | None, float | None], None] | None = None,
        on_poll: Callable[[str | None, float | None, str | None, int, float], None] | None = None,
    ) -> str:
        last_status: str | None = None
        last_progress: float | None = None
        last_message: str | None = None
        start = time.time()
        deadline = None if self.poll_timeout is None else start + self.poll_timeout
        attempt = 0
        last_payload_log = -1.0
        while True:
            attempt += 1
            response = self._get(endpoint)
            if self.poll_log_payload:
                elapsed = time.time() - start
                if last_payload_log < 0 or elapsed - last_payload_log >= (self.poll_log_seconds or 0):
                    last_payload_log = elapsed
                    summary = _summarize_payload(response)
                    print(f"[V+A2E] poll payload: {summary}")
            url = _find_first_url(response, extensions)
            if url:
                return url
            status = _extract_status(response)
            progress = _extract_progress(response)
            message = _extract_message(response)
            if on_update and (status != last_status or progress != last_progress):
                on_update(status, progress)
                last_status, last_progress = status, progress
            if message:
                last_message = message
            if on_poll:
                on_poll(status, progress, message, attempt, time.time() - start)
            if status in {"failed", "error", "canceled"}:
                detail = f"status={status}"
                if message:
                    detail += f", message={message}"
                raise RuntimeError(f"A2E task failed ({detail})")
            if deadline is not None and time.time() >= deadline:
                elapsed = time.time() - start
                raise TimeoutError(_format_timeout_message(elapsed, last_status, last_progress, last_message))
            time.sleep(self.poll_interval)

    def wait_for_task(
        self,
        endpoint: str,
        extensions: Iterable[str],
        on_update: Callable[[str | None, float | None], None] | None = None,
        on_poll: Callable[[str | None, float | None, str | None, int, float], None] | None = None,
    ) -> tuple[str, dict[str, Any]]:
        last_status: str | None = None
        last_progress: float | None = None
        last_message: str | None = None
        start = time.time()
        deadline = None if self.poll_timeout is None else start + self.poll_timeout
        attempt = 0
        last_payload_log = -1.0
        while True:
            attempt += 1
            response = self._get(endpoint)
            if self.poll_log_payload:
                elapsed = time.time() - start
                if last_payload_log < 0 or elapsed - last_payload_log >= (self.poll_log_seconds or 0):
                    last_payload_log = elapsed
                    summary = _summarize_payload(response)
                    print(f"[V+A2E] poll payload: {summary}")
            url = _find_first_url(response, extensions)
            if url:
                return url, response
            status = _extract_status(response)
            progress = _extract_progress(response)
            message = _extract_message(response)
            if on_update and (status != last_status or progress != last_progress):
                on_update(status, progress)
                last_status, last_progress = status, progress
            if message:
                last_message = message
            if on_poll:
                on_poll(status, progress, message, attempt, time.time() - start)
            if status in {"failed", "error", "canceled"}:
                detail = f"status={status}"
                if message:
                    detail += f", message={message}"
                raise RuntimeError(f"A2E task failed ({detail})")
            if deadline is not None and time.time() >= deadline:
                elapsed = time.time() - start
                raise TimeoutError(_format_timeout_message(elapsed, last_status, last_progress, last_message))
            time.sleep(self.poll_interval)

    def _post(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.api_base}{endpoint}"
        response = self.session.post(url, json=payload, timeout=self.timeout)
        if not response.ok:
            raise RuntimeError(f"A2E request failed ({response.status_code}): {response.text}")
        return response.json()

    def _get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.api_base}{endpoint}"
        response = self.session.get(url, params=params, timeout=self.timeout)
        if not response.ok:
            raise RuntimeError(f"A2E request failed ({response.status_code}): {response.text}")
        return response.json()


def run_venice_a2e_image(
    template_dir: str,
    idea: str,
    venice_model: str | None = None,
    use_cache: bool = True,
    image_prompt: str | None = None,
    audio_language: str | None = None,
    aspect_ratio: str | None = None,
    width: int | None = None,
    height: int | None = None,
    events: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if events is None:
        events = []
    prompts: dict[str, Any] = {}
    if not width or not height:
        width, height = _ratio_to_dimensions(aspect_ratio or "9:16")

    _log_event(events, "start", "Starting Venice + A2E image step.")

    title = ""
    if not image_prompt:
        if not idea:
            raise RuntimeError("idea is required when image_prompt is missing")
        _log_event(events, "venice", "Generating prompts with Venice.")
        generator = VenicePromptGenerator(
            template_dir=template_dir,
            model=venice_model,
            use_cache=use_cache,
            cache_dir="cache/venice_prompts",
        )
        prompts = generator.generate(idea=idea, audio_language=audio_language)
        title = str(prompts.get("title") or "").strip()
        image_prompt = prompts.get("image_prompt", "").strip()
    else:
        prompts = {"image_prompt": image_prompt}

    if not image_prompt:
        raise RuntimeError("Missing image prompt after Venice generation")

    _log_event(events, "venice", "Image prompt ready.", {"image_prompt": image_prompt})

    client = A2EClient()
    if not client.api_key:
        raise RuntimeError("A2E_API_KEY is not configured")

    _log_event(events, "a2e_image", "Requesting image generation.")
    image_task_id, image_task_payload = client.create_text_to_image(image_prompt, width, height)
    _log_event(events, "a2e_image", "Image task queued.", {"task_id": image_task_id})
    _log_event(events, "a2e_image", "Polling image status.")
    image_url, image_detail = client.wait_for_task(
        f"/api/v1/userText2Image/{image_task_id}",
        IMAGE_EXTENSIONS,
        on_update=_progress_logger(events, "a2e_image", "Image progress"),
        on_poll=_poll_logger(events, "a2e_image", "Image polling", client.poll_log_seconds),
    )
    _log_event(events, "a2e_image", "Image ready.", {"image_url": image_url})

    return {
        "idea": idea,
        "title": title or None,
        "prompts": prompts,
        "image_prompt": image_prompt,
        "image_url": image_url,
        "events": events,
        "debug": {
            "image_task": image_task_payload,
            "image_detail": image_detail,
        },
    }


def run_venice_a2e_video(
    template_dir: str,
    idea: str,
    image_url: str,
    venice_model: str | None = None,
    use_cache: bool = True,
    video_prompt: str | None = None,
    audio_language: str | None = None,
    video_time: int | None = None,
    negative_prompt: str | None = None,
    events: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if events is None:
        events = []
    prompts: dict[str, Any] = {}
    if not video_time:
        video_time = 10
    negative_prompt = negative_prompt or DEFAULT_NEGATIVE_PROMPT

    _log_event(events, "start", "Starting Venice + A2E video step.")

    if not image_url:
        raise RuntimeError("image_url is required to generate video")

    title = ""
    if not video_prompt:
        if not idea:
            raise RuntimeError("idea is required when video_prompt is missing")
        _log_event(events, "venice", "Generating prompts with Venice.")
        generator = VenicePromptGenerator(
            template_dir=template_dir,
            model=venice_model,
            use_cache=use_cache,
            cache_dir="cache/venice_prompts",
        )
        prompts = generator.generate(idea=idea, audio_language=audio_language)
        title = str(prompts.get("title") or "").strip()
        video_prompt = prompts.get("video_prompt", "").strip()
    else:
        prompts = {"video_prompt": video_prompt}

    if not video_prompt:
        raise RuntimeError("Missing video prompt after Venice generation")

    _log_event(events, "venice", "Video prompt ready.", {"video_prompt": video_prompt})

    client = A2EClient()
    if not client.api_key:
        raise RuntimeError("A2E_API_KEY is not configured")

    _log_event(events, "a2e_video", "Requesting image-to-video.")
    video_task_id, video_task_payload = client.create_image_to_video(
        image_url=image_url,
        prompt=video_prompt,
        video_time=int(video_time),
        negative_prompt=negative_prompt,
    )
    _log_event(events, "a2e_video", "Video task queued.", {"task_id": video_task_id})
    _log_event(events, "a2e_video", "Polling video status.")
    video_url, video_detail = client.wait_for_task(
        f"/api/v1/userImage2Video/{video_task_id}",
        VIDEO_EXTENSIONS,
        on_update=_progress_logger(events, "a2e_video", "Video progress"),
        on_poll=_poll_logger(events, "a2e_video", "Video polling", client.poll_log_seconds),
    )
    _log_event(events, "a2e_video", "Video ready.", {"video_url": video_url})

    return {
        "idea": idea,
        "title": title or None,
        "prompts": prompts,
        "image_url": image_url,
        "video_prompt": video_prompt,
        "video_url": video_url,
        "events": events,
        "debug": {
            "video_task": video_task_payload,
            "video_detail": video_detail,
        },
    }


def run_venice_a2e_audio(
    template_dir: str,
    idea: str,
    video_url: str,
    venice_model: str | None = None,
    use_cache: bool = True,
    audio_text: str | None = None,
    audio_url: str | None = None,
    video_prompt: str | None = None,
    audio_language: str | None = None,
    video_time: int | None = None,
    negative_prompt: str | None = None,
    events: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if events is None:
        events = []
    prompts: dict[str, Any] = {}
    if not video_time:
        video_time = 10
    negative_prompt = negative_prompt or DEFAULT_NEGATIVE_PROMPT

    _log_event(events, "start", "Starting Venice + A2E audio step.")

    if not video_url:
        raise RuntimeError("video_url is required to generate audio")

    title = ""
    need_audio_text = not audio_url
    if (need_audio_text and not audio_text) or not video_prompt:
        if not idea:
            if not video_prompt:
                video_prompt = "Sync the lips to the provided audio."
            if need_audio_text and not audio_text:
                raise RuntimeError("idea is required when audio_text is missing")
        else:
            _log_event(events, "venice", "Generating prompts with Venice.")
            generator = VenicePromptGenerator(
                template_dir=template_dir,
                model=venice_model,
                use_cache=use_cache,
                cache_dir="cache/venice_prompts",
            )
            prompts = generator.generate(idea=idea, audio_language=audio_language)
            title = str(prompts.get("title") or "").strip()
            if need_audio_text and not audio_text:
                audio_text = prompts.get("audio_text", "").strip()
            if not video_prompt:
                video_prompt = prompts.get("video_prompt", "").strip()
    else:
        prompts = {"audio_text": audio_text, "video_prompt": video_prompt}

    if need_audio_text and not audio_text:
        raise RuntimeError("Missing audio text after Venice generation")

    if not video_prompt:
        video_prompt = "Sync the lips to the provided audio."

    prompt_meta = {"audio_text": audio_text} if audio_text else None
    _log_event(events, "venice", "Audio prompt ready.", prompt_meta)

    client = A2EClient()
    if not client.api_key:
        raise RuntimeError("A2E_API_KEY is not configured")

    audio_detail: dict[str, Any] | None = None
    if audio_url:
        _log_event(events, "a2e_audio", "Using provided audio URL.", {"audio_url": audio_url})
        audio_detail = {"audio_url": audio_url, "source": "provided"}
    else:
        _log_event(events, "a2e_audio", "Generating audio (TTS).")
        audio_url, audio_detail = client.generate_tts(
            audio_text,
            language=audio_language,
            on_update=_progress_logger(events, "a2e_audio", "TTS progress"),
            on_poll=_poll_logger(events, "a2e_audio", "TTS polling", client.poll_log_seconds),
        )
        _log_event(events, "a2e_audio", "Audio ready.", {"audio_url": audio_url})

    _log_event(events, "a2e_talking", "Requesting talking video.")
    talking_task_id, talking_task_payload = client.create_talking_video(
        video_url=video_url,
        audio_url=audio_url,
        prompt=video_prompt,
        negative_prompt=negative_prompt,
        duration=int(video_time),
    )
    _log_event(events, "a2e_talking", "Talking video task queued.", {"task_id": talking_task_id})
    _log_event(events, "a2e_talking", "Polling talking video status.")
    talking_video_url, talking_detail = client.wait_for_task(
        f"/api/v1/talkingVideo/{talking_task_id}",
        VIDEO_EXTENSIONS,
        on_update=_progress_logger(events, "a2e_talking", "Talking video progress"),
        on_poll=_poll_logger(events, "a2e_talking", "Talking video polling", client.poll_log_seconds),
    )
    _log_event(events, "a2e_talking", "Talking video ready.", {"video_url": talking_video_url})

    return {
        "idea": idea,
        "title": title or None,
        "prompts": prompts,
        "video_url": video_url,
        "audio_text": audio_text,
        "audio_url": audio_url,
        "talking_video_url": talking_video_url,
        "events": events,
        "debug": {
            "audio_detail": audio_detail,
            "talking_task": talking_task_payload,
            "talking_detail": talking_detail,
        },
    }


def run_venice_a2e_pipeline(
    template_dir: str,
    idea: str,
    venice_model: str | None = None,
    use_cache: bool = True,
    image_prompt: str | None = None,
    video_prompt: str | None = None,
    audio_text: str | None = None,
    audio_language: str | None = None,
    aspect_ratio: str | None = None,
    video_time: int | None = None,
    width: int | None = None,
    height: int | None = None,
    negative_prompt: str | None = None,
    events: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if events is None:
        events = []
    prompts: dict[str, Any] = {}
    if not video_time:
        video_time = 10
    if not width or not height:
        width, height = _ratio_to_dimensions(aspect_ratio or "9:16")
    negative_prompt = negative_prompt or DEFAULT_NEGATIVE_PROMPT

    _log_event(events, "start", "Starting Venice + A2E pipeline.")

    title = ""
    if not image_prompt or not video_prompt or not audio_text:
        _log_event(events, "venice", "Generating prompts with Venice.")
        generator = VenicePromptGenerator(
            template_dir=template_dir,
            model=venice_model,
            use_cache=use_cache,
            cache_dir="cache/venice_prompts",
        )
        prompts = generator.generate(idea=idea, audio_language=audio_language)
        title = str(prompts.get("title") or "").strip()
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
    _log_event(events, "a2e_image", "Polling image status.")
    image_url, image_detail = client.wait_for_task(
        f"/api/v1/userText2Image/{image_task_id}",
        IMAGE_EXTENSIONS,
        on_update=_progress_logger(events, "a2e_image", "Image progress"),
        on_poll=_poll_logger(events, "a2e_image", "Image polling", client.poll_log_seconds),
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
    _log_event(events, "a2e_video", "Polling video status.")
    video_url, video_detail = client.wait_for_task(
        f"/api/v1/userImage2Video/{video_task_id}",
        VIDEO_EXTENSIONS,
        on_update=_progress_logger(events, "a2e_video", "Video progress"),
        on_poll=_poll_logger(events, "a2e_video", "Video polling", client.poll_log_seconds),
    )
    _log_event(events, "a2e_video", "Video ready.", {"video_url": video_url})

    _log_event(events, "a2e_audio", "Generating audio (TTS).")
    audio_url, audio_detail = client.generate_tts(
        audio_text,
        language=audio_language,
        on_update=_progress_logger(events, "a2e_audio", "TTS progress"),
        on_poll=_poll_logger(events, "a2e_audio", "TTS polling", client.poll_log_seconds),
    )
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
    _log_event(events, "a2e_talking", "Polling talking video status.")
    talking_video_url, talking_detail = client.wait_for_task(
        f"/api/v1/talkingVideo/{talking_task_id}",
        VIDEO_EXTENSIONS,
        on_update=_progress_logger(events, "a2e_talking", "Talking video progress"),
        on_poll=_poll_logger(events, "a2e_talking", "Talking video polling", client.poll_log_seconds),
    )
    _log_event(events, "a2e_talking", "Talking video ready.", {"video_url": talking_video_url})

    return {
        "idea": idea,
        "title": title or None,
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
