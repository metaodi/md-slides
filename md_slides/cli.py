"""Command-line interface for md-slides."""

import argparse
import sys

from md_slides import __version__
from md_slides.converter import convert
from md_slides.parser import parse_markdown


def main():
    """Entry point for the md-slides CLI."""
    parser = argparse.ArgumentParser(
        prog="md-slides",
        description="Convert a Markdown file into a PowerPoint presentation.",
    )
    parser.add_argument("input", help="Path to the input Markdown (.md) file.")
    parser.add_argument(
        "-o",
        "--output",
        default="output.pptx",
        help="Path for the output .pptx file (default: output.pptx).",
    )
    parser.add_argument(
        "--template",
        default=None,
        help="Path to a custom .pptx template file (default: bundled template).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    args = parser.parse_args()

    # Read markdown input
    try:
        with open(args.input, "r", encoding="utf-8") as fh:
            content = fh.read()
    except FileNotFoundError:
        print(f"Error: input file '{args.input}' not found.", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"Error reading '{args.input}': {exc}", file=sys.stderr)
        sys.exit(1)

    # Parse markdown into slides
    slides = parse_markdown(content)
    if not slides:
        print("Warning: no slides found in the input file.", file=sys.stderr)

    # Convert to PPTX
    try:
        output_path = convert(slides, args.output, template_path=args.template)
    except Exception as exc:  # noqa: BLE001
        print(f"Error generating presentation: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Presentation saved to '{output_path}'.")


if __name__ == "__main__":
    main()
