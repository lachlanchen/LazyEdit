# Vietnamese Prompts

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/8155279760556954035.json`

```json
{
  "prompt": "Detect the primary language of this text and return ISO 639-1 code only.\nText: do you have arabic?",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/23480586069838066.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: zh\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: 真的会讲越南语吗",
  "response": {
    "mode": "x_to_vi",
    "translation": "Có thật sự biết nói tiếng Việt không?",
    "tokens": [
      {
        "word": "Có",
        "pos": "verb",
        "pronunciation": "Co",
        "color": "#000000",
        "gloss": "to have"
      },
      {
        "word": "thật",
        "pos": "adverb",
        "pronunciation": "that",
        "color": "#000000",
        "gloss": "really"
      },
      {
        "word": "sự",
        "pos": "noun",
        "pronunciation": "su",
        "color": "#000000",
        "gloss": "existence"
      },
      {
        "word": "biết",
        "pos": "verb",
        "pronunciation": "biet",
        "color": "#000000",
        "gloss": "to know"
      },
      {
        "word": "nói",
        "pos": "verb",
        "pronunciation": "noi",
        "color": "#000000",
        "gloss": "to speak"
      },
      {
        "word": "tiếng",
        "pos": "noun",
        "pronunciation": "tieng",
        "color": "#000000",
        "gloss": "language"
      },
      {
        "word": "Việt",
        "pos": "proper noun",
        "pronunciation": "Viet",
        "color": "#000000",
        "gloss": "Vietnamese"
      },
      {
        "word": "không",
        "pos": "particle",
        "pronunciation": "khong",
        "color": "#000000",
        "gloss": "not"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/4424774243931656498.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: all_zh\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: 你好！有什么我可以帮助你的吗？",
  "response": {
    "mode": "x_to_vi",
    "translation": "Xin chào! Có gì tôi có thể giúp bạn không?",
    "tokens": [
      {
        "word": "Xin",
        "pos": "interjection",
        "pronunciation": "Xin",
        "color": "#000000",
        "gloss": "Please"
      },
      {
        "word": "chào",
        "pos": "verb",
        "pronunciation": "chao",
        "color": "#000000",
        "gloss": "greet"
      },
      {
        "word": "Có",
        "pos": "verb",
        "pronunciation": "Co",
        "color": "#000000",
        "gloss": "There is"
      },
      {
        "word": "gì",
        "pos": "pronoun",
        "pronunciation": "gi",
        "color": "#000000",
        "gloss": "what"
      },
      {
        "word": "tôi",
        "pos": "pronoun",
        "pronunciation": "toi",
        "color": "#000000",
        "gloss": "I"
      },
      {
        "word": "có",
        "pos": "verb",
        "pronunciation": "co",
        "color": "#000000",
        "gloss": "can"
      },
      {
        "word": "thể",
        "pos": "verb",
        "pronunciation": "the",
        "color": "#000000",
        "gloss": "be able to"
      },
      {
        "word": "giúp",
        "pos": "verb",
        "pronunciation": "giup",
        "color": "#000000",
        "gloss": "help"
      },
      {
        "word": "bạn",
        "pos": "pronoun",
        "pronunciation": "ban",
        "color": "#000000",
        "gloss": "you"
      },
      {
        "word": "không",
        "pos": "particle",
        "pronunciation": "khong",
        "color": "#000000",
        "gloss": "not"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/4223778723503468320.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: zh\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: I forwarded this post. 非非非非你还在吗没有没有我先我先那个啥",
  "response": {
    "mode": "x_to_vi",
    "translation": "Tôi đã chuyển tiếp bài viết này. Không không không không, bạn vẫn ở đó không? Không không, trước tiên tôi, trước tiên cái đó.",
    "tokens": [
      {
        "word": "Tôi",
        "pos": "pronoun",
        "pronunciation": "Toi",
        "color": "#000000",
        "gloss": "I"
      },
      {
        "word": "đã",
        "pos": "adverb",
        "pronunciation": "da",
        "color": "#000000",
        "gloss": "already"
      },
      {
        "word": "chuyển",
        "pos": "verb",
        "pronunciation": "chuyen",
        "color": "#000000",
        "gloss": "forward"
      },
      {
        "word": "tiếp",
        "pos": "verb",
        "pronunciation": "tiep",
        "color": "#000000",
        "gloss": "continue"
      },
      {
        "word": "bài",
        "pos": "noun",
        "pronunciation": "bai",
        "color": "#000000",
        "gloss": "post"
      },
      {
        "word": "viết",
        "pos": "verb",
        "pronunciation": "viet",
        "color": "#000000",
        "gloss": "write"
      },
      {
        "word": "này",
        "pos": "pronoun",
        "pronunciation": "nay",
        "color": "#000000",
        "gloss": "this"
      },
      {
        "word": "Không",
        "pos": "adverb",
        "pronunciation": "Khong",
        "color": "#000000",
        "gloss": "no"
      },
      {
        "word": "không",
        "pos": "adverb",
        "pronunciation": "khong",
        "color": "#000000",
        "gloss": "no (repeated for emphasis)"
      },
      {
        "word": "bạn",
        "pos": "pronoun",
        "pronunciation": "ban",
        "color": "#000000",
        "gloss": "you"
      },
      {
        "word": "vẫn",
        "pos": "adverb",
        "pronunciation": "van",
        "color": "#000000",
        "gloss": "still"
      },
      {
        "word": "ở",
        "pos": "verb",
        "pronunciation": "o",
        "color": "#000000",
        "gloss": "to be"
      },
      {
        "word": "đó",
        "pos": "pronoun",
        "pronunciation": "do",
        "color": "#000000",
        "gloss": "there"
      },
      {
        "word": "không",
        "pos": "adverb",
        "pronunciation": "khong",
        "color": "#000000",
        "gloss": "no (again for emphasis)"
      },
      {
        "word": "trước",
        "pos": "adverb",
        "pronunciation": "truoc",
        "color": "#000000",
        "gloss": "first"
      },
      {
        "word": "tiên",
        "pos": "adverb",
        "pronunciation": "tien",
        "color": "#000000",
        "gloss": "before"
      },
      {
        "word": "tôi",
        "pos": "pronoun",
        "pronunciation": "toi",
        "color": "#000000",
        "gloss": "I (repeated)"
      },
      {
        "word": "cái",
        "pos": "noun",
        "pronunciation": "cai",
        "color": "#000000",
        "gloss": "that"
      },
      {
        "word": "đó",
        "pos": "pronoun",
        "pronunciation": "do",
        "color": "#000000",
        "gloss": "that (repeated)"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/5632865401596325280.json`

```json
{
  "prompt": "If the text: \"@lachlan Owner\" is not Vietnamese, translate it into natural Vietnamese (with correct diacritics) first.\nIf it's already Vietnamese, polish it to correct and native Vietnamese.\n\nAnalyze this Vietnamese text into words.\n\nReturn JSON with:\n- vietnamese_text: native and exact Vietnamese translation or polished original Vietnamese\n- words: array of objects with:\n  - word: the word/particle/punctuation as it appears in vietnamese_text\n  - type: grammatical type from this enum: noun, verb, adjective, adverb, particle, pronoun, numeral, measure, preposition, conjunction, interjection, punctuation, other\n\nRequirements:\n- Segment precisely; keep punctuation as separate words.\n- Use Vietnamese diacritics.\n- Be consistent; no empty items.\n",
  "response": {
    "vietnamese_text": "@lachlan Chủ sở hữu",
    "words": [
      {
        "word": "@lachlan",
        "type": "other"
      },
      {
        "word": "Chủ",
        "type": "noun"
      },
      {
        "word": "sở",
        "type": "noun"
      },
      {
        "word": "hữu",
        "type": "noun"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/238012449260175640.json`

```json
{
  "prompt": "Detect the primary language of this text and return ISO 639-1 code only.\nText: Let me post something",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/1392461030505488650.json`

```json
{
  "prompt": "Detect the primary language of this text and return ISO 639-1 code only.\nText: How about I say a very long sentecne? Can you do the same thing for me?",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/8212659197794555566.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nIf input is not Vietnamese, rewrite it into pure Vietnamese first.\nThen analyze the Vietnamese sentence and reply with JSON ONLY per schema: { mode: 'vi_native' | 'x_to_vi', translation: <vietnamese>, tokens: [ { word, pos, pronunciation, gloss } ] }.\nText: be a good man",
  "response": {
    "mode": "x_to_vi",
    "translation": "hãy là một người tốt",
    "tokens": [
      {
        "word": "hãy",
        "pos": "verb",
        "pronunciation": "hảy",
        "gloss": "used to express an imperative or suggestion"
      },
      {
        "word": "là",
        "pos": "verb",
        "pronunciation": "là",
        "gloss": "to be"
      },
      {
        "word": "một",
        "pos": "determiner",
        "pronunciation": "một",
        "gloss": "one/a/an"
      },
      {
        "word": "người",
        "pos": "noun",
        "pronunciation": "người",
        "gloss": "person"
      },
      {
        "word": "tốt",
        "pos": "adjective",
        "pronunciation": "tốt",
        "gloss": "good"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/9216668452486195406.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: en\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: do you have color?",
  "response": {
    "mode": "x_to_vi",
    "translation": "bạn có màu sắc không?",
    "tokens": [
      {
        "word": "bạn",
        "pos": "pronoun",
        "pronunciation": "ban",
        "color": "#000000",
        "gloss": "you"
      },
      {
        "word": "có",
        "pos": "verb",
        "pronunciation": "co",
        "color": "#000000",
        "gloss": "have"
      },
      {
        "word": "màu",
        "pos": "noun",
        "pronunciation": "mau",
        "color": "#000000",
        "gloss": "color"
      },
      {
        "word": "sắc",
        "pos": "noun",
        "pronunciation": "sac",
        "color": "#000000",
        "gloss": "spectrum"
      },
      {
        "word": "không",
        "pos": "particle",
        "pronunciation": "khong",
        "color": "#000000",
        "gloss": "not"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/6391377465145065480.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: zh\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: 你还想跟我聊天吗?",
  "response": {
    "mode": "x_to_vi",
    "translation": "Bạn có muốn trò chuyện với tôi nữa không?",
    "tokens": [
      {
        "word": "Bạn",
        "pos": "pronoun",
        "pronunciation": "Ban",
        "color": "#00A0B0",
        "gloss": "You"
      },
      {
        "word": "có",
        "pos": "verb",
        "pronunciation": "co",
        "color": "#00A0B0",
        "gloss": "to have"
      },
      {
        "word": "muốn",
        "pos": "verb",
        "pronunciation": "muon",
        "color": "#00A0B0",
        "gloss": "to want"
      },
      {
        "word": "trò",
        "pos": "noun",
        "pronunciation": "tro",
        "color": "#00A0B0",
        "gloss": "conversation"
      },
      {
        "word": "chuyện",
        "pos": "noun",
        "pronunciation": "chuyen",
        "color": "#00A0B0",
        "gloss": "talk"
      },
      {
        "word": "với",
        "pos": "preposition",
        "pronunciation": "voi",
        "color": "#00A0B0",
        "gloss": "with"
      },
      {
        "word": "tôi",
        "pos": "pronoun",
        "pronunciation": "toi",
        "color": "#00A0B0",
        "gloss": "I"
      },
      {
        "word": "nữa",
        "pos": "adverb",
        "pronunciation": "nua",
        "color": "#00A0B0",
        "gloss": "again"
      },
      {
        "word": "không",
        "pos": "particle",
        "pronunciation": "khong",
        "color": "#00A0B0",
        "gloss": "not"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/1650212334591397177.json`

```json
{
  "prompt": "Detect the primary language of this text and return ISO 639-1 code only.\nText: do you still have color?",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/6022523063237471482.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: zh\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: 真的会讲越南语吗",
  "response": {
    "mode": "x_to_vi",
    "translation": "Bạn có thật sự nói được tiếng Việt không?",
    "tokens": [
      {
        "word": "Bạn",
        "pos": "pronoun",
        "pronunciation": "ban",
        "color": "#FFCC00",
        "gloss": "you"
      },
      {
        "word": "có",
        "pos": "verb",
        "pronunciation": "co",
        "color": "#FFCC00",
        "gloss": "can"
      },
      {
        "word": "thật",
        "pos": "adverb",
        "pronunciation": "that",
        "color": "#FFCC00",
        "gloss": "really"
      },
      {
        "word": "sự",
        "pos": "noun",
        "pronunciation": "su",
        "color": "#FFCC00",
        "gloss": "fact"
      },
      {
        "word": "nói",
        "pos": "verb",
        "pronunciation": "noi",
        "color": "#FFCC00",
        "gloss": "speak"
      },
      {
        "word": "được",
        "pos": "verb",
        "pronunciation": "duoc",
        "color": "#FFCC00",
        "gloss": "be able to"
      },
      {
        "word": "tiếng",
        "pos": "noun",
        "pronunciation": "tieng",
        "color": "#FFCC00",
        "gloss": "language"
      },
      {
        "word": "Việt",
        "pos": "noun",
        "pronunciation": "Viet",
        "color": "#FFCC00",
        "gloss": "Vietnamese"
      },
      {
        "word": "không",
        "pos": "particle",
        "pronunciation": "khong",
        "color": "#FFCC00",
        "gloss": "not?"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/815539049578078640.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: en\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: are you okay?",
  "response": {
    "mode": "x_to_vi",
    "translation": "Bạn có ổn không?",
    "tokens": [
      {
        "word": "Bạn",
        "pos": "Pronoun",
        "pronunciation": "Ban",
        "color": "#000000",
        "gloss": "You"
      },
      {
        "word": "có",
        "pos": "Verb",
        "pronunciation": "co",
        "color": "#000000",
        "gloss": "are"
      },
      {
        "word": "ổn",
        "pos": "Adjective",
        "pronunciation": "on",
        "color": "#000000",
        "gloss": "okay"
      },
      {
        "word": "không",
        "pos": "Particle",
        "pronunciation": "khong",
        "color": "#000000",
        "gloss": "not (used for questions)"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/8757422479930047444.json`

```json
{
  "prompt": "Detect the primary language of this text and return ISO 639-1 code only.\nText: What meal are you asking about? Are you looking for breakfast, lunch, or dinner ideas?",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/6908434101400330972.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: zh\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: 說一點中文",
  "response": {
    "mode": "x_to_vi",
    "translation": "Nói một chút tiếng Trung",
    "tokens": [
      {
        "word": "Nói",
        "pos": "verb",
        "pronunciation": "noi",
        "color": "#000000",
        "gloss": "to speak"
      },
      {
        "word": "một",
        "pos": "quantity",
        "pronunciation": "mot",
        "color": "#000000",
        "gloss": "one/a"
      },
      {
        "word": "chút",
        "pos": "noun",
        "pronunciation": "chut",
        "color": "#000000",
        "gloss": "bit/a little"
      },
      {
        "word": "tiếng",
        "pos": "noun",
        "pronunciation": "tieng",
        "color": "#000000",
        "gloss": "language"
      },
      {
        "word": "Trung",
        "pos": "noun",
        "pronunciation": "Trung",
        "color": "#000000",
        "gloss": "Chinese"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/2945766455463973886.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: all_zh\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: 不客气！有什么我可以帮你的吗？",
  "response": {
    "mode": "x_to_vi",
    "translation": "Đừng khách sáo! Có gì tôi có thể giúp bạn không?",
    "tokens": [
      {
        "word": "Đừng",
        "pos": "verb",
        "pronunciation": "Dung",
        "color": "#000000",
        "gloss": "do not"
      },
      {
        "word": "khách sáo",
        "pos": "adjective",
        "pronunciation": "khach sao",
        "color": "#000000",
        "gloss": "polite, formal"
      },
      {
        "word": "Có",
        "pos": "verb",
        "pronunciation": "Co",
        "color": "#000000",
        "gloss": "there is"
      },
      {
        "word": "gì",
        "pos": "pronoun",
        "pronunciation": "gi",
        "color": "#000000",
        "gloss": "what"
      },
      {
        "word": "tôi",
        "pos": "pronoun",
        "pronunciation": "toi",
        "color": "#000000",
        "gloss": "I"
      },
      {
        "word": "có thể",
        "pos": "verb",
        "pronunciation": "co the",
        "color": "#000000",
        "gloss": "can"
      },
      {
        "word": "giúp",
        "pos": "verb",
        "pronunciation": "giup",
        "color": "#000000",
        "gloss": "help"
      },
      {
        "word": "bạn",
        "pos": "pronoun",
        "pronunciation": "ban",
        "color": "#000000",
        "gloss": "you"
      },
      {
        "word": "không",
        "pos": "particle",
        "pronunciation": "khong",
        "color": "#000000",
        "gloss": "not"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/6348170464746234517.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: en\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: This is my first message on EchoMind! Exciting😝",
  "response": {
    "mode": "x_to_vi",
    "translation": "Đây là thông điệp đầu tiên của tôi trên EchoMind! Thú vị😝",
    "tokens": [
      {
        "word": "Đây",
        "pos": "pronoun",
        "pronunciation": "Day",
        "color": "#000000",
        "gloss": "This"
      },
      {
        "word": "là",
        "pos": "verb",
        "pronunciation": "la",
        "color": "#000000",
        "gloss": "is"
      },
      {
        "word": "thông",
        "pos": "noun",
        "pronunciation": "thong",
        "color": "#000000",
        "gloss": "message"
      },
      {
        "word": "điệp",
        "pos": "noun",
        "pronunciation": "diep",
        "color": "#000000",
        "gloss": "message (part of compound)"
      },
      {
        "word": "đầu",
        "pos": "adjective",
        "pronunciation": "dau",
        "color": "#000000",
        "gloss": "first"
      },
      {
        "word": "tiên",
        "pos": "adjective",
        "pronunciation": "tien",
        "color": "#000000",
        "gloss": "first (part of compound)"
      },
      {
        "word": "của",
        "pos": "preposition",
        "pronunciation": "cua",
        "color": "#000000",
        "gloss": "of"
      },
      {
        "word": "tôi",
        "pos": "pronoun",
        "pronunciation": "toi",
        "color": "#000000",
        "gloss": "my"
      },
      {
        "word": "trên",
        "pos": "preposition",
        "pronunciation": "tren",
        "color": "#000000",
        "gloss": "on"
      },
      {
        "word": "EchoMind",
        "pos": "noun",
        "pronunciation": "EchoMind",
        "color": "#000000",
        "gloss": "EchoMind (name)"
      },
      {
        "word": "!",
        "pos": "punctuation",
        "pronunciation": "",
        "color": "#000000",
        "gloss": "exclamation"
      },
      {
        "word": "Thú",
        "pos": "adjective",
        "pronunciation": "Thu",
        "color": "#000000",
        "gloss": "exciting"
      },
      {
        "word": "vị",
        "pos": "noun",
        "pronunciation": "vi",
        "color": "#000000",
        "gloss": "fun (as in fun/excitation)"
      },
      {
        "word": "😝",
        "pos": "emoji",
        "pronunciation": "",
        "color": "#000000",
        "gloss": "excited face"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/3561981487324745583.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: en\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: I added vietnamese.",
  "response": {
    "mode": "x_to_vi",
    "translation": "Tôi đã thêm tiếng Việt.",
    "tokens": [
      {
        "word": "Tôi",
        "pos": "pronoun",
        "pronunciation": "toi",
        "color": "#FF0000",
        "gloss": "I"
      },
      {
        "word": "đã",
        "pos": "particle",
        "pronunciation": "da",
        "color": "#0000FF",
        "gloss": "(past tense marker)"
      },
      {
        "word": "thêm",
        "pos": "verb",
        "pronunciation": "them",
        "color": "#00FF00",
        "gloss": "add"
      },
      {
        "word": "tiếng",
        "pos": "noun",
        "pronunciation": "tieng",
        "color": "#FFFF00",
        "gloss": "language"
      },
      {
        "word": "Việt",
        "pos": "proper noun",
        "pronunciation": "Viet",
        "color": "#FF00FF",
        "gloss": "Vietnamese"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/4953287438975737771.json`

```json
{
  "prompt": "Detect the primary language of this text and return ISO 639-1 code only.\nText: Is this vietnamese?",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/5246898907418263447.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: en\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: What will happen if we push new thing?",
  "response": {
    "mode": "x_to_vi",
    "translation": "Điều gì sẽ xảy ra nếu chúng ta thúc đẩy điều mới?",
    "tokens": [
      {
        "word": "Điều",
        "pos": "noun",
        "pronunciation": "Dieu",
        "color": "#FFFFFF",
        "gloss": "thing"
      },
      {
        "word": "gì",
        "pos": "pronoun",
        "pronunciation": "gi",
        "color": "#FFFFFF",
        "gloss": "what"
      },
      {
        "word": "sẽ",
        "pos": "modal",
        "pronunciation": "se",
        "color": "#FFFFFF",
        "gloss": "will"
      },
      {
        "word": "xảy",
        "pos": "verb",
        "pronunciation": "xay",
        "color": "#FFFFFF",
        "gloss": "to happen"
      },
      {
        "word": "ra",
        "pos": "particle",
        "pronunciation": "ra",
        "color": "#FFFFFF",
        "gloss": "out"
      },
      {
        "word": "nếu",
        "pos": "conjunction",
        "pronunciation": "neu",
        "color": "#FFFFFF",
        "gloss": "if"
      },
      {
        "word": "chúng",
        "pos": "pronoun",
        "pronunciation": "chung",
        "color": "#FFFFFF",
        "gloss": "we"
      },
      {
        "word": "ta",
        "pos": "pronoun",
        "pronunciation": "ta",
        "color": "#FFFFFF",
        "gloss": "we"
      },
      {
        "word": "thúc",
        "pos": "verb",
        "pronunciation": "thuc",
        "color": "#FFFFFF",
        "gloss": "to push"
      },
      {
        "word": "đẩy",
        "pos": "verb",
        "pronunciation": "day",
        "color": "#FFFFFF",
        "gloss": "to propel"
      },
      {
        "word": "điều",
        "pos": "noun",
        "pronunciation": "Dieu",
        "color": "#FFFFFF",
        "gloss": "thing"
      },
      {
        "word": "mới",
        "pos": "adjective",
        "pronunciation": "moi",
        "color": "#FFFFFF",
        "gloss": "new"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/5506058269601609728.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: en\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: hello",
  "response": {
    "mode": "x_to_vi",
    "translation": "xin chào",
    "tokens": [
      {
        "word": "xin",
        "pos": "particle",
        "pronunciation": "xin",
        "color": "#000000",
        "gloss": "please"
      },
      {
        "word": "chào",
        "pos": "verb",
        "pronunciation": "chao",
        "color": "#000000",
        "gloss": "greet"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/8923748743980132108.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: zh\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: 可以说是越南语吗",
  "response": {
    "mode": "x_to_vi",
    "translation": "Có thể nói là tiếng Việt không?",
    "tokens": [
      {
        "word": "Có",
        "pos": "verb",
        "pronunciation": "Co",
        "color": "#FFFFFF",
        "gloss": "Can"
      },
      {
        "word": "thể",
        "pos": "noun",
        "pronunciation": "the",
        "color": "#FFFFFF",
        "gloss": "ability"
      },
      {
        "word": "nói",
        "pos": "verb",
        "pronunciation": "noi",
        "color": "#FFFFFF",
        "gloss": "to say"
      },
      {
        "word": "là",
        "pos": "verb",
        "pronunciation": "la",
        "color": "#FFFFFF",
        "gloss": "is"
      },
      {
        "word": "tiếng",
        "pos": "noun",
        "pronunciation": "tieng",
        "color": "#FFFFFF",
        "gloss": "language"
      },
      {
        "word": "Việt",
        "pos": "noun",
        "pronunciation": "Viet",
        "color": "#FFFFFF",
        "gloss": "Vietnamese"
      },
      {
        "word": "không",
        "pos": "adverb",
        "pronunciation": "khong",
        "color": "#FFFFFF",
        "gloss": "not"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/8882863442240351652.json`

```json
{
  "prompt": "Detect the primary language of this text and return ISO 639-1 code only.\nText: hello arabic",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/7980891062860865794.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: all_zh\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: 不客气！圣桑的音乐确实很美妙，你最喜欢他哪一部作品呢？",
  "response": {
    "mode": "x_to_vi",
    "translation": "Không có gì! Âm nhạc của Saint-Saëns thật sự rất tuyệt vời, bạn thích tác phẩm nào nhất của ông?",
    "tokens": [
      {
        "word": "Không",
        "pos": "Đại từ",
        "pronunciation": "Khong",
        "color": "#FF5733",
        "gloss": "No/Not"
      },
      {
        "word": "có",
        "pos": "Động từ",
        "pronunciation": "co",
        "color": "#FF5733",
        "gloss": "to have"
      },
      {
        "word": "gì",
        "pos": "Đại từ",
        "pronunciation": "gi",
        "color": "#FF5733",
        "gloss": "anything"
      },
      {
        "word": "!",
        "pos": "Dấu câu",
        "pronunciation": "",
        "color": "",
        "gloss": ""
      },
      {
        "word": "Âm",
        "pos": "Danh từ",
        "pronunciation": "Am",
        "color": "#FF5733",
        "gloss": "Sound"
      },
      {
        "word": "nhạc",
        "pos": "Danh từ",
        "pronunciation": "nhac",
        "color": "#FF5733",
        "gloss": "Music"
      },
      {
        "word": "của",
        "pos": "Giới từ",
        "pronunciation": "cua",
        "color": "#FF5733",
        "gloss": "of"
      },
      {
        "word": "Saint-Saëns",
        "pos": "Tên riêng",
        "pronunciation": "",
        "color": "",
        "gloss": "Name of person/composer"
      },
      {
        "word": "thật",
        "pos": "Trạng từ",
        "pronunciation": "that",
        "color": "#FF5733",
        "gloss": "really"
      },
      {
        "word": "sự",
        "pos": "Giới từ",
        "pronunciation": "su",
        "color": "#FF5733",
        "gloss": "(indicates noun—adds emphasis)"
      },
      {
        "word": "rất",
        "pos": "Trạng từ",
        "pronunciation": "rat",
        "color": "#FF5733",
        "gloss": "very"
      },
      {
        "word": "tuyệt",
        "pos": "Tính từ",
        "pronunciation": "tuyet",
        "color": "#FF5733",
        "gloss": "wonderful"
      },
      {
        "word": "vời",
        "pos": "Tính từ",
        "pronunciation": "voi",
        "color": "#FF5733",
        "gloss": "(complement to ‘tuyệt’) very good/nice"
      },
      {
        "word": ",",
        "pos": "Dấu câu",
        "pronunciation": "",
        "color": "",
        "gloss": ""
      },
      {
        "word": "bạn",
        "pos": "Đại từ",
        "pronunciation": "ban",
        "color": "#FF5733",
        "gloss": "you"
      },
      {
        "word": "thích",
        "pos": "Động từ",
        "pronunciation": "thich",
        "color": "#FF5733",
        "gloss": "to like"
      },
      {
        "word": "tác",
        "pos": "Danh từ",
        "pronunciation": "tac",
        "color": "#FF5733",
        "gloss": "work"
      },
      {
        "word": "phẩm",
        "pos": "Danh từ",
        "pronunciation": "pham",
        "color": "#FF5733",
        "gloss": "product/item"
      },
      {
        "word": "nào",
        "pos": "Đại từ",
        "pronunciation": "nao",
        "color": "#FF5733",
        "gloss": "which"
      },
      {
        "word": "nhất",
        "pos": "Trạng từ",
        "pronunciation": "nhat",
        "color": "#FF5733",
        "gloss": "most"
      },
      {
        "word": "của",
        "pos": "Giới từ",
        "pronunciation": "cua",
        "color": "#FF5733",
        "gloss": "of"
      },
      {
        "word": "ông",
        "pos": "Đại từ",
        "pronunciation": "ong",
        "color": "#FF5733",
        "gloss": "he/him?"
      },
      {
        "word": "?",
        "pos": "Dấu câu",
        "pronunciation": "",
        "color": "",
        "gloss": ""
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/6913800965774886600.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: en\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: Is this vietnamese?",
  "response": {
    "mode": "x_to_vi",
    "translation": "Đây có phải là tiếng Việt không?",
    "tokens": [
      {
        "word": "Đây",
        "pos": "pronoun",
        "pronunciation": "Day",
        "color": "#000000",
        "gloss": "This"
      },
      {
        "word": "có",
        "pos": "verb",
        "pronunciation": "co",
        "color": "#000000",
        "gloss": "is/has"
      },
      {
        "word": "phải",
        "pos": "particle",
        "pronunciation": "phai",
        "color": "#000000",
        "gloss": "must/should"
      },
      {
        "word": "là",
        "pos": "verb",
        "pronunciation": "la",
        "color": "#000000",
        "gloss": "be"
      },
      {
        "word": "tiếng",
        "pos": "noun",
        "pronunciation": "tieng",
        "color": "#000000",
        "gloss": "language"
      },
      {
        "word": "Việt",
        "pos": "proper noun",
        "pronunciation": "Viet",
        "color": "#000000",
        "gloss": "Vietnamese"
      },
      {
        "word": "không",
        "pos": "adverb",
        "pronunciation": "khong",
        "color": "#000000",
        "gloss": "not"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/8161333509466579133.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nIf input is not Vietnamese, rewrite it into pure Vietnamese first.\nThen analyze the Vietnamese sentence and reply with JSON ONLY per schema: { mode: 'vi_native' | 'x_to_vi', translation: <vietnamese>, tokens: [ { word, pos, pronunciation, gloss } ] }.\nText: can you talk?",
  "response": {
    "mode": "x_to_vi",
    "translation": "Bạn có thể nói không?",
    "tokens": [
      {
        "word": "Bạn",
        "pos": "đại từ",
        "pronunciation": "bạn",
        "gloss": "you"
      },
      {
        "word": "có",
        "pos": "động từ",
        "pronunciation": "có",
        "gloss": "can"
      },
      {
        "word": "thể",
        "pos": "động từ",
        "pronunciation": "thể",
        "gloss": "to be able to"
      },
      {
        "word": "nói",
        "pos": "động từ",
        "pronunciation": "nói",
        "gloss": "talk"
      },
      {
        "word": "không",
        "pos": "phó từ",
        "pronunciation": "không",
        "gloss": "not / question marker"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/7369175828197157130.json`

```json
{
  "prompt": "Detect the primary language of this text and return ISO 639-1 code only.\nText: hello",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/6691655703506100861.json`

```json
{
  "prompt": "Detect the primary language of this text and return ISO 639-1 code only.\nText: be a good man",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/5000207772514560795.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: en\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: What's the meal",
  "response": {
    "mode": "x_to_vi",
    "translation": "Bữa ăn là gì?",
    "tokens": [
      {
        "word": "Bữa",
        "pos": "Noun",
        "pronunciation": "Bua",
        "color": "#FF5733",
        "gloss": "meal"
      },
      {
        "word": "ăn",
        "pos": "Verb",
        "pronunciation": "an",
        "color": "#FFC300",
        "gloss": "eat"
      },
      {
        "word": "là",
        "pos": "Verb",
        "pronunciation": "la",
        "color": "#C70039",
        "gloss": "is"
      },
      {
        "word": "gì",
        "pos": "Pronoun",
        "pronunciation": "gi",
        "color": "#900C3F",
        "gloss": "what?"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/8774823928005436135.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: auto\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: what bubble?",
  "response": {
    "mode": "x_to_vi",
    "translation": "bong bóng nào?",
    "tokens": [
      {
        "word": "bong",
        "pos": "noun",
        "pronunciation": "bong",
        "color": "#FFCC00",
        "gloss": "bubble"
      },
      {
        "word": "bóng",
        "pos": "noun",
        "pronunciation": "bóng",
        "color": "#FFCC00",
        "gloss": "shadow"
      },
      {
        "word": "nào",
        "pos": "pronoun",
        "pronunciation": "nào",
        "color": "#FFCC00",
        "gloss": "which?"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/3011909588621343470.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: all_zh\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: 当然会！我能说一点越南语，不过主要还是中文。如果你对越南语有兴趣，我可以帮你了解一些基本的词汇和短语哦！",
  "response": {
    "mode": "x_to_vi",
    "translation": "Chắc chắn rồi! Tôi có thể nói một chút tiếng Việt, nhưng chủ yếu vẫn là tiếng Trung. Nếu bạn quan tâm đến tiếng Việt, tôi có thể giúp bạn hiểu một số từ vựng và cụm từ cơ bản nhé!",
    "tokens": [
      {
        "word": "Chắc chắn",
        "pos": "phrase",
        "pronunciation": "Chắc chắn",
        "color": "#ffcc00",
        "gloss": "Certainly"
      },
      {
        "word": "rồi",
        "pos": "particle",
        "pronunciation": "rồi",
        "color": "#ffcc00",
        "gloss": "already"
      },
      {
        "word": "Tôi",
        "pos": "pronoun",
        "pronunciation": "Tôi",
        "color": "#ffcc00",
        "gloss": "I"
      },
      {
        "word": "có",
        "pos": "verb",
        "pronunciation": "có",
        "color": "#ffcc00",
        "gloss": "can"
      },
      {
        "word": "thể",
        "pos": "verb",
        "pronunciation": "thể",
        "color": "#ffcc00",
        "gloss": "to be able to"
      },
      {
        "word": "nói",
        "pos": "verb",
        "pronunciation": "nói",
        "color": "#ffcc00",
        "gloss": "speak"
      },
      {
        "word": "một",
        "pos": "numeral",
        "pronunciation": "một",
        "color": "#ffcc00",
        "gloss": "a"
      },
      {
        "word": "chút",
        "pos": "noun",
        "pronunciation": "chút",
        "color": "#ffcc00",
        "gloss": "little"
      },
      {
        "word": "tiếng Việt",
        "pos": "noun",
        "pronunciation": "tiếng Việt",
        "color": "#ffcc00",
        "gloss": "Vietnamese"
      },
      {
        "word": "nhưng",
        "pos": "conjunction",
        "pronunciation": "nhưng",
        "color": "#ffcc00",
        "gloss": "but"
      },
      {
        "word": "chủ yếu",
        "pos": "adverb",
        "pronunciation": "chủ yếu",
        "color": "#ffcc00",
        "gloss": "primarily"
      },
      {
        "word": "vẫn",
        "pos": "adverb",
        "pronunciation": "vẫn",
        "color": "#ffcc00",
        "gloss": "still"
      },
      {
        "word": "là",
        "pos": "verb",
        "pronunciation": "là",
        "color": "#ffcc00",
        "gloss": "is"
      },
      {
        "word": "tiếng Trung",
        "pos": "noun",
        "pronunciation": "tiếng Trung",
        "color": "#ffcc00",
        "gloss": "Chinese"
      },
      {
        "word": "Nếu",
        "pos": "conjunction",
        "pronunciation": "Nếu",
        "color": "#ffcc00",
        "gloss": "If"
      },
      {
        "word": "bạn",
        "pos": "pronoun",
        "pronunciation": "bạn",
        "color": "#ffcc00",
        "gloss": "you"
      },
      {
        "word": "quan tâm",
        "pos": "verb",
        "pronunciation": "quan tâm",
        "color": "#ffcc00",
        "gloss": "interested"
      },
      {
        "word": "đến",
        "pos": "preposition",
        "pronunciation": "đến",
        "color": "#ffcc00",
        "gloss": "to"
      },
      {
        "word": "tiếng Việt",
        "pos": "noun",
        "pronunciation": "tiếng Việt",
        "color": "#ffcc00",
        "gloss": "Vietnamese"
      },
      {
        "word": "tôi",
        "pos": "pronoun",
        "pronunciation": "tôi",
        "color": "#ffcc00",
        "gloss": "I"
      },
      {
        "word": "có",
        "pos": "verb",
        "pronunciation": "có",
        "color": "#ffcc00",
        "gloss": "can"
      },
      {
        "word": "thể",
        "pos": "verb",
        "pronunciation": "thể",
        "color": "#ffcc00",
        "gloss": "to be able to"
      },
      {
        "word": "giúp",
        "pos": "verb",
        "pronunciation": "giúp",
        "color": "#ffcc00",
        "gloss": "help"
      },
      {
        "word": "bạn",
        "pos": "pronoun",
        "pronunciation": "bạn",
        "color": "#ffcc00",
        "gloss": "you"
      },
      {
        "word": "hiểu",
        "pos": "verb",
        "pronunciation": "hiểu",
        "color": "#ffcc00",
        "gloss": "understand"
      },
      {
        "word": "một",
        "pos": "numeral",
        "pronunciation": "một",
        "color": "#ffcc00",
        "gloss": "a"
      },
      {
        "word": "số",
        "pos": "noun",
        "pronunciation": "số",
        "color": "#ffcc00",
        "gloss": "some"
      },
      {
        "word": "từ vựng",
        "pos": "noun",
        "pronunciation": "từ vựng",
        "color": "#ffcc00",
        "gloss": "vocabulary"
      },
      {
        "word": "và",
        "pos": "conjunction",
        "pronunciation": "và",
        "color": "#ffcc00",
        "gloss": "and"
      },
      {
        "word": "cụm từ",
        "pos": "noun",
        "pronunciation": "cụm từ",
        "color": "#ffcc00",
        "gloss": "phrases"
      },
      {
        "word": "cơ bản",
        "pos": "adjective",
        "pronunciation": "cơ bản",
        "color": "#ffcc00",
        "gloss": "basic"
      },
      {
        "word": "nhé",
        "pos": "particle",
        "pronunciation": "nhé",
        "color": "#ffcc00",
        "gloss": "OK"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/2885044105377184530.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: en\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: do you have arabic?",
  "response": {
    "mode": "x_to_vi",
    "translation": "bạn có tiếng Ả Rập không?",
    "tokens": [
      {
        "word": "bạn",
        "pos": "pronoun",
        "pronunciation": "ban",
        "color": "#FF5733",
        "gloss": "you"
      },
      {
        "word": "có",
        "pos": "verb",
        "pronunciation": "co",
        "color": "#33FF57",
        "gloss": "have"
      },
      {
        "word": "tiếng",
        "pos": "noun",
        "pronunciation": "tieng",
        "color": "#3357FF",
        "gloss": "language"
      },
      {
        "word": "Ả",
        "pos": "adjective",
        "pronunciation": "A",
        "color": "#FF33A6",
        "gloss": "Arab"
      },
      {
        "word": "Rập",
        "pos": "noun",
        "pronunciation": "Rap",
        "color": "#FF33D4",
        "gloss": "Arab"
      },
      {
        "word": "không",
        "pos": "particle",
        "pronunciation": "khong",
        "color": "#FFC300",
        "gloss": "not"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/4291319113275322482.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: all_zh\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: 好的，我们开始聊天吧！你最近过得怎么样？",
  "response": {
    "mode": "x_to_vi",
    "translation": "Được rồi, chúng ta bắt đầu nói chuyện nhé! Dạo này bạn thế nào?",
    "tokens": [
      {
        "word": "Được",
        "pos": "verb",
        "pronunciation": "Duoc",
        "color": "#000000",
        "gloss": "okay"
      },
      {
        "word": "rồi",
        "pos": "particle",
        "pronunciation": "roi",
        "color": "#000000",
        "gloss": "already"
      },
      {
        "word": "chúng",
        "pos": "pronoun",
        "pronunciation": "chung",
        "color": "#000000",
        "gloss": "we"
      },
      {
        "word": "ta",
        "pos": "pronoun",
        "pronunciation": "ta",
        "color": "#000000",
        "gloss": "us"
      },
      {
        "word": "bắt",
        "pos": "verb",
        "pronunciation": "bat",
        "color": "#000000",
        "gloss": "to start"
      },
      {
        "word": "đầu",
        "pos": "verb",
        "pronunciation": "dau",
        "color": "#000000",
        "gloss": "to begin"
      },
      {
        "word": "nói",
        "pos": "verb",
        "pronunciation": "noi",
        "color": "#000000",
        "gloss": "to speak"
      },
      {
        "word": "chuyện",
        "pos": "noun",
        "pronunciation": "chuyen",
        "color": "#000000",
        "gloss": "story"
      },
      {
        "word": "nhé",
        "pos": "particle",
        "pronunciation": "nhe",
        "color": "#000000",
        "gloss": "okay"
      },
      {
        "word": "Dạo",
        "pos": "noun",
        "pronunciation": "Dao",
        "color": "#000000",
        "gloss": "time period"
      },
      {
        "word": "này",
        "pos": "pronoun",
        "pronunciation": "nay",
        "color": "#000000",
        "gloss": "this"
      },
      {
        "word": "bạn",
        "pos": "noun",
        "pronunciation": "ban",
        "color": "#000000",
        "gloss": "friend"
      },
      {
        "word": "thế",
        "pos": "adverb",
        "pronunciation": "the",
        "color": "#000000",
        "gloss": "how"
      },
      {
        "word": "nào",
        "pos": "pronoun",
        "pronunciation": "nao",
        "color": "#000000",
        "gloss": "which"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/8842726409090541245.json`

```json
{
  "prompt": "Detect the primary language of this text and return ISO 639-1 code only.\nText: are you okay?",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/5188258439764650232.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: all_zh\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: 你好呀！有什么我可以帮助你的吗？",
  "response": {
    "mode": "x_to_vi",
    "translation": "Chào bạn! Có gì tôi có thể giúp bạn không?",
    "tokens": [
      {
        "word": "Chào",
        "pos": "verb",
        "pronunciation": "Chao",
        "color": "#FF5733",
        "gloss": "greet"
      },
      {
        "word": "bạn",
        "pos": "noun",
        "pronunciation": "ban",
        "color": "#33FF57",
        "gloss": "you"
      },
      {
        "word": "Có",
        "pos": "verb",
        "pronunciation": "Co",
        "color": "#3357FF",
        "gloss": "there is"
      },
      {
        "word": "gì",
        "pos": "pronoun",
        "pronunciation": "gi",
        "color": "#FF33A1",
        "gloss": "what"
      },
      {
        "word": "tôi",
        "pos": "pronoun",
        "pronunciation": "toi",
        "color": "#F1C40F",
        "gloss": "I"
      },
      {
        "word": "có",
        "pos": "verb",
        "pronunciation": "co",
        "color": "#AF7AC5",
        "gloss": "can"
      },
      {
        "word": "thể",
        "pos": "verb",
        "pronunciation": "the",
        "color": "#E67E22",
        "gloss": "to be able to"
      },
      {
        "word": "giúp",
        "pos": "verb",
        "pronunciation": "giup",
        "color": "#16A085",
        "gloss": "help"
      },
      {
        "word": "bạn",
        "pos": "noun",
        "pronunciation": "ban",
        "color": "#33FF57",
        "gloss": "you"
      },
      {
        "word": "không",
        "pos": "particle",
        "pronunciation": "khong",
        "color": "#E74C3C",
        "gloss": "not"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/1843378738326145245.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: zh\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: 那我们现在开始聊天吧",
  "response": {
    "mode": "x_to_vi",
    "translation": "Vậy bây giờ chúng ta bắt đầu trò chuyện nhé",
    "tokens": [
      {
        "word": "Vậy",
        "pos": "conjunction",
        "pronunciation": "Vay",
        "color": "#FF5733",
        "gloss": "So"
      },
      {
        "word": "bây",
        "pos": "adverb",
        "pronunciation": "bay",
        "color": "#33FF57",
        "gloss": "now"
      },
      {
        "word": "giờ",
        "pos": "noun",
        "pronunciation": "gio",
        "color": "#33A1FF",
        "gloss": "hour"
      },
      {
        "word": "chúng",
        "pos": "pronoun",
        "pronunciation": "chung",
        "color": "#FF33A1",
        "gloss": "we"
      },
      {
        "word": "ta",
        "pos": "pronoun",
        "pronunciation": "ta",
        "color": "#A133FF",
        "gloss": "I"
      },
      {
        "word": "bắt",
        "pos": "verb",
        "pronunciation": "bat",
        "color": "#FFC300",
        "gloss": "start"
      },
      {
        "word": "đầu",
        "pos": "verb",
        "pronunciation": "dau",
        "color": "#FF33C4",
        "gloss": "begin"
      },
      {
        "word": "trò",
        "pos": "noun",
        "pronunciation": "tro",
        "color": "#FF5733",
        "gloss": "game"
      },
      {
        "word": "chuyện",
        "pos": "noun",
        "pronunciation": "chuyen",
        "color": "#33FF57",
        "gloss": "talk"
      },
      {
        "word": "nhé",
        "pos": "particle",
        "pronunciation": "nhe",
        "color": "#FF33A1",
        "gloss": "let's"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/6078502664378384662.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: ko\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: 감사합니다.",
  "response": {
    "mode": "x_to_vi",
    "translation": "Cảm ơn.",
    "tokens": [
      {
        "word": "Cảm",
        "pos": "verb",
        "pronunciation": "cam",
        "color": "#000000",
        "gloss": "feel"
      },
      {
        "word": "ơn",
        "pos": "noun",
        "pronunciation": "on",
        "color": "#000000",
        "gloss": "grace"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/3906244258790510835.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: auto\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: 通知のこと？わかりません",
  "response": {
    "mode": "x_to_vi",
    "translation": "Thông tin về việc thông báo? Tôi không biết.",
    "tokens": [
      {
        "word": "Thông tin",
        "pos": "noun",
        "pronunciation": "Thong tin",
        "color": "#000000",
        "gloss": "information"
      },
      {
        "word": "về",
        "pos": "preposition",
        "pronunciation": "ve",
        "color": "#000000",
        "gloss": "about"
      },
      {
        "word": "việc",
        "pos": "noun",
        "pronunciation": "viec",
        "color": "#000000",
        "gloss": "matter"
      },
      {
        "word": "thông báo",
        "pos": "noun",
        "pronunciation": "thong bao",
        "color": "#000000",
        "gloss": "notification"
      },
      {
        "word": "?",
        "pos": "punctuation",
        "pronunciation": "",
        "color": "#000000",
        "gloss": ""
      },
      {
        "word": "Tôi",
        "pos": "pronoun",
        "pronunciation": "Toi",
        "color": "#000000",
        "gloss": "I"
      },
      {
        "word": "không",
        "pos": "adverb",
        "pronunciation": "khong",
        "color": "#000000",
        "gloss": "not"
      },
      {
        "word": "biết",
        "pos": "verb",
        "pronunciation": "biet",
        "color": "#000000",
        "gloss": "know"
      },
      {
        "word": ".",
        "pos": "punctuation",
        "pronunciation": "",
        "color": "#000000",
        "gloss": ""
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/6964661930420295905.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: en\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: How about I say a very long sentecne? Can you do the same thing for me?",
  "response": {
    "mode": "x_to_vi",
    "translation": "Thế nào nếu tôi nói một câu rất dài? Bạn có thể làm điều tương tự cho tôi không?",
    "tokens": [
      {
        "word": "Thế",
        "pos": "adverb",
        "pronunciation": "the",
        "color": "#000000",
        "gloss": "how"
      },
      {
        "word": "nào",
        "pos": "adverb",
        "pronunciation": "nao",
        "color": "#000000",
        "gloss": "about"
      },
      {
        "word": "nếu",
        "pos": "conjunction",
        "pronunciation": "neu",
        "color": "#000000",
        "gloss": "if"
      },
      {
        "word": "tôi",
        "pos": "pronoun",
        "pronunciation": "toi",
        "color": "#000000",
        "gloss": "I"
      },
      {
        "word": "nói",
        "pos": "verb",
        "pronunciation": "noi",
        "color": "#000000",
        "gloss": "say"
      },
      {
        "word": "một",
        "pos": "numeral",
        "pronunciation": "mot",
        "color": "#000000",
        "gloss": "a"
      },
      {
        "word": "câu",
        "pos": "noun",
        "pronunciation": "cau",
        "color": "#000000",
        "gloss": "sentence"
      },
      {
        "word": "rất",
        "pos": "adverb",
        "pronunciation": "rat",
        "color": "#000000",
        "gloss": "very"
      },
      {
        "word": "dài",
        "pos": "adjective",
        "pronunciation": "dai",
        "color": "#000000",
        "gloss": "long"
      },
      {
        "word": "Bạn",
        "pos": "pronoun",
        "pronunciation": "ban",
        "color": "#000000",
        "gloss": "you"
      },
      {
        "word": "có",
        "pos": "verb",
        "pronunciation": "co",
        "color": "#000000",
        "gloss": "can"
      },
      {
        "word": "thể",
        "pos": "verb",
        "pronunciation": "the",
        "color": "#000000",
        "gloss": "do"
      },
      {
        "word": "làm",
        "pos": "verb",
        "pronunciation": "lam",
        "color": "#000000",
        "gloss": "do"
      },
      {
        "word": "điều",
        "pos": "noun",
        "pronunciation": "dieul",
        "color": "#000000",
        "gloss": "thing"
      },
      {
        "word": "tương",
        "pos": "adjective",
        "pronunciation": "tuong",
        "color": "#000000",
        "gloss": "similar"
      },
      {
        "word": "tự",
        "pos": "adverb",
        "pronunciation": "tu",
        "color": "#000000",
        "gloss": "same"
      },
      {
        "word": "cho",
        "pos": "preposition",
        "pronunciation": "cho",
        "color": "#000000",
        "gloss": "for"
      },
      {
        "word": "tôi",
        "pos": "pronoun",
        "pronunciation": "toi",
        "color": "#000000",
        "gloss": "me"
      },
      {
        "word": "không",
        "pos": "adverb",
        "pronunciation": "khong",
        "color": "#000000",
        "gloss": "not"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/2903271945674331701.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: en\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: what do you think?",
  "response": {
    "mode": "x_to_vi",
    "translation": "Bạn nghĩ sao?",
    "tokens": [
      {
        "word": "Bạn",
        "pos": "pronoun",
        "pronunciation": "Ban",
        "color": "#ffeb3b",
        "gloss": "You"
      },
      {
        "word": "nghĩ",
        "pos": "verb",
        "pronunciation": "nghi",
        "color": "#4caf50",
        "gloss": "think"
      },
      {
        "word": "sao",
        "pos": "adverb",
        "pronunciation": "sao",
        "color": "#2196f3",
        "gloss": "how"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/2372626441524814016.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: en\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: be a good man",
  "response": {
    "mode": "x_to_vi",
    "translation": "Hãy trở thành một người tốt",
    "tokens": [
      {
        "word": "Hãy",
        "pos": "adverb",
        "pronunciation": "hay",
        "color": "#ffcc00",
        "gloss": "Please"
      },
      {
        "word": "trở",
        "pos": "verb",
        "pronunciation": "tro",
        "color": "#ffcc00",
        "gloss": "become"
      },
      {
        "word": "thành",
        "pos": "verb",
        "pronunciation": "thanh",
        "color": "#ffcc00",
        "gloss": "become"
      },
      {
        "word": "một",
        "pos": "numeral",
        "pronunciation": "mot",
        "color": "#ffcc00",
        "gloss": "one/a"
      },
      {
        "word": "người",
        "pos": "noun",
        "pronunciation": "nguoi",
        "color": "#ffcc00",
        "gloss": "person"
      },
      {
        "word": "tốt",
        "pos": "adjective",
        "pronunciation": "tot",
        "color": "#ffcc00",
        "gloss": "good"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/1449605457520709011.json`

```json
{
  "prompt": "Detect the primary language of this text and return ISO 639-1 code only.\nText: I added vietnamese.",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/5067269969050234554.json`

```json
{
  "prompt": "Detect the primary language of this text and return ISO 639-1 code only.\nText: 說一點中文",
  "response": {
    "language_code": "zh"
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/5767757068417090974.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: zh\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: 吃饭了吗?吃饭了吗?Hello",
  "response": {
    "mode": "x_to_vi",
    "translation": "Ăn cơm chưa? Ăn cơm chưa? Xin chào",
    "tokens": [
      {
        "word": "Ăn",
        "pos": "verb",
        "pronunciation": "An",
        "color": "#000000",
        "gloss": "to eat"
      },
      {
        "word": "cơm",
        "pos": "noun",
        "pronunciation": "com",
        "color": "#000000",
        "gloss": "rice/meal"
      },
      {
        "word": "chưa",
        "pos": "adverb",
        "pronunciation": "chua",
        "color": "#000000",
        "gloss": "not yet"
      },
      {
        "word": "?",
        "pos": "punctuation",
        "pronunciation": "",
        "color": "#000000",
        "gloss": "question mark"
      },
      {
        "word": "Ăn",
        "pos": "verb",
        "pronunciation": "An",
        "color": "#000000",
        "gloss": "to eat"
      },
      {
        "word": "cơm",
        "pos": "noun",
        "pronunciation": "com",
        "color": "#000000",
        "gloss": "rice/meal"
      },
      {
        "word": "chưa",
        "pos": "adverb",
        "pronunciation": "chua",
        "color": "#000000",
        "gloss": "not yet"
      },
      {
        "word": "?",
        "pos": "punctuation",
        "pronunciation": "",
        "color": "#000000",
        "gloss": "question mark"
      },
      {
        "word": "Xin",
        "pos": "verb",
        "pronunciation": "Xin",
        "color": "#000000",
        "gloss": "to request/please"
      },
      {
        "word": "chào",
        "pos": "noun",
        "pronunciation": "chao",
        "color": "#000000",
        "gloss": "greet/hello"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/5322828569693499731.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: auto\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: @lachlan Owner",
  "response": {
    "mode": "x_to_vi",
    "translation": "@lachlan Chủ sở hữu",
    "tokens": [
      {
        "word": "@lachlan",
        "pos": "Noun",
        "pronunciation": "@lachlan",
        "color": "#000000",
        "gloss": "username"
      },
      {
        "word": "Chủ",
        "pos": "Noun",
        "pronunciation": "Chu",
        "color": "#000000",
        "gloss": "owner"
      },
      {
        "word": "sở hữu",
        "pos": "Verb",
        "pronunciation": "so huu",
        "color": "#000000",
        "gloss": "to own"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/8701873266745793862.json`

```json
{
  "prompt": "Detect the primary language of this text and return ISO 639-1 code only.\nText: hello",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/6877259133089834275.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: en\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: hello arabic",
  "response": {
    "mode": "x_to_vi",
    "translation": "xin chào tiếng Ả Rập",
    "tokens": [
      {
        "word": "xin",
        "pos": "particle",
        "pronunciation": "xin",
        "color": "#000000",
        "gloss": "please"
      },
      {
        "word": "chào",
        "pos": "verb",
        "pronunciation": "chao",
        "color": "#000000",
        "gloss": "greet"
      },
      {
        "word": "tiếng",
        "pos": "noun",
        "pronunciation": "tieng",
        "color": "#000000",
        "gloss": "language"
      },
      {
        "word": "Ả",
        "pos": "noun",
        "pronunciation": "A",
        "color": "#000000",
        "gloss": "Arabic"
      },
      {
        "word": "Rập",
        "pos": "noun",
        "pronunciation": "Rap",
        "color": "#000000",
        "gloss": "Arab"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/3912557848594425903.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nIf input is not Vietnamese, rewrite it into pure Vietnamese first.\nThen analyze the Vietnamese sentence and reply with JSON ONLY per schema: { mode: 'vi_native' | 'x_to_vi', translation: <vietnamese>, tokens: [ { word, pos, pronunciation, gloss } ] }.\nText: are you a man",
  "response": {
    "mode": "x_to_vi",
    "translation": "bạn có phải là đàn ông không",
    "tokens": [
      {
        "word": "bạn",
        "pos": "pronoun",
        "pronunciation": "bạn",
        "gloss": "you"
      },
      {
        "word": "có",
        "pos": "verb",
        "pronunciation": "có",
        "gloss": "have"
      },
      {
        "word": "phải",
        "pos": "verb",
        "pronunciation": "phải",
        "gloss": "must/be"
      },
      {
        "word": "là",
        "pos": "verb",
        "pronunciation": "là",
        "gloss": "to be"
      },
      {
        "word": "đàn",
        "pos": "noun",
        "pronunciation": "đàn",
        "gloss": "man"
      },
      {
        "word": "ông",
        "pos": "noun",
        "pronunciation": "ông",
        "gloss": "male/husband"
      },
      {
        "word": "không",
        "pos": "particle",
        "pronunciation": "không",
        "gloss": "not/particle for yes-no question"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/2266139648130470730.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: en\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: hello",
  "response": {
    "mode": "x_to_vi",
    "translation": "xin chào",
    "tokens": [
      {
        "word": "xin",
        "pos": "adv",
        "pronunciation": "xin",
        "color": "#000000",
        "gloss": "please"
      },
      {
        "word": "chào",
        "pos": "verb",
        "pronunciation": "chao",
        "color": "#000000",
        "gloss": "greet"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/3177694125307814984.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: en\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: Let me post something",
  "response": {
    "mode": "x_to_vi",
    "translation": "Để tôi đăng một cái gì đó",
    "tokens": [
      {
        "word": "Để",
        "pos": "preposition",
        "pronunciation": "De",
        "color": "#000000",
        "gloss": "to let"
      },
      {
        "word": "tôi",
        "pos": "pronoun",
        "pronunciation": "toi",
        "color": "#000000",
        "gloss": "I"
      },
      {
        "word": "đăng",
        "pos": "verb",
        "pronunciation": "dang",
        "color": "#000000",
        "gloss": "to post"
      },
      {
        "word": "một",
        "pos": "numeral",
        "pronunciation": "mot",
        "color": "#000000",
        "gloss": "a/one"
      },
      {
        "word": "cái",
        "pos": "classifier",
        "pronunciation": "cai",
        "color": "#000000",
        "gloss": "classifier for objects"
      },
      {
        "word": "gì",
        "pos": "pronoun",
        "pronunciation": "gi",
        "color": "#000000",
        "gloss": "what"
      },
      {
        "word": "đó",
        "pos": "demonstrative",
        "pronunciation": "do",
        "color": "#000000",
        "gloss": "that"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/7508744840128650200.json`

```json
{
  "prompt": "Detect the primary language of this text and return ISO 639-1 code only.\nText: good night",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/8892519115674030139.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: zh\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: 当然可以，我可以用越南语和你交流！有什么特别想知道的吗？",
  "response": {
    "mode": "x_to_vi",
    "translation": "Đương nhiên rồi, tôi có thể giao tiếp với bạn bằng tiếng Việt! Có điều gì đặc biệt bạn muốn biết không?",
    "tokens": [
      {
        "word": "Đương nhiên",
        "pos": "adv.",
        "pronunciation": "duong-nhien",
        "color": "#000000",
        "gloss": "Of course"
      },
      {
        "word": "rồi",
        "pos": "part.",
        "pronunciation": "roi",
        "color": "#000000",
        "gloss": "(modal particle indicating completeness)"
      },
      {
        "word": "tôi",
        "pos": "pron.",
        "pronunciation": "toi",
        "color": "#000000",
        "gloss": "I"
      },
      {
        "word": "có",
        "pos": "v.",
        "pronunciation": "co",
        "color": "#000000",
        "gloss": "can"
      },
      {
        "word": "thể",
        "pos": "v.",
        "pronunciation": "the",
        "color": "#000000",
        "gloss": "to be able to"
      },
      {
        "word": "giao tiếp",
        "pos": "v.",
        "pronunciation": "giao-tiep",
        "color": "#000000",
        "gloss": "communicate"
      },
      {
        "word": "với",
        "pos": "prep.",
        "pronunciation": "voi",
        "color": "#000000",
        "gloss": "with"
      },
      {
        "word": "bạn",
        "pos": "pron.",
        "pronunciation": "ban",
        "color": "#000000",
        "gloss": "you"
      },
      {
        "word": "bằng",
        "pos": "prep.",
        "pronunciation": "bang",
        "color": "#000000",
        "gloss": "by"
      },
      {
        "word": "tiếng",
        "pos": "n.",
        "pronunciation": "tieng",
        "color": "#000000",
        "gloss": "language"
      },
      {
        "word": "Việt",
        "pos": "adj.",
        "pronunciation": "Viet",
        "color": "#000000",
        "gloss": "Vietnamese"
      },
      {
        "word": "Có",
        "pos": "v.",
        "pronunciation": "Co",
        "color": "#000000",
        "gloss": "Is there"
      },
      {
        "word": "điều",
        "pos": "n.",
        "pronunciation": "dieu",
        "color": "#000000",
        "gloss": "thing"
      },
      {
        "word": "gì",
        "pos": "pron.",
        "pronunciation": "gi",
        "color": "#000000",
        "gloss": "what"
      },
      {
        "word": "đặc biệt",
        "pos": "adj.",
        "pronunciation": "dac-biet",
        "color": "#000000",
        "gloss": "special"
      },
      {
        "word": "bạn",
        "pos": "pron.",
        "pronunciation": "ban",
        "color": "#000000",
        "gloss": "you"
      },
      {
        "word": "muốn",
        "pos": "v.",
        "pronunciation": "muon",
        "color": "#000000",
        "gloss": "want"
      },
      {
        "word": "biết",
        "pos": "v.",
        "pronunciation": "biet",
        "color": "#000000",
        "gloss": "to know"
      },
      {
        "word": "không",
        "pos": "part.",
        "pronunciation": "khong",
        "color": "#000000",
        "gloss": "(negative particle)"
      },
      {
        "word": "?",
        "pos": "punct.",
        "pronunciation": "",
        "color": "#000000",
        "gloss": ""
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/261134183238456202.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: fr\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: Et au revoir pour moi.",
  "response": {
    "mode": "x_to_vi",
    "translation": "Và tạm biệt cho tôi.",
    "tokens": [
      {
        "word": "Và",
        "pos": "conjunction",
        "pronunciation": "Va",
        "color": "#000000",
        "gloss": "And"
      },
      {
        "word": "tạm",
        "pos": "adverb",
        "pronunciation": "tam",
        "color": "#000000",
        "gloss": "temporarily"
      },
      {
        "word": "biệt",
        "pos": "verb",
        "pronunciation": "biet",
        "color": "#000000",
        "gloss": "say goodbye"
      },
      {
        "word": "cho",
        "pos": "preposition",
        "pronunciation": "cho",
        "color": "#000000",
        "gloss": "for"
      },
      {
        "word": "tôi",
        "pos": "pronoun",
        "pronunciation": "toi",
        "color": "#000000",
        "gloss": "me"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/1805850688532462144.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: en\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: What meal are you asking about? Are you looking for breakfast, lunch, or dinner ideas?",
  "response": {
    "mode": "x_to_vi",
    "translation": "Bạn đang hỏi về món ăn nào? Bạn đang tìm ý tưởng cho bữa sáng, bữa trưa hoặc bữa tối?",
    "tokens": [
      {
        "word": "Bạn",
        "pos": "pronoun",
        "pronunciation": "Ban",
        "color": "#000000",
        "gloss": "You"
      },
      {
        "word": "đang",
        "pos": "verb",
        "pronunciation": "dang",
        "color": "#000000",
        "gloss": "are"
      },
      {
        "word": "hỏi",
        "pos": "verb",
        "pronunciation": "hoi",
        "color": "#000000",
        "gloss": "ask"
      },
      {
        "word": "về",
        "pos": "preposition",
        "pronunciation": "ve",
        "color": "#000000",
        "gloss": "about"
      },
      {
        "word": "món",
        "pos": "noun",
        "pronunciation": "mon",
        "color": "#000000",
        "gloss": "meal/dish"
      },
      {
        "word": "ăn",
        "pos": "verb",
        "pronunciation": "an",
        "color": "#000000",
        "gloss": "eat"
      },
      {
        "word": "nào",
        "pos": "pronoun",
        "pronunciation": "nao",
        "color": "#000000",
        "gloss": "which"
      },
      {
        "word": "Bạn",
        "pos": "pronoun",
        "pronunciation": "Ban",
        "color": "#000000",
        "gloss": "You"
      },
      {
        "word": "đang",
        "pos": "verb",
        "pronunciation": "dang",
        "color": "#000000",
        "gloss": "are"
      },
      {
        "word": "tìm",
        "pos": "verb",
        "pronunciation": "tim",
        "color": "#000000",
        "gloss": "looking for"
      },
      {
        "word": "ý",
        "pos": "noun",
        "pronunciation": "y",
        "color": "#000000",
        "gloss": "idea"
      },
      {
        "word": "tưởng",
        "pos": "noun",
        "pronunciation": "tuong",
        "color": "#000000",
        "gloss": "thought"
      },
      {
        "word": "cho",
        "pos": "preposition",
        "pronunciation": "cho",
        "color": "#000000",
        "gloss": "for"
      },
      {
        "word": "bữa",
        "pos": "noun",
        "pronunciation": "bua",
        "color": "#000000",
        "gloss": "meal"
      },
      {
        "word": "sáng",
        "pos": "noun",
        "pronunciation": "sang",
        "color": "#000000",
        "gloss": "breakfast"
      },
      {
        "word": ",",
        "pos": "punctuation",
        "pronunciation": ",",
        "color": "#000000",
        "gloss": "."
      },
      {
        "word": "bữa",
        "pos": "noun",
        "pronunciation": "bua",
        "color": "#000000",
        "gloss": "meal"
      },
      {
        "word": "trưa",
        "pos": "noun",
        "pronunciation": "trua",
        "color": "#000000",
        "gloss": "lunch"
      },
      {
        "word": "hoặc",
        "pos": "conjunction",
        "pronunciation": "hoac",
        "color": "#000000",
        "gloss": "or"
      },
      {
        "word": "bữa",
        "pos": "noun",
        "pronunciation": "bua",
        "color": "#000000",
        "gloss": "meal"
      },
      {
        "word": "tối",
        "pos": "noun",
        "pronunciation": "toi",
        "color": "#000000",
        "gloss": "dinner"
      },
      {
        "word": "?",
        "pos": "punctuation",
        "pronunciation": "?",
        "color": "#000000",
        "gloss": "?"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/4346151798181544994.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: en\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: good night",
  "response": {
    "mode": "x_to_vi",
    "translation": "chúc ngủ ngon",
    "tokens": [
      {
        "word": "chúc",
        "pos": "verb",
        "pronunciation": "chuc",
        "color": "#FF5733",
        "gloss": "wish"
      },
      {
        "word": "ngủ",
        "pos": "verb",
        "pronunciation": "ngu",
        "color": "#FF5733",
        "gloss": "sleep"
      },
      {
        "word": "ngon",
        "pos": "adjective",
        "pronunciation": "ngon",
        "color": "#FF5733",
        "gloss": "good"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/2626931529326509385.json`

```json
{
  "prompt": "Detect the primary language of this text and return ISO 639-1 code only.\nText: what do you think?",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/970433761433405483.json`

```json
{
  "prompt": "Detect the primary language of this text and return ISO 639-1 code only.\nText: I forwarded this post. 非非非非你还在吗没有没有我先我先那个啥",
  "response": {
    "language_code": "zh"
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/4555696097220843152.json`

```json
{
  "prompt": "Detect the primary language of this text and return ISO 639-1 code only.\nText: This is my first message on EchoMind! Exciting😝",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/5916209905980400329.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: en\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: hello",
  "response": {
    "mode": "x_to_vi",
    "translation": "xin chào",
    "tokens": [
      {
        "word": "xin",
        "pos": "adv",
        "pronunciation": "xin",
        "color": "#FF5733",
        "gloss": "please"
      },
      {
        "word": "chào",
        "pos": "v",
        "pronunciation": "chao",
        "color": "#FF5733",
        "gloss": "hello"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/6261578216809778623.json`

```json
{
  "prompt": "Detect the primary language of this text and return ISO 639-1 code only.\nText: What's the meal",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/6493708875435245517.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nIf input is not Vietnamese, rewrite it into pure Vietnamese first.\nThen analyze the Vietnamese sentence and reply with JSON ONLY per schema: { mode: 'vi_native' | 'x_to_vi', translation: <vietnamese>, tokens: [ { word, pos, pronunciation, gloss } ] }.\nText: hello arabic",
  "response": {
    "mode": "x_to_vi",
    "translation": "xin chào tiếng Ả Rập",
    "tokens": [
      {
        "word": "xin",
        "pos": "adverb",
        "pronunciation": "sin",
        "gloss": "a polite expression used before a request or greeting"
      },
      {
        "word": "chào",
        "pos": "verb",
        "pronunciation": "chao",
        "gloss": "to greet"
      },
      {
        "word": "tiếng",
        "pos": "noun",
        "pronunciation": "tiếng",
        "gloss": "language or sound"
      },
      {
        "word": "Ả Rập",
        "pos": "noun",
        "pronunciation": "a rap",
        "gloss": "Arabic (referring to the language or people)"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/220063012600955466.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: auto\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: can you see the msg bubble？",
  "response": {
    "mode": "x_to_vi",
    "translation": "Bạn có thấy bong bóng tin nhắn không?",
    "tokens": [
      {
        "word": "Bạn",
        "pos": "pronoun",
        "pronunciation": "ban",
        "color": "#000000",
        "gloss": "You"
      },
      {
        "word": "có",
        "pos": "verb",
        "pronunciation": "co",
        "color": "#000000",
        "gloss": "can"
      },
      {
        "word": "thấy",
        "pos": "verb",
        "pronunciation": "thay",
        "color": "#000000",
        "gloss": "see"
      },
      {
        "word": "bong",
        "pos": "noun",
        "pronunciation": "bong",
        "color": "#000000",
        "gloss": "bubble"
      },
      {
        "word": "bóng",
        "pos": "noun",
        "pronunciation": "bong",
        "color": "#000000",
        "gloss": "bubble (repeated for context)"
      },
      {
        "word": "tin",
        "pos": "noun",
        "pronunciation": "tin",
        "color": "#000000",
        "gloss": "message"
      },
      {
        "word": "nhắn",
        "pos": "verb",
        "pronunciation": "nhan",
        "color": "#000000",
        "gloss": "to message"
      },
      {
        "word": "không",
        "pos": "particle",
        "pronunciation": "khong",
        "color": "#000000",
        "gloss": "not (question particle)?"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/3972646381730932899.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: all_zh\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: 当然会！我能说一点越南语，不过主要还是中文。如果你对越南语有兴趣，我可以帮你了解一些基本的词汇和短语哦！",
  "response": {
    "mode": "x_to_vi",
    "translation": "Đương nhiên rồi! Tôi có thể nói một chút tiếng Việt, nhưng chủ yếu vẫn là tiếng Trung. Nếu bạn quan tâm đến tiếng Việt, tôi có thể giúp bạn hiểu một số từ vựng và cụm từ cơ bản!",
    "tokens": [
      {
        "word": "Đương nhiên",
        "pos": "phrase",
        "pronunciation": "duong-nhien",
        "color": "#ffcc00",
        "gloss": "Of course"
      },
      {
        "word": "rồi",
        "pos": "particle",
        "pronunciation": "roi",
        "color": "#cccccc",
        "gloss": "already"
      },
      {
        "word": "Tôi",
        "pos": "pronoun",
        "pronunciation": "toi",
        "color": "#cccccc",
        "gloss": "I"
      },
      {
        "word": "có",
        "pos": "verb",
        "pronunciation": "co",
        "color": "#cccccc",
        "gloss": "can"
      },
      {
        "word": "thể",
        "pos": "verb",
        "pronunciation": "the",
        "color": "#cccccc",
        "gloss": "to be able to"
      },
      {
        "word": "nói",
        "pos": "verb",
        "pronunciation": "noi",
        "color": "#cccccc",
        "gloss": "speak"
      },
      {
        "word": "một",
        "pos": "numeral",
        "pronunciation": "mot",
        "color": "#cccccc",
        "gloss": "a/little"
      },
      {
        "word": "chút",
        "pos": "noun",
        "pronunciation": "chut",
        "color": "#cccccc",
        "gloss": "bit"
      },
      {
        "word": "tiếng",
        "pos": "noun",
        "pronunciation": "tieng",
        "color": "#cccccc",
        "gloss": "language"
      },
      {
        "word": "Việt",
        "pos": "noun",
        "pronunciation": "Viet",
        "color": "#cccccc",
        "gloss": "Vietnamese"
      },
      {
        "word": "nhưng",
        "pos": "conjunction",
        "pronunciation": "nhung",
        "color": "#cccccc",
        "gloss": "but"
      },
      {
        "word": "chủ yếu",
        "pos": "adverb",
        "pronunciation": "chu-yeu",
        "color": "#cccccc",
        "gloss": "mainly"
      },
      {
        "word": "vẫn",
        "pos": "adverb",
        "pronunciation": "van",
        "color": "#cccccc",
        "gloss": "still"
      },
      {
        "word": "là",
        "pos": "verb",
        "pronunciation": "la",
        "color": "#cccccc",
        "gloss": "is"
      },
      {
        "word": "tiếng",
        "pos": "noun",
        "pronunciation": "tieng",
        "color": "#cccccc",
        "gloss": "language"
      },
      {
        "word": "Trung",
        "pos": "noun",
        "pronunciation": "Trung",
        "color": "#cccccc",
        "gloss": "Chinese"
      },
      {
        "word": "Nếu",
        "pos": "conjunction",
        "pronunciation": "neu",
        "color": "#cccccc",
        "gloss": "If"
      },
      {
        "word": "bạn",
        "pos": "pronoun",
        "pronunciation": "ban",
        "color": "#cccccc",
        "gloss": "you"
      },
      {
        "word": "quan tâm",
        "pos": "verb",
        "pronunciation": "quan-tam",
        "color": "#cccccc",
        "gloss": "interested"
      },
      {
        "word": "đến",
        "pos": "preposition",
        "pronunciation": "den",
        "color": "#cccccc",
        "gloss": "to"
      },
      {
        "word": "tiếng",
        "pos": "noun",
        "pronunciation": "tieng",
        "color": "#cccccc",
        "gloss": "language"
      },
      {
        "word": "Việt",
        "pos": "noun",
        "pronunciation": "Viet",
        "color": "#cccccc",
        "gloss": "Vietnamese"
      },
      {
        "word": "tôi",
        "pos": "pronoun",
        "pronunciation": "toi",
        "color": "#cccccc",
        "gloss": "I"
      },
      {
        "word": "có",
        "pos": "verb",
        "pronunciation": "co",
        "color": "#cccccc",
        "gloss": "can"
      },
      {
        "word": "thể",
        "pos": "verb",
        "pronunciation": "the",
        "color": "#cccccc",
        "gloss": "to be able to"
      },
      {
        "word": "giúp",
        "pos": "verb",
        "pronunciation": "giup",
        "color": "#cccccc",
        "gloss": "help"
      },
      {
        "word": "bạn",
        "pos": "pronoun",
        "pronunciation": "ban",
        "color": "#cccccc",
        "gloss": "you"
      },
      {
        "word": "hiểu",
        "pos": "verb",
        "pronunciation": "hieu",
        "color": "#cccccc",
        "gloss": "understand"
      },
      {
        "word": "một số",
        "pos": "numeral",
        "pronunciation": "mot-so",
        "color": "#cccccc",
        "gloss": "some"
      },
      {
        "word": "từ vựng",
        "pos": "noun",
        "pronunciation": "tu-vung",
        "color": "#cccccc",
        "gloss": "vocabulary"
      },
      {
        "word": "và",
        "pos": "conjunction",
        "pronunciation": "va",
        "color": "#cccccc",
        "gloss": "and"
      },
      {
        "word": "cụm từ",
        "pos": "noun",
        "pronunciation": "cum-tu",
        "color": "#cccccc",
        "gloss": "phrases"
      },
      {
        "word": "cơ bản",
        "pos": "adjective",
        "pronunciation": "co-ban",
        "color": "#cccccc",
        "gloss": "basic"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/4646535914977966941.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: auto\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: たぶんだけどmiaoがオンラインになった瞬間に右下にmiaoのアイコンが出てきた気がする",
  "response": {
    "mode": "x_to_vi",
    "translation": "Có lẽ nhưng mà vào khoảnh khắc miao trực tuyến thì tôi cảm thấy ở góc dưới bên phải đã xuất hiện biểu tượng của miao.",
    "tokens": [
      {
        "word": "Có",
        "pos": "verb",
        "pronunciation": "Co",
        "color": "#000000",
        "gloss": "There is"
      },
      {
        "word": "lẽ",
        "pos": "noun",
        "pronunciation": "le",
        "color": "#000000",
        "gloss": "possibility"
      },
      {
        "word": "nhưng",
        "pos": "conjunction",
        "pronunciation": "nhung",
        "color": "#000000",
        "gloss": "but"
      },
      {
        "word": "mà",
        "pos": "particle",
        "pronunciation": "ma",
        "color": "#000000",
        "gloss": "(conjunction particle)"
      },
      {
        "word": "vào",
        "pos": "preposition",
        "pronunciation": "vao",
        "color": "#000000",
        "gloss": "into"
      },
      {
        "word": "khoảnh khắc",
        "pos": "noun",
        "pronunciation": "khoanh khac",
        "color": "#000000",
        "gloss": "moment"
      },
      {
        "word": "miao",
        "pos": "noun",
        "pronunciation": "miao",
        "color": "#000000",
        "gloss": "(name)"
      },
      {
        "word": "trực tuyến",
        "pos": "adjective",
        "pronunciation": "truc tuyen",
        "color": "#000000",
        "gloss": "online"
      },
      {
        "word": "thì",
        "pos": "particle",
        "pronunciation": "thi",
        "color": "#000000",
        "gloss": "then"
      },
      {
        "word": "tôi",
        "pos": "pronoun",
        "pronunciation": "toi",
        "color": "#000000",
        "gloss": "I"
      },
      {
        "word": "cảm thấy",
        "pos": "verb",
        "pronunciation": "cam thay",
        "color": "#000000",
        "gloss": "feel"
      },
      {
        "word": "ở",
        "pos": "preposition",
        "pronunciation": "o",
        "color": "#000000",
        "gloss": "at"
      },
      {
        "word": "góc",
        "pos": "noun",
        "pronunciation": "goc",
        "color": "#000000",
        "gloss": "corner"
      },
      {
        "word": "dưới",
        "pos": "noun",
        "pronunciation": "duoi",
        "color": "#000000",
        "gloss": "below"
      },
      {
        "word": "bên",
        "pos": "preposition",
        "pronunciation": "ben",
        "color": "#000000",
        "gloss": "side"
      },
      {
        "word": "phải",
        "pos": "noun",
        "pronunciation": "phai",
        "color": "#000000",
        "gloss": "right"
      },
      {
        "word": "đã",
        "pos": "particle",
        "pronunciation": "da",
        "color": "#000000",
        "gloss": "(past marker)"
      },
      {
        "word": "xuất hiện",
        "pos": "verb",
        "pronunciation": "xuat hien",
        "color": "#000000",
        "gloss": "appear"
      },
      {
        "word": "biểu tượng",
        "pos": "noun",
        "pronunciation": "bieu tuong",
        "color": "#000000",
        "gloss": "icon"
      },
      {
        "word": "của",
        "pos": "preposition",
        "pronunciation": "cua",
        "color": "#000000",
        "gloss": "of"
      },
      {
        "word": "miao",
        "pos": "noun",
        "pronunciation": "miao",
        "color": "#000000",
        "gloss": "(name)"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/3185009336594348325.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: all_zh\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: 当然想聊！你想聊些什么呢？",
  "response": {
    "mode": "x_to_vi",
    "translation": "Tất nhiên muốn nói chuyện! Bạn muốn nói về điều gì?",
    "tokens": [
      {
        "word": "Tất",
        "pos": "adverb",
        "pronunciation": "tat",
        "color": "#000000",
        "gloss": "of course"
      },
      {
        "word": "nhiên",
        "pos": "adverb",
        "pronunciation": "nhien",
        "color": "#000000",
        "gloss": "naturally"
      },
      {
        "word": "muốn",
        "pos": "verb",
        "pronunciation": "muon",
        "color": "#000000",
        "gloss": "want"
      },
      {
        "word": "nói",
        "pos": "verb",
        "pronunciation": "noi",
        "color": "#000000",
        "gloss": "to speak"
      },
      {
        "word": "chuyện",
        "pos": "noun",
        "pronunciation": "chuyen",
        "color": "#000000",
        "gloss": "topic"
      },
      {
        "word": "Bạn",
        "pos": "pronoun",
        "pronunciation": "ban",
        "color": "#000000",
        "gloss": "you"
      },
      {
        "word": "muốn",
        "pos": "verb",
        "pronunciation": "muon",
        "color": "#000000",
        "gloss": "want"
      },
      {
        "word": "nói",
        "pos": "verb",
        "pronunciation": "noi",
        "color": "#000000",
        "gloss": "to speak"
      },
      {
        "word": "về",
        "pos": "preposition",
        "pronunciation": "ve",
        "color": "#000000",
        "gloss": "about"
      },
      {
        "word": "điều",
        "pos": "noun",
        "pronunciation": "dieul",
        "color": "#000000",
        "gloss": "thing"
      },
      {
        "word": "gì",
        "pos": "pronoun",
        "pronunciation": "gi",
        "color": "#000000",
        "gloss": "what"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/3994560290985721797.json`

```json
{
  "prompt": "Detect the primary language of this text and return ISO 639-1 code only.\nText: hello",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/4044373858555870266.json`

```json
{
  "prompt": "Detect the primary language of this text and return ISO 639-1 code only.\nText: can you fetch vietnamese?",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/7554917016763371825.json`

```json
{
  "prompt": "If the text: \"can i post?\" is not Vietnamese, translate it into natural Vietnamese (with correct diacritics) first.\nIf it's already Vietnamese, polish it to correct and native Vietnamese.\n\nAnalyze this Vietnamese text into words.\n\nReturn JSON with:\n- vietnamese_text: native and exact Vietnamese translation or polished original Vietnamese\n- words: array of objects with:\n  - word: the word/particle/punctuation as it appears in vietnamese_text\n  - type: grammatical type from this enum: noun, verb, adjective, adverb, particle, pronoun, numeral, measure, preposition, conjunction, interjection, punctuation, other\n\nRequirements:\n- Segment precisely; keep punctuation as separate words.\n- Use Vietnamese diacritics.\n- Be consistent; no empty items.\n",
  "response": {
    "vietnamese_text": "Tôi có thể đăng không?",
    "words": [
      {
        "word": "Tôi",
        "type": "pronoun"
      },
      {
        "word": "có",
        "type": "verb"
      },
      {
        "word": "thể",
        "type": "verb"
      },
      {
        "word": "đăng",
        "type": "verb"
      },
      {
        "word": "không",
        "type": "adverb"
      },
      {
        "word": "?",
        "type": "punctuation"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/584736834187018685.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: en\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: good night",
  "response": {
    "mode": "x_to_vi",
    "translation": "chúc ngủ ngon",
    "tokens": [
      {
        "word": "chúc",
        "pos": "verb",
        "pronunciation": "chuc",
        "color": "#00FF00",
        "gloss": "wish"
      },
      {
        "word": "ngủ",
        "pos": "verb",
        "pronunciation": "ngu",
        "color": "#0000FF",
        "gloss": "sleep"
      },
      {
        "word": "ngon",
        "pos": "adjective",
        "pronunciation": "ngon",
        "color": "#FF0000",
        "gloss": "good"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/3672780247205784915.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: all_zh\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: 看起来你要说再见了！希望我们的对话让你感到愉快！如果有机会，欢迎你再回来聊天！",
  "response": {
    "mode": "x_to_vi",
    "translation": "Có vẻ như bạn sắp nói lời tạm biệt! Hy vọng cuộc trò chuyện của chúng ta khiến bạn cảm thấy vui vẻ! Nếu có cơ hội, hoan nghênh bạn quay lại trò chuyện!",
    "tokens": [
      {
        "word": "Có",
        "pos": "verb",
        "pronunciation": "Co",
        "color": "#7C7C7C",
        "gloss": "to have"
      },
      {
        "word": "vẻ",
        "pos": "noun",
        "pronunciation": "veh",
        "color": "#7C7C7C",
        "gloss": "appearance"
      },
      {
        "word": "như",
        "pos": "particle",
        "pronunciation": "như",
        "color": "#7C7C7C",
        "gloss": "as, like"
      },
      {
        "word": "bạn",
        "pos": "noun",
        "pronunciation": "ban",
        "color": "#7C7C7C",
        "gloss": "you"
      },
      {
        "word": "sắp",
        "pos": "adverb",
        "pronunciation": "sap",
        "color": "#7C7C7C",
        "gloss": "about to"
      },
      {
        "word": "nói",
        "pos": "verb",
        "pronunciation": "noi",
        "color": "#7C7C7C",
        "gloss": "to say"
      },
      {
        "word": "lời",
        "pos": "noun",
        "pronunciation": "loi",
        "color": "#7C7C7C",
        "gloss": "word"
      },
      {
        "word": "tạm",
        "pos": "adjective",
        "pronunciation": "tam",
        "color": "#7C7C7C",
        "gloss": "temporary"
      },
      {
        "word": "biệt",
        "pos": "noun",
        "pronunciation": "biet",
        "color": "#7C7C7C",
        "gloss": "farewell"
      },
      {
        "word": "Hy",
        "pos": "noun",
        "pronunciation": "Hy",
        "color": "#7C7C7C",
        "gloss": "hope"
      },
      {
        "word": "vọng",
        "pos": "verb",
        "pronunciation": "vong",
        "color": "#7C7C7C",
        "gloss": "to expect"
      },
      {
        "word": "cuộc",
        "pos": "noun",
        "pronunciation": "cuoc",
        "color": "#7C7C7C",
        "gloss": "meeting"
      },
      {
        "word": "trò",
        "pos": "noun",
        "pronunciation": "tro",
        "color": "#7C7C7C",
        "gloss": "game, talk"
      },
      {
        "word": "chuyện",
        "pos": "noun",
        "pronunciation": "chuyen",
        "color": "#7C7C7C",
        "gloss": "story, talk"
      },
      {
        "word": "của",
        "pos": "particle",
        "pronunciation": "cua",
        "color": "#7C7C7C",
        "gloss": "of"
      },
      {
        "word": "chúng",
        "pos": "pronoun",
        "pronunciation": "chung",
        "color": "#7C7C7C",
        "gloss": "we"
      },
      {
        "word": "ta",
        "pos": "pronoun",
        "pronunciation": "ta",
        "color": "#7C7C7C",
        "gloss": "us"
      },
      {
        "word": "khiến",
        "pos": "verb",
        "pronunciation": "khien",
        "color": "#7C7C7C",
        "gloss": "to cause"
      },
      {
        "word": "bạn",
        "pos": "noun",
        "pronunciation": "ban",
        "color": "#7C7C7C",
        "gloss": "you"
      },
      {
        "word": "cảm",
        "pos": "verb",
        "pronunciation": "cam",
        "color": "#7C7C7C",
        "gloss": "to feel"
      },
      {
        "word": "thấy",
        "pos": "verb",
        "pronunciation": "thay",
        "color": "#7C7C7C",
        "gloss": "to see"
      },
      {
        "word": "vui",
        "pos": "adjective",
        "pronunciation": "vui",
        "color": "#7C7C7C",
        "gloss": "happy"
      },
      {
        "word": "vẻ",
        "pos": "noun",
        "pronunciation": "veh",
        "color": "#7C7C7C",
        "gloss": "appearance"
      },
      {
        "word": "Nếu",
        "pos": "conjunction",
        "pronunciation": "neu",
        "color": "#7C7C7C",
        "gloss": "if"
      },
      {
        "word": "có",
        "pos": "verb",
        "pronunciation": "co",
        "color": "#7C7C7C",
        "gloss": "to have"
      },
      {
        "word": "cơ",
        "pos": "noun",
        "pronunciation": "co",
        "color": "#7C7C7C",
        "gloss": "chance"
      },
      {
        "word": "hội",
        "pos": "noun",
        "pronunciation": "hoi",
        "color": "#7C7C7C",
        "gloss": "meeting"
      },
      {
        "word": "hoan",
        "pos": "verb",
        "pronunciation": "hoan",
        "color": "#7C7C7C",
        "gloss": "to welcome"
      },
      {
        "word": "nghênh",
        "pos": "verb",
        "pronunciation": "nghenh",
        "color": "#7C7C7C",
        "gloss": "to greet"
      },
      {
        "word": "bạn",
        "pos": "noun",
        "pronunciation": "ban",
        "color": "#7C7C7C",
        "gloss": "you"
      },
      {
        "word": "quay",
        "pos": "verb",
        "pronunciation": "quay",
        "color": "#7C7C7C",
        "gloss": "to return"
      },
      {
        "word": "lại",
        "pos": "adverb",
        "pronunciation": "lai",
        "color": "#7C7C7C",
        "gloss": "again"
      },
      {
        "word": "trò",
        "pos": "noun",
        "pronunciation": "tro",
        "color": "#7C7C7C",
        "gloss": "game, talk"
      },
      {
        "word": "chuyện",
        "pos": "noun",
        "pronunciation": "chuyen",
        "color": "#7C7C7C",
        "gloss": "story, talk"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/64609044257503892.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nIf input is not Vietnamese, rewrite it into pure Vietnamese first.\nThen analyze the Vietnamese sentence and reply with JSON ONLY per schema: { mode: 'vi_native' | 'x_to_vi', translation: <vietnamese>, tokens: [ { word, pos, pronunciation, gloss } ] }.\nText: Do you know vietnamese?",
  "response": {
    "mode": "x_to_vi",
    "translation": "Bạn có biết tiếng Việt không?",
    "tokens": [
      {
        "word": "Bạn",
        "pos": "Đại từ",
        "pronunciation": "bạn",
        "gloss": "you"
      },
      {
        "word": "có",
        "pos": "Động từ",
        "pronunciation": "có",
        "gloss": "do/have"
      },
      {
        "word": "biết",
        "pos": "Động từ",
        "pronunciation": "biết",
        "gloss": "know"
      },
      {
        "word": "tiếng",
        "pos": "Danh từ",
        "pronunciation": "tiếng",
        "gloss": "language"
      },
      {
        "word": "Việt",
        "pos": "Danh từ riêng",
        "pronunciation": "Việt",
        "gloss": "Vietnamese"
      },
      {
        "word": "không",
        "pos": "Trạng từ",
        "pronunciation": "không",
        "gloss": "not/no"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/7056593499676765840.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nIf input is not Vietnamese, rewrite it into pure Vietnamese first.\nThen analyze the Vietnamese sentence and reply with JSON ONLY per schema: { mode: 'vi_native' | 'x_to_vi', translation: <vietnamese>, tokens: [ { word, pos, pronunciation, gloss } ] }.\nText: 你还想跟我聊天吗?",
  "response": {
    "mode": "x_to_vi",
    "translation": "Bạn còn muốn trò chuyện với tôi không?",
    "tokens": [
      {
        "word": "Bạn",
        "pos": "pronoun",
        "pronunciation": "bạn",
        "gloss": "you"
      },
      {
        "word": "còn",
        "pos": "adverb",
        "pronunciation": "còn",
        "gloss": "still"
      },
      {
        "word": "muốn",
        "pos": "verb",
        "pronunciation": "muốn",
        "gloss": "want"
      },
      {
        "word": "trò chuyện",
        "pos": "verb phrase",
        "pronunciation": "trò chuyện",
        "gloss": "chat"
      },
      {
        "word": "với",
        "pos": "preposition",
        "pronunciation": "với",
        "gloss": "with"
      },
      {
        "word": "tôi",
        "pos": "pronoun",
        "pronunciation": "tôi",
        "gloss": "I"
      },
      {
        "word": "không",
        "pos": "particle",
        "pronunciation": "không",
        "gloss": "not"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/326034854208500981.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nIf input is not Vietnamese, rewrite it into pure Vietnamese first.\nThen analyze the Vietnamese sentence and reply with JSON ONLY per schema: { mode: 'vi_native' | 'x_to_vi', translation: <vietnamese>, tokens: [ { word, pos, pronunciation, gloss } ] }.\nText: good night",
  "response": {
    "mode": "x_to_vi",
    "translation": "chúc ngủ ngon",
    "tokens": [
      {
        "word": "chúc",
        "pos": "động từ",
        "pronunciation": "tʃúk",
        "gloss": "to wish"
      },
      {
        "word": "ngủ",
        "pos": "động từ",
        "pronunciation": "ŋu̟",
        "gloss": "to sleep"
      },
      {
        "word": "ngon",
        "pos": "tính từ",
        "pronunciation": "ŋɔ̄n",
        "gloss": "delicious, good (in context of sleep)"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/7337801324587025033.json`

```json
{
  "prompt": "Detect the primary language of this text and return ISO 639-1 code only.\nText: do you have color?",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/2599043947452227617.json`

```json
{
  "prompt": "Detect the primary language of this text and return ISO 639-1 code only.\nText: I want to post something to delete.",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/6369588668338437723.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: en\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: I want to post something to delete.",
  "response": {
    "mode": "x_to_vi",
    "translation": "Tôi muốn đăng một cái gì đó để xóa.",
    "tokens": [
      {
        "word": "Tôi",
        "pos": "pronoun",
        "pronunciation": "Toi",
        "color": "#000000",
        "gloss": "I"
      },
      {
        "word": "muốn",
        "pos": "verb",
        "pronunciation": "muon",
        "color": "#000000",
        "gloss": "want"
      },
      {
        "word": "đăng",
        "pos": "verb",
        "pronunciation": "dang",
        "color": "#000000",
        "gloss": "post"
      },
      {
        "word": "một",
        "pos": "quantifier",
        "pronunciation": "mot",
        "color": "#000000",
        "gloss": "a"
      },
      {
        "word": "cái",
        "pos": "classifier",
        "pronunciation": "cai",
        "color": "#000000",
        "gloss": "thing"
      },
      {
        "word": "gì",
        "pos": "pronoun",
        "pronunciation": "gi",
        "color": "#000000",
        "gloss": "what"
      },
      {
        "word": "đó",
        "pos": "pronoun",
        "pronunciation": "do",
        "color": "#000000",
        "gloss": "that"
      },
      {
        "word": "để",
        "pos": "particle",
        "pronunciation": "de",
        "color": "#000000",
        "gloss": "to"
      },
      {
        "word": "xóa",
        "pos": "verb",
        "pronunciation": "xoa",
        "color": "#000000",
        "gloss": "delete"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/6266509682710882225.json`

```json
{
  "prompt": "If the text: \"Auto coin test content\" is not Vietnamese, translate it into natural Vietnamese (with correct diacritics) first.\nIf it's already Vietnamese, polish it to correct and native Vietnamese.\n\nAnalyze this Vietnamese text into words.\n\nReturn JSON with:\n- vietnamese_text: native and exact Vietnamese translation or polished original Vietnamese\n- words: array of objects with:\n  - word: the word/particle/punctuation as it appears in vietnamese_text\n  - type: grammatical type from this enum: noun, verb, adjective, adverb, particle, pronoun, numeral, measure, preposition, conjunction, interjection, punctuation, other\n\nRequirements:\n- Segment precisely; keep punctuation as separate words.\n- Use Vietnamese diacritics.\n- Be consistent; no empty items.\n",
  "response": {
    "vietnamese_text": "Nội dung kiểm tra đồng xu tự động",
    "words": [
      {
        "word": "Nội",
        "type": "noun"
      },
      {
        "word": "dung",
        "type": "noun"
      },
      {
        "word": "kiểm",
        "type": "verb"
      },
      {
        "word": "tra",
        "type": "verb"
      },
      {
        "word": "đồng",
        "type": "noun"
      },
      {
        "word": "xu",
        "type": "noun"
      },
      {
        "word": "tự",
        "type": "adjective"
      },
      {
        "word": "động",
        "type": "adjective"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/8926435617149074035.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: en\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: can you work?",
  "response": {
    "mode": "x_to_vi",
    "translation": "Bạn có thể làm việc không?",
    "tokens": [
      {
        "word": "Bạn",
        "pos": "pronoun",
        "pronunciation": "Ban",
        "color": "#0000FF",
        "gloss": "you"
      },
      {
        "word": "có",
        "pos": "verb",
        "pronunciation": "co",
        "color": "#000000",
        "gloss": "can"
      },
      {
        "word": "thể",
        "pos": "verb",
        "pronunciation": "the",
        "color": "#000000",
        "gloss": "be able to"
      },
      {
        "word": "làm",
        "pos": "verb",
        "pronunciation": "lam",
        "color": "#000000",
        "gloss": "work"
      },
      {
        "word": "việc",
        "pos": "noun",
        "pronunciation": "viec",
        "color": "#000000",
        "gloss": "task"
      },
      {
        "word": "không",
        "pos": "particle",
        "pronunciation": "khong",
        "color": "#000000",
        "gloss": "not?"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/3817796402550254179.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: en\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: Hello, hello, hello, hello, hello, hello.",
  "response": {
    "mode": "x_to_vi",
    "translation": "Xin chào, xin chào, xin chào, xin chào, xin chào, xin chào.",
    "tokens": [
      {
        "word": "Xin",
        "pos": "interjection",
        "pronunciation": "xin",
        "color": "#000000",
        "gloss": "please"
      },
      {
        "word": "chào",
        "pos": "verb",
        "pronunciation": "chao",
        "color": "#000000",
        "gloss": "greet"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/7420331799647273436.json`

```json
{
  "prompt": "Detect the primary language of this text and return ISO 639-1 code only.\nText: can you work?",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/530267138134329395.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: auto\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: or is this my code's bug?",
  "response": {
    "mode": "x_to_vi",
    "translation": "hoặc đây có phải là lỗi trong mã của tôi không?",
    "tokens": [
      {
        "word": "hoặc",
        "pos": "CC",
        "pronunciation": "hoặc",
        "color": "#000000",
        "gloss": "or"
      },
      {
        "word": "đây",
        "pos": "DT",
        "pronunciation": "đây",
        "color": "#000000",
        "gloss": "this"
      },
      {
        "word": "có",
        "pos": "VB",
        "pronunciation": "có",
        "color": "#000000",
        "gloss": "is/has"
      },
      {
        "word": "phải",
        "pos": "AUX",
        "pronunciation": "phải",
        "color": "#000000",
        "gloss": "must"
      },
      {
        "word": "là",
        "pos": "VB",
        "pronunciation": "là",
        "color": "#000000",
        "gloss": "be"
      },
      {
        "word": "lỗi",
        "pos": "N",
        "pronunciation": "lỗi",
        "color": "#000000",
        "gloss": "bug/error"
      },
      {
        "word": "trong",
        "pos": "IN",
        "pronunciation": "trong",
        "color": "#000000",
        "gloss": "in"
      },
      {
        "word": "mã",
        "pos": "N",
        "pronunciation": "mã",
        "color": "#000000",
        "gloss": "code"
      },
      {
        "word": "của",
        "pos": "AP",
        "pronunciation": "của",
        "color": "#000000",
        "gloss": "of"
      },
      {
        "word": "tôi",
        "pos": "PRP",
        "pronunciation": "tôi",
        "color": "#000000",
        "gloss": "my"
      },
      {
        "word": "không",
        "pos": "AUX",
        "pronunciation": "không",
        "color": "#000000",
        "gloss": "not?"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/8869792005885921759.json`

```json
{
  "prompt": "Detect the primary language of this text and return ISO 639-1 code only.\nText: What will happen if we push new thing?",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/5750241311850884331.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: zh\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: 可以说是越南语吗",
  "response": {
    "mode": "x_to_vi",
    "translation": "Có thể nói là tiếng Việt không?",
    "tokens": [
      {
        "word": "Có",
        "pos": "verb",
        "pronunciation": "Co",
        "color": "#000000",
        "gloss": "Can"
      },
      {
        "word": "thể",
        "pos": "verb",
        "pronunciation": "the",
        "color": "#000000",
        "gloss": "Be able to"
      },
      {
        "word": "nói",
        "pos": "verb",
        "pronunciation": "noi",
        "color": "#000000",
        "gloss": "Speak"
      },
      {
        "word": "là",
        "pos": "verb",
        "pronunciation": "la",
        "color": "#000000",
        "gloss": "Is"
      },
      {
        "word": "tiếng",
        "pos": "noun",
        "pronunciation": "tieng",
        "color": "#000000",
        "gloss": "Language"
      },
      {
        "word": "Việt",
        "pos": "noun",
        "pronunciation": "Viet",
        "color": "#000000",
        "gloss": "Vietnamese"
      },
      {
        "word": "không",
        "pos": "adverb",
        "pronunciation": "khong",
        "color": "#000000",
        "gloss": "Not/No?"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/233247244924413128.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: auto\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: @indigopurple",
  "response": {
    "mode": "x_to_vi",
    "translation": "@indigopurple",
    "tokens": [
      {
        "word": "@indigopurple",
        "pos": "Noun",
        "pronunciation": "@indigopurple",
        "color": "#6F6F6F",
        "gloss": "Tên người dùng trên mạng xã hội."
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/8880259689764698632.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nIf input is not Vietnamese, rewrite it into pure Vietnamese first.\nThen analyze the Vietnamese sentence and reply with JSON ONLY per schema: { mode: 'vi_native' | 'x_to_vi', translation: <vietnamese>, tokens: [ { word, pos, pronunciation, gloss } ] }.\nText: what do you think",
  "response": {
    "mode": "x_to_vi",
    "translation": "Bạn nghĩ gì?",
    "tokens": [
      {
        "word": "Bạn",
        "pos": "đại từ nhân xưng",
        "pronunciation": "bạn",
        "gloss": "you"
      },
      {
        "word": "nghĩ",
        "pos": "động từ",
        "pronunciation": "nghĩ",
        "gloss": "think"
      },
      {
        "word": "gì",
        "pos": "từ để hỏi",
        "pronunciation": "gì",
        "gloss": "what"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/6779939075437350471.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nIf input is not Vietnamese, rewrite it into pure Vietnamese first.\nThen analyze the Vietnamese sentence and reply with JSON ONLY per schema: { mode: 'vi_native' | 'x_to_vi', translation: <vietnamese>, tokens: [ { word, pos, pronunciation, gloss } ] }.\nText: 감사합니다.",
  "response": {
    "mode": "x_to_vi",
    "translation": "Cảm ơn bạn.",
    "tokens": [
      {
        "word": "Cảm",
        "pos": "Động từ",
        "pronunciation": "kæ̂m",
        "gloss": "Cảm nhận, thể hiện lòng biết ơn"
      },
      {
        "word": "ơn",
        "pos": "Danh từ",
        "pronunciation": "ʔɤ̄n",
        "gloss": "Lòng biết ơn, sự tri ân"
      },
      {
        "word": "bạn",
        "pos": "Danh từ",
        "pronunciation": "bɑn",
        "gloss": "Người bạn, bạn bè"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/7566900811490635107.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: zh\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: 有人回答一下吗",
  "response": {
    "mode": "x_to_vi",
    "translation": "Có ai trả lời không?",
    "tokens": [
      {
        "word": "Có",
        "pos": "verb",
        "pronunciation": "Co",
        "color": "#000000",
        "gloss": "To have"
      },
      {
        "word": "ai",
        "pos": "pronoun",
        "pronunciation": "ai",
        "color": "#000000",
        "gloss": "who"
      },
      {
        "word": "trả",
        "pos": "verb",
        "pronunciation": "tra",
        "color": "#000000",
        "gloss": "to return"
      },
      {
        "word": "lời",
        "pos": "noun",
        "pronunciation": "loi",
        "color": "#000000",
        "gloss": "answer"
      },
      {
        "word": "không",
        "pos": "adverb",
        "pronunciation": "khong",
        "color": "#000000",
        "gloss": "not"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/4076352809924370677.json`

```json
{
  "prompt": "Detect the primary language of this text and return ISO 639-1 code only.\nText: good night",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/1588900025475121248.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: all_zh\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: 我吃过了，谢谢！你呢？吃饭了吗？",
  "response": {
    "mode": "x_to_vi",
    "translation": "Tôi đã ăn rồi, cảm ơn! Còn bạn thì sao? Bạn đã ăn cơm chưa?",
    "tokens": [
      {
        "word": "Tôi",
        "pos": "pronoun",
        "pronunciation": "toi",
        "color": "#FFC107",
        "gloss": "I"
      },
      {
        "word": "đã",
        "pos": "particle",
        "pronunciation": "da",
        "color": "#9C27B0",
        "gloss": "(past tense marker)"
      },
      {
        "word": "ăn",
        "pos": "verb",
        "pronunciation": "an",
        "color": "#4CAF50",
        "gloss": "eat"
      },
      {
        "word": "rồi",
        "pos": "particle",
        "pronunciation": "roi",
        "color": "#2196F3",
        "gloss": "already"
      },
      {
        "word": ",",
        "pos": "punctuation",
        "pronunciation": ",",
        "color": "",
        "gloss": ""
      },
      {
        "word": "cảm",
        "pos": "verb",
        "pronunciation": "cam",
        "color": "#4CAF50",
        "gloss": "feel"
      },
      {
        "word": "ơn",
        "pos": "noun",
        "pronunciation": "on",
        "color": "#9C27B0",
        "gloss": "thanks"
      },
      {
        "word": "!",
        "pos": "punctuation",
        "pronunciation": "!",
        "color": "",
        "gloss": ""
      },
      {
        "word": "Còn",
        "pos": "particle",
        "pronunciation": "con",
        "color": "#FFC107",
        "gloss": "and"
      },
      {
        "word": "bạn",
        "pos": "pronoun",
        "pronunciation": "ban",
        "color": "#2196F3",
        "gloss": "you"
      },
      {
        "word": "thì",
        "pos": "particle",
        "pronunciation": "thi",
        "color": "#9C27B0",
        "gloss": "(to indicate topic)"
      },
      {
        "word": "sao",
        "pos": "adverb",
        "pronunciation": "sao",
        "color": "#4CAF50",
        "gloss": "how"
      },
      {
        "word": "?",
        "pos": "punctuation",
        "pronunciation": "?",
        "color": "",
        "gloss": ""
      },
      {
        "word": "Bạn",
        "pos": "pronoun",
        "pronunciation": "ban",
        "color": "#2196F3",
        "gloss": "You"
      },
      {
        "word": "đã",
        "pos": "particle",
        "pronunciation": "da",
        "color": "#9C27B0",
        "gloss": "(past tense marker)"
      },
      {
        "word": "ăn",
        "pos": "verb",
        "pronunciation": "an",
        "color": "#4CAF50",
        "gloss": "eat"
      },
      {
        "word": "cơm",
        "pos": "noun",
        "pronunciation": "com",
        "color": "#FF9800",
        "gloss": "rice"
      },
      {
        "word": "chưa",
        "pos": "particle",
        "pronunciation": "chua",
        "color": "#9C27B0",
        "gloss": "not yet"
      },
      {
        "word": "?",
        "pos": "punctuation",
        "pronunciation": "?",
        "color": "",
        "gloss": ""
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/4086880577049884172.json`

```json
{
  "prompt": "Detect the primary language of this text and return ISO 639-1 code only.\nText: do you have color?",
  "response": {
    "language_code": "en"
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/6524608928968397668.json`

```json
{
  "prompt": "You are a Vietnamese linguistic assistant.\nAlways respond with strict JSON per the provided schema.\nSource language: fr\nTasks: If source is 'vi' analyze the original Vietnamese and set mode='vi_to_en' and translation to English.\nOtherwise translate the text into Vietnamese first and set mode='x_to_vi'; use the Vietnamese translation for token analysis.\nTokens must reflect Vietnamese words with fields: word, pos, pronunciation (romanized or diacritics-removed), optional color (hex), optional gloss.\nText: Merci, Saint-Saëns. Thank you.",
  "response": {
    "mode": "x_to_vi",
    "translation": "Cảm ơn, Saint-Saëns. Cảm ơn bạn.",
    "tokens": [
      {
        "word": "Cảm ơn",
        "pos": "verb",
        "pronunciation": "cam on",
        "color": "#000000",
        "gloss": "to thank"
      },
      {
        "word": ",",
        "pos": "punctuation",
        "pronunciation": ",",
        "color": "#000000",
        "gloss": ""
      },
      {
        "word": "Saint-Saëns",
        "pos": "proper noun",
        "pronunciation": "Saint-Saens",
        "color": "#000000",
        "gloss": "Saint-Saëns"
      },
      {
        "word": ".",
        "pos": "punctuation",
        "pronunciation": ".",
        "color": "#000000",
        "gloss": ""
      },
      {
        "word": "Cảm ơn",
        "pos": "verb",
        "pronunciation": "cam on",
        "color": "#000000",
        "gloss": "to thank"
      },
      {
        "word": "bạn",
        "pos": "pronoun",
        "pronunciation": "ban",
        "color": "#000000",
        "gloss": "you"
      }
    ]
  }
}
```

## Source: `echomind/cachexxx/vietnamese_enhancement_cache/5945963130227266342.json`

```json
{
  "prompt": "Detect the primary language of this text and return ISO 639-1 code only.\nText: does it work?",
  "response": {
    "language_code": "en"
  }
}
```
