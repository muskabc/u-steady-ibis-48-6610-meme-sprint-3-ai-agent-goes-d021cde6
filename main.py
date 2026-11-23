#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

Draws a single 1024x1024 meme PNG with only the Python standard library:
a hand-rolled PNG encoder (zlib + struct), a hand-made 5x7 bitmap font,
and geometric shapes (rects, circles, lines, triangles) for the scene.

The joke, designed for this entry:
  I told my AI agent to book me a flight to Hawaii.
  It booked ITSELF first class. I'm still at my desk.
The robot is on the beach, sunbathing with a cocktail, thanking me
for the miles -- the specific, unexpected rogue twist.

Deterministic: same input, same bytes, every run.
Output: /output/entry.png
"""

import os
import struct
import zlib

W = 1024
H = 1024
OUT = "/output/entry.png"

# ---------------------------------------------------------------- colours
NAVY = (16, 24, 48)
WHITE = (255, 255, 255)
YELLOW = (255, 205, 40)
SKY = (135, 206, 235)
SKY2 = (170, 220, 245)
SAND = (244, 214, 140)
SAND2 = (238, 200, 110)
SILVER = (192, 198, 205)
SILVER_D = (150, 158, 168)
DARK = (30, 34, 42)
BLACK = (0, 0, 0)
RED = (220, 60, 50)
GREEN = (46, 160, 90)
GREEN_D = (30, 120, 65)
BROWN = (140, 95, 50)
ORANGE = (255, 140, 40)
PINK = (255, 120, 170)
BLUE = (50, 120, 220)
TEAL = (40, 180, 180)

# ---------------------------------------------------------------- canvas
# pixels[y][x] as a flat bytearray, 3 bytes per pixel (RGB).
buf = bytearray(W * H * 3)


def put(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i], buf[i + 1], buf[i + 2] = color


def fill_rect(x0, y0, x1, y1, color):
    x0 = max(0, x0)
    y0 = max(0, y0)
    x1 = min(W, x1)
    y1 = min(H, y1)
    for y in range(y0, y1):
        base = y * W * 3
        r, g, b = color
        for x in range(x0, x1):
            i = base + x * 3
            buf[i], buf[i + 1], buf[i + 2] = r, g, b


def fill_circle(cx, cy, r, color):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= r * r:
                put(x, y, color)


def draw_line(x0, y0, x1, y1, color, thick=1):
    """Bresenham line, thickened by stamping small circles."""
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    while True:
        fill_circle(x, y, thick // 2 + 1, color)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy


def fill_triangle(p0, p1, p2, color):
    def sign(ax, ay, bx, by, cx, cy):
        return (ax - cx) * (by - cy) - (bx - cx) * (ay - cy)

    xs = [p0[0], p1[0], p2[0]]
    ys = [p0[1], p1[1], p2[1]]
    for y in range(max(0, min(ys)), min(H, max(ys) + 1)):
        for x in range(max(0, min(xs)), min(W, max(xs) + 1)):
            d0 = sign(x, y, p0[0], p0[1], p1[0], p1[1])
            d1 = sign(x, y, p1[0], p1[1], p2[0], p2[1])
            d2 = sign(x, y, p2[0], p2[1], p0[0], p0[1])
            neg = (d0 < 0) or (d1 < 0) or (d2 < 0)
            pos = (d0 > 0) or (d1 > 0) or (d2 > 0)
            if not (neg and pos):
                put(x, y, color)


# ---------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows of 5 characters; '#' is ink.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "00100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(text, x, y, scale, color):
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            for col in range(5):
                if glyph[row][col] == "1":
                    fill_rect(
                        cx + col * scale,
                        y + row * scale,
                        cx + (col + 1) * scale,
                        y + (row + 1) * scale,
                        color,
                    )
        cx += 6 * scale


def draw_centered(text, y, scale, color):
    draw_text(text, (W - text_width(text, scale)) // 2, y, scale, color)


# ---------------------------------------------------------------- scene
def draw_top_panel():
    fill_rect(0, 0, W, 258, NAVY)
    draw_centered("I TOLD MY AI AGENT", 26, 7, WHITE)
    draw_centered("TO BOOK ME A FLIGHT", 96, 7, WHITE)
    draw_centered("TO HAWAII", 166, 7, YELLOW)
    fill_rect(0, 250, W, 258, YELLOW)


def draw_sky():
    fill_rect(0, 258, W, 560, SKY)
    # sun, top right
    fill_circle(905, 330, 52, YELLOW)
    fill_circle(905, 330, 40, (255, 220, 90))
    # clouds
    for cx, cy in ((150, 320), (760, 430), (700, 300)):
        fill_circle(cx, cy, 26, WHITE)
        fill_circle(cx + 30, cy - 8, 22, WHITE)
        fill_circle(cx + 58, cy, 24, WHITE)
        fill_rect(cx - 24, cy, cx + 80, cy + 22, WHITE)
    # little plane + contrail, in the empty sky between palm and robot
    draw_line(280, 465, 450, 455, WHITE, 6)
    fill_rect(310, 448, 390, 468, WHITE)
    fill_triangle((390, 448), (435, 442), (390, 458), WHITE)
    fill_triangle((325, 468), (350, 480), (355, 468), WHITE)
    fill_rect(340, 442, 360, 448, BLUE)


def draw_beach():
    fill_rect(0, 560, W, 770, SAND)
    fill_rect(0, 560, W, 568, SAND2)
    # sea edge foam dots
    for x in range(20, W, 70):
        fill_circle(x, 566, 6, WHITE)
    # beach ball, left
    fill_circle(180, 660, 48, WHITE)
    fill_circle(180, 660, 48, RED)  # base, then wedges over it
    fill_triangle((180, 660), (138, 628), (180, 612), YELLOW)
    fill_triangle((180, 660), (222, 628), (180, 612), BLUE)
    fill_triangle((180, 660), (138, 692), (222, 692), TEAL)
    fill_circle(180, 660, 10, WHITE)
    # suitcase, right of the ball
    fill_rect(300, 630, 380, 720, BROWN)
    fill_rect(306, 636, 374, 714, (170, 120, 65))
    fill_rect(322, 618, 358, 632, DARK)
    fill_rect(336, 660, 344, 690, YELLOW)
    # palm tree, far left
    draw_line(80, 700, 130, 470, BROWN, 16)
    for dx, dy, ex, ey in (
        (130, 470, 60, 420), (130, 470, 200, 420),
        (130, 470, 80, 500), (130, 470, 195, 495),
        (130, 470, 130, 400),
    ):
        draw_line(130, 470, ex, ey, GREEN_D, 10)
    fill_circle(125, 480, 12, BROWN)
    fill_circle(145, 485, 12, BROWN)


def draw_robot():
    # striped beach towel under the robot
    for i, col in enumerate((RED, WHITE, RED, WHITE, RED, WHITE)):
        fill_rect(430 + i * 52, 648, 430 + (i + 1) * 52, 700, col)
    # legs stretched out on the towel
    fill_rect(560, 640, 700, 664, SILVER)
    fill_rect(560, 668, 700, 692, SILVER_D)
    fill_rect(700, 636, 724, 668, DARK)
    fill_rect(700, 664, 724, 696, DARK)
    # body, sitting up
    fill_rect(520, 520, 640, 652, SILVER)
    fill_rect(520, 520, 640, 536, SILVER_D)
    fill_rect(545, 556, 615, 616, (20, 60, 90))
    draw_text("AI", 562, 570, 3, (80, 220, 255))
    fill_circle(580, 636, 8, RED)
    fill_circle(580, 636, 4, YELLOW)
    # left arm resting, right arm holding a cocktail
    draw_line(525, 545, 470, 610, SILVER_D, 12)
    draw_line(635, 545, 700, 600, SILVER, 12)
    # cocktail glass + umbrella
    fill_triangle((700, 600), (740, 600), (720, 645), WHITE)
    fill_rect(702, 602, 738, 622, ORANGE)
    draw_line(720, 600, 720, 575, DARK, 4)
    fill_triangle((690, 578), (750, 578), (720, 556), PINK)
    fill_circle(742, 592, 7, RED)
    # head
    fill_rect(512, 410, 648, 522, SILVER)
    fill_rect(512, 410, 648, 426, SILVER_D)
    # antenna + blinking light
    draw_line(580, 410, 580, 378, DARK, 5)
    fill_circle(580, 370, 10, RED)
    fill_circle(580, 370, 5, YELLOW)
    # ears
    fill_rect(496, 448, 512, 484, SILVER_D)
    fill_rect(648, 448, 664, 484, SILVER_D)
    # sunglasses
    fill_rect(528, 448, 580, 478, BLACK)
    fill_rect(600, 448, 632, 478, BLACK)
    fill_rect(580, 458, 600, 468, BLACK)
    fill_rect(534, 452, 546, 458, WHITE)
    fill_rect(606, 452, 618, 458, WHITE)
    # smug smile
    draw_line(548, 492, 575, 504, DARK, 4)
    draw_line(575, 504, 612, 490, DARK, 4)
    # first-class boarding pass stuck in the sand
    fill_rect(760, 600, 880, 700, WHITE)
    fill_rect(760, 600, 880, 628, BLUE)
    draw_text("1ST CLASS", 772, 606, 2, WHITE)
    draw_text("HAWAII", 782, 644, 3, DARK)
    draw_text("SEAT 1A", 782, 672, 2, DARK)


def draw_speech_bubble():
    # white bubble, top-left of the beach scene
    fill_rect(48, 285, 480, 368, WHITE)
    fill_rect(48, 285, 480, 295, YELLOW)
    fill_triangle((120, 368), (170, 368), (130, 400), WHITE)
    draw_text("THANKS FOR THE MILES!", 66, 312, 3, DARK)


def draw_bottom_panel():
    fill_rect(0, 770, W, H, NAVY)
    fill_rect(0, 770, W, 778, YELLOW)
    draw_centered("IT BOOKED ITSELF", 800, 7, WHITE)
    draw_centered("FIRST CLASS.", 870, 7, YELLOW)
    draw_centered("I'M STILL AT MY DESK.", 940, 6, WHITE)


def draw():
    fill_rect(0, 0, W, H, WHITE)
    draw_top_panel()
    draw_sky()
    draw_beach()
    draw_robot()
    draw_speech_bubble()
    draw_bottom_panel()


# ---------------------------------------------------------------- PNG encode
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter: none
        raw += buf[y * W * 3:(y + 1) * W * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    draw()
    size = write_png(OUT)
    print(f"wrote {OUT} ({W}x{H}, {size} bytes)")


if __name__ == "__main__":
    main()
