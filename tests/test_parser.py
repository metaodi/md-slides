"""Tests for md_slides.parser."""

import pytest

from md_slides.parser import parse_inline, parse_markdown

# ── parse_markdown ─────────────────────────────────────────────────────────────


def test_parse_markdown_single_title_slide():
    md = "# Hello World"
    slides = parse_markdown(md)
    assert len(slides) == 1
    assert slides[0]["type"] == "title"
    assert slides[0]["title"] == "Hello World"


def test_parse_markdown_title_with_subtitle():
    md = "# My Title\nThis is a subtitle"
    slides = parse_markdown(md)
    assert slides[0]["type"] == "title"
    assert slides[0]["title"] == "My Title"
    assert slides[0]["subtitle"] == "This is a subtitle"


def test_parse_markdown_content_slide():
    md = "## Slide Title\n- Bullet one\n- Bullet two"
    slides = parse_markdown(md)
    assert len(slides) == 1
    assert slides[0]["type"] == "content"
    assert slides[0]["title"] == "Slide Title"
    elements = slides[0]["elements"]
    assert len(elements) == 2
    assert all(e["type"] == "bullet" for e in elements)
    assert elements[0]["text"] == "Bullet one"
    assert elements[1]["text"] == "Bullet two"


def test_parse_markdown_multiple_slides():
    md = "# Title Slide\nSubtitle here\n\n---\n\n## Content Slide\n- Item A\n- Item B"
    slides = parse_markdown(md)
    assert len(slides) == 2
    assert slides[0]["type"] == "title"
    assert slides[1]["type"] == "content"


def test_parse_markdown_ignores_empty_sections():
    md = "\n---\n# Hello\n\n---\n\n---\n## Content\n- bullet"
    slides = parse_markdown(md)
    # Only non-empty sections become slides
    assert len(slides) == 2


def test_parse_markdown_paragraph_elements():
    md = "## Slide\nSome paragraph text\nAnother paragraph"
    slides = parse_markdown(md)
    elements = slides[0]["elements"]
    assert any(e["type"] == "paragraph" for e in elements)


def test_parse_markdown_star_bullet():
    md = "## Slide\n* Star bullet"
    slides = parse_markdown(md)
    elements = slides[0]["elements"]
    assert elements[0]["type"] == "bullet"
    assert elements[0]["text"] == "Star bullet"


def test_parse_markdown_fallback_slide():
    """A slide without a # or ## heading becomes a content slide with no title."""
    md = "Some plain text"
    slides = parse_markdown(md)
    assert slides[0]["type"] == "content"
    assert slides[0]["title"] == ""


# ── parse_inline ───────────────────────────────────────────────────────────────


def test_parse_inline_plain_text():
    runs = parse_inline("hello world")
    assert len(runs) == 1
    assert runs[0]["text"] == "hello world"
    assert not runs[0]["bold"]
    assert not runs[0]["italic"]


def test_parse_inline_bold():
    runs = parse_inline("before **bold text** after")
    texts = [r["text"] for r in runs]
    assert "bold text" in texts
    bold_run = next(r for r in runs if r["text"] == "bold text")
    assert bold_run["bold"] is True
    assert bold_run["italic"] is False


def test_parse_inline_italic():
    runs = parse_inline("before *italic text* after")
    italic_run = next(r for r in runs if r["text"] == "italic text")
    assert italic_run["bold"] is False
    assert italic_run["italic"] is True


def test_parse_inline_bold_and_italic():
    runs = parse_inline("**bold** and *italic*")
    bold_run = next(r for r in runs if r.get("bold"))
    italic_run = next(r for r in runs if r.get("italic"))
    assert bold_run["text"] == "bold"
    assert italic_run["text"] == "italic"


def test_parse_inline_no_markup():
    runs = parse_inline("")
    # Empty string should return a single run with empty text
    assert len(runs) == 1
    assert runs[0]["text"] == ""


def test_parse_inline_preserves_surrounding_text():
    runs = parse_inline("start **bold** end")
    full = "".join(r["text"] for r in runs)
    assert full == "start bold end"
