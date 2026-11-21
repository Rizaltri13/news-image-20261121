#!/usr/bin/env python3
"""The World Today - Saturday 21 November 2026 in one image.

A make.fun bounty entry for news-image-20261121. The program draws a
1024x1024 newspaper front page that sums up the world's news of Saturday
21 November 2026 and writes it to /output/entry.png (or $MAKEFUN_OUTPUT_DIR).

Standard library only, no network. Fully deterministic: two runs write
byte-identical files. The hero picture is a generated illustration stored
beside this file as hero.png and decoded here with a small PNG reader;
every letter on the page comes from a hand-typed 5x7 bitmap font, and the
final PNG is encoded by hand (zlib + struct), so nothing about the output
depends on installed fonts or libraries.
"""

import os
import struct
import zlib

W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (18, 18, 18)
RED = (178, 32, 42)
NAVY = (20, 38, 74)
GREY = (96, 91, 82)
LIGHT = (231, 225, 212)
WHITE = (255, 255, 255)
GOLD = (212, 160, 40)

# ---------------------------------------------------------------------------
# 5x7 bitmap font. Each glyph is 7 rows of 5 bits, "1" = ink. Lowercase is
# folded to uppercase by the text renderer; the page is set in capitals.
# ---------------------------------------------------------------------------
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
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    ",": ("00000", "00000", "00000", "00000", "00100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "00100", "00100"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    ":": ("00000", "00100", "00000", "00000", "00000", "00100", "00000"),
    ";": ("00000", "00100", "00000", "00000", "00100", "00100", "01000"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "\\": ("10000", "01000", "01000", "00100", "00010", "00010", "00001"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "^": ("00100", "01010", "10001", "00000", "00000", "00000", "00000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "`": ("00100", "00100", "00010", "00000", "00000", "00000", "00000"),
    "{": ("00110", "01000", "01000", "01110", "01000", "01000", "00110"),
    "|": ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
    "}": ("01100", "00010", "00010", "01110", "00010", "00010", "01100"),
    "~": ("00000", "00000", "01001", "10110", "00000", "00000", "00000"),
}


def text_width(text, scale):
    """Pixel width of text at a scale (glyph 5 wide, 1 blank column)."""
    return len(text) * 6 * scale - scale


def wrap_text(text, scale, max_width):
    """Greedy word wrap; returns a list of lines fitting max_width."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------------------
# Canvas: an RGB pixel buffer with tiny drawing primitives.
# ---------------------------------------------------------------------------
class Page:
    def __init__(self):
        self.px = bytearray(bytes(PAPER) * (W * H))

    def set(self, x, y, colour):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = colour

    def rect(self, x, y, w, h, colour):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, colour)

    def hline(self, x, y, w, colour):
        self.rect(x, y, w, 1, colour)

    def vline(self, x, y, h, colour):
        self.rect(x, y, 1, h, colour)

    def frame(self, x, y, w, h, colour):
        self.hline(x, y, w, colour)
        self.hline(x, y + h - 1, w, colour)
        self.vline(x, y, h, colour)
        self.vline(x + w - 1, y, h, colour)

    def line(self, x0, y0, x1, y1, colour):
        """Bresenham line."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, colour)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, colour):
        """Midpoint circle outline."""
        x, y, d = 0, r, 1 - r
        while x <= y:
            for px, py in ((cx + x, cy + y), (cx + y, cy + x),
                           (cx - x, cy + y), (cx - y, cy + x),
                           (cx + x, cy - y), (cx + y, cy - x),
                           (cx - x, cy - y), (cx - y, cy - x)):
                self.set(px, py, colour)
            if d < 0:
                d += 2 * x + 3
            else:
                d += 2 * (x - y) + 5
                y -= 1
            x += 1

    def disc(self, cx, cy, r, colour):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, colour)

    def blit(self, img, dx, dy):
        iw, ih, data = img
        for yy in range(ih):
            for xx in range(iw):
                j = (yy * iw + xx) * 3
                self.set(dx + xx, dy + yy, (data[j], data[j + 1], data[j + 2]))

    def glyph(self, x, y, ch, scale, colour, bold=False):
        rows = FONT.get(ch, FONT[" "])
        for r, row in enumerate(rows):
            for c, bit in enumerate(row):
                if bit == "1":
                    self.rect(x + c * scale, y + r * scale,
                              scale, scale, colour)
                    if bold:
                        self.rect(x + c * scale + 1, y + r * scale,
                                  scale, scale, colour)

    def text(self, x, y, s, scale, colour, bold=False):
        for ch in s.upper():
            self.glyph(x, y, ch, scale, colour, bold)
            x += 6 * scale
        return x

    def centred(self, y, s, scale, colour, bold=False):
        x = (W - text_width(s, scale)) // 2
        self.text(x, y, s, scale, colour, bold)


# ---------------------------------------------------------------------------
# PNG decode (8-bit RGB/RGBA, non-interlaced) and encode.
# ---------------------------------------------------------------------------
def _paeth(a, b, c):
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def decode_png(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    pos, width, height, ctype, depth = 8, 0, 0, 0, 0
    idat = bytearray()
    while pos < len(data):
        (ln,) = struct.unpack(">I", data[pos:pos + 4])
        kind = data[pos + 4:pos + 8]
        chunk = data[pos + 8:pos + 8 + ln]
        if kind == b"IHDR":
            width, height, depth, ctype = struct.unpack(">IIBB", chunk[:10])
            interlace = chunk[12]
            if depth != 8 or interlace != 0 or ctype not in (2, 6):
                raise ValueError("unsupported PNG flavour")
        elif kind == b"IDAT":
            idat += chunk
        elif kind == b"IEND":
            break
        pos += 12 + ln
    ch = 3 if ctype == 2 else 4
    raw = zlib.decompress(bytes(idat))
    stride = width * ch
    out = bytearray(width * height * 3)
    prev = bytearray(stride)
    p = 0
    for y in range(height):
        f = raw[p]
        p += 1
        row = bytearray(raw[p:p + stride])
        p += stride
        for i in range(stride):
            a = row[i - ch] if i >= ch else 0
            b = prev[i]
            c = prev[i - ch] if i >= ch else 0
            if f == 1:
                row[i] = (row[i] + a) & 0xFF
            elif f == 2:
                row[i] = (row[i] + b) & 0xFF
            elif f == 3:
                row[i] = (row[i] + (a + b) // 2) & 0xFF
            elif f == 4:
                row[i] = (row[i] + _paeth(a, b, c)) & 0xFF
        for x in range(width):
            j = (y * width + x) * 3
            k = x * ch
            out[j], out[j + 1], out[j + 2] = row[k], row[k + 1], row[k + 2]
        prev = row
    return width, height, bytes(out)


def _chunk(kind, payload):
    out = struct.pack(">I", len(payload)) + kind + payload
    return out + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)


def encode_png(rgb, width, height):
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    stride = width * 3
    body = bytearray()
    prev = bytearray(stride)
    for y in range(height):
        row = rgb[y * stride:(y + 1) * stride]
        # Filter 0 (none) vs filter 2 (up): keep whichever sums smaller.
        up = bytes((row[i] - prev[i]) & 0xFF for i in range(stride))
        score0 = sum(v if v < 128 else 256 - v for v in row)
        score2 = sum(v if v < 128 else 256 - v for v in up)
        if score2 < score0:
            body.append(2)
            body += up
        else:
            body.append(0)
            body += row
        prev = bytearray(row)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(bytes(body), 6))
            + _chunk(b"IEND", b""))


# ---------------------------------------------------------------------------
# Small pictograms for the story tiles (navy line art, red accent).
# ---------------------------------------------------------------------------
def draw_icon(page, kind, x, y):
    c, r = NAVY, RED
    if kind == "court":  # courthouse: roof, columns, base
        page.line(x + 2, y + 12, x + 22, y + 2, c)
        page.line(x + 22, y + 2, x + 42, y + 12, c)
        page.hline(x + 4, y + 12, 37, c)
        for cx in (x + 8, x + 21, x + 34):
            page.vline(cx, y + 14, 20, c)
        page.hline(x + 4, y + 36, 37, c)
        page.hline(x + 2, y + 40, 41, c)
        page.disc(x + 22, y + 8, 2, r)
    elif kind == "chart":  # falling market chart
        page.vline(x + 6, y + 4, 34, c)
        page.hline(x + 6, y + 38, 34, c)
        page.line(x + 8, y + 10, x + 18, y + 18, r)
        page.line(x + 18, y + 18, x + 26, y + 16, r)
        page.line(x + 26, y + 16, x + 38, y + 34, r)
        page.line(x + 38, y + 34, x + 34, y + 34, r)
        page.line(x + 38, y + 34, x + 38, y + 30, r)
    elif kind == "storm":  # cyclone swirl
        page.circle(x + 22, y + 22, 6, c)
        page.circle(x + 22, y + 22, 12, c)
        page.circle(x + 22, y + 22, 18, c)
        page.disc(x + 22, y + 22, 3, r)
        page.line(x + 22, y + 4, x + 22, y + 10, c)
    elif kind == "flags":  # two partner flags
        page.rect(x + 4, y + 10, 16, 22, c)
        page.rect(x + 6, y + 18, 12, 3, WHITE)
        page.rect(x + 11, y + 12, 3, 18, WHITE)
        page.rect(x + 24, y + 10, 16, 22, NAVY)
        page.disc(x + 32, y + 21, 6, GOLD)
        page.rect(x + 31, y + 20, 3, 3, NAVY)
    elif kind == "summit":  # three towers
        page.rect(x + 5, y + 18, 9, 22, c)
        page.rect(x + 18, y + 8, 9, 32, c)
        page.rect(x + 31, y + 14, 9, 26, c)
        for wy in (y + 12, y + 20, y + 28):
            page.rect(x + 20, wy, 5, 3, GOLD)
        page.rect(x + 7, y + 22, 5, 3, GOLD)
        page.rect(x + 33, y + 18, 5, 3, GOLD)
        page.hline(x + 3, y + 40, 40, c)
    elif kind == "aid":  # relief crate with a cross
        page.frame(x + 8, y + 10, 28, 26, c)
        page.rect(x + 19, y + 14, 6, 18, r)
        page.rect(x + 14, y + 19, 16, 6, r)
        page.hline(x + 8, y + 38, 28, c)
        page.line(x + 8, y + 38, x + 4, y + 42, c)
        page.line(x + 36, y + 38, x + 40, y + 42, c)


# ---------------------------------------------------------------------------
# The day's stories (verified against wire and press reports, 20-21 Nov 2026).
# ---------------------------------------------------------------------------
TILES = [
    ("THE HAGUE", "court",
     "WORLD COURT FINDS MYANMAR RESPONSIBLE FOR GENOCIDE",
     "ICJ RULES 9-6 MYANMAR COMMITTED GENOCIDE AGAINST THE ROHINGYA IN "
     "2017 AND ORDERS REPARATIONS."),
    ("MARKETS", "chart",
     "WALL ST ROUT: S&P INTO CORRECTION",
     "S&P FALLS 3.7% AND NASDAQ 5.3% IN ITS WORST WEEK SINCE 2020 AS THE "
     "AI RALLY UNWINDS. NVIDIA -14%."),
    ("INDIA", "storm",
     "CYCLONE AKVAN HITS ODISHA",
     "STORM CROSSES THE COAST NEAR GOPALPUR WITH 80 KM/H WINDS AFTER "
     "300,000 PEOPLE ARE EVACUATED."),
    ("BRUSSELS", "flags",
     "UK AND EU SIGN NEW DEALS",
     "BURNHAM SIGNS PACTS ON FOOD TRADE, CARBON MARKETS AND YOUTH "
     "MOBILITY AT A BRUSSELS SUMMIT."),
    ("SHENZHEN", "summit",
     "SUMMIT ENDS WITH LITTLE TO SHOW",
     "TRUMP, XI AND PUTIN LEAVE THEIR FIRST TRILATERAL MEETING WITH FEW "
     "CONCRETE RESULTS."),
    ("GAZA", "aid",
     "FOUR NATIONS DEMAND GAZA AID ACCESS",
     "AUSTRALIA, CANADA, ITALY AND THE UK CALL ON ISRAEL TO LET AID IN "
     "AS FLOODS WORSEN THE CRISIS."),
]


def build(hero):
    page = Page()
    # Masthead.
    page.centred(26, "THE WORLD TODAY", 7, NAVY, bold=True)
    page.hline(24, 86, 976, NAVY)
    page.hline(24, 89, 976, RED)
    # Red date band.
    page.rect(24, 96, 976, 34, RED)
    page.centred(104, "SATURDAY 21 NOVEMBER 2026", 3, WHITE, bold=True)
    # Hero picture + label.
    page.blit(hero, 24, 140)
    page.rect(24, 140, 118, 20, NAVY)
    page.text(30, 146, "ILLUSTRATION", 1, WHITE)
    # Hero headline and standfirst.
    page.centred(402, "RUSSIAN MISSILES HIT POLAND", 5, INK, bold=True)
    page.centred(448, "POLAND CALLS IT A DELIBERATE PROVOCATION AS NATO "
                       "JETS SCRAMBLE", 2, INK)
    page.centred(464, "EIGHT KILLED IN MOSCOW'S BIGGEST OVERNIGHT ATTACK "
                       "ON UKRAINE", 2, INK)
    page.hline(24, 486, 976, INK)
    # Story tiles: 2 rows x 3 columns.
    tw, th, gap = 314, 190, 17
    for i, (kicker, icon, head, body) in enumerate(TILES):
        tx = 24 + (i % 3) * (tw + gap)
        ty = 496 + (i // 3) * (th + 12)
        page.frame(tx, ty, tw, th, GREY)
        page.rect(tx + 1, ty + 1, tw - 2, 4, RED)
        page.text(tx + 12, ty + 13, kicker, 2, RED, bold=True)
        draw_icon(page, icon, tx + tw - 58, ty + 8)
        # Headlines wrap clear of the icon column (icon starts at tx+256,
        # so headline text must end by tx+250: width 244 from tx+12).
        lines = wrap_text(head, 2, tw - 70)
        for n, ln in enumerate(lines[:2]):
            page.text(tx + 12, ty + 34 + n * 16, ln, 2, INK, bold=True)
        blines = wrap_text(body, 2, tw - 24)
        for n, ln in enumerate(blines[:5]):
            page.text(tx + 12, ty + 72 + n * 15, ln, 2, INK)
    # Ticker strip.
    page.rect(24, 900, 976, 68, RED)
    page.centred(910, "BOLSONARO IN HOSPITAL - PALISADES ARSONIST GUILTY "
                       "- FRANCE PROTESTS", 2, WHITE, bold=True)
    page.centred(934, "COP31: FINAL STAGE - VENEZUELA OIL $12BN - INDIA "
                       "FIGHT BACK IN WELLINGTON", 2, WHITE, bold=True)
    # Footer.
    page.centred(980, "SOURCES: AP - REUTERS - THE TIMES - WSJ - HRW - IMD "
                       "- INVESTOPEDIA", 1, GREY)
    page.centred(991, "ALL STORIES FIRST REPORTED 20-21 NOVEMBER 2026",
                  1, GREY)
    return page


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "hero.png"), "rb") as f:
        hero = decode_png(f.read())
    page = build(hero)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "entry.png"), "wb") as f:
        f.write(encode_png(page.px, W, H))


if __name__ == "__main__":
    main()
