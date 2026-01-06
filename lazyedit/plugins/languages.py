SUPPORTED_LANGUAGES = [
    {"code": "en", "name": "English", "plugin": "english"},
    {"code": "zh", "name": "Chinese", "plugin": "chinese"},
    {"code": "zh-Hant", "name": "Chinese (Traditional)", "plugin": "chinese_traditional"},
    {"code": "zh-Hans", "name": "Chinese (Simplified)", "plugin": "chinese_simplified"},
    {"code": "yue", "name": "Cantonese", "plugin": "cantonese"},
    {"code": "ja", "name": "Japanese", "plugin": "japanese"},
    {"code": "ko", "name": "Korean", "plugin": "korean"},
    {"code": "ar", "name": "Arabic", "plugin": "arabic", "rtl": True},
    {"code": "vi", "name": "Vietnamese", "plugin": "vietnamese"},
    {"code": "fr", "name": "French", "plugin": "french"},
    {"code": "es", "name": "Spanish", "plugin": "spanish"},
    {"code": "ru", "name": "Russian", "plugin": "russian"},
]


def list_languages():
    return SUPPORTED_LANGUAGES
