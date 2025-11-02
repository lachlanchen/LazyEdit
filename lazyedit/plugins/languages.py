SUPPORTED_LANGUAGES = [
    {"code": "en", "name": "English", "plugin": "english"},
    {"code": "zh", "name": "Chinese", "plugin": "chinese"},
    {"code": "yue", "name": "Cantonese", "plugin": "cantonese"},
    {"code": "ja", "name": "Japanese", "plugin": "japanese"},
    {"code": "ko", "name": "Korean", "plugin": "korean"},
    {"code": "ar", "name": "Arabic", "plugin": "arabic", "rtl": True},
    {"code": "vi", "name": "Vietnamese", "plugin": "vietnamese"},
    {"code": "fr", "name": "French", "plugin": "french"},
    {"code": "es", "name": "Spanish", "plugin": "spanish"},
]


def list_languages():
    return SUPPORTED_LANGUAGES

