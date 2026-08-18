# Polished subtitle text can drift onto unrelated ASR timestamps

## Summary

The LALACHAN Japan episode published on 2026-08-18 exposed a severe subtitle
alignment failure. Story-context correction changed the number and order of
subtitle lines, moved later dialogue into earlier ASR cues, and then left a
second copy of some original dialogue near its real position. Translation and
burning proceeded from that invalid polished timeline.

## Affected run

- LazyEdit video: `526`
- Publish job: `362`
- Stem: `japan_sky_route_black_egg_55s_2026-08-18`
- Source duration: `55.7s`

## Evidence

Source ASR contains 20 cues. Examples:

```text
00:16.040 --> 00:17.680  我们到宇宙了吗
00:17.680 --> 00:18.720  还没有
00:30.000 --> 00:35.060  先吃午饭
00:39.680 --> 00:40.660  明迪找到了
00:42.780 --> 00:44.820  飞得像火箭一样高
```

The polished SRT contains 21 cues and moved later story lines into earlier
timestamps:

```text
00:09.300 --> 00:10.820  地球真的变圆了！我们到宇宙了吗？
00:10.820 --> 00:16.040  还没有。系稳了，我们再飞高一点。
00:16.040 --> 00:17.680  先吃午饭。
00:18.720 --> 00:19.760  谜底找到了。
00:30.000 --> 00:31.560  飞得像火箭一样高，原来就是为了这一口？
```

It then retained another copy of the black-egg dialogue around `40-49s`.

## Expected behavior

1. Ordinary subtitle correction must be cue-local and preserve cue count,
   ordering, start time, and end time.
2. Prompt/story context may repair names and recognition errors but must not be
   treated as a replacement transcript.
3. Recovering ASR-missed speech must run a separate audio-alignment operation
   that assigns evidence-based timestamps.
4. Translation, burn, and publish must be blocked when source and polished SRT
   cue counts or timestamps differ unexpectedly.
5. The publish API/CLI should expose the validation result in the process state.

## Suggested regression test

Feed a 20-cue source SRT and a correction response that returns 21 lines or
changes cue 11 from `30.000-35.060` to `30.000-31.560`. Assert that polish fails
with a timeline-integrity error and downstream translation/burn steps do not
start.
