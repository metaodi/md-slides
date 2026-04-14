# Introduction to md-slides

A Python-based CLI tool that converts Markdown files into PowerPoint presentations.

---

## Features

- Write slide content in plain Markdown
- Use `---` to separate slides
- Supports **bold** and *italic* inline formatting
- Bullet points and paragraphs

---

## How It Works

1. Write your content in Markdown
2. Run `md-slides input.md -o output.pptx`
3. Open the generated PowerPoint file

---

## Supported Slide Types

- **Title slides** — detected by a single `#` heading
- **Content slides** — start with a `##` heading
- Bullet points from `- item` or `* item` syntax

---

## Custom Templates

You can bring your own branded template:

- Create a `.pptx` file with your employer's design
- Use `--template your_brand.pptx` when running the tool
- The tool merges your content into the template automatically
    * and even supports level 2 bullets

---

## Example Bullet Slide

- First bullet point with **bold** text
- Second bullet point with *italic* text
- Third bullet point with plain text
- A bullet with **bold and** *italic* mixed

---

## Conclusion

Start writing slides today with md-slides!

*Happy presenting!*
