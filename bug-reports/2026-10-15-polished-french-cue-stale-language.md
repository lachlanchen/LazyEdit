# Corrected French Cue Retains Chinese ASR Language

Observed during owner-authorized LALACHAN publication, video 617, before render.

## Reproduction

1. ASR emits a Chinese transliteration `苏利`, tagged `zh`.
2. Normal context correction correctly changes the text to French `Souriez`.
3. The polished JSON still has `lang: zh` for 00:05.680-00:06.640.
4. `SubtitleTranslator._target_matches_source_language` treats it as native
   Chinese. Its stale-tag guard currently handles Han-only corrections of
   Latin-language cues, not the reverse case. The source-language sound marker
   can also remain on the wrong row.

## Scoped Recovery

The normal correction endpoint handled text and removed false nonverbal/
thanks captions. Only the inspected French cue's polished JSON language tag
was changed from `zh` to `fr`; ASR originals, text and timing were preserved.
No metadata was manually rewritten and no shared service was restarted.

## Suggested Shared Fix

Allow an explicit, validated per-cue language correction through the normal
correction API/UI, and propagate it into translation and speaker markers.
Preserve existing language tags by default; Latin spelling alone cannot
distinguish French from English or a proper name. Test a known French
correction, a genuine Chinese line containing a Latin proper name, and timing
preservation. This report does not claim that the shared fix is implemented.
