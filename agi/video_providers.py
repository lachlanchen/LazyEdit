from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from .video_requests import create_poll_and_download
from .veo_requests import create_veo_video_and_download

SORA_MODELS = {"sora-2", "sora-2-pro"}
VEO_MODELS = {"veo3.1-fast", "veo3.1-pro", "veo3-fast", "veo3-pro"}
ALL_VIDEO_MODELS = SORA_MODELS | VEO_MODELS


def normalize_video_model(model: str | None, default: str = "sora-2") -> str:
    if not model:
        return default
    model = str(model).strip()
    return model if model in ALL_VIDEO_MODELS else default


def is_sora_model(model: str) -> bool:
    return model in SORA_MODELS


@dataclass
class VideoRequest:
    prompt: str
    model: str
    size: str
    seconds: int
    output: str
    reference: Optional[str] = None
    use_cache: bool = True


class VideoProvider(ABC):
    reference_mode: str = "none"

    def __init__(self, model: str):
        self.model = model

    @classmethod
    @abstractmethod
    def supports(cls, model: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def generate(self, request: VideoRequest) -> str:
        raise NotImplementedError


class SoraProvider(VideoProvider):
    reference_mode = "file"

    @classmethod
    def supports(cls, model: str) -> bool:
        return model in SORA_MODELS

    def generate(self, request: VideoRequest) -> str:
        return create_poll_and_download(
            prompt=request.prompt,
            model=request.model,
            size=request.size,
            seconds=request.seconds,
            output=request.output,
            input_reference=request.reference,
            use_cache=request.use_cache,
        )


class VeoProvider(VideoProvider):
    reference_mode = "url"

    @classmethod
    def supports(cls, model: str) -> bool:
        return model in VEO_MODELS

    def generate(self, request: VideoRequest) -> str:
        aspect_ratio = "9:16" if request.size in {"720x1280", "1024x1792"} else "16:9"
        return create_veo_video_and_download(
            prompt=request.prompt,
            model=request.model,
            aspect_ratio=aspect_ratio,
            output=request.output,
            reference_url=request.reference,
            use_cache=request.use_cache,
            size=request.size,
            seconds=request.seconds,
        )


def get_video_provider(model: str) -> VideoProvider:
    if SoraProvider.supports(model):
        return SoraProvider(model)
    if VeoProvider.supports(model):
        return VeoProvider(model)
    return SoraProvider("sora-2")
