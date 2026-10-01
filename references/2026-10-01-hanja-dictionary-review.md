# Korean restoration: local candidates, contextual LLM review

The user requested a simple, fast dictionary-assisted method, without a vector
database or extra service. The existing normal translation/annotation request
remains. No new publication, subtitle render, or UI-default change is needed.

## Flow

1. The existing LLM translates and emits lossless grammar/ruby tokens.
2. Validate row count, timestamps, complete source surfaces, display spelling,
   grammar types, native ruby for restored roots and Korean romanization for
   unrestored Hangul. Missing fields, empty tokens and dropped text are errors.
3. For Korean only, consult a local dictionary for missed or conflicting Han
   candidates. Use longest whole-word matches (at least two Hangul syllables)
   to find roots even when the LLM left a particle attached. This is candidate
   retrieval, not a morphological analyzer or automatic replacement algorithm.
4. If needed, make **one** LLM review/repair with the sentence context, previous
   JSON and bounded candidate list. Keep the translated text and timestamps
   frozen. Existing transport retries still apply; there is no new retry loop.
5. Revalidate before returning to the existing ruby/color/wrapping renderer.
   If repair is still structurally invalid, fail visibly rather than burn it.

Correct known restorations and dictionary misses do not need another call.
Zero restored roots remains valid. A miss is not evidence that a word is native.
The dictionary does not cover every word, and the LLM remains responsible for
meaning and pronunciation. Structurally valid but linguistically wrong output
is still possible; these checks are not a guarantee of perfect translation.

## Dictionary and setup

`lazyedit/hanja_dictionary.py` uses the libhangul input-method candidate data:

- Upstream: <https://github.com/libhangul/libhangul>
- Revision: `5094421d9586294b2aad09924b9a54e2e6060f06`
- File: `data/hanja/hanja.txt` (6,452,537 bytes)
- SHA-256: `b1004034589f1357daaea3534a6136f6b5ef825afa8779886b20f0b7908bbe3b`
- The **data file** carries Choe Hwanjin's BSD-3-Clause notice; preserve it.
- Default local path: `cache/dictionaries/libhangul-hanja.txt`, already ignored.
- Optional alternate file: `LAZYEDIT_HANJA_DICTIONARY`.

Explicit setup, using the existing LazyEdit Python environment:

```bash
python -m lazyedit.hanja_dictionary
```

First Korean use also attempts setup once per process if the default file is
missing. The download has a timeout and size cap, checks the pinned digest, and
installs atomically. Concurrent subtitle workers share the setup/load lock.
An offline failure logs a warning and uses normal LLM annotations without
repeated download waits. The parsed lookup stays in memory; a changed file
mtime refreshes it. No per-word network request or new API key is required.

The candidate list is NOT an authoritative context-sensitive dictionary.
For example, 감자 has entries such as 減資, which is inappropriate for potatoes.
Never substitute the first candidate, even when there is only one. The review
prompt explicitly permits retaining Hangul for native/uncertain meanings.
Hints are limited to 12 occurrences with up to 12 candidates each.

## Scope and files

- `lazyedit/hanja_dictionary.py`: pinned data setup, cached lookup, bounded hints.
- `lazyedit/subtitle_annotations.py`: explicit root/homophone self-check prompt,
  lossless token validation and missing-romanization checks.
- `lazyedit/subtitle_translate.py`: shared Korean/Vietnamese bounded review;
  Korean gets dictionary hints, Vietnamese keeps its LLM-only restoration.
- `tests/test_hanja_dictionary.py`: candidate retrieval, native homophones,
  missed roots, exact text preservation, one-repair limit and offline behavior.

Vietnamese does not use Korean data. It benefits from the improved prompt and
validation/repair path. A Vietnamese dictionary can be considered separately
after evaluating an appropriate source; none is claimed to be installed here.

Completed video files and posts remain unchanged. Request new translation via
the normal Studio pipeline to use the new behavior. The prompt/cache version
changed, so old cached model responses are not reused for these requests.

## Validation on the deployed workstation

- 42 focused automated tests pass, including the actual renderer's token loader
  and wrapping checks. Unit tests inject tiny local dictionary data and need no
  dictionary download or model API.
- The installed snapshot yields 186,732 multi-syllable lookup keys. Parsing took
  about 0.715 seconds once; 1,000 repeated short-cue lookups averaged approximately
  0.005 ms each. These are local lookup measurements, not end-to-end LLM latency.
- Seven live checks used the existing `deepseek-v4-flash` translator: six
  same-language annotation checks and one Chinese-to-Korean translation.
- 학생/학교/공부 restored to 學生/學校/工夫 with Hangul ruby. A Chinese source
  sentence also produced 中國語 with 중국어 ruby, preserving all particles.
- 사과 in an eating sentence became 沙果; in an apology sentence it became 謝過.
- The food sentence kept 소고기/감자 plus romanization rather than selecting an
  unrelated dictionary homophone. The old post was not republished.
- Vietnamese Học sinh restored 學/生; native Tôi ăn cơm retained Quốc ngữ and IPA.
  One initial Vietnamese response had an invalid ruby mapping; the bounded
  repair corrected it. All clean native texts and timestamps stayed unchanged.
- Live response timings varied from roughly 5 to 69 seconds, including review
  where needed. Network/model response time dominates; no fixed speed claim.
- Local evidence: `cache/hanja-review-2026-10-01/results.json`, `translation.json`
  and request logs (ignored runtime files). The normal backend remained healthy
  and its publish queue was idle during integration.
