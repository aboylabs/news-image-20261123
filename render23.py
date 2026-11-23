#!/usr/bin/env python3
"""Render the 23 November 2026 world-news front page (1024x1024 PNG).

Written fresh for make.fun news-image-20261123. Deterministic: every pixel
comes from constants below, so two runs write identical bytes.
Run: python3 render23.py  ->  writes entry/entry.png
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (26, 26, 26)
NAVY = (20, 38, 76)
RUST = (176, 42, 30)
MUTED = (96, 92, 82)
RULE = (26, 26, 26)
STRIP_BG = (232, 226, 210)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, face, width):
    """Greedy word wrap; returns a list of lines that fit `width` px."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=face) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, text, face, width, leading, color=INK):
    """Draw wrapped paragraph; returns the y after the last line."""
    for line in wrap(draw, text, face, width):
        draw.text((x, y), line, font=face, fill=color)
        y += leading
    return y


def chip(draw, box, tint, accent, kind):
    """Draw a small pictogram (ship, ballot, flame, chart, factory, glass)."""
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=10, fill=tint)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    if kind == "ship":
        draw.polygon([(cx - 34, cy + 6), (cx + 34, cy + 6),
                      (cx + 24, cy + 24), (cx - 24, cy + 24)], fill=accent)
        draw.rectangle([cx - 3, cy - 26, cx + 3, cy + 6], fill=accent)
        draw.polygon([(cx + 3, cy - 26), (cx + 26, cy - 12),
                      (cx + 3, cy - 12)], fill=accent)
        for wx in (-30, -6, 18):
            draw.arc([cx + wx - 12, cy + 28, cx + wx + 12, cy + 40],
                     0, 180, fill=accent, width=3)
    elif kind == "ballot":
        draw.rectangle([cx - 12, cy - 32, cx + 12, cy - 8],
                       outline=accent, width=3)
        draw.rectangle([cx - 30, cy - 8, cx + 30, cy + 28],
                       outline=accent, width=4)
        draw.line([cx - 20, cy + 8, cx - 6, cy + 20, cx + 22, cy - 6],
                  fill=accent, width=5, joint="curve")
    elif kind == "flame":
        draw.polygon([(cx, cy - 34), (cx + 16, cy - 6), (cx + 24, cy + 12),
                      (cx + 12, cy + 28), (cx - 12, cy + 28),
                      (cx - 24, cy + 12), (cx - 16, cy - 6)],
                     fill=accent)
        draw.ellipse([cx - 7, cy + 2, cx + 7, cy + 20], fill=(255, 214, 120))
    elif kind == "chart":
        draw.line([cx - 32, cy + 28, cx + 32, cy + 28], fill=accent, width=3)
        draw.line([cx - 32, cy + 28, cx - 32, cy - 30], fill=accent, width=3)
        draw.line([cx - 26, cy + 14, cx - 8, cy - 2, cx + 8, cy + 6,
                   cx + 28, cy - 24], fill=accent, width=4, joint="curve")
        draw.polygon([(cx + 28, cy - 24), (cx + 16, cy - 22),
                      (cx + 26, cy - 12)], fill=accent)
    elif kind == "factory":
        draw.rectangle([cx - 32, cy - 6, cx + 32, cy + 28], fill=accent)
        draw.polygon([(cx - 32, cy - 6), (cx - 20, cy - 22), (cx - 8, cy - 6),
                      (cx + 4, cy - 22), (cx + 16, cy - 6), (cx + 32, cy - 6)],
                     fill=accent)
        draw.rectangle([cx - 26, cy - 34, cx - 16, cy - 6], fill=accent)
        for wx in (-20, 0, 20):
            draw.rectangle([cx + wx - 5, cy + 10, cx + wx + 5, cy + 28],
                           fill=PAPER)
    elif kind == "glass":
        draw.polygon([(cx - 24, cy - 30), (cx + 24, cy - 30), (cx, cy - 2),
                      (cx - 24, cy - 30)], fill=accent)
        draw.polygon([(cx - 24, cy + 30), (cx + 24, cy + 30), (cx, cy + 2),
                      (cx - 24, cy + 30)], fill=accent)
        draw.rectangle([cx - 3, cy - 2, cx + 3, cy + 2], fill=accent)
        draw.ellipse([cx - 8, cy + 8, cx + 8, cy + 24], fill=(255, 214, 120))


def globe(draw, box):
    """A cracked globe for the lead panel."""
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    r = (x1 - x0) // 2 - 8
    draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                 outline=NAVY, width=4)
    draw.ellipse([cx - r // 2, cy - r, cx + r // 2, cy + r],
                 outline=NAVY, width=2)
    draw.arc([cx - r, cy - r // 2, cx + r, cy + r // 2], 0, 360,
             fill=NAVY, width=2)
    draw.line([cx - r, cy, cx + r, cy], fill=NAVY, width=2)
    crack = [(cx - 8, cy - r + 6), (cx + 10, cy - r // 2), (cx - 6, cy - 4),
             (cx + 12, cy + r // 3), (cx - 2, cy + r - 8)]
    draw.line(crack, fill=RUST, width=5, joint="curve")


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    f_date = font(SANS_B, 17)
    f_mast = font(SERIF_B, 62)
    f_kick = font(SANS_B, 20)
    f_head = font(SERIF_B, 46)
    f_dek = font(SANS, 19)
    f_tag = font(SANS_B, 15)
    f_tile_head = font(SERIF_B, 21)
    f_tile_body = font(SANS, 15)
    f_strip_tag = font(SANS_B, 16)
    f_strip = font(SANS, 15)
    f_foot = font(SANS_B, 14)

    # --- date bar + masthead ---
    d.text((W // 2, 20), "MONDAY 23 NOVEMBER 2026  •  THE DAY IN WORLD NEWS",
           font=f_date, fill=MUTED, anchor="ma")
    d.text((W // 2, 46), "THE WORLD TODAY", font=f_mast, fill=INK, anchor="ma")
    d.line([(28, 118), (996, 118)], fill=RULE, width=3)
    d.line([(28, 124), (996, 124)], fill=RULE, width=1)

    # --- lead story: COP31 ---
    lx, ly, lw = 28, 140, 600
    d.text((lx, ly), "CLIMATE SUMMIT FAILS", font=f_kick, fill=RUST)
    y = para(d, lx, ly + 30, "COP31 ends with no deal", f_head, lw, 52)
    y = para(d, lx, y + 6,
             "First climate summit since 2009 to fail. The EU and about "
             "130 nations refuse a text with no fossil-fuel phaseout.",
             f_dek, lw, 25, color=(58, 56, 48))
    d.rounded_rectangle([660, 140, 996, 330], radius=12,
                        fill=(214, 228, 238))
    globe(d, [748, 168, 908, 308])
    d.text((828, 314), "COP31  •  ANTALYA", font=f_tag, fill=NAVY, anchor="ma")
    d.line([(28, 344), (996, 344)], fill=RULE, width=2)

    # --- six story tiles, 2 columns x 3 rows ---
    tiles = [
        ("UKRAINE  •  LIBYA", "Ukraine sinks Russian warship off Libya",
         "Seven sea drones sank the corvette Merkury at Benghazi, Zelensky "
         "confirms. A helicopter was destroyed and a cargo ship hit.",
         "ship", (214, 228, 238), NAVY),
        ("US POLITICS", "Democrats clinch 258 House seats",
         "Largest majority since 1992. Hubbard beats Foxx by 330 votes in "
         "a North Carolina recount.",
         "ballot", (228, 232, 214), (74, 96, 44)),
        ("UKRAINE  •  DYMER", "Dymer toll rises to 11",
         "Kyiv region mourns after a Russian drone flattens an apartment "
         "block; a supermarket strike kills three.",
         "flame", (240, 224, 208), (176, 90, 26)),
        ("MARKETS", "Taiwan stocks rebound 2.2%",
         "Taiex whipsaws back after its worst week since 1990. Short-sale "
         "curbs bite; the Nikkei is shut for a holiday.",
         "chart", (216, 234, 222), (26, 110, 74)),
        ("INDONESIA", "24 dead in Banten factory fire",
         "A candy factory blaze in Serang leaves about 30 still missing as "
         "rescuers pick through the wreckage.",
         "factory", (238, 222, 214), (140, 60, 30)),
        ("THE GULF", "Trump sets New Year deadline on Iran",
         "\u201cInclined\u201d to resume strikes if no deal, he said on "
         "Sunday. Blockade-breakers would be sunk.",
         "glass", (232, 224, 238), (84, 52, 110)),
    ]
    tx0, ty0, tw, th, gap = 28, 360, 476, 160, 14
    for i, (tag, head, body, kind, tint, accent) in enumerate(tiles):
        x = tx0 + (i % 2) * (tw + gap)
        y = ty0 + (i // 2) * (th + gap)
        d.rounded_rectangle([x, y, x + tw, y + th], radius=10,
                            outline=(200, 192, 172), width=1, fill=(255, 255, 255))
        chip(d, [x + 14, y + 14, x + 110, y + 110], tint, accent, kind)
        bx = x + 124
        d.text((bx, y + 12), tag, font=f_tag, fill=accent)
        hy = para(d, bx, y + 34, head, f_tile_head, tw - 140, 25)
        para(d, bx, hy + 4, body, f_tile_body, tw - 140, 19,
             color=(58, 56, 48))

    # --- also-today strip ---
    sy = 360 + 3 * th + 2 * gap + 14
    d.rounded_rectangle([28, sy, 996, sy + 92], radius=10, fill=STRIP_BG)
    d.text((44, sy + 10), "ALSO TODAY", font=f_strip_tag, fill=RUST)
    para(d, 44, sy + 34,
         "Delta outage delays 1,600+ flights as Thanksgiving travel begins  •  "
         "M\u00e1rquez takes an eighth MotoGP crown  •  Liverpool beat Man Utd 4\u20130  •  "
         "Houthis claim a Saudi refinery hit  •  Five EU states back Rwanda "
         "deportation centres  •  Sudan drones kill five children in Khartoum  •  "
         "FIFA to confirm the UK as 2035 Women\u2019s World Cup host",
         f_strip, 924, 19, color=(58, 56, 48))

    # --- footer ---
    fy = sy + 92 + 12
    d.line([(28, fy), (996, fy)], fill=RULE, width=1)
    d.text((28, fy + 8), "MONDAY 23 NOVEMBER 2026", font=f_foot, fill=MUTED)
    d.text((996, fy + 8), "THE WORLD TODAY", font=f_foot, fill=MUTED,
           anchor="ra")
    return img


def main():
    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry")
    os.makedirs(outdir, exist_ok=True)
    build().save(os.path.join(outdir, "entry.png"), format="PNG")
    print("wrote entry/entry.png")


if __name__ == "__main__":
    main()
