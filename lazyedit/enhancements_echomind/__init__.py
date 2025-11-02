"""Enhancement modules for EchoMind.

This package groups language enhancement utilities and a lightweight
plugin system for High Cohesion, Low Coupling (HCLC).
"""

from .japanese_enhancement import (
    LanguageEnhancer,
    FuriganaWord,
    GrammaticalType,
    GrammaticalColorScheme,
    enhance_message_with_language,
    format_furigana_for_display,
)

from .english_enhancement import (
    EnglishLanguageEnhancer,
    EnglishWord,
    EnglishGrammaticalType,
    EnglishGrammaticalColorScheme,
    enhance_message_with_english,
    format_english_for_display,
)

# Plugin base + registry
from .base import EnhancementResult, EnhancementPlugin
from . import registry
from .cantonese_enhancement import get_plugin as get_cantonese_plugin
from .chinese_enhancement import get_plugin as get_chinese_plugin
from .korean_enhancement import get_plugin as get_korean_plugin

# Register built-in plugins
try:
    registry.register(get_cantonese_plugin())
except Exception:
    # Plugin registration should never crash import
    pass
try:
    registry.register(get_chinese_plugin())
except Exception:
    pass
try:
    registry.register(get_korean_plugin())
except Exception:
    pass

__all__ = [
    # Japanese
    "LanguageEnhancer",
    "FuriganaWord",
    "GrammaticalType",
    "GrammaticalColorScheme",
    "enhance_message_with_language",
    "format_furigana_for_display",
    # English
    "EnglishLanguageEnhancer",
    "EnglishWord",
    "EnglishGrammaticalType",
    "EnglishGrammaticalColorScheme",
    "enhance_message_with_english",
    "format_english_for_display",
    # Plugin system
    "EnhancementResult",
    "EnhancementPlugin",
    "registry",
]
