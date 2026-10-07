# Workshop scaffold verification — 2026-10-07

## Preserved solution

- Copied 22 original files into `solution/`, including source, model, lockfile, configuration, tests, README, and licenses. Excluded environment/cache files.
- Verified all file hashes against `solution/SNAPSHOT.json` after editing the participant starter. The solution is unchanged.
- All 20 original solution tests pass.
- Three new participant MediaPipe contract tests also pass against the solution implementation. These mock model output and verify configuration/cleanup, RGB conversion/timestamps, and stable identities/confidence filtering.
- The full 23-test participant acceptance suite also passes when run against the solution modules.
- Historical real-camera checks are recorded in `solution/TEST_REPORT.md`; a complete physical pinch-drag solve remains unverified.

## Participant starter

- Replaced CV and interaction logic with 11 numbered exercises across vision.py, gestures.py, and session.py. No automatic solution imports or fallback exist.
- Source parses. Provided game rules (3 tests) and app shell (1 test) pass.
- Synthetic frame check confirms an unfinished exercise returns a 600 × 710 video frame with an Exercise 1 message, and camera cleanup resets the error.
- Live browser check at localhost:8517 confirmed the Practice banner, working camera video, and the Exercise 1 message. STOP released the stream and restored the camera-stopped status.
- The complete 23-test participant suite is intentionally not green: unfinished exercises fail acceptance tests. The supplied infrastructure accounts for 10 passing tests; 13 checks still require participant code.
- WORKSHOP.md supplies contracts, behavior tables, hints, and test checkpoints. README provides separate participant and solution launch commands.

## Limits

- Automated checks do not establish camera accuracy, latency, or workshop readiness. Use the live checklist in WORKSHOP.md after completing the exercises.
- The solution copy is an answer key. Exclude it when distributing materials if participants should not see answers.
