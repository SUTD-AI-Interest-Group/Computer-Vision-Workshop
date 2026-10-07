# Computer Vision Workshop

SUTD AI Interest Group · Snap & Solve participant practice

Build a hand-controlled camera puzzle in Python. The working game has been preserved in **`solution/`**. The project root is now the participant starter: camera streaming, drawing, animations, and puzzle rules are provided; the computer vision and gesture-to-game logic contain **11 numbered exercises**.

## Run the participant starter

```bash
uv sync --locked
uv run streamlit run app.py
```

Python 3.12 is selected by `.python-version`. Press START to see your camera. An unfinished exercise displays its number and instructions; this is expected, not a setup failure. Read **[WORKSHOP.md](WORKSHOP.md)** and replace each `TODO(...)` call with your implementation. Stop the camera before editing, then restart it after Streamlit reloads. If old imports remain cached, restart the Streamlit process.

No keyboard, mouse-tile, upload, or demo modes are included. The participant code never imports or falls back to `solution/`.

## Run the complete solution

From this project's root:

```bash
cd solution
uv sync --locked
uv run streamlit run app.py --server.port 8518
```

Using a second port lets you compare it with the starter. This folder is self-contained, including its own model, lockfile, tests, notices, and original README. `solution/SNAPSHOT.json` records the checksums of the preserved files. It is the answer key; distribute the root without `solution/` if participants should not receive answers.

## Where to work

| File | Participant work |
| --- | --- |
| `vision.py` | Exercises 1–3: create MediaPipe, infer landmarks, keep stable hand identities |
| `gestures.py` | Exercises 4–7: normalized pinch distance, gesture state machine, grid and capture geometry |
| `session.py` | Exercises 8–11: connect landmarks to events, capture a photo, grab and swap tiles |
| `practice.py` | Placeholder helper; leave it unchanged |
| `game.py`, `rendering.py`, `app.py` | Provided puzzle rules, drawing, and native Streamlit UI |

## Check your progress

```bash
# Provided puzzle rules and app shell should already pass:
uv run python -m unittest discover -s tests -p test_game.py -v
uv run python -m unittest discover -s tests -p test_app.py -v

# Complete vision.py, then gestures.py, then session.py:
uv run python -m unittest discover -s tests -p test_vision.py -v
uv run python -m unittest discover -s tests -p test_gestures.py -v
uv run python -m unittest discover -s tests -p test_session.py -v

# Final participant acceptance check:
uv run python -m unittest discover -s tests -v
```

The full suite intentionally fails while required exercises are blank. Do not remove tests, skip failures, or change `TODO()` to return fake data. Vision checks mock MediaPipe's output; interaction checks use synthetic landmarks. Passing them does not establish physical hand-tracking accuracy. Finish with the camera checklist in WORKSHOP.md.

## Camera and dependencies

MediaPipe and game rendering run on the Python server. With a local server, frames remain on your laptop; a remote server receives the video. Audio is disabled; the app does not write photos or video to disk. The bundled model loads locally, and the first dependency installation needs internet.

The default is one local server per participant. Remote hosting needs HTTPS and may need STUN/TURN configuration. Streamlit and streamlit-webrtc include internal browser JavaScript; there is no custom application JavaScript or npm step.

Use uv and keep `pyproject.toml` with `uv.lock`. The headless OpenCV dependency deliberately replaces MediaPipe's desktop OpenCV wheel. Restore a missing model with `uv run scripts/download_model.py`.

Original [Snap-Solve-NAISC-2026](https://github.com/SUTD-AI-Interest-Group/Snap-Solve-NAISC-2026) attribution remains in LICENSE. See THIRD_PARTY_NOTICES.md and TEST_REPORT.md.
