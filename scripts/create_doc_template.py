"""Script to generate the default md-docs template.docx.

Run this script to regenerate the bundled Word template:

    python scripts/create_doc_template.py

The output is written to md_slides/template.docx so that it is included as
package data when the project is installed.
"""

import sys
from pathlib import Path

from docx import Document
from docx.shared import Pt, RGBColor

# Output path inside the package so it ships as package data
OUTPUT = Path(__file__).parent.parent / "md_slides" / "template.docx"


def build_doc_template(output_path: Path):
    """Create a minimal Word document template with standard styles."""
    doc = Document()

    # Ensure common styles exist with sensible defaults.
    # python-docx's default template already provides Heading 1-9,
    # Normal, List Bullet, etc.  We just tweak a few properties so
    # the generated documents look clean out of the box.

    style = doc.styles["Normal"]
    font = style.font
    font.name = "Calibri"
    font.size = Pt(11)
    font.color.rgb = RGBColor(0x26, 0x26, 0x26)

    for level in range(1, 4):
        heading_style = doc.styles[f"Heading {level}"]
        heading_style.font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_path))
    print(f"Word template saved to {output_path}")


if __name__ == "__main__":
    build_doc_template(OUTPUT)
    sys.exit(0)
