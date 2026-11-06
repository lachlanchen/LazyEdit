# Rendering after correction removes all speech

Subtitle correction may reject an ASR hallucination while retaining its cue and
timestamps with an empty `text` value. This preserves the audit trail. The
translator correctly omits those cues, but the burn endpoint previously checked
only whether the source list was empty. A nonempty list of empty cues therefore
reached translation validation and failed with `translation not ready for en`.

The burn endpoint now treats an empty list and a list containing only blank or
null text as having no captions to render. It keeps the existing logo/portrait
processing path, or records the burn as skipped when neither is requested. It
does not delete audit cues or manufacture captions. If any cue contains real
text, the usual translation requirements still apply.

The regression tests exercise the actual HTTP handler with isolated database and
encoder doubles. They cover blank and whitespace/null corrected cues, logo-only
processing, a skip without a logo, unchanged transcript contents and timestamps,
and the missing-translation error for a mixed blank/real-speech transcript:

```bash
python -m pytest tests/test_empty_corrected_burn.py -q
```

If a live publication is already running on an older backend, use the normal
`--no-burn-subtitles --logo` preparation path after confirming there is no usable
speech. Inspect that output, then publish it once. Apply the backend fix only at
an idle checkpoint; do not trigger autoreload during processing or publication.
Completed platform receipts must be preserved, and an uncertain submission must
be reconciled before any retry.
