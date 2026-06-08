import re

from django import template

register = template.Library()

DEFAULT_MAX_WIDTH = 718.0
DEFAULT_FONT_SIZE = 14.6667
DEFAULT_MAX_LINES = None


def _parse_svg_wrap_args(args):
    if args is None:
        return DEFAULT_MAX_WIDTH, DEFAULT_FONT_SIZE, DEFAULT_MAX_LINES

    parts = [part.strip() for part in str(args).split(",")]

    max_width = float(parts[0]) if parts and parts[0] else DEFAULT_MAX_WIDTH
    font_size = (
        float(parts[1]) if len(parts) > 1 and parts[1] else DEFAULT_FONT_SIZE
    )
    max_lines = (
        int(parts[2]) if len(parts) > 2 and parts[2] else DEFAULT_MAX_LINES
    )

    return max_width, font_size, max_lines


def _estimated_text_width(text, font_size):
    width = 0.0

    for character in text:
        if character in "ilI.,'|!;: ":
            factor = 0.28
        elif character in "mwMW@%&":
            factor = 0.9
        elif character.isupper():
            factor = 0.68
        elif character.isdigit():
            factor = 0.58
        else:
            factor = 0.52

        width += font_size * factor

    return width


def _split_long_word(word, max_width, font_size):
    chunks = []
    current = ""

    for character in word:
        candidate = f"{current}{character}"
        if current and _estimated_text_width(candidate, font_size) > max_width:
            chunks.append(current)
            current = character
        else:
            current = candidate

    if current:
        chunks.append(current)

    return chunks


@register.filter
def svg_wrap(value, args=None):
    max_width, font_size, max_lines = _parse_svg_wrap_args(args)

    text = "-" if value in (None, "") else str(value)
    paragraphs = re.split(r"\r\n|\r|\n", text)
    lines = []

    for paragraph in paragraphs:
        words = paragraph.split()

        if not words:
            lines.append("")
            continue

        current = ""
        for word in words:
            candidates = _split_long_word(word, max_width, font_size)

            for candidate_word in candidates:
                candidate = (
                    f"{current} {candidate_word}".strip()
                    if current
                    else candidate_word
                )

                if (
                    current
                    and _estimated_text_width(candidate, font_size) > max_width
                ):
                    lines.append(current)
                    current = candidate_word
                else:
                    current = candidate

        if current:
            lines.append(current)

    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        if lines:
            lines[-1] = f"{lines[-1].rstrip()}..."

    return lines
