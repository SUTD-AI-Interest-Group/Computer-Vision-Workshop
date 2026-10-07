import unittest
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest


class AppTests(unittest.TestCase):
    def test_native_camera_only_interface(self):
        # AppTest does not start a browser's WebRTC stream.
        with patch("streamlit_webrtc.webrtc_streamer") as camera:
            app = AppTest.from_file(
                str(Path(__file__).resolve().parents[1] / "app.py")
            ).run(timeout=20)
            self.assertFalse(app.exception)
            self.assertEqual(len(app.radio), 0)
            self.assertEqual(len(app.get("file_uploader")), 0)
            self.assertFalse(
                camera.call_args.kwargs["media_stream_constraints"]["audio"]
            )
            self.assertTrue(callable(camera.call_args.kwargs["video_frame_callback"]))
            app.button[1].click().run(timeout=20)  # New photo
            self.assertFalse(app.exception)
