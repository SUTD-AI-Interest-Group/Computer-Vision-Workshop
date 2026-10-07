"""OpenCV draws the game into the outgoing video; no browser interaction code."""

import cv2
import numpy as np

BOARD_PIXELS = 600
TILE_PIXELS = BOARD_PIXELS // 3
HAND_CHAINS = (
    (0, 1, 2, 3, 4),
    (0, 5, 6, 7, 8),
    (5, 9, 10, 11, 12),
    (9, 13, 14, 15, 16),
    (13, 17, 18, 19, 20),
    (0, 17),
)


def camera_square(image):
    """Mirror once, then crop; inference and drawing use the same coordinates."""
    height, width = image.shape[:2]
    side = min(height, width)
    x, y = (width - side) // 2, (height - side) // 2
    return cv2.resize(cv2.flip(image[y : y + side, x : x + side], 1), (600, 600))


def paste_tile(canvas, tile, x, y, color):
    """Clipped drawing allows a held tile to move beyond the board edges."""
    x, y = round(x), round(y)
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(600, x + 200), min(600, y + 200)
    if x0 < x1 and y0 < y1:
        canvas[y0:y1, x0:x1] = tile[y0 - y : y1 - y, x0 - x : x1 - x]
        cv2.rectangle(canvas, (x0, y0), (x1 - 1, y1 - 1), color, 2)


def draw(session, camera, hands, now):
    canvas = camera.copy() if session.photo is None else np.full_like(camera, 22)
    if session.photo is not None:
        duration = session.animation_duration
        progress = min(1, max(0, (now - session.animation_started) / duration))
        progress = 1 - (1 - progress) ** 3  # Ease-out motion between cells.
        for position, tile_id in enumerate(session.game.board):
            if session.held and position == session.held[1]:
                continue
            old = session.previous_board.index(tile_id)
            x = ((old % 3) * (1 - progress) + (position % 3) * progress) * 200
            y = ((old // 3) * (1 - progress) + (position // 3) * progress) * 200
            tile = session.tiles[tile_id]
            color = (100, 220, 100) if tile_id == position else (55, 65, 55)
            paste_tile(canvas, tile, x, y, color)
        if session.held:
            _, position = session.held
            x, y = session.cursor
            if session.target is not None:
                tx, ty = (session.target % 3) * 200, (session.target // 3) * 200
                cv2.rectangle(
                    canvas, (tx + 2, ty + 2), (tx + 198, ty + 198), (80, 220, 255), 5
                )
            paste_tile(
                canvas,
                session.tiles[session.game.board[position]],
                x * 600 - 100,
                y * 600 - 100,
                (80, 220, 255),
            )
    if session.capture_rect:
        x, y, side = session.capture_rect
        cv2.rectangle(canvas, (x, y), (x + side, y + side), (80, 220, 255), 3)
    for hand in hands:
        points = [(round(x * 600), round(y * 600)) for x, y in hand.points]
        for chain in HAND_CHAINS:
            cv2.polylines(
                canvas, [np.array([points[i] for i in chain])], False, (90, 180, 90), 1
            )
        cv2.circle(canvas, points[8], 12, (80, 220, 255), 3)
    if session.game.phase == "countdown":
        cv2.putText(
            canvas,
            str(session.game.remaining(now)),
            (255, 330),
            cv2.FONT_HERSHEY_SIMPLEX,
            3,
            (255, 255, 255),
            6,
        )
    footer = np.full((110, 600, 3), (22, 30, 24), dtype=np.uint8)
    cv2.putText(
        footer,
        f"{session.game.elapsed(now):.1f}s   Swaps: {session.game.moves}",
        (15, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (220, 240, 220),
        2,
    )
    # Full instructions also appear as native Streamlit text below the video.
    cv2.putText(
        footer,
        session.game.phase.upper(),
        (15, 68),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (160, 220, 160),
        1,
    )
    if session.photo is not None:
        footer[5:105, 490:590] = cv2.resize(camera, (100, 100))
    return np.vstack([canvas, footer])
