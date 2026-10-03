#!/usr/bin/env python
"""Validate public interface dictionaries and copy exact bytes to native assets."""
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
LANGUAGES = ('en', 'zh-Hans', 'zh-Hant', 'ja', 'ko', 'vi', 'ar', 'fr', 'es', 'de', 'ru')


def main():
    source = ROOT / 'studio/locales'
    english = json.loads((source / 'en.json').read_text())
    for language in LANGUAGES:
        file = source / f'{language}.json'
        values = json.loads(file.read_text())
        if set(values) != set(english) or any(not isinstance(v, str) or not v.strip() for v in values.values()):
            raise SystemExit(f'Invalid or incomplete public interface: {language}')
        for destination in (ROOT / 'mobile/ios/App/App/StudioLocales',
                            ROOT / 'mobile/android/app/src/main/assets/studio-locales'):
            destination.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(file, destination / file.name)
    print(f'Validated and synced {len(LANGUAGES)} languages, {len(english)} entries each.')


if __name__ == '__main__':
    main()
