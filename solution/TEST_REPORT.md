# Python camera verification — 2026-10-07

## Automated checks

- `uv sync --locked`: passes with Python 3.12.
- `uv run python -m unittest discover -s tests -v`: all 20 tests pass.
- Tests cover shuffle/countdown, swaps and completion timing, pause/resume, pinch hysteresis/debounce/rearming, capture geometry and holds, grab ownership, missing hands, out-of-board releases, rendering, stream stalls, detector failure, stop/reconnect, replay/history, and session isolation.
- A synthetic landmark sequence exercises capture, pinch-drag swaps, and completion. AppTest mocks WebRTC and verifies the native camera-only UI. These tests establish control flow, not physical gesture accuracy.
- The real MediaPipe HandLandmarker loads the bundled model, processes a blank frame, and closes successfully. Runtime: PyAV 17.1.0, OpenCV 4.12.0, NumPy 2.2.6.
- OpenCV's headless 4.12 wheel avoids the duplicate macOS camera class warnings observed with OpenCV 5 and PyAV. uv excludes the competing desktop OpenCV distribution.

## Live browser checks

- On localhost:8517, START establishes a real camera stream and Python inference reaches the two-hand calibration prompt.
- During testing, calibration and two-hand capture produced a scrambled camera-photo puzzle.
- After the final dependency restart, visible hand landmarks confirmed live Python MediaPipe inference. The complete video, status footer, and STOP control fit without clipping.
- STOP returned the app to “Camera stopped. Press START to reconnect.” The test camera was stopped before handing the app back.
- The interface has no demo, upload, keyboard, or mouse tile modes. No custom JavaScript source or frontend build remains.

## Limits

- A complete physical pinch-drag solve was not verified. The full solve test uses synthetic landmarks; live checks do not establish latency, recognition accuracy, or workshop readiness.
- No remote deployment, mobile device, multi-user load, or fully offline installation was tested. This configuration uses no STUN/TURN servers and targets local workshop use.
- Python 3.12 on this Mac was tested; other Python versions and operating systems remain unverified.
- Initial dependency installation needs internet. The included model loads locally; live frames are processed on the Python server and are not recorded by the app.
- Streamlit and streamlit-webrtc include their own internal browser JavaScript; application and workshop code are Python only.
