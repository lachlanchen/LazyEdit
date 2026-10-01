# Beef and potatoes — Korean-bottom publication

Video 600: `IMG_8951_2026_10_01_22_08_26_COMPLETED.MOV`.
Source: 3840×2160 landscape, 10.5 seconds. User requested the new upload with
Korean at the bottom, Hanja restoration where appropriate, native Hangul plus
romanization otherwise, and portrait background fill.

The automatic mixed-language pass incorrectly interpreted 牛肉配土豆 as Korean
`유럽의 도도`. A Chinese-only Whisper large-v3 pass without a text prompt recovered
the wording; a second pass aligned it to the original audio:

- 3.50–4.80: 看着很好吃。
- 5.56–7.04: 牛肉配土豆。

Imported these aligned cues using `--subtitle-file --subtitle-language zh`,
then used normal translation/burn/metadata/cover processing. Context remained
reference material. Pronunciation: Japanese kanji ruby/kana romanization,
Chinese pinyin, Korean romanization. Natural Korean translations were
맛있어 보인다 and 소고기와 감자; these kept modern Hangul with romanization.
The initial explanation that every word has no Han connection was too broad:
감자 has historical links to 감저/甘藷, although modern dictionary classification
treats it as native. Historical etymology is not automatically a conventional
modern Han spelling. The shared restoration path remains enabled for clear
Sino-Korean roots; no speculative Chinese equivalents were inserted.

Sources: [modern dictionary classification](https://krdict.korean.go.kr/kor/dicSearch/SearchView?ParaWordNo=15203),
[National Institute of Korean Language etymology article](https://www.korean.go.kr/nkview/nklife/2009_3/2009_0306.pdf).

One-shot settings: languages `ko,zh-Hant,ja,en` bottom-to-top, four reserved rows,
zero lift, portrait blur-fill with 40% lower reserve, configured top-right logo.
Studio defaults were not changed. Final render:
`DATA/IMG_8951_2026_10_01_22_08_26_COMPLETED/IMG_8951_2026_10_01_22_08_26_COMPLETED_portrait_subtitles_logo.mp4`.
The packaged MP4 SHA-256 matches this render. Reviewed frame at 6.3 seconds is
saved as `review_final.jpg` beside it.

System repairs and tests are documented in
`2026-10-01-multilingual-subtitle-restoration.md`. An unwanted prerequisite
rerun in job 441 was stopped before any platform submission; repaired queue
readiness now respects the job's language selection. Job 442 reused the output.
Misleading automatic image captions (apples, onions, pan) were corrected through
the normal metadata context prompt after visual inspection of the whole clip.

Publication job: LazyEdit 442; AutoPublish `job-1790864904050-1`.
- Douyin: published, accepted receipt and matching management title. Its stale
  management list needed one reload; permanent verifier fix is AutoPublish
  commit `1278e02`, deployed on lazyingart after the queue completed.
- Shipinhao: published, draft saved, cover ready and management entry verified.
- Instagram: published; Original crop and saved caption verified:
  https://www.instagram.com/lazyingart/reel/Dd9I3uBOgAc/
- YouTube: published; checks completed and publication receipt verified:
  https://youtube.com/shorts/EQntCzMgr40

Final local and remote job statuses: `done` for all four platforms. Queue idle.
