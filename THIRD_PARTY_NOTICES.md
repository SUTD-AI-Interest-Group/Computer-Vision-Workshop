# Third-party notices

- Original Snap & Solve: Copyright (c) 2026 SUTD AIIG, MIT. Attribution retained in `LICENSE`. https://github.com/SUTD-AI-Interest-Group/Snap-Solve-NAISC-2026
- Streamlit: Apache-2.0. https://github.com/streamlit/streamlit
- streamlit-webrtc: MIT. https://github.com/whitphx/streamlit-webrtc
- MediaPipe: Apache-2.0. https://github.com/google-ai-edge/mediapipe
- OpenCV: Apache-2.0 (with third-party component notices). https://github.com/opencv/opencv
- NumPy: BSD-3-Clause. https://github.com/numpy/numpy
- PyAV: BSD-3-Clause; distributed wheels include FFmpeg components and their notices. https://github.com/PyAV-Org/PyAV

Installed distributions include their own license notices. Exact Python versions are recorded in `uv.lock`.

Bundled model: Google MediaPipe Hand Landmarker float16, version 1.
Source: https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
SHA-256: `fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1`.
Model documentation: https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker
The Apache-2.0 license text is retained in `licenses/Apache-2.0.txt`.

No custom JavaScript frontend or browser-downloaded MediaPipe runtime remains in this repository. Streamlit and streamlit-webrtc supply their own browser assets through their installed distributions.
