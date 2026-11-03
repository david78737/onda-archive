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

    pad_x = 100

    # Shrink the name font until it fits within the card width, so a long
    # name (or two names) doesn't run off the right edge. Capped at 92pt —
    # a smaller, more restrained scale than the name of an app or a headline;
    # this is someone's name on a memorial card, not a billboard.
    max_text_w = W - pad_x * 2
    size = 92
    while size > 44:
        name_font = ImageFont.truetype(F_BOLD, size)
        w = draw.textbbox((0, 0), name, font=name_font)[2]
        if w <= max_text_w:
            break
        size -= 4

    sub_font = ImageFont.truetype(F_BOLD_ITAL, 38)

    name_bbox = draw.textbbox((0, 0), name, font=name_font)
    name_h = name_bbox[3] - name_bbox[1]
    sub_bbox = draw.textbbox((0, 0), subtitle, font=sub_font)
    sub_h = sub_bbox[3] - sub_bbox[1]

    gap = 26
    block_h = name_h + gap + sub_h
    name_y = (H - block_h) // 2 - 20
    draw.text((pad_x, name_y), name, font=name_font, fill=WHITE)

    sub_y = name_y + name_h + gap
    draw.text((pad_x, sub_y), subtitle, font=sub_font, fill=ACCENT)

    # Bottom-right credit: small, subordinate to the name. "ONDA" sized
    # ~40% larger than "REPLAY" — same proportion as the real app logo.
    # "By" and "REPLAY" share the small size; "By" and "ONDA" share white.
    small_size = 26
    onda_size = round(small_size * 1.4)
    credit_small = ImageFont.truetype(F_BOLD_ITAL, small_size)
    credit_onda = ImageFont.truetype(F_BOLD, onda_size)

    segments = [("By ", credit_small, WHITE), ("ONDA ", credit_onda, WHITE), ("REPLAY", credit_small, ACCENT)]
    bboxes = [draw.textbbox((0, 0), text, font=font) for text, font, _ in segments]
    widths = [b[2] for b in bboxes]
    heights = [b[3] - b[1] for b in bboxes]

    cx = W - 60 - sum(widths)
    baseline_y = H - 60
    for (text, font, color), w, h in zip(segments, widths, heights):
        draw.text((cx, baseline_y - h), text, font=font, fill=color)
        cx += w

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
<link rel="icon" type="image/png" sizes="32x32" href="/favicon/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon/favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/favicon/apple-touch-icon.png">
<link rel="shortcut icon" href="/favicon/favicon.ico">
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
