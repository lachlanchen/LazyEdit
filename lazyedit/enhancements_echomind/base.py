#!/usr/bin/env python3
"""
Enhancement plugin base types for EchoMind.
Encourages High Cohesion, Low Coupling (HCLC):
- Each plugin is responsible for text enhancement only.
- TTS generation stays outside (handled by voice layer).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any, Protocol


@dataclass
class EnhancementResult:
    """Standard result from a language enhancement plugin."""
    original_text: str
    processed_text: str
    display_html: Optional[str]
    tts_language_code: str
    processing_time: float
    meta: Dict[str, Any]
    error: Optional[str] = None


class EnhancementPlugin(Protocol):
    """Minimal plugin interface for enhancements."""
    key: str  # e.g., "cantonese"

    def enhance(self, text: str, source_language: Optional[str] = None) -> EnhancementResult:
        ...

