# md-slides

> Convert Markdown files into PowerPoint presentations from the command line.

```
your_slides.md  +  template.pptx  →  md-slides  →  output.pptx
(content)          (design)           (tool)        (final slides)
```

## Features

- Write slide content in plain Markdown — no PowerPoint expertise required
- Uses `---` (horizontal rule) as the slide separator
- Supports:
  - **Title slides** (single `# Heading` with optional subtitle)
  - **Content slides** (`## Heading` + body text / bullet points)
  - **Bullet points** (`- item` or `* item`)
  - **Bold** (`**text**`) and *italic* (`*text*`) inline formatting
- Bundled default template — clean, professional look out of the box
- Swap in your own branded `.pptx` template with `--template`

---

## Installation

```bash
pip install md-slides
```

Or install from source:

```bash
git clone https://github.com/metaodi/md-slides.git
cd md-slides
pip install .
```

---

## Usage

```bash
md-slides input.md -o output.pptx
```

### Arguments

| Argument | Description | Default |
|---|---|---|
| `input` | Path to the Markdown file | *(required)* |
| `-o` / `--output` | Output `.pptx` file path | `output.pptx` |
| `--template` | Path to a custom `.pptx` template | bundled template |
| `--version` | Show version and exit | — |

### Examples

```bash
# Basic conversion
md-slides example.md

# Custom output path
md-slides example.md -o slides/my_presentation.pptx

# Use a branded template
md-slides example.md -o output.pptx --template corporate_template.pptx
```

---

## Markdown Format

Slides are separated by `---` on its own line.

```markdown
# Presentation Title

Optional subtitle text goes here

---

## Slide with Bullets

- First bullet point
- **Bold** text in a bullet
- *Italic* text in a bullet

---

## Slide with Paragraphs

This is a regular paragraph.

Another paragraph with **bold** and *italic* words.
```

### Slide types

| Markdown | Slide type | Layout used |
|---|---|---|
| Starts with `# Heading` | Title slide | "Title Slide" layout |
| Starts with `## Heading` | Content slide | "Title and Content" layout |
| Any other content | Content slide (no title) | "Title and Content" layout |

---

## Custom Templates

You (or your design team) can create a branded `.pptx` template in Microsoft
PowerPoint and supply it via `--template`:

```bash
md-slides input.md --template my_brand.pptx
```

**Requirements for a custom template:**

- The template must have at least two slide layouts:
  1. **Layout index 0** — used for title slides (should have a title placeholder
     at index 0 and a subtitle placeholder at index 1)
  2. **Layout index 1** — used for content slides (should have a title placeholder
     at index 0 and a body/content placeholder at index 1)

The simplest way to create a compatible template is to save any PowerPoint file
as a template (`.potx` or `.pptx`) after customising the slide master and the
first two layouts.

### Regenerating the bundled template

If you want to tweak the default template, edit and re-run:

```bash
python scripts/create_template.py
```

The output is written to `md_slides/template.pptx`.

---

## Development

### Set up the environment

```bash
pip install -e ".[dev]"
pip install pre-commit pytest black
pre-commit install
```

### Run the tests

```bash
pytest
```

### Code style

All Python code is formatted with [Black](https://black.readthedocs.io/):

```bash
black md_slides tests scripts
```

---

## Project structure

```
md-slides/
├── md_slides/
│   ├── __init__.py       # package version
│   ├── cli.py            # CLI entry point
│   ├── parser.py         # Markdown → slide dicts
│   ├── converter.py      # slide dicts → .pptx
│   └── template.pptx     # bundled default template
├── scripts/
│   └── create_template.py  # regenerate template.pptx
├── tests/
│   ├── test_parser.py
│   └── test_converter.py
├── example.md
├── pyproject.toml
├── requirements.txt
└── .pre-commit-config.yaml
```

---

## License

MIT — see [LICENSE](LICENSE).