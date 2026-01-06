# Arabic Prompts

## Source: `echomind/cachexxx/arabic_enhancement_cache/7607452516502444189.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: good night",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/4575270050233326066.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: good night",
  "response": {
    "mode": "x_to_ar",
    "text": "ليلة سعيدة",
    "tokens": [
      {
        "word": "ليلة",
        "pos": "noun",
        "gloss": "night",
        "pronunciation": "laila"
      },
      {
        "word": "سعيدة",
        "pos": "adjective",
        "gloss": "good",
        "pronunciation": "sa'idah"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/873640085736514658.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: zh\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: 你还想跟我聊天吗?",
  "response": {
    "mode": "x_to_ar",
    "text": "هل ترغب في الدردشة معي؟",
    "tokens": [
      {
        "word": "هل",
        "pos": "particle",
        "gloss": "interrogative particle",
        "pronunciation": "hal"
      },
      {
        "word": "ترغب",
        "pos": "verb",
        "gloss": "to desire",
        "pronunciation": "targab"
      },
      {
        "word": "في",
        "pos": "preposition",
        "gloss": "in",
        "pronunciation": "fi"
      },
      {
        "word": "الدردشة",
        "pos": "noun",
        "gloss": "chat",
        "pronunciation": "al-dardasha"
      },
      {
        "word": "معي",
        "pos": "pronoun",
        "gloss": "with me",
        "pronunciation": "ma'i"
      },
      {
        "word": "؟",
        "pos": "punct",
        "gloss": "question mark",
        "pronunciation": "?"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/5980401787634237393.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: I added korean.",
  "response": {
    "language_code": "ko"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/4434723378748941482.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: hello",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/8801297141341497422.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: auto\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: good night",
  "response": {
    "mode": "x_to_ar",
    "text": "تصبح على خير",
    "tokens": [
      {
        "word": "تصبح",
        "pos": "verb",
        "gloss": "good night (you become)",
        "pronunciation": "taṣbiḥ"
      },
      {
        "word": "على",
        "pos": "preposition",
        "gloss": "on",
        "pronunciation": "ʿalā"
      },
      {
        "word": "خير",
        "pos": "noun",
        "gloss": "goodness",
        "pronunciation": "khayr"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/2752662266842498608.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: zh\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: 說一點中文",
  "response": {
    "mode": "x_to_ar",
    "text": "تحدث قليلاً بالعربية",
    "tokens": [
      {
        "word": "تحدث",
        "pos": "verb",
        "gloss": "speak",
        "pronunciation": "taḥaddaθ"
      },
      {
        "word": "قليلاً",
        "pos": "adverb",
        "gloss": "a little",
        "pronunciation": "qaliilan"
      },
      {
        "word": "باللغة",
        "pos": "preposition",
        "gloss": "in the language",
        "pronunciation": "bil-luɣati"
      },
      {
        "word": "العربية",
        "pos": "noun",
        "gloss": "Arabic",
        "pronunciation": "al-‘arabiyyah"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/4971908372816009707.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: How about I say a very long sentecne? Can you do the same thing for me?",
  "response": {
    "mode": "x_to_ar",
    "text": "ماذا عن أن أقول جملةً طويلة جداً؟ هل يمكنك فعل الشيء نفسه من أجلي؟",
    "tokens": [
      {
        "word": "ماذا",
        "pos": "pronoun",
        "gloss": "what",
        "pronunciation": "ma-dha"
      },
      {
        "word": "عن",
        "pos": "preposition",
        "gloss": "about",
        "pronunciation": "ʿan"
      },
      {
        "word": "أن",
        "pos": "particle",
        "gloss": "to",
        "pronunciation": "an"
      },
      {
        "word": "أقول",
        "pos": "verb",
        "gloss": "I say",
        "pronunciation": "a-qu-l"
      },
      {
        "word": "جملةً",
        "pos": "noun",
        "gloss": "sentence",
        "pronunciation": "jum-laً"
      },
      {
        "word": "طويلةً",
        "pos": "adjective",
        "gloss": "long",
        "pronunciation": "ṭawi-lah"
      },
      {
        "word": "جداً",
        "pos": "adverb",
        "gloss": "very",
        "pronunciation": "jid-dan"
      },
      {
        "word": "؟",
        "pos": "punct",
        "gloss": "?",
        "pronunciation": "؟"
      },
      {
        "word": "هل",
        "pos": "particle",
        "gloss": "can",
        "pronunciation": "hal"
      },
      {
        "word": "يمكنك",
        "pos": "verb",
        "gloss": "you can",
        "pronunciation": "yun-ki-k"
      },
      {
        "word": "فعل",
        "pos": "verb",
        "gloss": "do",
        "pronunciation": "fa-ʿal"
      },
      {
        "word": "الشيء",
        "pos": "noun",
        "gloss": "thing",
        "pronunciation": "ash-shayء"
      },
      {
        "word": "نفسه",
        "pos": "pronoun",
        "gloss": "the same",
        "pronunciation": "nafs-uh"
      },
      {
        "word": "من",
        "pos": "preposition",
        "gloss": "for",
        "pronunciation": "min"
      },
      {
        "word": "أجلي",
        "pos": "noun",
        "gloss": "me",
        "pronunciation": "a-jal-i"
      },
      {
        "word": "؟",
        "pos": "punct",
        "gloss": "?",
        "pronunciation": "؟"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/7400052807071491365.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: hello",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/1209948160054083855.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: hello",
  "response": {
    "mode": "x_to_ar",
    "text": "مرحبا",
    "tokens": [
      {
        "word": "مرحبا",
        "pos": "interjection",
        "gloss": "hello",
        "pronunciation": "marhaban"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/4545103915678085501.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: hello",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/9074037639362914657.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: What will happen if we push new thing?",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/2377142785337268356.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: hello arabic",
  "response": {
    "language_code": "ar"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/4986388823331492235.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: auto\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: hello arabic",
  "response": {
    "mode": "x_to_ar",
    "text": "مرحبا بالعربية",
    "tokens": [
      {
        "word": "مرحبا",
        "pos": "interjection",
        "gloss": "hello",
        "pronunciation": "marhaban"
      },
      {
        "word": "بالعربية",
        "pos": "preposition",
        "gloss": "in Arabic",
        "pronunciation": "bil-‘arabiyya"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/2709633047690555011.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: I want to post something to delete.",
  "response": {
    "mode": "x_to_ar",
    "text": "أريد أن أنشر شيئًا للحذف.",
    "tokens": [
      {
        "word": "أريد",
        "pos": "verb",
        "gloss": "I want",
        "pronunciation": "urid"
      },
      {
        "word": "أن",
        "pos": "particle",
        "gloss": "to",
        "pronunciation": "an"
      },
      {
        "word": "أنشر",
        "pos": "verb",
        "gloss": "post",
        "pronunciation": "anshur"
      },
      {
        "word": "شيئًا",
        "pos": "noun",
        "gloss": "something",
        "pronunciation": "shay'an"
      },
      {
        "word": "للحذف",
        "pos": "preposition",
        "gloss": "to delete",
        "pronunciation": "lil-hadhf"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/7574939262594281350.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: Can you show korean?",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/8183507483677333538.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: auto\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: what do you think",
  "response": {
    "mode": "x_to_ar",
    "text": "ماذا تعتقد؟",
    "tokens": [
      {
        "word": "ماذا",
        "pos": "pronoun",
        "gloss": "what",
        "pronunciation": "madha"
      },
      {
        "word": "تعتقد",
        "pos": "verb",
        "gloss": "you think",
        "pronunciation": "ta'taqid"
      },
      {
        "word": "؟",
        "pos": "punct",
        "gloss": "?",
        "pronunciation": ""
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/3945852987739652966.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: good night",
  "response": {
    "mode": "x_to_ar",
    "text": "تصبح على خير",
    "tokens": [
      {
        "word": "تصبح",
        "pos": "verb",
        "gloss": "good (to become)",
        "pronunciation": "taṣbiḥ"
      },
      {
        "word": "على",
        "pos": "preposition",
        "gloss": "on",
        "pronunciation": "ʿalā"
      },
      {
        "word": "خير",
        "pos": "noun",
        "gloss": "goodness",
        "pronunciation": "khayr"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/1229614842956385433.json`

```json
{
  "prompt": "If the text: \"can i post?\" is not Arabic, translate it into natural Arabic (Arabic script) first.\nIf it's already Arabic, polish it to correct and native Arabic (Arabic script).\n\nAnalyze this Arabic text into words.\n\nReturn JSON with:\n- arabic_text: native and exact Arabic translation or polished original Arabic (Arabic script only)\n- words: array of objects:\n  - word: the word/particle/punctuation as it appears in arabic_text (Arabic script for Arabic words)\n  - type: grammatical type from this enum: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, measure, classifier, particle, auxiliary, determiner, interjection, punctuation, other\n  - pronunciation: Arabic-to-Latin romanization for the ENTIRE word (empty string for non-Arabic words)\n\nRequirements:\n- Keep arabic_text strictly in Arabic script.\n- Segment precisely; keep punctuation as separate words.\n- Provide pronunciation for Arabic words; leave empty for non-Arabic tokens.\n- Be consistent; no empty items.\n- Output strict JSON only.\n",
  "response": {
    "arabic_text": "هل يمكنني النشر؟",
    "words": [
      {
        "word": "هل",
        "type": "particle",
        "pronunciation": "hal"
      },
      {
        "word": "يمكنني",
        "type": "verb",
        "pronunciation": "yumkinuni"
      },
      {
        "word": "النشر",
        "type": "noun",
        "pronunciation": "al-nashr"
      },
      {
        "word": "؟",
        "type": "punctuation",
        "pronunciation": ""
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/6057349551907119724.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: hello",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/2363120143626996101.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: good night",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/5251687588135223463.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: hello",
  "response": {
    "mode": "x_to_ar",
    "text": "مرحبا",
    "tokens": [
      {
        "word": "مرحبا",
        "pos": "interjection",
        "gloss": "hello",
        "pronunciation": "marhaban"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/281091525508644147.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: hello",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/8138767292468101427.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: now can you use arabic?",
  "response": {
    "language_code": "ar"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/2360055498190756771.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: good night",
  "response": {
    "mode": "x_to_ar",
    "text": "ليلة سعيدة",
    "tokens": [
      {
        "word": "ليلة",
        "pos": "noun",
        "gloss": "night",
        "pronunciation": "laylah"
      },
      {
        "word": "سعيدة",
        "pos": "adjective",
        "gloss": "good",
        "pronunciation": "sa'idah"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/4279012475345192476.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: good night",
  "response": {
    "mode": "x_to_ar",
    "text": "تصبح على خير",
    "tokens": [
      {
        "word": "تصبح",
        "pos": "verb",
        "gloss": "you become",
        "pronunciation": "taṣbiḥ"
      },
      {
        "word": "على",
        "pos": "preposition",
        "gloss": "on",
        "pronunciation": "ʿalā"
      },
      {
        "word": "خير",
        "pos": "noun",
        "gloss": "good",
        "pronunciation": "khayr"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/1961435092486664898.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: zh\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: I forwarded this post. 非非非非你还在吗没有没有我先我先那个啥",
  "response": {
    "mode": "x_to_ar",
    "text": "لقد أرسلت هذه المشاركة.",
    "tokens": [
      {
        "word": "لقد",
        "pos": "particle",
        "gloss": "I have",
        "pronunciation": "laqad"
      },
      {
        "word": "أرسلت",
        "pos": "verb",
        "gloss": "forwarded",
        "pronunciation": "arsalt"
      },
      {
        "word": "هذه",
        "pos": "determiner",
        "gloss": "this",
        "pronunciation": "hadhihi"
      },
      {
        "word": "المشاركة",
        "pos": "noun",
        "gloss": "post",
        "pronunciation": "al-musharaka"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/4378527295165180664.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: good morning",
  "response": {
    "mode": "x_to_ar",
    "text": "صباح الخير",
    "tokens": [
      {
        "word": "صباح",
        "pos": "noun",
        "gloss": "morning",
        "pronunciation": "sabah"
      },
      {
        "word": "الخير",
        "pos": "noun",
        "gloss": "goodness",
        "pronunciation": "alkhayr"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/8991410728435045950.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: what do you think",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/1878095305715039141.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: Wow, it's great. おはようございます",
  "response": {
    "language_code": "ja"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/674990164740400880.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: I added vietnamese.",
  "response": {
    "language_code": "vi"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/3768457872217477090.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: I forwarded this post. 非非非非你还在吗没有没有我先我先那个啥",
  "response": {
    "language_code": "zh"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/6011424952337059998.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: good morning",
  "response": {
    "mode": "x_to_ar",
    "text": "صباح الخير",
    "tokens": [
      {
        "word": "صباح",
        "pos": "noun",
        "gloss": "morning",
        "pronunciation": "sabah"
      },
      {
        "word": "الخير",
        "pos": "noun",
        "gloss": "goodness",
        "pronunciation": "al-khayr"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/450271481252442910.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: hello",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/8055672232927056814.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: zh\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: 你还想跟我聊天吗?",
  "response": {
    "mode": "x_to_ar",
    "text": "هل تريد الدردشة معي؟",
    "tokens": [
      {
        "word": "هل",
        "pos": "particle",
        "gloss": "interrogative particle",
        "pronunciation": "hal"
      },
      {
        "word": "تريد",
        "pos": "verb",
        "gloss": "to want",
        "pronunciation": "turid"
      },
      {
        "word": "الدردشة",
        "pos": "noun",
        "gloss": "chatting",
        "pronunciation": "al-dardasha"
      },
      {
        "word": "معي",
        "pos": "pronoun",
        "gloss": "with me",
        "pronunciation": "ma'i"
      },
      {
        "word": "؟",
        "pos": "punct",
        "gloss": "question mark",
        "pronunciation": ""
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/4042983488590083403.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: auto\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: be a good man",
  "response": {
    "mode": "x_to_ar",
    "text": "كن إنسانًا جيدًا",
    "tokens": [
      {
        "word": "كن",
        "pos": "verb",
        "gloss": "be",
        "pronunciation": "kun"
      },
      {
        "word": "إنسانًا",
        "pos": "noun",
        "gloss": "man",
        "pronunciation": "insāna"
      },
      {
        "word": "جيدًا",
        "pos": "adjective",
        "gloss": "good",
        "pronunciation": "jayyidan"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/2739620818028088457.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: hello",
  "response": {
    "mode": "x_to_ar",
    "text": "مرحبا",
    "tokens": [
      {
        "word": "مرحبا",
        "pos": "interjection",
        "gloss": "hello",
        "pronunciation": "marhaba"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/8241560367016823732.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: ja\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: Wow, it's great. おはようございます",
  "response": {
    "mode": "x_to_ar",
    "text": "واو، إنه رائع.",
    "tokens": [
      {
        "word": "واو",
        "pos": "interjection",
        "gloss": "Wow",
        "pronunciation": "wāw"
      },
      {
        "word": "إنه",
        "pos": "pronoun",
        "gloss": "it is",
        "pronunciation": "innahu"
      },
      {
        "word": "رائع",
        "pos": "adjective",
        "gloss": "great",
        "pronunciation": "rā'ī"
      },
      {
        "word": ".",
        "pos": "punct",
        "gloss": "period",
        "pronunciation": ". "
      },
      {
        "word": "صباح",
        "pos": "noun",
        "gloss": "morning",
        "pronunciation": "ṣabāḥ"
      },
      {
        "word": "الخير",
        "pos": "noun",
        "gloss": "good",
        "pronunciation": "alkhayr"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/7354346977219237894.json`

```json
{
  "prompt": "If the text: \"Hello\" is not Arabic, translate it into natural Arabic (Arabic script) first.\nIf it's already Arabic, polish it to correct and native Arabic (Arabic script).\n\nAnalyze this Arabic text into words.\n\nReturn JSON with:\n- arabic_text: native and exact Arabic translation or polished original Arabic (Arabic script only)\n- words: array of objects:\n  - word: the word/particle/punctuation as it appears in arabic_text (Arabic script for Arabic words)\n  - type: grammatical type from this enum: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, measure, classifier, particle, auxiliary, determiner, interjection, punctuation, other\n  - pronunciation: Arabic-to-Latin romanization for the ENTIRE word (empty string for non-Arabic words)\n\nRequirements:\n- Keep arabic_text strictly in Arabic script.\n- Segment precisely; keep punctuation as separate words.\n- Provide pronunciation for Arabic words; leave empty for non-Arabic tokens.\n- Be consistent; no empty items.\n- Output strict JSON only.\n",
  "response": {
    "arabic_text": "مرحباً",
    "words": [
      {
        "word": "مرحباً",
        "type": "interjection",
        "pronunciation": "marhaban"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/5677158475207478479.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: hello",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/2015306751425190108.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: Let me post something",
  "response": {
    "mode": "x_to_ar",
    "text": "دعني أنشر شيئًا",
    "tokens": [
      {
        "word": "دعني",
        "pos": "verb",
        "gloss": "let me",
        "pronunciation": "da'ni"
      },
      {
        "word": "أنشر",
        "pos": "verb",
        "gloss": "post",
        "pronunciation": "anshur"
      },
      {
        "word": "شيئًا",
        "pos": "noun",
        "gloss": "something",
        "pronunciation": "shay'an"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/2349194156452089368.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: what do you think?",
  "response": {
    "mode": "x_to_ar",
    "text": "ماذا تعتقد؟",
    "tokens": [
      {
        "word": "ماذا",
        "pos": "pronoun",
        "gloss": "what",
        "pronunciation": "máðā"
      },
      {
        "word": "تعتقد",
        "pos": "verb",
        "gloss": "do you think",
        "pronunciation": "taʕtāqid"
      },
      {
        "word": "؟",
        "pos": "punct",
        "gloss": "?",
        "pronunciation": ""
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/1929983222591959411.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: good night",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/8180704786058860475.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: ko\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: 감사합니다.",
  "response": {
    "mode": "x_to_ar",
    "text": "شكرًا جزيلاً.",
    "tokens": [
      {
        "word": "شكرًا",
        "pos": "noun",
        "gloss": "thank you",
        "pronunciation": "shukran"
      },
      {
        "word": "جزيلاً",
        "pos": "adjective",
        "gloss": "greatly",
        "pronunciation": "jazeelan"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/4765481898682042386.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: How about I say a very long sentecne? Can you do the same thing for me?",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/8001871004082981449.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: auto\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: @lachlan Owner",
  "response": {
    "mode": "x_to_ar",
    "text": "@لاكلان مالك",
    "tokens": [
      {
        "word": "@لاكلان",
        "pos": "proper_noun",
        "gloss": "@Lachlan",
        "pronunciation": "@lakaːlan"
      },
      {
        "word": "مالك",
        "pos": "noun",
        "gloss": "owner",
        "pronunciation": "maːlik"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/5043317215966842446.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: do you have color?",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/5517474721643655072.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: hello",
  "response": {
    "mode": "x_to_ar",
    "text": "مرحبا",
    "tokens": [
      {
        "word": "مرحبا",
        "pos": "interjection",
        "gloss": "hello",
        "pronunciation": "marhaban"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/5527030909186571473.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: good morning",
  "response": {
    "mode": "x_to_ar",
    "text": "صباح الخير",
    "tokens": [
      {
        "word": "صباح",
        "pos": "noun",
        "gloss": "morning",
        "pronunciation": "sabah"
      },
      {
        "word": "الخير",
        "pos": "noun",
        "gloss": "goodness",
        "pronunciation": "alkhayr"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/2034108926164260394.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: hello",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/1387475933984642347.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: What will happen if we push new thing?",
  "response": {
    "mode": "x_to_ar",
    "text": "ماذا سيحدث إذا دفعنا شيئًا جديدًا؟",
    "tokens": [
      {
        "word": "ماذا",
        "pos": "pronoun",
        "gloss": "what",
        "pronunciation": "maadha"
      },
      {
        "word": "سيحدث",
        "pos": "verb",
        "gloss": "will happen",
        "pronunciation": "sayahduth"
      },
      {
        "word": "إذا",
        "pos": "conjunction",
        "gloss": "if",
        "pronunciation": "itha"
      },
      {
        "word": "دفعنا",
        "pos": "verb",
        "gloss": "we push",
        "pronunciation": "dafana"
      },
      {
        "word": "شيئًا",
        "pos": "noun",
        "gloss": "thing",
        "pronunciation": "shay'an"
      },
      {
        "word": "جديدًا",
        "pos": "adjective",
        "gloss": "new",
        "pronunciation": "jadeedan"
      },
      {
        "word": "؟",
        "pos": "punct",
        "gloss": "?",
        "pronunciation": ""
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/8414063893122194015.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: zh\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: 吃一个好飞飞吗",
  "response": {
    "mode": "x_to_ar",
    "text": "هل تريد أن تأكل طائرة جيدة؟",
    "tokens": [
      {
        "word": "هل",
        "pos": "particle",
        "gloss": "interrogative particle",
        "pronunciation": "hal"
      },
      {
        "word": "تريد",
        "pos": "verb",
        "gloss": "you want",
        "pronunciation": "turid"
      },
      {
        "word": "أن",
        "pos": "particle",
        "gloss": "to",
        "pronunciation": "an"
      },
      {
        "word": "تأكل",
        "pos": "verb",
        "gloss": "eat",
        "pronunciation": "ta'kul"
      },
      {
        "word": "طائرة",
        "pos": "noun",
        "gloss": "airplane",
        "pronunciation": "ta'ira"
      },
      {
        "word": "جيدة",
        "pos": "adjective",
        "gloss": "good",
        "pronunciation": "jayyida"
      },
      {
        "word": "؟",
        "pos": "punct",
        "gloss": "question mark",
        "pronunciation": ""
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/4989942255867562088.json`

```json
{
  "prompt": "If the text: \"Auto coin test content\" is not Arabic, translate it into natural Arabic (Arabic script) first.\nIf it's already Arabic, polish it to correct and native Arabic (Arabic script).\n\nAnalyze this Arabic text into words.\n\nReturn JSON with:\n- arabic_text: native and exact Arabic translation or polished original Arabic (Arabic script only)\n- words: array of objects:\n  - word: the word/particle/punctuation as it appears in arabic_text (Arabic script for Arabic words)\n  - type: grammatical type from this enum: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, measure, classifier, particle, auxiliary, determiner, interjection, punctuation, other\n  - pronunciation: Arabic-to-Latin romanization for the ENTIRE word (empty string for non-Arabic words)\n\nRequirements:\n- Keep arabic_text strictly in Arabic script.\n- Segment precisely; keep punctuation as separate words.\n- Provide pronunciation for Arabic words; leave empty for non-Arabic tokens.\n- Be consistent; no empty items.\n- Output strict JSON only.\n",
  "response": {
    "arabic_text": "اختبار العملة الآلية محتوى",
    "words": [
      {
        "word": "اختبار",
        "type": "noun",
        "pronunciation": "ikhtibār"
      },
      {
        "word": "العملة",
        "type": "noun",
        "pronunciation": "al-ʿumla"
      },
      {
        "word": "الآلية",
        "type": "adjective",
        "pronunciation": "al-āliyya"
      },
      {
        "word": "محتوى",
        "type": "noun",
        "pronunciation": "muḥtawā"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/8413820361210279143.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: do you have color?",
  "response": {
    "mode": "x_to_ar",
    "text": "هل لديك لون؟",
    "tokens": [
      {
        "word": "هل",
        "pos": "particle",
        "gloss": "interrogative particle",
        "pronunciation": "hal"
      },
      {
        "word": "لديك",
        "pos": "pronoun",
        "gloss": "you have",
        "pronunciation": "ladayk"
      },
      {
        "word": "لون",
        "pos": "noun",
        "gloss": "color",
        "pronunciation": "lawn"
      },
      {
        "word": "؟",
        "pos": "punct",
        "gloss": "question mark",
        "pronunciation": "?"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/3714032078430211338.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: do you know arabic?",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/3885465645666286093.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: all_zh\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: 当然想聊！你想聊些什么呢？",
  "response": {
    "mode": "x_to_ar",
    "text": "بالطبع أود أن أتحدث! ماذا تريد أن تتحدث عنه؟",
    "tokens": [
      {
        "word": "بالطبع",
        "pos": "adverb",
        "gloss": "of course",
        "pronunciation": "bil-tab'a"
      },
      {
        "word": "أود",
        "pos": "verb",
        "gloss": "I would like",
        "pronunciation": "awad"
      },
      {
        "word": "أن",
        "pos": "particle",
        "gloss": "to",
        "pronunciation": "an"
      },
      {
        "word": "أتحدث",
        "pos": "verb",
        "gloss": "I talk",
        "pronunciation": "atahadath"
      },
      {
        "word": "ماذا",
        "pos": "pronoun",
        "gloss": "what",
        "pronunciation": "madha"
      },
      {
        "word": "تريد",
        "pos": "verb",
        "gloss": "you want",
        "pronunciation": "turid"
      },
      {
        "word": "أن",
        "pos": "particle",
        "gloss": "to",
        "pronunciation": "an"
      },
      {
        "word": "تتحدث",
        "pos": "verb",
        "gloss": "you talk",
        "pronunciation": "tatahadath"
      },
      {
        "word": "عنه",
        "pos": "preposition",
        "gloss": "about him",
        "pronunciation": "anhu"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/5638878750310851977.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: hello",
  "response": {
    "mode": "x_to_ar",
    "text": "مرحبا",
    "tokens": [
      {
        "word": "مرحبا",
        "pos": "interjection",
        "gloss": "hello",
        "pronunciation": "marhaban"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/8760555807190322754.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: good night",
  "response": {
    "mode": "x_to_ar",
    "text": "تصبح على خير",
    "tokens": [
      {
        "word": "تصبح",
        "pos": "verb",
        "gloss": "good (you) become",
        "pronunciation": "taṣbiḥ"
      },
      {
        "word": "على",
        "pos": "preposition",
        "gloss": "on",
        "pronunciation": "ʿalā"
      },
      {
        "word": "خير",
        "pos": "noun",
        "gloss": "goodness",
        "pronunciation": "khayr"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/3350269676617327219.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: ko\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: I added korean.",
  "response": {
    "mode": "x_to_ar",
    "text": "أضفت الكورية.",
    "tokens": [
      {
        "word": "أضفت",
        "pos": "verb",
        "gloss": "I added",
        "pronunciation": "'aḍaf-tu"
      },
      {
        "word": "الكورية",
        "pos": "proper_noun",
        "gloss": "the Korean (language)",
        "pronunciation": "al-kūriyya"
      },
      {
        "word": ".",
        "pos": "punct",
        "gloss": "period",
        "pronunciation": ""
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/4553447426105308749.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: is this work?",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/4425928604397107403.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: 說一點中文",
  "response": {
    "language_code": "zh"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/5990923192589262029.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: hello",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/7140067631461692386.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: do you still have color?",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/9113873698623596688.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: hello",
  "response": {
    "mode": "x_to_ar",
    "text": "مرحبا",
    "tokens": [
      {
        "word": "مرحبا",
        "pos": "interjection",
        "gloss": "hello",
        "pronunciation": "marhaban"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/9085420282852312445.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: all_zh\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: 当然想聊！你想聊些什么呢？",
  "response": {
    "mode": "x_to_ar",
    "text": "بالطبع أريد الدردشة! ماذا تريد أن تتحدث عنه؟",
    "tokens": [
      {
        "word": "بالطبع",
        "pos": "adverb",
        "gloss": "of course",
        "pronunciation": "bilṭabʿ"
      },
      {
        "word": "أريد",
        "pos": "verb",
        "gloss": "I want",
        "pronunciation": "urīdu"
      },
      {
        "word": "الدردشة",
        "pos": "noun",
        "gloss": "the chat",
        "pronunciation": "aldardasha"
      },
      {
        "word": "ماذا",
        "pos": "pronoun",
        "gloss": "what",
        "pronunciation": "mādhā"
      },
      {
        "word": "تريد",
        "pos": "verb",
        "gloss": "you want",
        "pronunciation": "turīdu"
      },
      {
        "word": "أن",
        "pos": "particle",
        "gloss": "to",
        "pronunciation": "an"
      },
      {
        "word": "تتحدث",
        "pos": "verb",
        "gloss": "talk",
        "pronunciation": "tataḥaddathu"
      },
      {
        "word": "عنه",
        "pos": "pronoun",
        "gloss": "about it",
        "pronunciation": "ʿanhu"
      },
      {
        "word": "؟",
        "pos": "punct",
        "gloss": "question mark",
        "pronunciation": ""
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/852770325965309340.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: can you talk?",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/3815161269139380997.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: hello",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/4900318790787089795.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: Is this vietnamese?",
  "response": {
    "language_code": "vi"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/2445105277893212941.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: good morning",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/8425875097009395042.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: are you a man",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/7369105110640215221.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: what do you think",
  "response": {
    "mode": "x_to_ar",
    "text": "ماذا تعتقد؟",
    "tokens": [
      {
        "word": "ماذا",
        "pos": "pronoun",
        "gloss": "what",
        "pronunciation": "maadha"
      },
      {
        "word": "تعتقد",
        "pos": "verb",
        "gloss": "do you think",
        "pronunciation": "ta'taqid"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/2792839678554253928.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: good night",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/944248853090350887.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: good morning",
  "response": {
    "mode": "x_to_ar",
    "text": "صباح الخير",
    "tokens": [
      {
        "word": "صباح",
        "pos": "noun",
        "gloss": "morning",
        "pronunciation": "sabaaḥ"
      },
      {
        "word": "الخير",
        "pos": "noun",
        "gloss": "goodness",
        "pronunciation": "al-khayr"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/715327742082269899.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: helo",
  "response": {
    "mode": "x_to_ar",
    "text": "مرحبا",
    "tokens": [
      {
        "word": "مرحبا",
        "pos": "interjection",
        "gloss": "hello",
        "pronunciation": "marhaba"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/3105756100093408047.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: auto\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: @indigopurple",
  "response": {
    "mode": "x_to_ar",
    "text": "نيلي أرجواني",
    "tokens": [
      {
        "word": "نيلي",
        "pos": "adjective",
        "gloss": "indigo",
        "pronunciation": "niːli"
      },
      {
        "word": "أرجواني",
        "pos": "adjective",
        "gloss": "purple",
        "pronunciation": "arjuːani"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/2926499096922289268.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: what do you think?",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/4538429492896913485.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: Let me post something",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/5817985155000927058.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: good morning",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/7692657774812972052.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: be a good man",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/2443168192029843703.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: hello",
  "response": {
    "mode": "x_to_ar",
    "text": "مرحبا",
    "tokens": [
      {
        "word": "مرحبا",
        "pos": "interjection",
        "gloss": "hello",
        "pronunciation": "marhaba"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/7362094278214387657.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: ko\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: 감사합니다.",
  "response": {
    "mode": "x_to_ar",
    "text": "شكرًا لك.",
    "tokens": [
      {
        "word": "شكرًا",
        "pos": "noun",
        "gloss": "thanks",
        "pronunciation": "shukran"
      },
      {
        "word": "لك",
        "pos": "pronoun",
        "gloss": "to you",
        "pronunciation": "lak"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/1512675236204262288.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: good night",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/6751939232804352514.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: hello",
  "response": {
    "mode": "x_to_ar",
    "text": "مرحبًا",
    "tokens": [
      {
        "word": "مرحبًا",
        "pos": "interjection",
        "gloss": "hello",
        "pronunciation": "marhaban"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/7053957091168924080.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: are you good?",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/4945881027502650426.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: good morning",
  "response": {
    "mode": "x_to_ar",
    "text": "صباح الخير",
    "tokens": [
      {
        "word": "صباح",
        "pos": "noun",
        "gloss": "morning",
        "pronunciation": "sabah"
      },
      {
        "word": "الخير",
        "pos": "noun",
        "gloss": "goodness",
        "pronunciation": "al-khayr"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/643436957942466218.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: Do you know vietnamese?",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/7066280205460249541.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: good night",
  "response": {
    "mode": "x_to_ar",
    "text": "تصبح على خير",
    "tokens": [
      {
        "word": "تصبح",
        "pos": "verb",
        "gloss": "goodnight",
        "pronunciation": "taSbaH"
      },
      {
        "word": "على",
        "pos": "preposition",
        "gloss": "on",
        "pronunciation": "ala"
      },
      {
        "word": "خير",
        "pos": "noun",
        "gloss": "goodness",
        "pronunciation": "khayr"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/9021843028433882689.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: be a good man",
  "response": {
    "mode": "x_to_ar",
    "text": "كن رجلاً جيداً",
    "tokens": [
      {
        "word": "كن",
        "pos": "verb",
        "gloss": "be",
        "pronunciation": "kun"
      },
      {
        "word": "رجلاً",
        "pos": "noun",
        "gloss": "man",
        "pronunciation": "rajulan"
      },
      {
        "word": "جيداً",
        "pos": "adjective",
        "gloss": "good",
        "pronunciation": "jayidan"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/5360975056719914482.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: good morning",
  "response": {
    "mode": "x_to_ar",
    "text": "صباح الخير",
    "tokens": [
      {
        "word": "صباح",
        "pos": "noun",
        "gloss": "morning",
        "pronunciation": "sabah"
      },
      {
        "word": "الخير",
        "pos": "noun",
        "gloss": "goodness",
        "pronunciation": "al-khayr"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/6833357272281247773.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: This is my first message on EchoMind! Exciting😝",
  "response": {
    "mode": "x_to_ar",
    "text": "هذه هي رسالتي الأولى على EchoMind! مثير😝",
    "tokens": [
      {
        "word": "هذه",
        "pos": "pronoun",
        "gloss": "this",
        "pronunciation": "hādhihi"
      },
      {
        "word": "هي",
        "pos": "pronoun",
        "gloss": "is",
        "pronunciation": "hiya"
      },
      {
        "word": "رسالتي",
        "pos": "noun",
        "gloss": "my message",
        "pronunciation": "risālatī"
      },
      {
        "word": "الأولى",
        "pos": "adjective",
        "gloss": "first",
        "pronunciation": "al-ūlā"
      },
      {
        "word": "على",
        "pos": "preposition",
        "gloss": "on",
        "pronunciation": "ʿalā"
      },
      {
        "word": "EchoMind",
        "pos": "proper_noun",
        "gloss": "EchoMind",
        "pronunciation": "EchoMind"
      },
      {
        "word": "!",
        "pos": "punct",
        "gloss": "exclamation",
        "pronunciation": ""
      },
      {
        "word": "مثير",
        "pos": "adjective",
        "gloss": "exciting",
        "pronunciation": "muthīr"
      },
      {
        "word": "😝",
        "pos": "punct",
        "gloss": "emoji",
        "pronunciation": ""
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/3466637071434813230.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: good night",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/235601201326969873.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: Good night! Sleep well and sweet dreams!",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/490810152428839276.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: do you have arabic?",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/8035180374105800871.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: are you good?",
  "response": {
    "mode": "x_to_ar",
    "text": "هل أنت جيد؟",
    "tokens": [
      {
        "word": "هل",
        "pos": "particle",
        "gloss": "interrogative particle",
        "pronunciation": "hal"
      },
      {
        "word": "أنت",
        "pos": "pronoun",
        "gloss": "you (masc.)",
        "pronunciation": "anta"
      },
      {
        "word": "جيد",
        "pos": "adjective",
        "gloss": "good",
        "pronunciation": "jayyid"
      },
      {
        "word": "؟",
        "pos": "punct",
        "gloss": "question mark",
        "pronunciation": ""
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/9025570221409572896.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: are you a man",
  "response": {
    "mode": "x_to_ar",
    "text": "هل أنت رجل؟",
    "tokens": [
      {
        "word": "هل",
        "pos": "particle",
        "gloss": "interrogative particle",
        "pronunciation": "hal"
      },
      {
        "word": "أنت",
        "pos": "pronoun",
        "gloss": "you (masc.)",
        "pronunciation": "anta"
      },
      {
        "word": "رجل",
        "pos": "noun",
        "gloss": "man",
        "pronunciation": "rajul"
      },
      {
        "word": "؟",
        "pos": "punct",
        "gloss": "question mark",
        "pronunciation": ""
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/6077239155748051427.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: do you have color?",
  "response": {
    "mode": "x_to_ar",
    "text": "هل لديك لون؟",
    "tokens": [
      {
        "word": "هل",
        "pos": "particle",
        "gloss": "do",
        "pronunciation": "hal"
      },
      {
        "word": "لديك",
        "pos": "pronoun",
        "gloss": "you have",
        "pronunciation": "ladayka"
      },
      {
        "word": "لون",
        "pos": "noun",
        "gloss": "color",
        "pronunciation": "lawn"
      },
      {
        "word": "؟",
        "pos": "punct",
        "gloss": "?",
        "pronunciation": "?"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/8667999940245128344.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: auto\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: Do you know vietnamese?",
  "response": {
    "mode": "x_to_ar",
    "text": "هل تعرف الفيتنامية؟",
    "tokens": [
      {
        "word": "هل",
        "pos": "particle",
        "gloss": "do",
        "pronunciation": "hal"
      },
      {
        "word": "تعرف",
        "pos": "verb",
        "gloss": "know",
        "pronunciation": "ta'raf"
      },
      {
        "word": "الفينامينية",
        "pos": "noun",
        "gloss": "Vietnamese",
        "pronunciation": "al-fiitnaamiyah"
      },
      {
        "word": "؟",
        "pos": "punct",
        "gloss": "?",
        "pronunciation": "?"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/3857179877748043540.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: good morning",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/5519971244856237350.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: Can you show korean?",
  "response": {
    "mode": "x_to_ar",
    "text": "هل يمكنك عرض الكورية؟",
    "tokens": [
      {
        "word": "هل",
        "pos": "particle",
        "gloss": "interrogative particle",
        "pronunciation": "hal"
      },
      {
        "word": "يمكنك",
        "pos": "verb",
        "gloss": "you can",
        "pronunciation": "yumkinuka"
      },
      {
        "word": "عرض",
        "pos": "verb",
        "gloss": "show",
        "pronunciation": "ard"
      },
      {
        "word": "الكورية",
        "pos": "noun",
        "gloss": "Korean (language)",
        "pronunciation": "alkuriyah"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/5915981617966500726.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: hello",
  "response": {
    "mode": "x_to_ar",
    "text": "مرحبا",
    "tokens": [
      {
        "word": "مرحبا",
        "pos": "interjection",
        "gloss": "hello",
        "pronunciation": "marhaban"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/6122818794700591178.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: hello",
  "response": {
    "mode": "x_to_ar",
    "text": "مرحبا",
    "tokens": [
      {
        "word": "مرحبا",
        "pos": "interjection",
        "gloss": "hello",
        "pronunciation": "marhaban"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/1745499371238279023.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: all_zh\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: 不客气！有什么我可以帮你的吗？",
  "response": {
    "mode": "x_to_ar",
    "text": "لا شكر على واجب! هل هناك شيء يمكنني مساعدتك به؟",
    "tokens": [
      {
        "word": "لا",
        "pos": "particle",
        "gloss": "no/not",
        "pronunciation": "la"
      },
      {
        "word": "شكر",
        "pos": "noun",
        "gloss": "thanks",
        "pronunciation": "shukr"
      },
      {
        "word": "على",
        "pos": "preposition",
        "gloss": "on/for",
        "pronunciation": "ʿala"
      },
      {
        "word": "واجب",
        "pos": "noun",
        "gloss": "duty/obligation",
        "pronunciation": "wajib"
      },
      {
        "word": "!",
        "pos": "punct",
        "gloss": "exclamation mark",
        "pronunciation": ""
      },
      {
        "word": "هل",
        "pos": "particle",
        "gloss": "is/are (question particle)",
        "pronunciation": "hal"
      },
      {
        "word": "هناك",
        "pos": "adverb",
        "gloss": "there/existence",
        "pronunciation": "hunak"
      },
      {
        "word": "شيء",
        "pos": "noun",
        "gloss": "thing",
        "pronunciation": "shayʾ"
      },
      {
        "word": "يمكنني",
        "pos": "verb",
        "gloss": "I can",
        "pronunciation": "yumkinuni"
      },
      {
        "word": "مساعدتك",
        "pos": "verb",
        "gloss": "helping you",
        "pronunciation": "musāʿadatak"
      },
      {
        "word": "به",
        "pos": "preposition",
        "gloss": "in/on/at (with object pronoun)",
        "pronunciation": "bih"
      },
      {
        "word": "؟",
        "pos": "punct",
        "gloss": "question mark",
        "pronunciation": ""
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/4721904339569269670.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: auto\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: are you a man",
  "response": {
    "mode": "x_to_ar",
    "text": "هل أنت رجل؟",
    "tokens": [
      {
        "word": "هل",
        "pos": "particle",
        "gloss": "interrogative particle",
        "pronunciation": "hal"
      },
      {
        "word": "أنت",
        "pos": "pronoun",
        "gloss": "you (masculine)",
        "pronunciation": "anta"
      },
      {
        "word": "رجل",
        "pos": "noun",
        "gloss": "man",
        "pronunciation": "rajul"
      },
      {
        "word": "؟",
        "pos": "punct",
        "gloss": "question mark",
        "pronunciation": ""
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/7805962083818272978.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: hello",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/7406560790318977771.json`

```json
{
  "prompt": "If the text: \"The door is closed.\" is not Arabic, translate it into natural Arabic (Arabic script) first.\nIf it's already Arabic, polish it to correct and native Arabic (Arabic script).\n\nAnalyze this Arabic text into words.\n\nReturn JSON with:\n- arabic_text: native and exact Arabic translation or polished original Arabic (Arabic script only)\n- words: array of objects:\n  - word: the word/particle/punctuation as it appears in arabic_text (Arabic script for Arabic words)\n  - type: grammatical type from this enum: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, measure, classifier, particle, auxiliary, determiner, interjection, punctuation, other\n  - pronunciation: Arabic-to-Latin romanization for the ENTIRE word (empty string for non-Arabic words)\n\nRequirements:\n- Keep arabic_text strictly in Arabic script.\n- Segment precisely; keep punctuation as separate words.\n- Provide pronunciation for Arabic words; leave empty for non-Arabic tokens.\n- Be consistent; no empty items.\n- Output strict JSON only.\n",
  "response": {
    "arabic_text": "الباب مغلق.",
    "words": [
      {
        "word": "الباب",
        "type": "noun",
        "pronunciation": "al-bāb"
      },
      {
        "word": "مغلق",
        "type": "adjective",
        "pronunciation": "mughlaq"
      },
      {
        "word": ".",
        "type": "punctuation",
        "pronunciation": ""
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/287473389615231218.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: hello",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/7354146486150291062.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: This is my first message on EchoMind! Exciting😝",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/5442159521412527825.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: helo",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/5394276623797045389.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: do you still have color?",
  "response": {
    "mode": "x_to_ar",
    "text": "هل لا زلت تمتلك لونًا؟",
    "tokens": [
      {
        "word": "هل",
        "pos": "particle",
        "gloss": "question particle",
        "pronunciation": "hal"
      },
      {
        "word": "لا",
        "pos": "particle",
        "gloss": "negation",
        "pronunciation": "la"
      },
      {
        "word": "زلت",
        "pos": "verb",
        "gloss": "still",
        "pronunciation": "zalat"
      },
      {
        "word": "تمتلك",
        "pos": "verb",
        "gloss": "have",
        "pronunciation": "tamilik"
      },
      {
        "word": "لونًا",
        "pos": "noun",
        "gloss": "color",
        "pronunciation": "lawnan"
      },
      {
        "word": "؟",
        "pos": "punct",
        "gloss": "question mark",
        "pronunciation": "؟"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/5784273752981544122.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: hello",
  "response": {
    "mode": "x_to_ar",
    "text": "مرحباً",
    "tokens": [
      {
        "word": "مرحباً",
        "pos": "interjection",
        "gloss": "hello",
        "pronunciation": "marhaban"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/2417555254606788826.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: good morning",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/6979289471964234580.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: all_zh\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: 你好呀！有什么我可以帮助你的吗？",
  "response": {
    "mode": "x_to_ar",
    "text": "مرحبًا! هل هناك شيء يمكنني مساعدتك به؟",
    "tokens": [
      {
        "word": "مرحبًا",
        "pos": "interjection",
        "gloss": "Hello",
        "pronunciation": "marhaban"
      },
      {
        "word": "هل",
        "pos": "particle",
        "gloss": "is",
        "pronunciation": "hal"
      },
      {
        "word": "هناك",
        "pos": "adverb",
        "gloss": "there",
        "pronunciation": "hunaak"
      },
      {
        "word": "شيء",
        "pos": "noun",
        "gloss": "thing",
        "pronunciation": "shay' "
      },
      {
        "word": "يمكنني",
        "pos": "verb",
        "gloss": "I can",
        "pronunciation": "yumkinuni"
      },
      {
        "word": "مساعدتك",
        "pos": "noun",
        "gloss": "your help",
        "pronunciation": "musaa'datak"
      },
      {
        "word": "به",
        "pos": "preposition",
        "gloss": "with it",
        "pronunciation": "bih"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/5803408217385547902.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: Do you know vietnamese?",
  "response": {
    "mode": "x_to_ar",
    "text": "هل تعرف الفيتنامية؟",
    "tokens": [
      {
        "word": "هل",
        "pos": "particle",
        "gloss": "Do",
        "pronunciation": "hal"
      },
      {
        "word": "تعرف",
        "pos": "verb",
        "gloss": "know",
        "pronunciation": "ta'ref"
      },
      {
        "word": "الفيتنامية",
        "pos": "noun",
        "gloss": "Vietnamese",
        "pronunciation": "al-feytnamiyah"
      },
      {
        "word": "؟",
        "pos": "punct",
        "gloss": "?",
        "pronunciation": ""
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/5634678063952136190.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: can you talk?",
  "response": {
    "mode": "x_to_ar",
    "text": "هل يمكنك التحدث؟",
    "tokens": [
      {
        "word": "هل",
        "pos": "particle",
        "gloss": "interrogative particle",
        "pronunciation": "hal"
      },
      {
        "word": "يمكنك",
        "pos": "verb",
        "gloss": "can you",
        "pronunciation": "yumkinuka"
      },
      {
        "word": "التحدث",
        "pos": "verb",
        "gloss": "to talk",
        "pronunciation": "at-tahaduth"
      },
      {
        "word": "؟",
        "pos": "punct",
        "gloss": "question mark",
        "pronunciation": "?"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/4251929233052724648.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: good night",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/9011191531587457026.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: ja\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: これはテスト投稿ですよ～～！",
  "response": {
    "mode": "x_to_ar",
    "text": "هذا هو منشور اختبار!!",
    "tokens": [
      {
        "word": "هذا",
        "pos": "pronoun",
        "gloss": "this",
        "pronunciation": "hādhā"
      },
      {
        "word": "هو",
        "pos": "pronoun",
        "gloss": "is",
        "pronunciation": "huwa"
      },
      {
        "word": "منشور",
        "pos": "noun",
        "gloss": "post",
        "pronunciation": "manšūr"
      },
      {
        "word": "اختبار",
        "pos": "noun",
        "gloss": "test",
        "pronunciation": "iḵtibār"
      },
      {
        "word": "!!",
        "pos": "punct",
        "gloss": "exclamation",
        "pronunciation": ""
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/7668489692928622677.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: good morning",
  "response": {
    "mode": "x_to_ar",
    "text": "صباح الخير",
    "tokens": [
      {
        "word": "صباح",
        "pos": "noun",
        "gloss": "morning",
        "pronunciation": "sabaah"
      },
      {
        "word": "الخير",
        "pos": "noun",
        "gloss": "goodness",
        "pronunciation": "al-khayr"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/4788075398056676856.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: good morning",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/7060999358822594350.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: is this work?",
  "response": {
    "mode": "x_to_ar",
    "text": "هل هذا عمل؟",
    "tokens": [
      {
        "word": "هل",
        "pos": "particle",
        "gloss": "interrogative particle",
        "pronunciation": "hal"
      },
      {
        "word": "هذا",
        "pos": "pronoun",
        "gloss": "this",
        "pronunciation": "hadha"
      },
      {
        "word": "عمل",
        "pos": "noun",
        "gloss": "work",
        "pronunciation": "amal"
      },
      {
        "word": "؟",
        "pos": "punct",
        "gloss": "question mark",
        "pronunciation": ""
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/5127979355521204020.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: do you have color?",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/5750329385854918738.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: hello",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/1502136515859198912.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: Good night! Sleep well and sweet dreams!",
  "response": {
    "mode": "x_to_ar",
    "text": "تصبح على خير! نام جيدًا وأحلام سعيدة!",
    "tokens": [
      {
        "word": "تصبح",
        "pos": "verb",
        "gloss": "wake up / good night",
        "pronunciation": "tuṣbiḥ"
      },
      {
        "word": "على",
        "pos": "preposition",
        "gloss": "on / upon",
        "pronunciation": "ʿalā"
      },
      {
        "word": "خير",
        "pos": "noun",
        "gloss": "goodness / well",
        "pronunciation": "khayr"
      },
      {
        "word": "!",
        "pos": "punct",
        "gloss": "exclamation mark",
        "pronunciation": ""
      },
      {
        "word": "نام",
        "pos": "verb",
        "gloss": "sleep",
        "pronunciation": "nām"
      },
      {
        "word": "جيدًا",
        "pos": "adverb",
        "gloss": "well",
        "pronunciation": "jayidan"
      },
      {
        "word": "و",
        "pos": "conjunction",
        "gloss": "and",
        "pronunciation": "wa"
      },
      {
        "word": "أحلام",
        "pos": "noun",
        "gloss": "dreams",
        "pronunciation": "aḥlām"
      },
      {
        "word": "سعيدة",
        "pos": "adjective",
        "gloss": "sweet / happy",
        "pronunciation": "saʿīdah"
      },
      {
        "word": "!",
        "pos": "punct",
        "gloss": "exclamation mark",
        "pronunciation": ""
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/2532891545621713912.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: good morning",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/8346575744894348317.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: do you have arabic?",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/8445822149148897778.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: do you have arabic?",
  "response": {
    "mode": "x_to_ar",
    "text": "هل لديك العربية؟",
    "tokens": [
      {
        "word": "هل",
        "pos": "particle",
        "gloss": "do",
        "pronunciation": "hal"
      },
      {
        "word": " لديك",
        "pos": "pronoun",
        "gloss": "you have",
        "pronunciation": "ladayka"
      },
      {
        "word": "العربية",
        "pos": "noun",
        "gloss": "Arabic",
        "pronunciation": "al-‘arabiyyah"
      },
      {
        "word": "؟",
        "pos": "punct",
        "gloss": "?",
        "pronunciation": ""
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/3913231379783509531.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: vi\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: Is this vietnamese?",
  "response": {
    "mode": "x_to_ar",
    "text": "هل هذه فيتنامية؟",
    "tokens": [
      {
        "word": "هل",
        "pos": "particle",
        "gloss": "Is",
        "pronunciation": "hal"
      },
      {
        "word": "هذه",
        "pos": "pronoun",
        "gloss": "this",
        "pronunciation": "hādhih"
      },
      {
        "word": "فيتنامية",
        "pos": "adjective",
        "gloss": "Vietnamese",
        "pronunciation": "vītnāmiyyah"
      },
      {
        "word": "؟",
        "pos": "punct",
        "gloss": "?",
        "pronunciation": ""
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/860645651523435076.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: これはテスト投稿ですよ～～！",
  "response": {
    "language_code": "ja"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/5739750543689723779.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: hello",
  "response": {
    "mode": "x_to_ar",
    "text": "مرحبا",
    "tokens": [
      {
        "word": "مرحبا",
        "pos": "interjection",
        "gloss": "hello",
        "pronunciation": "marhaban"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/1310959215988174060.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: Hello, hello, hello, hello, hello, hello.",
  "response": {
    "mode": "x_to_ar",
    "text": "مرحبا، مرحبا، مرحبا، مرحبا، مرحبا، مرحبا.",
    "tokens": [
      {
        "word": "مرحبا",
        "pos": "interjection",
        "gloss": "hello",
        "pronunciation": "marhaban"
      },
      {
        "word": "،",
        "pos": "punct",
        "gloss": ",",
        "pronunciation": ","
      },
      {
        "word": "مرحبا",
        "pos": "interjection",
        "gloss": "hello",
        "pronunciation": "marhaban"
      },
      {
        "word": "،",
        "pos": "punct",
        "gloss": ",",
        "pronunciation": ","
      },
      {
        "word": "مرحبا",
        "pos": "interjection",
        "gloss": "hello",
        "pronunciation": "marhaban"
      },
      {
        "word": "،",
        "pos": "punct",
        "gloss": ",",
        "pronunciation": ","
      },
      {
        "word": "مرحبا",
        "pos": "interjection",
        "gloss": "hello",
        "pronunciation": "marhaban"
      },
      {
        "word": "،",
        "pos": "punct",
        "gloss": ",",
        "pronunciation": ","
      },
      {
        "word": "مرحبا",
        "pos": "interjection",
        "gloss": "hello",
        "pronunciation": "marhaban"
      },
      {
        "word": "،",
        "pos": "punct",
        "gloss": ",",
        "pronunciation": ","
      },
      {
        "word": "مرحبا",
        "pos": "interjection",
        "gloss": "hello",
        "pronunciation": "marhaban"
      },
      {
        "word": "،",
        "pos": "punct",
        "gloss": ",",
        "pronunciation": ","
      },
      {
        "word": "مرحبا",
        "pos": "interjection",
        "gloss": "hello",
        "pronunciation": "marhaban"
      },
      {
        "word": "،",
        "pos": "punct",
        "gloss": ",",
        "pronunciation": ","
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/2494454006560073737.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: en\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: good night",
  "response": {
    "mode": "x_to_ar",
    "text": "تصبح على خير",
    "tokens": [
      {
        "word": "تصبح",
        "pos": "verb",
        "gloss": "you (masculine) become",
        "pronunciation": "taṣbiḥ"
      },
      {
        "word": "على",
        "pos": "preposition",
        "gloss": "on",
        "pronunciation": "ʿalā"
      },
      {
        "word": "خير",
        "pos": "noun",
        "gloss": "good (thing)",
        "pronunciation": "khayr"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/5286142410007128319.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: vi\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: I added vietnamese.",
  "response": {
    "mode": "x_to_ar",
    "text": "لقد أضفت الفيتنامية.",
    "tokens": [
      {
        "word": "لقد",
        "pos": "particle",
        "gloss": "indeed",
        "pronunciation": "laqad"
      },
      {
        "word": "أضفت",
        "pos": "verb",
        "gloss": "I added",
        "pronunciation": "aḍafta"
      },
      {
        "word": "الفيتنامية",
        "pos": "noun",
        "gloss": "Vietnamese (language)",
        "pronunciation": "al-fītnāmiyyah"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/2661835195821041643.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: good morning",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/970220018667035119.json`

```json
{
  "prompt": "Detect ISO 639-1 language code for: I want to post something to delete.",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/arabic_enhancement_cache/6218121624530400948.json`

```json
{
  "prompt": "You are an Arabic linguistic assistant.\nReturn strict JSON per schema.\nSource language: all_zh\nIf source is Arabic, set mode='ar_native' and use the given text for analysis.\nOtherwise translate the text into Arabic first, set mode='x_to_ar', and analyze the Arabic translation.\nCRITICAL: When translating (mode='x_to_ar'), both `text` and every token `word` MUST be Arabic script only.\nTokens: provide a coarse POS and concise English gloss; add Arabic-to-Latin pronunciation in `pronunciation`.\nAllowed POS: noun, proper_noun, verb, adjective, adverb, pronoun, preposition, conjunction, numeral, classifier, measure, particle, auxiliary, determiner, interjection, punct, other.\nText: 不客气！有什么我可以帮你的吗？",
  "response": {
    "mode": "x_to_ar",
    "text": "لا شكر على واجب! هل هناك شيء يمكنني مساعدتك به؟",
    "tokens": [
      {
        "word": "لا",
        "pos": "particle",
        "gloss": "no",
        "pronunciation": "la"
      },
      {
        "word": "شكر",
        "pos": "noun",
        "gloss": "thanks",
        "pronunciation": "shukr"
      },
      {
        "word": "على",
        "pos": "preposition",
        "gloss": "on",
        "pronunciation": "‘ala"
      },
      {
        "word": "واجب",
        "pos": "noun",
        "gloss": "duty",
        "pronunciation": "wajib"
      },
      {
        "word": "！",
        "pos": "punct",
        "gloss": "exclamation mark",
        "pronunciation": ""
      },
      {
        "word": "هل",
        "pos": "particle",
        "gloss": "does",
        "pronunciation": "hal"
      },
      {
        "word": "هناك",
        "pos": "pronoun",
        "gloss": "there",
        "pronunciation": "hunak"
      },
      {
        "word": "شيء",
        "pos": "noun",
        "gloss": "thing",
        "pronunciation": "shay"
      },
      {
        "word": "يمكنني",
        "pos": "verb",
        "gloss": "I can",
        "pronunciation": "yumkinuni"
      },
      {
        "word": "مساعدتك",
        "pos": "noun",
        "gloss": "helping you",
        "pronunciation": "musa’adatak"
      },
      {
        "word": "به",
        "pos": "preposition",
        "gloss": "it",
        "pronunciation": "bihi"
      },
      {
        "word": "؟",
        "pos": "punct",
        "gloss": "question mark",
        "pronunciation": ""
      }
    ]
  }
}
```
