# Snap & Solve · Python camera workshop

A camera-only hand-pose game written in Python. Show two open hands, pinch to capture a photo, then pinch-and-drag its nine tiles back into place. There are no demo, upload, keyboard, or mouse puzzle modes.

Streamlit provides the surrounding controls. `streamlit-webrtc` transports live camera frames to Python; MediaPipe estimates hand landmarks; OpenCV draws the puzzle and returns it as video. Our repository contains no application JavaScript, custom frontend, npm manifest, or build step. Streamlit/WebRTC still use their own browser code internally.

## Run

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/) and a working webcam. Python 3.12 is selected by `.python-version`.

```bash
uv sync --locked
uv run streamlit run app.py
```

Open the printed localhost URL. Click **START** and allow camera access. Audio is disabled. The versioned hand model is included under `models/`; if it is missing, restore and checksum-verify it with:

```bash
uv run scripts/download_model.py
```

The first dependency installation needs internet access. The model is loaded locally during play; the app makes no cloud inference requests. `uv add PACKAGE` updates dependencies; keep `pyproject.toml` and `uv.lock` together.

The headless OpenCV wheel is selected explicitly. `tool.uv.exclude-dependencies` excludes MediaPipe's desktop OpenCV dependency so two distributions do not compete for the same `cv2` import. Use uv for this environment.

## Play

1. Press **START**. Hold both open hands in the camera for one second.
2. Pinch your thumb and index finger on both hands at opposite corners of the desired photo. Hold for **1.5 seconds**. Move farther apart if prompted. The outline shows the square that will be saved.
3. Release your pinches during the three-second scramble countdown.
4. Point with your index finger, pinch to grab a tile, move onto another tile, and open your fingers to swap. All nine tiles move; there is no blank square.
5. Use native **Pause**, **Resume**, **Replay photo**, or **New photo** buttons. **STOP** releases the camera and pauses the current round; reconnect and press Resume to continue.

A lost hand or out-of-board release cancels a held tile. Reopen your hand before grabbing again. A stalled video stream pauses the stopwatch; a missing hand alone does not. Completed rounds are kept in session memory, up to 20 entries. Refreshing clears the session. New photo resets the puzzle but keeps the stream and history.

## Workshop reading order

Participants only need Python. This is **hand-pose estimation**, not full-body tracking or model training. A pretrained model predicts landmarks; our code translates those estimates into gestures.

```mermaid
flowchart LR
    A[Browser webcam] -->|WebRTC| B[Python video frame]
    B --> C[MediaPipe landmarks]
    C --> D[Pinch events]
    D --> E[Puzzle state]
    E --> F[OpenCV drawing]
    F -->|WebRTC| G[Browser video]
```

| Read | What it teaches |
| --- | --- |
| `gestures.py` | Landmark indices, normalized distances, pinch debounce and hysteresis, coordinates |
| `vision.py` | The actual MediaPipe `HandLandmarker` initialization and `detect_for_video()` call |
| `game.py` | Nine-tile board, shuffle, swaps, countdown, monotonic stopwatch |
| `session.py` → `receive()` | The complete frame-to-game pipeline in one place |
| `session.py` → `advance()`, `capture()`, `drag()` | Turning landmarks into game actions and maintaining hand ownership |
| `rendering.py` | Drawing landmarks, capture outlines, moving tiles, and the camera thumbnail |
| `app.py` | Native Streamlit controls and the WebRTC connection |

### Trace one pinch

MediaPipe's wrist, thumb tip, index base, and index tip IDs are named in `gestures.py`.

```text
pinch ratio = distance(thumb tip, index tip)
              / distance(wrist, index base)
```

A ratio below `CLOSE_THRESHOLD = 0.45` for `PINCH_HOLD_SECONDS = 0.1` produces a grab, provided the hand was open first. A held pinch releases only above `OPEN_THRESHOLD = 0.55`. The separate thresholds prevent jitter around one boundary (hysteresis); the hold duration ignores brief accidental pinches (debounce).

“Open” here means separated thumb and index fingertips. It is not a classifier that checks all five fingers. Hand-size normalization reduces sensitivity to camera distance, but the 2D geometry still depends on pose and occlusion.

`session.receive()` first mirrors and center-crops the camera image, so inference, display, and gestures share one coordinate system. `cell_at()` maps a normalized fingertip `(x, y)` to `row * 3 + column`, or returns `None` outside the board. `board[position]` stores a tile ID; both are numbered 0–8.

The hand that grabbed a tile owns that grab. Handedness labels identify hands; result-array positions do not. Losing an owner cancels the move rather than pretending its fingers opened. Python's `Game.swap()` updates the board and freezes the stopwatch on completion.

All game/gesture timestamps are **monotonic seconds**. Only `vision.py` converts them to strictly increasing milliseconds for MediaPipe's video API.

### Why there is a lock

WebRTC calls `receive()` on a worker thread. Streamlit buttons and the status fragment run on the UI thread. Both access the same player's game, so `CameraGame` uses a lock around each public entrypoint. The callback never calls `st.write`, `st.session_state`, or any other Streamlit API. `snapshot()` returns a small copy of status/history for the native UI.

Read the CV and gesture functions before studying this threading boundary. It is transport plumbing, not part of pose estimation.

### Suggested 75-minute lesson

| Time | Activity |
| --- | --- |
| 0–10 min | Start the webcam; trace `receive()` and distinguish estimation from gesture rules |
| 10–25 min | Inspect `vision.py`; identify landmarks and calculate a pinch ratio |
| 25–40 min | Follow `Pinch.update()` and compare debounce settings |
| 40–55 min | Follow coordinate mapping and the two-hand capture hold |
| 55–65 min | Trace grab ownership, release, a tile swap, and completion |
| 65–75 min | Test occlusion, lighting, and camera distance; explain failure cases |

### Small exercises

1. Change the pinch debounce from 0.1 to 0.2 seconds. Predict the effect; update the timing assertions in `tests/test_gestures.py` without removing the brief-pinch rejection check.
2. Add `cell_at()` tests for every corner and out-of-board coordinates. Explain why an out-of-board release cancels.
3. Explain what happens when the grabbing hand leaves the frame but the other hand remains. Confirm it with `test_loss_and_outside_release_do_not_swap`.
4. Try two camera distances and record cursor responsiveness and false grabs. Explain what hand-size normalization helps with and what it cannot fix.

## Verify

```bash
uv run python -m unittest discover -s tests -v
```

Tests use synthetic landmarks and frames to check the game loop deterministically. AppTest mocks WebRTC. See `TEST_REPORT.md` for actual runtime checks and limits. These tests do not measure real-world gesture accuracy.

## Camera, privacy, and deployment

Unlike the earlier JavaScript version, **live video is sent to the Python server** for inference and rendering. Running locally keeps that server on the participant's laptop. Hosting remotely sends participants' video to that host. No video or captured photo is written to disk by the game; the model file is not a recording.

This configuration targets one local server per participant. Camera permission requires localhost or HTTPS. It deliberately uses no external ICE servers; deploying across networks/NAT may require STUN/TURN configuration in `app.py`. No remote deployment is included.

Responsiveness depends on camera capture, Python inference, video encoding, and transport. Tiles are pixels in the outgoing video, not browser buttons. Animation updates only while frames arrive. This is suitable for teaching the Python pipeline; compare performance on workshop hardware before the event.

Test the actual laptops, camera permissions, room lighting, two-hand capture, pinch dragging, tracking loss, stream restart, and camera shutdown before the workshop.

## Source and licensing

Adapted from [SUTD AIIG's Snap-Solve-NAISC-2026](https://github.com/SUTD-AI-Interest-Group/Snap-Solve-NAISC-2026). Original MIT attribution remains in `LICENSE`. See `THIRD_PARTY_NOTICES.md` for libraries and the bundled model.
