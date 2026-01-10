#!/usr/bin/env python3
"""Simple registry for enhancement plugins."""

from typing import Dict, Type, Optional

from .base import EnhancementPlugin


_registry: Dict[str, EnhancementPlugin] = {}


def register(plugin: EnhancementPlugin) -> None:
    _registry[plugin.key] = plugin


def get(name: str) -> Optional[EnhancementPlugin]:
    return _registry.get(name)


def available() -> Dict[str, EnhancementPlugin]:
    return dict(_registry)

