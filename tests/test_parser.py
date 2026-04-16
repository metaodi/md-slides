"""Tests for md_slides.parser."""

import pytest

from md_slides.parser import parse_inline, parse_markdown, parse_markdown_doc

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


# ── parse_markdown_doc ─────────────────────────────────────────────────────────


def test_doc_heading_level_1():
    elements = parse_markdown_doc("# Title")
    assert len(elements) == 1
    assert elements[0]["type"] == "heading"
    assert elements[0]["level"] == 1
    assert elements[0]["text"] == "Title"


def test_doc_heading_level_2():
    elements = parse_markdown_doc("## Subtitle")
    assert elements[0]["type"] == "heading"
    assert elements[0]["level"] == 2


def test_doc_heading_level_3():
    elements = parse_markdown_doc("### Sub-sub")
    assert elements[0]["type"] == "heading"
    assert elements[0]["level"] == 3


def test_doc_multiple_headings():
    md = "# One\n## Two\n### Three"
    elements = parse_markdown_doc(md)
    headings = [e for e in elements if e["type"] == "heading"]
    assert len(headings) == 3
    assert headings[0]["level"] == 1
    assert headings[1]["level"] == 2
    assert headings[2]["level"] == 3


def test_doc_bullets():
    md = "- First\n- Second"
    elements = parse_markdown_doc(md)
    bullets = [e for e in elements if e["type"] == "bullet"]
    assert len(bullets) == 2
    assert bullets[0]["text"] == "First"
    assert bullets[1]["text"] == "Second"


def test_doc_nested_bullets():
    md = "- Top\n    - Nested"
    elements = parse_markdown_doc(md)
    bullets = [e for e in elements if e["type"] == "bullet"]
    assert bullets[0]["level"] == 1
    assert bullets[1]["level"] == 2


def test_doc_paragraphs():
    md = "Some plain text.\nAnother line."
    elements = parse_markdown_doc(md)
    paras = [e for e in elements if e["type"] == "paragraph"]
    assert len(paras) == 2


def test_doc_page_break_from_hr():
    md = "# Before\n\n---\n\n# After"
    elements = parse_markdown_doc(md)
    breaks = [e for e in elements if e["type"] == "page_break"]
    assert len(breaks) == 1


def test_doc_page_break_multiple():
    md = "Text\n\n---\n\nMore\n\n---\n\nEnd"
    elements = parse_markdown_doc(md)
    breaks = [e for e in elements if e["type"] == "page_break"]
    assert len(breaks) == 2


def test_doc_mixed_content():
    md = "# Title\n\nIntro paragraph.\n\n## Section\n\n- Bullet A\n- Bullet B\n\nAnother paragraph."
    elements = parse_markdown_doc(md)
    types = [e["type"] for e in elements]
    assert "heading" in types
    assert "paragraph" in types
    assert "bullet" in types


def test_doc_empty_input():
    elements = parse_markdown_doc("")
    assert elements == []


def test_doc_heading_inline_formatting():
    elements = parse_markdown_doc("## A **bold** heading")
    assert elements[0]["type"] == "heading"
    bold_runs = [r for r in elements[0]["runs"] if r["bold"]]
    assert any(r["text"] == "bold" for r in bold_runs)
