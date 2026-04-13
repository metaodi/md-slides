"""Markdown parser for md-slides.

Parses a Markdown file into a list of slide dictionaries, where each slide has
a type ('title' or 'content') and relevant fields for the PPTX converter.
"""

import re


def parse_markdown(content):
    """Parse markdown content into a list of slide dicts.

    Slides are separated by '---' (horizontal rule) on its own line.

    Args:
        content: Raw markdown string.

    Returns:
        List of slide dicts. Each dict has at minimum a 'type' key.
    """
    # Normalize line endings
    content = content.replace("\r\n", "\n").replace("\r", "\n")

    # Split by horizontal rule (--- on its own line)
    raw_slides = re.split(r"\n\s*---\s*\n", content)

    slides = []
    for raw in raw_slides:
        raw = raw.strip()
        if not raw:
            continue
        slide = _parse_slide(raw)
        slides.append(slide)

    return slides


def _parse_slide(content):
    """Parse a single slide's markdown content into a structured dict.

    Args:
        content: Raw markdown string for one slide.

    Returns:
        A dict with 'type' and type-specific fields.
    """
    lines = content.split("\n")
    first_line = lines[0].rstrip()

    # Title slide: single # heading
    if first_line.startswith("# "):
        title = first_line[2:].strip()
        subtitle_lines = [l.rstrip() for l in lines[1:] if l.strip()]
        subtitle = "\n".join(subtitle_lines)
        return {
            "type": "title",
            "title": title,
            "subtitle": subtitle,
        }

    # Content slide: ## heading
    if first_line.startswith("## "):
        title = first_line[3:].strip()
        body_lines = lines[1:]
        elements = _parse_body(body_lines)
        return {
            "type": "content",
            "title": title,
            "elements": elements,
        }

    # Fallback: treat as content slide with no title
    return {
        "type": "content",
        "title": "",
        "elements": _parse_body(lines),
    }


def _parse_body(lines):
    """Parse body lines into a list of element dicts.

    Each element is either a 'bullet' or a 'paragraph'.

    Args:
        lines: List of raw text lines.

    Returns:
        List of element dicts with 'type', 'text', and 'runs'.
    """
    elements = []
    for line in lines:
        line = line.rstrip()
        if not line:
            continue

        # Bullet point (- item or * item)
        if re.match(r"^[-*]\s+", line):
            text = re.sub(r"^[-*]\s+", "", line)
            elements.append(
                {
                    "type": "bullet",
                    "text": text,
                    "runs": parse_inline(text),
                }
            )
        else:
            elements.append(
                {
                    "type": "paragraph",
                    "text": line,
                    "runs": parse_inline(line),
                }
            )

    return elements


def parse_inline(text):
    """Parse inline formatting (bold, italic) into a list of run dicts.

    Each run dict has 'text', 'bold', and 'italic' keys.

    Args:
        text: Plain text with optional Markdown inline formatting.

    Returns:
        List of run dicts.
    """
    runs = []
    # Match **bold** before *italic* to avoid greedy overlap
    pattern = re.compile(r"\*\*(.+?)\*\*|\*(.+?)\*")
    last_end = 0

    for m in pattern.finditer(text):
        # Plain text before this match
        if m.start() > last_end:
            runs.append(
                {"text": text[last_end : m.start()], "bold": False, "italic": False}
            )

        if m.group(0).startswith("**"):
            # Bold text
            runs.append({"text": m.group(1), "bold": True, "italic": False})
        else:
            # Italic text
            runs.append({"text": m.group(2), "bold": False, "italic": True})

        last_end = m.end()

    # Remaining plain text
    if last_end < len(text):
        runs.append({"text": text[last_end:], "bold": False, "italic": False})

    # If no runs were found, return the whole text as a single plain run
    if not runs:
        runs.append({"text": text, "bold": False, "italic": False})

    return runs
