#!/usr/bin/env python3
"""Draws the front page of THE WORLD for Saturday, 21 November 2026.

One 1024x1024 PNG newspaper front page: a lead story plus seven more,
spanning regions and fields. Pure Python standard library, deterministic:
two runs write byte-identical PNGs. Writes to /output/entry.png (or the
directory in MAKEFUN_OUTPUT_DIR). Never deletes the output folder.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---- palette ---------------------------------------------------------------
PAPER = (247, 243, 232)
CARD = (255, 255, 255)
INK = (17, 17, 17)
NAVY = (26, 42, 74)
DARK = (40, 44, 52)
RED = (176, 32, 32)
BRIGHT_RED = (214, 48, 32)
GOLD = (201, 162, 39)
TEAL = (0, 120, 110)
GREEN = (34, 120, 60)
SKY = (120, 170, 210)
NIGHT = (16, 22, 44)
ORANGE = (240, 130, 30)
GREY = (120, 118, 110)
LIGHT_GREY = (225, 220, 205)

# ---- 5x7 bitmap font (uppercase, digits, punctuation) ----------------------
# Each glyph is 7 rows of 5 characters; '#' is on, '.' is off.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".....", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '%': ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    '+': (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    '/': ("....#", "...#.", "...#.", "..#..", ".#...", "#....", "#...."),
    '&': (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '=': (".....", ".....", ".###.", ".....", ".###.", ".....", "....."),
}

# ---- pixel buffer ----------------------------------------------------------
BUF = bytearray(W * H * 3)


def set_px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        BUF[i] = c[0]
        BUF[i + 1] = c[1]
        BUF[i + 2] = c[2]


def rect(x, y, w, h, c):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            BUF[i] = c[0]
            BUF[i + 1] = c[1]
            BUF[i + 2] = c[2]


def hline(x0, x1, y, c):
    if x1 < x0:
        x0, x1 = x1, x0
    for x in range(max(0, x0), min(W, x1 + 1)):
        set_px(x, y, c)


def vline(x, y0, y1, c):
    if y1 < y0:
        y0, y1 = y1, y0
    for y in range(max(0, y0), min(H, y1 + 1)):
        set_px(x, y, c)


def line(x0, y0, x1, y1, c):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        set_px(x0, y0, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def circle(cx, cy, r, c):
    for y in range(cy - r, cy + r + 1):
        d = r * r - (y - cy) * (y - cy)
        if d < 0:
            continue
        dx = int(d ** 0.5)
        for x in range(cx - dx, cx + dx + 1):
            set_px(x, y, c)


def poly(points, c):
    ys = [p[1] for p in points]
    ymin, ymax = min(ys), max(ys)
    n = len(points)
    for y in range(ymin, ymax + 1):
        xs = []
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if y0 == y1:
                continue
            if min(y0, y1) <= y < max(y0, y1):
                xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            for x in range(int(xs[i]), int(xs[i + 1]) + 1):
                set_px(x, y, c)


def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(s, x, y, scale, c):
    cx = x
    for ch in s:
        g = FONT.get(ch)
        if g is not None:
            for row in range(7):
                bits = g[row]
                for col in range(5):
                    if bits[col] == '#':
                        rect(cx + col * scale, y + row * scale,
                             scale, scale, c)
        cx += 6 * scale


def wrap_text(s, scale, max_w):
    lines = []
    cur = ''
    for word in s.split(' '):
        trial = (cur + ' ' + word).strip() if cur else word
        if text_w(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_block(s, x, y, scale, max_w, line_h, c):
    lines = wrap_text(s, scale, max_w)
    for i, ln in enumerate(lines):
        draw_text(ln, x, y + i * line_h, scale, c)
    return len(lines)


# ---- story illustrations ---------------------------------------------------
def scene_lead(x, y, w, h):
    """Night skyline over Kryvyi Rih: dark sky, black towers, orange blast."""
    rect(x, y, w, h, NIGHT)
    for i in range(6):
        rect(x + 8 + i * 6, y + 10 + i * 4, w - 16 - i * 12, 3, (30, 38, 70))
    # stars
    for sx, sy in [(30, 14), (90, 26), (150, 10), (230, 30), (300, 16),
                   (360, 24), (60, 44), (190, 40), (330, 48)]:
        set_px(x + sx, y + sy, (255, 255, 255))
        set_px(x + sx + 1, y + sy, (200, 200, 220))
    # skyline silhouettes
    base = y + h
    towers = [(0, 150, 46), (48, 120, 60), (110, 165, 40), (152, 130, 55),
              (209, 175, 38), (249, 140, 52), (303, 160, 44), (349, 125, 48)]
    for tx, tw, th in towers:
        rect(x + tx, base - th, tw, th, (8, 10, 20))
    # lit windows
    for wx, wy in [(12, 180), (60, 150), (120, 190), (165, 160), (220, 200),
                   (260, 170), (315, 185), (360, 155), (90, 210), (280, 205)]:
        rect(x + wx, base - wy, 5, 6, GOLD)
    # blast glow and fireball
    cx, cy = x + w // 2, y + h - 120
    circle(cx, cy, 58, (120, 50, 10))
    circle(cx, cy, 44, ORANGE)
    circle(cx, cy, 30, (250, 190, 60))
    circle(cx, cy, 16, (255, 240, 180))
    # blast rays
    for ang in range(0, 360, 30):
        import math
        r1, r2 = 62, 78
        a = math.radians(ang)
        line(cx + int(r1 * math.cos(a)), cy + int(r1 * math.sin(a)),
             cx + int(r2 * math.cos(a)), cy + int(r2 * math.sin(a)), ORANGE)
    # smoke
    circle(x + 70, y + 60, 22, (70, 70, 80))
    circle(x + 100, y + 48, 16, (90, 90, 100))
    circle(x + 320, y + 70, 20, (70, 70, 80))


def scene_gulf(x, y, w, h):
    """Tanker on a dark sea, flame and smoke over Bahrain."""
    rect(x, y, w, h, (10, 40, 70))
    rect(x, y, w, h // 3, (20, 60, 100))
    circle(x + w - 50, y + 26, 18, (240, 220, 180))
    # sea
    rect(x, y + h // 2, w, h // 2, (8, 30, 55))
    for i in range(4):
        hline(x + 10 + i * 24, x + 60 + i * 24, y + h // 2 + 10 + i * 10,
              (40, 90, 130))
    # tanker hull and bridge, all inside the box
    hull_y = y + h - 26
    rect(x + 40, hull_y, w - 80, 18, (12, 12, 14))
    rect(x + w - 100, hull_y - 22, 52, 22, (20, 20, 24))
    rect(x + 64, hull_y - 12, 8, 12, (30, 30, 34))
    rect(x + 92, hull_y - 12, 8, 12, (30, 30, 34))
    # flame above the hull, mid-ship
    fx, fy = x + w // 2, hull_y - 26
    poly([(fx, fy - 18), (fx - 12, fy + 4), (fx + 12, fy + 4)], ORANGE)
    circle(fx, fy, 9, (250, 190, 60))
    circle(fx - 26, fy - 4, 8, (90, 90, 100))
    circle(fx + 28, fy - 8, 9, (110, 110, 120))


def scene_climate(x, y, w, h):
    """A green globe under a pale sun, smoke drifting across it."""
    rect(x, y, w, h, (210, 230, 235))
    circle(x + w - 46, y + 34, 20, GOLD)
    # globe
    cx, cy, r = x + w // 2, y + h // 2 + 6, 62
    circle(cx, cy, r, TEAL)
    circle(cx - 18, cy - 12, 16, GREEN)
    circle(cx + 20, cy + 16, 14, GREEN)
    circle(cx + 8, cy - 26, 10, GREEN)
    # latitude lines
    hline(cx - r + 8, cx + r - 8, cy - 26, (180, 220, 210))
    hline(cx - r + 4, cx + r - 4, cy + 26, (180, 220, 210))
    # smoke stacks
    rect(x + 14, y + h - 52, 10, 52, DARK)
    rect(x + 34, y + h - 44, 10, 44, DARK)
    circle(x + 30, y + h - 62, 12, GREY)
    circle(x + 52, y + h - 74, 14, GREY)
    circle(x + 76, y + h - 86, 12, GREY)


def scene_mexico(x, y, w, h):
    """Gold star badge on navy, with handcuff rings below."""
    rect(x, y, w, h, NAVY)
    cx, cy = x + w // 2, y + h // 2 - 14
    import math
    outer, inner = 52, 22
    pts = []
    for i in range(10):
        ang = math.radians(-90 + i * 36)
        rr = outer if i % 2 == 0 else inner
        pts.append((cx + int(rr * math.cos(ang)),
                    cy + int(rr * math.sin(ang))))
    poly(pts, GOLD)
    circle(cx, cy, 16, NAVY)
    draw_text("10", cx - 11, cy - 7, 2, GOLD)
    # handcuff rings
    circle(x + w // 2 - 34, y + h - 26, 13, (200, 200, 205))
    circle(x + w // 2 - 34, y + h - 26, 7, NAVY)
    circle(x + w // 2 + 34, y + h - 26, 13, (200, 200, 205))
    circle(x + w // 2 + 34, y + h - 26, 7, NAVY)
    line(x + w // 2 - 22, y + h - 26, x + w // 2 + 22, y + h - 26,
         (200, 200, 205))


def scene_peru(x, y, w, h):
    """Andes peaks with a red seismograph zigzag across them."""
    rect(x, y, w, h, (215, 225, 235))
    circle(x + w - 44, y + 32, 18, (245, 200, 90))
    poly([(x, y + h), (x + 90, y + 40), (x + 170, y + h)], (120, 100, 80))
    poly([(x + 120, y + h), (x + 220, y + 26), (x + 320, y + h)],
         (90, 75, 60))
    poly([(x + 230, y + h), (x + 300, y + 60), (x + w, y + h)],
         (140, 120, 95))
    # snow caps
    poly([(x + 76, y + 52), (x + 90, y + 40), (x + 104, y + 52),
          (x + 96, y + 58), (x + 84, y + 58)], (255, 255, 255))
    poly([(x + 208, y + 38), (x + 220, y + 26), (x + 232, y + 38),
          (x + 226, y + 44), (x + 214, y + 44)], (255, 255, 255))
    # seismograph zigzag
    pts = [(x + 6, y + h - 70), (x + 40, y + h - 70), (x + 55, y + h - 96),
           (x + 70, y + h - 44), (x + 85, y + h - 88), (x + 100, y + h - 58),
           (x + 130, y + h - 70), (x + 160, y + h - 70), (x + 175, y + h - 100),
           (x + 190, y + h - 40), (x + 205, y + h - 82), (x + 220, y + h - 60),
           (x + 250, y + h - 70), (x + 300, y + h - 70), (x + 315, y + h - 92),
           (x + 326, y + h - 70)]
    for i in range(len(pts) - 1):
        line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], RED)
    # houses at the foot
    for hx in (x + 30, x + 70, x + 250, x + 290):
        rect(hx, y + h - 18, 22, 18, (90, 60, 40))


def scene_science(x, y, w, h):
    """A zeta curve rising over prime numbers."""
    rect(x, y, w, h, (240, 238, 225))
    # axes
    vline(x + 24, y + 12, y + h - 34, INK)
    hline(x + 24, x + w - 12, y + h - 34, INK)
    # curve: damped oscillation rising to the right
    import math
    prev = None
    for i in range(0, w - 48):
        px = x + 28 + i
        t = i / (w - 48)
        py = y + h - 40 - int(46 * t + 14 * math.sin(i * 0.09) * (1 - t))
        if prev is not None:
            line(prev[0], prev[1], px, py, RED)
        prev = (px, py)
    circle(x + w - 24, y + h - 40 - 46, 7, RED)
    # primes along the bottom
    draw_text("2  3  5  7  11  13", x + 30, y + h - 24, 2, NAVY)


def scene_britain(x, y, w, h):
    """Union Jack and EU flag side by side, joined by a gold link."""
    half = w // 2
    # Union Jack (simplified): navy, white cross, red cross
    rect(x, y, half - 4, h, NAVY)
    rect(x, y + h // 2 - 10, half - 4, 20, (255, 255, 255))
    rect(x + half // 2 - 10, y, 20, h, (255, 255, 255))
    rect(x, y + h // 2 - 5, half - 4, 10, RED)
    rect(x + half // 2 - 5, y, 10, h, RED)
    # EU flag: blue with a ring of gold stars
    ex = x + half + 4
    rect(ex, y, half - 4, h, (0, 51, 153))
    import math
    ccx, ccy = ex + (half - 4) // 2, y + h // 2
    for i in range(12):
        ang = math.radians(i * 30 - 90)
        sx = ccx + int(34 * math.cos(ang))
        sy = ccy + int(34 * math.sin(ang))
        circle(sx, sy, 4, GOLD)
    # gold link between the flags
    rect(x + half - 12, y + h // 2 - 6, 24, 12, GOLD)


def scene_markets(x, y, w, h):
    """Falling red bars with a down arrow."""
    rect(x, y, w, h, (250, 246, 238))
    base = y + h - 12
    max_h = h - 26
    heights = [int(max_h * f) for f in (0.92, 0.78, 0.60, 0.44, 0.28)]
    for i, hh in enumerate(heights):
        bx = x + 16 + i * 34
        rect(bx, base - hh, 24, hh, BRIGHT_RED)
    # down arrow
    line(x + 14, y + 16, x + w - 30, y + h - 30, RED)
    poly([(x + w - 30, y + h - 30), (x + w - 52, y + h - 30),
          (x + w - 30, y + h - 8)], RED)
    draw_text("-3.7%", x + w - 92, y + 10, 2, RED)


# ---- layout ----------------------------------------------------------------
STORIES = [
    # kicker, headline, deck, source, scene
    ("GULF", "IRAN STRIKES BAHRAIN AS TANKERS ARE HIT IN HORMUZ",
     "CIVILIAN PLANT HIT; TWO TANKERS STRUCK IN HORMUZ.", "AFP",
     scene_gulf),
    ("CLIMATE", "COP31 IN OVERTIME AS FOSSIL FUELS VANISH FROM THE DRAFT",
     "DELEGATES FIGHT OVER ONE PHRASE: FOSSIL FUELS.", "AP",
     scene_climate),
    ("MEXICO", "MEXICO CAPTURES 'EL CHAPO ISIDRO', FBI'S MOST WANTED",
     "FOUR SOLDIERS AND SEVEN GUNMEN KILLED.", "REUTERS",
     scene_mexico),
    ("PERU", "MAGNITUDE 6.9 QUAKE SHAKES PERU'S ANDES",
     "FELT IN LIMA. NO CASUALTIES REPORTED.", "AP / USGS",
     scene_peru),
    ("SCIENCE", "AI'S RIEMANN PROOF PASSES FIRST INDEPENDENT CHECKS",
     "LEAN PROOF CLEARS FIRST TESTS. NOT YET CONFIRMED.",
     "SCIENTIFIC AMERICAN", scene_science),
    ("BRITAIN", "UK-EU RESET SEALED, THEN HELD UP BY TUITION ROW",
     "FOOD CHECKS END. EU WANTS A FEES DEAL FIRST.", "THE TIMES",
     scene_britain),
]

KICKER_COLOURS = {
    "GULF": RED, "CLIMATE": GREEN, "MEXICO": NAVY,
    "PERU": (120, 80, 40), "SCIENCE": (90, 40, 110), "BRITAIN": NAVY,
}


def draw_card(x, y, w, h, kicker, headline, deck, source, scene):
    rect(x, y, w, h, CARD)
    for i in range(w):
        set_px(x + i, y, INK)
        set_px(x + i, y + h - 1, INK)
    for j in range(h):
        set_px(x, y + j, INK)
        set_px(x + w - 1, y + j, INK)
    scene(x + 2, y + 2, w - 4, 96)
    rect(x + 2, y + 100, w - 4, 2, LIGHT_GREY)
    # kicker band
    col = KICKER_COLOURS.get(kicker, NAVY)
    rect(x + 8, y + 106, text_w(kicker, 2) + 16, 20, col)
    draw_text(kicker, x + 16, y + 109, 2, (255, 255, 255))
    # headline
    n = draw_block(headline, x + 10, y + 132, 2, w - 20, 18, INK)
    # deck
    draw_block(deck, x + 10, y + 132 + n * 18 + 6, 2, w - 20, 16, DARK)
    # source
    draw_text("SOURCE: " + source, x + 10, y + h - 16, 1, GREY)


def draw_lead(x, y, w, h):
    rect(x, y, w, h, CARD)
    for i in range(w):
        set_px(x + i, y, INK)
        set_px(x + i, y + h - 1, INK)
    for j in range(h):
        set_px(x, y + j, INK)
        set_px(x + w - 1, y + j, INK)
    scene_lead(x + 2, y + 2, 398, h - 4)
    tx = x + 416
    rect(tx, y + 14, text_w("UKRAINE - LEAD", 2) + 16, 20, RED)
    draw_text("UKRAINE - LEAD", tx + 8, y + 17, 2, (255, 255, 255))
    n = draw_block(
        "RUSSIAN 'TRIPLE-TAP' STRIKE KILLS CHILD AND PARAMEDIC IN KRYVYI RIH",
        tx, y + 44, 4, w - 432, 32, INK)
    draw_block(
        "TWO KILLED, ABOUT 60 WOUNDED. MISSILES HIT A CAR PARK, THEN "
        "DRONES STRUCK THE RESCUERS.",
        tx, y + 44 + n * 32 + 10, 2, w - 432, 18, DARK)
    rect(tx, y + h - 34, w - 432, 2, LIGHT_GREY)
    draw_text("REPORTED SATURDAY 21 NOVEMBER 2026  -  CNN",
              tx, y + h - 26, 2, GREY)


def draw_markets(x, y, w, h):
    rect(x, y, w, h, CARD)
    for i in range(w):
        set_px(x + i, y, INK)
        set_px(x + i, y + h - 1, INK)
    for j in range(h):
        set_px(x, y + j, INK)
        set_px(x + w - 1, y + j, INK)
    scene_markets(x + 2, y + 2, 210, h - 4)
    tx = x + 226
    rect(tx, y + 10, text_w("MARKETS", 2) + 16, 20, RED)
    draw_text("MARKETS", tx + 8, y + 13, 2, (255, 255, 255))
    draw_block("WALL STREET FALLS INTO CORRECTION IN AI SELL-OFF",
              tx, y + 38, 2, w - 242, 18, INK)
    draw_text("S&P DOWN 3.7%, DOW DOWN 950 POINTS. NVIDIA SINKS 14%.",
              tx, y + h - 26, 2, DARK)
    draw_text("SOURCE: REUTERS", x + w - 118, y + 13, 1, GREY)


def draw_masthead():
    draw_text("THE WORLD", 24, 14, 11, NAVY)
    draw_text("SATURDAY, 21 NOVEMBER 2026", 688, 24, 2, INK)
    draw_text("ONE DAY. EIGHT STORIES.", 724, 52, 2, RED)
    for xx in range(24, 1000):
        set_px(xx, 104, RED)
        set_px(xx, 105, RED)
        set_px(xx, 108, INK)
        set_px(xx, 109, INK)


def write_png(path):
    raw = b"".join(
        b"\x00" + bytes(BUF[y * W * 3:(y + 1) * W * 3]) for y in range(H))

    def chunk(typ, data):
        return (struct.pack(">I", len(data)) + typ + data +
                struct.pack(">I", zlib.crc32(typ + data) & 0xffffffff))

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
           chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    rect(0, 0, W, H, PAPER)
    draw_masthead()
    # lead story
    draw_lead(24, 126, 976, 282)
    # two rows of three cards
    cw, ch = 320, 242
    gap = 8
    for row in range(2):
        for col in range(3):
            s = STORIES[row * 3 + col]
            draw_card(24 + col * (cw + gap), 416 + row * (ch + gap),
                      cw, ch, s[0], s[1], s[2], s[3], s[4])
    # markets strip
    draw_markets(24, 916, 976, 88)
    # sources footer
    foot = ("SOURCES: CNN - AFP - AP - REUTERS - USGS - SCIENTIFIC AMERICAN "
            "- THE TIMES - LE MONDE")
    draw_text(foot, (W - text_w(foot, 1)) // 2, 1010, 1, GREY)
    size = write_png(os.path.join(out, "entry.png"))
    print("wrote", os.path.join(out, "entry.png"), size, "bytes")


if __name__ == "__main__":
    main()
