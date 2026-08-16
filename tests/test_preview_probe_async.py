import os
import tempfile
import unittest
from unittest import mock

import app


class PreviewProbeAsyncTests(unittest.TestCase):
    def test_preview_info_never_runs_ffprobe_on_request_thread(self):
        with tempfile.NamedTemporaryFile(suffix=".mp4") as source:
            with mock.patch.object(app, "_should_create_preview_proxy") as probe:
                with mock.patch.object(app, "_enqueue_preview_probe") as enqueue:
                    info = app._preview_info_for_video(9123, source.name, auto_enqueue=True)

        probe.assert_not_called()
        enqueue.assert_called_once_with(9123, source.name)
        self.assertFalse(info["needs_preview_proxy"])
        self.assertFalse(info["has_preview_proxy"])


if __name__ == "__main__":
    unittest.main()
