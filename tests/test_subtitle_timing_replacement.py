import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import _validated_resegmented_subtitle_items


class SubtitleTimingReplacementTests(unittest.TestCase):
    def setUp(self):
        self.original = [
            {
                "start": "00:00:01,000",
                "end": "00:00:02,000",
                "text": "hallucinated opening",
                "language": "zh",
            },
            {
                "start": "00:00:13,000",
                "end": "00:00:15,000",
                "text": "hallucinated ending",
                "language": "zh",
            },
        ]
        self.replacement = [
            {
                "start": "00:00:03,640",
                "end": "00:00:05,700",
                "text": "哎，别掉呀！",
            },
            {
                "start": "00:00:05,700",
                "end": "00:00:07,680",
                "text": "靠近我，慢慢飞。",
            },
        ]

    def test_explicit_replacement_accepts_valid_timing_inside_video(self):
        result = _validated_resegmented_subtitle_items(
            self.original,
            self.replacement,
            max_end_seconds=15.047,
            enforce_original_span=False,
        )

        self.assertIsNotNone(result)
        self.assertEqual([item["text"] for item in result], ["哎，别掉呀！", "靠近我，慢慢飞。"])
        self.assertEqual(result[0]["start"], "00:00:03,640")
        self.assertEqual(result[-1]["end"], "00:00:07,680")
        self.assertTrue(all(item["language"] == "zh" for item in result))

    def test_normal_resegmentation_still_requires_original_span(self):
        result = _validated_resegmented_subtitle_items(
            self.original,
            self.replacement,
            max_end_seconds=15.047,
        )

        self.assertIsNone(result)

    def test_replacement_rejects_overlap_and_out_of_bounds_timing(self):
        overlapping = [dict(item) for item in self.replacement]
        overlapping[1]["start"] = "00:00:05,000"
        outside_video = [dict(item) for item in self.replacement]
        outside_video[1]["end"] = "00:00:15,200"

        self.assertIsNone(
            _validated_resegmented_subtitle_items(
                self.original,
                overlapping,
                max_end_seconds=15.047,
                enforce_original_span=False,
            )
        )
        self.assertIsNone(
            _validated_resegmented_subtitle_items(
                self.original,
                outside_video,
                max_end_seconds=15.047,
                enforce_original_span=False,
            )
        )


if __name__ == "__main__":
    unittest.main()
