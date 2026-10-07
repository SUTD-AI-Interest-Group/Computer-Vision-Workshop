"""Native Streamlit controls around a camera-only, Python-rendered CV game."""

import streamlit as st
from streamlit_webrtc import WebRtcMode, webrtc_streamer

from session import CameraGame

st.set_page_config(
    page_title="Snap & Solve · Camera", page_icon="🧩", layout="centered"
)
st.title("🧩 Snap & Solve · Practice")
st.info(
    "Participant starter: complete exercises 1–11 in WORKSHOP.md. "
    "Camera video works; tracking and gameplay unlock as you fill the blanks."
)
st.write("Capture a photo with two pinches, then rebuild it using your hands.")
st.caption(
    "Live camera frames are processed by this Python server. Audio is disabled; video is not recorded."
)

# Keep one game per browser session. The video callback runs on a worker thread;
# CameraGame's lock protects it from simultaneous native button interactions.
if "camera_game" not in st.session_state:
    st.session_state.camera_game = CameraGame()
session = st.session_state.camera_game

webrtc_streamer(
    key="camera_puzzle",
    mode=WebRtcMode.SENDRECV,
    video_frame_callback=session.receive,
    on_video_ended=session.close,
    media_stream_constraints={
        "video": {
            "width": {"ideal": 640},
            "height": {"ideal": 480},
            "frameRate": {"ideal": 24, "max": 30},
        },
        "audio": False,
    },
    # Local workshop setup: no external STUN/TURN dependency. Remote hosting
    # across NAT/firewalls needs ICE server configuration (see README).
    rtc_configuration={"iceServers": []},
    async_processing=True,
    media_toggle_controls=False,
    video_html_attrs={
        "autoPlay": True,
        "controls": False,
        "muted": True,
        # Show a larger playing area; contain keeps the entire frame and footer
        # visible. The page scrolls normally on shorter screens.
        "style": {
            "width": "100%",
            "height": "600px",
            "objectFit": "contain",
        },
    },
)


@st.fragment(run_every=0.5)
def controls():
    state = session.snapshot()
    if state["error"]:
        st.error(
            state["error"] + " After editing, stop and restart the camera to retry."
        )
    else:
        st.info(state["status"])
    if state["phase"] == "solved":
        st.success(
            f"Solved in {state['seconds']:.2f} seconds with {state['moves']} swaps!"
        )
    left, middle, right = st.columns(3)
    if state["phase"] in ("running", "countdown"):
        left.button("Pause", on_click=session.command, args=("pause",))
    elif state["phase"] == "paused":
        left.button(
            "Resume",
            disabled=not state["connected"] or bool(state["error"]),
            on_click=session.command,
            args=("resume",),
        )
    middle.button(
        "Replay photo",
        disabled=state["phase"] != "solved" or not state["connected"],
        on_click=session.command,
        args=("replay",),
    )
    right.button("New photo", on_click=session.command, args=("new",))
    if state["history"]:
        with st.expander("Completed rounds this session"):
            st.dataframe(list(reversed(state["history"])), hide_index=True)


controls()
with st.expander("How to play", expanded=False):
    st.markdown("""
1. Press **START** and allow camera access.
2. Show both open hands for one second.
3. Pinch with both hands at opposite corners. Hold for **1.5 seconds** to capture the outlined square.
4. Release during the countdown. Point at a tile, **pinch to grab**, move, and **open to drop** onto another tile.
5. Use **Pause** before stepping away. **STOP** releases the camera and pauses the puzzle.

If your hand disappears, the held tile returns without swapping. Reopen your hand before trying again.
""")
