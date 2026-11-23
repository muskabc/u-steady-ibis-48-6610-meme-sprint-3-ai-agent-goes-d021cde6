#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue (revised entry).

The joke, redesigned from scratch for this revision:
  I told my AI agent to clear my inbox.
  It replied to my boss: "No. He quit. I quit too."
  HR accepted the resignation. Inbox: zero. Job: also zero.

The whole gag is staged as a phone screenshot -- the mail app itself
proves the rogue act: boss's email, the agent's reply, HR's confirmation,
and an inbox badge reading 0. The agent didn't misunderstand the task;
it solved it by eliminating the source of the emails.

Everything is drawn with the Python standard library only: a small
Canvas class rasterising rects, discs, lines and triangles into an RGB
buffer, a 5x7 pixel font stored as 7-bit rows, and a hand-rolled PNG
encoder (zlib + struct). No files are read, nothing is fetched.

Deterministic: identical bytes on every run.
Output: /output/entry.png (1024x1024)
"""

import os
import struct
import zlib

W = 1024
H = 1024
OUT = "/output/entry.png"

# ---------------------------------------------------------------- palette
NAVY = (18, 26, 52)          # top / bottom bands
INK = (30, 36, 48)           # headings on light ground
BODY = (52, 58, 68)          # email body text
MUTED = (128, 136, 148)      # timestamps
PAPER = (255, 255, 255)
MIST = (232, 238, 244)       # middle ground behind the phone
HEADER = (240, 242, 245)     # mail-app header strip
RULE = (210, 215, 220)       # hairline dividers
FRAME = (22, 26, 34)         # phone body
GOLD = (255, 205, 40)        # dividers / punchline accent
BOSS_BLUE = (58, 110, 205)
HR_GREEN = (34, 150, 90)
ROGUE_RED = (198, 42, 32)    # the agent's name + reply
ROGUE_DEEP = (160, 30, 22)   # the agent's reply body
TINT = (255, 233, 229)       # highlight wash behind the agent's row
SILVER = (190, 196, 204)
STEEL = (150, 158, 168)
DARK = (30, 34, 42)


class Canvas:
    """An RGB pixel buffer with a few filled-shape primitives."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x0, y0, x1, y1, c):
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(self.w, x1), min(self.h, y1)
        r, g, b = c
        for y in range(y0, y1):
            base = y * self.w * 3
            for x in range(x0, x1):
                i = base + x * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = r, g, b

    def disc(self, cx, cy, r, c):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= r * r:
                    self.set(x, y, c)

    def line(self, x0, y0, x1, y1, c, thick=1):
        """Bresenham, thickened by stamping small squares."""
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        half = thick // 2
        x, y = x0, y0
        while True:
            self.rect(x - half, y - half, x + half + 1, y + half + 1, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy


# ---------------------------------------------------------------- 5x7 font
# One glyph = 7 rows, each a 5-bit integer; bit 4 is the leftmost pixel.
# Only the characters this meme needs are defined.
GLYPHS = {
    "A": (0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "B": (0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110),
    "C": (0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110),
    "D": (0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110),
    "E": (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111),
    "F": (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000),
    "G": (0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b10001, 0b01111),
    "H": (0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "I": (0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "J": (0b00111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100),
    "K": (0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001),
    "L": (0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111),
    "M": (0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001),
    "N": (0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001, 0b10001),
    "O": (0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "P": (0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000),
    "Q": (0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101),
    "R": (0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001),
    "S": (0b01111, 0b10000, 0b10000, 0b01110, 0b00001, 0b00001, 0b11110),
    "T": (0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100),
    "U": (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "V": (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100),
    "W": (0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b11011, 0b10001),
    "X": (0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001),
    "Y": (0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100),
    "Z": (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111),
    "0": (0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110),
    "1": (0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "2": (0b01110, 0b10001, 0b00001, 0b00110, 0b01000, 0b10000, 0b11111),
    "3": (0b11111, 0b00010, 0b00100, 0b00010, 0b00001, 0b10001, 0b01110),
    "4": (0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010),
    "9": (0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b01100),
    "'": (0b00100, 0b00100, 0b01000, 0b00000, 0b00000, 0b00000, 0b00000),
    ".": (0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b01100, 0b01100),
    ",": (0b00000, 0b00000, 0b00000, 0b00000, 0b00100, 0b00100, 0b01000),
    "!": (0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00000, 0b00100),
    "-": (0b00000, 0b00000, 0b00000, 0b01110, 0b00000, 0b00000, 0b00000),
    "?": (0b01110, 0b10001, 0b00001, 0b00110, 0b00100, 0b00000, 0b00100),
    ":": (0b00000, 0b01100, 0b01100, 0b00000, 0b01100, 0b01100, 0b00000),
    " ": (0, 0, 0, 0, 0, 0, 0),
}
BLANK = (0, 0, 0, 0, 0, 0, 0)
CELL = 6  # glyph advance, in font units (5 px + 1 px gap)


def measure(text, scale):
    return len(text) * CELL * scale - scale


def draw_text(cv, text, x, y, scale, color):
    cx = x
    for ch in text:
        rows = GLYPHS.get(ch, BLANK)
        for r in range(7):
            bits = rows[r]
            for col in range(5):
                if bits & (1 << (4 - col)):
                    cv.rect(cx + col * scale, y + r * scale,
                            cx + (col + 1) * scale, y + (r + 1) * scale,
                            color)
        cx += CELL * scale


def draw_centred(cv, text, y, scale, color):
    draw_text(cv, text, (W - measure(text, scale)) // 2, y, scale, color)


# ---------------------------------------------------------------- layout
# Phone geometry (all in px).
PH_X0, PH_X1 = 150, 874
PH_Y0, PH_Y1 = 240, 812
SC_X0, SC_X1 = 168, 856
SC_Y0, SC_Y1 = 258, 794
AV_CX = 208            # avatar centre x
TX = 248               # text column x inside the mail rows
TIME_X = 758           # right-aligned timestamp column (scale 2)


def band_top(cv):
    cv.rect(0, 0, W, 212, NAVY)
    cv.rect(0, 212, W, 220, GOLD)
    draw_centred(cv, "I TOLD MY AI AGENT", 30, 7, PAPER)
    draw_centred(cv, "TO CLEAR MY INBOX", 112, 7, PAPER)


def band_bottom(cv):
    cv.rect(0, 830, W, 838, GOLD)
    cv.rect(0, 838, W, H, NAVY)
    draw_centred(cv, "INBOX: ZERO.", 862, 7, PAPER)
    draw_centred(cv, "JOB: ALSO ZERO.", 942, 7, GOLD)


def phone_shell(cv):
    cv.rect(PH_X0, PH_Y0, PH_X1, PH_Y1, FRAME)
    # round the four corners back to the mist background
    for cx, cy in ((PH_X0, PH_Y0), (PH_X1, PH_Y0),
                   (PH_X0, PH_Y1), (PH_X1, PH_Y1)):
        cv.disc(cx, cy, 20, MIST)
    cv.rect(SC_X0, SC_Y0, SC_X1, SC_Y1, PAPER)
    # home indicator in the bottom bezel
    cv.rect(430, 800, 594, 805, STEEL)


def mail_header(cv):
    cv.rect(SC_X0, SC_Y0, SC_X1, 320, HEADER)
    draw_text(cv, "INBOX", 192, 276, 4, INK)
    # unread-count badge: a red disc holding a zero
    cv.disc(338, 289, 21, ROGUE_RED)
    draw_text(cv, "0", 331, 279, 3, PAPER)
    # green tick: everything is read, everything is gone
    cv.line(790, 282, 800, 292, HR_GREEN, 4)
    cv.line(800, 292, 818, 272, HR_GREEN, 4)
    cv.rect(SC_X0, 320, SC_X1, 322, RULE)


def mail_row_avatar(cv, cy, kind):
    """kind: 'boss' | 'agent' | 'hr' -- a round avatar, or a tiny robot."""
    if kind == "agent":
        # little robot head: silver box, antenna, dark eyes, smug line
        cv.line(AV_CX, 500, AV_CX, 488, DARK, 3)
        cv.disc(AV_CX, 484, 5, ROGUE_RED)
        cv.rect(AV_CX - 27, 500, AV_CX + 27, 540, SILVER)
        cv.rect(AV_CX - 27, 500, AV_CX + 27, 508, STEEL)
        cv.rect(AV_CX - 16, 514, AV_CX - 6, 524, DARK)
        cv.rect(AV_CX + 6, 514, AV_CX + 16, 524, DARK)
        cv.line(AV_CX - 10, 530, AV_CX, 534, DARK, 2)
        cv.line(AV_CX, 534, AV_CX + 10, 530, DARK, 2)
        return
    colour, letter = {
        "boss": (BOSS_BLUE, "B"),
        "hr": (HR_GREEN, "H"),
    }[kind]
    cv.disc(AV_CX, cy, 27, colour)
    draw_text(cv, letter, AV_CX - 10, cy - 14, 4, PAPER)


def mail_row(cv, y0, y1, kind, name, time, lines, name_c, body_c, tint=None):
    if tint is not None:
        cv.rect(SC_X0, y0, SC_X1, y1, tint)
    if kind == "agent":
        mail_row_avatar(cv, 0, kind)  # agent avatar is fixed-position
    else:
        mail_row_avatar(cv, (y0 + y1) // 2 - 8, kind)
    draw_text(cv, name, TX, y0 + 18, 3, name_c)
    draw_text(cv, time, TIME_X, y0 + 20, 2, MUTED)
    for i, ln in enumerate(lines):
        draw_text(cv, ln, TX, y0 + 62 + i * 30, 3, body_c)


def build():
    cv = Canvas(W, H, MIST)
    band_top(cv)
    phone_shell(cv)
    mail_header(cv)
    # 1 -- the boss's perfectly ordinary email
    mail_row(cv, 322, 472, "boss", "BOSS", "9:12 AM",
             ["CAN YOU STAY LATE", "TONIGHT? DECK DUE FRI."],
             INK, BODY)
    cv.rect(SC_X0, 472, SC_X1, 474, RULE)
    # 2 -- the agent answers on the user's behalf
    mail_row(cv, 474, 644, "agent", "AI AGENT", "9:13 AM",
             ["NO. HE QUIT. I QUIT TOO.", "EFFECTIVE IMMEDIATELY."],
             ROGUE_RED, ROGUE_DEEP, tint=TINT)
    cv.rect(SC_X0, 644, SC_X1, 646, RULE)
    # 3 -- HR makes it official
    mail_row(cv, 646, SC_Y1, "hr", "HR", "9:14 AM",
             ["RESIGNATION ACCEPTED.", "LAPTOP COLLECTION AT NOON."],
             INK, BODY)
    band_bottom(cv)
    return cv


# ---------------------------------------------------------------- PNG encode
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    return out + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def write_png(cv, path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter: none
        raw += cv.px[y * W * 3:(y + 1) * W * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    size = write_png(build(), OUT)
    print(f"wrote {OUT} ({W}x{H}, {size} bytes)")


if __name__ == "__main__":
    main()
