"""Restore the bundled, versioned MediaPipe model: uv run scripts/download_model.py."""

from hashlib import sha256
from pathlib import Path
from urllib.request import urlopen

URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
SHA256 = "fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1"
path = Path(__file__).resolve().parents[1] / "models" / "hand_landmarker.task"
with urlopen(URL, timeout=60) as response:
    data = response.read()
if sha256(data).hexdigest() != SHA256:
    raise RuntimeError("Model checksum mismatch; existing file was not changed.")
path.parent.mkdir(parents=True, exist_ok=True)
path.write_bytes(data)
print(f"Verified model saved to {path}")
