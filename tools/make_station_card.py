#!/usr/bin/env python3
"""
Generate a branded link-preview (Open Graph) card and landing page for one
ONDA Nile station — e.g. a memorial.

What it makes, given a name and a slug:
  assets/og-cards/<slug>.png   — 1200x630 share-card image: the person's
                                  name large, "ONDA REPLAY" small in the
                                  lower-right corner.
  chapter/<slug>/index.html    — a tiny static landing page at
                                  archive.ondareplay.com/chapter/<slug>/
                                  carrying the right title/description/image
                                  meta tags for link previews (iMessage,
                                  Facebook, Slack, etc. all read these from
                                  the plain HTML — they never run the real
                                  chapter page's JavaScript), then instantly
                                  redirects a real visitor's browser on to
                                  the live chapter page.

Usage:
  python3 tools/make_station_card.py \
      --slug pat-stone-memorium \
      --name "Pat Stone" \
      --subtitle "Memorial"

Run from the repo root (or any directory — paths below are resolved
relative to this script's own location, so it also works from elsewhere).
"""
import argparse
import math
import random
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_BASE = "https://archive.ondareplay.com"

W, H = 1200, 630
BG = (0, 89, 98)          # matches the app icon's background teal
WHITE = (255, 255, 255)
ACCENT = (174, 251, 255)  # #aefbff — same accent used in the app logo

F_BOLD = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"
F_BOLD_ITAL = "/System/Library/Fonts/Supplemental/Arial Bold Italic.ttf"


def make_card_image(name: str, subtitle: str, out_path: Path) -> None:
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    name_font = ImageFont.truetype(F_BOLD, 130)
    sub_font = ImageFont.truetype(F_BOLD_ITAL, 60)
    pad_x = 80

    # Shrink the name font until it fits within the card width, so a long
    # name (or two names) doesn't run off the right edge.
    max_text_w = W - pad_x * 2
    size = 130
    while size > 50:
        name_font = ImageFont.truetype(F_BOLD, size)
        w = draw.textbbox((0, 0), name, font=name_font)[2]
        if w <= max_text_w:
            break
        size -= 6

    name_bbox = draw.textbbox((0, 0), name, font=name_font)
    name_h = name_bbox[3] - name_bbox[1]
    name_y = 155
    draw.text((pad_x, name_y), name, font=name_font, fill=WHITE)

    sub_y = name_y + name_h + 42
    draw.text((pad_x, sub_y), subtitle, font=sub_font, fill=ACCENT)
    sub_bbox = draw.textbbox((pad_x, sub_y), subtitle, font=sub_font)
    sub_h = sub_bbox[3] - sub_bbox[1]

    # Small waveform accent strip — same visual language as the app icon,
    # procedurally generated rather than traced from the real logo svg so
    # it can live at any width/position without needing an SVG renderer.
    random.seed(7)
    wave_y_center = sub_y + sub_h + 55
    bar_w, gap, n_bars = 5, 4, 55
    x = pad_x
    for i in range(n_bars):
        t = i / n_bars
        env = math.sin(t * math.pi)
        bar_h = max(6, 8 + env * 34 + random.uniform(-6, 6))
        draw.line([(x, wave_y_center - bar_h / 2), (x, wave_y_center + bar_h / 2)],
                   fill=ACCENT, width=bar_w)
        x += bar_w + gap

    # Bottom-right credit: small, subordinate to the name.
    credit_bold = ImageFont.truetype(F_BOLD, 34)
    credit_ital = ImageFont.truetype(F_BOLD_ITAL, 34)
    onda_w = draw.textbbox((0, 0), "ONDA ", font=credit_bold)[2]
    replay_w = draw.textbbox((0, 0), "REPLAY", font=credit_ital)[2]
    cx = W - 60 - (onda_w + replay_w)
    cy = H - 70
    draw.text((cx, cy), "ONDA ", font=credit_bold, fill=WHITE)
    draw.text((cx + onda_w, cy), "REPLAY", font=credit_ital, fill=ACCENT)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)


LANDING_PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{image_url}">
<meta property="og:type" content="website">
<meta property="og:url" content="{page_url}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{image_url}">
<meta http-equiv="refresh" content="0; url={redirect_url}">
<script>location.replace({redirect_url_js});</script>
</head>
<body>
<p>Taking you to <a href="{redirect_url}">{title}</a>&hellip;</p>
</body>
</html>
"""


def make_landing_page(slug: str, name: str, subtitle: str, out_path: Path) -> None:
    title = f"{name} {subtitle}"
    description = f"Stories, photos, and voices preserved with ONDA Replay."
    image_url = f"{SITE_BASE}/assets/og-cards/{slug}.png"
    page_url = f"{SITE_BASE}/chapter/{slug}/"
    redirect_url = f"{SITE_BASE}/chapter/?station={slug}"

    html = LANDING_PAGE_TEMPLATE.format(
        title=title,
        description=description,
        image_url=image_url,
        page_url=page_url,
        redirect_url=redirect_url,
        redirect_url_js=repr(redirect_url),
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slug", required=True, help="station slug, e.g. pat-stone-memorium (used in the URL)")
    ap.add_argument("--name", required=True, help='the person\'s name as it should appear, e.g. "Pat Stone"')
    ap.add_argument("--subtitle", default="Memorial", help='small line under the name (default: "Memorial")')
    args = ap.parse_args()

    image_out = REPO_ROOT / "assets" / "og-cards" / f"{args.slug}.png"
    page_out = REPO_ROOT / "chapter" / args.slug / "index.html"

    make_card_image(args.name, args.subtitle, image_out)
    make_landing_page(args.slug, args.name, args.subtitle, page_out)

    print(f"Image:       {image_out.relative_to(REPO_ROOT)}")
    print(f"Landing page: {page_out.relative_to(REPO_ROOT)}")
    print(f"Share URL:    {SITE_BASE}/chapter/{args.slug}/")


if __name__ == "__main__":
    main()
