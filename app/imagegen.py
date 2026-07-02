"""Compose the 1080x1350 Instagram image: center-cropped hero photo with a title overlay."""
from __future__ import annotations

import io
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

IMAGE_SIGNOFF = "https://substack.com/@stevenboykeysidley or click on link in my bio"

CANVAS_SIZE = (1080, 1350)  # 4:5 portrait
FONTS_DIR = Path(__file__).parent / "fonts"
TITLE_FONT_PATH = FONTS_DIR / "Montserrat-Bold.ttf"
SUBTITLE_FONT_PATH = FONTS_DIR / "Montserrat-Medium.ttf"

MARGIN = 64
TITLE_FONT_SIZE = 64
SUBTITLE_FONT_SIZE = TITLE_FONT_SIZE // 2
LINE_SPACING = 10
BAND_PADDING = 48


def _download_image(url: str, timeout: int = 15) -> Image.Image:
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return Image.open(io.BytesIO(resp.content)).convert("RGB")


def _center_crop_resize(img: Image.Image, target_size: tuple[int, int]) -> Image.Image:
    target_w, target_h = target_size
    target_ratio = target_w / target_h
    src_w, src_h = img.size
    src_ratio = src_w / src_h

    if src_ratio > target_ratio:
        new_w = int(src_h * target_ratio)
        left = (src_w - new_w) // 2
        img = img.crop((left, 0, left + new_w, src_h))
    else:
        new_h = int(src_w / target_ratio)
        top = (src_h - new_h) // 2
        img = img.crop((0, top, src_w, top + new_h))

    return img.resize(target_size, Image.LANCZOS)


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def build_image(hero_image_url: str, title: str, extra_subtitle: str | None = None) -> Image.Image:
    """Download the hero image, center-crop to 4:5, and overlay the title, an optional
    extra subtitle, and the fixed on-image sign-off beneath it."""
    hero = _download_image(hero_image_url)
    canvas = _center_crop_resize(hero, CANVAS_SIZE)
    draw = ImageDraw.Draw(canvas, "RGBA")

    title_font = ImageFont.truetype(str(TITLE_FONT_PATH), TITLE_FONT_SIZE)
    subtitle_font = ImageFont.truetype(str(SUBTITLE_FONT_PATH), SUBTITLE_FONT_SIZE)

    max_text_width = CANVAS_SIZE[0] - 2 * MARGIN
    title_lines = _wrap_text(draw, title, title_font, max_text_width)

    subtitle_lines = []
    if extra_subtitle:
        subtitle_lines.extend(_wrap_text(draw, extra_subtitle, subtitle_font, max_text_width))
    subtitle_lines.extend(_wrap_text(draw, IMAGE_SIGNOFF, subtitle_font, max_text_width))

    title_line_height = title_font.size + LINE_SPACING
    subtitle_line_height = subtitle_font.size + LINE_SPACING

    text_block_height = (
        len(title_lines) * title_line_height
        + (len(subtitle_lines) * subtitle_line_height if subtitle_lines else 0)
        + (BAND_PADDING if subtitle_lines else 0)
    )
    band_height = text_block_height + 2 * BAND_PADDING
    band_top = CANVAS_SIZE[1] - band_height

    # Semi-opaque dark gradient band behind the text for readability.
    gradient = Image.new("L", (1, band_height), color=0)
    for y in range(band_height):
        alpha = int(200 * (y / band_height))
        gradient.putpixel((0, y), alpha)
    gradient = gradient.resize((CANVAS_SIZE[0], band_height))
    band = Image.new("RGBA", (CANVAS_SIZE[0], band_height), (0, 0, 0, 0))
    band.putalpha(gradient)
    black_layer = Image.new("RGBA", (CANVAS_SIZE[0], band_height), (0, 0, 0, 255))
    black_layer.putalpha(gradient)
    canvas.paste(black_layer, (0, band_top), black_layer)

    y = band_top + BAND_PADDING
    for line in title_lines:
        draw.text((MARGIN, y), line, font=title_font, fill=(255, 255, 255, 255))
        y += title_line_height

    if subtitle_lines:
        y += BAND_PADDING - LINE_SPACING
        for line in subtitle_lines:
            draw.text((MARGIN, y), line, font=subtitle_font, fill=(230, 230, 230, 255))
            y += subtitle_line_height

    return canvas.convert("RGB")
