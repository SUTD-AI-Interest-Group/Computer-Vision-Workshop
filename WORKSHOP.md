# Build the hand-to-game pipeline

This exercise is for intermediate Python coders. You will use a pretrained **hand-pose estimation** model, interpret its landmarks, and connect gestures to a game. You are not training a model or implementing full-body pose estimation.

## How the blanks work

Search for `TODO(` in `vision.py`, `gestures.py`, and `session.py`. Each call deliberately raises `ExerciseIncomplete` with an exercise number. Replace the call with an expression or a block of Python. Multiple blanks can belong to the same exercise. Imports, method signatures, and data structures are supplied. Do not change the helper to hide unfinished work.

The starter opens normally and continues displaying video when a blank is reached. Later tasks unlock as earlier ones are completed. Stop the stream before editing; start it again after the app reloads. Restart Streamlit if an edited module remains cached. The solution is available separately for instructor review, never loaded automatically.

## Data contracts

- `camera`: a mirrored, square, 600 × 600 BGR NumPy array. Do not mirror again.
- `now`: monotonic time in **seconds**. MediaPipe alone uses integer milliseconds.
- `Hand`: an identity (`Left` or `Right`), 21 normalized `(x, y)` landmarks, and an action string. The cursor is the index fingertip.
- `Pinch`: state for one identity. `armed` means an open hand was seen; `held` means a grab is active; `since` marks the start of a possible pinch.
- `board[position]`: tile ID at a row-major position from 0 to 8. All nine tiles move; there is no empty cell.
- `self.held`: either `None` or `(hand_identity, origin_cell)`. Only that hand may release the tile.

## Part A — MediaPipe (`vision.py`)

### 1. Create the detector

Use the imported MediaPipe Tasks API and supplied `MODEL_PATH` to create a `HandLandmarker`. Configure VIDEO mode, two hands, and 0.6 for detection, presence, and tracking confidence. Assign it to `self.model` so the provided `close()` can release it.

**Check:** `test_video_model_configuration_and_cleanup` in `tests/test_vision.py`.

### 2. Prepare a frame and run inference

Convert the BGR frame to RGB without modifying the input. Wrap it in an SRGB `mp.Image`. Convert `now` to milliseconds and ensure the timestamp is greater than `self.last_timestamp`, even if the clock value repeats. Save the new timestamp, call video inference, and assign its output to `result`.

**Think:** Why does sending seconds, or an equal timestamp, violate this API's contract?

**Check:** `test_rgb_and_strictly_increasing_milliseconds` (also needs exercise 3 to return an empty list).

### 3. Translate model results

Pair `result.handedness` and `result.hand_landmarks`. Build `Hand` objects with the classification label and all normalized `(x, y)` points. Reject confidence below 0.6 and any identity occurring more than once in a frame. Return an empty list for no accepted hands.

**Think:** Why can't result index 0 permanently identify the left hand?

**Check:** all tests in `test_vision.py`. Live milestone: landmarks reach the next unfinished interaction exercise. The app will pause processing there until that blank is filled.

## Part B — Gesture geometry (`gestures.py`)

### 4. Measure a pinch

Use the named landmark indices to measure thumb-tip to index-tip separation. Normalize by wrist-to-index-base distance. Return NaN if that scale is at most 0.01. The ratio should stay similar when the same hand moves closer to the camera.

**Check:** `test_normalized_geometry`. Example expectation: tip separation 0.08 and hand scale 0.2 produce a ratio of 0.4. That test also checks exercises 6 and 7.

### 5. Recognize gesture events

Implement `Pinch.update()` using these rules in order:

| Condition | State change and returned event |
| --- | --- |
| Measurement is not finite | Reset all state; `cancel` |
| Ratio above `OPEN_THRESHOLD` | Arm, clear held/timer; `release` if previously held, otherwise `open` |
| Already held | Keep holding; `hold` |
| Not armed, or ratio at/above `CLOSE_THRESHOLD` | Clear candidate timer; `idle` |
| First sufficiently closed measurement | Start candidate timer |
| Closed for less than `PINCH_HOLD_SECONDS` | `idle` |
| Closed long enough | Set held, disarm; `grab` |

A held pinch survives the gap between the close and open thresholds. This is hysteresis. Waiting for a sustained close is debounce. Neither should use sleeping; compare the frame timestamps.

**Check:** `test_rearm_debounce_and_hysteresis` and `test_invalid_measurement_cancels`.

### 6. Find a tile

Map a normalized point to a 3 × 3 row-major cell. Reject coordinates outside the half-open interval `[0, 1)`. A release beyond the board must return `None`, not snap to an edge tile.

**Check:** the geometry test. Add cases for all nine cell centers and each outside boundary.

### 7. Frame the captured photo

Convert the two normalized corners to rounded pixel coordinates and clamp them to `[0, size]`. Find the largest square centered inside their rectangle. Return `(x, y, side)` or `None` if the side is below 150 pixels. Reversing the hands must not change the result.

**Check:** the geometry test; add reversed-corner and boundary cases.

## Part C — Link detection to gameplay (`session.py`)

### 8. Landmarks → events

In `advance()`, connect each hand's points to `pinch_distance()` and its own `Pinch.update()`. Store the event in `hand.action`. Per-identity state, missing-hand cleanup, and jump rejection are already provided.

### 9. Events → interaction mode

Fill both dispatch blanks. A frame with no captured photo goes to `capture()` with the camera, hands, and time. A running puzzle goes to `drag()` with hands and time. Countdown, pause, and solved states are already handled.

### 10. Two-hand capture

Fill all three blanks in `capture()`:

- Calibration requires exactly two hands reporting `open`.
- Capture requires exactly two hands with held pinch states. Look up the states by identity; do not count `grab` events alone.
- Use both cursors and the camera size with your capture geometry function.

The supplied code handles the one-second calibration hold, 1.5-second capture hold, interruption resets, photo crop, tile splitting, and countdown. Understand each step before moving on.

**Check:** `test_capture_full_gesture_sequence` and `test_capture_loss_resets_hold`. Live milestone: capture a photo and see it scramble.

### 11. Pinch-drag → tile swap

Fill all three blanks in `drag()`:

- While holding, map the owner's cursor to the drop target.
- On owner release, call the game's swap method with origin, destination, and time only when the destination is valid. Store the boolean result in `swapped` so animation and completion history update only for successful swaps.
- When no tile is held, recognize a `grab` inside the board, assign ownership and origin to `self.held`, update the cursor, and return. Ignore other events.

Owner loss and invalid actions already cancel. Preserve those guards. Never treat a disappearing hand as a release.

**Check:** `test_owner_release_solves_once`, `test_loss_and_outside_release_do_not_swap`, then `test_landmarks_drive_a_complete_pinch_swap`. Run the entire suite when finished.

## Final camera checklist

1. Show two open hands, then hold two pinches to capture. Confirm the outlined square matches the photo.
2. Release during countdown. Grab one tile, move it, and open to swap.
3. Hide the grabbing hand. Confirm no unintended swap occurs.
4. Release outside the board; then reopen and try again.
5. Pause/resume, STOP/reconnect, and finish a complete puzzle.
6. Compare different camera distances and lighting. Record false grabs and responsiveness.

Synthetic tests cannot measure recognition accuracy or latency. Use the workshop laptops and room conditions for this final check.

## Instructor notes

Allow roughly 90–120 minutes, adjusting to participants' MediaPipe experience: 25 minutes for A, 30 for B, 30 for C, and the remainder for camera testing. The complete answer key and original tests are in `solution/`. Keep camera/threading/rendering infrastructure supplied so the session focuses on CV and interaction. Do not distribute `solution/` if answers should be withheld.
