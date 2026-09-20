"""Black-box CLI regression: a token expiry during upload must refresh and resume."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest


class ClientRefreshTest(unittest.TestCase):
    def test_upload_refresh_retries_only_rejected_chunk(self):
        state = {"refreshes": 0, "accepted": b"", "parts": 0}

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass

            def reply(self, data, status=200):
                raw = json.dumps(data).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def do_POST(self):
                data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                if self.path == "/auth/token":
                    state["refreshes"] += 1
                    self.reply({"access_token": "access"+str(state["refreshes"]),
                                "refresh_token": "rotated", "grant_id": "test"})
                elif self.path == "/v1/studio/uploads":
                    self.reply({"uploadId": "test", "offset": 0})
                elif self.path == "/v1/studio/upload-complete":
                    self.reply({"videoId": 1})
                else:
                    self.reply({}, 404)

            def do_PUT(self):
                chunk = self.rfile.read(int(self.headers["Content-Length"]))
                state["parts"] += 1
                if self.headers["Authorization"] == "Bearer access1":
                    self.reply({"error": "Credential expired or revoked"}, 401)
                    return
                state["accepted"] += chunk
                self.reply({"offset": len(state["accepted"])})

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                saved = root/"session.json"
                saved.write_text(json.dumps({"refresh_token": "initial"}))
                video = root/"fixture.mp4"
                video.write_bytes(b"controlled-upload-fixture")
                result = subprocess.run(
                    [sys.executable, str(Path(__file__).with_name("client.py")),
                     "--server", f"http://127.0.0.1:{server.server_port}",
                     "--state", str(saved), "upload", str(video)],
                    capture_output=True, text=True, timeout=20)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(state["accepted"], video.read_bytes())
                self.assertEqual(state["refreshes"], 2)
                self.assertEqual(state["parts"], 2)
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main()
